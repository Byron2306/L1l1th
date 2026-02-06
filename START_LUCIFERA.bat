@echo off
:: LUCIFERA - One-Click Launcher (BAT version)
:: Double-click this to start LUCIFERA

title LUCIFERA - Red Team Command Center

echo.
echo ========================================
echo    LUCIFERA - Red Team Command Center
echo ========================================
echo.

cd /d "%~dp0"

:: Activate venv if exists
if exist ".venv\Scripts\activate.bat" (
    echo [*] Activating virtual environment...
    call .venv\Scripts\activate.bat
)

:: Kill old processes
echo [*] Cleaning up...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 1 >nul

:: Start backend in new minimized window
echo [*] Starting Backend...
start /min "LILITH Backend" python tools\lilith_full_backend.py

:: Wait for backend
echo [*] Waiting for backend...
timeout /t 5 >nul

:: Check backend
curl -s http://127.0.0.1:5000/status >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Backend may not be ready, waiting more...
    timeout /t 5 >nul
)

:: Start dashboard
echo [*] Starting Dashboard...
echo.
echo ========================================
echo    LUCIFERA READY - ENGAGE TARGET
echo ========================================
echo.

python ui\dashboard_streamlined.py

:: Cleanup when dashboard closes
echo.
echo [*] Shutting down...
taskkill /F /IM python.exe >nul 2>&1
echo [+] LUCIFERA shutdown complete.
pause
