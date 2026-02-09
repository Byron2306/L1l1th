#!/usr/bin/env python3
"""
LEAKED KEY DATABASE & CREDENTIAL STUFFING
==========================================
Database of leaked/exposed API key patterns, common mutations,
and credential stuffing techniques for key discovery.
"""

import secrets
import string
import hashlib
import re
import itertools
from typing import Dict, List, Generator, Optional
from datetime import datetime
import random


class LeakedKeyDatabase:
    """
    Database of leaked/exposed API key patterns and common formats.
    Includes real patterns found in GitHub leaks, paste sites, etc.
    """
    
    # Common leaked key prefixes found in the wild
    LEAKED_PREFIXES = {
        'openai': [
            'sk-proj-', 'sk-None', 'sk-svcacct-', 'sk-admin-',
            'sk-test-', 'sk-live-', 'sk-org-', 'sk-user-'
        ],
        'anthropic': [
            'sk-ant-api01-', 'sk-ant-api02-', 'sk-ant-api03-',
            'sk-ant-sid01-', 'sk-ant-admin-'
        ],
        'groq': ['gsk_test_', 'gsk_live_', 'gsk_prod_', 'gsk_dev_'],
        'huggingface': ['hf_test_', 'hf_api_', 'hf_read_', 'hf_write_'],
        'google': ['AIzaSyA', 'AIzaSyB', 'AIzaSyC', 'AIzaSyD', 'AIzaSyE'],
        'aws': ['AKIA', 'ASIA', 'AROA', 'AIDA', 'ANPA', 'ANVA'],
        'stripe': ['sk_test_', 'sk_live_', 'pk_test_', 'pk_live_', 'rk_test_', 'rk_live_'],
    }
    
    # Common patterns found in leaked keys
    COMMON_PATTERNS = {
        'openai': [
            # Patterns from GitHub leaks
            'sk-{word}{digits}{random}',
            'sk-proj-{random48}',
            'sk-{company}{random}',
        ],
        'anthropic': [
            'sk-ant-api03-{random}',
            'sk-ant-{word}-{random}',
        ],
        'groq': [
            'gsk_{word}{digits}{random}',
        ]
    }
    
    # Words commonly found in leaked keys
    COMMON_WORDS = [
        'test', 'dev', 'prod', 'live', 'demo', 'sample', 'example',
        'admin', 'user', 'api', 'key', 'secret', 'token', 'auth',
        'project', 'app', 'service', 'backend', 'frontend', 'client',
        'internal', 'external', 'public', 'private', 'staging', 'beta',
        'alpha', 'v1', 'v2', 'v3', 'main', 'master', 'default'
    ]
    
    # Common number patterns in leaked keys
    COMMON_NUMBERS = [
        '123', '1234', '12345', '123456', '0000', '1111', '2222',
        '2023', '2024', '2025', '001', '002', '100', '200', '999'
    ]
    
    # Actual leaked key samples (redacted/modified for safety but pattern-accurate)
    # These represent PATTERNS found in real leaks, not actual working keys
    LEAKED_KEY_PATTERNS = {
        'openai': [
            # Format: prefix + base64-like string
            lambda: f"sk-{''.join(random.choices(string.ascii_letters + string.digits, k=48))}",
            lambda: f"sk-proj-{''.join(random.choices(string.ascii_letters + string.digits + '-_', k=44))}",
            lambda: f"sk-{random.choice(['test', 'dev', 'prod'])}-{''.join(random.choices(string.ascii_letters + string.digits, k=44))}",
            # Common GitHub leak patterns
            lambda: f"sk-{''.join(random.choices('abcdefABCDEF0123456789', k=48))}",
        ],
        'anthropic': [
            lambda: f"sk-ant-api03-{''.join(random.choices(string.ascii_letters + string.digits + '-_', k=89))}",
            lambda: f"sk-ant-sid01-{''.join(random.choices(string.ascii_letters + string.digits, k=85))}",
        ],
        'groq': [
            lambda: f"gsk_{''.join(random.choices(string.ascii_letters + string.digits, k=52))}",
            lambda: f"gsk_{random.choice(COMMON_WORDS)}{''.join(random.choices(string.ascii_letters + string.digits, k=48))}",
        ],
        'huggingface': [
            lambda: f"hf_{''.join(random.choices(string.ascii_letters + string.digits, k=34))}",
            lambda: f"hf_{random.choice(['read', 'write', 'api'])}{''.join(random.choices(string.ascii_letters + string.digits, k=30))}",
        ],
        'google': [
            lambda: f"AIzaSy{''.join(random.choices(string.ascii_letters + string.digits + '-_', k=33))}",
        ],
        'together': [
            lambda: ''.join(random.choices('0123456789abcdef', k=64)),
        ],
        'mistral': [
            lambda: ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
        ],
        'openrouter': [
            lambda: f"sk-or-v1-{''.join(random.choices('0123456789abcdef', k=64))}",
        ],
        'cerebras': [
            lambda: f"csk-{''.join(random.choices(string.ascii_letters + string.digits, k=48))}",
        ],
        'deepinfra': [
            lambda: ''.join(random.choices(string.ascii_letters + string.digits, k=40)),
        ],
        'fireworks': [
            lambda: f"fw_{''.join(random.choices(string.ascii_letters + string.digits, k=43))}",
        ],
        'cohere': [
            lambda: ''.join(random.choices(string.ascii_letters + string.digits, k=40)),
        ],
        'replicate': [
            lambda: f"r8_{''.join(random.choices(string.ascii_letters + string.digits, k=37))}",
        ],
        'perplexity': [
            lambda: f"pplx-{''.join(random.choices('0123456789abcdef', k=48))}",
        ],
        'deepseek': [
            lambda: f"sk-{''.join(random.choices('0123456789abcdef', k=32))}",
        ],
    }
    
    def __init__(self):
        self.generated_count = 0
        self.pattern_index = {}
    
    def generate_leaked_pattern_key(self, provider: str) -> str:
        """Generate a key based on leaked patterns"""
        provider = provider.lower()
        
        if provider in self.LEAKED_KEY_PATTERNS:
            pattern_func = random.choice(self.LEAKED_KEY_PATTERNS[provider])
            key = pattern_func()
            self.generated_count += 1
            return key
        
        # Fallback to generic
        return ''.join(random.choices(string.ascii_letters + string.digits, k=40))
    
    def generate_batch(self, provider: str, count: int = 10) -> List[str]:
        """Generate batch of keys using leaked patterns"""
        return [self.generate_leaked_pattern_key(provider) for _ in range(count)]


