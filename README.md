# PSU Racing - Mobile Dashboard

Real-time telemetry dashboard for electric racing car monitoring via MQTT.

## Project Structure

```
dashboardPSU_ECOteam/
├── app/                      # Mobile Dashboard Application
│   ├── index.html           # Main dashboard interface
│   ├── style.css            # Dashboard styling
│   └── script.js            # MQTT connection & UI logic
├── data/                     # Test Data & CSV Files
│   ├── 2025/                # 2025 Race data
│   │   ├── Attempt/         # Attempt1.csv, Attempt2.csv
│   │   └── practice1/       # Practice session data
│   └── race_data.csv        # Additional test data
├── scripts/                  # Testing & Replay Scripts
│   └── replay_attempt1.py   # MQTT replay script for testing
└── utils/                    # Development Utilities
    ├── extract_single_lap.py       # Extract single lap from CSV
    ├── extract_track.py            # Extract track outline
    ├── extract_track_combined.py   # Combine multiple attempts
    ├── fix_script.py               # Fix corrupted files
    ├── update_outline.py           # Update track in script.js
    └── verify_turns.py             # Verify turn directions
```

## Features

- **Real-time MQTT Telemetry**: Live data streaming from race car
- **Interactive Track Map**: GPS-based visualization with Leaflet.js
- **Heat Map**: Current draw visualization across the track
- **Auto-Timer**: Starts on movement, pauses after 15s idle
- **Lap Detection**: GPS-based lap counting at start/finish line
- **Efficiency Tracking**: Wh/km per lap calculation
- **Turn Guidance**: 7 directional arrows for key turns
- **Speedometer**: Real-time speed with animated arc
- **Current Display**: Live amperage monitoring

## Quick Start

### 1. Test with Replay Data

Run the MQTT replay script to broadcast CSV data:

```bash
python scripts/replay_attempt1.py
```

### 2. Open Dashboard

Open `app/index.html` in your browser:
- **Local**: `file:///C:/path/to/app/index.html`
- **Requires**: Active internet connection for Leaflet & MQTT libraries

### 3. Live Car Testing

1. Configure MQTT broker settings in `app/script.js`:
   ```javascript
   const MQTT_BROKER = "your-broker-url";
   const TOPIC = "car/telemetry";
   ```

2. Deploy to phone/tablet for in-car use

## MQTT Message Format

```json
{
  "voltage": 48.5,
  "current": 12.3,
  "power": 596.55,
  "speed": 87.5,
  "rpm": 4375,
  "distance_km": 2.45,
  "latitude": 25.488435,
  "longitude": 51.450190
}
```

## Track Configuration

Track outline and turns are defined in `app/script.js`:
- **Center**: Start/finish line coordinates
- **Outline**: 47-point GPS polyline (single lap)
- **Turns**: 7 significant turns with left/right directions

## Development

### Extract Track from CSV

```bash
python utils/extract_single_lap.py
```

### Verify Turn Directions

```bash
python utils/verify_turns.py
```

## Mobile Deployment

To use on mobile device in car:

1. **Option 1**: Host on local server accessible via WiFi
2. **Option 2**: Download offline libraries and deploy as PWA
3. **Option 3**: Use Cordova/Capacitor for native app

## Requirements

- Python 3.x (for testing/replay)
- paho-mqtt library: `pip install paho-mqtt`
- Modern web browser with JavaScript enabled
- Internet connection (for CDN libraries)

## Credits

**PSU Racing Team**
Electric Vehicle Racing Dashboard - 2025
