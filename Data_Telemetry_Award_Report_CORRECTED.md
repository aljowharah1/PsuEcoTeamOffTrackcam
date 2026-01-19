# PSU Eco Team I: Data and Telemetry Award Report

**SA0003002: PSU Eco Team I, Prince Sultan University**
**Shell Eco-marathon 2026**

---

## Abstract

This report presents the design and implementation of a camera-based heads-up display (HUD) telemetry system developed for the Shell Eco-marathon competition. The system overlays real-time vehicle telemetry and optimal racing line guidance onto a live forward-facing camera feed, allowing the driver to maintain full visual awareness of the track while receiving continuous, data-driven guidance for energy-efficient driving.

The system operates on a dual-data paradigm: **historical telemetry** from previous race attempts establishes an initial ideal racing line and target speed profile based on energy efficiency (km/kWh), while **live telemetry** collected during each round is continuously integrated to refine and improve the optimal path. Between rounds, newly collected data is processed to generate updated guidance that incorporates the latest performance insights.

**During the race**, the driver views a live camera feed with a glowing green racing line overlay projected onto the track ahead, showing the optimal path to follow. Target speeds and deviation warnings are displayed in real-time. **After each round**, telemetry is analyzed to identify the most efficient segments, which are then incorporated into an improved ideal lap for the next attempt.

---

## 1. Introduction

In energy-limited competitions such as Shell Eco-marathon, marginal inefficiencies in speed control, racing line selection, or driver consistency can lead to disproportionate losses in overall performance. While Shell Eco-marathon vehicles are increasingly equipped with telemetry systems capable of recording detailed operational data, this information is often underutilized during the race itself.

Traditional dashboards typically present numerical indicators such as speed, current, or voltage, which require continuous interpretation by the driver. Under race conditions, this increases cognitive load and reliance on estimation, potentially leading to inconsistent execution of an otherwise well-designed strategy.

To address these limitations, this project introduces a **Vision-Telemetry HUD system** that directly links historical and live race data to in-car visual cues. By overlaying the optimal racing line onto a live camera feed of the track, the system provides intuitive guidance that supports precise and energy-efficient driving behavior—both during the race and through post-race analysis.

---

## 2. Data Concept

### 2.1 Dual-Data Paradigm

The system leverages two complementary data sources:

**Historical Data (Pre-Race):**
- Telemetry from previous test sessions and competition rounds
- Used to construct the initial ideal racing line
- Provides baseline target speeds for each track segment

**Live Data (During Race):**
- Real-time telemetry from Joulemeter (voltage, current, power, GPS)
- Real-time GPS from Pi camera system for video synchronization
- Used to display current position, speed, and deviation from ideal line
- Logged for post-race analysis and ideal lap refinement

### 2.2 Key Parameters

| Category | Parameters | Purpose |
|----------|------------|---------|
| Energy | Voltage, current, power, energy (Wh) | Efficiency calculation |
| Position | GPS latitude, longitude, heading | Racing line overlay, lap detection |
| Motion | Speed (km/h), RPM, distance | Performance tracking |
| Video | Camera frames, timestamps | HUD overlay background |

---

## 3. System Architecture

*See Diagram A.1: System Architecture (`diagrams/system_architecture.puml`)*

Our telemetry system is built around a distributed architecture with two sensor systems communicating via MQTT cloud broker:

### 3.1 Sensor System 1: Joulemeter (Vehicle Telemetry)

- **Joulemeter ECU**: Measures voltage, current, and power directly from the vehicle's electrical system
- **Vehicle GPS**: Provides position data for lap detection and racing line correlation
- **Wheel Encoder**: Measures RPM and calculates distance traveled

### 3.2 Sensor System 2: Pi Camera (Vision & Sync)

- **USB Global Shutter Camera**: Captures 1280x720 video at 10fps for HUD background
- **GPS Module (Pi)**: Dedicated GPS for video-telemetry timestamp synchronization
- **MJPEG Streaming**: Serves live video feed on local network (port 8001)

### 3.3 Processing Layer

- **Raspberry Pi 5**: GPS-camera synchronization, MJPEG encoding, NMEA parsing
- **Vercel Serverless API**: Racing line overlay calculations (`/api/racing_line`)
- **Client-side JavaScript**: Real-time telemetry display, canvas overlay rendering

