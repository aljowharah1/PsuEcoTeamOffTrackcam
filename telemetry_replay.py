#!/usr/bin/env python3
"""
PSU Racing - Telemetry Replay Tool
Replays recorded CSV telemetry data through MQTT to test the dashboard visualization.

Usage:
    python telemetry_replay.py [csv_file] [--speed 1.0]

Examples:
    python telemetry_replay.py data/2025/Attempt/Attempt1.csv
    python telemetry_replay.py data/2025/Attempt/Attempt1.csv --speed 2.0  # 2x speed
    python telemetry_replay.py data/2025/Attempt/Attempt1.csv --speed 0.5  # Half speed
"""

import csv
import json
import time
import argparse
import ssl
import paho.mqtt.client as mqtt
from datetime import datetime

# MQTT Configuration (same as dashboard)
MQTT_BROKER = "8fac0c92ea0a49b8b56f39536ba2fd78.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "ShellJM"
MQTT_PASS = "psuEcoteam1st"
MQTT_TOPIC = "car/telemetry"

def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print("[MQTT] Connected to broker successfully!")
    else:
        print(f"[MQTT] Connection failed with code {reason_code}")

def on_publish(client, userdata, mid, reason_code=None, properties=None):
    pass  # Silent publish confirmation

def load_csv(filepath):
    """Load telemetry data from CSV file."""
    data = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    print(f"[DATA] Loaded {len(data)} records from {filepath}")
    return data

def calculate_heading(lat1, lon1, lat2, lon2):
    """Calculate heading between two GPS points."""
    import math

    if lat1 == lat2 and lon1 == lon2:
        return 0

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lon = math.radians(lon2 - lon1)

    x = math.sin(delta_lon) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)

    heading = math.degrees(math.atan2(x, y))
    return (heading + 360) % 360

def replay_telemetry(csv_file, speed_multiplier=1.0):
    """Replay telemetry data through MQTT."""

    # Load data
    data = load_csv(csv_file)
    if not data:
        print("[ERROR] No data to replay!")
        return

    # Connect to MQTT
    print(f"[MQTT] Connecting to {MQTT_BROKER}:{MQTT_PORT}...")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"replay_{int(time.time())}")
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.tls_set(tls_version=ssl.PROTOCOL_TLS)
    client.on_connect = on_connect
    client.on_publish = on_publish

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        time.sleep(1)  # Wait for connection
    except Exception as e:
        print(f"[ERROR] Failed to connect to MQTT: {e}")
        return

    print(f"\n[REPLAY] Starting replay at {speed_multiplier}x speed...")
    print("[REPLAY] Press Ctrl+C to stop\n")

    prev_timestamp = None
    prev_lat = None
    prev_lon = None
    heading = 0

    try:
        for i, row in enumerate(data):
            # Parse data
            try:
                timestamp = float(row.get('obc_timestamp', 0))
                lat = float(row.get('gps_latitude', 0))
                lon = float(row.get('gps_longitude', 0))
                speed = float(row.get('gps_speed', 0))
                voltage = float(row.get('jm3_voltage', 0)) / 1000.0  # Convert mV to V
                current = float(row.get('jm3_current', 0)) / 1000.0  # Convert mA to A
                distance = float(row.get('dist', 0))
                lap = int(row.get('lap_lap', 0))
            except (ValueError, TypeError) as e:
                continue

            # Calculate heading from movement
            if prev_lat is not None and prev_lon is not None:
                if lat != prev_lat or lon != prev_lon:
                    heading = calculate_heading(prev_lat, prev_lon, lat, lon)

            # Calculate delay between packets
            if prev_timestamp is not None:
                delay = (timestamp - prev_timestamp) / speed_multiplier
                if delay > 0 and delay < 5:  # Cap at 5 seconds
                    time.sleep(delay)

            # Build telemetry packet (matching Joulemeter format)
            packet = {
                "latitude": lat,
                "longitude": lon,
                "speed_kmh": speed,
                "heading": heading,
                "voltage": voltage,
                "current": abs(current),  # Current is often negative in data
                "power": voltage * abs(current),
                "distance": distance,
                "lap": lap,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "replay"
            }

            # Publish
            payload = json.dumps(packet)
            client.publish(MQTT_TOPIC, payload, qos=0)

            # Progress display
            if i % 50 == 0:
                print(f"[{i:5d}/{len(data)}] Lat: {lat:.6f}, Lon: {lon:.6f}, Speed: {speed:.1f} km/h, Heading: {heading:.1f}°")

            prev_timestamp = timestamp
            prev_lat = lat
            prev_lon = lon

    except KeyboardInterrupt:
        print("\n\n[REPLAY] Stopped by user")
    finally:
        client.loop_stop()
        client.disconnect()
        print("[MQTT] Disconnected")

def main():
    parser = argparse.ArgumentParser(description='Replay telemetry data through MQTT')
    parser.add_argument('csv_file', nargs='?',
                        default='data/2025/Attempt/Attempt1.csv',
                        help='Path to CSV telemetry file')
    parser.add_argument('--speed', type=float, default=1.0,
                        help='Playback speed multiplier (default: 1.0)')

    args = parser.parse_args()

    print("=" * 50)
    print("  PSU Racing - Telemetry Replay Tool")
    print("=" * 50)
    print(f"  File: {args.csv_file}")
    print(f"  Speed: {args.speed}x")
    print("=" * 50)

    replay_telemetry(args.csv_file, args.speed)

if __name__ == '__main__':
    main()
