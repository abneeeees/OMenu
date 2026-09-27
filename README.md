# OMenu

A fast, GTA-inspired radial menu application launcher for Wayland-based Linux systems.

**OMenu** is an application launcher that brings the fluid radial selection wheel interaction to Linux desktop environments. Implemented using **GTK 4**, **Cairo**, and the Linux **`evdev`** input subsystem, OMenu delivers a responsive, low-latency launcher overlay:

---

## Screenshots
<img width="484" height="482" alt="Screenshot From 2026-09-27 20-39-17" src="https://github.com/user-attachments/assets/b8f50869-d240-4514-ba8c-d3c4441f0fe7" />
<img width="1912" height="1175" alt="Screenshot From 2026-09-27 20-39-32" src="https://github.com/user-attachments/assets/bf8d04cd-b9e7-48c6-8e9b-74eb5e088fe1" />


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
- Make sure you enter the right event device path in the configuration file.
- Find out using `ls -la /dev/input/`

```bash
sudo usermod -aG input $USER
```

> **Note**: A session restart or system reboot is required for group membership updates to take effect.

---

## Installation

### Using `uv` (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/abneeeees/OMenu.git
   cd OMenu
   ```

2. Synchronize project dependencies:
   ```bash
   uv sync
   ```

---

## Usage

Start the OMenu daemon:

```bash
# Using uv
uv run omenu

# Or using Python module execution
python -m omenu
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

Application entries are defined in [`config.json`](config.json) located at the root of the project:

```json
{
  "input_device": "/dev/input/your-event-device",
  "apps": [
    {
      "name": "Terminal",
      "command": "ptyxis",
      "icon": "org.gnome.Ptyxis",
      "cwd": "~"
    },
    {
      "name": "Files",
      "command": "nautilus",
      "icon": "org.gnome.Nautilus",
      "cwd": "~"
    },
    {
      "name": "Zen Browser",
      "command": "flatpak run app.zen_browser.zen",
      "icon": "app.zen_browser.zen",
      "cwd": "~"
    },
    {
      "name": "Settings",
      "command": "gnome-control-center",
      "icon": "org.gnome.Settings",
      "cwd": "~"
    }
  ]
}
```

---

## Architecture & Project Structure

```
OMenu/
├── config.json            # Application shortcuts and icon configuration
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
