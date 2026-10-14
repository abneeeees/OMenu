# handles main mouse funtions and things 
from evdev import InputDevice, UInput, ecodes
import json

# Every wheel variant this device can emit. All of them have to be swallowed
# while the menu is open, otherwise the ones we forget still scroll the window
# sitting behind the overlay.
WHEEL_CODES = (ecodes.REL_WHEEL, ecodes.REL_WHEEL_HI_RES)

class InputHandler:
    def __init__(self, device_path=None):
        if not device_path:
            with open("omenu.json", "r") as f:
                config = json.load(f)
                device_path = config.get("input_device")
        self.device_path = device_path
        self.mouse = InputDevice(device_path)

        # A virtual mouse that replays everything we do not swallow. Grabbing a
        # device is exclusive, so without it the pointer would be frozen for
        # every other application for as long as OMenu holds the real device.
        try:
            self.virtual = UInput.from_device(
                self.mouse, name="omenu virtual mouse"
            )
        except Exception as exc:
            # Without a virtual mouse there is nothing to re-emit events
            # through, so fall back to observing only rather than freezing
            # the pointer.
            print(f"omenu: could not create a virtual mouse: {exc}")
            self.virtual = None

        self.menu_open = False
        self.grabbed = False

    def _grab(self):
        """Take exclusive ownership of the device (EVIOCGRAB).

        While held, the kernel delivers this device's events to OMenu alone, so
        the compositor never sees the middle button or the wheel at all.
        """
        if self.grabbed or self.virtual is None:
            return
        try:
            self.mouse.grab()
        except OSError as exc:
            print(f"omenu: could not grab {self.device_path}: {exc}")
        else:
            self.grabbed = True

    def _ungrab(self):
        """Release the device so normal input is restored."""
        if not self.grabbed:
            return
        try:
            self.mouse.ungrab()
        except OSError as exc:
            print(f"omenu: could not ungrab {self.device_path}: {exc}")
        self.grabbed = False

    def listen(self, on_press=None, on_release=None, on_motion=None, on_scroll=None):
        self._grab()
        try:
            for event in self.mouse.read_loop():
                # The middle button drives the menu, so it must never reach the
                # compositor: otherwise applications also receive a real middle
                # click, which pastes the primary selection in terminals.
                if event.type == ecodes.EV_KEY and event.code == ecodes.BTN_MIDDLE:
                    if event.value == 1:
                        self.menu_open = True
                        if on_press:
                            on_press()
                    elif event.value == 0:
                        self.menu_open = False
                        if on_release:
                            on_release()
                    continue

                # While the menu is open the wheel rotates the selection, and is
                # swallowed so the window behind does not scroll as well.
                if (
                    self.menu_open
                    and event.type == ecodes.EV_REL
                    and event.code in WHEEL_CODES
                ):
                    if event.code == ecodes.REL_WHEEL and on_scroll:
                        on_scroll(event.value)
                    continue

                # Everything else is replayed on the virtual mouse, including
                # the SYN frames, so ordinary movement and clicking still work.
                if self.virtual is not None:
                    self.virtual.write_event(event)

                if event.type == ecodes.EV_REL and on_motion:
                    if event.code == ecodes.REL_X:
                        on_motion(event.value, 0)
                    elif event.code == ecodes.REL_Y:
                        on_motion(0, event.value)
        finally:
            self._ungrab()
            if self.virtual is not None:
                self.virtual.close()
