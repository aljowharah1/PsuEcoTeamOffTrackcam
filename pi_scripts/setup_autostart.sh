#!/bin/bash
# PSU Racing - Auto-start Setup Script
# This will make the dashboard start automatically on boot

echo "================================================"
echo "  PSU Racing - Auto-Start Setup"
echo "================================================"
echo ""

# Create systemd service file
echo "[1/3] Creating systemd service..."
sudo tee /etc/systemd/system/psu-racing.service > /dev/null <<EOF
[Unit]
Description=PSU Racing Dashboard - Auto Start
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/racing
ExecStart=/usr/bin/python3 /home/pi/racing/gps_sync_streamer.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Environment
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Service file created"
echo ""

# Reload systemd
echo "[2/3] Reloading systemd..."
sudo systemctl daemon-reload
echo "✓ Systemd reloaded"
echo ""

# Enable and start service
echo "[3/3] Enabling auto-start..."
sudo systemctl enable psu-racing.service
sudo systemctl start psu-racing.service
echo "✓ Auto-start enabled"
echo ""

echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "The dashboard will now:"
echo "  • Start automatically on boot"
echo "  • Restart automatically if it crashes"
echo "  • Clean up camera/port conflicts on start"
echo ""
echo "Useful commands:"
echo "  • Check status:  sudo systemctl status psu-racing"
echo "  • View logs:     sudo journalctl -u psu-racing -f"
echo "  • Restart:       sudo systemctl restart psu-racing"
echo "  • Stop:          sudo systemctl stop psu-racing"
echo "  • Disable:       sudo systemctl disable psu-racing"
echo ""
echo "Dashboard URL: http://172.20.10.4:8001/app/"
echo ""
