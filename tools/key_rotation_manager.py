#!/usr/bin/env python3
"""
API KEY ROTATION & TESTING SYSTEM
==================================
Auto-generates, tests, and rotates API keys until finding working ones.
Supports multiple providers with real API validation.
"""

import os
import json
import time
import asyncio
import threading
import requests
from datetime import datetime
from typing import Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import secrets
import string


class APIKeyTester:
    """Tests API keys against real provider endpoints"""
    
    # Provider test configurations
    PROVIDER_TESTS = {
        'openai': {
            'url': 'https://api.openai.com/v1/models',
            'method': 'GET',
            'headers': lambda key: {'Authorization': f'Bearer {key}'},
            'success_codes': [200],
            'error_indicators': ['invalid_api_key', 'Incorrect API key']
        },
        'anthropic': {
            'url': 'https://api.anthropic.com/v1/messages',
            'method': 'POST',
            'headers': lambda key: {
                'x-api-key': key,
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json'
            },
            'body': {'model': 'claude-3-haiku-20240307', 'max_tokens': 1, 'messages': [{'role': 'user', 'content': 'hi'}]},
            'success_codes': [200, 400],  # 400 with valid key format but may have quota issues
            'error_indicators': ['invalid_api_key', 'invalid x-api-key']
        },
        'groq': {
            'url': 'https://api.groq.com/openai/v1/models',
            'method': 'GET',
            'headers': lambda key: {'Authorization': f'Bearer {key}'},
            'success_codes': [200],
            'error_indicators': ['invalid_api_key', 'Invalid API Key']
        },
        'huggingface': {
            'url': 'https://huggingface.co/api/whoami-v2',
            'method': 'GET',
            'headers': lambda key: {'Authorization': f'Bearer {key}'},
            'success_codes': [200],
            'error_indicators': ['Invalid credentials', 'Unauthorized']
        },
        'together': {
            'url': 'https://api.together.xyz/v1/models',
            'method': 'GET',
            'headers': lambda key: {'Authorization': f'Bearer {key}'},
            'success_codes': [200],
            'error_indicators': ['invalid_api_key', 'Unauthorized']
        },
        'mistral': {
            'url': 'https://api.mistral.ai/v1/models',
            'method': 'GET',
            'headers': lambda key: {'Authorization': f'Bearer {key}'},
            'success_codes': [200],
            'error_indicators': ['Unauthorized', 'invalid']
        },
        'openrouter': {
            'url': 'https://openrouter.ai/api/v1/models',
            'method': 'GET',
            'headers': lambda key: {'Authorization': f'Bearer {key}'},
            'success_codes': [200],
            'error_indicators': ['invalid_api_key', 'Unauthorized']
        },
        'cerebras': {
            'url': 'https://api.cerebras.ai/v1/models',
            'method': 'GET',
            'headers': lambda key: {'Authorization': f'Bearer {key}'},
            'success_codes': [200],
            'error_indicators': ['invalid', 'Unauthorized']
        },
        'deepinfra': {
            'url': 'https://api.deepinfra.com/v1/openai/models',
            'method': 'GET',
            'headers': lambda key: {'Authorization': f'Bearer {key}'},
            'success_codes': [200],
            'error_indicators': ['invalid', 'Unauthorized']
        },
        'fireworks': {
            'url': 'https://api.fireworks.ai/inference/v1/models',
            'method': 'GET',
            'headers': lambda key: {'Authorization': f'Bearer {key}'},
            'success_codes': [200],
            'error_indicators': ['invalid', 'Unauthorized']
        },
        'cohere': {
            'url': 'https://api.cohere.ai/v1/models',
            'method': 'GET',
            'headers': lambda key: {'Authorization': f'Bearer {key}'},
            'success_codes': [200],
            'error_indicators': ['invalid api token', 'Unauthorized']
        },
        'replicate': {
            'url': 'https://api.replicate.com/v1/models',
            'method': 'GET',
            'headers': lambda key: {'Authorization': f'Token {key}'},
            'success_codes': [200],
            'error_indicators': ['Invalid token', 'Unauthorized']
        },
        'perplexity': {
            'url': 'https://api.perplexity.ai/chat/completions',
            'method': 'POST',
            'headers': lambda key: {
                'Authorization': f'Bearer {key}',
                'Content-Type': 'application/json'
            },
            'body': {'model': 'llama-3.1-sonar-small-128k-online', 'messages': [{'role': 'user', 'content': 'hi'}]},
            'success_codes': [200, 400],
            'error_indicators': ['invalid_api_key', 'Unauthorized']
        },
        'deepseek': {
            'url': 'https://api.deepseek.com/v1/models',
            'method': 'GET',
            'headers': lambda key: {'Authorization': f'Bearer {key}'},
            'success_codes': [200],
            'error_indicators': ['invalid', 'Unauthorized']
        },
        'google': {
            'url': 'https://generativelanguage.googleapis.com/v1/models',
            'method': 'GET',
            'headers': lambda key: {},
            'params': lambda key: {'key': key},
            'success_codes': [200],
            'error_indicators': ['API_KEY_INVALID', 'invalid']
        }
    }
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def test_key(self, key: str, provider: str) -> Dict:
        """
        Test a single API key against provider's endpoint.
        
        Returns:
            Dict with test results
        """
        provider = provider.lower()
        
        if provider not in self.PROVIDER_TESTS:
            return {
                'valid': False,
                'error': f'No test available for provider: {provider}',
                'provider': provider,
                'key': key[:20] + '...'
            }
        
        config = self.PROVIDER_TESTS[provider]
        
        try:
            headers = config['headers'](key)
            url = config['url']
            method = config['method']
            
            # Build request kwargs
            kwargs = {
                'headers': headers,
                'timeout': self.timeout
            }
            
            if 'params' in config:
                kwargs['params'] = config['params'](key)
            
            if method == 'POST' and 'body' in config:
                kwargs['json'] = config['body']
            
            # Make request
            if method == 'GET':
                response = self.session.get(url, **kwargs)
            else:
                response = self.session.post(url, **kwargs)
            
            # Check response
            is_valid = response.status_code in config['success_codes']
            
            # Check for error indicators in response
            response_text = response.text.lower()
            for indicator in config.get('error_indicators', []):
                if indicator.lower() in response_text:
                    is_valid = False
                    break
            
            return {
                'valid': is_valid,
                'status_code': response.status_code,
                'provider': provider,
                'key': key[:20] + '...',
                'full_key': key if is_valid else None,
                'response_preview': response.text[:200] if not is_valid else 'Valid key!',
                'tested_at': datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.Timeout:
            return {
                'valid': False,
                'error': 'Request timeout',
                'provider': provider,
                'key': key[:20] + '...'
            }
        except requests.exceptions.RequestException as e:
            return {
                'valid': False,
                'error': str(e)[:100],
                'provider': provider,
                'key': key[:20] + '...'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)[:100],
                'provider': provider,
                'key': key[:20] + '...'
            }


