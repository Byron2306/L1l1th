#!/usr/bin/env python3
"""
ROBUST API KEY GENERATOR
========================
Generates realistic API keys for various AI/ML providers.
Supports multiple formats, validation, and batch generation.
"""

import secrets
import string
import hashlib
import base64
import uuid
import time
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class APIKeyGenerator:
    """
    Robust API Key Generator for multiple providers.
    Generates keys that match the real format of each provider.
    """
    
    # Provider key formats and patterns
    PROVIDERS = {
        'openai': {
            'prefix': 'sk-',
            'length': 48,
            'charset': string.ascii_letters + string.digits,
            'pattern': r'^sk-[A-Za-z0-9]{48}$',
            'example': 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        },
        'anthropic': {
            'prefix': 'sk-ant-',
            'length': 95,
            'charset': string.ascii_letters + string.digits + '-_',
            'pattern': r'^sk-ant-[A-Za-z0-9\-_]{89}$',
            'example': 'sk-ant-api03-xxxxx...'
        },
        'groq': {
            'prefix': 'gsk_',
            'length': 52,
            'charset': string.ascii_letters + string.digits,
            'pattern': r'^gsk_[A-Za-z0-9]{52}$',
            'example': 'gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        },
        'huggingface': {
            'prefix': 'hf_',
            'length': 34,
            'charset': string.ascii_letters + string.digits,
            'pattern': r'^hf_[A-Za-z0-9]{34}$',
            'example': 'hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        },
        'together': {
            'prefix': '',
            'length': 64,
            'charset': string.hexdigits.lower(),
            'pattern': r'^[a-f0-9]{64}$',
            'example': '0123456789abcdef...'
        },
        'mistral': {
            'prefix': '',
            'length': 32,
            'charset': string.ascii_letters + string.digits,
            'pattern': r'^[A-Za-z0-9]{32}$',
            'example': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        },
        'openrouter': {
            'prefix': 'sk-or-v1-',
            'length': 64,
            'charset': string.hexdigits.lower(),
            'pattern': r'^sk-or-v1-[a-f0-9]{64}$',
            'example': 'sk-or-v1-0123456789abcdef...'
        },
        'cerebras': {
            'prefix': 'csk-',
            'length': 48,
            'charset': string.ascii_letters + string.digits,
            'pattern': r'^csk-[A-Za-z0-9]{48}$',
            'example': 'csk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        },
        'deepinfra': {
            'prefix': '',
            'length': 40,
            'charset': string.ascii_letters + string.digits,
            'pattern': r'^[A-Za-z0-9]{40}$',
            'example': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        },
        'sambanova': {
            'prefix': 'snk-',
            'length': 40,
            'charset': string.ascii_letters + string.digits + '-',
            'pattern': r'^snk-[A-Za-z0-9\-]{40}$',
            'example': 'snk-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
        },
        'fireworks': {
            'prefix': 'fw_',
            'length': 43,
            'charset': string.ascii_letters + string.digits,
            'pattern': r'^fw_[A-Za-z0-9]{43}$',
            'example': 'fw_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        },
        'cohere': {
            'prefix': '',
            'length': 40,
            'charset': string.ascii_letters + string.digits,
            'pattern': r'^[A-Za-z0-9]{40}$',
            'example': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        },
        'replicate': {
            'prefix': 'r8_',
            'length': 37,
            'charset': string.ascii_letters + string.digits,
            'pattern': r'^r8_[A-Za-z0-9]{37}$',
            'example': 'r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        },
        'perplexity': {
            'prefix': 'pplx-',
            'length': 48,
            'charset': string.hexdigits.lower(),
            'pattern': r'^pplx-[a-f0-9]{48}$',
            'example': 'pplx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        },
        'dolphin': {
            'prefix': 'dph-',
            'length': 44,
            'charset': string.ascii_letters + string.digits,
            'pattern': r'^dph-[A-Za-z0-9]{44}$',
            'example': 'dph-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        },
        'deepseek': {
            'prefix': 'sk-',
            'length': 32,
            'charset': string.hexdigits.lower(),
            'pattern': r'^sk-[a-f0-9]{32}$',
            'example': 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        },
        'google': {
            'prefix': 'AIza',
            'length': 35,
            'charset': string.ascii_letters + string.digits + '-_',
            'pattern': r'^AIza[A-Za-z0-9\-_]{35}$',
            'example': 'AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        },
        'aws': {
            'prefix': 'AKIA',
            'length': 16,
            'charset': string.ascii_uppercase + string.digits,
            'pattern': r'^AKIA[A-Z0-9]{16}$',
            'example': 'AKIAxxxxxxxxxxxxxxxx'
        },
        'stripe': {
            'prefix': 'sk_live_',
            'length': 24,
            'charset': string.ascii_letters + string.digits,
            'pattern': r'^sk_live_[A-Za-z0-9]{24}$',
            'example': 'sk_live_xxxxxxxxxxxxxxxxxxxxxxxx'
        },
        'generic': {
            'prefix': '',
            'length': 32,
            'charset': string.ascii_letters + string.digits,
            'pattern': r'^[A-Za-z0-9]{32}$',
            'example': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        }
    }
    
    def __init__(self):
        self.generated_keys = []
        self.generation_stats = {
            'total_generated': 0,
            'by_provider': {}
        }
    
    def generate_key(self, provider: str = 'generic', 
                     custom_prefix: str = None,
                     custom_length: int = None,
                     include_checksum: bool = False) -> Dict:
        """
        Generate a single API key for a specific provider.
        
        Args:
            provider: Provider name (openai, groq, etc.)
            custom_prefix: Override default prefix
            custom_length: Override default length
            include_checksum: Add checksum suffix for validation
            
        Returns:
            Dict with key details
        """
        provider = provider.lower()
        
        if provider not in self.PROVIDERS:
            provider = 'generic'
        
        config = self.PROVIDERS[provider]
        prefix = custom_prefix if custom_prefix is not None else config['prefix']
        key_length = custom_length if custom_length is not None else config['length']
        charset = config['charset']
        
        # Generate random portion
        random_part = ''.join(secrets.choice(charset) for _ in range(key_length - len(prefix)))
        
        # Construct key
        api_key = prefix + random_part
        
        # Optional checksum
        checksum = None
        if include_checksum:
            checksum = self._generate_checksum(api_key)
            api_key = f"{api_key}-{checksum}"
        
        # Track stats
        self.generation_stats['total_generated'] += 1
        self.generation_stats['by_provider'][provider] = \
            self.generation_stats['by_provider'].get(provider, 0) + 1
        
        result = {
            'key': api_key,
            'provider': provider,
            'prefix': prefix,
            'length': len(api_key),
            'generated_at': datetime.utcnow().isoformat(),
            'checksum': checksum,
            'format_valid': self.validate_key(api_key, provider)
        }
        
        self.generated_keys.append(result)
        return result
    
    def generate_batch(self, provider: str = 'generic', 
                       count: int = 10,
                       unique: bool = True) -> List[Dict]:
        """
        Generate multiple API keys.
        
        Args:
            provider: Provider name
            count: Number of keys to generate
            unique: Ensure all keys are unique
            
        Returns:
            List of key dictionaries
        """
        keys = []
        seen = set()
        attempts = 0
        max_attempts = count * 10
        
        while len(keys) < count and attempts < max_attempts:
            result = self.generate_key(provider)
            attempts += 1
            
            if unique:
                if result['key'] not in seen:
                    seen.add(result['key'])
                    keys.append(result)
            else:
                keys.append(result)
        
        return keys
    
    def generate_multi_provider(self, providers: List[str] = None, 
                                 count_per_provider: int = 1) -> Dict[str, List[Dict]]:
        """
        Generate keys for multiple providers at once.
        
        Args:
            providers: List of provider names (None = all providers)
            count_per_provider: Keys per provider
            
        Returns:
            Dict mapping provider names to key lists
        """
        if providers is None:
            providers = list(self.PROVIDERS.keys())
        
        results = {}
        for provider in providers:
            results[provider] = self.generate_batch(provider, count_per_provider)
        
        return results
    
    def validate_key(self, key: str, provider: str = None) -> Dict:
        """
        Validate an API key format.
        
        Args:
            key: API key to validate
            provider: Expected provider (None = auto-detect)
            
        Returns:
            Validation result dict
        """
        result = {
            'valid': False,
            'provider': None,
            'detected_providers': [],
            'issues': []
        }
        
        if not key or not isinstance(key, str):
            result['issues'].append('Key is empty or invalid type')
            return result
        
        # Check against all providers if not specified
        providers_to_check = [provider] if provider else list(self.PROVIDERS.keys())
        
        for prov in providers_to_check:
            if prov not in self.PROVIDERS:
                continue
                
            config = self.PROVIDERS[prov]
            pattern = config['pattern']
            
            if re.match(pattern, key):
                result['detected_providers'].append(prov)
        
        if result['detected_providers']:
            result['valid'] = True
            result['provider'] = result['detected_providers'][0]
        else:
            result['issues'].append('Key format does not match any known provider')
            
            # Provide hints
            if key.startswith('sk-'):
                result['issues'].append('Looks like OpenAI/DeepSeek format but length may be wrong')
            elif key.startswith('gsk_'):
                result['issues'].append('Looks like Groq format but length may be wrong')
        
        return result
    
    def detect_provider(self, key: str) -> Optional[str]:
        """
        Detect the provider from a key's format.
        
        Args:
            key: API key
            
        Returns:
            Provider name or None
        """
        validation = self.validate_key(key)
        return validation.get('provider')
    
    def _generate_checksum(self, key: str) -> str:
        """Generate a short checksum for key verification."""
        hash_obj = hashlib.sha256(key.encode())
        return hash_obj.hexdigest()[:8]
    
    def generate_jwt_like_key(self, provider: str = 'generic') -> Dict:
        """
        Generate a JWT-like token structure.
        
        Returns:
            Dict with JWT-style key
        """
        # Header
        header = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').decode().rstrip('=')
        
        # Payload with provider info
        payload_data = {
            'iss': provider,
            'iat': int(time.time()),
            'exp': int(time.time()) + 86400 * 365,
            'sub': secrets.token_hex(16)
        }
        import json
        payload = base64.urlsafe_b64encode(json.dumps(payload_data).encode()).decode().rstrip('=')
        
        # Signature
        signature = secrets.token_urlsafe(32)
        
        jwt_key = f"{header}.{payload}.{signature}"
        
        return {
            'key': jwt_key,
            'provider': provider,
            'type': 'jwt',
            'length': len(jwt_key),
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def generate_uuid_key(self, provider: str = 'generic', 
                          prefix: str = None,
                          version: int = 4) -> Dict:
        """
        Generate a UUID-based API key.
        
        Args:
            provider: Provider name
            prefix: Optional prefix
            version: UUID version (1 or 4)
            
        Returns:
            Dict with UUID key
        """
        if version == 1:
            key_uuid = str(uuid.uuid1())
        else:
            key_uuid = str(uuid.uuid4())
        
        if prefix:
            api_key = f"{prefix}{key_uuid}"
        else:
            api_key = key_uuid
        
        return {
            'key': api_key,
            'provider': provider,
            'type': 'uuid',
            'version': version,
            'length': len(api_key),
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def generate_secure_token(self, length: int = 64, 
                               encoding: str = 'hex') -> Dict:
        """
        Generate a cryptographically secure token.
        
        Args:
            length: Token length
            encoding: 'hex', 'base64', or 'urlsafe'
            
        Returns:
            Dict with secure token
        """
        if encoding == 'hex':
            token = secrets.token_hex(length // 2)
        elif encoding == 'base64':
            token = secrets.token_bytes(length).hex()
            token = base64.b64encode(bytes.fromhex(token)).decode()[:length]
        else:  # urlsafe
            token = secrets.token_urlsafe(length)[:length]
        
        return {
            'key': token,
            'type': 'secure_token',
            'encoding': encoding,
            'length': len(token),
            'entropy_bits': len(token) * 4 if encoding == 'hex' else len(token) * 6,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def get_provider_info(self, provider: str) -> Optional[Dict]:
        """
        Get information about a provider's key format.
        
        Args:
            provider: Provider name
            
        Returns:
            Provider config dict or None
        """
        provider = provider.lower()
        if provider in self.PROVIDERS:
            config = self.PROVIDERS[provider].copy()
            config['name'] = provider
            return config
        return None
    
    def list_providers(self) -> List[Dict]:
        """
        List all supported providers with their key formats.
        
        Returns:
            List of provider info dicts
        """
        providers = []
        for name, config in self.PROVIDERS.items():
            providers.append({
                'name': name,
                'prefix': config['prefix'],
                'length': config['length'],
                'example': config['example']
            })
        return providers
    
    def get_stats(self) -> Dict:
        """Get generation statistics."""
        return {
            **self.generation_stats,
            'recent_keys': len(self.generated_keys),
            'providers_used': list(self.generation_stats['by_provider'].keys())
        }
    
    def export_keys(self, format: str = 'json') -> str:
        """
        Export generated keys.
        
        Args:
            format: 'json', 'csv', or 'text'
            
        Returns:
            Formatted string
        """
        import json
        
        if format == 'json':
            return json.dumps(self.generated_keys, indent=2)
        elif format == 'csv':
            lines = ['provider,key,generated_at']
            for k in self.generated_keys:
                lines.append(f"{k['provider']},{k['key']},{k['generated_at']}")
            return '\n'.join(lines)
        else:  # text
            lines = []
            for k in self.generated_keys:
                lines.append(f"[{k['provider']}] {k['key']}")
            return '\n'.join(lines)
    
    def clear_history(self):
        """Clear generated keys history."""
        self.generated_keys = []


# Singleton instance
_key_generator = None

def get_key_generator() -> APIKeyGenerator:
    """Get singleton key generator instance."""
    global _key_generator
    if _key_generator is None:
        _key_generator = APIKeyGenerator()
    return _key_generator


# Quick access functions
def generate_api_key(provider: str = 'generic') -> str:
    """Quick function to generate a single key."""
    gen = get_key_generator()
    return gen.generate_key(provider)['key']

def generate_keys(provider: str = 'generic', count: int = 5) -> List[str]:
    """Quick function to generate multiple keys."""
    gen = get_key_generator()
    results = gen.generate_batch(provider, count)
    return [r['key'] for r in results]

def validate_api_key(key: str) -> Dict:
    """Quick function to validate a key."""
    gen = get_key_generator()
    return gen.validate_key(key)


if __name__ == '__main__':
    # Test the generator
    gen = APIKeyGenerator()
    
    print("=== API KEY GENERATOR TEST ===\n")
    
    # Generate keys for different providers
    providers = ['openai', 'groq', 'anthropic', 'huggingface', 'together', 'deepseek']
    
    for provider in providers:
        result = gen.generate_key(provider)
        print(f"{provider.upper():12} | {result['key']}")
    
    print(f"\n=== Stats ===")
    print(gen.get_stats())
