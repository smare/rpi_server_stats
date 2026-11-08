# rpi_server_stats

Display OS statistics (system info, network traffic and top processes) on a small display attached to a Raspberry Pi. The current display is the Mini PiTFT 1.3" (ST7789, 240x240) with two buttons. Pages change with the buttons, and automatically every 2 minutes.

## Which README do I need?

| Your Raspberry Pi | Script | Installer | Guide |
|-------------------|--------|-----------|-------|
| Raspberry Pi 5 or newer | `run_rpi5_stats_ST7789.py` (gpiod) | `prerequisites-run_rpi5_stats_ST7789.sh` | [doc/rpi5/README.md](doc/rpi5/README.md) |
| Raspberry Pi 4 or older | `run_rpi_stats_ST7789.py` (RPi.GPIO) | `prerequisites-run_rpi_stats_ST7789.sh` | [doc/rpi/README.md](doc/rpi/README.md) |

## Quick start

```bash
git clone https://github.com/smare/rpi_server_stats.git
cd rpi_server_stats

# Raspberry Pi 4 or older
bash ./prerequisites-run_rpi_stats_ST7789.sh
python3 run_rpi_stats_ST7789.py

# Raspberry Pi 5
bash ./prerequisites-run_rpi5_stats_ST7789.sh
python3 run_rpi5_stats_ST7789.py
```

If the installer asks you to reboot (it enabled SPI/I2C, or the SPI device is not active yet), reboot first and then run the script.

## Start at boot

See [set-up-script-as-a-service.md](set-up-script-as-a-service.md) to run the monitor as a systemd service.

Tested with Raspberry Pi 5, Raspberry Pi 4b, Raspberry Pi 3b+, Raspberry Pi Zero 2 W
