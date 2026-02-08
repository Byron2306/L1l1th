#!/bin/bash
# LUCIFER-OS OpenClaw Integrated Startup Launcher
# Combines LUCIFER-OS backend with OpenClaw gateway startup

set -euo pipefail

# Configuration
LUCIFER_DIR="/workspaces/LUCIFER-OS"
OPENCLAW_DIR="${LUCIFER_DIR}/openclaw"
BACKEND_PORT=5000
GATEWAY_PORT=3000
WEB_DASHBOARD_PORT=8080
WEB_DASHBOARD_HOST="127.0.0.1"
LOG_DIR="${LUCIFER_DIR}/logs"
STARTUP_LOG="${LOG_DIR}/startup.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create log directory
mkdir -p "$LOG_DIR"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$STARTUP_LOG"
}

# Generate a gateway token if not provided
generate_gateway_token() {
    if [ -n "${OPENCLAW_GATEWAY_TOKEN:-}" ]; then
        info "Using existing OPENCLAW_GATEWAY_TOKEN"
        return 0
    fi

    # Try to generate a reasonably random token
    if command -v openssl >/dev/null 2>&1; then
        OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 16)
    else
        OPENCLAW_GATEWAY_TOKEN=$(head -c 32 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | cut -c1-32)
    fi
    export OPENCLAW_GATEWAY_TOKEN
    success "Generated OpenClaw gateway token"
    return 0
}

success() {
    echo -e "${GREEN}✓ $*${NC}" | tee -a "$STARTUP_LOG"
}

error() {
    echo -e "${RED}✗ $*${NC}" | tee -a "$STARTUP_LOG"
}

info() {
    echo -e "${BLUE}ℹ $*${NC}" | tee -a "$STARTUP_LOG"
}

warning() {
    echo -e "${YELLOW}⚠ $*${NC}" | tee -a "$STARTUP_LOG"
}

# Function to check if port is in use
check_port() {
    local port=$1
    local name=$2
    if lsof -i :$port >/dev/null 2>&1; then
        warning "$name port $port is already in use"
        return 1
    else
        return 0
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1

    info "Waiting for $service_name to be ready..."

    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            success "$service_name is ready"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
    done
    error "$service_name failed to start within $(($max_attempts * 2)) seconds"
    return 1

}

start_backend() {
    info "Starting LUCIFER-OS backend..."

    if check_port $BACKEND_PORT "Backend"; then
        cd "$LUCIFER_DIR"
        bash start_backend.sh &
        local backend_pid=$!

        # Wait for backend to start
        if wait_for_service "http://127.0.0.1:$BACKEND_PORT/openclaw/redteam-skills" "LUCIFER-OS backend"; then
            success "Backend started successfully (PID: $backend_pid)"
            return 0
        else
            error "Backend failed to start"
            return 1
        fi
    else
        warning "Backend appears to already be running"
        return 0
    fi
}

# Function to start OpenClaw gateway
start_gateway() {
    info "Starting OpenClaw gateway..."

    if check_port $GATEWAY_PORT "Gateway"; then
        cd "$OPENCLAW_DIR"

        # Generate and set token
        if ! generate_gateway_token; then
            return 1
        fi

        # Start gateway in background
        timeout 30s node openclaw.mjs gateway --dev --port $GATEWAY_PORT &
        local gateway_pid=$!

        # Wait for gateway to start
        if wait_for_service "http://127.0.0.1:$GATEWAY_PORT/api/status" "OpenClaw gateway"; then
            success "Gateway started successfully (PID: $gateway_pid)"
            return 0
        else
            error "Gateway failed to start"
            return 1
        fi
    else
        warning "Gateway appears to already be running"
        return 0
    fi
}

# Function to start Telegram bot
start_telegram_bot() {
    info "Starting Telegram Lilith bot..."
    local bot_script="$LUCIFER_DIR/telegram_lilith_bot.py"

    if [ ! -f "$bot_script" ]; then
        warning "Telegram bot script not found: $bot_script"
        return 0
    fi

    # Start bot in background and log output
    python3 "$bot_script" >> "$LOG_DIR/telegram_bot.log" 2>&1 &
    local bot_pid=$!
    sleep 1
    if ps -p $bot_pid >/dev/null 2>&1; then
        success "Telegram bot started (PID: $bot_pid)"
        return 0
    else
        error "Telegram bot failed to start"
        return 1
    fi
}

