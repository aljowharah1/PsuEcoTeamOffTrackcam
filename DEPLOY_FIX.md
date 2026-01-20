# CRITICAL FIX DEPLOYMENT GUIDE
**PSU Eco Racing - Camera & Dashboard Recovery**

## 🔴 PROBLEM SUMMARY

The camera stream is failing because:
1. ❌ OpenCV was using wrong backend (GStreamer instead of V4L2)
2. ❌ Camera device conflicts (multiple processes trying to use camera)
3. ❌ Wrong fallback device numbers
4. ❌ Frontend had wrong Pi IP address (172.20.10.2 instead of 172.20.10.4)

## ✅ FIXES APPLIED

### Backend Fixes ([pi_scripts/gps_sync_streamer.py](pi_scripts/gps_sync_streamer.py)):
1. ✅ **Line 26**: `CAMERA_DEVICE = "/dev/video0"` (correct device)
2. ✅ **Line 315**: Force V4L2 backend: `cv2.VideoCapture(CAMERA_DEVICE, cv2.CAP_V4L2)`
3. ✅ **Lines 317-323**: Better fallback logic (tries device 0, then 1)
4. ✅ **Lines 502-519**: New `kill_camera_users()` function to kill processes holding camera
5. ✅ **Lines 532-533**: Auto-kill camera conflicts on startup
6. ✅ **Lines 482-500**: Port conflict resolution (already present)
7. ✅ **Lines 553-555**: Auto-start recording on boot (already present)

### Frontend Fixes ([app/script.js](app/script.js)):
1. ✅ **Line 24**: Fixed `PI_HOST = "172.20.10.4"` (was 172.20.10.2)
2. ✅ **Lines 964-1032**: Camera retry logic with proper MJPEG handling (already present)

### Frontend ([app/index.html](app/index.html)):
1. ✅ **Line 32**: Removed inline onerror handler (already fixed)

---

## 📋 DEPLOYMENT STEPS

### Step 1: Kill All Running Instances on Pi

SSH into the Pi:
```bash
ssh pi@berryspie
# Password: Aa12312312
```

Kill all running instances:
```bash
pkill -f gps_sync_streamer
```

### Step 2: Deploy Updated Files from Windows

**On your Windows computer**, run these commands:

```bash
# Navigate to project directory
cd C:\Users\Juju\Desktop\PSU_ECOteam_offtrack_award

# Deploy Python script
scp pi_scripts\gps_sync_streamer.py pi@berryspie:~/racing/gps_sync_streamer.py

# Deploy updated dashboard
scp app\index.html pi@berryspie:~/racing/app/index.html
scp app\script.js pi@berryspie:~/racing/app/script.js
```

Password for all: `Aa12312312`

### Step 3: Start the Fixed Script

SSH back into Pi:
```bash
ssh pi@berryspie
cd ~/racing
python3 gps_sync_streamer.py
```

### Expected Output (SUCCESS):
```
==================================================
  PSU Racing - GPS-Synced Camera Streamer
==================================================
[PORT] Checking for conflicts on port 8001...
[CAM] Checking for camera conflicts...
[GPS] Opening /dev/serial0 at 9600 baud...
[GPS] Serial port opened successfully
[MQTT] Connecting to broker...
[CAM] Opening camera /dev/video0...
[CAM] Camera opened: 1280x720 @ 30fps  ← SUCCESS!
[MQTT] Connected to broker
[REC] Recording started: /home/pi/racing/recordings/race_20260119_HHMMSS.mp4
[REC] Auto-started recording on boot

[HTTP] Starting server on port 8001...
[HTTP] Stream URL: http://172.20.10.4:8001/stream
[HTTP] Status URL: http://172.20.10.4:8001/status
```

### Step 4: Verify Dashboard

1. **Connect to Pi WiFi:**
   - SSID: `Psuecoteam`
   - Password: `shell123`

2. **Open Dashboard:**
   - URL: `http://172.20.10.4:8001/app/`

3. **Check Camera Stream:**
   - Should see live video feed
   - No "Not Found" errors
   - No freezing after first frame

---

## 🔍 KEY CHANGES EXPLAINED

### Why V4L2 Backend?
OpenCV on Raspberry Pi defaults to GStreamer, which adds complexity and can fail. V4L2 (Video4Linux2) is the direct kernel interface and is more reliable.

**Old Code:**
```python
cap = cv2.VideoCapture(CAMERA_DEVICE)
```

**New Code:**
```python
cap = cv2.VideoCapture(CAMERA_DEVICE, cv2.CAP_V4L2)
```

### Why Kill Camera Conflicts?
Your error logs showed `Device '/dev/video0' is busy`. This means another process (probably an old instance of the script) was holding the camera.

**New Function:**
```python
def kill_camera_users():
    """Kill any process using the camera device."""
    result = os.popen(f"fuser {CAMERA_DEVICE} 2>/dev/null").read().strip()
    if result:
        pids = result.split()
        for pid in pids:
            os.kill(int(pid), signal.SIGTERM)
```

### Why Multiple Device Fallbacks?
Raspberry Pi can have multiple video device nodes. The new code tries:
1. `/dev/video0` with V4L2
2. Device `0` (numeric) with V4L2
3. Device `1` (numeric) with V4L2

This ensures it finds the camera even if the device number shifts.

---

## 🚨 IF IT STILL FAILS

### Check What Video Devices Exist
```bash
ls -la /dev/video*
v4l2-ctl --list-devices
```

### Check If Camera is Recognized
```bash
lsusb
# Should show "Global Shutter Camera" or similar
```

### Check If Process is Holding Camera
```bash
fuser /dev/video0
# Shows PID if camera is in use
```

### Manual Camera Test
```bash
# Install v4l-utils if not present
sudo apt install v4l-utils

# Test camera capture
v4l2-ctl --device=/dev/video0 --stream-mmap --stream-count=10
```

### View Full System Logs
```bash
sudo journalctl -u racing-dashboard -n 100
```

---

## 📊 TESTING CHECKLIST

After deployment, verify:

- [ ] Script starts without errors
- [ ] Camera opens: `[CAM] Camera opened: 1280x720 @ 30fps`
- [ ] Flask server runs: `Running on http://172.20.10.4:8001`
- [ ] Recording starts: `[REC] Recording started: .../race_YYYYMMDD_HHMMSS.mp4`
- [ ] Dashboard loads at `http://172.20.10.4:8001/app/`
- [ ] Camera stream shows live video (not "Not Found")
- [ ] Video doesn't freeze after first frame
- [ ] MQTT connected: `[MQTT] Connected to broker`

---

## 🎯 WHAT WORKED BEFORE (From Past Conversations)

Based on your conversation history:

### ✅ What Was Working:
1. GPS module reading NMEA sentences
2. MQTT publishing to HiveMQ Cloud
3. Flask HTTP server starting
4. Dashboard UI rendering
5. Racing line overlay logic
6. Video recording to MP4 files
7. Port conflict resolution

### ❌ What Was Failing:
1. Camera initialization (wrong device path)
2. Camera stream freezing (frontend race condition - FIXED)
3. Camera "busy" errors (multiple processes - NOW FIXED)
4. Wrong Pi IP in frontend (172.20.10.2 vs 172.20.10.4 - FIXED)
5. OpenCV backend issues (GStreamer failures - NOW FIXED with V4L2)

---

## 🔄 AUTO-START SETUP (After Manual Testing Works)

Once you confirm the script works manually, enable auto-start on boot:

```bash
cd ~/racing
chmod +x setup_autostart.sh
./setup_autostart.sh
```

This will:
- Install systemd service
- Enable auto-start on boot
- Start recording automatically
- Restart service if it crashes

**Service Commands:**
```bash
# Check status
sudo systemctl status racing-dashboard

# View logs
sudo journalctl -u racing-dashboard -f

# Restart
sudo systemctl restart racing-dashboard

# Stop
sudo systemctl stop racing-dashboard

# Disable auto-start
sudo systemctl disable racing-dashboard
```

---

## 📞 QUICK REFERENCE

**WiFi:** Psuecoteam / shell123
**SSH:** ssh pi@berryspie (password: Aa12312312)
**Dashboard:** http://172.20.10.4:8001/app/
**Stream:** http://172.20.10.4:8001/stream
**Status:** http://172.20.10.4:8001/status

**Kill Process:**
```bash
pkill -f gps_sync_streamer
```

**Deploy Files:**
```bash
scp pi_scripts\gps_sync_streamer.py pi@berryspie:~/racing/gps_sync_streamer.py
scp app\index.html pi@berryspie:~/racing/app/index.html
scp app\script.js pi@berryspie:~/racing/app/script.js
```

**Start Script:**
```bash
cd ~/racing
python3 gps_sync_streamer.py
```

---

## ✅ FILES MODIFIED

1. **pi_scripts/gps_sync_streamer.py** - Backend fixes
2. **app/script.js** - Fixed Pi IP address
3. **app/index.html** - Already correct (no changes needed)

All files are ready to deploy. Follow the steps above to get your system working!
