# 🏎️ PSU Racing Dashboard - Quick Start for Drivers

## For Your Teammate (No Laptop Needed!)

### Setup (Do This Once):

**On Windows, deploy auto-start:**
```cmd
cd C:\Users\Juju\Desktop\PSU_ECOteam_offtrack_award
scp pi_scripts\setup_autostart.sh pi@berryspie:~/racing/
```

**On Pi (via SSH one time):**
```bash
cd ~/racing
chmod +x setup_autostart.sh
./setup_autostart.sh
```

Done! The dashboard will now start automatically every time the Pi boots.

---

## Race Day Instructions (For Your Teammate)

### 1. Power On the Pi
- Plug in the Raspberry Pi
- Wait 30-60 seconds for it to boot
- The dashboard starts **automatically**!

### 2. Connect to Pi WiFi
**On your phone:**
- WiFi Name: `Psuecoteam`
- Password: `shell123`

### 3. Open Dashboard
**In phone browser, go to:**
```
http://172.20.10.4:8001/app/
```

**That's it!** The camera, GPS, and telemetry will all be working.

---

## If Connected to Teammate's Hotspot Instead

If the Pi is connected to a phone hotspot instead of broadcasting its own WiFi:

### Find the Pi's IP Address
The Pi's IP will be different. Two options:

**Option A: Check router/hotspot settings**
- Look in your phone's hotspot connected devices
- Find device named "berryspie" or "raspberrypi"
- Note the IP (e.g., `192.168.x.x`)

**Option B: Use IP scanner app**
- Download "Fing" or similar network scanner app
- Scan network for device named "berryspie"
- Note the IP address

### Access Dashboard with New IP
Replace `172.20.10.4` with the actual IP:
```
http://192.168.x.x:8001/app/
```

---

## Troubleshooting

### Dashboard doesn't load?

**Wait 2 minutes** - Pi might still be booting.

**Check WiFi:** Make sure you're connected to `Psuecoteam` or the same network as the Pi.

**Try the stream directly:**
```
http://172.20.10.4:8001/stream
```
If this works but `/app/` doesn't, the script needs updating.

---

### Camera not showing?

**Refresh the page** - Sometimes the stream needs a moment to start.

**Check camera is connected** - Make sure USB camera is plugged into Pi.

---

### Pi is not broadcasting WiFi?

The Pi might be set to connect to a saved WiFi instead of being a hotspot.

**Solution:** Power cycle the Pi (unplug and replug).

If still not working, you'll need SSH access to reconfigure WiFi.

---

## Auto-Start Details

Once `setup_autostart.sh` is run:

✅ Dashboard starts automatically on boot
✅ Restarts if it crashes
✅ Cleans up camera/port conflicts automatically
✅ No SSH needed for normal operation

**Your teammate just needs to:**
1. Power on Pi
2. Connect to WiFi
3. Open the URL

---

## Advanced (Only if needed)

If you do have SSH access:

**Check if service is running:**
```bash
sudo systemctl status psu-racing
```

**View live logs:**
```bash
sudo journalctl -u psu-racing -f
```

**Restart service:**
```bash
sudo systemctl restart psu-racing
```

**Stop service:**
```bash
sudo systemctl stop psu-racing
```

**Disable auto-start:**
```bash
sudo systemctl disable psu-racing
```

---

## WiFi IP Address Reference

**Pi WiFi Hotspot Mode:**
- SSID: `Psuecoteam`
- Password: `shell123`
- Pi IP: `172.20.10.4`
- Dashboard: `http://172.20.10.4:8001/app/`

**Connected to Phone Hotspot:**
- Pi IP: Find using hotspot settings or Fing app
- Dashboard: `http://[PI_IP]:8001/app/`

---

## What Your Teammate Sees

When they open the dashboard, they'll see:
- 📹 Live camera feed with racing line overlay
- 🗺️ Track map with real-time car position
- ⚡ Speed, battery, current draw
- 📊 Lap times and efficiency metrics
- 🏁 Auto-timer that starts on movement

Everything works automatically - no buttons to press!

---

**Summary:** Power on, connect WiFi, open URL. That's it! 🏁
