#!/usr/bin/env python3
"""
Comprehensive camera test - tries EVERY device and backend combination
"""

import cv2
import sys

print("=" * 60)
print("COMPREHENSIVE CAMERA TEST")
print("=" * 60)

# Test both low-numbered devices and high-numbered ones
test_devices = [
    "/dev/video0", "/dev/video1", "/dev/video19",
    0, 1, 19, 20, 21
]

test_backends = [
    (None, "Default backend"),
    (cv2.CAP_V4L2, "V4L2 backend"),
    (cv2.CAP_GSTREAMER, "GStreamer backend"),
]

working_configs = []

print("\nTesting all device and backend combinations...\n")

for device in test_devices:
    for backend, backend_name in test_backends:
        desc = f"{device} with {backend_name}"

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
                    print(f"✓ SUCCESS: {desc}")
                    print(f"  Resolution: {width}x{height}")
                    working_configs.append((device, backend, backend_name, width, height))
                    cap.release()
                else:
                    print(f"✗ FAIL: {desc} - opened but no frame")
                    cap.release()
            else:
                print(f"✗ FAIL: {desc} - couldn't open")
        except Exception as e:
            print(f"✗ ERROR: {desc} - {e}")

print("\n" + "=" * 60)
if working_configs:
    print("WORKING CONFIGURATIONS FOUND:")
    print("=" * 60)
    for i, (device, backend, backend_name, width, height) in enumerate(working_configs, 1):
        print(f"\n{i}. Device: {device}")
        print(f"   Backend: {backend_name}")
        print(f"   Resolution: {width}x{height}")
        if backend:
            print(f"   Code: cap = cv2.VideoCapture({repr(device)}, {backend})")
        else:
            print(f"   Code: cap = cv2.VideoCapture({repr(device)})")

    print("\n" + "=" * 60)
    print("RECOMMENDED FIX:")
    print("=" * 60)
    device, backend, backend_name, width, height = working_configs[0]
    print(f"\nUse this in your script:")
    print(f"  CAMERA_DEVICE = {repr(device)}")
    if backend:
        print(f"  cap = cv2.VideoCapture(CAMERA_DEVICE, {backend})")
    else:
        print(f"  cap = cv2.VideoCapture(CAMERA_DEVICE)")
else:
    print("NO WORKING CONFIGURATIONS FOUND")
    print("=" * 60)
    print("\nPossible issues:")
    print("1. Camera driver not loaded")
    print("2. Camera incompatible with OpenCV")
    print("3. Permission issues (run: sudo usermod -a -G video pi && sudo reboot)")
    print("4. Camera hardware failure")
    print("\nTry manual test:")
    print("  v4l2-ctl --device=/dev/video0 --stream-mmap --stream-count=1")

print("=" * 60)
