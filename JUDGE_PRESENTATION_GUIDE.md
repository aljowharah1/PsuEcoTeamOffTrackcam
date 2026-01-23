# Shell Eco-Marathon Off-Track Award: Judge Presentation Guide

**PSU Eco Team I - Data and Telemetry Award**

---

## Part 1: Understanding Your System (What You Built)

### The Big Picture (30-Second Elevator Pitch)

"We built a **real-time augmented reality racing guidance system** that overlays the optimal racing line directly onto a live camera feed. The driver sees a glowing green path on their phone showing exactly where to drive for maximum energy efficiency. Unlike traditional dashboards that show numbers, our system provides **intuitive visual guidance** - the driver just follows the green line.

The system uses a **dual-data paradigm**: historical data from previous laps establishes the initial optimal path, and live data collected during each round is used to **continuously improve** the racing line between attempts. Each round makes the next one better."

---

### Core Components Explained

#### 1. The Racing Line Overlay API (`api/racing_line.py`)

**What it does:**
Converts GPS coordinates into screen pixel positions so we can draw the racing line on the camera feed.

**How it works:**
```
GPS Position → Haversine Distance → Heading Rotation → Perspective Projection → Screen Pixels
```

**Key algorithms:**

1. **Haversine Formula** - Calculates distance between two GPS points on Earth's curved surface
   - Formula: `d = 2R × arcsin(√(sin²(Δlat/2) + cos(lat1)×cos(lat2)×sin²(Δlon/2)))`
   - Why not Euclidean distance? Earth is spherical, not flat. At the equator, 1° longitude = 111km, but at 60°N it's only 55km.

2. **Heading Rotation** - Rotates world coordinates to camera's perspective
   - Uses rotation matrix: `[cos(θ), sin(θ); -sin(θ), cos(θ)]`
   - Why? The camera sees "forward" but GPS coordinates are in North-East orientation.

3. **Perspective Projection** - Makes close objects appear larger/lower, far objects smaller/higher
   - Horizon at 40% from top of screen
   - Close points (0.5m) appear at bottom (95% of screen height)
   - Far points (100m) appear near horizon

4. **Point Interpolation** - Creates smooth line by adding 10 points between each GPS coordinate
   - Raw GPS has ~47 points around track (points are far apart)
   - After interpolation: ~470 points for smooth rendering

**Why serverless (Vercel)?**
- No server maintenance needed
- Scales automatically under load
- Low latency (~50-100ms response time)
- Free tier sufficient for competition use

---

#### 2. The Dashboard (`app/script.js`)

**What it does:**
Receives telemetry via MQTT, displays live video with overlay, and tracks efficiency.

**Key features explained:**

1. **MQTT Connection** (lines 25-80)
   - Uses WebSocket over TLS (port 8884) for browser compatibility
   - HiveMQ Cloud broker handles message routing
   - Topics: `car/telemetry` (Joulemeter), `car/pi_gps` (camera GPS)

2. **Efficiency Calculation** (Wh/km tracking)
   ```javascript
   efficiency = (energy_wh / distance_km)  // Lower is better
   // Or inverted: km/kWh = distance_km / (energy_wh / 1000)  // Higher is better
   ```

3. **Lap Detection**
   - Uses GPS proximity to start/finish line (within 15m)
   - Requires minimum lap distance (>500m) to prevent false triggers
   - Auto-starts timer when speed > 0.5 km/h

4. **Racing Line API Integration**
   - Calls Vercel API with current GPS position
   - Receives array of [x, y] pixel coordinates
   - Draws green glowing path using HTML5 Canvas

---

#### 3. The Raspberry Pi System (`pi_scripts/gps_sync_streamer.py`)

**What it does:**
Captures camera video, reads GPS data, and publishes both with synchronized timestamps.

**Key components:**

1. **NMEA GPS Parsing**
   - Reads serial data at 9600 baud from GPIO UART
   - Parses $GPGGA (position), $GPRMC (speed), $GPVTG (heading)
   - Converts NMEA format to decimal degrees

2. **MJPEG Streaming**
   - Captures frames from USB camera using OpenCV
   - Encodes as JPEG and serves via HTTP
   - Client receives continuous image stream

