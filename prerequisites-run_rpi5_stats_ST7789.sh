#!/bin/bash
# prerequisites-run_rpi5_stats_ST7789.sh
# Installation script for Mini PiTFT System Monitor prerequisites - Raspberry Pi 5 Compatible

set -e  # Exit on any error

echo "========================================"
echo "Mini PiTFT System Monitor Setup"
echo "Installing prerequisites for Raspberry Pi 5"
echo "========================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Raspberry Pi 5
print_status "Checking Raspberry Pi version..."
if grep -q "Raspberry Pi 5" /proc/cpuinfo; then
    print_success "Raspberry Pi 5 detected"
elif grep -q "BCM2712" /proc/cpuinfo; then
    print_success "Raspberry Pi 5 (BCM2712) detected"
else
    print_warning "This script is optimized for Raspberry Pi 5"
    print_warning "For other Raspberry Pi models, use prerequisites-run_rpi_stats_ST7789.sh"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if running as root (not recommended)
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. This script should be run as a regular user with sudo privileges."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_success "System packages updated"

# Install essential packages
print_status "Installing essential packages..."
sudo apt install -y python3-pip python3-dev python3-setuptools git python3-full python3-venv

# Install build dependencies
print_status "Installing build dependencies..."
sudo apt install -y build-essential python3-dev python3-smbus python3-pil python3-numpy

# Install Raspberry Pi 5 specific GPIO libraries
print_status "Installing Raspberry Pi 5 GPIO libraries..."
# First install the core libgpiod library
sudo apt install -y libgpiod-dev libgpiod2
if [ $? -eq 0 ]; then
    print_success "Core GPIO libraries installed"

    # Check if python3-gpiod is available in repositories
    if apt-cache show python3-gpiod >/dev/null 2>&1; then
        sudo apt install -y python3-gpiod
        print_success "python3-gpiod installed via apt"
    else
        print_warning "python3-gpiod not available in repositories"
        print_status "Will install gpiod via pip in virtual environment"
        GPIOD_VIA_PIP=true
    fi
else
    print_error "Failed to install core GPIO libraries"
    print_status "Continuing without gpiod - script may not work on RPi 5"
fi

# Install system packages for Python libraries (Debian way)
print_status "Installing Python libraries via apt (recommended for Bookworm)..."
sudo apt install -y python3-spidev python3-psutil python3-pil

# Install font utilities
print_status "Installing font utilities..."
sudo apt install -y fontconfig wget unzip

# Check for and install UbuntuNerdFont
print_status "Checking for UbuntuNerdFont..."
if fc-list | grep -qi "ubuntu.*nerd" || [ -f "/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuMonoNerdFont-Regular.ttf" ]; then
    print_success "UbuntuNerdFont already installed"
