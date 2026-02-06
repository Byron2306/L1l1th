# LUCIFERA - One-Click Launcher
# Starts Backend + Streamlined Dashboard

Write-Host ""
Write-Host "========================================" -ForegroundColor Red
Write-Host "   LUCIFERA - Red Team Command Center  " -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Kill any existing Python processes that might conflict
Write-Host "[*] Cleaning up old processes..." -ForegroundColor Yellow
taskkill /F /IM python.exe 2>$null | Out-Null
Start-Sleep -Seconds 1

# Activate virtual environment if exists
$VenvPath = Join-Path $ScriptDir ".venv\Scripts\Activate.ps1"
if (Test-Path $VenvPath) {
    Write-Host "[*] Activating virtual environment..." -ForegroundColor Cyan
    & $VenvPath
}

# Start the backend
Write-Host "[*] Starting LILITH Backend..." -ForegroundColor Green
$BackendPath = Join-Path $ScriptDir "tools\lilith_full_backend.py"

# Start backend in background
$BackendProcess = Start-Process -FilePath "python" -ArgumentList $BackendPath -WorkingDirectory (Join-Path $ScriptDir "tools") -PassThru -WindowStyle Minimized
Write-Host "[+] Backend PID: $($BackendProcess.Id)" -ForegroundColor Green

# Wait for backend to be ready
Write-Host "[*] Waiting for backend to initialize..." -ForegroundColor Yellow
$MaxAttempts = 15
$Attempt = 0
$BackendReady = $false

while ($Attempt -lt $MaxAttempts -and -not $BackendReady) {
    Start-Sleep -Seconds 1
    $Attempt++
    try {
        $Response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/status" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($Response.status -eq "online") {
            $BackendReady = $true
            Write-Host "[+] Backend ONLINE!" -ForegroundColor Green
            
            # Show AI provider status
            if ($Response.ai_providers) {
                $Active = $Response.ai_providers.active_count
                $Total = $Response.ai_providers.total_count
                Write-Host "[+] AI Providers: $Active/$Total available" -ForegroundColor Cyan
                foreach ($Provider in $Response.ai_providers.providers) {
                    $Status = if ($Provider.is_available) { "OK" } else { "DOWN" }
                    $Color = if ($Provider.is_available) { "Green" } else { "Red" }
                    Write-Host "    - $($Provider.name): $Status" -ForegroundColor $Color
                }
            }
        }
    } catch {
        Write-Host "    Attempt $Attempt/$MaxAttempts..." -ForegroundColor DarkGray
    }
}

if (-not $BackendReady) {
    Write-Host "[!] Backend failed to start. Check for errors." -ForegroundColor Red
    Write-Host "[!] Try running manually: python tools\lilith_full_backend.py" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Start the streamlined dashboard
Write-Host ""
Write-Host "[*] Starting Streamlined Dashboard..." -ForegroundColor Green
$DashboardPath = Join-Path $ScriptDir "ui\dashboard_streamlined.py"

# Run dashboard in foreground (this will block until closed)
Write-Host "[+] Dashboard launching..." -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Red
Write-Host "   LUCIFERA READY - ENGAGE TARGET      " -ForegroundColor Red  
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

# Start dashboard
& python $DashboardPath

# When dashboard closes, cleanup
Write-Host ""
Write-Host "[*] Dashboard closed. Cleaning up..." -ForegroundColor Yellow

# Stop backend
if ($BackendProcess -and -not $BackendProcess.HasExited) {
    Stop-Process -Id $BackendProcess.Id -Force -ErrorAction SilentlyContinue
    Write-Host "[+] Backend stopped." -ForegroundColor Green
}

Write-Host "[+] LUCIFERA shutdown complete." -ForegroundColor Green