3. **Timestamp Synchronization**
   - Attaches GPS timestamp to each frame
   - Enables correlation between video and Joulemeter data
   - Critical for accurate overlay positioning

---

#### 4. Ideal Lap Construction (Post-Race Analysis)

**What it does:**
Combines the best segments from ALL laps to create a theoretical optimal lap.

**Algorithm (from `shell_eco_v7_complete.ipynb`):**

1. **Segment**: Divide track into 4 quadrants (Q1-Q4) by GPS distance
2. **Calculate**: Compute km/kWh efficiency for each segment of each lap
3. **Filter**: Remove outliers (efficiency < 20 or > 500 km/kWh)
4. **Select**: For each quarter, pick the segment with HIGHEST efficiency
5. **Stitch**: Combine best segments into composite "ideal lap"

**Why this works:**
- Different laps have different strengths (one lap might have great Q1, another great Q3)
- Combining best segments gives theoretically optimal path
- Result: +47% improvement over best single lap

---

## Part 2: Technical Deep Dives (Know These Cold)

### GPS Mathematics

**Haversine Formula (Why We Use It):**
```python
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c  # Distance in km
```

**When asked "Why not just use Pythagorean distance?":**
"GPS coordinates are on a sphere, not a flat plane. The Pythagorean theorem only works on flat surfaces. At different latitudes, the same degree change represents different physical distances. Haversine accounts for Earth's curvature and gives accurate distances regardless of location."

---

### Camera Projection Mathematics

**Perspective Transformation Explained:**

```python
# 1. Calculate relative position (where is target relative to car?)
dx = haversine(car_lat, car_lon, car_lat, target_lon) * 1000  # East-West offset in meters
dy = haversine(car_lat, car_lon, target_lat, car_lon) * 1000  # North-South offset in meters

# 2. Rotate by heading (transform to camera's coordinate system)
heading_rad = math.radians(car_heading)
rel_x = dx * cos(heading) + dy * sin(heading)   # Left-Right in camera view
rel_y = -dx * sin(heading) + dy * cos(heading)  # Forward-Back in camera view

# 3. Calculate screen position using perspective projection
angle_h = atan2(rel_x, rel_y)  # Horizontal angle from center
px = screen_width/2 + (angle_h / (FOV/2)) * (screen_width/2)  # Pixel X

# Vertical uses inverse distance for perspective
distance_ratio = (rel_y - 0.5) / (100 - 0.5)  # 0=close, 1=far
py = ground_y - (distance_ratio * (ground_y - horizon_y))  # Pixel Y
```

**When asked "How do you handle different camera positions?":**
"The projection parameters are configurable - camera height, FOV, and lookahead distance. We currently assume 0.5m height and 120° horizontal FOV. For a different camera, we'd recalibrate these values by matching known track points to their screen positions."

---

### MQTT Architecture

**Why MQTT over HTTP Polling?**
| Aspect | MQTT | HTTP Polling |
|--------|------|--------------|
| Latency | ~10-50ms | ~100-500ms |
| Bandwidth | Low (push-based) | High (constant requests) |
| Battery | Efficient | Drains quickly |
| Real-time | True real-time | Simulated |

**Topic Structure:**
- `car/telemetry` - Joulemeter publishes energy data
- `car/pi_gps` - Pi publishes camera GPS for sync
- Both subscribe from dashboard for display

**Why HiveMQ Cloud?**
- Free tier with 100 connections
- TLS/SSL encryption built-in
- WebSocket support (works in browsers)
- No server maintenance

---

### Data Synchronization Strategy

**The Problem:**
We have two GPS sources (Joulemeter + Pi) with different sampling rates and network latencies.

**The Solution:**
```javascript
// Sync buffer stores recent readings
syncBuffer = {
    joulemeter: [...last 100 readings],
    pi_gps: [...last 100 readings]
}

// Match by GPS proximity (not timestamp!)
function findMatchingReading(piGps) {
    for (reading of joulemeter_buffer) {
        if (haversine(reading.lat, reading.lon, piGps.lat, piGps.lon) < 5) {
            return reading;  // Within 5 meters = match
        }
    }
}
```

