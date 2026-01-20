# Auto-Start Setup Guide
**PSU Eco Racing Team - Automatic Recording & Dashboard on Boot**

## Overview
This guide sets up the Raspberry Pi to automatically:
- ✅ Start the camera streamer on boot
- ✅ Begin recording video immediately
- ✅ Serve the dashboard on `http://172.20.10.4:8001/app/`
- ✅ Restart automatically if it crashes

---

## Quick Setup (One-Time Setup)

### Step 1: Copy Files to Raspberry Pi

On your computer, run these commands:

```bash
cd Desktop\PSU_ECOteam_offtrack_award

# Copy all necessary files
scp pi_scripts\gps_sync_streamer.py pi@berryspie:~/racing/gps_sync_streamer.py
scp pi_scripts\racing-dashboard.service pi@berryspie:~/racing/racing-dashboard.service
scp pi_scripts\setup_autostart.sh pi@berryspie:~/racing/setup_autostart.sh
scp app\index.html pi@berryspie:~/racing/app/index.html
scp app\script.js pi@berryspie:~/racing/app/script.js
```

### Step 2: SSH into the Pi

```bash
ssh pi@berryspie
# Password: Aa12312312
```

### Step 3: Run Auto-Start Setup

```bash
cd ~/racing
chmod +x setup_autostart.sh
./setup_autostart.sh
```

**Done!** The system is now configured to start automatically on every boot.

---

## How It Works

### On Every Boot:
1. **Pi powers on** → Boots Raspberry Pi OS
2. **Systemd starts service** → Runs `racing-dashboard.service`
3. **Camera initializes** → Opens `/dev/video8` (Global Shutter Camera)
4. **GPS connects** → Opens `/dev/serial0` at 9600 baud
5. **Recording starts** → Begins saving to `/home/pi/racing/recordings/race_YYYYMMDD_HHMMSS.mp4`
6. **HTTP server starts** → Serves dashboard on port 8001
7. **MQTT connects** → Publishes GPS data to HiveMQ Cloud

### Auto-Recovery:
- If the service crashes, systemd **automatically restarts it** after 10 seconds
- Recordings are saved properly even if the service restarts

---

## Accessing the Dashboard

### From Any Device Connected to Pi Hotspot:

**WiFi Connection:**
- SSID: `Psuecoteam`
- Password: `shell123`

**URLs:**
- **Dashboard**: `http://172.20.10.4:8001/app/`
- **Camera Stream**: `http://172.20.10.4:8001/stream`
- **System Status**: `http://172.20.10.4:8001/status`
- **Recording Status**: `http://172.20.10.4:8001/recording/status`

---

## Managing the Service

### Check if Service is Running
```bash
sudo systemctl status racing-dashboard
```

**Expected output:**
```
● racing-dashboard.service - PSU Racing Dashboard - Camera Stream and Recording
   Loaded: loaded (/etc/systemd/system/racing-dashboard.service; enabled)
   Active: active (running) since Sun 2026-01-19 14:30:52 UTC; 5min ago
```

### View Live Logs
```bash
sudo journalctl -u racing-dashboard -f
```

Press `Ctrl+C` to stop viewing logs.

### Stop the Service
```bash
sudo systemctl stop racing-dashboard
```

### Start the Service
```bash
sudo systemctl start racing-dashboard
```

### Restart the Service
```bash
sudo systemctl restart racing-dashboard
```

### Disable Auto-Start (won't start on boot)
```bash
sudo systemctl disable racing-dashboard
```

### Enable Auto-Start (will start on boot)
```bash
sudo systemctl enable racing-dashboard
```

---

## Stopping a Recording Manually

Even though recording starts automatically, you can still stop it:

### Method 1: Via URL
```bash
curl http://172.20.10.4:8001/recording/stop
```

### Method 2: Via Browser
Visit: `http://172.20.10.4:8001/recording/stop`

### Method 3: Restart the Service
```bash
sudo systemctl restart racing-dashboard
```
This stops the current recording and starts a new one.

---

## Video Files Location

All recordings are saved to:
```
/home/pi/racing/recordings/
```

**Filename format:**
```
race_20260119_143052.mp4
race_YYYYMMDD_HHMMSS.mp4
```

### Viewing Recordings on Pi
```bash
ls -lh ~/racing/recordings/
```

### Copying Recordings to Your Computer
```bash
# From your computer
scp pi@berryspie:~/racing/recordings/*.mp4 ./
```

---

## Race Day Workflow

### Before the Race:
1. **Power on the Raspberry Pi**
2. **Wait 60 seconds** for boot and service to start
3. **Connect to WiFi hotspot**: `Psuecoteam` / `shell123`
4. **Verify dashboard is live**: Visit `http://172.20.10.4:8001/app/`
5. **Confirm recording started**: Visit `http://172.20.10.4:8001/recording/status`

### During the Race:
- Everything runs automatically
- Dashboard updates in real-time
- Video records continuously

### After the Race:
1. **Power off the Pi** (or let it keep running)
2. **Retrieve videos later** via SCP or USB drive

---

## Troubleshooting

### Dashboard Not Loading
**Check if service is running:**
```bash
sudo systemctl status racing-dashboard
```

**If stopped, start it:**
```bash
sudo systemctl start racing-dashboard
```

**View error logs:**
```bash
sudo journalctl -u racing-dashboard -n 50
```

