#!/bin/bash
# LuciferOS Boot Initialization

echo "[+] LuciferOS Initializing..."
echo "[+] Version: 2.0"
echo ""

# Mount filesystems
mount -t proc proc /proc
mount -t sysfs sys /sys
mount -t devtmpfs dev /dev

# Network setup
ip link set lo up
echo "[+] Network initialized"

# Start services
echo "[+] Starting LILITH backend..."
python3 /opt/lucifera/lilith_complete.py &
sleep 3

# Start X server (if available)
if command -v Xvfb &> /dev/null; then
    echo "[+] Starting X server..."
    Xvfb :0 -screen 0 2560x1440x24 &
    export DISPLAY=:0
fi

# Launch dashboard
echo "[+] Launching LuciferOS Dashboard..."
python3 /opt/lucifera/dashboard_complete.py

exec /bin/bash
