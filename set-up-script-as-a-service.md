# Setting Up the System Monitor as a Systemd Service

This guide walks through setting up either the RPi 5 (`run_rpi5_stats_ST7789.py`) or RPi ≤4 (`run_rpi_stats_ST7789.py`) script as a systemd service that starts automatically on boot.

## Prerequisites

- Script tested and working manually
- Project directory: `/home/smare/dev/projects/rpi_server_stats`
- Service files location: `/etc/systemd/system/`

## Choose Your Version

| Raspberry Pi Model | Script | Service Name |
|-------------------|--------|--------------|
| RPi 5 | `run_rpi5_stats_ST7789.py` | `pitft-rpi5-monitor.service` |
| RPi ≤4 (Zero, 3, 4) | `run_rpi_stats_ST7789.py` | `pitft-rpi-monitor.service` |

---

## Option A: Raspberry Pi 5 Setup

### Step 1: Remove Any Existing Service (if needed)

```bash
sudo systemctl stop pitft-rpi5-monitor.service 2>/dev/null
sudo systemctl disable pitft-rpi5-monitor.service 2>/dev/null
sudo rm -f /etc/systemd/system/pitft-rpi5-monitor.service
sudo systemctl daemon-reload
sudo systemctl reset-failed
```

### Step 2: Create the Service File

```bash
sudo nano /etc/systemd/system/pitft-rpi5-monitor.service
```

Paste the following content:

```ini
[Unit]
Description=Mini PiTFT System Monitor (RPi 5 - gpiod)
After=multi-user.target

[Service]
Type=simple
User=smare
WorkingDirectory=/home/smare/dev/projects/rpi_server_stats
ExecStart=/usr/bin/python3 /home/smare/dev/projects/rpi_server_stats/run_rpi5_stats_ST7789.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

### Step 3: Enable and Start the Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable pitft-rpi5-monitor.service
sudo systemctl start pitft-rpi5-monitor.service
```

### Step 4: Verify Status

```bash
sudo systemctl status pitft-rpi5-monitor.service
```

---

## Option B: Raspberry Pi ≤4 Setup (Zero, 3, 4)

### Step 1: Remove Any Existing Service (if needed)

```bash
sudo systemctl stop pitft-rpi-monitor.service 2>/dev/null
sudo systemctl disable pitft-rpi-monitor.service 2>/dev/null
sudo rm -f /etc/systemd/system/pitft-rpi-monitor.service
sudo systemctl daemon-reload
sudo systemctl reset-failed
```

### Step 2: Create the Service File

```bash
sudo nano /etc/systemd/system/pitft-rpi-monitor.service
```

Paste the following content:

```ini
[Unit]
Description=Mini PiTFT System Monitor (RPi.GPIO)
After=multi-user.target

[Service]
Type=simple
User=smare
WorkingDirectory=/home/smare/dev/projects/rpi_server_stats
ExecStart=/usr/bin/python3 /home/smare/dev/projects/rpi_server_stats/run_rpi_stats_ST7789.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

### Step 3: Enable and Start the Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable pitft-rpi-monitor.service
sudo systemctl start pitft-rpi-monitor.service
```

### Step 4: Verify Status

```bash
sudo systemctl status pitft-rpi-monitor.service
```

---

## Service Management Commands

Replace `SERVICE_NAME` with either `pitft-rpi5-monitor` or `pitft-rpi-monitor`:

| Action | Command |
|--------|---------|
| Check status | `sudo systemctl status SERVICE_NAME.service` |
| Start service | `sudo systemctl start SERVICE_NAME.service` |
| Stop service | `sudo systemctl stop SERVICE_NAME.service` |
| Restart service | `sudo systemctl restart SERVICE_NAME.service` |
| View logs | `sudo journalctl -u SERVICE_NAME.service -f` |
| View recent logs | `sudo journalctl -u SERVICE_NAME.service --since "10 minutes ago"` |
| Disable auto-start | `sudo systemctl disable SERVICE_NAME.service` |
| Enable auto-start | `sudo systemctl enable SERVICE_NAME.service` |

---

## Troubleshooting

### Service Won't Start

1. **Check logs:**
   ```bash
   sudo journalctl -u pitft-rpi5-monitor.service -n 50
   ```

2. **Test script manually:**
   ```bash
   cd /home/smare/dev/projects/rpi_server_stats
   python3 run_rpi5_stats_ST7789.py
   ```

3. **Check file permissions:**
   ```bash
   ls -la /home/smare/dev/projects/rpi_server_stats/run_rpi5_stats_ST7789.py
   chmod +x /home/smare/dev/projects/rpi_server_stats/run_rpi5_stats_ST7789.py
   ```

4. **Verify Python path:**
   ```bash
   which python3
   ```

### GPIO Permission Issues (RPi 5)

If gpiod can't access GPIO:

```bash
sudo usermod -a -G gpio smare
# Then logout and login, or reboot
```

### Service Status Meanings

| Status | Meaning |
|--------|---------|
| `Active (running)` | Working correctly |
| `Failed` | Error occurred - check logs |
| `Inactive (dead)` | Service stopped |
| `Activating` | Service starting up |

---

## Reboot and Verify

After setup, reboot to confirm the service starts automatically:

```bash
sudo reboot
```

After reboot, check service status:

```bash
sudo systemctl status pitft-rpi5-monitor.service
```

The display should show system stats within ~10 seconds of boot completing.
