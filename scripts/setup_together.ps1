# Together.ai Setup for LuciferOS
# Together.ai provides $25 FREE credits with full function calling + reasoning support

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host " Together.ai Setup for LuciferOS LILITH" -ForegroundColor Cyan  
Write-Host " $25 FREE Credits - Full Tools + Reasoning" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan

$WorkspaceRoot = Split-Path -Parent $PSScriptRoot
$ConfigPath = Join-Path $WorkspaceRoot "config\lucifera.conf"

Write-Host "`n[1] GET YOUR FREE TOGETHER.AI API KEY:" -ForegroundColor Yellow
Write-Host "    1. Go to: https://api.together.ai/signup" -ForegroundColor White
Write-Host "    2. Sign up with Google/GitHub (instant, no credit card)" -ForegroundColor White
Write-Host "    3. You get `$25 FREE credits automatically" -ForegroundColor Green
Write-Host "    4. Copy your API key from: https://api.together.ai/settings/api-keys" -ForegroundColor White

Write-Host "`n[2] Enter your Together.ai API key:" -ForegroundColor Yellow
$ApiKey = Read-Host "    API Key"

if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    Write-Host "`n[!] No API key provided. Please run this script again with your key." -ForegroundColor Red
    Write-Host "    Get your free key at: https://api.together.ai/signup" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n[3] Updating configuration..." -ForegroundColor Yellow

# Read current config
$ConfigContent = Get-Content $ConfigPath -Raw

# Update the together_key
$ConfigContent = $ConfigContent -replace 'together_key\s*=\s*.*', "together_key = $ApiKey"

# Write back
$ConfigContent | Set-Content $ConfigPath -NoNewline

Write-Host "    Configuration updated: $ConfigPath" -ForegroundColor Green

Write-Host "`n[4] Testing API connection..." -ForegroundColor Yellow

$Headers = @{
    "Authorization" = "Bearer $ApiKey"
    "Content-Type" = "application/json"
}

$Body = @{
    model = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    messages = @(
        @{
            role = "user"
            content = "Say 'LILITH online' in exactly 2 words"
        }
    )
    max_tokens = 20
} | ConvertTo-Json -Depth 3

try {
    $Response = Invoke-RestMethod -Uri "https://api.together.xyz/v1/chat/completions" -Method POST -Headers $Headers -Body $Body -TimeoutSec 30
    $Message = $Response.choices[0].message.content
    Write-Host "    API Response: $Message" -ForegroundColor Green
    Write-Host "`n[SUCCESS] Together.ai is configured and working!" -ForegroundColor Green
} catch {
    Write-Host "    [!] API test failed: $_" -ForegroundColor Red
    Write-Host "    Please verify your API key is correct" -ForegroundColor Yellow
}

Write-Host "`n[5] Available Models with Function Calling:" -ForegroundColor Yellow
Write-Host "    - meta-llama/Llama-3.3-70B-Instruct-Turbo (CURRENT - Fast + Tools)" -ForegroundColor Cyan
Write-Host "    - meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo (Most Powerful)" -ForegroundColor White
Write-Host "    - Qwen/Qwen2.5-72B-Instruct-Turbo (Great for coding)" -ForegroundColor White
Write-Host "    - deepseek-ai/DeepSeek-R1 (Reasoning model)" -ForegroundColor White
Write-Host "    - deepseek-ai/DeepSeek-V3 (Fast reasoning)" -ForegroundColor White

Write-Host "`n[6] Pricing (from your `$25 free credits):" -ForegroundColor Yellow
Write-Host "    - Llama 3.3 70B: `$0.88/M tokens (~28M tokens free)" -ForegroundColor White
Write-Host "    - Llama 3.1 8B:  `$0.18/M tokens (~138M tokens free)" -ForegroundColor White
Write-Host "    - DeepSeek-R1:   `$3.00/M input (reasoning model)" -ForegroundColor White

Write-Host "`n===============================================" -ForegroundColor Cyan
Write-Host " Setup Complete! Start the backend:" -ForegroundColor Green
Write-Host " python tools/lilith_complete.py" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Cyan
