# ============================================================================
# LUCIFERAOS - FULL SYSTEM STARTUP
# ============================================================================
# This script starts all components of the LuciferOS red team platform
# ============================================================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Red
Write-Host "       LUCIFERAOS - RED TEAM COMMAND CENTER                 " -ForegroundColor Red
Write-Host "============================================================" -ForegroundColor Red
Write-Host ""

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ROOT

# Kill any existing processes
Write-Host "[1/5] Cleaning up existing processes..." -ForegroundColor Yellow
taskkill /F /IM python.exe 2>$null | Out-Null
Start-Sleep -Seconds 2

# Activate virtual environment
Write-Host "[2/5] Activating Python environment..." -ForegroundColor Yellow
$VENV = "$ROOT\.venv\Scripts\python.exe"
if (-not (Test-Path $VENV)) {
    Write-Host "  [!] Virtual environment not found, using system Python" -ForegroundColor Yellow
    $VENV = "python"
}

# Start backend
Write-Host "[3/5] Starting LILITH Backend..." -ForegroundColor Green
$backendJob = Start-Process -FilePath $VENV -ArgumentList "$ROOT\tools\lilith_full_backend.py" -WorkingDirectory "$ROOT\tools" -PassThru -WindowStyle Minimized
Start-Sleep -Seconds 3

# Check backend
$status = $null
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/status" -Method GET -TimeoutSec 5 -ErrorAction SilentlyContinue
    $status = $response.Content | ConvertFrom-Json
} catch {}

if ($status) {
    Write-Host "  [+] Backend ONLINE at http://127.0.0.1:5000" -ForegroundColor Green
    Write-Host "  [+] AI Providers: $($status.ai_providers.active_count) active" -ForegroundColor Cyan
} else {
    Write-Host "  [!] Backend may still be starting..." -ForegroundColor Yellow
}

# Check OpenClaw
Write-Host "[4/5] Checking OpenClaw..." -ForegroundColor Yellow
$openclawPath = "$ROOT\openclaw"
if (Test-Path "$openclawPath\openclaw.mjs") {
    try {
        $skillsResponse = Invoke-WebRequest -Uri "http://127.0.0.1:5000/openclaw/redteam-skills" -Method GET -TimeoutSec 5 -ErrorAction SilentlyContinue
        $skills = $skillsResponse.Content | ConvertFrom-Json
        Write-Host "  [+] OpenClaw: $($skills.total) red team skills available" -ForegroundColor Green
    } catch {
        Write-Host "  [!] OpenClaw skills endpoint not responding yet" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [!] OpenClaw not installed" -ForegroundColor Yellow
}

# Start Dashboard
Write-Host "[5/5] Launching Dashboard UI..." -ForegroundColor Green
Start-Process -FilePath $VENV -ArgumentList "$ROOT\ui\dashboard_streamlined.py" -WorkingDirectory "$ROOT\ui"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  LUCIFERAOS STARTUP COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Backend:    http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host "  Attack Srv: http://127.0.0.1:8888" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Dashboard UI should open automatically." -ForegroundColor White
Write-Host ""
Write-Host "  To stop: taskkill /F /IM python.exe" -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================================" -ForegroundColor Red
Write-Host ""

# Keep window open
Read-Host "Press Enter to close this window"