# Function to start UI (attempts common UI runners)
start_ui() {
    info "Starting UI components..."

    # If PyQt dashboard exists, try launching it (only when DISPLAY present)
    if [ -f "$LUCIFER_DIR/ui/luciferos_master_dashboard.py" ]; then
        if [ -n "${DISPLAY:-}" ]; then
            PYTHONPATH="$LUCIFER_DIR" python3 "$LUCIFER_DIR/ui/luciferos_master_dashboard.py" >> "$LOG_DIR/ui.log" 2>&1 &
            ui_pid=$!
            sleep 1
            if ps -p $ui_pid >/dev/null 2>&1; then
                success "PyQt UI started (PID: $ui_pid)"
                return 0
            else
                warning "PyQt UI failed to start; falling back to web dashboard"
            fi
        else
            info "No DISPLAY; skipping PyQt dashboard (headless environment)"
        fi
    fi

    # Try OpenClaw UI dev server if pnpm available
    if command -v pnpm >/dev/null 2>&1 && [ -d "$OPENCLAW_DIR/ui" ]; then
        (cd "$OPENCLAW_DIR" && pnpm dev) >> "$LOG_DIR/openclaw_ui.log" 2>&1 &
        ui_pid=$!
        sleep 2
        if ps -p $ui_pid >/dev/null 2>&1; then
            success "OpenClaw UI dev server started (PID: $ui_pid)"
            return 0
        else
            warning "OpenClaw UI dev server failed to start"
        fi
    fi

    # Final fallback: start the lightweight Flask web dashboard
    if check_port $WEB_DASHBOARD_PORT "Web Dashboard"; then
        info "Starting web dashboard on port $WEB_DASHBOARD_PORT"
        export LUCIFER_BACKEND_URL="http://127.0.0.1:$BACKEND_PORT"
        export OPENCLAW_CANVAS="http://127.0.0.1:$GATEWAY_PORT/__openclaw__/canvas/"
        PYTHONPATH="$LUCIFER_DIR" python3 "$LUCIFER_DIR/ui/web_dashboard.py" >> "$LOG_DIR/web_dashboard.log" 2>&1 &
        ui_pid=$!
        if wait_for_service "http://$WEB_DASHBOARD_HOST:$WEB_DASHBOARD_PORT/" "Web Dashboard"; then
            success "Web dashboard started (PID: $ui_pid)"
            return 0
        else
            warning "Web dashboard failed to start; check $LOG_DIR/web_dashboard.log"
        fi
    else
        warning "Web dashboard port $WEB_DASHBOARD_PORT is in use; skipping web dashboard start"
    fi

    warning "No UI started. Check logs: $LOG_DIR/ui.log or openclaw_ui.log or web_dashboard.log"
    return 0
}

# Function to verify integration
verify_integration() {
    info "Verifying LUCIFER-OS OpenClaw integration..."

    # Test backend skills endpoint
    if curl -s "http://127.0.0.1:$BACKEND_PORT/openclaw/redteam-skills" | grep -q '"success":true'; then
        success "Backend skills endpoint responding"
    else
        error "Backend skills endpoint not responding correctly"
        return 1
    fi

    # Test gateway status
    if curl -s "http://127.0.0.1:$GATEWAY_PORT/api/status" >/dev/null 2>&1; then
        success "Gateway status endpoint responding"
    else
        warning "Gateway status endpoint not responding (may be normal for dev mode)"
    fi

    # Test a skill execution
    info "Testing LILITH skill execution..."
    local test_result
    test_result=$(curl -s -X POST "http://127.0.0.1:$BACKEND_PORT/openclaw/skill/lilith" \
        -H "Content-Type: application/json" \
        -d '{"args": ["recon", "127.0.0.1"], "background": false}' 2>/dev/null || echo "failed")

    if echo "$test_result" | grep -q "success\|response"; then
        success "LILITH skill test successful"
    else
        warning "LILITH skill test returned: $test_result"
    fi

    return 0
}

# Function to show status
show_status() {
    echo
    info "=== LUCIFER-OS OpenClaw Integration Status ==="
    echo

    # Backend status
    if curl -s "http://127.0.0.1:$BACKEND_PORT/openclaw/redteam-skills" >/dev/null 2>&1; then
        success "✓ LUCIFER-OS Backend: RUNNING (Port $BACKEND_PORT)"
    else
        error "✗ LUCIFER-OS Backend: NOT RUNNING"
    fi

    # Gateway status
    if curl -s "http://127.0.0.1:$GATEWAY_PORT/api/status" >/dev/null 2>&1; then
        success "✓ OpenClaw Gateway: RUNNING (Port $GATEWAY_PORT)"
    else
        warning "⚠ OpenClaw Gateway: STATUS UNKNOWN (may be normal for dev mode)"
    fi

    # Skills count
    local skills_count
    skills_count=$(curl -s "http://127.0.0.1:$BACKEND_PORT/openclaw/redteam-skills" | grep -o '"total":[0-9]*' | cut -d':' -f2 || echo "0")
    info "Available Skills: $skills_count"

    echo
    info "=== Access URLs ==="
    echo "LUCIFER-OS Dashboard: http://127.0.0.1:3000"
    echo "Web Dashboard: http://$WEB_DASHBOARD_HOST:$WEB_DASHBOARD_PORT/"
    echo "Backend API: http://127.0.0.1:$BACKEND_PORT"
    echo "OpenClaw Gateway: http://127.0.0.1:$GATEWAY_PORT"
    echo
}

# Main startup sequence
main() {
    log "=== LUCIFER-OS OpenClaw Integrated Startup ==="
    log "Starting integrated system..."

    # Start backend first
    if ! start_backend; then
        error "Failed to start LUCIFER-OS backend"
        exit 1
    fi

    # Start gateway
    if ! start_gateway; then
        error "Failed to start OpenClaw gateway"
        exit 1
    fi

    # Start Telegram bot and UI
    if ! start_telegram_bot; then
        warning "Telegram bot failed to start"
    fi

    if ! start_ui; then
        warning "UI failed to start"
    fi

    # Verify integration
    if verify_integration; then
        success "Integration verification completed"
    else
        warning "Some integration checks failed, but continuing..."
    fi

    # Show final status
    show_status

    success "LUCIFER-OS OpenClaw integration startup complete!"
    log "System is ready for red team operations"

    # Keep running to show logs
    info "Press Ctrl+C to stop all services"
    trap 'log "Shutdown requested..."; exit 0' INT
    wait
}

# Run main function

main "$@"
