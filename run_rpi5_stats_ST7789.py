#!/usr/bin/env python3
"""
Mini PiTFT System Monitor - Raspberry Pi 5 Compatible with Auto-Cycling
=======================================================================

A comprehensive system monitoring display for Raspberry Pi 5 using the Mini PiTFT (ST7789) display.
Features 180° rotation, button navigation, auto-cycling pages, and real-time system statistics.

Hardware Requirements:
- Raspberry Pi 5
- Mini PiTFT 1.3" ST7789 240x240 display
- Two buttons connected to GPIO 23 and GPIO 24

Features:
- Real-time system monitoring (CPU, RAM, Disk, Temperature, IP)
- Network statistics (interface, sent/received data)
- Top running processes by memory usage
- Color-coded page titles for easy identification
- Bidirectional button navigation
- AUTO-CYCLING: Automatically cycles through pages every 2 minutes
- Manual button presses override auto-cycling temporarily
- 180° display rotation for proper orientation

Raspberry Pi 5 Compatibility:
- Uses gpiod library instead of RPi.GPIO
- Compatible with new GPIO hardware architecture
- Maintains all functionality from original version

Author: Sean Mare
Date: 2025
License: MIT
"""

import time
import socket
import psutil
import signal
import sys
from PIL import Image, ImageDraw, ImageFont
import spidev
import gpiod

# Hardware Configuration
# ======================
DC_PIN = 25      # Data/Command pin for SPI display communication
RST_PIN = 27     # Reset pin for display initialization (changed from 24 to avoid conflict)
BTN_A_PIN = 23   # Bottom button (previous page navigation)
BTN_B_PIN = 24   # Top button (next page navigation)

# Display Configuration
# ====================
WIDTH = 240      # Display width in pixels
HEIGHT = 240     # Display height in pixels
SPI_SPEED = 8000000  # SPI communication speed (8MHz)

# Auto-cycling Configuration
# ==========================
AUTO_CYCLE_INTERVAL = 120.0  # Auto-cycle every 2 minutes (120 seconds)

# Color Definitions
# ================
# Standard colors for UI elements
BLACK = (0, 0, 0)           # Background color
WHITE = (255, 255, 255)     # Primary text color
BLUE = (0, 100, 255)        # Navigation text color
GREEN = (0, 255, 0)         # Button instruction color
RED = (255, 0, 0)           # Page indicator color
PURPLE = (128, 0, 128)      # Auto-cycle indicator color

# Bright colors for page-specific titles
BRIGHT_YELLOW = (255, 255, 0)   # System Info page title
BRIGHT_BLUE = (0, 150, 255)     # Network Info page title
BRIGHT_ORANGE = (255, 165, 0)   # Top Processes page title

# Global State Variables
# =====================
spi = None                      # SPI device handle
gpio_chip = None               # GPIO chip handle for RPi 5
dc_line = None                 # DC pin line
rst_line = None                # Reset pin line
btn_a_line = None              # Button A line
btn_b_line = None              # Button B line
running = True                 # Main loop control flag
current_page = 0              # Current displayed page (0=System, 1=Network, 2=Processes)
last_button_a_state = False   # Previous state of button A (for debouncing)
last_button_b_state = False   # Previous state of button B (for debouncing)
last_auto_cycle_time = 0      # Time of last auto-cycle
last_manual_interaction = 0   # Time of last manual button press
manual_override_duration = 10.0  # How long to wait after manual interaction before resuming auto-cycle

def cleanup():
    """
    Clean up GPIO and SPI resources for Raspberry Pi 5.

    This function is called when the program exits to ensure proper
    cleanup of hardware resources and prevent GPIO conflicts.
    """
    global running, spi, gpio_chip, dc_line, rst_line, btn_a_line, btn_b_line
    running = False
    try:
        if spi:
            spi.close()
        # Release GPIO lines properly for RPi 5
        if dc_line:
            dc_line.release()
        if rst_line:
            rst_line.release()
        if btn_a_line:
            btn_a_line.release()
        if btn_b_line:
            btn_b_line.release()
        if gpio_chip:
            gpio_chip.close()
    except:
        pass

