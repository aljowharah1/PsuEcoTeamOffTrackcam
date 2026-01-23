# GoPro Hero 7 Integration Guide

## Problem: Raspberry Pi 5 drains battery too fast
## Solution: Use GoPro Hero 7 for camera, keep Joulemeter for GPS/telemetry

---

## Architecture Change

### Before (Pi Camera Setup)
```
Raspberry Pi 5 + USB Camera + GPS Module
├── Camera Stream (MJPEG on port 8001)
├── GPS Data (MQTT to car/pi_gps)
└── Dashboard Server (port 5000)
     ↓
Phone displays: Camera + Overlay + Telemetry
```

### After (GoPro Setup)
```
GoPro Hero 7 → WiFi → Phone
     ↓
Camera Stream (via GoPro app or RTMP)

Joulemeter GPS → MQTT → Phone Dashboard
     ↓
GPS + Telemetry Data

Racing Line API (Vercel) → Overlay Coordinates
     ↓
Phone displays: GoPro feed + Overlay + Telemetry
```

---

## Method 1: GoPro Live Stream via RTMP (Recommended)

### What You Need
- GoPro Hero 7 Black (check model - only Black has live streaming)
- Phone with GoPro app installed
- RTMP streaming app on phone (VLC, Larix Broadcaster, or custom HTML5 player)

### Setup Steps

#### 1. Enable GoPro Live Streaming

On GoPro:
1. Swipe down → Preferences → Connections → Live
2. Enable "Live"
3. Set streaming quality (720p for lower latency, 1080p for quality)

#### 2. Get GoPro Stream URL

GoPro streams to RTMP URLs. You need to set up an RTMP receiver on your phone.

**Option A: Use Phone as RTMP Server**
- Install "RTMP Server" app on Android (or similar for iOS)
- Start server, note the URL (e.g., `rtmp://192.168.x.x:1935/live`)
- Configure GoPro to stream to this URL

**Option B: Direct WiFi Connection**
- Connect phone to GoPro WiFi hotspot
- GoPro creates stream at `udp://@:8554`
- Use VLC or custom player to view

#### 3. Modify Dashboard HTML

Your dashboard currently uses `<img>` for MJPEG. For GoPro, you need `<video>`:

**Change this (current Pi camera):**
```html
<img id="cameraStream" class="camera-feed" src="http://berryspie.local:8001/stream">
```

**To this (GoPro RTMP):**
```html
<video id="cameraStream" class="camera-feed" autoplay muted playsinline>
    <source src="YOUR_STREAM_URL" type="application/x-mpegURL">
</video>
```

---

## Method 2: GoPro USB Webcam Mode (Lower Latency)

### Requirements
- GoPro Hero 7 Black with latest firmware
- USB-C cable to phone
- Phone with USB OTG support

### Setup Steps

#### 1. Enable Webcam Mode on GoPro
GoPro Hero 7 doesn't officially support webcam mode (added in Hero 8+). **Skip this method if you have Hero 7 Silver/White.**

If you have Hero 7 Black with custom firmware:
1. Update to latest GoPro firmware
2. Connect via USB-C
3. Use third-party app to read USB video

---

## Method 3: GoPro WiFi Preview (Simplest - Best for Testing)

### How It Works
Use GoPro's live preview feature via WiFi.

### Setup Steps

#### 1. Connect Phone to GoPro WiFi
1. Turn on GoPro WiFi (swipe down → Connections → WiFi → ON)
2. Connect phone to GoPro's WiFi network (password shown on GoPro screen)

#### 2. Access GoPro Stream
GoPro Hero 7 preview is at: `http://10.5.5.9:8080/live/amba.m3u8`

#### 3. Update Dashboard to Use GoPro Stream

Edit `app/index.html`:

```html
<!-- Replace the img tag with video tag -->
<video id="cameraStream" class="camera-feed" autoplay muted playsinline></video>
```

Edit `app/script.js` (add this at the top of the file):

```javascript
// GoPro Stream Configuration
const GOPRO_STREAM_URL = "http://10.5.5.9:8080/live/amba.m3u8";
const USE_GOPRO = true;  // Set to false to use Pi camera

// Initialize video stream
function initializeVideoStream() {
    const videoElement = document.getElementById('cameraStream');

    if (USE_GOPRO) {
        // GoPro HLS stream
        if (Hls.isSupported()) {
            const hls = new Hls({
                enableWorker: true,
                lowLatencyMode: true,
                backBufferLength: 90
            });
            hls.loadSource(GOPRO_STREAM_URL);
            hls.attachMedia(videoElement);
            hls.on(Hls.Events.MANIFEST_PARSED, function() {
                videoElement.play();
            });
        } else if (videoElement.canPlayType('application/vnd.apple.mpegurl')) {
            // Safari native HLS support
            videoElement.src = GOPRO_STREAM_URL;
            videoElement.addEventListener('loadedmetadata', function() {
                videoElement.play();
            });
        }
    } else {
        // Use Pi camera MJPEG (original method)
        const piStreamUrl = `http://${window.location.hostname}:8001/stream`;
        videoElement.src = piStreamUrl;
    }
}

