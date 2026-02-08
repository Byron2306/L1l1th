#!/usr/bin/env bash
# LUCIFEROS MASTER STARTUP SCRIPT
# Complete system integration with all components

set -e  # Exit on any error

# Configuration
VENV_PATH="./.venv"
PYTHON="${VENV_PATH}/bin/python"
MASTER_BACKEND="./tools/luciferos_master_backend.py"
MASTER_UI="./ui/luciferos_master_dashboard.py"
BACKEND_PID_FILE="./logs/backend.pid"
UI_PID_FILE="./logs/ui.pid"
LOG_DIR="./logs"

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
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_DIR/startup.log"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_DIR/startup.log" >&2
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_DIR/startup.log"
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a "$LOG_DIR/startup.log"
}

# Cleanup function
cleanup() {
    log "🧹 Cleaning up processes..."

    # Kill backend if running
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            log "Stopping backend (PID: $BACKEND_PID)"
            kill "$BACKEND_PID" 2>/dev/null || true
        fi
        rm -f "$BACKEND_PID_FILE"
    fi

    # Kill UI if running
    if [ -f "$UI_PID_FILE" ]; then
        UI_PID=$(cat "$UI_PID_FILE")
        if kill -0 "$UI_PID" 2>/dev/null; then
            log "Stopping UI (PID: $UI_PID)"
            kill "$UI_PID" 2>/dev/null || true
        fi
        rm -f "$UI_PID_FILE"
    fi

    # Kill any remaining Python processes from this directory
    pkill -f "python.*luciferos" || true
    pkill -f "python.*lilith" || true

    log "✅ Cleanup complete"
}

# Trap signals
trap cleanup EXIT INT TERM

# Check if virtual environment exists
check_venv() {
    if [ ! -d "$VENV_PATH" ]; then
        error "Virtual environment not found at $VENV_PATH"
        error "Please run setup scripts first:"
        error "  ./scripts/setup_openclaw.sh"
        error "  pip install -r requirements.txt"
        exit 1
    fi

    if [ ! -x "$PYTHON" ]; then
        error "Python executable not found at $PYTHON"
        exit 1
    fi

    log "✅ Virtual environment ready"
}

# Check system dependencies
check_dependencies() {
    log "🔍 Checking system dependencies..."

    # Check Python version
    PYTHON_VERSION=$("$PYTHON" --version 2>&1 | grep -oP '\d+\.\d+')
    if ! "$PYTHON" -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
        error "Python 3.8+ required, found $PYTHON_VERSION"
        exit 1
    fi
    log "✅ Python $PYTHON_VERSION"

    # Check required Python packages
    REQUIRED_PACKAGES=("flask" "requests" "pyqt5" "playwright")
    for package in "${REQUIRED_PACKAGES[@]}"; do
        if ! "$PYTHON" -c "import $package" 2>/dev/null; then
            error "Required package '$package' not found"
            error "Run: $PYTHON -m pip install $package"
            exit 1
        fi
    done
    log "✅ Python packages installed"

    # Check Node.js for OpenClaw (optional)
    if command -v node >/dev/null 2>&1; then
        NODE_VERSION=$(node --version)
        log "✅ Node.js available: $NODE_VERSION"
        OPENCLAW_AVAILABLE=true
    else
        warning "Node.js not found - OpenClaw integration disabled"
        OPENCLAW_AVAILABLE=false
    fi

    # Check for browser binaries
    if command -v google-chrome >/dev/null 2>&1 || command -v chromium-browser >/dev/null 2>&1; then
        log "✅ Browser available for automation"
    else
        warning "No Chrome/Chromium found - browser automation limited"
    fi
}

# Install Playwright browsers
install_playwright() {
    log "🎭 Installing Playwright browsers..."
    if ! "$PYTHON" -m playwright install chromium 2>/dev/null; then
        warning "Playwright browser installation failed - browser features may not work"
    else
        log "✅ Playwright browsers installed"
    fi
}

# Start OpenClaw if available
start_openclaw() {
    if [ "$OPENCLAW_AVAILABLE" = true ]; then
        log "🦞 Starting OpenClaw integration..."

        # Check if OpenClaw directory exists
        if [ -d "./openclaw" ]; then
            cd "./openclaw"

            # Check if OpenClaw is already running
            if pgrep -f "openclaw.*gateway" >/dev/null; then
                log "✅ OpenClaw gateway already running"
            else
                # Start OpenClaw gateway
                if command -v pnpm >/dev/null 2>&1; then
                    nohup pnpm run gateway:dev > "../logs/openclaw.log" 2>&1 &
                    OPENCLAW_PID=$!
                    echo $OPENCLAW_PID > "../logs/openclaw.pid"
                    log "✅ OpenClaw gateway started (PID: $OPENCLAW_PID)"
                else
                    warning "pnpm not found - OpenClaw integration skipped"
                fi
            fi

            cd ..
        else
            warning "OpenClaw directory not found - integration disabled"
        fi
    fi
}

