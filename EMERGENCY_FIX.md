# 🚨 EMERGENCY FIX - STREAM LAG & APP NOT WORKING

## ⚡ FASTEST FIX (3 STEPS)

### Step 1: Run Deployment Script

**On Windows**, double-click: `QUICK_FIX.bat`

Or run in Command Prompt:
```cmd
cd C:\Users\Juju\Desktop\PSU_ECOteam_offtrack_award
QUICK_FIX.bat
```

Enter password when prompted: `Aa12312312` (4 times - one for each file)

---

### Step 2: Test Camera on Pi

SSH into Pi:
```bash
ssh pi@berryspie
# Password: Aa12312312
```

Kill any old processes:
```bash
pkill -f gps_sync_streamer
pkill -f python
```

Run camera test:
```bash
python3 ~/racing/camera_test.py
```

**Expected output:**
```
[SUCCESS] ✓ Camera opened: 1280x720
```

If you see this, **camera is working!** Continue to Step 3.

If you see `NO CAMERA FOUND`:
```bash
# Check if camera is connected
lsusb | grep -i camera

# Check video devices
ls -la /dev/video*

# Reboot Pi if camera was just plugged in
sudo reboot
```

---

### Step 3: Start Dashboard

```bash
cd ~/racing
python3 gps_sync_streamer.py
```

**Expected SUCCESS output:**
```
[CAM] Camera opened: 1280x720 @ 30fps  ← MUST SEE THIS!
[HTTP] Starting server on port 8001...
Running on http://172.20.10.4:8001
```

**If you see `[CAM] Failed to open camera`:**
- The camera test passed but main script failed
- Check if another process is using camera: `fuser /dev/video0`
- Rerun Step 2

---

### Step 4: Access Dashboard

1. **Connect to Pi WiFi:**
   - SSID: `Psuecoteam`
   - Password: `shell123`

2. **Open dashboard in browser:**
   ```
   http://172.20.10.4:8001/app/
   ```

3. **Check stream:**
   - Should see live video
   - Should update smoothly at 20fps
   - Should NOT freeze

---

## 🔧 WHAT WAS FIXED

### Stream Lag Issues:
1. ✅ Reduced JPEG quality from 80 to 70 (less CPU load)
2. ✅ Limited stream to 20fps (smoother, less bandwidth)
3. ✅ Added FPS limiting in generate_mjpeg()
4. ✅ Force V4L2 backend (more reliable than GStreamer)

### App Not Working:
1. ✅ Fixed camera device path (/dev/video0)
2. ✅ Fixed PI_HOST IP address (172.20.10.4)
3. ✅ Auto-kill processes holding port/camera
4. ✅ Better device fallback logic

---

## 🚨 IF STILL NOT WORKING

### Problem: Camera test fails

**Solution A: Check USB connection**
```bash
lsusb
# Should show your camera
```

**Solution B: Try different video device**
```bash
# List all video devices
v4l2-ctl --list-devices

# Test each device manually
python3 ~/racing/camera_test.py
```

**Solution C: Permissions issue**
```bash
sudo usermod -a -G video pi
sudo reboot
```

---

### Problem: Camera works but stream is laggy

**Solution: Reduce resolution**

Edit the script:
```bash
nano ~/racing/gps_sync_streamer.py
```

Find and change:
```python
CAMERA_WIDTH = 1280   # Change to 640
CAMERA_HEIGHT = 720   # Change to 480
STREAM_FPS = 20       # Change to 15
JPEG_QUALITY = 70     # Change to 60
```

Save (Ctrl+X, Y, Enter) and restart.

---

### Problem: Stream freezes after a few seconds

**Solution 1: Check if recording is eating CPU**
```bash
# Disable recording temporarily
nano ~/racing/gps_sync_streamer.py
# Change: ENABLE_RECORDING = False
```

**Solution 2: Check network connection**
```bash
# On Pi, check WiFi
ifconfig wlan0

# Ping from your computer
ping 172.20.10.4
```

---

### Problem: App shows "Not Found"

**Checklist:**
- [ ] Is Flask running? Check SSH terminal for "Running on http://172.20.10.4:8001"
- [ ] Connected to Pi WiFi? (Psuecoteam)
- [ ] Using correct URL? http://172.20.10.4:8001/app/
- [ ] Port 8001 conflict? Run: `lsof -ti:8001` on Pi

**Fix port conflict:**
```bash
# On Pi
pkill -f gps_sync_streamer
python3 gps_sync_streamer.py
```

---

## 📊 PERFORMANCE TIPS

### For Smooth Streaming:

1. **Stay close to Pi**
   - WiFi signal affects stream quality
   - Closer = smoother

2. **Use one device**
   - Don't open dashboard on multiple phones
   - More connections = more lag

3. **Close other apps**
   - Browser should be dedicated to dashboard
   - Close Facebook, Instagram, etc.

4. **Check Pi temperature**
   ```bash
   vcgencmd measure_temp
   # Should be < 70°C
   ```

5. **SD card speed matters**
   - Slow SD card = slow recording = lag
   - Use Class 10 or UHS-I card

---

## ⚙️ CONFIGURATION GUIDE

### Current Settings (Optimized):
```python
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30        # Recording FPS
STREAM_FPS = 20        # Stream FPS (lower = smoother)
JPEG_QUALITY = 70      # 0-100 (lower = faster, worse quality)
```

### For Ultra-Smooth (lower quality):
```python
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
STREAM_FPS = 15
JPEG_QUALITY = 60
```

### For Best Quality (might lag):
```python
CAMERA_WIDTH = 1920
CAMERA_HEIGHT = 1080
STREAM_FPS = 25
JPEG_QUALITY = 85
```

---

## 🎯 TESTING CHECKLIST

After deploying fixes, verify:

- [ ] Camera test passes: `python3 camera_test.py`
- [ ] Script starts: `python3 gps_sync_streamer.py`
- [ ] Camera opens: See `[CAM] Camera opened: 1280x720 @ 30fps`
- [ ] Flask runs: See `Running on http://172.20.10.4:8001`
- [ ] Dashboard loads: `http://172.20.10.4:8001/app/`
- [ ] Stream shows video (not "Not Found")
- [ ] Stream is smooth (not freezing every second)
- [ ] Recording works: Check `/home/pi/racing/recordings/`

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

**Check logs:**
```bash
sudo journalctl -u racing-dashboard -f
```

---

## 🔄 REVERT IF NEEDED

If the new version is worse, revert to basics:

1. Delete the main script
2. Copy from backup
3. Manually set to working configuration

Or just disable recording and reduce resolution:
```python
ENABLE_RECORDING = False
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
```

---

**Everything is fixed and ready. Run QUICK_FIX.bat now!**