def signal_handler(sig, frame):
    """
    Handle Ctrl+C interrupt signal for graceful shutdown.

    Args:
        sig: Signal number
        frame: Current stack frame
    """
    print("\nShutting down...")
    cleanup()
    sys.exit(0)

def write_cmd(cmd):
    """
    Send a command byte to the display via SPI.

    Args:
        cmd (int): Command byte to send (0x00-0xFF)
    """
    if not running:
        return
    dc_line.set_value(0)  # Set DC low for command mode
    spi.xfer2([cmd])

def write_data(data):
    """
    Send data byte(s) to the display via SPI.

    Args:
        data (int or list): Data byte or list of bytes to send
    """
    if not running:
        return
    dc_line.set_value(1)  # Set DC high for data mode
    if isinstance(data, list):
        spi.xfer2(data)
    else:
        spi.xfer2([data])

def rgb_to_rgb565(r, g, b):
    """
    Convert RGB888 color to RGB565 format for display.

    The ST7789 display uses 16-bit RGB565 color format:
    - Red: 5 bits (bits 15-11)
    - Green: 6 bits (bits 10-5)
    - Blue: 5 bits (bits 4-0)

    Args:
        r (int): Red component (0-255)
        g (int): Green component (0-255)
        b (int): Blue component (0-255)

    Returns:
        int: 16-bit RGB565 color value
    """
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def clear_display_memory():
    """
    Clear the entire display memory to black.

    Sets the display window to full screen and fills it with black pixels.
    This prevents display artifacts and ensures clean startup.
    """
    # Set full display area
    write_cmd(0x2A)  # Column address
    write_data([0x00, 0x00, 0x00, 0xEF])  # 0 to 239

    write_cmd(0x2B)  # Row address
    write_data([0x00, 0x50, 0x01, 0x3F])  # 80 to 319 (Mini PiTFT offset)

    write_cmd(0x2C)  # Memory write

    # Send black pixels to entire display
    black_pixel = [0x00, 0x00]  # Black in RGB565 format
    total_pixels = WIDTH * HEIGHT

    # Send pixels in chunks for efficiency
    chunk_size = 1024
    for i in range(0, total_pixels * 2, chunk_size):
        if not running:
            break
        chunk = black_pixel * (chunk_size // 2)
        write_data(chunk)

def init_display():
    """
    Initialize the ST7789 display with proper configuration for Raspberry Pi 5.

    This function handles:
    - GPIO setup using gpiod for RPi 5 compatibility
    - SPI initialization
    - ST7789 chip initialization sequence
    - 180° rotation configuration
    - Display memory clearing

    Returns:
        bool: True if initialization successful, False otherwise
    """
    global spi, gpio_chip, dc_line, rst_line, btn_a_line, btn_b_line

    print("Initializing display for Raspberry Pi 5...")

    # Initialize GPIO using gpiod for Raspberry Pi 5
    try:
        # First try to detect gpiod version and use appropriate API
        gpio_chip = gpiod.Chip('gpiochip4')  # RPi 5 uses gpiochip4 for main GPIO

        # Test which API version we have
        test_line = gpio_chip.get_line(DC_PIN)

        # Try newer API first
        try:
            test_line.request(consumer="test", type=gpiod.LINE_REQ_DIR_OUT)
            test_line.release()
            print("Using gpiod v1.x API")
            use_v1_api = True
        except:
            # Try older API
            try:
                test_line.request(consumer="test", direction=gpiod.LINE_REQ_DIR_OUT)
                test_line.release()
                print("Using gpiod v0.x API")
                use_v1_api = False
            except Exception as e:
                print(f"Could not determine gpiod API version: {e}")
                return False

        # Configure pins based on API version
        if use_v1_api:
            # v1.x API
            dc_line = gpio_chip.get_line(DC_PIN)
            dc_line.request(consumer="pitft_dc", type=gpiod.LINE_REQ_DIR_OUT)

            rst_line = gpio_chip.get_line(RST_PIN)
            rst_line.request(consumer="pitft_rst", type=gpiod.LINE_REQ_DIR_OUT)

            btn_a_line = gpio_chip.get_line(BTN_A_PIN)
            btn_a_line.request(consumer="pitft_btn_a", type=gpiod.LINE_REQ_DIR_IN,
                              flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)

            btn_b_line = gpio_chip.get_line(BTN_B_PIN)
            btn_b_line.request(consumer="pitft_btn_b", type=gpiod.LINE_REQ_DIR_IN,
                              flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)
        else:
            # v0.x API
            dc_line = gpio_chip.get_line(DC_PIN)
            dc_line.request(consumer="pitft_dc", direction=gpiod.LINE_REQ_DIR_OUT)

            rst_line = gpio_chip.get_line(RST_PIN)
            rst_line.request(consumer="pitft_rst", direction=gpiod.LINE_REQ_DIR_OUT)

            btn_a_line = gpio_chip.get_line(BTN_A_PIN)
            btn_a_line.request(consumer="pitft_btn_a", direction=gpiod.LINE_REQ_DIR_IN,
                              bias=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)

            btn_b_line = gpio_chip.get_line(BTN_B_PIN)
            btn_b_line.request(consumer="pitft_btn_b", direction=gpiod.LINE_REQ_DIR_IN,
                              bias=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)

        print("GPIO initialized for Raspberry Pi 5")

    except Exception as e:
        print(f"GPIO initialization failed: {e}")
        return False

    # Initialize SPI communication
    try:
        spi = spidev.SpiDev()
        spi.open(0, 0)  # SPI bus 0, device 0
        spi.max_speed_hz = SPI_SPEED
        spi.mode = 0    # SPI mode 0 (CPOL=0, CPHA=0)
        print(f"SPI initialized at {SPI_SPEED} Hz")
    except Exception as e:
        print(f"SPI failed: {e}")
        return False

    # Hardware reset sequence
    rst_line.set_value(0)  # Reset low
    time.sleep(0.1)
    rst_line.set_value(1)    # Reset high
    time.sleep(0.12)

    try:
        # ST7789 initialization sequence
        # ==============================

        # Software reset
        write_cmd(0x01)
        time.sleep(0.15)

        # Sleep out (exit sleep mode)
        write_cmd(0x11)
        time.sleep(0.25)

        # Set 180° rotation for proper Mini PiTFT orientation
        write_cmd(0x36)  # Memory Access Control
        write_data([0xC0])  # 180° rotation

        # Set color format to 16-bit RGB565
        write_cmd(0x3A)  # Interface Pixel Format
        write_data([0x55])  # 16-bit color

        # Set display area for 1.3" Mini PiTFT with 180° rotation
        # Column address set (X coordinates)
        write_cmd(0x2A)
        write_data([0x00, 0x00, 0x00, 0xEF])  # 0 to 239

        # Row address set (Y coordinates with Mini PiTFT offset)
        write_cmd(0x2B)
        write_data([0x00, 0x50, 0x01, 0x3F])  # 80 to 319 (Mini PiTFT specific offset)

        # Porch control
        write_cmd(0xB2)
        write_data([0x0C, 0x0C, 0x00, 0x33, 0x33])

        # Gate control
        write_cmd(0xB7)
        write_data([0x35])

        # VCOM setting
        write_cmd(0xBB)
        write_data([0x19])

        # LCM control
        write_cmd(0xC0)
        write_data([0x2C])

        # VDV and VRH command enable
        write_cmd(0xC2)
        write_data([0x01])

        # VRH set
        write_cmd(0xC3)
        write_data([0x12])

        # VDV set
        write_cmd(0xC4)
        write_data([0x20])

        # Frame rate control
        write_cmd(0xC6)
        write_data([0x0F])

        # Power control
        write_cmd(0xD0)
        write_data([0xA4, 0xA1])

        # Positive voltage gamma control
        write_cmd(0xE0)
        write_data([0xD0, 0x04, 0x0D, 0x11, 0x13, 0x2B, 0x3F, 0x54,
                   0x4C, 0x18, 0x0D, 0x0B, 0x1F, 0x23])

        # Negative voltage gamma control
        write_cmd(0xE1)
        write_data([0xD0, 0x04, 0x0C, 0x11, 0x13, 0x2C, 0x3F, 0x44,
                   0x51, 0x2F, 0x1F, 0x1F, 0x20, 0x23])

        # Display inversion on (improves color accuracy)
        write_cmd(0x21)

        # Normal display mode
        write_cmd(0x13)

        # Clear display memory before turning on
        print("Clearing display memory...")
        clear_display_memory()

        # Display on
        write_cmd(0x29)
        time.sleep(0.1)

        print("Display initialized with 180° rotation and cleared memory")
        return True

    except Exception as e:
        print(f"Display initialization failed: {e}")
        return False

def display_image_corrected(image):
    """
    Display an image on the ST7789 display with proper memory mapping.

    Converts PIL Image to RGB565 format and sends to display memory.
    Handles the Mini PiTFT's specific memory offset and 180° rotation.

    Args:
        image (PIL.Image): Image to display (will be converted to RGB if needed)
    """
    if not running:
        return

    # Ensure image is in RGB format
    rgb_image = image.convert('RGB')

    # Set display area with Mini PiTFT offset for 180° rotation
    write_cmd(0x2A)  # Column address
    write_data([0x00, 0x00, 0x00, 0xEF])  # 0 to 239

    write_cmd(0x2B)  # Row address
    write_data([0x00, 0x50, 0x01, 0x3F])  # 80 to 319 (Mini PiTFT offset)

    write_cmd(0x2C)  # Memory write

    # Convert PIL image pixels to RGB565 format
    pixels = []
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if x < rgb_image.width and y < rgb_image.height:
                r, g, b = rgb_image.getpixel((x, y))
            else:
                r, g, b = 0, 0, 0  # Black for areas outside image bounds

            # Convert to RGB565 and split into high/low bytes
            rgb565 = rgb_to_rgb565(r, g, b)
            pixels.append((rgb565 >> 8) & 0xFF)  # High byte
            pixels.append(rgb565 & 0xFF)         # Low byte

    # Send pixel data in chunks for efficiency
    chunk_size = 1024
    for i in range(0, len(pixels), chunk_size):
        if not running:
            break
        chunk = pixels[i:i + chunk_size]
        write_data(chunk)

# Font Configuration
# ==================
try:
    # Try to load UbuntuNerdFont with multiple possible paths
    font = ImageFont.truetype('/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuMonoNerdFont-Regular.ttf', 20)
    font_title = ImageFont.truetype('/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuMonoNerdFont-Bold.ttf', 22)
    font_title_small = ImageFont.truetype('/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuMonoNerdFont-Bold.ttf', 21)  # 1pt smaller for page 2
    font_small = ImageFont.truetype('/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuMonoNerdFont-Regular.ttf', 16)  # Small font for auto-cycle indicator
    print("Ubuntu Nerd Font loaded (MonoNerdFont)")
except:
    try:
        # Fallback to alternative UbuntuNerdFont path
        font = ImageFont.truetype('/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuNerdFont-Regular.ttf', 20)
        font_title = ImageFont.truetype('/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuNerdFont-Bold.ttf', 22)
        font_title_small = ImageFont.truetype('/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuNerdFont-Bold.ttf', 21)  # 1pt smaller for page 2
        font_small = ImageFont.truetype('/usr/share/fonts/truetype/UbuntuNerdFont/UbuntuNerdFont-Regular.ttf', 16)  # Small font for auto-cycle indicator
        print("Ubuntu Nerd Font loaded (NerdFont)")
    except:
        # Use system default fonts as last resort
        font = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_title_small = ImageFont.load_default()
        font_small = ImageFont.load_default()
        print("Using default fonts (UbuntuNerdFont not found)")

def get_system_data():
    """
    Retrieve current system performance metrics.

    Collects real-time data including IP address, CPU usage, RAM usage,
    disk usage, and CPU temperature (converted to Fahrenheit).

    Returns:
        tuple: (ip_address, cpu_percent, ram_percent, disk_percent, temperature)
               All values are formatted as strings for display
    """
    # Get IP address by connecting to external DNS
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connect to Google DNS
        ip = s.getsockname()[0]      # Get local IP used for connection
        s.close()
    except:
        ip = "No Connection"

    # Get CPU usage percentage
    try:
        cpu = f"{psutil.cpu_percent(interval=0.1):.1f}%"
    except:
        cpu = "N/A"

    # Get RAM usage percentage
    try:
        ram = f"{psutil.virtual_memory().percent:.1f}%"
    except:
        ram = "N/A"

    # Get disk usage percentage for root filesystem
    try:
        disk = psutil.disk_usage('/')
        disk_pct = f"{(disk.used / disk.total) * 100:.1f}%"
    except:
        disk_pct = "N/A"

    # Get CPU temperature and convert to Fahrenheit
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp_celsius = int(f.read()) / 1000.0
            temp_fahrenheit = (temp_celsius * 9/5) + 32
            temp_str = f"{temp_fahrenheit:.1f}°F"
    except:
        temp_str = "N/A"

    return ip, cpu, ram, disk_pct, temp_str

def get_network_info():
    """
    Retrieve network interface statistics.

    Finds the first active ethernet interface and returns its
    data transmission statistics.

    Returns:
        tuple: (interface_name, bytes_sent_mb, bytes_received_mb)
               All values formatted as strings for display
    """
    try:
        interfaces = psutil.net_if_stats()
        net_io = psutil.net_io_counters(pernic=True)

        # Find first active ethernet interface
        eth_interface = None
        for interface in interfaces:
            if interface.startswith('eth') and interfaces[interface].isup:
                eth_interface = interface
                break

        if eth_interface and eth_interface in net_io:
            stats = net_io[eth_interface]
            sent_mb = stats.bytes_sent / (1024 * 1024)    # Convert to MB
            recv_mb = stats.bytes_recv / (1024 * 1024)    # Convert to MB
            return eth_interface, f"{sent_mb:.1f}MB", f"{recv_mb:.1f}MB"
        else:
            return "No Ethernet", "0 MB", "0 MB"
    except:
        return "Error", "N/A", "N/A"

def get_top_processes():
    """
    Get the top 5 processes by memory usage from all users, with username display.

    Uses RSS (Resident Set Size) memory and includes processes
    from all users, showing username for clarity.

    Returns:
        list: List of tuples (process_display_name, memory_percent)
              Limited to top 5 processes from all users
    """
    try:
        processes = []
        total_memory = psutil.virtual_memory().total

        # Get all processes with detailed memory and user info
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'username']):
            try:
                # Get memory info
                memory_info = proc.info['memory_info']
                if memory_info is None:
                    continue

                # Calculate RSS memory percentage (matches 'top' better)
                rss_bytes = memory_info.rss  # Resident Set Size
                memory_percent = (rss_bytes / total_memory) * 100

                # Include even smaller processes to match 'top' behavior
                if memory_percent > 0.05:  # Lower threshold to catch more processes
                    process_name = proc.info['name'] or f"PID-{proc.info['pid']}"
                    username = proc.info['username'] or "unknown"

                    # Create display name with user info for clarity
                    if username == "root":
                        display_name = process_name  # Just show process name for root
                    else:
                        # Keep full names for better display formatting
                        display_name = f"{username}:{process_name}"

                    processes.append((display_name, memory_percent))

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Skip processes we can't access
                continue
            except Exception:
                # Skip any other errors
                continue

        # Sort by memory usage (descending) and return top 5
        processes.sort(key=lambda x: x[1], reverse=True)
        return processes[:5]

    except Exception as e:
        print(f"Error getting processes: {e}")
        return [("Error", 0)]

