# OMenu

A fast, GTA-inspired radial menu application launcher for Wayland-based Linux systems.

**OMenu** is an application launcher that brings the fluid radial selection wheel interaction to Linux desktop environments. Implemented using **GTK 4**, **Cairo**, and the Linux **`evdev`** input subsystem, OMenu delivers a responsive, low-latency launcher overlay:

---

## Preview
<img width="484" height="482" alt="Screenshot From 2026-09-27 20-39-17" src="https://github.com/user-attachments/assets/b8f50869-d240-4514-ba8c-d3c4441f0fe7" />


## System Requirements & Dependencies

OMenu requires Python 3.10+ (configured for Python 3.14+) and the development libraries for GTK 4, Cairo, and GObject Introspection.

### Package Installation

#### Fedora / RHEL
```bash
sudo dnf install gtk4-devel gobject-introspection-devel cairo-gobject-devel cairo-devel
```

#### Ubuntu / Debian
```bash
sudo apt update
sudo apt install libgtk-4-dev libgirepository1.0-dev libcairo2-dev python3-gi
```

#### Arch Linux
```bash
sudo pacman -S gtk4 gobject-introspection cairo python-gobject
```

### Input Device Permissions

- OMenu reads input events directly from `/dev/input/`. To run OMenu without root privileges, ensure your user is part of the `input` group:
- Make sure you enter the right event device path in [`omenu.json`](omenu.json).
```bash
cat /proc/bus/input/devices
sudo usermod -aG input $USER
```

> **Note**: A session restart or system reboot is required for group membership updates to take effect.

---

## Installation and Usage

### Using `uv` (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/abneeeees/OMenu.git
   cd OMenu
   ```

2. Synchronize project dependencies:
   ```bash
   uv sync
   uv run omenu
   ```

   

### Controls

| Action | Input |
| :--- | :--- |
| **Open Menu** | Press and hold the **Middle Mouse Button** |
| **Select Application** | Move cursor toward a segment, or rotate the **Scroll Wheel** |
| **Launch Application** | Release the **Middle Mouse Button** on the selected segment |
| **Cancel Selection** | Move cursor back to center or outside the outer radius before releasing |

---

## Configuration

### Applications

Application entries are defined in [`application.json`](application.json) located at the root of the project:

```json
{
  "apps": [
    {
      "name": "Terminal",
      "command": "ptyxis",
      "icon": "org.gnome.Ptyxis",
      "cwd": "~"
    },
    ....
  ]
}
```

### Appearance

`input_device` selects the evdev device OMenu reads from (find it with `ls -la /dev/input/`). The menu geometry, colors, and label styling are configured in the `style` array of [`omenu.json`](omenu.json) — colors are RGBA arrays with values in the `0.0`–`1.0` range:

```json
{
  "input_device": "/dev/input/event4",
  "style": [
    {
      "inner-radius": 100,
      "outer-radius": 200,
      "icon-size": 50,
      ...
    }
  ]
}
```

### Some Other themes to try

#### Cyberpunk

Neon teal highlights over a dark background:

```json
{
  "input_device": "/dev/input/event4",
  "style": [
    {
      "inner-radius": 100,
      "outer-radius": 200,
      "icon-size": 50,
      "wedge-fill-selected": [0.05, 0.9, 0.8, 0.85],
      "wedge-fill-unselected": [0.04, 0.05, 0.08, 0.9],
      "wedge-border-selected": [0.4, 1.0, 0.95, 1.0],
      "wedge-border-unselected": [0.15, 0.25, 0.3, 1.0],
      "wedge-border-selected-width": 3,
      "wedge-border-unselected-width": 2,
      "center-fill": [0.02, 0.03, 0.05, 1.0],
      "center-border": [0.05, 0.9, 0.8, 1.0],
      "center-border-width": 2,
      "icon-y-offset": -18,
      "label-font-family": "Sans",
      "label-font-weight": "bold",
      "label-font-size": 16,
      "label-color": [0.75, 1.0, 0.95, 1.0],
      "label-y-offset": 32,
      "label-y-offset-no-icon": 6
    }
  ]
}
```

#### Modern Orange

Warm amber-orange accents on a dark brown palette:

```json
{
  "input_device": "/dev/input/event4",
  "style": [
    {
      "inner-radius": 100,
      "outer-radius": 200,
      "icon-size": 50,
      "wedge-fill-selected": [0.95, 0.35, 0.12, 0.9],
      "wedge-fill-unselected": [0.12, 0.1, 0.09, 0.9],
      "wedge-border-selected": [1.0, 0.75, 0.45, 1.0],
      "wedge-border-unselected": [0.28, 0.24, 0.21, 1.0],
      "wedge-border-selected-width": 3,
      "wedge-border-unselected-width": 2,
      "center-fill": [0.09, 0.07, 0.06, 1.0],
      "center-border": [0.95, 0.35, 0.12, 1.0],
      "center-border-width": 2,
      "icon-y-offset": -18,
      "label-font-family": "Sans",
      "label-font-weight": "bold",
      "label-font-size": 16,
      "label-color": [1.0, 0.88, 0.72, 1.0],
      "label-y-offset": 32,
      "label-y-offset-no-icon": 6
    }
  ]
}
```

---

## Architecture & Project Structure

```
OMenu/
├── application.json       # Application shortcuts and icon configuration
├── omenu.json             # Input device and radial menu appearance settings
├── pyproject.toml         # Package metadata, dependencies, and build definitions
├── src/
│   └── omenu/
│       ├── __init__.py
│       ├── __main__.py    # Main event loop and background thread lifecycle
│       ├── input.py       # Hardware event listener (motion, click, scroll) via evdev
│       ├── launcher.py    # Process execution and process lifecycle management
│       └── menu.py        # GTK 4 overlay window, Cairo rendering, and icon resolution
└── README.md
```

---

## License

Distributed under the [GNU General Public License (GPL) v3](https://www.gnu.org/licenses/gpl-3.0.en.html). See `LICENSE` for more information.