# Start backend
start_backend() {
    log "🚀 Starting LuciferOS Master Backend..."

    # Check if backend is already running
    if [ -f "$BACKEND_PID_FILE" ]; then
        OLD_PID=$(cat "$BACKEND_PID_FILE")
        if kill -0 "$OLD_PID" 2>/dev/null; then
            log "✅ Backend already running (PID: $OLD_PID)"
            return
        else
            rm -f "$BACKEND_PID_FILE"
        fi
    fi

    # Start backend
    nohup "$PYTHON" "$MASTER_BACKEND" > "$LOG_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$BACKEND_PID_FILE"

    log "✅ Backend started (PID: $BACKEND_PID)"

    # Wait for backend to be ready
    log "⏳ Waiting for backend readiness..."
    MAX_RETRIES=30
    RETRY=0
    while [ $RETRY -lt $MAX_RETRIES ]; do
        if curl -s --connect-timeout 2 http://127.0.0.1:5000/status >/dev/null 2>&1; then
            log "✅ Backend is ready"
            return
        fi
        sleep 1
        RETRY=$((RETRY+1))
    done

    error "Backend failed to become ready after $MAX_RETRIES seconds"
    error "Check logs at $LOG_DIR/backend.log"
    exit 1
}

# Start UI
start_ui() {
    log "🖥️  Starting LuciferOS Master UI..."

    # Check if UI is already running
    if [ -f "$UI_PID_FILE" ]; then
        OLD_PID=$(cat "$UI_PID_FILE")
        if kill -0 "$OLD_PID" 2>/dev/null; then
            log "✅ UI already running (PID: $OLD_PID)"
            return
        else
            rm -f "$UI_PID_FILE"
        fi
    fi

    # Start UI
    nohup "$PYTHON" "$MASTER_UI" > "$LOG_DIR/ui.log" 2>&1 &
    UI_PID=$!
    echo $UI_PID > "$UI_PID_FILE"

    log "✅ UI started (PID: $UI_PID)"

    # Give UI time to start
    sleep 2
}

# Show system status
show_status() {
    log "📊 System Status:"

    # Backend status
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            echo -e "  ${GREEN}✅ Backend running (PID: $BACKEND_PID)${NC}"
        else
            echo -e "  ${RED}❌ Backend not responding${NC}"
        fi
    else
        echo -e "  ${RED}❌ Backend not started${NC}"
    fi

    # UI status
    if [ -f "$UI_PID_FILE" ]; then
        UI_PID=$(cat "$UI_PID_FILE")
        if kill -0 "$UI_PID" 2>/dev/null; then
            echo -e "  ${GREEN}✅ UI running (PID: $UI_PID)${NC}"
        else
            echo -e "  ${RED}❌ UI not responding${NC}"
        fi
    else
        echo -e "  ${RED}❌ UI not started${NC}"
    fi

    # OpenClaw status
    if [ -f "./logs/openclaw.pid" ]; then
        OPENCLAW_PID=$(cat "./logs/openclaw.pid")
        if kill -0 "$OPENCLAW_PID" 2>/dev/null; then
            echo -e "  ${GREEN}✅ OpenClaw running (PID: $OPENCLAW_PID)${NC}"
        else
            echo -e "  ${YELLOW}⚠️  OpenClaw not responding${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠️  OpenClaw not started${NC}"
    fi

    # API status
    if curl -s --connect-timeout 2 http://127.0.0.1:5000/health >/dev/null 2>&1; then
        echo -e "  ${GREEN}✅ API responding${NC}"
    else
        echo -e "  ${RED}❌ API not responding${NC}"
    fi
}

# Main startup sequence
main() {
    echo "
╔══════════════════════════════════════════════════════════╗
║                 LUCIFEROS MASTER STARTUP                 ║
║                 Ultimate Red Team Integration           ║
╚══════════════════════════════════════════════════════════╝
"

    log "🔥 Starting LuciferOS Master System v2026.2.7"

    # Pre-flight checks
    check_venv
    check_dependencies
    install_playwright

    # Start components
    start_openclaw
    start_backend
    start_ui

    # Show final status
    echo
    show_status
    echo

    log "🎯 LuciferOS Master System ready!"
    log "🌐 UI: http://localhost:5000 (if web interface enabled)"
    log "📊 API: http://localhost:5000/api/"
    log "📝 Logs: $LOG_DIR/"
    echo
    log "Press Ctrl+C to stop all services"

    # Keep running and monitor
    while true; do
        sleep 10

        # Check if components are still running
        if [ -f "$BACKEND_PID_FILE" ]; then
            BACKEND_PID=$(cat "$BACKEND_PID_FILE")
            if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
                error "Backend process died - restarting..."
                start_backend
            fi
        fi

        if [ -f "$UI_PID_FILE" ]; then
            UI_PID=$(cat "$UI_PID_FILE")
            if ! kill -0 "$UI_PID" 2>/dev/null; then
                warning "UI process died - restarting..."
                start_ui
            fi
        fi
    done
}

# Handle command line arguments
case "${1:-}" in
    "stop")
        log "🛑 Stopping all LuciferOS services..."
        cleanup
        log "✅ All services stopped"
        exit 0
        ;;
    "status")
        show_status
        exit 0
        ;;
    "restart")
        log "🔄 Restarting LuciferOS services..."
        cleanup
        sleep 2
        main
        ;;
    "backend-only")
        log "🚀 Starting backend only..."
        check_venv
        check_dependencies
        start_backend
        show_status
        log "Backend ready. Press Ctrl+C to stop."
        wait
        ;;
    "ui-only")
        log "🖥️  Starting UI only..."
        check_venv
        check_dependencies
        start_ui
        show_status
        log "UI ready. Press Ctrl+C to stop."
        wait
        ;;
    *)
        main
        ;;
esac</content>
<parameter name="filePath">/workspaces/LUCIFER-OS/scripts/start_master.sh