// Call this when page loads
window.addEventListener('DOMContentLoaded', initializeVideoStream);
```

#### 4. Add HLS.js Library

Add this to `app/index.html` in the `<head>` section:

```html
<!-- HLS.js for GoPro stream playback -->
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
```

---

## GPS Integration (Important!)

Since you're removing the Raspberry Pi, you lose the Pi GPS. **Two options:**

### Option A: Use Joulemeter GPS Only (Recommended)
Your Joulemeter already publishes GPS via MQTT topic `car/telemetry`. Your dashboard already reads this!

**No changes needed** - just remove the Pi and the dashboard will use Joulemeter GPS automatically.

### Option B: Use Phone GPS as Fallback
Your dashboard already has this feature built-in (GPS fallback mode). If MQTT fails, it uses phone GPS.

---

## Updated System Flow

```
┌─────────────────┐
│   GoPro Hero 7  │
│   (Camera Only) │
└────────┬────────┘
         │ WiFi (video stream)
         ↓
┌─────────────────────────────────┐
│        Driver's Phone           │
│  ┌───────────────────────────┐  │
│  │    Dashboard (Browser)    │  │
│  │  - GoPro video feed       │  │
│  │  - Racing line overlay    │  │
│  │  - Telemetry display      │  │
│  └───────────────────────────┘  │
└────────┬────────────────────────┘
         │ MQTT (receive telemetry)
         ↓
┌─────────────────┐
│  HiveMQ Cloud   │
│  MQTT Broker    │
└────────┬────────┘
         │ MQTT (publish)
         ↓
┌─────────────────┐
│   Joulemeter    │
│  - GPS          │
│  - Voltage      │
│  - Current      │
│  - Power        │
└─────────────────┘

         ↓ (Racing line calculation)
┌─────────────────┐
│  Vercel API     │
│ racing_line.py  │
└─────────────────┘
```

---

## Step-by-Step Implementation

### Step 1: Test GoPro Stream Access

1. Turn on GoPro Hero 7
2. Enable WiFi on GoPro
3. Connect your phone to GoPro WiFi (network name shown on GoPro screen)
4. Open VLC app on phone
5. Go to "Network Stream"
6. Enter: `http://10.5.5.9:8080/live/amba.m3u8`
7. If you see video → GoPro streaming works!

### Step 2: Modify Dashboard HTML

Save your current `app/index.html` as backup, then:

**Find this line (~line 32):**
```html
<img id="cameraStream" class="camera-feed" src="" alt="Pi USB Camera Stream" style="display:none;">
```

**Replace with:**
```html
<video id="cameraStream" class="camera-feed" autoplay muted playsinline></video>
```

**Add HLS.js before `</head>` tag:**
```html
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
```

### Step 3: Modify Dashboard JavaScript

Open `app/script.js`, find the camera initialization section (around line 30-50), and add:

```javascript
// ============== GOPRO STREAM SETUP ==============
const USE_GOPRO = true;  // Set to false to revert to Pi camera
const GOPRO_STREAM_URL = "http://10.5.5.9:8080/live/amba.m3u8";

function initCameraStream() {
    const video = document.getElementById('cameraStream');

    if (USE_GOPRO) {
        console.log("Initializing GoPro stream...");

        if (Hls.isSupported()) {
            const hls = new Hls({
                enableWorker: true,
                lowLatencyMode: true,
                backBufferLength: 90,
                maxBufferLength: 10
            });

            hls.loadSource(GOPRO_STREAM_URL);
            hls.attachMedia(video);

            hls.on(Hls.Events.MANIFEST_PARSED, () => {
                console.log("GoPro stream ready");
                video.play().catch(err => {
                    console.error("Autoplay failed:", err);
                });
            });

            hls.on(Hls.Events.ERROR, (event, data) => {
                console.error("HLS Error:", data);
                if (data.fatal) {
                    setTimeout(() => {
                        console.log("Retrying GoPro connection...");
                        hls.loadSource(GOPRO_STREAM_URL);
                    }, 3000);
                }
            });
        } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
            // Safari native HLS
            video.src = GOPRO_STREAM_URL;
            video.addEventListener('loadedmetadata', () => {
                video.play();
            });
        } else {
            console.error("HLS not supported in this browser");
        }
    } else {
        // Original Pi camera method
        const piUrl = `http://${window.location.hostname}:8001/stream`;
        video.src = piUrl;
    }
}

