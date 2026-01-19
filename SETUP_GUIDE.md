# PSU Racing - Dashboard Setup Guide for Teammates

**Quick Guide: How to Access the Camera & Dashboard**

---

## Prerequisites

✅ Raspberry Pi 5 is powered ON
✅ USB Global Shutter Camera is connected
✅ GPS module is connected to GPIO pins
✅ You have a smartphone or tablet with WiFi

---

## Step 1: SSH into the Raspberry Pi

### On Windows:

1. **Open Command Prompt or PowerShell:**
   - Press `Win + R`
   - Type `cmd` or `powershell`
   - Press Enter

2. **SSH into the Pi:**
   ```bash
   ssh pi@berryspie
   ```
   Or using IP address:
   ```bash
   ssh pi@172.20.10.4
   ```

3. **Enter the password when prompted:**
   - Username: `pi`
   - Password: `Aa12312312`
   - **Note:** You won't see the password as you type (this is normal for security)

4. **First time connecting?** You'll see a warning:
   ```
   The authenticity of host '172.20.10.4' can't be established.
   Are you sure you want to continue connecting (yes/no)?
   ```
   - Type `yes` and press Enter

5. **You're in!** You should see:
   ```
   pi@berryspie:~ $
   ```

### On Mac/Linux:

1. **Open Terminal:**
   - Press `Cmd + Space`
   - Type `Terminal`
   - Press Enter

2. **SSH into the Pi:**
   ```bash
   ssh pi@berryspie
   ```
   Or using IP address:
   ```bash
   ssh pi@172.20.10.4
   ```

3. **Enter password:** `Aa12312312`

4. **You're in!** You should see:
   ```
   pi@berryspie:~ $
   ```

### Alternative: Use PuTTY (Windows)

1. **Download PuTTY** from https://putty.org
2. **Open PuTTY**
3. **Enter connection details:**
   - **Host Name:** `berryspie` or `172.20.10.4`
   - **Port:** `22` (This is the SSH port - standard for remote terminal access)
   - **Connection type:** `SSH`
4. **Click "Open"**
5. **Login when prompted:**
   - Username: `pi`
   - Password: `Aa12312312`

**What is Port 22?** Port 22 is the standard port for SSH (Secure Shell) connections. SSH allows you to securely access and control the Raspberry Pi remotely over the network.

---

## Step 2: Start the Camera Streamer on Raspberry Pi

1. **Once logged in via SSH, navigate to the scripts folder:**
   ```bash
   cd ~/racing
   ```

2. **Run the GPS-synced camera streamer:**
   ```bash
   python3 gps_sync_streamer.py
   ```

4. **Wait for confirmation messages:**
   ```
   [GPS] Serial port opened successfully
   [CAM] Camera opened: 1280x720 @ 10fps
   [MQTT] Connected to broker
   [HTTP] Starting server on port 8001...
   ```

5. **Keep this terminal window open** (the camera stream is now running)

---

## Step 3: Connect Your Phone/Tablet to the Pi Network

### Option A: Pi as WiFi Hotspot (Recommended for Race Day)

1. **On your phone**, go to WiFi settings
2. **Connect to the Pi's hotspot:**
   - **Network name:** `Psuecoteam`
   - **Password:** `shell123`

### Option B: Same Local Network (For Testing)

1. **Connect your phone to the same WiFi** as the Raspberry Pi
2. **Verify connection** by pinging:
   ```
   ping 172.20.10.4
   ```

---

## Step 4: Open the Dashboard on Your Phone

1. **Open your phone's web browser** (Chrome, Safari, Firefox)

2. **Type this URL in the address bar:**
   ```
   http://172.20.10.4:8001/app/
   ```

3. **Press Enter/Go**

4. **You should see:**
   - Live camera feed with racing line overlay
   - Speedometer (top right)
   - Lap counter
   - Current draw display
   - Countdown timer

---

## Step 5: Verify Everything is Working

### Check Camera Feed
- ✅ You should see live video from the forward-facing camera
- ✅ Video should update smoothly (~10 FPS)

### Check GPS Data
- ✅ Top-left should show GPS coordinates updating
- ✅ Green racing line should appear on the camera feed (once GPS has lock)

### Check Telemetry
- ✅ Speedometer should show "0 km/h" when stationary
- ✅ Current draw should update when vehicle is powered
- ✅ Lap counter shows "Lap 1"

---

## Troubleshooting

### Problem: Camera feed not showing

**Solution:**
1. Check camera is connected: `ls /dev/video*`
2. Restart camera streamer:
   ```bash
   # Press Ctrl+C to stop
   python3 gps_sync_streamer.py
   ```

### Problem: "Can't connect" error on phone

**Solution:**
1. Verify Pi IP address:
   ```bash
   hostname -I
   ```
2. Make sure your phone is on the same network
3. Try using the actual IP instead of 172.20.10.4

### Problem: Racing line not appearing

**Solution:**
1. Check GPS has satellite lock:
   ```bash
   # On Pi, visit:
   curl http://localhost:8001/gps
   ```
2. Wait 2-3 minutes for GPS to acquire satellites
3. GPS works best **outdoors** with clear sky view

### Problem: No telemetry data (voltage, current)

**Solution:**
1. Check MQTT connection:
   - Dashboard should show "MQTT offline" warning if disconnected
2. Verify Joulemeter is powered ON
3. Check MQTT credentials in script

### Problem: Dashboard is slow/laggy

**Solution:**
1. Close other apps on your phone
2. Reduce camera quality (edit `JPEG_QUALITY` in `gps_sync_streamer.py`)
3. Use a phone with better WiFi antenna

---

## Quick Command Reference

### Start Everything (Race Day)
```bash
# Only need ONE terminal!
cd ~/racing
python3 gps_sync_streamer.py
```
The camera streamer serves both the video AND the dashboard on port 8001.

### Stop Everything
```bash
# In each terminal, press:
Ctrl + C
```

### Check System Status
```bash
# Camera stream status:
curl http://172.20.10.4:8001/status

# GPS data:
curl http://172.20.10.4:8001/gps
```

### Reboot Pi (if needed)
```bash
sudo reboot
```

---

## Race Day Checklist

Before each race session:

- [ ] Pi is powered ON
- [ ] Camera is connected and visible (`ls /dev/video*`)
- [ ] GPS module is connected
- [ ] Camera streamer is running (Terminal 1)
- [ ] Dashboard server is running (Terminal 2)
- [ ] Driver's phone is connected to Pi network
- [ ] Dashboard loads at `http://172.20.10.4:8080/index.html`
- [ ] Camera feed is visible
- [ ] GPS has satellite lock (wait 2-3 min outdoors)
- [ ] Racing line overlay appears on screen
- [ ] Telemetry is updating (speed, current, voltage)

---

## URLs Quick Reference

| Service | URL | Purpose |
|---------|-----|---------|
| **Dashboard** | `http://172.20.10.4:8001/app/` | Main driver HUD |
| **Camera Stream** | `http://172.20.10.4:8001/stream` | Raw MJPEG video |
| **Camera Status** | `http://172.20.10.4:8001/status` | System diagnostics |
| **GPS Data** | `http://172.20.10.4:8001/gps` | Current GPS position |

---

## Contact

**Questions?** Ask Juju or check the main README.

**GitHub:** `PSU_ECOteam_offtrack_award`

---

**Good luck at Shell Eco-marathon Qatar 2026! 🏎️**
