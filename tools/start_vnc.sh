#!/bin/bash
# Start virtual display and VNC for browser viewing

# Kill any existing Xvfb and VNC
pkill -f Xvfb 2>/dev/null
pkill -f x11vnc 2>/dev/null
pkill -f websockify 2>/dev/null

# Start virtual framebuffer
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &
sleep 2

# Start a simple window manager
DISPLAY=:99 fluxbox &
sleep 1

# Start VNC server on the display
x11vnc -display :99 -forever -shared -rfbport 5900 -nopw &
sleep 1

# Start noVNC websocket proxy (connects VNC to web)
websockify --web=/usr/share/novnc 6080 localhost:5900 &
sleep 1

echo "Virtual display started on :99"
echo "VNC available on port 5900"
echo "noVNC web interface available on port 6080"
echo ""
echo "Access the browser at: http://localhost:6080/vnc.html"
