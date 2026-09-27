import sys
import threading
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from omenu.menu import MenuWindow
from omenu.input import InputHandler


def on_activate(app: Gtk.Application):
    # Keep GTK application alive even when the window is hidden
    app.hold()

    menu = MenuWindow()
    menu.on_activate(app)
    # Start hidden until the middle mouse button is pressed
    menu.hide()

    input_handler = InputHandler()

    def handle_motion(dx, dy):
        GLib.idle_add(menu.update_motion_rel, dx, dy)

    def handle_scroll(delta):
        GLib.idle_add(menu.scroll_select, delta)

    def listen_mouse():
        input_handler.listen(
            on_press=lambda: GLib.idle_add(menu.show),
            on_release=lambda: GLib.idle_add(menu.release),
            on_motion=handle_motion,
            on_scroll=handle_scroll,
        )

    # Run the blocking evdev read loop in a background thread
    listener_thread = threading.Thread(target=listen_mouse, daemon=True)
    listener_thread.start()


def main():
    app = Gtk.Application(application_id="com.omenu.app")
    app.connect("activate", on_activate)
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())