def get_auto_cycle_status():
    """
    Get auto-cycle status information for display.

    Returns:
        tuple: (is_auto_cycling, time_until_next_cycle)
    """
    global last_auto_cycle_time, last_manual_interaction, manual_override_duration

    current_time = time.time()

    # Check if we're in manual override period
    time_since_manual = current_time - last_manual_interaction
    is_in_manual_override = time_since_manual < manual_override_duration

    if is_in_manual_override:
        # Manual override active - no auto-cycling
        return False, manual_override_duration - time_since_manual
    else:
        # Auto-cycling active
        time_since_last_cycle = current_time - last_auto_cycle_time
        time_until_next = AUTO_CYCLE_INTERVAL - time_since_last_cycle
        return True, max(0, time_until_next)

def create_page(page_num):
    """
    Create a page image with system information and auto-cycle status.

    Generates different pages based on page number:
    - Page 0: System information (IP, CPU, RAM, Disk, Temperature)
    - Page 1: Network information (Interface, Sent/Received data)
    - Page 2: Root processes by memory usage

    Each page has a unique color-coded title, consistent navigation instructions,
    and auto-cycle status indicator.

    Args:
        page_num (int): Page number to create (0, 1, or 2)

    Returns:
        PIL.Image: Generated page image ready for display
    """
    # Create blank image with black background
    image = Image.new("RGB", (WIDTH, HEIGHT), BLACK)
    draw = ImageDraw.Draw(image)

    # Get auto-cycle status
    is_auto_cycling, time_remaining = get_auto_cycle_status()

    if page_num == 0:
        # Page 0: System Information
        # =========================
        ip, cpu, ram, disk, temp = get_system_data()

        # Title with bright yellow color for easy identification
        draw.text((10, 8), "-- SYSTEM INFO --", font=font_title, fill=BRIGHT_YELLOW)

        # System metrics with consistent spacing
        draw.text((10, 35), f"IP: {ip}", font=font, fill=WHITE)
        draw.text((10, 55), f"CPU: {cpu}", font=font, fill=WHITE)
        draw.text((10, 75), f"RAM: {ram}", font=font, fill=WHITE)
        draw.text((10, 95), f"Disk: {disk}", font=font, fill=WHITE)
        draw.text((10, 115), f"Temp: {temp}", font=font, fill=WHITE)

        # Auto-cycle status
        if is_auto_cycling:
            mins, secs = divmod(int(time_remaining), 60)
            draw.text((10, 140), f"Auto: {mins}:{secs:02d}", font=font_small, fill=PURPLE)
        else:
            override_remaining = int(time_remaining)
            draw.text((10, 140), f"Manual: {override_remaining}s", font=font_small, fill=PURPLE)

        # Navigation instructions at bottom
        draw.text((10, 180), "Top: Next ->", font=font, fill=GREEN)
        draw.text((10, 205), "Bottom: <- Prev", font=font, fill=GREEN)

    elif page_num == 1:
        # Page 1: Network Information
        # ===========================
        interface, sent, recv = get_network_info()

        # Title with bright blue color
        draw.text((10, 8), "-- NETWORK INFO --", font=font_title, fill=BRIGHT_BLUE)

        # Network statistics
        draw.text((10, 35), f"Interface: {interface}", font=font, fill=WHITE)
        draw.text((10, 55), f"Sent: {sent}", font=font, fill=WHITE)
        draw.text((10, 75), f"Received: {recv}", font=font, fill=WHITE)

        # Auto-cycle status
        if is_auto_cycling:
            mins, secs = divmod(int(time_remaining), 60)
            draw.text((10, 100), f"Auto: {mins}:{secs:02d}", font=font_small, fill=PURPLE)
        else:
            override_remaining = int(time_remaining)
            draw.text((10, 100), f"Manual: {override_remaining}s", font=font_small, fill=PURPLE)

        # Navigation instructions
        draw.text((10, 180), "Top: Next ->", font=font, fill=GREEN)
        draw.text((10, 205), "Bottom: <- Prev", font=font, fill=GREEN)

    # Page indicator in top-right corner
    draw.text((WIDTH-25, 10), f"P{page_num}", font=font_title, fill=RED)

    return image

