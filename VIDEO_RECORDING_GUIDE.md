# Video Recording Setup Guide
**PSU Eco Racing Team - Camera Recording System**

## Overview
The Raspberry Pi camera streamer now supports **video recording** in addition to live streaming. Videos are saved as MP4 files with GPS-synced timestamps on the Raspberry Pi's SD card.

---

## Quick Start

### Option 1: Start Recording via URL (Easiest)
1. Make sure the Pi is running and streaming
2. Open a browser and navigate to:
   ```
   http://172.20.10.4:8001/recording/start
   ```
3. To stop recording:
   ```
   http://172.20.10.4:8001/recording/stop
   ```

### Option 2: Use curl Commands (Via SSH)
```bash
# Start recording
curl http://172.20.10.4:8001/recording/start

# Stop recording
curl http://172.20.10.4:8001/recording/stop

# Check recording status
curl http://172.20.10.4:8001/recording/status
```

---

## Setup Instructions

### Step 1: Update the Streamer Script on Pi
1. **SSH into the Raspberry Pi:**
   ```bash
   ssh pi@berryspie
   # Password: Aa12312312
   ```

2. **Navigate to the racing directory:**
   ```bash
   cd ~/racing
   ```

3. **Copy the updated script from your computer:**

   On your computer (Windows PowerShell or Command Prompt):
   ```bash
   scp pi_scripts/gps_sync_streamer.py pi@berryspie:~/racing/gps_sync_streamer.py
   ```

4. **Create the recordings directory:**
   ```bash
   mkdir -p ~/racing/recordings
   ```

### Step 2: Restart the Streamer
1. **Stop the current streamer** (if running):
   ```bash
   # Find the process
   ps aux | grep gps_sync_streamer

   # Kill it (replace XXXX with actual PID)
   kill XXXX
   ```

2. **Start the updated streamer:**
   ```bash
   cd ~/racing
   python3 gps_sync_streamer.py
   ```

   You should see output like:
   ```
   [REC] Recording enabled - videos will be saved to: /home/pi/racing/recordings
   [HTTP] Start recording: http://172.20.10.4:8001/recording/start
   [HTTP] Stop recording: http://172.20.10.4:8001/recording/stop
   ```

---

## How to Record a Race Session

### Before the Race
1. **Power on the Raspberry Pi** and wait for it to boot (~30 seconds)
2. **Connect to Pi hotspot:**
   - WiFi: `Psuecoteam`
   - Password: `shell123`
3. **Verify streaming is working:**
   - Open browser: `http://172.20.10.4:8001/stream`

### During the Race
**Method A: Manual Start/Stop**
1. When ready to start recording, visit: `http://172.20.10.4:8001/recording/start`
2. Drive the race
3. When done, visit: `http://172.20.10.4:8001/recording/stop`

**Method B: Auto-Start on Boot** (Optional)
If you want recording to start automatically when the Pi boots:
1. SSH into the Pi
2. Edit the script:
   ```bash
   nano ~/racing/gps_sync_streamer.py
   ```
3. Find these lines (around line 498):
   ```python
   # if ENABLE_RECORDING:
   #     start_recording()
   ```
4. Uncomment them:
   ```python
   if ENABLE_RECORDING:
       start_recording()
   ```
5. Save and exit (Ctrl+X, Y, Enter)
6. Restart the streamer

### After the Race
Videos are saved to: `/home/pi/racing/recordings/`

Filename format: `race_YYYYMMDD_HHMMSS.mp4`

Example: `race_20260119_143052.mp4`

---

## Retrieving Recorded Videos

### Option 1: SCP (Secure Copy) - Recommended
**From your computer:**
```bash
# Copy a specific video
scp pi@berryspie:~/racing/recordings/race_20260119_143052.mp4 ./

# Copy all videos
scp pi@berryspie:~/racing/recordings/*.mp4 ./
```

### Option 2: USB Drive
1. SSH into the Pi:
   ```bash
   ssh pi@berryspie
   ```

2. Insert USB drive into Pi

3. Find the USB drive:
   ```bash
   lsblk
   # Look for something like /dev/sda1
   ```

4. Mount it:
   ```bash
   sudo mkdir -p /mnt/usb
   sudo mount /dev/sda1 /mnt/usb
   ```

5. Copy videos:
   ```bash
   cp ~/racing/recordings/*.mp4 /mnt/usb/
   ```

6. Unmount safely:
   ```bash
   sudo umount /mnt/usb
   ```

### Option 3: FTP/SFTP Client
Use FileZilla or WinSCP:
- **Host:** `172.20.10.4` (or `berryspie`)
- **Protocol:** SFTP
- **Username:** `pi`
- **Password:** `Aa12312312`
- **Port:** 22
- **Navigate to:** `/home/pi/racing/recordings/`

---

## Configuration Options

Edit `/home/pi/racing/gps_sync_streamer.py`:

```python
# Video Recording settings
ENABLE_RECORDING = True  # Set to False to disable recording
RECORDING_DIR = "/home/pi/racing/recordings"  # Where to save videos
RECORDING_CODEC = "mp4v"  # MP4 codec
RECORDING_FORMAT = ".mp4"  # File format
```

### Camera Settings
```python
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30
```

---

## API Endpoints

### Start Recording
**URL:** `GET http://172.20.10.4:8001/recording/start`

**Response:**
```json
{
  "success": true,
  "filename": "/home/pi/racing/recordings/race_20260119_143052.mp4"
}
```

### Stop Recording
**URL:** `GET http://172.20.10.4:8001/recording/stop`

**Response:**
```json
{
  "success": true,
  "filename": "/home/pi/racing/recordings/race_20260119_143052.mp4"
}
```

