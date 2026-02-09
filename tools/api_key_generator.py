#!/usr/bin/env python3
"""
API Key Generator for LILITH
=============================
Generates and validates working API keys from various free providers.
This module helps LILITH find new working endpoints when existing ones fail.
"""

import requests
import json
import time
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class APIKeyGenerator:
    """
    Generates and validates API keys from various sources.
    """
    
    # Free API providers that don't require keys or have free tiers
    FREE_PROVIDERS = [
        {
            'name': 'Ollama (Local)',
            'type': 'local',
            'base_url': 'http://localhost:11434',
            'models': ['llama3.2:3b', 'mistral:7b', 'phi3:mini'],
            'requires_key': False,
            'instructions': 'Install Ollama: curl -fsSL https://ollama.com/install.sh | sh'
        },
        {
            'name': 'Together.ai Free Tier',
            'type': 'cloud',
            'base_url': 'https://api.together.xyz/v1',
            'models': ['meta-llama/Llama-3.2-3B-Instruct-Turbo', 'mistralai/Mixtral-8x7B-Instruct-v0.1'],
            'requires_key': True,
            'signup_url': 'https://api.together.xyz',
            'instructions': 'Sign up at https://api.together.xyz for $25 free credits'
        },
        {
            'name': 'Groq Free Tier',
            'type': 'cloud',
            'base_url': 'https://api.groq.com/openai/v1',
            'models': ['llama-3.3-70b-versatile', 'mixtral-8x7b-32768'],
            'requires_key': True,
            'signup_url': 'https://console.groq.com',
            'instructions': 'Sign up at https://console.groq.com for free API access'
        },
        {
            'name': 'HuggingFace Inference',
            'type': 'cloud',
            'base_url': 'https://router.huggingface.co/hf-inference/models',
            'models': ['meta-llama/Llama-3.2-3B-Instruct', 'mistralai/Mistral-7B-Instruct-v0.3'],
            'requires_key': True,
            'signup_url': 'https://huggingface.co/settings/tokens',
            'instructions': 'Create a free account at https://huggingface.co and generate a token'
        },
        {
            'name': 'OpenRouter Free Models',
            'type': 'cloud',
            'base_url': 'https://openrouter.ai/api/v1',
            'models': ['meta-llama/llama-3.2-3b-instruct:free', 'google/gemma-2-9b-it:free'],
            'requires_key': False,
            'instructions': 'Some models available without API key'
        }
    ]
    
    def __init__(self):
        self.working_keys = []
        self.tested_providers = []
    
    def test_ollama(self) -> Tuple[bool, str]:
        """Test if Ollama is running locally"""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    return True, f"✓ Ollama is running with {len(models)} models"
                else:
                    return False, "✗ Ollama is running but no models installed"
            return False, "✗ Ollama not responding"
        except Exception as e:
            return False, f"✗ Ollama not available: {str(e)}"
    
    def test_openrouter_free(self) -> Tuple[bool, str]:
        """Test OpenRouter free models (no key required)"""
        try:
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Content-Type': 'application/json',
                    'HTTP-Referer': 'https://luciferos.local',
                    'X-Title': 'LILITH'
                },
                json={
                    'model': 'meta-llama/llama-3.2-3b-instruct:free',
                    'messages': [{'role': 'user', 'content': 'test'}],
                    'max_tokens': 10
                },
                timeout=30
            )
            if response.status_code == 200:
                return True, "✓ OpenRouter free models working (no key needed)"
            return False, f"✗ OpenRouter returned {response.status_code}: {response.text[:100]}"
        except Exception as e:
            return False, f"✗ OpenRouter error: {str(e)}"
    
    def generate_instructions(self) -> str:
        """Generate instructions for getting working API keys"""
        instructions = """
╔════════════════════════════════════════════════════════════════╗
║           LILITH API Key Generation Guide                      ║
╚════════════════════════════════════════════════════════════════╝

IMMEDIATE OPTIONS (No API Key Required):
----------------------------------------

1. 🏠 OLLAMA (RECOMMENDED - Local, Free, No Restrictions)
   Installation:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull llama3.2:3b
   ```
   Then restart LILITH backend

2. 🌐 OpenRouter Free Models
   - No API key needed for free models
   - Limited rate limits
   - Works out of the box


FREE API KEY OPTIONS (Sign up required):
-----------------------------------------

3. ⚡ GROQ (FAST & FREE)
   - Sign up: https://console.groq.com
   - Get API key from dashboard
   - Free tier: Very fast, generous limits
   - Add to config: groq_api_key = YOUR_KEY

4. 🤗 HuggingFace (FREE)
   - Sign up: https://huggingface.co
   - Generate token: https://huggingface.co/settings/tokens
   - Free tier: Unlimited inference
   - Add to config: hf_token = YOUR_TOKEN

5. 🔥 Together.ai (FREE CREDITS)
   - Sign up: https://api.together.xyz
   - Get $25 free credits
   - Add to config: together_api_key = YOUR_KEY

6. 🧠 Venice.ai (FREE & UNCENSORED)
   - Sign up: https://venice.ai
   - Free tier available
   - No content restrictions


CONFIGURATION:
--------------
Add your keys to /app/config/lucifera.conf:

[lilith]
groq_api_key = YOUR_GROQ_KEY
hf_token = YOUR_HF_TOKEN
together_api_key = YOUR_TOGETHER_KEY
venice_api_key = YOUR_VENICE_KEY


TESTING:
--------
After adding keys, test with:
```bash
curl -X POST http://127.0.0.1:5000/chat \\
  -H "Content-Type: application/json" \\
  -d '{"message": "Hello LILITH"}'
```

"""
        return instructions
    
    def scan_working_providers(self) -> Dict:
        """Scan all providers and return status"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'working': [],
            'needs_key': [],
            'failed': []
        }
        
        print("\n🔍 Scanning for working AI providers...")
        print("=" * 60)
        
        # Test Ollama
        print("\nTesting Ollama (local)...")
        success, message = self.test_ollama()
        print(f"  {message}")
        if success:
            results['working'].append({
                'provider': 'Ollama',
                'type': 'local',
                'requires_key': False,
                'status': message
            })
        else:
            results['needs_key'].append({
                'provider': 'Ollama',
                'type': 'local',
                'requires_key': False,
                'status': message,
                'instructions': 'curl -fsSL https://ollama.com/install.sh | sh'
            })
        
        # Test OpenRouter free
        print("\nTesting OpenRouter free models...")
        success, message = self.test_openrouter_free()
        print(f"  {message}")
        if success:
            results['working'].append({
                'provider': 'OpenRouter',
                'type': 'cloud',
                'requires_key': False,
                'status': message
            })
        else:
            results['failed'].append({
                'provider': 'OpenRouter',
                'type': 'cloud',
                'status': message
            })
        
        # List providers that need keys
        for provider in self.FREE_PROVIDERS:
            if provider['requires_key'] and provider['name'] not in ['OpenRouter Free Models']:
                results['needs_key'].append({
                    'provider': provider['name'],
                    'type': provider['type'],
                    'requires_key': True,
                    'signup_url': provider.get('signup_url', ''),
                    'instructions': provider.get('instructions', '')
                })
        
        return results
    
    def save_results(self, results: Dict, filename: str = '/tmp/api_scan_results.json'):
        """Save scan results to file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Results saved to: {filename}")


def main():
    """Main function to run API key generator"""
    generator = APIKeyGenerator()
    
    print("""
╔════════════════════════════════════════════════════════════════╗
║         LILITH API Key Generator & Provider Scanner           ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Scan providers
    results = generator.scan_working_providers()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✓ Working providers (no key needed): {len(results['working'])}")
    print(f"🔑 Providers available (key required): {len(results['needs_key'])}")
    print(f"✗ Failed/unavailable: {len(results['failed'])}")
    
    # Print working providers
    if results['working']:
        print("\n✅ WORKING NOW:")
        for p in results['working']:
            print(f"  • {p['provider']}: {p['status']}")
    
    # Print instructions for getting keys
    print(generator.generate_instructions())
    
    # Save results
    generator.save_results(results)


if __name__ == '__main__':
    main()
