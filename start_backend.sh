#!/bin/bash
# LUCIFER-OS Backend Startup Script
# Ensures reliable auto-start of all system components

echo "🔥 Starting LUCIFER-OS Backend Services..."

# Set working directory
cd "$(dirname "$0")"

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "lilith_full_backend.py" 2>/dev/null || true
pkill -f "flask" 2>/dev/null || true
sleep 2

# Start the main backend
echo "🚀 Starting LILITH Backend..."
python tools/lilith_full_backend.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend is running
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "✅ Backend started successfully (PID: $BACKEND_PID)"
    echo "🌐 Backend available at: http://127.0.0.1:5000"

    # Start attack server if backend is running
    echo "⚔️  Starting Attack Server..."
    python -c "
from tools.attack_server import get_attack_server
server = get_attack_server()
result = server.start_server(8888)
print('Attack server result:', result)
" &

    echo "🎯 All services started!"
    echo "📊 Status check: curl http://127.0.0.1:5000/status"
else
    echo "❌ Backend failed to start"
    exit 1
fi

echo "🔥 LUCIFER-OS is now operational!"