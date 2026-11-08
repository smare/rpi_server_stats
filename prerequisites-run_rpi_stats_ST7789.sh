#!/bin/bash
# prerequisites-run_rpi_stats_ST7789.sh
# Installation script for Mini PiTFT System Monitor prerequisites

# This script uses bash features. Re-run it under bash if it was started with sh or dash.
if [ -z "$BASH_VERSION" ]; then
    exec bash "$0" "$@"
fi

set -e  # Exit on any error

# Work from the folder that contains this script (the repo folder)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Mini PiTFT System Monitor Setup"
echo "Installing prerequisites for Raspberry Pi"
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

# Check if running as root (not recommended)
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. This script should be run as a regular user with sudo privileges."
    read -r -p "Continue anyway? (y/N): " REPLY
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_success "System packages updated"

# Report which OS this is (package names differ between Raspberry Pi OS releases)
OS_NAME="unknown"
if [ -r /etc/os-release ]; then
    OS_NAME="$(. /etc/os-release && echo "${PRETTY_NAME:-unknown}")"
fi
print_status "Detected OS: $OS_NAME"

# Install essential packages
print_status "Installing essential packages..."
sudo apt install -y python3-pip python3-setuptools git python3-venv

# Install support packages
print_status "Installing support packages..."
sudo apt install -y python3-smbus python3-pil python3-numpy

# Install system packages for Python libraries (Debian way)
print_status "Installing Python libraries via apt..."
sudo apt install -y python3-spidev python3-psutil python3-pil

# RPi.GPIO: install a provider only if "import RPi.GPIO" does not already work.
# Raspberry Pi OS ships python3-rpi-lgpio, which provides RPi.GPIO and conflicts with
# python3-rpi.gpio, so installing the second package would remove the first.
if python3 -c "import RPi.GPIO" >/dev/null 2>&1; then
    print_success "RPi.GPIO already available, leaving the installed package alone"
else
    print_status "RPi.GPIO not found, installing it..."
    if apt-cache policy python3-rpi-lgpio 2>/dev/null | grep -q "Candidate: [0-9]"; then
        sudo apt install -y python3-rpi-lgpio || print_warning "Could not install python3-rpi-lgpio"
    else
        sudo apt install -y python3-rpi.gpio || print_warning "Could not install python3-rpi.gpio"
    fi
fi

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
INTERFACES_CHANGED=false

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
    INTERFACES_CHANGED=true
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
    INTERFACES_CHANGED=true
fi

# Verify installation
print_status "Verifying installation..."

# Test Python imports (system packages)
SYSTEM_LIBS_OK=true
python3 -c "
try:
    import spidev
    import RPi.GPIO as GPIO
    import psutil
    from PIL import Image, ImageDraw, ImageFont
    print('✓ All required libraries imported successfully (system packages)')
except ImportError as e:
    print(f'! System packages import issue: {e}')
    print('! Will use virtual environment instead')
    raise SystemExit(1)
" || SYSTEM_LIBS_OK=false

# Fall back to a virtual environment only if the system packages are not usable
VENV_DIR="$HOME/pitft_venv"
if [ "$SYSTEM_LIBS_OK" = false ]; then
    print_warning "System packages are not usable, creating a virtual environment instead..."
    sudo apt install -y build-essential python3-dev
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created at $VENV_DIR"
    fi
    print_status "Installing Python packages in the virtual environment..."
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install spidev RPi.GPIO psutil pillow
    print_success "Packages installed in virtual environment"
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

# Check that the monitor script is next to this installer
if [ -f "run_rpi_stats_ST7789.py" ]; then
    print_success "Found run_rpi_stats_ST7789.py script"
else
    print_warning "run_rpi_stats_ST7789.py not found in current directory"
    print_status "Make sure to download the main script to this directory"
fi

echo
echo "========================================"
print_success "Installation completed successfully!"
echo "========================================"

if [ "$SYSTEM_LIBS_OK" = false ]; then
    print_status "The system Python packages were not usable, so a virtual environment was created."
    echo
    print_success "To run the monitor with the virtual environment:"
    echo "$VENV_DIR/bin/python run_rpi_stats_ST7789.py"
fi

# A reboot is needed if SPI/I2C were just enabled, or if the SPI device is not there yet
REBOOT_REQUIRED=false
if [ "$INTERFACES_CHANGED" = true ] || [ ! -e /dev/spidev0.0 ]; then
    REBOOT_REQUIRED=true
fi

if [ "$REBOOT_REQUIRED" = true ]; then
    echo
    print_warning "REBOOT REQUIRED!"
    print_status "Hardware interfaces (SPI/I2C) have been enabled."
    print_status "Please reboot your Raspberry Pi before running the display script."
    echo
    read -r -p "Reboot now? (y/N): " REPLY
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Rebooting..."
        sudo reboot
    else
        print_status "Remember to reboot before running the display script!"
    fi
else
    echo
    print_status "You can now run the script:"
    print_success "python3 run_rpi_stats_ST7789.py"
    if [ "$SYSTEM_LIBS_OK" = false ]; then
        print_status "Or with the virtual environment:"
        print_success "$VENV_DIR/bin/python run_rpi_stats_ST7789.py"
    fi
fi

echo
print_status "Setup complete! Check doc/rpi/README.md for usage instructions."