# Setup script to configure LuciferOS to use an online Hugging Face Dolphin model
# This uses the HF Inference API (free tier) - NO local model required

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " HuggingFace Dolphin Model Setup" -ForegroundColor Cyan
Write-Host " (Online/Cloud - Free Tier)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$WorkspaceRoot = Split-Path -Parent $PSScriptRoot
$ConfigPath = Join-Path $WorkspaceRoot "config\lucifera.conf"
$VenvPython = Join-Path $WorkspaceRoot ".venv\Scripts\python.exe"

# Dolphin models available on HuggingFace Inference API (free tier)
# These are hosted online by HF - no local GPU needed
$DolphinModels = @(
    "cognitivecomputations/dolphin-2.9.3-mistral-nemo-12b",
    "cognitivecomputations/dolphin-2.8-mistral-7b-v02",
    "cognitivecomputations/dolphin-2.6-mixtral-8x7b"
)

Write-Host ""
Write-Host "[1] Updating configuration for online HuggingFace hosting..." -ForegroundColor Yellow

# Read current config
$configContent = Get-Content $ConfigPath -Raw

# Update to use huggingface host (online, not ollama)
$configContent = $configContent -replace "host\s*=\s*ollama", "host = huggingface"

# Set the Dolphin model
$selectedModel = $DolphinModels[0]  # Default to the first one
$configContent = $configContent -replace "model\s*=\s*[^\r\n]+", "model = $selectedModel"

# Ensure we have the HF router URL (free inference API)
if ($configContent -notmatch "hf_api_url") {
    $configContent = $configContent -replace "(\[lilith\])", "`$1`nhf_api_url = https://router.huggingface.co/v1"
}

# Write updated config
Set-Content -Path $ConfigPath -Value $configContent -Encoding UTF8
Write-Host "[+] Config updated: host=huggingface, model=$selectedModel" -ForegroundColor Green

Write-Host ""
Write-Host "[2] Installing required Python packages for HF Inference..." -ForegroundColor Yellow

# Install/upgrade openai package (used for HF OpenAI-compatible API)
& $VenvPython -m pip install --upgrade openai httpx 2>&1 | Out-Null
Write-Host "[+] Packages installed" -ForegroundColor Green

Write-Host ""
Write-Host "[3] Verifying HuggingFace token..." -ForegroundColor Yellow

# Check if HF token exists in config
$hfToken = $null
if ($configContent -match "hf_token\s*=\s*(\S+)") {
    $hfToken = $Matches[1]
}

if ($hfToken -and $hfToken -ne "YOUR_HF_TOKEN_HERE") {
    Write-Host "[+] HF token found in config" -ForegroundColor Green
} else {
    Write-Host "[!] WARNING: No valid HF token found!" -ForegroundColor Red
    Write-Host "    Edit config/lucifera.conf and set hf_token = your_token" -ForegroundColor Red
    Write-Host "    Get a free token at: https://huggingface.co/settings/tokens" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration:" -ForegroundColor White
Write-Host "  Host:  huggingface (online/cloud)" -ForegroundColor Gray
Write-Host "  Model: $selectedModel" -ForegroundColor Gray
Write-Host "  API:   https://router.huggingface.co/v1 (free tier)" -ForegroundColor Gray
Write-Host ""
Write-Host "To start the system, run:" -ForegroundColor Yellow
Write-Host "  .\scripts\start_all.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "NOTE: The HF free tier has rate limits. If you hit limits," -ForegroundColor Yellow
Write-Host "      consider upgrading to HF Pro or using a different model." -ForegroundColor Yellow