### 3.4 Communication Layer

- **MQTT Protocol**: HiveMQ Cloud broker for telemetry transmission
  - `car/telemetry`: Joulemeter data (voltage, current, power, speed, GPS)
  - `car/pi_gps`: Pi camera GPS for video frame synchronization
- **HTTP MJPEG Stream**: Camera feed served via Flask on port 8001
- **REST API**: Racing line calculations via Vercel serverless functions

---

## 4. Real-Time HUD Display (During Race)

### 4.1 Driver Interface

The driver views a mobile dashboard displaying:

**Camera Feed Background:**
- Live MJPEG stream from forward-facing USB camera
- Full track visibility maintained at all times

**Racing Line Overlay (Canvas):**
- Green glowing path projected onto camera view showing optimal trajectory
- Updates in real-time based on current GPS position and heading
- 40-meter lookahead distance for anticipation

**HUD Elements:**
- **Target Speed**: Current segment's optimal speed displayed on overlay
- **Deviation Warning**: "X.Xm OFF" alert when deviating from racing line (yellow >3m, red >5m)
- **Speedometer**: Large digital display showing current speed
- **Current Draw**: Real-time amperage display
- **Lap Counter**: Current lap number
- **Countdown Timer**: 35-minute race timer with auto-start on movement

### 4.2 Racing Line Projection

The racing line is projected from GPS coordinates to screen pixels using perspective transformation:

```javascript
function drawRacingLineOverlay(overlayData) {
    // Green glow effect for racing line
    overlayCtx.strokeStyle = '#00ff88';
    overlayCtx.lineWidth = 6;
    overlayCtx.shadowColor = '#00ff88';
    overlayCtx.shadowBlur = 15;

    // Draw path from overlay points
    overlayCtx.beginPath();
    overlayCtx.moveTo(points[0][0], points[0][1]);
    for (let i = 1; i < points.length; i++) {
        overlayCtx.lineTo(points[i][0], points[i][1]);
    }
    overlayCtx.stroke();

    // Deviation warning
    if (overlayData.deviation_m > 3) {
        overlayCtx.fillStyle = overlayData.deviation_m > 5 ? '#ff4444' : '#ffaa00';
        overlayCtx.fillText(`${overlayData.deviation_m.toFixed(1)}m OFF`, ...);
    }
}
```

### 4.3 GPS-to-Pixel Transformation

*See Diagram A.6: GPS-to-Pixel Projection Algorithm (`diagrams/gps_projection.puml`)*

The Racing Line API calculates overlay coordinates using:

1. **Haversine Distance**: Calculate relative position in meters
2. **Heading Rotation**: Rotate coordinates by car's current heading
3. **Perspective Projection**: Convert 3D world position to 2D screen pixels
4. **FOV Clipping**: Only display points within camera field of view

Camera parameters:
- **Height**: 0.8m from ground
- **Horizontal FOV**: 118° (wide-angle lens)
- **Vertical FOV**: 69°
- **Lookahead**: 40m maximum

---

## 5. Post-Race Analysis & Strategy Refinement

### 5.1 Ideal Lap Construction

*See Diagram A.3: Ideal Lap Construction Algorithm (`diagrams/ideal_lap_algorithm.puml`)*

After each race round, the Ideal Lap Optimizer processes all telemetry:

1. **Segment**: Divide each lap into 4 quarters (Q1-Q4) by GPS distance
2. **Calculate**: Compute efficiency (km/kWh) for each segment of each lap
3. **Filter**: Remove outliers using statistical bounds (20-500 km/kWh valid range)
4. **Select**: For each quarter, choose the segment with highest efficiency across ALL laps
5. **Combine**: Merge selected segments into a composite "ideal lap"

**Example Results (24-lap test session):**

| Quarter | Best Source Lap | Efficiency (km/kWh) |
|---------|-----------------|---------------------|
| Q1 | Lap 10 | 987.1 |
| Q2 | Lap 23 | 642.2 |
| Q3 | Lap 23 | 608.1 |
| Q4 | Lap 3 | 246.2 |
| **Ideal Composite** | - | **507.0** |
| Best Single Lap | Lap 19 | 344.3 |
| **Improvement** | - | **+47.2%** |

