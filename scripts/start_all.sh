#!/usr/bin/env bash
# Start LuciferOS components on Unix-like systems
VENV_PY="$(pwd)/.venv/bin/python"
WATCHDOG="$(pwd)/tools/backend_watchdog.py"
DASHBOARD="$(pwd)/ui/dashboard_complete.py"

echo "[+] Starting LuciferOS (safe mode)"
"$VENV_PY" "$WATCHDOG" &

# Wait for backend readiness
MAX_RETRIES=30
RETRY=0
OK=0
while [ $RETRY -lt $MAX_RETRIES ]; do
  if curl -s --connect-timeout 2 http://127.0.0.1:5000/status | grep -q 'ONLINE'; then
    OK=1
    break
  fi
  sleep 1
  RETRY=$((RETRY+1))
done

if [ $OK -eq 1 ]; then
  echo "[+] Backend is up. Launching dashboard..."
  "$VENV_PY" "$DASHBOARD" &
else
  echo "[-] Backend did not become ready after $MAX_RETRIES retries. Check logs and run watchdog manually." >&2
fi