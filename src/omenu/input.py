# handles main mouse funtions and things 
from evdev import InputDevice, ecodes
import json

class InputHandler:
    def __init__(self, device_path=None):
        if not device_path:
            with open("omenu.json", "r") as f:
                config = json.load(f)
                device_path = config.get("input_device")
        self.mouse = InputDevice(device_path)
        
    def listen(self, on_press=None, on_release=None, on_motion=None, on_scroll=None):
        for event in self.mouse.read_loop():
            if event.type == ecodes.EV_KEY and event.code == ecodes.BTN_MIDDLE:
                if event.value == 1 and on_press:
                    on_press()
                elif event.value == 0 and on_release:
                    on_release()
            elif event.type == ecodes.EV_REL:
                if event.code == ecodes.REL_X and on_motion:
                    on_motion(event.value, 0)
                elif event.code == ecodes.REL_Y and on_motion:
                    on_motion(0, event.value)
                elif event.code == ecodes.REL_WHEEL and on_scroll:
                    on_scroll(event.value)