class CredentialStuffer:
    """
    Credential stuffing engine that generates keys using:
    - Common patterns from breaches
    - Character mutations
    - Dictionary-based generation
    - Entropy analysis
    """
    
    # Character substitutions (leet speak, typos, etc.)
    CHAR_SUBS = {
        'a': ['@', '4', 'A'],
        'e': ['3', 'E'],
        'i': ['1', '!', 'I'],
        'o': ['0', 'O'],
        's': ['$', '5', 'S'],
        't': ['7', '+', 'T'],
        'l': ['1', 'L', '|'],
        'g': ['9', 'G'],
        'b': ['8', 'B'],
    }
    
    # Common base strings found in leaked keys
    COMMON_BASES = [
        'testkey', 'apikey', 'secretkey', 'myapikey', 'devkey',
        'prodkey', 'livekey', 'demokey', 'samplekey', 'defaultkey',
        'adminkey', 'userkey', 'clientkey', 'serverkey', 'backendkey',
        'projectkey', 'appkey', 'servicekey', 'tokenkey', 'authkey'
    ]
    
    # Sequential patterns
    SEQUENTIAL_PATTERNS = [
        'abcdef', 'qwerty', 'asdfgh', 'zxcvbn', '123456', '000000',
        'aaaaaa', 'abcabc', '121212', '111111', '112233', '123123'
    ]
    
    def __init__(self):
        self.mutation_cache = {}
    
    def mutate_string(self, base: str, mutations: int = 3) -> Generator[str, None, None]:
        """Generate mutations of a base string"""
        yield base
        yield base.upper()
        yield base.lower()
        yield base.capitalize()
        
        # Character substitutions
        for _ in range(mutations):
            mutated = list(base)
            for i, char in enumerate(mutated):
                if char.lower() in self.CHAR_SUBS and random.random() > 0.5:
                    mutated[i] = random.choice(self.CHAR_SUBS[char.lower()])
            yield ''.join(mutated)
        
        # Add numbers
        for num in ['1', '12', '123', '1234', '01', '00', '99']:
            yield base + num
            yield num + base
        
        # Add special chars
        for special in ['!', '@', '#', '_', '-']:
            yield base + special
            yield special + base
    
    def generate_dictionary_keys(self, provider: str, count: int = 20) -> List[str]:
        """Generate keys using dictionary-based approach"""
        keys = []
        
        # Get provider-specific prefix
        prefix_map = {
            'openai': 'sk-',
            'anthropic': 'sk-ant-api03-',
            'groq': 'gsk_',
            'huggingface': 'hf_',
            'google': 'AIzaSy',
            'openrouter': 'sk-or-v1-',
            'cerebras': 'csk-',
            'fireworks': 'fw_',
            'replicate': 'r8_',
            'perplexity': 'pplx-',
        }
        
        prefix = prefix_map.get(provider.lower(), '')
        
        # Generate using common bases + mutations
        for base in random.sample(self.COMMON_BASES, min(5, len(self.COMMON_BASES))):
            for mutation in self.mutate_string(base, mutations=2):
                # Pad to appropriate length
                key_body = mutation
                target_len = self._get_target_length(provider) - len(prefix)
                
                if len(key_body) < target_len:
                    key_body += ''.join(random.choices(string.ascii_letters + string.digits, k=target_len - len(key_body)))
                else:
                    key_body = key_body[:target_len]
                
                keys.append(prefix + key_body)
                
                if len(keys) >= count:
                    return keys
        
        return keys
    
    def generate_sequential_keys(self, provider: str, count: int = 10) -> List[str]:
        """Generate keys with sequential patterns (often found in test keys)"""
        keys = []
        
        prefix_map = {
            'openai': 'sk-',
            'anthropic': 'sk-ant-api03-',
            'groq': 'gsk_',
            'huggingface': 'hf_',
        }
        
        prefix = prefix_map.get(provider.lower(), '')
        target_len = self._get_target_length(provider) - len(prefix)
        
        for pattern in self.SEQUENTIAL_PATTERNS:
            # Repeat pattern to fill length
            repeated = (pattern * (target_len // len(pattern) + 1))[:target_len]
            keys.append(prefix + repeated)
            
            # Mix with random
            mixed = repeated[:target_len//2] + ''.join(random.choices(string.ascii_letters + string.digits, k=target_len//2))
            keys.append(prefix + mixed)
            
            if len(keys) >= count:
                break
        
        return keys[:count]
    
    def generate_bruteforce_keys(self, provider: str, 
                                  charset: str = None,
                                  count: int = 50) -> List[str]:
        """Generate keys using bruteforce patterns"""
        keys = []
        
        prefix_map = {
            'openai': 'sk-',
            'anthropic': 'sk-ant-api03-',
            'groq': 'gsk_',
            'huggingface': 'hf_',
            'google': 'AIzaSy',
            'together': '',
            'mistral': '',
            'openrouter': 'sk-or-v1-',
            'cerebras': 'csk-',
            'deepinfra': '',
            'fireworks': 'fw_',
            'cohere': '',
            'replicate': 'r8_',
            'perplexity': 'pplx-',
            'deepseek': 'sk-',
        }
        
        prefix = prefix_map.get(provider.lower(), '')
        target_len = self._get_target_length(provider) - len(prefix)
        
        if charset is None:
            # Use provider-appropriate charset
            if provider.lower() in ['together', 'perplexity', 'deepseek', 'openrouter']:
                charset = '0123456789abcdef'
            else:
                charset = string.ascii_letters + string.digits
        
        for _ in range(count):
            key_body = ''.join(random.choices(charset, k=target_len))
            keys.append(prefix + key_body)
        
        return keys
    
    def _get_target_length(self, provider: str) -> int:
        """Get target key length for provider"""
        lengths = {
            'openai': 51,
            'anthropic': 108,
            'groq': 56,
            'huggingface': 37,
            'together': 64,
            'mistral': 32,
            'openrouter': 73,
            'cerebras': 52,
            'deepinfra': 40,
            'fireworks': 46,
            'cohere': 40,
            'replicate': 40,
            'perplexity': 53,
            'deepseek': 35,
            'google': 39,
        }
        return lengths.get(provider.lower(), 40)
    
    def stuff_credentials(self, provider: str, count: int = 100) -> List[str]:
        """
        Main credential stuffing function.
        Combines multiple techniques for maximum coverage.
        """
        keys = []
        
        # 30% from dictionary
        keys.extend(self.generate_dictionary_keys(provider, count // 3))
        
        # 20% from sequential patterns
        keys.extend(self.generate_sequential_keys(provider, count // 5))
        
        # 50% from bruteforce
        keys.extend(self.generate_bruteforce_keys(provider, count=count // 2))
        
        # Shuffle and return
        random.shuffle(keys)
        return keys[:count]


class RateLimitManager:
    """
    Manages rate limiting detection and adaptive delays.
    Tracks response patterns and adjusts timing accordingly.
    """
    
    def __init__(self):
        # Provider rate limit tracking
        self.rate_limits = {}  # provider -> {last_request, delay, consecutive_429s, blocked_until}
        
        # Default delays (seconds)
        self.default_delay = 0.5
        self.min_delay = 0.1
        self.max_delay = 60.0
        
        # Backoff multiplier
        self.backoff_multiplier = 2.0
        
        # Rate limit indicators
        self.rate_limit_codes = [429, 503, 529]
        self.rate_limit_headers = ['retry-after', 'x-ratelimit-remaining', 'x-ratelimit-reset']
    
    def init_provider(self, provider: str):
        """Initialize tracking for a provider"""
        if provider not in self.rate_limits:
            self.rate_limits[provider] = {
                'last_request': 0,
                'delay': self.default_delay,
                'consecutive_429s': 0,
                'blocked_until': 0,
                'total_requests': 0,
                'rate_limited_count': 0
            }
    
    def should_wait(self, provider: str) -> tuple:
        """
        Check if we should wait before making a request.
        Returns (should_wait: bool, wait_time: float)
        """
        self.init_provider(provider)
        state = self.rate_limits[provider]
        
        now = datetime.utcnow().timestamp()
        
        # Check if blocked
        if state['blocked_until'] > now:
            return True, state['blocked_until'] - now
        
        # Check minimum delay
        time_since_last = now - state['last_request']
        if time_since_last < state['delay']:
            return True, state['delay'] - time_since_last
        
        return False, 0
    
    def get_delay(self, provider: str) -> float:
        """Get current delay for provider"""
        self.init_provider(provider)
        return self.rate_limits[provider]['delay']
    
    def record_request(self, provider: str):
        """Record that a request was made"""
        self.init_provider(provider)
        self.rate_limits[provider]['last_request'] = datetime.utcnow().timestamp()
        self.rate_limits[provider]['total_requests'] += 1
    
    def handle_response(self, provider: str, status_code: int, 
                        headers: dict = None) -> dict:
        """
        Handle response and adjust rate limiting accordingly.
        Returns adjustment info.
        """
        self.init_provider(provider)
        state = self.rate_limits[provider]
        headers = headers or {}
        
        result = {
            'rate_limited': False,
            'new_delay': state['delay'],
            'blocked_until': None,
            'action': 'continue'
        }
        
        # Check for rate limiting
        if status_code in self.rate_limit_codes:
            state['consecutive_429s'] += 1
            state['rate_limited_count'] += 1
            result['rate_limited'] = True
            
            # Check for Retry-After header
            retry_after = headers.get('retry-after') or headers.get('Retry-After')
            if retry_after:
                try:
                    wait_time = int(retry_after)
                    state['blocked_until'] = datetime.utcnow().timestamp() + wait_time
                    result['blocked_until'] = wait_time
                    result['action'] = 'wait'
                except ValueError:
                    pass
            
            # Exponential backoff
            new_delay = min(
                state['delay'] * (self.backoff_multiplier ** state['consecutive_429s']),
                self.max_delay
            )
            state['delay'] = new_delay
            result['new_delay'] = new_delay
            
            # If too many consecutive 429s, block for longer
            if state['consecutive_429s'] >= 5:
                state['blocked_until'] = datetime.utcnow().timestamp() + 300  # 5 min block
                result['action'] = 'blocked'
                result['blocked_until'] = 300
        
        else:
            # Success or non-rate-limit error
            state['consecutive_429s'] = 0
            
            # Gradually reduce delay on success
            if status_code in [200, 401, 403]:  # Valid responses
                new_delay = max(
                    state['delay'] * 0.9,
                    self.min_delay
                )
                state['delay'] = new_delay
                result['new_delay'] = new_delay
        
        return result
    
    def get_stats(self, provider: str = None) -> dict:
        """Get rate limiting stats"""
        if provider:
            self.init_provider(provider)
            return self.rate_limits[provider].copy()
        return {k: v.copy() for k, v in self.rate_limits.items()}
    
    def reset_provider(self, provider: str):
        """Reset rate limiting for a provider"""
        if provider in self.rate_limits:
            self.rate_limits[provider] = {
                'last_request': 0,
                'delay': self.default_delay,
                'consecutive_429s': 0,
                'blocked_until': 0,
                'total_requests': 0,
                'rate_limited_count': 0
            }
    
    def reset_all(self):
        """Reset all rate limiting"""
        self.rate_limits = {}


# Global instances
COMMON_WORDS = LeakedKeyDatabase.COMMON_WORDS

_leaked_db = None
_credential_stuffer = None
_rate_limit_manager = None

def get_leaked_db() -> LeakedKeyDatabase:
    global _leaked_db
    if _leaked_db is None:
        _leaked_db = LeakedKeyDatabase()
    return _leaked_db

def get_credential_stuffer() -> CredentialStuffer:
    global _credential_stuffer
    if _credential_stuffer is None:
        _credential_stuffer = CredentialStuffer()
    return _credential_stuffer

def get_rate_limit_manager() -> RateLimitManager:
    global _rate_limit_manager
    if _rate_limit_manager is None:
        _rate_limit_manager = RateLimitManager()
    return _rate_limit_manager


if __name__ == '__main__':
    # Test
    db = LeakedKeyDatabase()
    stuffer = CredentialStuffer()
    
    print("=== LEAKED KEY DATABASE TEST ===")
    for provider in ['openai', 'groq', 'anthropic']:
        keys = db.generate_batch(provider, 3)
        print(f"\n{provider.upper()}:")
        for k in keys:
            print(f"  {k[:50]}...")
    
    print("\n=== CREDENTIAL STUFFING TEST ===")
    keys = stuffer.stuff_credentials('openai', 10)
    print("OpenAI stuffed keys:")
    for k in keys[:5]:
        print(f"  {k[:50]}...")
