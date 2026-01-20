#!/usr/bin/env python3
"""
Simple camera test script - diagnose what's wrong
Run this FIRST before running the full script
"""

import cv2
import sys

print("=" * 60)
print("CAMERA DIAGNOSTIC TEST")
print("=" * 60)

# Test different device paths and backends
test_configs = [
    ("/dev/video0", cv2.CAP_V4L2, "V4L2 backend, /dev/video0"),
    (0, cv2.CAP_V4L2, "V4L2 backend, device 0"),
    (1, cv2.CAP_V4L2, "V4L2 backend, device 1"),
    ("/dev/video0", None, "Default backend, /dev/video0"),
    (0, None, "Default backend, device 0"),
]

working_config = None

for device, backend, description in test_configs:
    print(f"\n[TEST] Trying: {description}")

    try:
        if backend:
            cap = cv2.VideoCapture(device, backend)
        else:
            cap = cv2.VideoCapture(device)

        if cap.isOpened():
            # Try to read a frame
            ret, frame = cap.read()
            if ret and frame is not None:
                height, width = frame.shape[:2]
                print(f"[SUCCESS] ✓ Camera opened: {width}x{height}")
                print(f"           Device: {device}")
                print(f"           Backend: {backend if backend else 'default'}")
                working_config = (device, backend, description)
                cap.release()
                break
            else:
                print(f"[FAIL] Camera opened but couldn't read frame")
                cap.release()
        else:
            print(f"[FAIL] Couldn't open camera")
    except Exception as e:
        print(f"[ERROR] {e}")

print("\n" + "=" * 60)
if working_config:
    print("RESULT: CAMERA WORKING! ✓")
    print(f"Use this configuration:")
    print(f"  Device: {working_config[0]}")
    print(f"  Backend: {working_config[1] if working_config[1] else 'cv2.VideoCapture (no backend)'}")
else:
    print("RESULT: NO CAMERA FOUND ✗")
    print("\nTroubleshooting steps:")
    print("1. Check if camera is connected: lsusb")
    print("2. Check video devices: ls -la /dev/video*")
    print("3. Check permissions: sudo usermod -a -G video $USER")
    print("4. Reboot the Pi if camera was just connected")
print("=" * 60)
