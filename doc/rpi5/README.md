# 🖥️ Mini PiTFT System Monitor

A comprehensive real-time system monitoring solution for Raspberry Pi 5 using the 1.3" Mini PiTFT display with 180° rotation, button navigation, and intelligent auto-cycling.

![System Monitor Status](https://img.shields.io/badge/Status-Fully%20Functional-brightgreen.svg)
![Hardware](https://img.shields.io/badge/Hardware-Raspberry%20Pi%205-red.svg)
![Display](https://img.shields.io/badge/Display-Mini%20PiTFT%201.3%22-blue.svg)
![Controller](https://img.shields.io/badge/Controller-ST7789%20240x240-orange.svg)
![Auto-Cycle](https://img.shields.io/badge/Auto--Cycle-2%20Minutes-purple.svg)

## ✨ Features

- **🔄 Perfect 180° Display Rotation** - Optimized for upside-down mounting
- **🖱️ Dual Button Navigation** - GPIO 23 & 24 buttons for bidirectional page control
- **⏰ Intelligent Auto-Cycling** - Automatically rotates through pages every 2 minutes
- **⏸️ Smart Manual Override** - Button presses pause auto-cycling for 10 seconds
- **📊 Real-time Monitoring** - System, network, and process statistics
- **🌡️ Temperature Display** - CPU temperature in Fahrenheit with ° symbol
- **🔄 Adaptive Refresh Rates** - 3s for system/network, 1.5s for processes
- **🎨 Clean Interface** - Color-coded pages with status indicators
- **🔧 Raspberry Pi 5 Compatible** - Uses modern gpiod library instead of RPi.GPIO

## 🆕 Auto-Cycling System

### **Automatic Page Rotation**
- **2-minute intervals**: Pages cycle automatically every 120 seconds
- **Sequential order**: System Info → Network Info → Top Processes → repeat
- **Visual countdown**: Purple status indicator shows time until next cycle

### **Manual Override Intelligence**
- **10-second pause**: Any button press pauses auto-cycling temporarily
- **Timer reset**: Manual navigation resets the auto-cycle countdown
- **Seamless resume**: Auto-cycling resumes automatically after override period

### **Status Display**
- **Auto mode**: Shows "Auto: 1:23" (minutes:seconds until next cycle)
- **Manual mode**: Shows "Manual: 7s" (seconds remaining in override)
- **Color coding**: Purple indicators distinguish from other UI elements

## 📋 System Pages

### Page 0 (P0) - System Information (Yellow Title)
- **IP Address** - Current network IP
- **CPU Usage** - Real-time CPU percentage
- **RAM Usage** - Memory utilization percentage  
- **Disk Usage** - Storage utilization percentage
- **Temperature** - CPU temperature in °F
- **Auto-cycle status** - Timer and mode indicator

### Page 1 (P1) - Network Information (Blue Title)
- **Interface** - Active network interface name
- **Data Sent** - Total transmitted data in MB
- **Data Received** - Total received data in MB
- **Auto-cycle status** - Timer and mode indicator

### Page 2 (P2) - Top Processes (Orange Title)
- **Top 5 Processes** - Ranked by memory usage (all users)
- **Memory Percentage** - RAM usage per process
- **User Information** - Process owner (username:process format)
- **Auto-cycle status** - Timer and mode indicator

## 🔧 Hardware Requirements

### Mini PiTFT 1.3" Display
- **Controller**: ST7789
- **Resolution**: 240x240 pixels
- **Interface**: SPI

### GPIO Connections (Raspberry Pi 5)
| Function | GPIO Pin | Physical Pin | Description |
|----------|----------|--------------|-------------|
| DC (Data/Command) | GPIO 25 | Pin 22 | SPI display control |
| RST (Reset) | GPIO 27 | Pin 13 | Display reset (changed from 24) |
| Button A (Previous) | GPIO 23 | Pin 16 | Navigate backward |
| Button B (Next) | GPIO 24 | Pin 18 | Navigate forward |

### SPI Configuration
- **Interface**: SPI0 (CE0)
- **Device**: /dev/spidev0.0
- **Speed**: 8MHz
- **Mode**: 0

### Raspberry Pi 5 Compatibility
- **GPIO Library**: gpiod (modern replacement for RPi.GPIO)
- **GPIO Chip**: gpiochip4 (via `/dev/gpiochip4`)
- **API Versions Supported**:
  - **libgpiod v2.x** (Debian Trixie / RPi OS based on Debian 13)
  - **libgpiod v1.x** (Debian Bookworm / RPi OS based on Debian 12)
- **Auto-Detection**: Script automatically detects and uses correct API

## 🚀 Quick Setup

### 1. Install Prerequisites (Raspberry Pi 5)
```bash
# Run the Raspberry Pi 5 installer with bash (no chmod needed)
bash ./prerequisites-run_rpi5_stats_ST7789.sh
```

The installer asks for your `sudo` password. It only installs what is missing (see [Prerequisites Installation Scripts](#prerequisites-installation-scripts)).

**For other Raspberry Pi models (≤4)**, use the RPi.GPIO version:
```bash
bash ./prerequisites-run_rpi_stats_ST7789.sh
```

### 2. Reboot (if required)
The installer will prompt you to reboot if it just enabled the SPI/I2C interfaces, or if the SPI device (`/dev/spidev0.0`) is not active yet:
```bash
sudo reboot
```

### 3. Run System Monitor

**Raspberry Pi 5 (Recommended Method):**
```bash
# Direct execution (the normal case)
python3 run_rpi5_stats_ST7789.py

# Only if the installer reported that it created a virtual environment (gpiod installed via pip)
~/pitft_venv/bin/python run_rpi5_stats_ST7789.py
```

**Other Raspberry Pi Models (≤4):**
```bash
python3 run_rpi_stats_ST7789.py
```

### 4. Configure Automatic Startup (Optional)

To start the monitor automatically at boot, follow [set-up-script-as-a-service.md](../../set-up-script-as-a-service.md). It covers the systemd service for this script (`pitft-rpi5-monitor.service`), the management commands (start, stop, restart, logs) and troubleshooting.

If the installer created the virtual environment (`~/pitft_venv`), point the service at `~/pitft_venv/bin/python` instead of `/usr/bin/python3`.

## 📦 Manual Installation

### Prerequisites Installation Scripts

The project includes two installation scripts for different Raspberry Pi models. Run them with bash (no chmod needed); both also re-launch themselves under bash if you start them with `sh`.

#### Raspberry Pi 5 (Modern gpiod Method)
```bash
bash ./prerequisites-run_rpi5_stats_ST7789.sh
```

**What the RPi 5 installer does:**
- **RPi 5 detection** - Checks for a Raspberry Pi 5 and asks before continuing on other models
- **OS and libgpiod detection** - Prints the OS release and picks `libgpiod3` (Trixie) or `libgpiod2` (Bookworm)
- **Modern GPIO libraries** - Installs `libgpiod-dev`, the libgpiod runtime, `gpiod` and `python3-libgpiod` through apt; if that fails it installs `gpiod` with pip in a virtual environment
- **Installs only what is needed** - No full Python bundle (`python3-full`), and no build tools unless the pip fallback is used
- **Virtual environment only as a fallback** - `~/pitft_venv` is created only if gpiod could not be installed through apt, or the system packages cannot be imported
- **Hardware interface configuration** - Enables SPI/I2C in the right config.txt (`/boot/firmware/config.txt` or `/boot/config.txt`)
- **UbuntuNerdFont installation** - Downloads and installs the display font if it is not present
- **Verification** - Tests the imports, access to the GPIO chip (`/dev/gpiochip4`) and font loading
- **Reboot prompt** - Asks whether to reboot if it enabled SPI/I2C, or if `/dev/spidev0.0` is not there yet

#### Legacy Raspberry Pi Models (≤4) (RPi.GPIO Method)
```bash
bash ./prerequisites-run_rpi_stats_ST7789.sh
```
See [the Raspberry Pi ≤4 README](../rpi/README.md) for what that installer does.

### Manual System Package Installation

**For Raspberry Pi 5:**
```bash
sudo apt update
sudo apt install -y python3-pip python3-setuptools git python3-venv python3-smbus python3-pil python3-numpy
sudo apt install -y libgpiod-dev libgpiod3 gpiod python3-libgpiod python3-spidev python3-psutil
```
Use `libgpiod2` instead of `libgpiod3` on Debian Bookworm (check with `apt-cache show libgpiod3`). Fonts: see Ubuntu Nerd Font below.

**For other Raspberry Pi models:** see [the Raspberry Pi ≤4 README](../rpi/README.md#manual-system-package-installation).

### Python Dependencies

**Raspberry Pi 5:** the apt packages above provide everything the script imports (`spidev`, `gpiod`, `psutil`, `PIL`).

**Virtual environment (fallback, only if gpiod cannot be installed through apt):** recent Raspberry Pi OS releases block `pip install` into the system Python, so use pip only inside a virtual environment. The installer creates one automatically when needed.
```bash
sudo apt install -y build-essential python3-dev python3-venv libgpiod-dev
python3 -m venv ~/pitft_venv
source ~/pitft_venv/bin/activate
pip install psutil Pillow spidev gpiod
```

**Other Raspberry Pi models:** see [the Raspberry Pi ≤4 README](../rpi/README.md#python-dependencies).

### Ubuntu Nerd Font (Recommended)
For optimal display quality, the Raspberry Pi 5 installer automatically downloads and installs Ubuntu Nerd Font. For manual installation:

```bash
# Download Ubuntu Nerd Font (UbuntuMono variant for better monospace display)
wget https://github.com/ryanoasis/nerd-fonts/releases/download/v3.1.1/UbuntuMono.zip

# Create font directory
sudo mkdir -p /usr/share/fonts/truetype/UbuntuNerdFont

# Extract and install fonts
unzip UbuntuMono.zip
sudo cp UbuntuMonoNerdFont-*.ttf /usr/share/fonts/truetype/UbuntuNerdFont/

# Update font cache
sudo fc-cache -fv

# Clean up
rm UbuntuMono.zip UbuntuMonoNerdFont-*.ttf
```

**Font Verification:**
```bash
# Check if Ubuntu Nerd Font is available
fc-list | grep -i "ubuntu.*nerd"

# Test font loading in Python
python3 -c "
from PIL import ImageFont
import os
font_paths = [
    '/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuMonoNerdFont-Regular.ttf',
    '/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuNerdFont-Regular.ttf'
]
for path in font_paths:
    if os.path.exists(path):
        font = ImageFont.truetype(path, 20)
        print(f'✓ Font working: {path}')
        break
else:
    print('! Font not found, will use default fonts')
"
```

**Note**: The system will automatically fall back to default fonts if Ubuntu Nerd Font is not available.

### Enable SPI Interface

**Raspberry Pi 5:**
The installation script automatically enables SPI in the correct config.txt location:
```bash
# Automatic detection of config.txt location:
# /boot/firmware/config.txt (Raspberry Pi 5 default)
# /boot/config.txt (fallback for older installs)
```

**Manual SPI enablement:**
```bash
# Enable SPI in raspi-config
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable

# Or add directly to config.txt (RPi 5)
echo "dtparam=spi=on" | sudo tee -a /boot/firmware/config.txt

# Or for older Pi models/installations
echo "dtparam=spi=on" | sudo tee -a /boot/config.txt

sudo reboot
```

**Verify SPI is working:**
```bash
# Check SPI device exists
ls -l /dev/spidev0.0

# Check SPI kernel module is loaded
lsmod | grep spi

# Test SPI permissions
groups $USER | grep spi
```

### Troubleshooting Installation

#### Raspberry Pi 5 Specific Issues
```bash
# Check if prerequisites script detected RPi 5 correctly
grep "Raspberry Pi 5" /proc/cpuinfo
grep "BCM2712" /proc/cpuinfo

# Check gpiod installation method
if python3 -c "import gpiod" 2>/dev/null; then
    echo "gpiod available in system packages"
else
    echo "gpiod may need virtual environment"
    source ~/pitft_venv/bin/activate
    python -c "import gpiod; print('gpiod working in venv')"
fi

# Verify virtual environment was created
ls -la ~/pitft_venv/

# Test GPIO chip access
python3 -c "
import gpiod
try:
    chip = gpiod.Chip('gpiochip4')
    print('✓ RPi 5 GPIO chip accessible')
    chip.close()
except Exception as e:
    print(f'✗ GPIO access error: {e}')
"
```

#### Installation Script Issues
```bash
# Re-run installation with verbose output
bash -x prerequisites-run_rpi5_stats_ST7789.sh

# Check installation script permissions
ls -la prerequisites-run_rpi5_stats_ST7789.sh

# Manual execution of script components
sudo apt update
sudo apt install -y python3-libgpiod libgpiod-dev
```

#### Virtual Environment Issues
```bash
# Recreate virtual environment if corrupted
rm -rf ~/pitft_venv
python3 -m venv ~/pitft_venv
source ~/pitft_venv/bin/activate
pip install --upgrade pip
pip install spidev psutil pillow gpiod

# Test virtual environment
~/pitft_venv/bin/python -c "
import spidev, gpiod, psutil
from PIL import Image
print('✓ All packages working in virtual environment')
"
```

#### Raspberry Pi 5 Installation Script
```bash
# Check if script ran successfully
echo $?  # Should be 0 if successful

# Verify all components were installed
python3 -c "
packages = ['spidev', 'gpiod', 'psutil']
pil_modules = ['PIL.Image', 'PIL.ImageDraw', 'PIL.ImageFont']

print('Testing package imports:')
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✓ {pkg}')
    except ImportError:
        print(f'✗ {pkg} - not available')

print('\\nTesting PIL modules:')
for module in pil_modules:
    try:
        parts = module.split('.')
        mod = __import__(parts[0])
        for part in parts[1:]:
            mod = getattr(mod, part)
        print(f'✓ {module}')
    except (ImportError, AttributeError):
        print(f'✗ {module} - not available')
"

# Check if the SPI device is active (if it is missing, reboot)
ls -l /dev/spidev0.0 || echo "SPI device not active - reboot, or enable SPI first"
```

#### Permission Errors (RPi 5)
```bash
# Add user to required groups
sudo usermod -a -G spi,gpio,i2c $USER

# Verify group membership
groups $USER

# Check GPIO device permissions
ls -la /dev/gpiochip*

# Logout and login again for group changes to take effect
```

#### Using Virtual Environment
If the Raspberry Pi 5 installer created a virtual environment (when gpiod needs pip installation):

```bash
# Activate virtual environment
source ~/pitft_venv/bin/activate

# Run script with virtual environment
~/pitft_venv/bin/python run_rpi5_stats_ST7789.py

# Or activate first, then run normally
source ~/pitft_venv/bin/activate
python run_rpi5_stats_ST7789.py

# Deactivate when done
deactivate
```

**Note**: The installer will inform you if virtual environment usage is required.

## 🎮 Usage

### Basic Operation
- **Start**: Run `python3 run_rpi5_stats_ST7789.py`
- **Auto-Cycling**: Pages change automatically every 2 minutes
- **Manual Navigation**: 
  - **Bottom button (GPIO 23)**: Previous page
  - **Top button (GPIO 24)**: Next page
- **Manual Override**: Any button press pauses auto-cycling for 10 seconds
- **Exit**: Press `Ctrl+C` for clean shutdown

### Button Controls
| Button | GPIO | Action | Override |
|--------|------|--------|----------|
| Bottom | 23 | Previous page (P0←P2←P1←P0) | 10 seconds |
| Top | 24 | Next page (P0→P1→P2→P0) | 10 seconds |

### Startup Sequence
1. Display initialization with gpiod detection
2. Memory clearing to prevent artifacts
3. 4-second startup message with auto-cycle info
4. Page 0 (System Info) displayed
5. Auto-cycling begins with 2-minute intervals

### Console Output
```
Ubuntu Nerd Font loaded (MonoNerdFont)
Mini PiTFT System Monitor - Raspberry Pi 5 Compatible with Auto-Cycling
=======================================================================
Initializing display for Raspberry Pi 5...
Using gpiod v2.x API (Debian Trixie)
GPIO initialized for Raspberry Pi 5
SPI initialized at 8000000 Hz
Clearing display memory...
Display initialized with 180° rotation and cleared memory
Showing startup message...
Displaying initial page...

Auto-Cycling Features:
  - Automatically cycles through pages every 2 minutes
  - Manual button presses pause auto-cycling for 10 seconds
  - Purple indicator shows auto-cycle status and timing

Button Controls:
  Bottom button: Previous page
  Top button: Next page

Pages:
  Page 0: System Info (Yellow title)
  Page 1: Network Info (Blue title)
  Page 2: Top Processes (Orange title)

Hardware:
  Using gpiod for Raspberry Pi 5 GPIO compatibility
  GPIO Chip: gpiochip4

Press Ctrl+C to exit
Auto-cycled to page 1
Updating display for page 1...
Bottom button pressed! Switched to page 0 (manual override)
Updating display for page 0...
Top button pressed! Switched to page 1 (manual override)
Updating display for page 1...
```

## 🔧 Technical Details

### Auto-Cycling Configuration
- **Cycle Interval**: 120 seconds (2 minutes)
- **Manual Override**: 10 seconds pause after button press
- **Timer Reset**: Button presses reset the auto-cycle countdown
- **Loop Rate**: 10Hz (100ms) for responsive button handling

### Display Configuration
- **Rotation Value**: `0xC0` (180° rotation)
- **Memory Mapping**: Mini PiTFT offset (rows 80-319)
- **Color Format**: RGB565 (16-bit)
- **Memory Clearing**: Prevents initialization artifacts

### GPIO Implementation (Raspberry Pi 5)
- **Library**: gpiod (modern GPIO interface)
- **Chip**: gpiochip4 (via `/dev/gpiochip4`)
- **API Detection**: Auto-detects libgpiod v2.x (Trixie) or v1.x (Bookworm)
- **Button Logic**: Active low with internal pull-up
- **Debouncing**: Edge detection with state tracking

### Performance Optimization
- **Adaptive Refresh**: 3s system/network, 1.5s processes
- **CPU Impact**: Minimal (~1-2% CPU usage)
- **Memory Usage**: ~20-25MB RAM
- **Button Response**: <100ms response time (the main loop polls the buttons at 10Hz, so a press made while the display is redrawing can be missed; the Raspberry Pi ≤4 version reads the buttons in a background thread to avoid this)
- **Auto-cycle Accuracy**: ±100ms timing precision

## 🛠️ Troubleshooting

### Common Issues

#### Raspberry Pi 5 Specific Issues
```bash
# Check gpiod installation
python3 -c "import gpiod; print('gpiod available')"

# Verify GPIO chip
ls /dev/gpiochip*

# Check gpiod API version
python3 -c '
import gpiod

# Try v2 API first (Debian Trixie)
try:
    from gpiod.line import Direction, Value, Bias
    chip = gpiod.Chip("/dev/gpiochip4")
    print("gpiod v2.x API detected (Debian Trixie)")
    chip.close()
except (ImportError, AttributeError):
    # Try v1 API (Debian Bookworm)
    try:
        chip = gpiod.Chip("gpiochip4")
        line = chip.get_line(25)
        line.request(consumer="test", type=gpiod.LINE_REQ_DIR_OUT)
        print("gpiod v1.x API detected (Debian Bookworm)")
        line.release()
        chip.close()
    except Exception as e:
        print(f"gpiod API error: {e}")
'
```

#### Display Not Working
```bash
# Check SPI device
ls -l /dev/spidev0.0

# Verify SPI enabled
lsmod | grep spi

# Check GPIO permissions (RPi 5)
groups $USER | grep -E "gpio|spi"
```

#### Button Not Responding
```bash
# Test GPIO with gpiod tools (libgpiod v2.x, Debian Trixie)
gpioinfo -c gpiochip4 | grep -E "23|24"

# Monitor button presses (libgpiod v2.x)
gpiomon -c gpiochip4 23 24

# libgpiod v1.x (Debian Bookworm) takes the chip as a plain argument:
#   gpioinfo gpiochip4 | grep -E "23|24"
#   gpiomon gpiochip4 23 24
```

#### Auto-Cycling Issues
```bash
# Check timing variables in console output
# Look for "Auto-cycled to page X" messages
# Verify manual override messages show "(manual override)"

# Test button override timing
# Press button and verify 10-second manual mode display
```

#### Import Errors
```bash
# Check Python packages (RPi 5)
python3 -c "import psutil, PIL, spidev, gpiod; print('All imports OK')"

# Install missing dependencies (system packages)
sudo apt install -y python3-psutil python3-pil python3-spidev python3-libgpiod

# Reinstall if needed
sudo apt install --reinstall -y python3-psutil python3-pil python3-spidev python3-libgpiod
```

#### Font Issues
```bash
# Check Ubuntu Nerd Font paths
find /usr/share/fonts -name "*Ubuntu*Nerd*" -type f

# Test font loading
python3 -c "
from PIL import ImageFont
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuMonoNerdFont-Regular.ttf', 20)
    print('Ubuntu Mono Nerd Font: OK')
except:
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuNerdFont-Regular.ttf', 20)
        print('Ubuntu Nerd Font: OK')
    except:
        print('Ubuntu Nerd Font: Not found - using fallback')
"
```

### Error Messages

| Error | Solution |
|-------|----------|
| `No module named 'gpiod'` | Run `sudo apt install python3-libgpiod` |
| `No module named 'spidev'` | Run `sudo apt install python3-spidev` |
| `SPI device not found` | Enable SPI: `sudo raspi-config` → Interface Options → SPI |
| `Permission denied /dev/spidev0.0` | Add user to spi group: `sudo usermod -a -G spi $USER` |
| `Could not determine gpiod API version` | Install proper gpiod: `sudo apt install python3-libgpiod` |
| `GPIO chip not found` | Check RPi 5 GPIO chip: `ls /dev/gpiochip*` (should show gpiochip4) |
| `No such file or directory: gpiochip4` | Use full path `/dev/gpiochip4` (v2 API) or check symlink exists |
| `Ubuntu Nerd Font not found` | Install manually or system will use fallback fonts |
| `Auto-cycle not working` | Check console for timing messages and button override indicators |

## 📊 System Requirements

- **Raspberry Pi**: Raspberry Pi 5 (for Raspberry Pi 4 and older use the RPi.GPIO version, see [doc/rpi/README.md](../rpi/README.md))
- **OS**: Raspberry Pi OS (Bookworm or Trixie)
- **Python**: 3.9 or newer (for gpiod compatibility)
- **Memory**: Minimum 1GB RAM (Pi 5 requirement)
- **Storage**: ~100MB for dependencies and fonts

## 🔄 Version History

### v2.0 (Current - Auto-Cycling)
- 🆕 **Intelligent Auto-Cycling**: 2-minute automatic page rotation
- 🆕 **Smart Manual Override**: 10-second pause system for button control
- 🆕 **Raspberry Pi 5 Support**: Modern gpiod library compatibility
- 🆕 **Dual Button Navigation**: Previous/Next page controls
- 🆕 **Visual Status Indicators**: Purple auto-cycle status on all pages
- 🆕 **Enhanced Startup Screen**: Auto-cycle information display
- 🆕 **Adaptive Refresh Rates**: Optimized for different page types
- 🆕 **GPIO Pin Update**: RST moved from GPIO 24 to 27 (button conflict resolution)

### v1.0 (Legacy)
- ✅ Perfect 180° rotation with ST7789 controller
- ✅ Single button navigation (GPIO 23) with debouncing
- ✅ 3-page system monitoring (System/Network/Processes)
- ✅ Temperature display in Fahrenheit
- ✅ Top 5 process monitoring
- ✅ Clean startup/shutdown sequence
- ✅ Ubuntu Nerd Font support with fallback

## 📝 Configuration

### Auto-Cycling Settings
```python
AUTO_CYCLE_INTERVAL = 120.0      # Auto-cycle every 2 minutes
manual_override_duration = 10.0   # Manual override lasts 10 seconds
```

### Display Settings
```python
DC_PIN = 25      # Data/Command GPIO
RST_PIN = 27     # Reset GPIO (changed from 24)
BTN_A_PIN = 23   # Previous page button
BTN_B_PIN = 24   # Next page button
WIDTH = 240      # Display width
HEIGHT = 240     # Display height
SPI_SPEED = 8000000  # 8MHz SPI speed
```

### Color Configuration
```python
# Page title colors
BRIGHT_YELLOW = (255, 255, 0)   # System Info
BRIGHT_BLUE = (0, 150, 255)     # Network Info  
BRIGHT_ORANGE = (255, 165, 0)   # Top Processes

# Status indicator
PURPLE = (128, 0, 128)          # Auto-cycle status
```

### Customization Options
- **Auto-cycle Interval**: Modify `AUTO_CYCLE_INTERVAL` (seconds)
- **Manual Override Duration**: Adjust `manual_override_duration` (seconds)
- **Refresh Rates**: Change intervals in main loop (1.5s/3.0s)
- **Temperature Unit**: Modify conversion in `get_system_data()`
- **Process Count**: Adjust `[:5]` in `get_top_processes()`
- **Colors**: Modify RGB color definitions for themes
- **Fonts**: Change font paths, sizes, or families

## 🤝 Contributing

Feel free to submit issues, feature requests, or improvements!

### Development Setup
```bash
git clone https://github.com/smare/rpi_server_stats.git
cd rpi_server_stats
bash ./prerequisites-run_rpi5_stats_ST7789.sh
```

### Feature Requests
- Custom auto-cycle intervals
- Additional monitoring pages
- Network interface selection
- Temperature unit toggle
- Theme customization
- Remote control via web interface

## 📄 License

This project is open source and available under standard terms.

---

**🎯 Project Status: Complete & Fully Functional with Auto-Cycling**

Tested and verified on Raspberry Pi 5 with Mini PiTFT 1.3" display and dual button navigation.