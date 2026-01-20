# 🔍 CAMERA DIAGNOSIS - FIND THE WORKING DEVICE

## Problem

The basic camera test found NO working cameras, even though:
- ✅ Camera is connected (shows in `lsusb`)
- ✅ Video devices exist (`/dev/video0`, `/dev/video1`, etc.)
- ✅ Permissions are correct (you're in `video` group)

## Solution: Comprehensive Test

I've created a new script that tests **EVERY device and backend combination** to find what actually works.

---

## 🚀 QUICK STEPS

### 1. Deploy the comprehensive test

Run [QUICK_FIX.bat](QUICK_FIX.bat) on your Windows computer:
```cmd
cd C:\Users\Juju\Desktop\PSU_ECOteam_offtrack_award
QUICK_FIX.bat
```

Password: `Aa12312312` (5 times now - one extra for new test script)

---

### 2. SSH into Pi

```bash
ssh pi@berryspie
# Password: Aa12312312
```

---

### 3. Run comprehensive camera test

```bash
python3 ~/racing/camera_test_all.py
```

This will test:
- **Devices**: `/dev/video0`, `/dev/video1`, `/dev/video19`, and numeric `0`, `1`, `19`, `20`, `21`
- **Backends**: Default, V4L2, GStreamer
- **All combinations**: 9 devices × 3 backends = 27 tests

---

### 4. Expected Output

**If it finds a working camera:**
```
============================================================
COMPREHENSIVE CAMERA TEST
============================================================

Testing all device and backend combinations...

✗ FAIL: /dev/video0 with Default backend - couldn't open
✗ FAIL: /dev/video0 with V4L2 backend - couldn't open
✗ FAIL: /dev/video0 with GStreamer backend - couldn't open
✗ FAIL: /dev/video1 with Default backend - couldn't open
✓ SUCCESS: /dev/video19 with V4L2 backend
  Resolution: 1280x720
✓ SUCCESS: 19 with V4L2 backend
  Resolution: 1280x720

============================================================
WORKING CONFIGURATIONS FOUND:
============================================================

1. Device: /dev/video19
   Backend: V4L2 backend
   Resolution: 1280x720
   Code: cap = cv2.VideoCapture('/dev/video19', 256)

2. Device: 19
   Backend: V4L2 backend
   Resolution: 1280x720
   Code: cap = cv2.VideoCapture(19, 256)

============================================================
RECOMMENDED FIX:
============================================================

Use this in your script:
  CAMERA_DEVICE = '/dev/video19'
  cap = cv2.VideoCapture(CAMERA_DEVICE, cv2.CAP_V4L2)
```

---

### 5. Fix the simple script

Once you know the working device (e.g., `/dev/video19`), edit the script:

```bash
nano ~/racing/gps_sync_streamer.py
```

Find line 23 and change:
```python
CAMERA_DEVICE = "/dev/video0"  # Change this to the working device
```

To (example if `/dev/video19` worked):
```python
CAMERA_DEVICE = "/dev/video19"  # Found by camera_test_all.py
```

If the test says you need V4L2 backend, also change the camera opening code.

Find around line 259:
```python
cap = cv2.VideoCapture(CAMERA_DEVICE)
```

Change to:
```python
cap = cv2.VideoCapture(CAMERA_DEVICE, cv2.CAP_V4L2)
```

Save (Ctrl+X, Y, Enter).

---

### 6. Run the fixed script

```bash
cd ~/racing
python3 gps_sync_streamer.py
```

Should now see:
```
[CAM] Camera opened: 1280x720 @ 30fps
```

---

## 🚨 IF NO CAMERAS WORK

If the comprehensive test finds **NO working cameras**, try:

### Option 1: Reboot Pi
```bash
sudo reboot
```

Then re-run the comprehensive test after reboot.

---

### Option 2: Check camera with v4l2-ctl

```bash
# Install if needed
sudo apt install v4l-utils

# List all devices
v4l2-ctl --list-devices

# Test capture on each device
v4l2-ctl --device=/dev/video0 --stream-mmap --stream-count=1
v4l2-ctl --device=/dev/video1 --stream-mmap --stream-count=1
v4l2-ctl --device=/dev/video19 --stream-mmap --stream-count=1
```

Look for which device successfully captures frames.

---

### Option 3: Check camera format

```bash
# Show supported formats
v4l2-ctl --device=/dev/video0 --list-formats-ext
```

Your camera might only support specific pixel formats.

---

### Option 4: Try libcamera (Raspberry Pi 5 uses this)

```bash
# Test with libcamera
libcamera-hello --list-cameras
libcamera-still -o test.jpg

# If this works, you might need to use libcamera instead of OpenCV
```

**If libcamera works but OpenCV doesn't**, we'll need to use a different approach with libcamera-vid piped to OpenCV.

---

## 📊 UNDERSTANDING THE RESULTS

### What the test shows:

1. **Which device number works**: `/dev/video0`, `/dev/video1`, `/dev/video19`, etc.
2. **Which backend works**: Default OpenCV, V4L2, or GStreamer
3. **What resolution you get**: 640x480, 1280x720, 1920x1080, etc.

### Common patterns:

- **Raspberry Pi 5 with USB cameras**: Often use `/dev/video0` or `/dev/video1`
- **Pi 5 with Camera Module**: Uses libcamera (not V4L2)
- **Multiple video devices**: Some are metadata-only (video19-35), only one is the actual camera
- **V4L2 backend**: Usually more reliable than default on Linux

---

## 🎯 NEXT ACTIONS

1. **Run QUICK_FIX.bat** on Windows ✓ (You should have already done this)
2. **SSH into Pi** ✓ (You're already in)
3. **Run comprehensive test**: `python3 ~/racing/camera_test_all.py` ← **DO THIS NOW**
4. **Tell me the results** - paste the output here
5. **I'll update the script** with the correct device
6. **Test if it works**

---

## 📞 QUICK REFERENCE

**Comprehensive test:**
```bash
python3 ~/racing/camera_test_all.py
```

**Check what devices exist:**
```bash
ls -la /dev/video*
v4l2-ctl --list-devices
```

**Check if camera is detected:**
```bash
lsusb | grep -i camera
```

**Reboot if needed:**
```bash
sudo reboot
```

---

**Run the comprehensive test now and paste the output!**
