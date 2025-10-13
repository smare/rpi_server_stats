Project home directory: `/home/smare/dev/projects/server-stats-7789-display`

Script name: `setup_install_claude_RPi5_ST7789.py`

Runtime executible: `/usr/bin/python`

`*.service` files go here: `/etc/systemd/system/`

**_______________BEGIN_______________**
1) Start in directory `/home/smare/dev/projects/server-stats-7789-display`
2) ** Switch to root: `sudo -s` **
3) Perform the following commands
4) Install `/etc/systemd/system/setup_install_claude_RPi5_ST7789` service script
4a) `cd /etc/systemd/system/`
4b) `vi setup_install_claude_RPi5_ST7789.py`
4c) Copy and paste the following configurations one by one:
	a) `systemctl stop setup_install_claude_RPi5_ST7789.service`
	b) `systemctl disable setup_install_claude_RPi5_ST7789.service`
	c) `rm /etc/systemd/system/setup_install_claude_RPi5_ST7789.service`
	d) `systemctl daemon-reload`
	e) `systemctl reset-failed`

5) Create the service file: `vi setup_install_claude_RPi5_ST7789.service`
5a) Paste the following into vi (don't forget to enter `i` to switch to `INSERT` mode!)
```
Description=Displays server statistics on ST7789 displays.
After=network.target

[Service]
ExecStart=/usr/bin/python /home/smare/dev/projects/server-stats-7789-display/setup_install_claude_RPi5_ST7789.py
WorkingDirectory=/home/smare/dev/projects/server-stats-7789-display
StandardOutput=inherit
StandardError=inherit
Restart=always
User=smare

[Install]
WantedBy=multi-user.target
```
5b) Save file `:wq` then `cd /home/smare/dev/projects/server-stats-7789-display`

6) root@rpi5sysmon:/home/smare/dev/projects/server-stats-7789-display# `systemctl enable /etc/systemd/system/setup_install_claude_RPi5_ST7789.service`
`Created symlink /etc/systemd/system/multi-user.target.wants/setup_install_claude_RPi5_ST7789.service → /etc/systemd/system/setup_install_claude_RPi5_ST7789.service.`

7) `chmod +x /etc/systemd/system/setup_install_claude_RPi5_ST7789.py`

8) `systemctl enable setup_install_claude_RPi5_ST7789.service`

9) `systemctl start setup_install_claude_RPi5_ST7789.service`

10) `systemctl status setup_install_claude_RPi5_ST7789.service`

11) `exit` root profile

12) `sudo shutdown -r now`