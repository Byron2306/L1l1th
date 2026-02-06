# OpenClaw/ClawdBot Setup for Windows
# Uses OpenRouter free models (no API key required for :free models)

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host " OpenClaw Setup with OpenRouter Free Models" -ForegroundColor Cyan  
Write-Host "===============================================" -ForegroundColor Cyan

$WorkspaceRoot = Split-Path -Parent $PSScriptRoot
$VenvPython = Join-Path $WorkspaceRoot ".venv\Scripts\python.exe"
$OpenClawDir = Join-Path $WorkspaceRoot "openclaw"

# Step 1: Clone OpenClaw if not present
Write-Host "`n[1] Setting up OpenClaw..." -ForegroundColor Yellow
if (-not (Test-Path $OpenClawDir)) {
    Write-Host "    Cloning OpenClaw repository..." -ForegroundColor Gray
    git clone https://github.com/openclaw/openclaw.git $OpenClawDir 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    [!] Could not clone OpenClaw repo. Creating local structure..." -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $OpenClawDir -Force | Out-Null
    }
} else {
    Write-Host "    OpenClaw directory already exists" -ForegroundColor Green
}

# Step 2: Create the LILITH bridge for OpenClaw
Write-Host "`n[2] Creating LILITH-OpenClaw bridge..." -ForegroundColor Yellow

$BridgeScript = @'
#!/usr/bin/env python3
"""
LILITH-OpenClaw Bridge
Connects OpenClaw CLI to LuciferOS LILITH agent via OpenRouter free models
No API key required for free-tier models (models ending with :free)
"""
import requests
import json
import configparser
import os
from pathlib import Path

class LILITHOpenClawBridge:
    def __init__(self):
        # Find and load LuciferOS config
        self.config = configparser.ConfigParser()
        config_paths = [
            Path(__file__).resolve().parents[1] / 'config' / 'lucifera.conf',
            Path(__file__).resolve().parents[0] / '..' / 'config' / 'lucifera.conf',
            Path(os.environ.get('LUCIFEROS_CONFIG', '')) if os.environ.get('LUCIFEROS_CONFIG') else None,
        ]
        
        for cp in config_paths:
            if cp and cp.exists():
                self.config.read(cp)
                print(f"[+] Loaded config from: {cp}")
                break
        
        # OpenRouter configuration (free models work without key)
        self.api_url = self.config.get('lilith', 'api_url', fallback='https://openrouter.ai/api/v1')
        self.model = self.config.get('lilith', 'model', fallback='qwen/qwen3-coder:free')
        self.openrouter_key = self.config.get('lilith', 'openrouter_key', fallback='')
        
        # LILITH backend for integrated queries
        self.lilith_url = "http://127.0.0.1:5000"
        
        print(f"[+] Bridge initialized")
        print(f"    Model: {self.model}")
        print(f"    API: {self.api_url}")
    
    def query_model(self, prompt, system_prompt=None):
        """Query the AI model directly via OpenRouter"""
        headers = {
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/luciferOS",
            "X-Title": "LuciferOS-OpenClaw"
        }
        
        # Add API key if provided (optional for free models)
        if self.openrouter_key:
            headers["Authorization"] = f"Bearer {self.openrouter_key}"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 2048
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return f"Error {response.status_code}: {response.text}"
        except Exception as e:
            return f"Request failed: {str(e)}"
    
    def query_lilith(self, prompt):
        """Query via LILITH backend if available"""
        try:
            response = requests.post(
                f"{self.lilith_url}/chat",
                json={"message": prompt},
                timeout=120
            )
            if response.status_code == 200:
                return response.json().get('response', '')
        except requests.exceptions.ConnectionError:
            pass
        
        # Fallback to direct OpenRouter
        return self.query_model(prompt)
    
    def analyze_target(self, target, attack_type="reconnaissance"):
        """Analyze target for attack planning"""
        prompt = f"""Analyze the following target for {attack_type}:

Target: {target}

Provide:
1. Attack surface analysis
2. Potential vulnerabilities
3. Recommended attack vectors
4. OpenClaw payload suggestions
5. Evasion techniques

Be specific and technical."""
        
        return self.query_lilith(prompt)
    
    def generate_payload(self, payload_type, target_platform):
        """Generate attack payload specifications"""
        prompt = f"""Generate a {payload_type} payload for {target_platform}.

Include:
1. Payload structure
2. Delivery mechanism
3. Execution chain
4. Obfuscation methods
5. C2 configuration

Provide code snippets where applicable."""
        
        return self.query_lilith(prompt)
    
    def cli_chat(self):
        """Interactive CLI chat mode"""
        print("\n" + "="*50)
        print("LILITH-OpenClaw Interactive Mode")
        print(f"Model: {self.model}")
        print("Type 'exit' to quit, 'help' for commands")
        print("="*50 + "\n")
        
        while True:
            try:
                user_input = input("openclaw> ").strip()
                
                if not user_input:
                    continue
                elif user_input.lower() == 'exit':
                    print("Goodbye.")
                    break
                elif user_input.lower() == 'help':
                    print("""
Commands:
  analyze <target>  - Analyze a target
  payload <type>    - Generate payload
  chat <message>    - Free chat with AI
  status            - Check backend status
  exit              - Quit
                    """)
                elif user_input.lower().startswith('analyze '):
                    target = user_input[8:]
                    print(f"\n[*] Analyzing: {target}\n")
                    print(self.analyze_target(target))
                elif user_input.lower().startswith('payload '):
                    ptype = user_input[8:]
                    print(f"\n[*] Generating {ptype} payload\n")
                    print(self.generate_payload(ptype, "multi-platform"))
                elif user_input.lower() == 'status':
                    try:
                        r = requests.get(f"{self.lilith_url}/status", timeout=5)
                        print(f"LILITH Backend: {r.json()}")
                    except:
                        print("LILITH Backend: OFFLINE (using direct OpenRouter)")
                else:
                    # Treat as chat
                    print(f"\n{self.query_lilith(user_input)}\n")
                    
            except KeyboardInterrupt:
                print("\nInterrupted. Type 'exit' to quit.")
            except Exception as e:
                print(f"Error: {e}")