def check_auto_cycle():
    """
    Check if it's time to auto-cycle to the next page.

    Returns:
        bool: True if auto-cycle should occur, False otherwise
    """
    global last_auto_cycle_time, last_manual_interaction, current_page

    current_time = time.time()

    # Check if we're in manual override period
    time_since_manual = current_time - last_manual_interaction
    is_in_manual_override = time_since_manual < manual_override_duration

    if is_in_manual_override:
        # Don't auto-cycle during manual override
        return False

    # Check if it's time for auto-cycle
    time_since_last_cycle = current_time - last_auto_cycle_time

    if time_since_last_cycle >= AUTO_CYCLE_INTERVAL:
        # Time to auto-cycle
        current_page = (current_page + 1) % 3  # Cycle to next page
        last_auto_cycle_time = current_time
        print(f"Auto-cycled to page {current_page}")
        return True

    return False

def check_buttons():
    """
    Check button states and handle page navigation using gpiod for RPi 5.

    Implements debouncing logic to prevent multiple triggers from a single
    button press. Updates the global current_page variable when buttons
    are pressed and records manual interaction time.

    Button mapping:
    - Bottom button (GPIO 23): Previous page (decrements page number)
    - Top button (GPIO 24): Next page (increments page number)

    Pages wrap around: 0 -> 1 -> 2 -> 0 (forward) or 0 -> 2 -> 1 -> 0 (backward)

    Returns:
        bool: True if page changed, False otherwise
    """
    global current_page, last_button_a_state, last_button_b_state, last_manual_interaction, last_auto_cycle_time

    if not running:
        return False

    try:
        # Read current button states using gpiod (active low - pressed = 0)
        btn_a_pressed = btn_a_line.get_value() == 0  # Bottom button
        btn_b_pressed = btn_b_line.get_value() == 0  # Top button

        page_changed = False
        current_time = time.time()

        # Check bottom button (GPIO 23) - Previous page
        # Only trigger on press edge (was not pressed, now pressed)
        if btn_a_pressed and not last_button_a_state:
            current_page = (current_page - 1) % 3  # Wrap around: 0->2, 1->0, 2->1
            last_manual_interaction = current_time
            last_auto_cycle_time = current_time  # Reset auto-cycle timer
            print(f"Bottom button pressed! Switched to page {current_page} (manual override)")
            page_changed = True

        # Check top button (GPIO 24) - Next page
        # Only trigger on press edge (was not pressed, now pressed)
        if btn_b_pressed and not last_button_b_state:
            current_page = (current_page + 1) % 3  # Wrap around: 0->1, 1->2, 2->0
            last_manual_interaction = current_time
            last_auto_cycle_time = current_time  # Reset auto-cycle timer
            print(f"Top button pressed! Switched to page {current_page} (manual override)")
            page_changed = True

        # Update button states for next iteration (debouncing)
        last_button_a_state = btn_a_pressed
        last_button_b_state = btn_b_pressed

        return page_changed

    except Exception as e:
        if running:
            print(f"Button error: {e}")
        return False

