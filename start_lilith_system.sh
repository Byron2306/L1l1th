#!/bin/bash
# Start LILITH/LuciferOS Complete System

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           Starting LILITH / LuciferOS System                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Function to check if process is running
check_service() {
    local name=$1
    local port=$2
    
    if lsof -i :$port >/dev/null 2>&1 || ss -tuln | grep -q ":$port "; then
        echo "✓ $name is running on port $port"
        return 0
    else
        echo "✗ $name is NOT running on port $port"
        return 1
    fi
}

# Start Ollama if not running
echo "1. Checking Ollama..."
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "   Starting Ollama..."
    ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
fi
check_service "Ollama" 11434
echo ""

# Start Backend
echo "2. Starting LILITH Backend..."
cd /app
python3 tools/lilith_full_backend.py > backend_out.log 2> backend_err.log &
BACKEND_PID=$!
sleep 5

check_service "Backend" 5000
echo "   PID: $BACKEND_PID"
echo ""

# Start Dashboard
echo "3. Starting Web Dashboard..."
python3 ui/web_dashboard.py > dashboard_out.log 2> dashboard_err.log &
DASHBOARD_PID=$!
sleep 5

check_service "Dashboard" 8080
echo "   PID: $DASHBOARD_PID"
echo ""

# Show status
echo "════════════════════════════════════════════════════════════════"
echo "SYSTEM STATUS"
echo "════════════════════════════════════════════════════════════════"
echo ""

curl -s http://127.0.0.1:5000/status | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"✓ Backend: {data.get('status', 'unknown')}\")
    print(f\"✓ Agent: {data.get('agent', 'unknown')}\")
    providers = data.get('ai_providers', {})
    print(f\"✓ AI Providers: {providers.get('active_count', 0)}/{providers.get('total_count', 0)} active\")
except:
    print('✗ Backend not responding')
" 2>/dev/null || echo "⚠️  Backend starting..."

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "ACCESS POINTS"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🌐 Dashboard:  http://127.0.0.1:8080"
echo "🔧 Backend API: http://127.0.0.1:5000"
echo "📊 Status:      http://127.0.0.1:5000/status"
echo ""
echo "Test endpoints:"
echo "  curl http://127.0.0.1:5000/status"
echo "  curl -X POST http://127.0.0.1:5000/chat -H 'Content-Type: application/json' -d '{\"message\":\"hello\"}'"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "LOGS"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Backend:   tail -f /app/backend_err.log"
echo "Dashboard: tail -f /app/dashboard_err.log"
echo "Ollama:    tail -f /tmp/ollama.log"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✓ System Started Successfully!"
echo "════════════════════════════════════════════════════════════════"
