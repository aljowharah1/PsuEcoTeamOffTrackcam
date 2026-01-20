#!/usr/bin/env python3
"""
PSU Racing - Test Data Replayer
Replays last year's telemetry data via MQTT for testing the dashboard.

Usage:
    python3 test_data_replayer.py [--speed 1.0]

    --speed: Playback speed multiplier (1.0 = real-time, 2.0 = 2x speed)
"""

import csv
import time
import json
import argparse
import paho.mqtt.client as mqtt

# MQTT Configuration (same as dashboard)
MQTT_BROKER = "8fac0c92ea0a49b8b56f39536ba2fd78.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "ShellJM"
MQTT_PASS = "psuEcoteam1st"
TOPIC_TELEMETRY = "car/telemetry"
TOPIC_PI_GPS = "car/pi_gps"

def parse_csv_row(row):
    """Parse CSV row into telemetry data (handles both old and new formats)."""
    try:
        # Auto-detect format based on column names
        if 'obc_timestamp' in row:
            # Last year's format
            return {
                'rec_id': int(row['rec_id']) if row.get('rec_id') else 0,
                'timestamp': float(row['obc_timestamp']),
                'lap_timestamp': float(row['lap_obc_timestamp']) if row.get('lap_obc_timestamp') else 0.0,
                'distance': float(row['dist']) if row.get('dist') else 0.0,
                'lap_distance': float(row['lap_dist']) if row.get('lap_dist') else 0.0,
                'gps_latitude': float(row['gps_latitude']) if row.get('gps_latitude') else 0.0,
                'gps_longitude': float(row['gps_longitude']) if row.get('gps_longitude') else 0.0,
                'gps_speed': float(row['gps_speed']) if row.get('gps_speed') else 0.0,
                'energy': float(row['jm3_netjoule']) if row.get('jm3_netjoule') else 0.0,
                'lap_energy': float(row['lap_jm3_netjoule']) if row.get('lap_jm3_netjoule') else 0.0,
                'voltage': float(row['jm3_voltage']) if row.get('jm3_voltage') else 0.0,
                'current': float(row['jm3_current']) if row.get('jm3_current') else 0.0,
                'lap': int(row['lap_lap']) if row.get('lap_lap') else 0,
            }
        else:
            # This year's format (timestamp, voltage, current, power, speed, rpm, distance_km, latitude, longitude, total_energy_wh, efficiency_km_per_kwh, consumption_wh_per_km)
            return {
                'rec_id': 0,
                'timestamp': float(row['timestamp']),
                'lap_timestamp': 0.0,
                'distance': float(row['distance_km']) if row.get('distance_km') else 0.0,
                'lap_distance': 0.0,
                'gps_latitude': float(row['latitude']) if row.get('latitude') else 0.0,
                'gps_longitude': float(row['longitude']) if row.get('longitude') else 0.0,
                'gps_speed': float(row['speed']) if row.get('speed') else 0.0,
                'energy': float(row['total_energy_wh']) if row.get('total_energy_wh') else 0.0,
                'lap_energy': 0.0,
                'voltage': float(row['voltage']) if row.get('voltage') else 0.0,
                'current': float(row['current']) if row.get('current') else 0.0,
                'power': float(row['power']) if row.get('power') else 0.0,
                'lap': 0,
            }
    except (ValueError, KeyError) as e:
        print(f"Error parsing row: {e}")
        return None

def format_telemetry(data):
    """Format data for MQTT telemetry topic."""
    return {
        "latitude": data['gps_latitude'],
        "longitude": data['gps_longitude'],
        "speed": data['gps_speed'],  # Dashboard expects "speed" not "speed_kmh"
        "rpm": 0,
        "heading": 0,  # Calculated from position changes later
        "voltage": data['voltage'],
        "current": data['current'],
        "power": data.get('power', data['voltage'] * data['current']),
        "total_energy_wh": data['energy'],
        "energy": data['energy'],
        "lap_energy": data['lap_energy'],
        "lap": data['lap'],
        "distance_km": data['distance'],  # Dashboard expects "distance_km" not "distance"
        "lap_distance": data['lap_distance'],
        "source": "test_replayer"
    }

def format_pi_gps(data):
    """Format data for Pi GPS topic."""
    return {
        "latitude": data['gps_latitude'],
        "longitude": data['gps_longitude'],
        "speed_kmh": data['gps_speed'],
        "heading": 0,
        "altitude": 0.0,
        "satellites": 8,
        "fix_quality": 1,
        "source": "test_replayer"
    }

def main():
    parser = argparse.ArgumentParser(description='Replay test data via MQTT')
    parser.add_argument('--speed', type=float, default=1.0, help='Playback speed multiplier')
    parser.add_argument('--file', type=str, default='lastyears_Data.csv', help='CSV file to replay')
    args = parser.parse_args()

    print("=" * 60)
    print("  PSU Racing - Test Data Replayer")
    print("=" * 60)
    print(f"Playback speed: {args.speed}x")
    print(f"Data file: {args.file}")
    print()

    # Connect to MQTT
    print("[MQTT] Connecting to broker...")
    client = mqtt.Client(client_id=f"test_replayer_{int(time.time())}")
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.tls_set()

    connected = False

    def on_connect(c, userdata, flags, rc):
        nonlocal connected
        if rc == 0:
            print("[MQTT] ✓ Connected to broker")
            connected = True
        else:
            print(f"[MQTT] ✗ Connection failed: {rc}")

    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    # Wait for connection
    timeout = 10
    while not connected and timeout > 0:
        time.sleep(0.1)
        timeout -= 0.1

    if not connected:
        print("[MQTT] Failed to connect. Exiting.")
        return

    # Read CSV data
    print(f"[DATA] Loading {args.file}...")
    with open(args.file, 'r') as f:
        reader = csv.DictReader(f)
        rows = [parse_csv_row(row) for row in reader]
        rows = [r for r in rows if r is not None]  # Filter out bad rows

    print(f"[DATA] ✓ Loaded {len(rows)} data points")
    print()

    print("[REPLAY] Starting playback...")
    print("Press Ctrl+C to stop")
    print()

    start_time = time.time()
    first_timestamp = rows[0]['timestamp']
    last_lat = None
    last_lon = None

    for i, data in enumerate(rows):
        # Calculate heading from position changes
        if last_lat and last_lon:
            import math
            dlat = data['gps_latitude'] - last_lat
            dlon = data['gps_longitude'] - last_lon
            heading = math.degrees(math.atan2(dlon, dlat)) % 360
        else:
            heading = 0

        last_lat = data['gps_latitude']
        last_lon = data['gps_longitude']

        # Prepare telemetry data
        telemetry = format_telemetry(data)
        telemetry['heading'] = heading

        pi_gps = format_pi_gps(data)
        pi_gps['heading'] = heading

        # Publish to MQTT
        client.publish(TOPIC_TELEMETRY, json.dumps(telemetry), qos=0)
        client.publish(TOPIC_PI_GPS, json.dumps(pi_gps), qos=0)

        # Print progress every 100 points
        if i % 100 == 0:
            print(f"[{i}/{len(rows)}] Lat: {data['gps_latitude']:.6f}, "
                  f"Lon: {data['gps_longitude']:.6f}, "
                  f"Speed: {data['gps_speed']:.1f} km/h, "
                  f"Voltage: {data['voltage']:.1f}V, "
                  f"Current: {data['current']:.1f}A")

        # Calculate sleep time for real-time playback
        elapsed_data_time = data['timestamp'] - first_timestamp
        elapsed_real_time = time.time() - start_time
        sleep_time = (elapsed_data_time - elapsed_real_time) / args.speed

        if sleep_time > 0:
            time.sleep(sleep_time)

    print()
    print("=" * 60)
    print("[REPLAY] ✓ Playback complete!")
    print(f"[REPLAY] Replayed {len(rows)} data points")
    print("=" * 60)

    client.loop_stop()
    client.disconnect()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[REPLAY] Stopped by user")
    except FileNotFoundError:
        print("Error: CSV file not found!")
        print("Make sure lastyears_Data.csv is in the same directory")