### 5.2 Racing Line Smoothing

Raw GPS paths from different laps have discontinuities at segment boundaries. A 4-stage smoothing pipeline is applied:

1. **Gaussian Filter** (σ=2): Remove GPS jitter
2. **Spline Interpolation** (s=0.00005): Create smooth curves
3. **Distance Resampling** (1-2m spacing): Ensure even point distribution
4. **Savitzky-Golay** (window=11): Final polish preserving features

### 5.3 Between-Round Updates

The system enables rapid strategy refinement:

1. Round 1 telemetry is automatically logged via MQTT
2. Between rounds (~5 minutes), data is processed to generate updated ideal lap
3. New racing line JSON is deployed to the dashboard
4. Round 2 begins with improved guidance incorporating Round 1 insights

---

## 6. Data Synchronization

### 6.1 Video-Telemetry Sync

The Pi camera system publishes GPS timestamps alongside video frames:

```python
gps_state.to_dict() = {
    "latitude": 25.488435,
    "longitude": 51.450190,
    "speed_kmh": 24.5,
    "heading": 45.2,
    "gps_timestamp": "2026-01-06T10:30:45.123456+00:00",
    "pi_timestamp": "2026-01-06T10:30:45.150000+00:00"
}
```

### 6.2 Sync Buffer

The dashboard maintains a `syncBuffer` that correlates Joulemeter telemetry with Pi GPS data:

- Stores last 100 packets from each source
- Matches readings by GPS proximity (within 5 meters)
- Enables accurate overlay projection even with timing differences

### 6.3 GPS Distance Correction

Wheel-based odometry suffers from tire slip and calibration errors. GPS-based distance calculation using the Haversine formula achieves ±0.5% accuracy compared to ±3-5% from wheel encoders.

---

## 7. Deployment Architecture

*See Diagram A.2: Data Flow (`diagrams/data_flow.puml`) and Diagram A.5: MQTT Topology (`diagrams/mqtt_topology.puml`)*

### 7.1 Vercel Configuration

```json
{
  "version": 2,
  "builds": [
    { "src": "app/**", "use": "@vercel/static" },
    { "src": "api/*.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "/api/$1" },
    { "src": "/app/(.*)", "dest": "/app/$1" },
    { "src": "/app", "dest": "/app/index.html" }
  ]
}
```

### 7.2 Race Day Setup

1. **Pi Camera Streamer**: Runs `gps_sync_streamer.py` serving MJPEG on port 8001
2. **Dashboard Server**: Pi hosts dashboard files via Python HTTP server on port 8080
3. **Driver Phone**: Connects to Pi network, opens `http://172.20.10.4:8080/index.html`
4. **Data Flow**:
   - Joulemeter → MQTT → HiveMQ Cloud → Dashboard
   - Pi Camera → HTTP MJPEG → Dashboard (local network)
   - Pi GPS → MQTT → HiveMQ Cloud → Dashboard (for sync)
   - Dashboard → Racing Line API (Vercel) → Overlay Coordinates

### 7.3 GPS Fallback Mode

If MQTT connection fails, the dashboard automatically switches to phone GPS:
- Speed and position from device GPS
- Lap detection and timer continue functioning
- Racing line overlay still works via local calculation
- Energy data unavailable (efficiency tracking disabled)

---

## 8. Results

### 8.1 System Performance

Testing with 37 recorded laps demonstrated:

| Metric | Value |
|--------|-------|
| Laps Recorded | 37 |
| Valid Laps (after filtering) | 24 |
| Best Single Lap Efficiency | 344.3 km/kWh |
| Ideal Lap (Composite) Efficiency | 507.0 km/kWh |
| Theoretical Improvement | +47.2% |
| GPS Distance Accuracy | ±0.5% |
| Overlay Update Rate | ~11 FPS |
| Sync Threshold | 5 meters |

### 8.2 Smoothing Quality

| Method | Smoothness Score | Accuracy Score | Overall |
|--------|------------------|----------------|---------|
| Raw (no smoothing) | 0 | 100 | 0 |
| Gaussian (σ=2) | 38.5 | 73.1 | 50.4 |
| Combined (recommended) | 75.7 | 85.2 | 80.1 |