**Why GPS proximity instead of timestamps?**
"Clocks can drift, but physics doesn't lie. If two GPS readings are within 5 meters of each other, they must be from approximately the same moment. This is more robust than trying to synchronize clocks across devices."

---

## Part 3: How to Talk to the Judge

### Opening Statement (Deliver with Confidence)

"Good [morning/afternoon]. I'm [Name] from PSU Eco Team I. We developed a Vision-Telemetry HUD system that fundamentally changes how drivers interact with efficiency data.

Traditional dashboards show numbers - voltage, current, speed. Our system shows the driver exactly where to drive by projecting an optimal racing line directly onto a live camera feed. The driver just follows the green line.

What makes our approach unique is the **continuous improvement loop**: every lap we drive makes the next lap's guidance better. We're not just displaying data - we're using data to actively optimize our race strategy in real-time."

---

### Key Selling Points (Memorize These)

1. **Reduced Cognitive Load**
   "Reading numbers while driving requires mental processing. Following a visual line is intuitive - it's how humans naturally navigate. This lets the driver focus on precise vehicle control rather than data interpretation."

2. **Data-Driven Improvement**
   "We don't guess at the optimal racing line - we calculate it from actual efficiency data. Each segment of our ideal lap comes from the most efficient execution of that segment across all recorded laps."

3. **+47% Theoretical Improvement**
   "Our composite ideal lap achieves 507 km/kWh compared to 344 km/kWh for the best single lap. That's 47% more efficient - not through hardware changes, but purely through data analysis and driver guidance."

4. **Rapid Strategy Updates**
   "Between rounds (5 minutes), we can process new telemetry and update the racing line. Round 2 incorporates everything we learned from Round 1. This creates a compounding advantage throughout competition day."

5. **Robust Fallback Modes**
   "If MQTT fails, we switch to phone GPS. If the racing line API is unavailable, we display stored coordinates. The system degrades gracefully - the driver always has guidance."

---

### Handling Skepticism

**If they say: "This seems over-engineered for an efficiency competition."**

"I understand that concern. But consider: in a competition where we're optimizing for km/kWh, even small inefficiencies compound over distance. A 2% deviation from the optimal line might cost 5% in efficiency due to unnecessary acceleration corrections. Our system ensures consistent execution of an optimized strategy - that consistency is what wins efficiency competitions."

**If they say: "How do you know the racing line is actually optimal?"**

"Great question. We don't assume - we measure. Each segment's efficiency is calculated from actual joule consumption and GPS distance. The segment with the highest km/kWh for each track quarter becomes part of our ideal lap. It's empirical, not theoretical. We can show you the data that proves segment X from lap Y was 23% more efficient than the average."

**If they say: "What about driver skill? Won't a bad driver still be inefficient?"**

"The racing line provides guidance, not guarantee. But that's exactly why visual guidance helps - it reduces the skill gap. A less experienced driver following a visible optimal path will outperform the same driver interpreting numbers. We're not replacing driver skill; we're augmenting it with data."

---

## Part 4: 20 Challenging Questions (With Answers)

### Technical Architecture

**Q1: Why did you choose MQTT over WebSockets for real-time data?**
"MQTT is specifically designed for IoT telemetry - it has built-in QoS levels, retained messages, and last-will-testament features. WebSockets would require us to build all of that infrastructure ourselves. MQTT also has lower overhead per message, which matters at 10Hz update rates."

**Q2: How do you handle GPS accuracy issues? Consumer GPS has 3-5m error.**
"You're right about the accuracy limitations. We mitigate this in several ways: First, we use 5-meter proximity matching for sync rather than exact coordinates. Second, our racing line interpolates between points, so small GPS errors average out over the path. Third, we apply Gaussian smoothing to remove jitter from the final racing line."

**Q3: Your serverless API is on Vercel. What happens if there's network latency or failure?**
"We've designed for degradation. The dashboard caches the last successful API response and can continue displaying the cached racing line during brief outages. For persistent failures, we store a pre-computed racing line JSON locally. Typical Vercel response times are 50-100ms, which is acceptable for 10Hz updates."

**Q4: How does the GPS-to-pixel projection handle camera lens distortion?**
"Currently, we assume a rectilinear (non-distorted) wide-angle lens with 120° FOV. For fisheye or barrel-distorted lenses, we'd need to apply inverse distortion correction before projection. Our current camera has minimal distortion, so this simplification is acceptable. For future versions, we could add a lens calibration step."

