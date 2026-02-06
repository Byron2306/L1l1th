# Start all LuciferOS components (Windows PowerShell)
# Usage: Right-click -> Run with PowerShell (or run from an elevated PowerShell if needed)

# Ensure script uses project's venv Python
$VenvPython = "C:\LuciferOS_FULL\.venv\Scripts\python.exe"
$Watchdog = "c:\LuciferOS_FULL\tools\backend_watchdog.py"
$Dashboard = "c:\LuciferOS_FULL\ui\dashboard_complete.py"

# Safety: ensure malware deployment is not run as part of startup
Write-Host "[+] Starting LuciferOS (safe mode)"

# Start watchdog (detached)
Start-Process -FilePath $VenvPython -ArgumentList $Watchdog

# Wait for backend readiness
$maxRetries = 30
$retry = 0
$ok = $false
while (-not $ok -and $retry -lt $maxRetries) {
    try {
        $r = Invoke-RestMethod -Uri http://127.0.0.1:5000/status -Method GET -TimeoutSec 3
        if ($r -and $r.status -eq 'ONLINE') { $ok = $true; break }
    } catch { }
    Start-Sleep -Seconds 1
    $retry++
}

if ($ok) {
    Write-Host "[+] Backend is up. Launching dashboard..."
    Start-Process -NoNewWindow -FilePath $VenvPython -ArgumentList $Dashboard
} else {
    Write-Host "[-] Backend did not become ready after $maxRetries retries. Check logs and run watchdog manually." -ForegroundColor Red
}
