# 🔙 RESTORE SIMPLE VERSION (NO RECORDING)

## What Changed

You're going back to the **original simple version** of the script that was working before video recording was added.

### What's Removed:
- ❌ Video recording to MP4 files
- ❌ Complex V4L2 backend forcing
- ❌ Port/camera conflict resolution
- ❌ Auto-start recording on boot

### What's Fixed:
- ✅ Camera device changed from `/dev/video8` to `/dev/video0`
- ✅ Simple fallback to device `0` if `/dev/video0` fails
- ✅ Uses default OpenCV backend (no V4L2 forcing)

### What Still Works:
- ✅ Live MJPEG camera streaming
- ✅ GPS data reading from UART
- ✅ MQTT telemetry publishing
- ✅ Flask HTTP dashboard
- ✅ Real-time GPS overlay capability

---

## 🚀 QUICK DEPLOYMENT

### Step 1: Run the Deployment Script

**On Windows**, double-click: [QUICK_FIX.bat](QUICK_FIX.bat)

Or in Command Prompt:
```cmd
cd C:\Users\Juju\Desktop\PSU_ECOteam_offtrack_award
QUICK_FIX.bat
```

This will deploy:
1. Camera test script
2. **Simple version** (gps_sync_streamer_SIMPLE.py → gps_sync_streamer.py)
3. Dashboard HTML
4. Dashboard JavaScript

Password: `Aa12312312` (4 times)

---

### Step 2: Test on Pi

SSH into the Pi:
```bash
ssh pi@berryspie
# Password: Aa12312312
```

Kill any old processes:
```bash
pkill -f gps_sync_streamer
pkill -f python
```

Test the camera:
```bash
python3 ~/racing/camera_test.py
```

Expected: `[SUCCESS] ✓ Camera opened: 640x480`

---

### Step 3: Start Simple Version

```bash
cd ~/racing
python3 gps_sync_streamer.py
```

**Expected Output:**
```
==================================================
  PSU Racing - GPS-Synced Camera Streamer
==================================================
[GPS] Opening /dev/serial0 at 9600 baud...
[GPS] Serial port opened successfully
[MQTT] Connecting to 8fac0c92ea0a49b8b56f39536ba2fd78.s1.eu.hivemq.cloud...
[CAM] Opening camera /dev/video0...
[CAM] Camera opened: 1280x720 @ 30fps

[HTTP] Starting server on port 8001...
[HTTP] Stream URL: http://172.20.10.4:8001/stream
[HTTP] Status URL: http://172.20.10.4:8001/status

Press Ctrl+C to stop.

 * Serving Flask app 'gps_sync_streamer'
 * Running on all addresses (0.0.0.0)
 * Running on http://172.20.10.4:8001
```

**Key differences from complex version:**
- ✅ No `[REC] Recording started` messages
- ✅ No port/camera conflict checking
- ✅ Simpler startup sequence
- ✅ Should be more stable and not crash

---

### Step 4: Access Dashboard

1. **Connect to Pi WiFi:**
   - SSID: `Psuecoteam`
   - Password: `shell123`

2. **Open dashboard:**
   ```
   http://172.20.10.4:8001/app/
   ```

3. **Verify:**
   - Live camera stream visible
   - GPS data updating
   - No freezing or lag
   - No "Not Found" errors

---

## 🔍 KEY DIFFERENCES

### Original Complex Version (gps_sync_streamer.py):
- 491 lines of code
- Video recording with cv2.VideoWriter
- V4L2 backend forcing
- Port/camera conflict resolution
- Process killing functions
- Auto-start recording on boot
- More complex, more prone to crashes

### Simple Version (gps_sync_streamer_SIMPLE.py):
- 330 lines of code
- **No video recording**
- Default OpenCV backend (no V4L2 forcing)
- No process management
- Simpler threading model
- More stable and reliable

---

## 📊 WHY THIS VERSION WORKS BETTER

1. **No V4L2 conflicts**: Uses default OpenCV backend which is more compatible
2. **No recording overhead**: Recording was eating CPU and causing crashes
3. **Simpler thread management**: Fewer threads = fewer race conditions
4. **Less resource intensive**: No MP4 encoding = smoother streaming
5. **Faster startup**: No conflict checking = quicker boot

---

## 🎯 TROUBLESHOOTING

### Problem: Camera still fails

**Solution**: Check if camera is at different device
```bash
ls -la /dev/video*
v4l2-ctl --list-devices
```

The simple version tries `/dev/video0` first, then falls back to device `0` (numeric).

---

### Problem: Script crashes after a few seconds

This **should not happen** with the simple version. If it does:

1. **Check if old complex version is still running:**
   ```bash
   ps aux | grep gps_sync
   pkill -f gps_sync_streamer
   ```

2. **Check for systemd service:**
   ```bash
   sudo systemctl status racing-dashboard
   sudo systemctl stop racing-dashboard
   sudo systemctl disable racing-dashboard
   ```

3. **Reboot Pi to clean slate:**
   ```bash
   sudo reboot
   ```

---

### Problem: Stream is still laggy

**Solution 1: Reduce quality**

Edit the script:
```bash
nano ~/racing/gps_sync_streamer.py
```

Find and change:
```python
CAMERA_WIDTH = 1280   # Change to 640
CAMERA_HEIGHT = 720   # Change to 480
JPEG_QUALITY = 80     # Change to 70
```

**Solution 2: Check WiFi signal**
- Get closer to Pi hotspot
- Only use one device at a time

---

## 📞 QUICK REFERENCE

**WiFi:** Psuecoteam / shell123
**SSH:** ssh pi@berryspie (Aa12312312)
**Dashboard:** http://172.20.10.4:8001/app/
**Stream:** http://172.20.10.4:8001/stream

**Kill processes:**
```bash
pkill -f gps_sync_streamer
```

**Test camera:**
```bash
python3 ~/racing/camera_test.py
```

**Start system:**
```bash
cd ~/racing && python3 gps_sync_streamer.py
```

---

## ✅ FILES DEPLOYED

1. [pi_scripts/camera_test.py](pi_scripts/camera_test.py) → `~/racing/camera_test.py`
2. [pi_scripts/gps_sync_streamer_SIMPLE.py](pi_scripts/gps_sync_streamer_SIMPLE.py) → `~/racing/gps_sync_streamer.py`
3. [app/index.html](app/index.html) → `~/racing/app/index.html`
4. [app/script.js](app/script.js) → `~/racing/app/script.js`

---

## 🔄 IF YOU WANT RECORDING BACK LATER

Once the simple version is stable and working, we can add recording back more carefully:

1. Start with the simple version working
2. Add recording as a **separate optional feature**
3. Make it disable-able with a flag
4. Test thoroughly before making it default

For now, focus on getting the **basic streaming working reliably**.

---

**The simple version is ready to deploy. Run QUICK_FIX.bat now!**
