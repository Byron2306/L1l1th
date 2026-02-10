#!/bin/bash
# Complete System Reset and Startup for LILITH/LuciferOS

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         LILITH/LuciferOS - Complete System Reset              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Kill all existing processes
echo "🛑 Stopping all services..."
pkill -f lilith_full_backend 2>/dev/null
pkill -f web_dashboard 2>/dev/null
pkill -f attack_server 2>/dev/null
pkill -f "openclaw.*gateway" 2>/dev/null
pkill -f ollama 2>/dev/null
sleep 3

# Clear logs
echo "🧹 Clearing logs..."
> /app/backend_out.log
> /app/backend_err.log
> /app/dashboard_out.log
> /app/dashboard_err.log
> /app/attack_server_out.log
> /app/attack_server_err.log
> /tmp/openclaw_gateway.log
> /tmp/ollama.log

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              Starting All Services                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Start Ollama
echo "1️⃣  Starting Ollama (Local AI)..."
ollama serve > /tmp/ollama.log 2>&1 &
sleep 3
if pgrep -f "ollama serve" > /dev/null; then
    echo "   ✓ Ollama started (PID: $(pgrep -f 'ollama serve'))"
else
    echo "   ⚠️  Ollama failed to start"
fi

# Start LILITH Backend
echo ""
echo "2️⃣  Starting LILITH Backend..."
cd /app
BACKEND_HOST=0.0.0.0 BACKEND_PORT=5000 python3 tools/lilith_full_backend.py > backend_out.log 2> backend_err.log &
BACKEND_PID=$!
echo "   Started with PID: $BACKEND_PID"
sleep 6

# Test backend
if curl -s http://127.0.0.1:5000/status > /dev/null 2>&1; then
    echo "   ✓ Backend responding on port 5000"
else
    echo "   ✗ Backend not responding - check logs"
fi

# Start Attack Server
echo ""
echo "3️⃣  Starting Attack Server..."
python3 tools/attack_server.py > attack_server_out.log 2> attack_server_err.log &
ATTACK_PID=$!
echo "   Started with PID: $ATTACK_PID"
sleep 2

# Start OpenClaw Gateway
echo ""
echo "4️⃣  Starting OpenClaw Gateway..."
if [ -f "/app/openclaw/openclaw.mjs" ]; then
    cd /app/openclaw
    node openclaw.mjs gateway --dev --port 18789 > /tmp/openclaw_gateway.log 2>&1 &
    OPENCLAW_PID=$!
    echo "   Started with PID: $OPENCLAW_PID"
    sleep 3
    echo "   ✓ OpenClaw gateway on port 18789"
else
    echo "   ⚠️  OpenClaw not found"
fi

# Start Enhanced Master Dashboard
echo ""
echo "5️⃣  Starting Enhanced Master Dashboard..."
cd /app
WEB_DASHBOARD_PORT=3000 WEB_DASHBOARD_HOST=0.0.0.0 python3 ui/web_dashboard_master.py > dashboard_out.log 2> dashboard_err.log &
DASHBOARD_PID=$!
echo "   Started with PID: $DASHBOARD_PID"
sleep 6

# Test dashboard
if curl -s http://127.0.0.1:3000/ > /dev/null 2>&1; then
    echo "   ✓ Dashboard responding on port 3000"
else
    echo "   ✗ Dashboard not responding - check logs"
fi

# System Status Check
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    SYSTEM STATUS                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check services
services_ok=0
services_total=5

echo "Service Health Check:"
if pgrep -f "ollama serve" > /dev/null; then
    echo "  ✓ Ollama:    Running"
    services_ok=$((services_ok + 1))
else
    echo "  ✗ Ollama:    Stopped"
fi

if pgrep -f "lilith_full_backend" > /dev/null; then
    echo "  ✓ Backend:   Running"
    services_ok=$((services_ok + 1))
else
    echo "  ✗ Backend:   Stopped"
fi

if pgrep -f "attack_server" > /dev/null; then
    echo "  ✓ Attack:    Running"
    services_ok=$((services_ok + 1))
else
    echo "  ✗ Attack:    Stopped"
fi

if pgrep -f "openclaw" > /dev/null; then
    echo "  ✓ OpenClaw:  Running"
    services_ok=$((services_ok + 1))
else
    echo "  ✗ OpenClaw:  Stopped"
fi

if pgrep -f "web_dashboard_master" > /dev/null; then
    echo "  ✓ Dashboard: Running"
    services_ok=$((services_ok + 1))
else
    echo "  ✗ Dashboard: Stopped"
fi

echo ""
echo "Services Running: $services_ok/$services_total"

# API Tests
echo ""
echo "API Endpoint Tests:"

test_endpoint() {
    url=$1
    name=$2
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo "  ✓ $name"
        return 0
    else
        echo "  ✗ $name"
        return 1
    fi
}

test_endpoint "http://127.0.0.1:5000/status" "Backend Status"
test_endpoint "http://127.0.0.1:3000/api/status" "Dashboard API"
test_endpoint "http://127.0.0.1:5000/openclaw/redteam-skills" "OpenClaw Skills"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                 ACCESS INFORMATION                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Dashboard URL:"
echo "   https://luciferos-hack.preview.emergentagent.com"
echo ""
echo "🔧 Local URLs:"
echo "   Dashboard:  http://127.0.0.1:3000"
echo "   Backend:    http://127.0.0.1:5000"
echo "   OpenClaw:   http://127.0.0.1:18789"
echo ""
echo "📊 Features:"
echo "   • 9 Dashboard Tabs (LILITH AI, Progress, Recon, etc.)"
echo "   • 🔑 NEW: Autonomous API Key Harvester (Tab 9)"
echo "   • 31 OpenClaw Skills"
echo "   • Learning & Memory Systems"
echo "   • Real-time Status Monitoring"
echo ""
echo "🔑 API Key Harvesting:"
echo "   1. Open dashboard and go to 'Harvester' tab"
echo "   2. Select provider (Groq recommended)"
echo "   3. Click 'START AUTONOMOUS HARVESTING'"
echo "   4. Watch real-time progress"
echo "   5. Key saved automatically when complete"
echo ""
echo "📝 Logs:"
echo "   Backend:   tail -f /app/backend_err.log"
echo "   Dashboard: tail -f /app/dashboard_err.log"
echo "   Attack:    tail -f /app/attack_server_err.log"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ System Reset and Startup Complete!"
echo "════════════════════════════════════════════════════════════════"