### Camera Not Working
**Check camera device:**
```bash
v4l2-ctl --list-devices
```

**Restart the service:**
```bash
sudo systemctl restart racing-dashboard
```

### Recording Not Starting
**Check logs:**
```bash
sudo journalctl -u racing-dashboard | grep REC
```

**Check disk space:**
```bash
df -h /home/pi
```

**Manually start recording:**
```bash
curl http://172.20.10.4:8001/recording/start
```

### Service Won't Start on Boot
**Check if enabled:**
```bash
sudo systemctl is-enabled racing-dashboard
```

**If disabled, enable it:**
```bash
sudo systemctl enable racing-dashboard
```

**Check for errors:**
```bash
sudo journalctl -u racing-dashboard -xe
```

### Pi Hotspot Not Working
**Restart networking:**
```bash
sudo systemctl restart NetworkManager
```

**Or reboot the Pi:**
```bash
sudo reboot
```

---

## Disabling Auto-Start (Manual Mode)

If you want to run the system manually instead:

```bash
# Disable auto-start
sudo systemctl disable racing-dashboard
sudo systemctl stop racing-dashboard

# Run manually when needed
cd ~/racing
python3 gps_sync_streamer.py
```

---

## Storage Management

### Check Remaining Space
```bash
df -h /home/pi
```

### Delete Old Recordings
```bash
# List all recordings with sizes
ls -lh ~/racing/recordings/

# Delete specific video
rm ~/racing/recordings/race_20260119_143052.mp4

# Delete all recordings older than 7 days
find ~/racing/recordings/ -name "*.mp4" -mtime +7 -delete

# Keep only the 3 most recent videos
cd ~/racing/recordings/
ls -t *.mp4 | tail -n +4 | xargs rm
```

### Expected Storage Usage
- **Per race (35 minutes)**: ~700 MB - 1.4 GB
- **32 GB SD card**: Can hold ~20-40 races
- **Recommended**: Download and delete recordings after each race day

---

## System Architecture

```
┌─────────────────────────────────────────┐
│         Raspberry Pi 5 Boot             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  systemd starts racing-dashboard.service│
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│     python3 gps_sync_streamer.py        │
│  ┌───────────────────────────────────┐  │
│  │  • GPS Reader Thread              │  │
│  │  • Camera Capture Thread          │  │
│  │  • MQTT Publisher Thread          │  │
│  │  • Video Recording (Auto-Start)   │  │
│  │  • HTTP Server (Flask)            │  │
│  └───────────────────────────────────┘  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Available Services              │
│  • http://172.20.10.4:8001/app/        │
│  • http://172.20.10.4:8001/stream      │
│  • Recording: race_YYYYMMDD_HHMMSS.mp4 │
└─────────────────────────────────────────┘
```

---

## Advanced: Viewing Logs in Real-Time

### Follow All System Logs
```bash
sudo journalctl -u racing-dashboard -f
```

### Filter for Specific Events
```bash
# Only recording events
sudo journalctl -u racing-dashboard | grep REC

# Only camera events
sudo journalctl -u racing-dashboard | grep CAM

# Only GPS events
sudo journalctl -u racing-dashboard | grep GPS

# Only MQTT events
sudo journalctl -u racing-dashboard | grep MQTT
```

### Export Logs to File
```bash
sudo journalctl -u racing-dashboard > racing-logs.txt
```

---

## Updating the System

When you make changes to the code:

### Update and Restart
```bash
# On your computer
scp pi_scripts\gps_sync_streamer.py pi@berryspie:~/racing/gps_sync_streamer.py

# On the Pi
sudo systemctl restart racing-dashboard
```

### Update Service Configuration
```bash
# On your computer
scp pi_scripts\racing-dashboard.service pi@berryspie:~/racing/racing-dashboard.service

# On the Pi
sudo cp ~/racing/racing-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart racing-dashboard
```

---

## Quick Reference Card

**Print this and keep it at the track:**

```
═══════════════════════════════════════════════════════
  PSU ECO RACING - AUTO-START SYSTEM CHEAT SHEET
═══════════════════════════════════════════════════════

WIFI HOTSPOT:
  SSID: Psuecoteam
  Password: shell123

DASHBOARD URL:
  http://172.20.10.4:8001/app/

SYSTEM STATUS:
  sudo systemctl status racing-dashboard

VIEW LOGS:
  sudo journalctl -u racing-dashboard -f

RESTART DASHBOARD:
  sudo systemctl restart racing-dashboard

RECORDINGS LOCATION:
  /home/pi/racing/recordings/

DOWNLOAD RECORDINGS:
  scp pi@berryspie:~/racing/recordings/*.mp4 ./

SSH ACCESS:
  ssh pi@berryspie
  Password: Aa12312312

═══════════════════════════════════════════════════════
  ON BOOT: Everything starts automatically!
  Recording begins immediately.
  No manual intervention needed.
═══════════════════════════════════════════════════════
```

---

## Support

For troubleshooting during the race:
1. Check service status: `sudo systemctl status racing-dashboard`
2. View recent logs: `sudo journalctl -u racing-dashboard -n 50`
3. Restart if needed: `sudo systemctl restart racing-dashboard`

For more details, see:
- [VIDEO_RECORDING_GUIDE.md](VIDEO_RECORDING_GUIDE.md) - Recording details
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - General setup instructions