def main():
    """
    Main application loop for Raspberry Pi 5 with auto-cycling functionality.

    Handles:
    - Display initialization with gpiod
    - Startup screen display
    - Main monitoring loop with button checking and auto-cycling
    - Periodic display updates (every 3 seconds for pages 0&1, 1.5 seconds for page 2)
    - Auto-cycling every 2 minutes (with manual override capability)
    - Graceful shutdown on Ctrl+C

    The main loop runs at 10Hz (100ms intervals) for responsive button handling
    while updating system data every 1.5-3 seconds and auto-cycling every 2 minutes
    to balance responsiveness with system load.
    """
    global running, last_auto_cycle_time, last_manual_interaction

    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    print("Mini PiTFT System Monitor - Raspberry Pi 5 Compatible with Auto-Cycling")
    print("=======================================================================")

    # Initialize display hardware
    if not init_display():
        print("Display initialization failed")
        return

    # Initialize timing variables
    current_time = time.time()
    last_auto_cycle_time = current_time
    last_manual_interaction = 0  # No manual interaction at start

    # Show startup screen with instructions
    print("Showing startup message...")
    startup_image = Image.new("RGB", (WIDTH, HEIGHT), BLACK)
    draw = ImageDraw.Draw(startup_image)
    draw.text((40, 80), "System Monitor", font=font_title, fill=WHITE)
    draw.text((60, 100), "RPi 5 Ready!", font=font, fill=GREEN)
    draw.text((30, 125), "Auto-Cycling: 2min", font=font_small, fill=PURPLE)
    draw.text((10, 160), "Top: Next ->", font=font, fill=BLUE)
    draw.text((10, 180), "Bottom: <- Prev", font=font, fill=BLUE)
    draw.text((10, 205), "Buttons pause auto", font=font_small, fill=PURPLE)
    display_image_corrected(startup_image)
    time.sleep(4)  # Show startup message for 4 seconds

    # Display initial page (page 0 - system info)
    print("Displaying initial page...")
    page_image = create_page(current_page)
    display_image_corrected(page_image)

    # Print control instructions to console
    print("\nAuto-Cycling Features:")
    print("  - Automatically cycles through pages every 2 minutes")
    print("  - Manual button presses pause auto-cycling for 10 seconds")
    print("  - Purple indicator shows auto-cycle status and timing")
    print("\nButton Controls:")
    print("  Bottom button: Previous page")
    print("  Top button: Next page")
    print("\nPages:")
    print("  Page 0: System Info (Yellow title)")
    print("  Page 1: Network Info (Blue title)")
    print("  Page 2: Top Processes (Orange title)")
    print("\nHardware:")
    print("  Using gpiod for Raspberry Pi 5 GPIO compatibility")
    print("  GPIO Chip: gpiochip4")
    print("\nPress Ctrl+C to exit")

    last_update = time.time()

    try:
        # Main monitoring loop
        while running:
            current_time = time.time()

            # Check for manual button presses and update display if page changed
            manual_page_change = check_buttons()

            # Check for auto-cycle page change (only if no manual change occurred)
            auto_page_change = False
            if not manual_page_change:
                auto_page_change = check_auto_cycle()

            # Update display if page changed (either manually or automatically)
            if manual_page_change or auto_page_change:
                print(f"Updating display for page {current_page}...")
                page_image = create_page(current_page)
                display_image_corrected(page_image)
                time.sleep(0.1)  # Brief pause after page change for debouncing

            # Different refresh rates for different pages
            refresh_interval = 1.5 if current_page == 2 else 3.0  # Page 2 refreshes faster

            # Update display with fresh data (but not more often than refresh interval)
            if current_time - last_update >= refresh_interval:
                page_image = create_page(current_page)
                display_image_corrected(page_image)
                last_update = current_time

            # Sleep briefly to prevent excessive CPU usage while maintaining responsiveness
            time.sleep(0.1)  # 10Hz loop rate

    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Ensure cleanup happens regardless of how we exit
        cleanup()