### Check Recording Status
**URL:** `GET http://172.20.10.4:8001/recording/status`

**Response:**
```json
{
  "active": true,
  "filename": "/home/pi/racing/recordings/race_20260119_143052.mp4",
  "enabled": true
}
```

### Full System Status
**URL:** `GET http://172.20.10.4:8001/status`

**Response:**
```json
{
  "camera": {
    "device": "/dev/video8",
    "frames": 15432
  },
  "gps": {
    "latitude": 25.488435,
    "longitude": 51.450190,
    "speed_kmh": 35.2,
    "satellites": 8
  },
  "mqtt": {
    "connected": true,
    "broker": "8fac0c92ea0a49b8b56f39536ba2fd78.s1.eu.hivemq.cloud"
  },
  "recording": {
    "active": true,
    "filename": "/home/pi/racing/recordings/race_20260119_143052.mp4",
    "enabled": true
  }
}
```

---

## Storage Management

### Check Available Space
```bash
df -h /home/pi
```

**1280x720 @ 30fps MP4 video:**
- Approximate size: **~200-400 MB per 10 minutes**
- 35-minute race: **~700 MB - 1.4 GB**

### Delete Old Recordings
```bash
# View all recordings with sizes
ls -lh ~/racing/recordings/

# Delete specific video
rm ~/racing/recordings/race_20260119_143052.mp4

# Delete all videos older than 7 days
find ~/racing/recordings/ -name "*.mp4" -mtime +7 -delete

# Keep only the 5 most recent videos
cd ~/racing/recordings/
ls -t *.mp4 | tail -n +6 | xargs rm
```

---

## Troubleshooting

### Recording Won't Start
**Problem:** Visiting `/recording/start` returns error

**Solutions:**
1. Check if recording is already active:
   ```bash
   curl http://172.20.10.4:8001/recording/status
   ```

2. Check disk space:
   ```bash
   df -h /home/pi
   ```

3. Check if directory exists:
   ```bash
   ls -la ~/racing/recordings/
   ```

4. Restart the streamer:
   ```bash
   # On the Pi
   pkill -f gps_sync_streamer
   cd ~/racing
   python3 gps_sync_streamer.py
   ```

### Video File is Corrupted
**Problem:** Can't play the recorded video

**Causes:**
- Recording was not stopped properly (Pi lost power)
- SD card issues

**Solution:**
Try to repair with ffmpeg:
```bash
# On your computer (not Pi)
ffmpeg -i corrupted_video.mp4 -c copy fixed_video.mp4
```

### Out of Disk Space
**Problem:** Recording stops or won't start due to full disk

**Solution:**
```bash
# SSH into Pi
ssh pi@berryspie

# Check space
df -h

# Delete old recordings
rm ~/racing/recordings/race_2026*.mp4

# Or move to external USB
cp ~/racing/recordings/*.mp4 /mnt/usb/
rm ~/racing/recordings/*.mp4
```

### Can't Access Pi URLs
**Problem:** `http://172.20.10.4:8001` not reachable

**Solutions:**
1. Verify you're connected to the Pi hotspot:
   - WiFi: `Psuecoteam`
   - Password: `shell123`

2. Check if streamer is running:
   ```bash
   ssh pi@berryspie
   ps aux | grep gps_sync_streamer
   ```

3. Restart the streamer if needed

---

## Adding Recording Button to Dashboard (Optional)

You can add recording controls to the web dashboard by editing `~/racing/app/index.html`:

```html
<!-- Add to settings panel -->
<button onclick="startRecording()" style="...">START RECORDING</button>
<button onclick="stopRecording()" style="...">STOP RECORDING</button>
<div id="recordingStatus">Not Recording</div>
```

Add to `script.js`:
```javascript
function startRecording() {
    fetch('http://172.20.10.4:8001/recording/start')
        .then(r => r.json())
        .then(d => {
            if (d.success) {
                document.getElementById('recordingStatus').textContent = 'Recording...';
            }
        });
}

function stopRecording() {
    fetch('http://172.20.10.4:8001/recording/stop')
        .then(r => r.json())
        .then(d => {
            if (d.success) {
                document.getElementById('recordingStatus').textContent = 'Stopped';
                alert('Video saved: ' + d.filename);
            }
        });
}

// Check recording status on load
setInterval(() => {
    fetch('http://172.20.10.4:8001/recording/status')
        .then(r => r.json())
        .then(d => {
            document.getElementById('recordingStatus').textContent =
                d.active ? 'Recording...' : 'Not Recording';
        });
}, 2000);
```

---

## Performance Notes

- Recording runs in parallel with streaming - **no impact on live dashboard**
- Videos are saved with **full resolution** (1280x720)
- GPS data is NOT embedded in video (stored separately via MQTT)
- To sync video with GPS data later, match timestamps from filenames with MQTT logs

---

## Quick Reference Card

**Copy this and laminate for race day:**

```
PSU ECO RACING - VIDEO RECORDING CHEAT SHEET

WiFi: Psuecoteam / shell123
Pi IP: 172.20.10.4

START RECORDING:
http://172.20.10.4:8001/recording/start

STOP RECORDING:
http://172.20.10.4:8001/recording/stop

CHECK STATUS:
http://172.20.10.4:8001/recording/status

RETRIEVE VIDEOS (from computer):
scp pi@berryspie:~/racing/recordings/*.mp4 ./

VIDEOS LOCATION ON PI:
/home/pi/racing/recordings/

SSH: ssh pi@berryspie
Password: Aa12312312
```

---

## Contact
For technical support during the race, refer to the main [SETUP_GUIDE.md](SETUP_GUIDE.md)