class KeyRotationManager:
    """
    Manages automatic key generation, testing, and rotation.
    Keeps trying until finding working keys.
    """
    
    # Key format configurations (same as APIKeyGenerator)
    KEY_FORMATS = {
        'openai': {'prefix': 'sk-', 'length': 51, 'charset': string.ascii_letters + string.digits},
        'anthropic': {'prefix': 'sk-ant-api03-', 'length': 108, 'charset': string.ascii_letters + string.digits + '-_'},
        'groq': {'prefix': 'gsk_', 'length': 56, 'charset': string.ascii_letters + string.digits},
        'huggingface': {'prefix': 'hf_', 'length': 37, 'charset': string.ascii_letters + string.digits},
        'together': {'prefix': '', 'length': 64, 'charset': string.hexdigits.lower()[:16]},
        'mistral': {'prefix': '', 'length': 32, 'charset': string.ascii_letters + string.digits},
        'openrouter': {'prefix': 'sk-or-v1-', 'length': 73, 'charset': string.hexdigits.lower()[:16]},
        'cerebras': {'prefix': 'csk-', 'length': 52, 'charset': string.ascii_letters + string.digits},
        'deepinfra': {'prefix': '', 'length': 40, 'charset': string.ascii_letters + string.digits},
        'fireworks': {'prefix': 'fw_', 'length': 46, 'charset': string.ascii_letters + string.digits},
        'cohere': {'prefix': '', 'length': 40, 'charset': string.ascii_letters + string.digits},
        'replicate': {'prefix': 'r8_', 'length': 40, 'charset': string.ascii_letters + string.digits},
        'perplexity': {'prefix': 'pplx-', 'length': 53, 'charset': string.hexdigits.lower()[:16]},
        'deepseek': {'prefix': 'sk-', 'length': 35, 'charset': string.hexdigits.lower()[:16]},
        'google': {'prefix': 'AIza', 'length': 39, 'charset': string.ascii_letters + string.digits + '-_'},
    }
    
    def __init__(self):
        self.tester = APIKeyTester()
        self.running = False
        self.paused = False
        self.thread = None
        
        # Statistics
        self.stats = {
            'total_generated': 0,
            'total_tested': 0,
            'valid_keys_found': 0,
            'by_provider': {},
            'start_time': None,
            'last_update': None
        }
        
        # Results storage
        self.valid_keys = {}  # provider -> list of valid keys
        self.tested_keys = []  # history of tested keys
        self.logs = []  # activity logs
        
        # Configuration
        self.target_providers = list(self.KEY_FORMATS.keys())
        self.keys_per_batch = 5
        self.delay_between_tests = 0.5  # seconds
        self.max_keys_per_provider = 3
        
        # Callbacks
        self.on_valid_key = None
        self.on_log = None
        self.on_status_change = None
    
    def _generate_key(self, provider: str) -> str:
        """Generate a single key for provider"""
        if provider not in self.KEY_FORMATS:
            provider = 'openai'
        
        config = self.KEY_FORMATS[provider]
        prefix = config['prefix']
        length = config['length']
        charset = config['charset']
        
        random_part = ''.join(secrets.choice(charset) for _ in range(length - len(prefix)))
        return prefix + random_part
    
    def _add_log(self, message: str, level: str = 'info'):
        """Add log entry"""
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message
        }
        self.logs.append(entry)
        
        # Keep only last 500 logs
        if len(self.logs) > 500:
            self.logs = self.logs[-500:]
        
        if self.on_log:
            self.on_log(entry)
    
    def _rotation_loop(self):
        """Main rotation loop - runs in background thread"""
        self._add_log('🚀 Key rotation started', 'info')
        self.stats['start_time'] = datetime.utcnow().isoformat()
        
        while self.running:
            if self.paused:
                time.sleep(1)
                continue
            
            # Check if we've found enough keys for all providers
            all_satisfied = all(
                len(self.valid_keys.get(p, [])) >= self.max_keys_per_provider
                for p in self.target_providers
            )
            
            if all_satisfied:
                self._add_log('✅ Found working keys for all providers!', 'success')
                self.running = False
                break
            
            # Generate and test keys for each provider that needs them
            for provider in self.target_providers:
                if not self.running:
                    break
                
                # Skip if we have enough for this provider
                if len(self.valid_keys.get(provider, [])) >= self.max_keys_per_provider:
                    continue
                
                # Generate batch of keys
                keys = [self._generate_key(provider) for _ in range(self.keys_per_batch)]
                self.stats['total_generated'] += len(keys)
                
                self._add_log(f'🔄 Testing {len(keys)} keys for {provider.upper()}...', 'info')
                
                # Test each key
                for key in keys:
                    if not self.running or self.paused:
                        break
                    
                    result = self.tester.test_key(key, provider)
                    self.stats['total_tested'] += 1
                    self.stats['last_update'] = datetime.utcnow().isoformat()
                    
                    # Update provider stats
                    if provider not in self.stats['by_provider']:
                        self.stats['by_provider'][provider] = {'tested': 0, 'valid': 0}
                    self.stats['by_provider'][provider]['tested'] += 1
                    
                    # Store result
                    self.tested_keys.append(result)
                    if len(self.tested_keys) > 1000:
                        self.tested_keys = self.tested_keys[-1000:]
                    
                    if result.get('valid'):
                        # Found a valid key!
                        self.stats['valid_keys_found'] += 1
                        self.stats['by_provider'][provider]['valid'] += 1
                        
                        if provider not in self.valid_keys:
                            self.valid_keys[provider] = []
                        self.valid_keys[provider].append({
                            'key': result.get('full_key', key),
                            'found_at': datetime.utcnow().isoformat()
                        })
                        
                        self._add_log(f'🎉 VALID KEY FOUND for {provider.upper()}!', 'success')
                        
                        if self.on_valid_key:
                            self.on_valid_key(provider, result.get('full_key', key))
                        
                        # Check if we now have enough
                        if len(self.valid_keys[provider]) >= self.max_keys_per_provider:
                            self._add_log(f'✅ {provider.upper()}: Got {self.max_keys_per_provider} working keys', 'success')
                            break
                    
                    time.sleep(self.delay_between_tests)
            
            # Brief pause between provider cycles
            time.sleep(1)
        
        self._add_log('🛑 Key rotation stopped', 'info')
        if self.on_status_change:
            self.on_status_change('stopped')
    
    def start(self, providers: List[str] = None, 
              keys_per_batch: int = 5,
              max_per_provider: int = 3):
        """Start the rotation process"""
        if self.running:
            return {'success': False, 'error': 'Already running'}
        
        if providers:
            self.target_providers = [p for p in providers if p in self.KEY_FORMATS]
        else:
            self.target_providers = list(self.KEY_FORMATS.keys())
        
        self.keys_per_batch = keys_per_batch
        self.max_keys_per_provider = max_per_provider
        self.running = True
        self.paused = False
        
        # Reset stats
        self.stats = {
            'total_generated': 0,
            'total_tested': 0,
            'valid_keys_found': 0,
            'by_provider': {},
            'start_time': None,
            'last_update': None
        }
        self.valid_keys = {}
        self.tested_keys = []
        
        # Start background thread
        self.thread = threading.Thread(target=self._rotation_loop, daemon=True)
        self.thread.start()
        
        if self.on_status_change:
            self.on_status_change('running')
        
        return {
            'success': True,
            'message': 'Key rotation started',
            'providers': self.target_providers,
            'keys_per_batch': self.keys_per_batch,
            'max_per_provider': self.max_keys_per_provider
        }
    
    def stop(self):
        """Stop the rotation process"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        return {
            'success': True,
            'message': 'Key rotation stopped',
            'stats': self.stats,
            'valid_keys_found': len(self.valid_keys)
        }
    
    def pause(self):
        """Pause rotation"""
        self.paused = True
        self._add_log('⏸️ Key rotation paused', 'info')
        return {'success': True, 'message': 'Paused'}
    
    def resume(self):
        """Resume rotation"""
        self.paused = False
        self._add_log('▶️ Key rotation resumed', 'info')
        return {'success': True, 'message': 'Resumed'}
    
    def get_status(self) -> Dict:
        """Get current status"""
        return {
            'running': self.running,
            'paused': self.paused,
            'stats': self.stats,
            'valid_keys': {k: len(v) for k, v in self.valid_keys.items()},
            'target_providers': self.target_providers,
            'logs': self.logs[-20:]  # Last 20 logs
        }
    
    def get_valid_keys(self) -> Dict:
        """Get all valid keys found"""
        return {
            'success': True,
            'keys': self.valid_keys,
            'count': sum(len(v) for v in self.valid_keys.values())
        }
    
    def test_single_key(self, key: str, provider: str) -> Dict:
        """Test a single user-provided key"""
        result = self.tester.test_key(key, provider)
        
        if result.get('valid'):
            if provider not in self.valid_keys:
                self.valid_keys[provider] = []
            self.valid_keys[provider].append({
                'key': key,
                'found_at': datetime.utcnow().isoformat(),
                'source': 'manual'
            })
        
        return result
    
    def load_keys_to_session(self) -> Dict:
        """Load valid keys into the session/config"""
        loaded = {}
        config_path = '/app/config/harvested_keys.json'
        
        try:
            # Load existing keys
            existing = {}
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    existing = json.load(f)
            
            # Add new valid keys
            for provider, keys in self.valid_keys.items():
                if keys:
                    key_data = keys[0]  # Use first valid key
                    existing[provider] = {
                        'key': key_data['key'],
                        'source': 'rotation',
                        'added_at': datetime.utcnow().isoformat()
                    }
                    loaded[provider] = True
            
            # Save
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(existing, f, indent=2)
            
            return {
                'success': True,
                'loaded': loaded,
                'count': len(loaded)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
_rotation_manager = None

def get_rotation_manager() -> KeyRotationManager:
    """Get singleton rotation manager instance"""
    global _rotation_manager
    if _rotation_manager is None:
        _rotation_manager = KeyRotationManager()
    return _rotation_manager


if __name__ == '__main__':
    # Test
    manager = get_rotation_manager()
    
    print("Testing key rotation manager...")
    
    # Test single key validation
    tester = APIKeyTester()
    result = tester.test_key('sk-test123', 'openai')
    print(f"Test result: {result}")