if __name__ == "__main__":
    """
    Entry point when script is run directly.

    This block only executes when the script is run as the main program,
    not when imported as a module.
    """
    main() Next ->", font=font, fill=GREEN)
        draw.text((10, 205), "Bottom: <- Prev", font=font, fill=GREEN)

    else:
        # Page 2: Top Processes
        # =====================
        processes = get_top_processes()

        # Title with bright orange color and slightly smaller font (21pt instead of 22pt)
        draw.text((10, 8), "-- TOP PROCESSES --", font=font_title_small, fill=BRIGHT_ORANGE)

        # List top processes with memory usage
        y = 35
        for i, (name, mem) in enumerate(processes):
            # Display process on single line without truncation
            draw.text((10, y), f"{i+1}. {name} {mem:.1f}%", font=font, fill=WHITE)
            y += 20  # 20px spacing between process entries

        # Auto-cycle status (positioned after processes)
        if is_auto_cycling:
            mins, secs = divmod(int(time_remaining), 60)
            draw.text((10, 155), f"Auto: {mins}:{secs:02d}", font=font_small, fill=PURPLE)
        else:
            override_remaining = int(time_remaining)
            draw.text((10, 155), f"Manual: {override_remaining}s", font=font_small, fill=PURPLE)

        # Navigation instructions
        draw.text((10, 180), "Top: