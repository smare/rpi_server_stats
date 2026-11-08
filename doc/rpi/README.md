# 🖥️ Mini PiTFT System Monitor (RPi.GPIO)

A comprehensive real-time system monitoring solution for Raspberry Pi using the 1.3" Mini PiTFT display with 180° rotation, button navigation, and intelligent auto-cycling.

![System Monitor Status](https://img.shields.io/badge/Status-Fully%20Functional-brightgreen.svg)
![Hardware](https://img.shields.io/badge/Hardware-Raspberry%20Pi%20All%20Models-green.svg)
![Display](https://img.shields.io/badge/Display-Mini%20PiTFT%201.3%22-blue.svg)
![Controller](https://img.shields.io/badge/Controller-ST7789%20240x240-orange.svg)
![Auto-Cycle](https://img.shields.io/badge/Auto--Cycle-2%20Minutes-purple.svg)
![GPIO Library](https://img.shields.io/badge/GPIO-RPi.GPIO-red.svg)

## ✨ Features

- **🔄 Perfect 180° Display Rotation** - Optimized for upside-down mounting
- **🖱️ Dual Button Navigation** - GPIO 23 & 24 buttons for bidirectional page control, read by a background thread with debouncing so quick presses are not missed
- **⏰ Intelligent Auto-Cycling** - Automatically rotates through pages every 2 minutes
- **⏸️ Smart Manual Override** - Button presses pause auto-cycling for 10 seconds
- **📊 Real-time Monitoring** - System, network, and process statistics
- **🌡️ Temperature Display** - CPU temperature in Fahrenheit with ° symbol
- **🔄 Adaptive Refresh Rates** - 3s for system/network, 1.5s for processes
- **🎨 Clean Interface** - Color-coded pages with status indicators
- **🔧 Universal Compatibility** - Uses RPi.GPIO for all Raspberry Pi models

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
- **Top 5 Processes** - Ranked by memory usage
- **Memory Percentage** - RAM usage per process
- **Process Names** - Truncated for display fit
- **Auto-cycle status** - Timer and mode indicator

## 🔧 Hardware Requirements

### Mini PiTFT 1.3" Display
- **Controller**: ST7789
- **Resolution**: 240x240 pixels
- **Interface**: SPI

### GPIO Connections (All Raspberry Pi Models)
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

### Raspberry Pi Compatibility
- **GPIO Library**: RPi.GPIO (legacy GPIO interface)
- **Models Supported**: Raspberry Pi Zero, Zero 2 W, 3, 4 (all models ≤4)
- **OS Support**: Raspberry Pi OS (Bullseye, Bookworm, Trixie)
- **Note**: For Raspberry Pi 5, use `run_rpi5_stats_ST7789.py` with gpiod instead

## 🚀 Quick Setup

### 1. Install Prerequisites
```bash
# Run the installer with bash (no chmod needed)
bash ./prerequisites-run_rpi_stats_ST7789.sh
```

The installer asks for your `sudo` password. It only installs what is missing and does not replace packages that already provide `RPi.GPIO` (see [Prerequisites Installation Script](#prerequisites-installation-script)).

**For Raspberry Pi 5**, use the gpiod version instead:
```bash
# RPi 5 requires gpiod - see doc/rpi5/README.md
bash ./prerequisites-run_rpi5_stats_ST7789.sh
```

### 2. Reboot (if required)
The installer will prompt you to reboot if it just enabled the SPI/I2C interfaces, or if the SPI device (`/dev/spidev0.0`) is not active yet:
```bash
sudo reboot
```

### 3. Run Auto-Cycling System Monitor

**System packages (recommended):**
```bash
python3 run_rpi_stats_ST7789.py
```

**Virtual environment (only if the installer reported that the system packages are not usable):**
```bash
# Activate virtual environment
source ~/pitft_venv/bin/activate
python run_rpi_stats_ST7789.py

# Or run directly
~/pitft_venv/bin/python run_rpi_stats_ST7789.py
```

### 4. Configure Automatic Startup (Optional)

To start the monitor automatically at boot, follow [set-up-script-as-a-service.md](../../set-up-script-as-a-service.md). It covers the systemd service for this script (`pitft-rpi-monitor.service`), the management commands (start, stop, restart, logs) and troubleshooting.

If the installer created the virtual environment (`~/pitft_venv`), point the service at `~/pitft_venv/bin/python` instead of `/usr/bin/python3`.

## 📦 Manual Installation

### Prerequisites Installation Script

The project includes an installation script for Raspberry Pi Zero, Zero 2 W, 3 and 4:

#### Universal RPi.GPIO Method
```bash
bash ./prerequisites-run_rpi_stats_ST7789.sh
```

**What the installer does:**
- **Runs under bash** - If you start it with `sh`, it re-launches itself under bash
- **Detects your OS** - Prints the Raspberry Pi OS release it found
- **Installs only what is missing** - `python3-spidev`, `python3-psutil`, `python3-pil` and the support packages through apt
- **Leaves `RPi.GPIO` alone if it already works** - Raspberry Pi OS ships `python3-rpi-lgpio`, which provides `RPi.GPIO` and conflicts with `python3-rpi.gpio`. The installer only installs a provider if `import RPi.GPIO` fails (`python3-rpi-lgpio` when available, otherwise `python3-rpi.gpio`), so it never swaps one for the other
- **Hardware interface configuration** - Enables SPI/I2C in the right config.txt (`/boot/firmware/config.txt` or `/boot/config.txt`) and asks for a reboot if it changed anything or `/dev/spidev0.0` is missing
- **UbuntuNerdFont installation** - Downloads and installs the display font if it is not present
- **Virtual environment only as a fallback** - `~/pitft_venv` is created only if the system packages cannot be imported
- **Verification** - Tests the library imports and font loading

### Manual System Package Installation

**For all Raspberry Pi models:**
```bash
sudo apt update
sudo apt install -y python3-pip python3-setuptools git python3-venv python3-smbus python3-pil python3-numpy python3-spidev python3-psutil
```

**RPi.GPIO:** Raspberry Pi OS normally provides it already (through `python3-rpi-lgpio`). Check first, and only install a provider if the import fails:
```bash
python3 -c "import RPi.GPIO as GPIO; print('RPi.GPIO version:', GPIO.VERSION)"
sudo apt install -y python3-rpi-lgpio    # only if the line above fails (use python3-rpi.gpio on releases without it)
```
Do not install `python3-rpi.gpio` on top of `python3-rpi-lgpio`: they conflict, and apt would remove the one that is installed.

**Fonts:** see Ubuntu Nerd Font below.

### Python Dependencies

**System packages (recommended):** the apt packages above provide everything the script imports (`spidev`, `RPi.GPIO`, `psutil`, `PIL`).

**Virtual environment (fallback):** recent Raspberry Pi OS releases block `pip install` into the system Python, so use pip only inside a virtual environment. The installer creates one automatically when the system packages are not usable.
```bash
sudo apt install -y build-essential python3-dev python3-venv
python3 -m venv ~/pitft_venv
source ~/pitft_venv/bin/activate
pip install psutil Pillow spidev RPi.GPIO
```
### Ubuntu Nerd Font (Recommended)
For optimal auto-cycling status display, the installer automatically downloads and installs Ubuntu Nerd Font. For manual installation:

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

# Test font loading for auto-cycling status indicators
python3 -c "
from PIL import ImageFont
import os
font_paths = [
    '/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuMonoNerdFont-Regular.ttf',
    '/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuNerdFont-Regular.ttf'
]
for path in font_paths:
    if os.path.exists(path):
        # Test both regular and small fonts for auto-cycle indicators
        font = ImageFont.truetype(path, 20)
        font_small = ImageFont.truetype(path, 16)
        print(f'✓ Font working for auto-cycling display: {path}')
        break
else:
    print('! Font not found, auto-cycling will use default fonts')
"
```

**Note**: The system will automatically fall back to default fonts if Ubuntu Nerd Font is not available.

### Enable SPI Interface

**All Raspberry Pi models:**
The installation script automatically enables SPI in the correct config.txt location:
```bash
# Automatic detection of config.txt location:
# /boot/firmware/config.txt (Bookworm and newer)
# /boot/config.txt (Legacy systems)
```

**Manual SPI enablement:**
```bash
# Enable SPI in raspi-config
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable

# Or add directly to config.txt
echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
# For Bookworm and newer:
echo "dtparam=spi=on" | sudo tee -a /boot/firmware/config.txt

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

#### RPi.GPIO Specific Issues
```bash
# Check RPi.GPIO installation and version
python3 -c "
import RPi.GPIO as GPIO
print('RPi.GPIO version:', GPIO.VERSION)
try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print('✓ RPi.GPIO working correctly')
    GPIO.cleanup()
except Exception as e:
    print(f'✗ RPi.GPIO error: {e}')
"

# Test GPIO permissions
python3 -c "
import RPi.GPIO as GPIO
try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(25, GPIO.OUT)  # DC pin
    GPIO.setup(27, GPIO.OUT)  # RST pin
    print('✓ GPIO pins accessible')
    GPIO.cleanup()
except Exception as e:
    print(f'✗ GPIO permission error: {e}')
    print('Try: sudo usermod -a -G gpio \$USER')
"
```

#### Auto-Cycling Feature Verification
```bash
# Check if script has auto-cycling features
if [ -f "run_rpi_stats_ST7789.py" ]; then
    if grep -q "AUTO_CYCLE_INTERVAL" run_rpi_stats_ST7789.py; then
        echo "✓ Auto-cycling features detected"
        grep "AUTO_CYCLE_INTERVAL\|manual_override_duration" run_rpi_stats_ST7789.py
    else
        echo "✗ Auto-cycling features not found"
        echo "Make sure you have the auto-cycling version of the script"
    fi
else
    echo "✗ Script not found: run_rpi_stats_ST7789.py"
fi
```

#### Installation Script Issues
```bash
# Re-run installation with verbose output
bash -x prerequisites-run_rpi_stats_ST7789.sh

# Check installation script permissions
ls -la prerequisites-run_rpi_stats_ST7789.sh

# Manual execution of script components
sudo apt update
sudo apt install -y python3-spidev python3-psutil python3-pil
```

#### Virtual Environment Issues
```bash
# Recreate virtual environment if corrupted
rm -rf ~/pitft_venv
python3 -m venv ~/pitft_venv
source ~/pitft_venv/bin/activate
pip install --upgrade pip
pip install spidev RPi.GPIO psutil pillow

# Test virtual environment with auto-cycling imports
~/pitft_venv/bin/python -c "
import spidev, RPi.GPIO, psutil, time
from PIL import Image, ImageDraw, ImageFont
print('✓ All packages working for auto-cycling system monitor')
"
```

#### Permission Errors
```bash
# Add user to required groups
sudo usermod -a -G spi,gpio,i2c $USER

# Verify group membership
groups $USER

# Check device permissions
ls -la /dev/spidev0.0 /dev/gpiomem

# Logout and login again for group changes to take effect
```

#### Using Virtual Environment
If the installer reported that the system packages are not usable:

```bash
# Activate virtual environment
source ~/pitft_venv/bin/activate

# Run auto-cycling system monitor
python run_rpi_stats_ST7789.py

# Or run directly without activation
~/pitft_venv/bin/python run_rpi_stats_ST7789.py

# Deactivate when done
deactivate
```

## 🎮 Usage

### Basic Operation
- **Start**: Run `python3 run_rpi_stats_ST7789.py`
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
1. Display initialization with RPi.GPIO setup
2. Memory clearing to prevent artifacts
3. Background button polling starts
4. 4-second startup message with auto-cycle info
5. Page 0 (System Info) displayed (button presses made during the startup screen are ignored)
6. Auto-cycling begins with 2-minute intervals

### Console Output
```
Ubuntu Nerd Font loaded (MonoNerdFont)
Mini PiTFT System Monitor - 180° Rotation with Auto-Cycling
===========================================================
Initializing display with proper memory mapping...
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

### GPIO Implementation (RPi.GPIO)
- **Library**: RPi.GPIO (universal compatibility; provided by `python3-rpi-lgpio` or `python3-rpi.gpio`)
- **Mode**: BCM (Broadcom chip-specific pin numbering)
- **Button Logic**: Active low with internal pull-up
- **Button Polling**: A background thread reads both buttons every 5 ms (`BUTTON_POLL_INTERVAL`)
- **Debouncing**: A new button level must hold for 4 consecutive samples, about 20 ms (`BUTTON_DEBOUNCE_SAMPLES`), which filters contact bounce on press and release
- **Press Queue**: Each accepted press is queued, so no press is lost while the display redraws; queued presses are applied together on the next loop pass
- **Pin Setup**: All pins configured with proper direction and pull-up/down

### Performance Optimization
- **Adaptive Refresh**: 3s system/network, 1.5s processes
- **CPU Impact**: Minimal (~1-2% CPU usage)
- **Memory Usage**: ~20-25MB RAM
- **Button Detection**: Presses are detected within about 5-20 ms and queued; the page redraw that follows takes roughly 0.3 s on a Raspberry Pi 4B
- **Auto-cycle Accuracy**: ±100ms timing precision

## 🛠️ Troubleshooting

### Common Issues

#### RPi.GPIO Specific Issues
```bash
# Check RPi.GPIO installation
python3 -c "import RPi.GPIO as GPIO; print('RPi.GPIO version:', GPIO.VERSION)"

# Test GPIO functionality
python3 -c "
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print('Button state (should be 1 when not pressed):', GPIO.input(23))
GPIO.cleanup()
"

# Check GPIO permissions
groups $USER | grep gpio
```

#### Display Not Working
```bash
# Check SPI device
ls -l /dev/spidev0.0

# Verify SPI enabled
lsmod | grep spi

# Check GPIO permissions
groups $USER | grep -E "gpio|spi"
```

#### Button Not Responding
```bash
# Test button wiring (active low)
python3 -c "
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print('Press buttons to test (Ctrl+C to exit):')
try:
    while True:
        btn_a = GPIO.input(23)
        btn_b = GPIO.input(24)
        print(f'Button A (GPIO 23): {btn_a}, Button B (GPIO 24): {btn_b}', end='\r')
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
    print('\nButton test complete')
"
```

#### Auto-Cycling Issues
```bash
# Check timing variables in console output
# Look for "Auto-cycled to page X" messages
# Verify manual override messages show "(manual override)"

# Verify auto-cycling functions exist
grep -n "check_auto_cycle\|get_auto_cycle_status" run_rpi_stats_ST7789.py
```

#### Import Errors
```bash
# Check Python packages
python3 -c "import psutil, PIL, spidev, RPi.GPIO; print('All imports OK')"

# Install missing dependencies (system packages)
sudo apt install -y python3-psutil python3-pil python3-spidev

# Use virtual environment if system packages fail
source ~/pitft_venv/bin/activate
python -c "import psutil, PIL, spidev, RPi.GPIO; print('Virtual env OK')"
```

#### Font Issues
```bash
# Check Ubuntu Nerd Font paths
find /usr/share/fonts -name "*Ubuntu*Nerd*" -type f

# Test font loading for auto-cycling status
python3 -c "
from PIL import ImageFont
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuMonoNerdFont-Regular.ttf', 20)
    font_small = ImageFont.truetype('/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuMonoNerdFont-Regular.ttf', 16)
    print('Ubuntu Mono Nerd Font: OK (auto-cycling status will display properly)')
except:
    print('Ubuntu Nerd Font: Not found - using fallback fonts for auto-cycling')
"
```

### Error Messages

| Error | Solution |
|-------|----------|
| `No module named 'RPi.GPIO'` | Run `sudo apt install python3-rpi-lgpio` (or `python3-rpi.gpio` on releases without it); do not install both |
| `No module named 'spidev'` | Run `sudo apt install python3-spidev` |
| `SPI device not found` | Enable SPI: `sudo raspi-config` → Interface Options → SPI |
| `Permission denied /dev/spidev0.0` | Add user to spi group: `sudo usermod -a -G spi $USER` |
| `RuntimeError: No access to /dev/mem` | Add user to gpio group: `sudo usermod -a -G gpio $USER` |
| `Ubuntu Nerd Font not found` | Install manually or system will use fallback fonts |
| `Auto-cycle not working` | Check console for timing messages and button override indicators |
| `GPIO already in use` | Run `GPIO.cleanup()` or restart script |

## 📊 System Requirements

- **Raspberry Pi**: Zero, Zero 2 W, 3 and 4 (use the Pi 5 version for Raspberry Pi 5)
- **OS**: Raspberry Pi OS (Bullseye, Bookworm or Trixie)
- **Python**: 3.7 or newer
- **Memory**: Minimum 512MB RAM
- **Storage**: ~100MB for dependencies and fonts

## 🔄 Version History

### v2.0 (Current - Auto-Cycling with RPi.GPIO)
- 🆕 **Intelligent Auto-Cycling**: 2-minute automatic page rotation
- 🆕 **Smart Manual Override**: 10-second pause system for button control
- 🆕 **Universal Compatibility**: RPi.GPIO for all Raspberry Pi models
- 🆕 **Dual Button Navigation**: Previous/Next page controls
- 🆕 **Visual Status Indicators**: Purple auto-cycle status on all pages
- 🆕 **Enhanced Startup Screen**: Auto-cycle information display
- 🆕 **Adaptive Refresh Rates**: Optimized for different page types
- 🆕 **Reliable Button Presses**: Background polling thread with debouncing and a press queue, so quick presses are not lost while the display redraws
- 🆕 **GPIO Pin Update**: RST moved from GPIO 24 to 27 (button conflict resolution)

### v1.0 (Legacy)
- ✅ Perfect 180° rotation with ST7789 controller
- ✅ Single button navigation with debouncing
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

### Button Settings
```python
BUTTON_POLL_INTERVAL = 0.005     # Poll the buttons every 5 ms in a background thread
BUTTON_DEBOUNCE_SAMPLES = 4      # A new level must hold for 4 samples (about 20 ms)
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
- **Button Sensitivity**: Adjust `BUTTON_POLL_INTERVAL` and `BUTTON_DEBOUNCE_SAMPLES`
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
bash ./prerequisites-run_rpi_stats_ST7789.sh
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

Tested and verified on multiple Raspberry Pi models with Mini PiTFT 1.3" display and dual button navigation using RPi.GPIO.