### 8.3 Continuous Improvement Framework

*See Diagram A.4: Continuous Improvement Cycle (`diagrams/continuous_improvement.puml`)*

The system creates a virtuous cycle:

**RACE** → **COLLECT** → **ANALYZE** → **OPTIMIZE** → **UPDATE** → **RACE**

Each round improves the ideal lap, creating a compounding advantage throughout the competition day.

---

## 9. Conclusion

This report presented a comprehensive Vision-Telemetry HUD system that provides **real-time racing line guidance during the race** and **data-driven strategy refinement between rounds**.

**Key contributions:**

1. **Real-time HUD Overlay**: Green glowing racing line projected onto live camera feed, showing optimal path with deviation warnings
2. **Dual-data Paradigm**: Historical data establishes baseline; live data enables continuous improvement
3. **Ideal Lap Construction**: Composite optimal lap achieving +47% theoretical improvement over best single lap
4. **GPS-based Synchronization**: Accurate video-telemetry correlation using location matching
5. **Rapid Strategy Updates**: <5 minutes between rounds to incorporate new data

The system reduces driver cognitive load by replacing numerical displays with intuitive visual guidance, while the data flywheel ensures continuous improvement throughout competition. This approach positions PSU Eco Team I to achieve maximum energy efficiency at Shell Eco-marathon Qatar 2026.

---

## Technology Stack Summary

| Component | Technology | Purpose |
|-----------|------------|---------|
| Vehicle Telemetry | Joulemeter ECU | Voltage, current, power measurement |
| Camera System | Raspberry Pi 5 + USB Global Shutter Camera | 1280x720 video stream + HUD background |
| GPS Modules | Serial NMEA (Pi) + Vehicle GPS | Position tracking & sync |
| Communication | MQTT (HiveMQ Cloud) + HTTP MJPEG | Real-time telemetry & video |
| Backend API | Python on Vercel Serverless | Racing line calculations |
| Frontend | HTML5/JavaScript + Canvas + Leaflet | Driver HUD dashboard |
| Deployment | Vercel (API) + Raspberry Pi (Local) | Hybrid cloud/edge architecture |

---

## Appendix A: System Diagrams

The following PlantUML diagrams are provided in the `diagrams/` folder:

### A.1 System Architecture Diagram
**File:** `diagrams/system_architecture.puml`

Shows the four-layer architecture with two distinct sensor systems:
- **Sensor Layer**: Joulemeter system (energy) + Pi Camera system (vision)
- **Processing Layer**: Raspberry Pi 5, Vercel serverless functions
- **Communication Layer**: HiveMQ MQTT broker, HTTP MJPEG stream, REST API
- **Display Layer**: Driver HUD dashboard, pit crew monitor

### A.2 Data Flow Diagram
**File:** `diagrams/data_flow.puml`

Illustrates real-time data flow:
- Camera stream (local network)
- GPS telemetry via MQTT
- Joulemeter telemetry via MQTT
- Racing line overlay API calls
- Sync buffer correlation

### A.3 Ideal Lap Construction Algorithm
**File:** `diagrams/ideal_lap_algorithm.puml`

Flowchart showing the 5-step optimization:
1. Load all recorded laps
2. Segment track into 4 quadrants
3. Calculate efficiency scores
4. Select best segments
5. Stitch and smooth into ideal lap

### A.4 Continuous Improvement Cycle
**File:** `diagrams/continuous_improvement.puml`

The "data flywheel" showing:
RACE → COLLECT → ANALYZE → OPTIMIZE → UPDATE → RACE

### A.5 MQTT Topology
**File:** `diagrams/mqtt_topology.puml`

Network diagram showing publishers, broker, subscribers, and topic structure.

### A.6 GPS-to-Pixel Projection Algorithm
**File:** `diagrams/gps_projection.puml`

Detailed flowchart of camera overlay calculation:
- Haversine distance calculation
- Heading rotation transformation
- Field-of-view clipping
- Pixel coordinate conversion

---

**To render diagrams:**
- **Online**: Visit [PlantUML Web Server](http://www.plantuml.com/plantuml/uml/)
- **VS Code**: Install "PlantUML" extension, press `Alt+D` to preview
- **Command Line**: `java -jar plantuml.jar diagrams/*.puml`