def main():
    bridge = LILITHOpenClawBridge()
    bridge.cli_chat()


if __name__ == "__main__":
    main()
'@

$BridgePath = Join-Path $OpenClawDir "lilith_bridge.py"
Set-Content -Path $BridgePath -Value $BridgeScript -Encoding UTF8
Write-Host "    Created: $BridgePath" -ForegroundColor Green

# Step 3: Install required packages
Write-Host "`n[3] Installing dependencies..." -ForegroundColor Yellow
& $VenvPython -m pip install requests --quiet 2>&1 | Out-Null
Write-Host "    Dependencies installed" -ForegroundColor Green

# Step 4: Create launcher script
Write-Host "`n[4] Creating launcher..." -ForegroundColor Yellow

$LauncherScript = @"
@echo off
cd /d "$WorkspaceRoot"
call .venv\Scripts\activate.bat
python openclaw\lilith_bridge.py %*
"@

$LauncherPath = Join-Path $WorkspaceRoot "openclaw.bat"
Set-Content -Path $LauncherPath -Value $LauncherScript -Encoding ASCII
Write-Host "    Created: $LauncherPath" -ForegroundColor Green

# Step 5: Verify config
Write-Host "`n[5] Verifying configuration..." -ForegroundColor Yellow
$ConfigPath = Join-Path $WorkspaceRoot "config\lucifera.conf"
$ConfigContent = Get-Content $ConfigPath -Raw

if ($ConfigContent -match "host\s*=\s*openrouter") {
    Write-Host "    [OK] Host set to OpenRouter" -ForegroundColor Green
} else {
    Write-Host "    [!] Host not set to openrouter in config" -ForegroundColor Yellow
}

if ($ConfigContent -match "model\s*=\s*([^\r\n]+)") {
    $model = $Matches[1]
    Write-Host "    [OK] Model: $model" -ForegroundColor Green
} 

Write-Host "`n===============================================" -ForegroundColor Cyan
Write-Host " OpenClaw Setup Complete!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "`nUsage:" -ForegroundColor Yellow
Write-Host "  .\openclaw.bat              - Start interactive CLI" -ForegroundColor Gray
Write-Host "  .\.venv\Scripts\python.exe openclaw\lilith_bridge.py" -ForegroundColor Gray
Write-Host "`nConfiguration:" -ForegroundColor Yellow
Write-Host "  Config: config\lucifera.conf" -ForegroundColor Gray
Write-Host "  Model: OpenRouter free models (no API key needed)" -ForegroundColor Gray
Write-Host "  API: https://openrouter.ai/api/v1" -ForegroundColor Gray
Write-Host "`nFree models available (no key required):" -ForegroundColor Yellow
Write-Host "  - qwen/qwen3-coder:free" -ForegroundColor Gray
Write-Host "  - arcee-ai/trinity-large-preview:free" -ForegroundColor Gray
Write-Host "  - liquid/lfm-2.5-1.2b-instruct:free" -ForegroundColor Gray
