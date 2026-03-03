#!/bin/bash
# Start ALL LILITH/LuciferOS Services

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      Starting Complete LILITH/LuciferOS System                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Kill any existing services
echo "🔄 Stopping existing services..."
pkill -f lilith_full_backend 2>/dev/null
pkill -f web_dashboard 2>/dev/null
pkill -f attack_server 2>/dev/null
sleep 2

# Start Ollama if not running
echo "1️⃣  Starting Ollama..."
if ! pgrep -f "ollama serve" > /dev/null; then
    ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
    echo "   ✓ Ollama started"
else
    echo "   ✓ Ollama already running"
fi

# Start LILITH Backend (accessible externally)
echo ""
echo "2️⃣  Starting LILITH Backend..."
cd /app
BACKEND_HOST=0.0.0.0 BACKEND_PORT=5000 python3 tools/lilith_full_backend.py > backend_out.log 2> backend_err.log &
BACKEND_PID=$!
echo "   PID: $BACKEND_PID"
sleep 5

# Check backend
if curl -s http://127.0.0.1:5000/status > /dev/null 2>&1; then
    echo "   ✓ Backend responding on port 5000"
else
    echo "   ✗ Backend not responding"
fi

# Start Attack Server
echo ""
echo "3️⃣  Starting Attack Server..."
python3 tools/attack_server.py > attack_server_out.log 2> attack_server_err.log &
ATTACK_PID=$!
echo "   PID: $ATTACK_PID"
sleep 2
echo "   ✓ Attack server started"

# Start OpenClaw Gateway (if available)
echo ""
echo "4️⃣  Starting OpenClaw Gateway..."
if [ -f "/app/openclaw/openclaw.mjs" ]; then
    cd /app/openclaw
    # Start gateway in background
    node openclaw.mjs gateway --dev --port 18789 > /tmp/openclaw_gateway.log 2>&1 &
    OPENCLAW_PID=$!
    echo "   PID: $OPENCLAW_PID"
    sleep 3
    echo "   ✓ OpenClaw gateway started on port 18789"
else
    echo "   ⚠️  OpenClaw not found, skipping"
fi

# Start Web Dashboard (on port 3000 - exposed)
echo ""
echo "5️⃣  Starting Web Dashboard..."
cd /app
WEB_DASHBOARD_PORT=3000 WEB_DASHBOARD_HOST=0.0.0.0 python3 ui/web_dashboard.py > dashboard_out.log 2> dashboard_err.log &
DASHBOARD_PID=$!
echo "   PID: $DASHBOARD_PID"
sleep 5

if curl -s http://127.0.0.1:3000/ > /dev/null 2>&1; then
    echo "   ✓ Dashboard responding on port 3000"
else
    echo "   ✗ Dashboard not responding"
fi

# Show status
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ ALL SERVICES STARTED"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🌐 Access Points:"
echo "   Dashboard:  https://luciferops.preview.emergentagent.com"
echo "   Backend:    http://0.0.0.0:5000"
echo "   OpenClaw:   http://127.0.0.1:18789"
echo ""
echo "🔧 Local URLs (internal):"
echo "   http://127.0.0.1:3000  - Dashboard"
echo "   http://127.0.0.1:5000  - Backend"
echo "   http://127.0.0.1:18789 - OpenClaw Gateway"
echo ""
echo "📊 Process IDs:"
echo "   Backend:  $BACKEND_PID"
echo "   Attack:   $ATTACK_PID"
echo "   OpenClaw: $OPENCLAW_PID"
echo "   Dashboard: $DASHBOARD_PID"
echo ""
echo "📝 Logs:"
echo "   Backend:   tail -f /app/backend_err.log"
echo "   Dashboard: tail -f /app/dashboard_err.log"
echo "   Attack:    tail -f /app/attack_server_err.log"
echo "   OpenClaw:  tail -f /tmp/openclaw_gateway.log"
echo ""
echo "🧪 Test Commands:"
echo "   curl http://127.0.0.1:5000/status"
echo "   curl http://127.0.0.1:3000/api/status"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✨ System Ready!"
echo "════════════════════════════════════════════════════════════════"