**Q5: What's the computational complexity of your nearest-point search?**
"Our current implementation is O(n) linear search through ~47 racing line points - which completes in microseconds and is perfectly acceptable. If we needed more points, we could implement a spatial index like an R-tree or grid-based lookup for O(log n) complexity. For this application, the simple approach is sufficient."

---

### Data Science / Algorithm Questions

**Q6: Explain your ideal lap construction algorithm. Why divide into quadrants?**
"We divide into quadrants because efficiency varies significantly by track section - straights vs. turns, uphill vs. downhill. Dividing by distance (not time) ensures consistent segment boundaries across laps. Four quadrants balance granularity against statistical significance - with 24 valid laps, each quadrant has 24 data points to compare."

**Q7: How do you handle outliers in your efficiency calculations?**
"We apply bounds filtering: any segment with efficiency below 20 km/kWh or above 500 km/kWh is flagged as an outlier. Below 20 suggests motor stall or measurement error. Above 500 suggests regenerative braking or GPS error causing negative energy calculation. These are removed before selecting 'best' segments."

**Q8: Your smoothing pipeline uses 4 stages. Isn't that over-processing?**
"Each stage addresses a different artifact. Gaussian removes GPS jitter (high-frequency noise). Spline interpolation creates continuous curves from discrete points. Distance resampling ensures even point spacing. Savitzky-Golay preserves turn features that might be over-smoothed by Gaussian. We validated this pipeline produces 80/100 combined smoothness/accuracy score."

**Q9: How do you validate that your ideal lap is actually achievable by a driver?**
"The ideal lap is constructed from segments that WERE actually driven - it's a composite of real executions, not a theoretical optimum. However, segment boundaries have discontinuities that require smoothing. We verify achievability by checking that turn radii don't exceed vehicle limits and that speed transitions are physically possible."

**Q10: What statistical methods ensure your efficiency comparisons are significant?**
"With 24 laps across 4 quadrants, we have 24 samples per segment. We calculate mean and standard deviation for each quadrant, then select the segment that's furthest above the mean (highest z-score). A segment must be at least 1 standard deviation above average to be considered significantly better."

---

### Real-Time Systems Questions

**Q11: What's your end-to-end latency from GPS reading to overlay display?**
"GPS reading: 0ms (continuous stream). NMEA parsing: ~1ms. MQTT publish: ~10-20ms (network dependent). Dashboard receive: ~10-20ms. API call: ~50-100ms. Canvas render: ~5ms. Total: approximately 80-150ms. At 25 km/h, the car moves ~0.7m in 100ms - within our 5m sync tolerance."

**Q12: How do you ensure the camera stream and overlay stay synchronized?**
"Both the camera frame and GPS reading are captured on the same Raspberry Pi with the same system clock. The GPS timestamp is attached to each frame's metadata. The overlay is calculated based on the GPS position that corresponds to that frame, not the 'current' position - this prevents the overlay from leading or lagging the video."

**Q13: What happens if the Pi CPU is overloaded?**
"We've profiled the load: MJPEG encoding uses ~30% CPU, GPS parsing ~5%, MQTT ~5%. Total ~40%, leaving headroom. If overload occurred, we'd prioritize camera streaming (driver needs to see) over GPS publishing (can interpolate). The systemd service auto-restarts on crash."

**Q14: How do you handle MQTT message ordering and duplicates?**
"MQTT QoS 1 guarantees at-least-once delivery, which can cause duplicates. We use GPS timestamps to detect and discard duplicates - if a message's timestamp matches the previous one, we skip it. For ordering, we process in arrival order but use timestamp comparison for sync buffer matching."

**Q15: Your dashboard runs in a browser. How do you handle JavaScript's single-threaded nature?**
"Heavy processing (sync buffer, efficiency calculations) runs asynchronously using async/await. Canvas rendering happens on requestAnimationFrame, which the browser optimizes for 60fps. MQTT callbacks are event-driven and return quickly. We avoid blocking operations that would freeze the UI."

---

### Competition / Strategy Questions

