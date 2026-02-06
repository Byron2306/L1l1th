# Uninstall OpenClaw/Clawdbot completely on Windows
# Run this script in PowerShell as Administrator if needed

Write-Host "[+] Uninstalling OpenClaw integration..." -ForegroundColor Yellow

# Remove local cloned folder if present
$optPath = "C:\opt\openclaw"
if (Test-Path $optPath) {
    Write-Host "[+] Removing $optPath"
    Remove-Item -Recurse -Force $optPath
} else {
    Write-Host "[!] $optPath not found; skipping"
}

# Remove any openclaw folder in the workspace
$workspaceOC = Join-Path $PSScriptRoot "..\openclaw"
if (Test-Path $workspaceOC) {
    Write-Host "[+] Removing workspace openclaw folder: $workspaceOC"
    Remove-Item -Recurse -Force $workspaceOC
}

# Uninstall openclaw pip package if installed
Write-Host "[+] Attempting to uninstall openclaw pip package..."
& "$PSScriptRoot\..\\.venv\Scripts\pip.exe" uninstall -y openclaw 2>$null
& "$PSScriptRoot\..\\.venv\Scripts\pip.exe" uninstall -y clawdbot 2>$null

# Update config to disable openclaw
$configPath = Join-Path $PSScriptRoot "..\config\lucifera.conf"
if (Test-Path $configPath) {
    $content = Get-Content $configPath -Raw
    $content = $content -replace "openclaw_enabled\s*=\s*true", "openclaw_enabled = false"
    Set-Content -Path $configPath -Value $content -Encoding UTF8
    Write-Host "[+] Disabled openclaw_enabled in config"
}

Write-Host "[+] OpenClaw uninstall complete." -ForegroundColor Green