// Call on page load
window.addEventListener('DOMContentLoaded', initCameraStream);
```

### Step 4: Test Overlay Still Works

The racing line overlay draws on a canvas OVER the video. It should work identically regardless of video source.

Test by running test data replayer:
```bash
python3 test_data_replayer.py
```

You should see:
- GoPro video feed in background
- Green racing line overlay on top
- Telemetry data updating

---

## Latency Comparison

| Method | Latency | Quality | Battery Impact |
|--------|---------|---------|----------------|
| Pi USB Camera (original) | ~50ms | Good | High (Pi drains battery) |
| GoPro WiFi Preview | ~200-300ms | Excellent | Low (GoPro has own battery) |
| GoPro RTMP | ~300-500ms | Excellent | Low |
| GoPro USB Webcam | ~100ms | Excellent | Medium |

**200-300ms latency is acceptable** because:
- Racing decisions happen over seconds, not milliseconds
- The overlay shows path ahead, not instant position
- Driver reacts to the path, not frame-by-frame changes

---

## Troubleshooting

### Issue: Can't connect to GoPro stream
**Solution:**
- Verify GoPro WiFi is ON (swipe down → Connections → WiFi)
- Check phone is connected to GoPro network (not cellular data)
- Try accessing `http://10.5.5.9` in browser to verify connection

### Issue: Video shows but no overlay
**Solution:**
- Check browser console for errors
- Verify racing line API is accessible: `https://psu-eco-team-off-trackcam-i5pq.vercel.app/api/racing_line`
- Ensure MQTT telemetry is being received (check GPS data in dashboard)

### Issue: Overlay position is wrong
**Solution:**
- GoPro has different resolution than Pi camera (1920x1080 vs 1280x720)
- Update canvas size in `script.js`:
```javascript
const canvas = document.getElementById('overlayCanvas');
canvas.width = 1920;  // GoPro resolution
canvas.height = 1080;
```

### Issue: High latency (>1 second)
**Solution:**
- Check WiFi signal strength between phone and GoPro
- Reduce GoPro stream quality (Settings → Live → 720p instead of 1080p)
- Move GoPro closer to phone

---

## Dashboard Hosting Options

Without the Pi, you need to host the dashboard somewhere. **Three options:**

### Option 1: Host on Phone Locally
Use a local web server app:
- Android: "Simple HTTP Server" app
- iOS: "HTTP Server" app

Copy `app/` folder to phone, serve on port 8080, access at `http://localhost:8080`

### Option 2: Host on Vercel (Recommended)
Your dashboard is already on Vercel! Access at:
`https://psu-eco-team-off-trackcam-i5pq.vercel.app/app/`

**Advantage:** No local hosting needed, access from any device

### Option 3: Lightweight Device (Arduino/ESP32)
Use a tiny microcontroller to host the HTML files. Much lower power than Pi5.

---

## Power Budget Comparison

| Component | Power Draw | Battery Life (10,000mAh) |
|-----------|------------|--------------------------|
| Raspberry Pi 5 + Camera | ~15W | ~2 hours |
| GoPro Hero 7 | ~6W | Built-in battery (2+ hours) |
| Phone (dashboard) | ~3W | Existing phone battery |

**Result:** Removing Pi saves 15W, GoPro runs on its own battery. Car battery only powers Joulemeter now.

---

## Final Checklist

- [ ] GoPro Hero 7 fully charged
- [ ] GoPro WiFi enabled and password noted
- [ ] Phone has HLS.js player or VLC installed
- [ ] Dashboard HTML updated with `<video>` tag
- [ ] Dashboard JS updated with GoPro stream initialization
- [ ] Test GoPro stream in VLC first
- [ ] Test dashboard with test data replayer
- [ ] Verify racing line overlay appears correctly
- [ ] Verify Joulemeter GPS data flows to dashboard via MQTT
- [ ] Test at track before race day

---

## Quick Start Commands

### Test GoPro Connection
```bash
# On phone, open browser and go to:
http://10.5.5.9:8080/live/amba.m3u8
# Should download or prompt to open in video player
```

### Test Dashboard Locally
```bash
cd app/
python3 -m http.server 8080
# Open browser: http://localhost:8080
```

### Test Telemetry Data Flow
```bash
python3 test_data_replayer.py
# Should see telemetry updating in dashboard
```

---

## Racing Line Overlay - No Changes Needed!

The racing line overlay API doesn't need modification. It receives:
- GPS position (from Joulemeter via MQTT)
- Camera width/height (you'll update this to GoPro resolution)
- Returns pixel coordinates to draw

**Only change:** Update canvas resolution to match GoPro:

In `script.js`, find:
```javascript
overlayCanvas.width = 1280;
overlayCanvas.height = 720;
```

Change to:
```javascript
overlayCanvas.width = 1920;  // GoPro 1080p
overlayCanvas.height = 1080;
```

---

## Summary

**What you're changing:**
- ❌ Remove: Raspberry Pi 5 + USB Camera + Pi GPS
- ✅ Add: GoPro Hero 7 WiFi stream
- ✅ Keep: Joulemeter (GPS + telemetry via MQTT)
- ✅ Keep: Racing line overlay API
- ✅ Keep: Dashboard interface (just change video source)

**Result:**
- Lower power consumption (no Pi draining battery)
- Better image quality (GoPro vs USB camera)
- Slightly higher latency (~200ms vs 50ms) - acceptable
- Racing line overlay still works perfectly

Ready to implement? Let me know which method you want to use!