else
    print_status "Installing UbuntuNerdFont..."

    # Create font directory
    sudo mkdir -p /usr/share/fonts/truetype/UbuntuNerdFont

    # Download and install UbuntuNerdFont
    cd /tmp
    if wget -q https://github.com/ryanoasis/nerd-fonts/releases/download/v3.1.1/UbuntuMono.zip; then
        print_status "Downloaded UbuntuMono.zip"

        # Extract and install
        if unzip -q UbuntuMono.zip; then
            sudo cp UbuntuMonoNerdFont-*.ttf /usr/share/fonts/truetype/UbuntuNerdFont/ 2>/dev/null || true
            sudo cp *Ubuntu*.ttf /usr/share/fonts/truetype/UbuntuNerdFont/ 2>/dev/null || true

            # Update font cache
            sudo fc-cache -fv >/dev/null 2>&1

            # Verify installation
            if fc-list | grep -qi "ubuntu.*nerd" || [ -f "/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuMonoNerdFont-Regular.ttf" ]; then
                print_success "UbuntuNerdFont installed successfully"
            else
                print_warning "UbuntuNerdFont installation may have issues, but continuing..."
            fi

            # Cleanup
            rm -f /tmp/UbuntuMono.zip /tmp/*Ubuntu*.ttf /tmp/*Nerd*.ttf 2>/dev/null || true
        else
            print_warning "Failed to extract UbuntuMono.zip, will use default fonts"
        fi
    else
        print_warning "Failed to download UbuntuNerdFont, will use default fonts"
    fi

    cd - >/dev/null
fi

# Enable SPI and I2C interfaces
print_status "Configuring hardware interfaces..."

# Check if SPI is already enabled
if grep -q "^dtparam=spi=on" /boot/firmware/config.txt 2>/dev/null || grep -q "^dtparam=spi=on" /boot/config.txt 2>/dev/null; then
    print_success "SPI already enabled"
else
    print_status "Enabling SPI interface..."
    # Try new location first, then fallback to old location
    if [ -f "/boot/firmware/config.txt" ]; then
        echo "dtparam=spi=on" | sudo tee -a /boot/firmware/config.txt
    else
        echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    fi
    print_success "SPI interface enabled (reboot required)"
fi

# Check if I2C is already enabled
if grep -q "^dtparam=i2c_arm=on" /boot/firmware/config.txt 2>/dev/null || grep -q "^dtparam=i2c_arm=on" /boot/config.txt 2>/dev/null; then
    print_success "I2C already enabled"
else
    print_status "Enabling I2C interface..."
    # Try new location first, then fallback to old location
    if [ -f "/boot/firmware/config.txt" ]; then
        echo "dtparam=i2c_arm=on" | sudo tee -a /boot/firmware/config.txt
    else
        echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
    fi
    print_success "I2C interface enabled (reboot required)"
fi

# Create virtual environment as fallback option
VENV_DIR="$HOME/pitft_venv"
print_status "Creating virtual environment as backup option..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    print_success "Virtual environment created at $VENV_DIR"

    # Install packages in virtual environment as backup
    print_status "Installing Python packages in virtual environment..."
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install spidev psutil pillow

    # Install gpiod via pip if not available via apt
    if [ "${GPIOD_VIA_PIP:-false}" = true ]; then
        print_status "Installing gpiod via pip in virtual environment..."
        "$VENV_DIR/bin/pip" install gpiod
        print_success "gpiod installed via pip"
    fi

    print_success "Packages installed in virtual environment"
else
    print_success "Virtual environment already exists"

    # If gpiod needs to be installed via pip and venv exists, install it
    if [ "${GPIOD_VIA_PIP:-false}" = true ]; then
        print_status "Installing gpiod via pip in existing virtual environment..."
        "$VENV_DIR/bin/pip" install gpiod
        print_success "gpiod installed via pip"
    fi
fi

# Verify installation
print_status "Verifying installation..."

# Test Python imports (system packages and virtual environment)
if [ "${GPIOD_VIA_PIP:-false}" = true ]; then
    print_status "Testing imports with virtual environment (gpiod via pip)..."
    "$VENV_DIR/bin/python" -c "
try:
    import spidev
    import gpiod
    import psutil
    from PIL import Image, ImageDraw, ImageFont
    print('✓ All required libraries imported successfully (virtual environment)')
except ImportError as e:
    print(f'! Import issue: {e}')
"
else
    python3 -c "
try:
    import spidev
    import gpiod
    import psutil
    from PIL import Image, ImageDraw, ImageFont
    print('✓ All required libraries imported successfully (system packages)')
except ImportError as e:
    print(f'! System packages import issue: {e}')
    print('! Will use virtual environment instead')
"
fi

# Test gpiod specifically for Raspberry Pi 5
print_status "Testing Raspberry Pi 5 GPIO compatibility..."
if [ "${GPIOD_VIA_PIP:-false}" = true ]; then
    "$VENV_DIR/bin/python" -c "
try:
    import gpiod
    chip = gpiod.Chip('gpiochip4')
    print('✓ Raspberry Pi 5 GPIO (gpiochip4) accessible via virtual environment')
    chip.close()
except Exception as e:
    print(f'! GPIO access issue: {e}')
    print('! May need to run as sudo or check permissions')
"
else
    python3 -c "
try:
    import gpiod
    chip = gpiod.Chip('gpiochip4')
    print('✓ Raspberry Pi 5 GPIO (gpiochip4) accessible')
    chip.close()
except Exception as e:
    print(f'! GPIO access issue: {e}')
    print('! May need to run as sudo or check permissions')
"
fi

# Test UbuntuNerdFont availability
print_status "Testing UbuntuNerdFont availability..."
python3 -c "
from PIL import ImageFont
import os

# Test paths for UbuntuNerdFont
font_paths = [
    '/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuMonoNerdFont-Regular.ttf',
    '/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuNerdFont-Regular.ttf'
]

font_found = False
for path in font_paths:
    if os.path.exists(path):
        try:
            font = ImageFont.truetype(path, 20)
            print(f'✓ UbuntuNerdFont found and working: {path}')
            font_found = True
            break
        except Exception as e:
            continue

if not font_found:
    print('! UbuntuNerdFont not found, script will use default fonts')
"

# Check if run_rpi5_stats_ST7789.py exists
if [ -f "run_rpi5_stats_ST7789.py" ]; then
    print_success "Found run_rpi5_stats_ST7789.py script"

    # Make the script executable
    chmod +x run_rpi5_stats_ST7789.py
    print_success "Made script executable"
else
    print_warning "run_rpi5_stats_ST7789.py not found in current directory"
    print_status "Make sure to download the Raspberry Pi 5 version of the main script"
fi

echo
echo "========================================"
print_success "Raspberry Pi 5 installation completed successfully!"
echo "========================================"

print_status "IMPORTANT: Raspberry Pi 5 specific notes:"
print_status "- Uses gpiod library for GPIO access (newer than RPi.GPIO)"
print_status "- GPIO chip: gpiochip4 (different from older Pi models)"
if [ "${GPIOD_VIA_PIP:-false}" = true ]; then
    print_status "- gpiod installed via pip in virtual environment"
    print_warning "IMPORTANT: Use virtual environment to run the script:"
    echo
    print_success "To activate virtual environment:"
    echo "source $VENV_DIR/bin/activate"
    echo
    print_success "To run your script with virtual environment:"
    echo "$VENV_DIR/bin/python run_rpi5_stats_ST7789.py"
else
    print_status "- If system packages don't work, use the virtual environment:"
    echo
    print_success "To activate virtual environment:"
    echo "source $VENV_DIR/bin/activate"
    echo
    print_success "To run your script with virtual environment:"
    echo "$VENV_DIR/bin/python run_rpi5_stats_ST7789.py"
fi

# Check for reboot requirement
CONFIG_FILE=""
if [ -f "/boot/firmware/config.txt" ]; then
    CONFIG_FILE="/boot/firmware/config.txt"
elif [ -f "/boot/config.txt" ]; then
    CONFIG_FILE="/boot/config.txt"
fi

REBOOT_REQUIRED=false
if [ -n "$CONFIG_FILE" ]; then
    if ! grep -q "^dtparam=spi=on" "$CONFIG_FILE" || ! grep -q "^dtparam=i2c_arm=on" "$CONFIG_FILE"; then
        REBOOT_REQUIRED=true
    fi
fi

if [ "$REBOOT_REQUIRED" = true ]; then
    echo
    print_warning "REBOOT REQUIRED!"
    print_status "Hardware interfaces (SPI/I2C) have been enabled."
    print_status "Please reboot your Raspberry Pi 5 before running the display script."
    echo
    read -p "Reboot now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Rebooting..."
        sudo reboot
    else
        print_status "Remember to reboot before running the display script!"
    fi
else
    echo
    if [ "${GPIOD_VIA_PIP:-false}" = true ]; then
        print_status "You can now run the Raspberry Pi 5 script using virtual environment:"
        print_success "$VENV_DIR/bin/python run_rpi5_stats_ST7789.py"
        print_warning "Note: Virtual environment required due to gpiod installation method"
    else
        print_status "You can now run the Raspberry Pi 5 script:"
        print_success "python3 run_rpi5_stats_ST7789.py"
        print_status "Or with virtual environment:"
        print_success "$VENV_DIR/bin/python run_rpi5_stats_ST7789.py"
    fi
fi

echo
print_status "Hardware Connections for Raspberry Pi 5:"
print_status "- GPIO 25: DC_PIN (Display Data/Command)"
print_status "- GPIO 27: RST_PIN (Display Reset)"
print_status "- GPIO 23: BTN_A_PIN (Bottom button - Previous page)"
print_status "- GPIO 24: BTN_B_PIN (Top button - Next page)"
echo
print_status "Setup complete! Check doc/rpi5/README.md for usage instructions."