# DJI Action 3 WiFi Setup - Quick Start

**Your Device:** OsmoAction3-38614A
**Password:** 50ec7a5e

---

## 5-Minute Setup

### Step 1: Enable DJI WiFi (on camera)
1. Power on DJI Action 3
2. Swipe down from top
3. Tap **Connections** → **Wi-Fi** → **ON**
4. You should see: `OsmoAction3-38614A` with WiFi icon

### Step 2: Connect Phone to DJI
1. Open phone **WiFi Settings**
2. Look for network: **OsmoAction3-38614A**
3. Tap to connect
4. Enter password: **50ec7a5e**
5. Wait 10-15 seconds for connection
6. ✅ Phone should show "Connected"

**Important:** Your phone will NOT have internet while connected to DJI WiFi. This is normal - the dashboard works offline!

---

## Step 3: Find DJI Stream URL

We need to find your DJI's stream URL. Try these methods:

### Method A: Use DJI Mimo App (Easiest)
1. Download **DJI Mimo** app from App Store/Play Store
2. Connect to DJI (should auto-detect)
3. Start live preview
4. Go to Settings → find stream URL

Common DJI URLs:
- `rtsp://192.168.42.1:8554/live`
- `http://192.168.42.1:8080/live.m3u8`

### Method B: Test in Browser
1. Make sure phone connected to `OsmoAction3-38614A` WiFi
2. Open browser
3. Try these URLs:
   - `http://192.168.42.1`
   - `http://192.168.42.1:8080`
   - `http://192.168.42.1:8080/live.m3u8`

If you see video or a player → that's your stream URL!

---

## Step 4: Update Stream URL (if needed)

If the default URL doesn't work, update it in `app/script.js`:

Current setting (line ~27):
```javascript
const DJI_WIFI_STREAM_URL = "rtsp://192.168.42.1:8554/live";
```

Change to whatever URL worked in Method A/B above.

---

## Step 5: Open Dashboard

1. Keep phone connected to **OsmoAction3-38614A** WiFi
2. Open Chrome or Safari
3. Go to: `https://psu-eco-team-off-trackcam-i5pq.vercel.app/app/`
4. Dashboard should load (works offline - cached)
5. You should see DJI camera feed!

**If you see "Loading camera...":**
- Check stream URL is correct
- Try different URLs from Step 3

---

## Step 6: Test with Telemetry

### Problem: Phone has no internet!

When connected to DJI WiFi, your phone can't reach the internet. But we need MQTT for telemetry!

### Solution: Use Mobile Hotspot

**Option A: Use Two Devices (Recommended)**
```
Device 1 (phone): Dashboard + DJI WiFi
Device 2 (tablet/laptop): MQTT Bridge
```

**Option B: WiFi Extender with Dual Band**
- Connect 2.4GHz to DJI
- Connect 5GHz to internet
- Some phones support this

**Option C: USB Webcam Mode Instead**
- Switch to `DJI_USB_WEBCAM = true`
- Phone can stay on cellular for MQTT
- Camera via USB, telemetry via internet

---

## Recommended: Switch to USB Mode

**Why USB is better:**
```
✅ Phone keeps cellular (MQTT works)
✅ Lower latency (100ms vs 200ms)
✅ More stable connection
✅ Phone charges camera
```

**To switch:**
1. In `app/script.js`, change line ~25:
   ```javascript
   const DJI_USB_WEBCAM = true;  // Change false to true
   ```
2. Connect DJI to phone via USB-C cable
3. On DJI: Settings → USB Mode → **Webcam**
4. Done!

---

## Testing Checklist

When connected to DJI WiFi:

- [ ] Phone WiFi shows: **OsmoAction3-38614A**
- [ ] Phone shows "Connected" (no internet symbol is OK)
- [ ] DJI screen shows WiFi icon
- [ ] Dashboard opens (cached version)
- [ ] Camera feed appears
- [ ] **Telemetry won't work** (no internet for MQTT)

**Solution:** Use USB mode or dual-device setup.

---

## Race Day Setup (WiFi Mode)

**Dual Device Setup:**

```
Device 1: Phone/Tablet
├── Connected to: OsmoAction3-38614A WiFi
├── Opens: Dashboard
└── Shows: Camera + Racing Line Overlay

Device 2: Phone/Laptop
├── Connected to: Cellular/Internet
├── Receives: MQTT Telemetry
└── Forward to: Device 1 (local network)
```

This requires MQTT bridge code - complex!

**OR just use USB mode - much simpler! ⭐**

---

## Quick Comparison

| Mode | Setup Time | Latency | MQTT Works? | Recommendation |
|------|------------|---------|-------------|----------------|
| **USB** | 30 sec | 100ms | ✅ Yes | ⭐ **Best** |
| **WiFi** | 5 min | 200ms | ❌ No* | Use for testing only |

*WiFi blocks cellular = no MQTT unless you have dual-device setup

---

## Your Device Info

Save this for reference:

```
Device Name: OsmoAction3-38614A
Password: 50ec7a5e
Default IP: 192.168.42.1
Stream URL: rtsp://192.168.42.1:8554/live (try this first)
Alt URL: http://192.168.42.1:8080/live.m3u8 (HLS fallback)
```

---

## Final Recommendation

**For Race Day: Use USB Mode!**

Change in `app/script.js`:
```javascript
const DJI_USB_WEBCAM = true;  // ← Change this
```

Why?
1. ✅ Dashboard gets camera via USB
2. ✅ Phone stays on cellular for MQTT
3. ✅ Everything works together
4. ✅ One device, one screen, simple!

WiFi mode is good for initial testing, but USB is better for racing.

---

## Need Help?

If WiFi streaming doesn't work:
1. Check DJI Mimo app can see live preview
2. Try both RTSP and HLS URLs
3. Check browser console for errors (F12)
4. **Or just switch to USB mode** (recommended!)

USB mode works out of the box - no URL hunting needed!