**Q16: How does this system actually improve race outcomes?**
"Three ways: First, consistent execution - the driver follows the same optimal path every lap rather than varying. Second, reduced errors - visual guidance prevents accidentally cutting corners or taking wrong lines. Third, continuous improvement - each round's data makes the next round's guidance better."

**Q17: What if the optimal racing line changes due to weather or track conditions?**
"The system adapts because it's based on efficiency, not fixed coordinates. If wet conditions make a particular line less efficient (more wheel slip = more energy), that segment's efficiency score drops, and a different segment becomes 'best' in the next ideal lap calculation. The guidance evolves with conditions."

**Q18: How long does between-rounds processing take?**
"Data export: ~30 seconds. Efficiency calculation: ~10 seconds. Best segment selection: ~5 seconds. Smoothing pipeline: ~20 seconds. JSON generation: ~5 seconds. Deployment: ~60 seconds. Total: under 3 minutes. With 5 minutes between rounds, we have margin for verification."

**Q19: What's your fallback if the entire system fails during a race?**
"The driver has trained without the system and knows the track. The car's basic Joulemeter display still shows speed and energy. We've practiced 'manual mode' racing. The technology enhances performance but isn't required for completion. Safety is never compromised by tech failure."

**Q20: Why should Shell give you the Off-Track Award over teams with more sensors or more complex systems?**
"Complexity isn't the goal - impact is. Our system directly improves the metric that matters: km/kWh. We take existing data (GPS, Joulemeter) and extract actionable guidance from it. The +47% theoretical improvement isn't from more sensors - it's from smarter data use. We've proven that the best efficiency gains come from optimizing what you have, not adding more hardware."

---

## Part 5: Demo Script (If You Get to Show the System)

### Live Demo Flow (3 minutes)

1. **Show Dashboard** (30 sec)
   "This is the driver view. You can see the live camera feed, the green racing line overlay, and the telemetry display. The driver just follows the green line."

2. **Show Racing Line Moving** (30 sec)
   "As the car moves [play test data], watch how the racing line updates. The perspective makes close points appear at the bottom and far points near the horizon - just like real depth perception."

3. **Show Efficiency Tracking** (30 sec)
   "Here's the real-time efficiency display. You can see current draw, speed, and the running Wh/km calculation. Lower is better."

4. **Show Ideal Lap Data** (30 sec)
   "After the race, we process telemetry. This table shows how we selected Q1 from Lap 10, Q2 from Lap 23, and so on - each the most efficient execution of that segment."

5. **Show Improvement** (30 sec)
   "The composite ideal lap achieves 507 km/kWh versus 344 for the best single lap. That's 47% improvement purely from data optimization."

6. **Wrap Up** (30 sec)
   "This creates a continuous improvement cycle. Every lap makes the next better. That's why we believe data-driven guidance is the future of efficiency racing."

---

## Quick Reference: Numbers to Know

| Metric | Value | Context |
|--------|-------|---------|
| Racing line points | 47 raw, ~470 interpolated | Lusail Short Circuit |
| Lookahead distance | 100 meters | How far ahead overlay shows |
| Camera FOV | 120° horizontal, 90° vertical | Wide-angle projection |
| MQTT latency | 10-20ms | HiveMQ Cloud |
| API latency | 50-100ms | Vercel serverless |
| Sync tolerance | 5 meters | GPS proximity matching |
| Best single lap | 344 km/kWh | Actual measured |
| Ideal composite | 507 km/kWh | Calculated optimal |
| Improvement | +47% | Theoretical max |
| Valid laps analyzed | 24 of 37 | After outlier removal |
| Update rate | ~10 FPS | Overlay refresh |
| Track length | 3.7 km | Lusail Short Circuit |

---

## Final Tips

1. **Be confident but not arrogant** - You know this system deeply. Let that knowledge show without dismissing questions.

2. **Admit limitations** - "That's a good point - we haven't optimized for that scenario yet, but here's how we'd approach it..."

3. **Connect to efficiency** - Every feature should tie back to km/kWh improvement.

4. **Show passion** - Judges can tell if you built this because you had to, or because you wanted to.

5. **Have fun** - You built something cool. Let that excitement come through.

Good luck!
