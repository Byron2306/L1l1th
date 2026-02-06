#!/bin/bash
# OpenClaw Integration for LuciferOS
# Configured to use OpenRouter free models (no API key required for free tier)

echo "[+] Installing OpenClaw..."
cd /opt
git clone https://github.com/openclaw/openclaw.git

cd openclaw
pip3 install -r requirements.txt

# Create wrapper for LILITH integration using OpenRouter
cat > /opt/openclaw/lilith_bridge.py << 'OPENCLAW_BRIDGE'
#!/usr/bin/env python3
import requests
import json
import configparser
from pathlib import Path

class LILITHOpenClawBridge:
    def __init__(self):
        # Load config from LuciferOS
        config = configparser.ConfigParser()
        config_path = Path(__file__).resolve().parents[1] / 'LuciferOS_FULL' / 'config' / 'lucifera.conf'
        if not config_path.exists():
            config_path = '/opt/lucifera/config/lucifera.conf'
        config.read(config_path)
        
        # OpenRouter configuration (free models, no key needed)
        self.api_url = config.get('lilith', 'api_url', fallback='https://openrouter.ai/api/v1')
        self.model = config.get('lilith', 'model', fallback='nousresearch/hermes-3-llama-3.1-405b:free')
        self.openrouter_key = config.get('lilith', 'openrouter_key', fallback='')
        
        # LILITH backend URL for integrated queries
        self.lilith_url = "http://127.0.0.1:5000"
    
    def query_openrouter(self, prompt):
        '''Query OpenRouter directly with free models'''
        headers = {
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/luciferOS",
            "X-Title": "LuciferOS-OpenClaw"
        }
        if self.openrouter_key:
            headers["Authorization"] = f"Bearer {self.openrouter_key}"
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024
        }
        
        response = requests.post(
            f"{self.api_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    def analyze_with_lilith(self, target, attack_type):
        '''Get LILITH's reasoning for attack strategy via backend'''
        prompt = f"Analyze {attack_type} attack against {target}. Provide OpenClaw payload recommendations."
        
        try:
            response = requests.post(
                f"{self.lilith_url}/chat",
                json={"message": prompt},
                timeout=120
            )
            if response.status_code == 200:
                return response.json()
            # Fallback to direct OpenRouter if LILITH backend unavailable
            return {"response": self.query_openrouter(prompt)}
        except requests.exceptions.ConnectionError:
            # LILITH backend not running, use OpenRouter directly
            return {"response": self.query_openrouter(prompt)}
    
    def execute_openclaw_payload(self, payload_config):
        '''Execute OpenClaw attack with LILITH's analysis'''
        # Placeholder for actual OpenClaw execution
        return {"status": "executed", "config": payload_config}

bridge = LILITHOpenClawBridge()
OPENCLAW_BRIDGE

chmod +x /opt/openclaw/lilith_bridge.py
echo "[+] OpenClaw integrated with LILITH using OpenRouter (free models)"
