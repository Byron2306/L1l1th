@echo off
title LUCIFERAOS - Red Team Command Center
color 0C
echo.
echo ============================================================
echo        LUCIFERAOS - RED TEAM COMMAND CENTER
echo ============================================================
echo.

cd /d "%~dp0"

echo [*] Starting LuciferOS...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0START_ALL.ps1"
