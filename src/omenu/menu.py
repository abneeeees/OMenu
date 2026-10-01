# Radial menu window, rendering, and lifecycle
import math
import os
import cairo
import gi
import json

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gdk, Gtk, GdkPixbuf

from omenu.launcher import Launcher

TRANSPARENT_CSS = b"""
window,
.transparent {
    background: none;
}
"""

class MenuWindow:
    def __init__(self):
        # Menu dimensions and geometry
        with open('application.json') as f1:
            self.application = json.load(f1)
        self.apps = self.application.get("apps", [])
        self.ITEM_COUNT = len(self.apps)

        with open("omenu.json") as f:
            self.omenu = json.load(f)
        
        self.style = self.omenu.get("style", [{}])[0]

        self.INNER_RADIUS = self.style.get("inner-radius")
        self.OUTER_RADIUS = self.style.get("outer-radius")
        self.ICON_SIZE = self.style.get("icon-size")

        self.WEDGE_FILL_SELECTED = self.style.get("wedge-fill-selected", (0.24, 0.47, 0.85, 0.75))
        self.WEDGE_FILL_UNSELECTED = self.style.get("wedge-fill-unselected", (0.15, 0.15, 0.17, 0.85))
        self.WEDGE_BORDER_SELECTED = self.style.get("wedge-border-selected", (0.80, 0.89, 1.0, 1.0))
        self.WEDGE_BORDER_UNSELECTED = self.style.get("wedge-border-unselected", (0.25, 0.25, 0.27, 1.0))
        self.WEDGE_BORDER_SELECTED_WIDTH = self.style.get("wedge-border-selected-width", 3)
        self.WEDGE_BORDER_UNSELECTED_WIDTH = self.style.get("wedge-border-unselected-width", 2)

        self.CENTER_FILL = self.style.get("center-fill", (0.07, 0.07, 0.08, 1.0))
        self.CENTER_BORDER = self.style.get("center-border", (0.18, 0.18, 0.20, 1.0))
        self.CENTER_BORDER_WIDTH = self.style.get("center-border-width", 2)

        self.ICON_Y_OFFSET = self.style.get("icon-y-offset")
        self.LABEL_FONT_FAMILY = self.style.get("label-font-family")
        self.LABEL_FONT_WEIGHT = self.style.get("label-font-weight")
        self.LABEL_FONT_SIZE = self.style.get("label-font-size")
        self.LABEL_COLOR = self.style.get("label-color")
        self.LABEL_Y_OFFSET = self.style.get("label-y-offset")
        self.LABEL_Y_OFFSET_NO_ICON = self.style.get("label-y-offset-no-icon")

        # The pointer position, and the fixed point the menu is drawn around
        self.pointer_x = 0
        self.pointer_y = 0
        self.center_x = 0
        self.center_y = 0

        # Index of the highlighted arc, -1 when nothing is selected
        self.selected = -1

        self.window = None
        self.drawing_area = None
        self.launcher = Launcher()
        self.icon_cache = {}    # cache of icon pixbufs by (icon_name, size)

    def get_icon_pixbuf(self, icon_name, size):
        """Lookup and cache an icon as a GdkPixbuf at the requested size."""
        if not icon_name:
            return None
        cache_key = (icon_name, size)
        if cache_key in self.icon_cache:
            # returns the cached pixbuf, or None if the icon could not be loaded
            return self.icon_cache[cache_key]

        pixbuf = None
        # 1. Direct file path check
        if os.path.isabs(icon_name) or os.path.exists(os.path.expanduser(icon_name)):
            expanded = os.path.expanduser(icon_name)
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    expanded, size, size, True
                )
            except Exception:
                print(f"Failed to load icon from {expanded}: ")

        # 2. GTK IconTheme lookup
        if pixbuf is None:
            display = Gdk.Display.get_default()
            if display:
                theme = Gtk.IconTheme.get_for_display(display)
                icon_paintable = theme.lookup_icon(
                    icon_name,
                    None,
                    size,
                    1,
                    Gtk.TextDirection.LTR,
                    Gtk.IconLookupFlags.FORCE_REGULAR,
                )
                if icon_paintable:
                    gfile = icon_paintable.get_file()
                    if gfile:
                        path = gfile.get_path()
                        if path and os.path.exists(path):
                            try:
                                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                                    path, size, size, True
                                )
                            except Exception:
                                print(f"Failed to load icon from {path}: ")
                                pixbuf = None
                        else:
                            pixbuf = None
                    else:
                        pixbuf = None
                else:
                    pixbuf = None

        # After finding the pixbuf, cache it for future use
        self.icon_cache[cache_key] = pixbuf
        # pixbuf may be None if the icon could not be loaded
        return pixbuf

    def show(self):
        """Present the menu window, recentered on the cursor, and trigger a redraw."""
        w, h = self.monitor_size()
        # Determine the center position, ensuring it stays within the monitor bounds
        self.center_x = max(self.OUTER_RADIUS, min(w - self.OUTER_RADIUS, self.pointer_x))
        self.center_y = max(self.OUTER_RADIUS, min(h - self.OUTER_RADIUS, self.pointer_y))
        self.selected = -1
        if self.window:
            self.window.present()
            if self.drawing_area:
                self.drawing_area.queue_draw()

    def hide(self):
        """Hide the menu window."""
        if self.window:
            self.window.set_visible(False)

    def release(self):
        """Hide the menu, launching the app when the pointer is released on its arc."""
        index = self.hit_test(self.pointer_x, self.pointer_y)
        self.hide()
        if index != -1:
            self.launcher.launch(self.apps[index]["command"])

    def hit_test(self, px, py):
        """Return the arc index for a point, launching even when the cursor
        is not touching a sector. Inside the center circle it keeps the
        currently highlighted sector; everywhere else the sector is picked
        by angle alone."""
        if self.ITEM_COUNT == 0:
            return -1
        dx = px - self.center_x
        dy = py - self.center_y
        distance = math.hypot(dx, dy)
        if distance < self.INNER_RADIUS:
            return self.selected
        angle = math.atan2(dy, dx) % math.tau
        return int(angle / (math.tau / self.ITEM_COUNT))

    def select_hovered(self):
        """Highlight the arc under the pointer, then trigger a redraw."""
        index = self.hit_test(self.pointer_x, self.pointer_y)
        if index != -1:
            self.selected = index
        self.redraw()

    def scroll_select(self, delta):
        """Move the selection by one arc per wheel notch."""
        if self.ITEM_COUNT == 0:
            return
        if self.selected == -1:
            self.selected = 0 if delta > 0 else self.ITEM_COUNT - 1
        else:
            step = 1 if delta > 0 else -1
            self.selected = (self.selected + step) % self.ITEM_COUNT
        self.redraw()

    def redraw(self):
        """Queue a redraw while the menu is on screen."""
        if self.drawing_area and self.window and self.window.get_visible():
            self.drawing_area.queue_draw()

    def make_transparent(self, *widgets):
        """Apply CSS provider to make the window background transparent."""
        provider = Gtk.CssProvider()
        provider.load_from_data(TRANSPARENT_CSS)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def monitor_size(self):
        """Get the primary monitor dimensions (width, height)."""
        monitors = Gdk.Display.get_default().get_monitors()
        geometry = monitors.get_item(0).get_geometry()
        return geometry.width, geometry.height

    def update_motion_rel(self, dx, dy):
        """Update cursor position using relative hardware deltas from evdev."""
        w, h = self.monitor_size()
        # Clamp within monitor bounds
        self.pointer_x = max(0, min(w, self.pointer_x + dx))
        self.pointer_y = max(0, min(h, self.pointer_y + dy))
        self.select_hovered()

    def on_motion(self, controller, x, y):
        """Update cursor position from GTK pointer motion events."""
        self.pointer_x = x
        self.pointer_y = y
        self.select_hovered()

    def on_activate(self, app):
        """Initialize the fullscreen transparent overlay window and drawing area."""
        w, h = self.monitor_size()
        self.pointer_x = w / 2
        self.pointer_y = h / 2
        self.center_x = self.pointer_x
        self.center_y = self.pointer_y

        self.window = Gtk.ApplicationWindow(application=app)
        self.window.set_decorated(False)
        self.window.set_default_size(w, h)

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_draw_func(self.draw)

        # Attach pointer motion controller to track cursor inside window
        motion_ctrl = Gtk.EventControllerMotion()
        motion_ctrl.connect("motion", self.on_motion)
        self.window.add_controller(motion_ctrl)

        # Make window transparent and mount the drawing area
        self.make_transparent(self.window, self.drawing_area)
        self.window.set_child(self.drawing_area)

    def draw(self, area, cr, width, height):
        """Cairo draw function to render radial menu wedges and center circle."""
        # 1. Clear to a transparent background
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()

        # Restore normal alpha blending for shapes, borders, icons, and text
        cr.set_operator(cairo.OPERATOR_OVER)

        angle_per_item = math.tau / self.ITEM_COUNT

        # 2. Draw radial menu segments (wedges)
        for i in range(self.ITEM_COUNT):
            start = i * angle_per_item
            end = start + angle_per_item
            selected = i == self.selected

            # Move to inner arc start
            cr.move_to(
                self.center_x + self.INNER_RADIUS * math.cos(start),
                self.center_y + self.INNER_RADIUS * math.sin(start),
            )

            # Draw inner arc (clockwise)
            cr.arc(self.center_x, self.center_y, self.INNER_RADIUS, start, end)

            # Draw outer arc (counter-clockwise back to start angle)
            cr.arc_negative(self.center_x, self.center_y, self.OUTER_RADIUS, end, start)

            # Close the wedge shape
            cr.close_path()

            # Fill wedge background, brighter when it is the selected arc
            if selected:
                cr.set_source_rgba(*self.WEDGE_FILL_SELECTED)
            else:
                cr.set_source_rgba(*self.WEDGE_FILL_UNSELECTED)
            cr.fill_preserve()

            # Stroke wedge border, highlighted when it is the selected arc
            if selected:
                cr.set_source_rgba(*self.WEDGE_BORDER_SELECTED)
                cr.set_line_width(self.WEDGE_BORDER_SELECTED_WIDTH)
            else:
                cr.set_source_rgba(*self.WEDGE_BORDER_UNSELECTED)
                cr.set_line_width(self.WEDGE_BORDER_UNSELECTED_WIDTH)
            cr.stroke()

        # 3. Draw center circle
        cr.arc(
            self.center_x,
            self.center_y,
            self.INNER_RADIUS,
            0,
            math.tau,
        )
        cr.set_source_rgba(*self.CENTER_FILL)
        cr.fill_preserve()

        # Center circle border
        cr.set_source_rgba(*self.CENTER_BORDER)
        cr.set_line_width(self.CENTER_BORDER_WIDTH)
        cr.stroke()

        # 4. Label the center circle with the selected app icon and name
        if 0 <= self.selected < self.ITEM_COUNT:
            app = self.apps[self.selected]
            name = app.get("name", "")
            icon_name = app.get("icon", "")

            icon_size = self.ICON_SIZE
            pixbuf = self.get_icon_pixbuf(icon_name, icon_size)

            font_weight = (
                cairo.FONT_WEIGHT_BOLD
                if self.LABEL_FONT_WEIGHT == "bold"
                else cairo.FONT_WEIGHT_NORMAL
            )

            if pixbuf:
                pw = pixbuf.get_width()
                ph = pixbuf.get_height()
                icon_x = self.center_x - pw / 2
                icon_y = self.center_y - ph / 2 + self.ICON_Y_OFFSET
                Gdk.cairo_set_source_pixbuf(cr, pixbuf, icon_x, icon_y)
                cr.rectangle(icon_x, icon_y, pw, ph)
                cr.fill()
                text_y = self.center_y + self.LABEL_Y_OFFSET
            else:
                text_y = self.center_y + self.LABEL_Y_OFFSET_NO_ICON

            cr.select_font_face(
                self.LABEL_FONT_FAMILY, cairo.FONT_SLANT_NORMAL, font_weight
            )
            cr.set_font_size(self.LABEL_FONT_SIZE)
            extents = cr.text_extents(name)
            cr.set_source_rgba(*self.LABEL_COLOR)
            cr.move_to(
                self.center_x - (extents.width / 2 + extents.x_bearing),
                text_y,
            )
            cr.show_text(name)
