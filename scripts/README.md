# LuciferOS Start Scripts

This folder contains convenience scripts to start the backend and dashboard reliably.

- `start_all.ps1` (Windows) — starts a watchdog that ensures the backend is up, waits for readiness, then launches the dashboard.
- `start_backend.ps1` (Windows) — starts the backend detached.
- `start_dashboard.ps1` (Windows) — starts the dashboard detached.
- `start_all.sh` (Unix) — same behavior for Unix-like systems.

Usage (Windows):
1. Open PowerShell.
2. Run `.	ools\bind_test.py` or `.	ools\backend_watchdog.py` manually to debug.
3. Run `.	ools\backend_watchdog.py` or `scripts\start_all.ps1`.

Safety note: The project contains `tools/malware_deployment.py` which is intentionally malicious. These start scripts do NOT execute that file. Keep malware modules disabled or isolated when debugging.
