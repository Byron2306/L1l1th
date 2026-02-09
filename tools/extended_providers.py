#!/usr/bin/env python3
"""
LILITH Extended AI Providers
==============================
Additional AI providers including:
- Dolphin (Uncensored)
- DeepSeek
- Perplexity
- Cohere
- AI21
- Anthropic (direct)
- Local Ollama models
"""

import os
import json
import time
import asyncio
import aiohttp
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class DolphinProvider:
    """Dolphin AI - Uncensored model access"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('DOLPHIN_API_KEY', '')
        self.base_url = "https://api.dolphin.ai/v1"  # Example URL
        self.models = [
            'dolphin-2.6-mixtral-8x7b',
            'dolphin-2.5-mixtral-8x7b', 
            'dolphin-2.2-70b',
            'dolphin-llama3-70b'
        ]
    
    def chat(self, message: str, model: str = None, system_prompt: str = None) -> Dict:
        """Send chat message to Dolphin"""
        if not self.api_key:
            return self._get_alternative_access()
        
        model = model or self.models[0]
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': model,
                'messages': [
                    {'role': 'system', 'content': system_prompt or 'You are a helpful assistant.'},
                    {'role': 'user', 'content': message}
                ],
                'temperature': 0.7,
                'max_tokens': 2048
            }
            
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'response': data['choices'][0]['message']['content'],
                    'model': model,
                    'provider': 'dolphin'
                }
            else:
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_alternative_access(self) -> Dict:
        """Return alternative ways to access Dolphin models"""
        return {
            'success': False,
            'error': 'No API key',
            'alternatives': {
                'huggingface': {
                    'url': 'https://huggingface.co/cognitivecomputations',
                    'models': self.models,
                    'inference': 'Use HuggingFace Inference API'
                },
                'local': {
                    'ollama': 'ollama pull dolphin-mixtral',
                    'lmstudio': 'Download GGUF from HuggingFace'
                },
                'api_sources': [
                    'https://openrouter.ai (has Dolphin models)',
                    'https://together.ai (has Dolphin)',
                    'https://deepinfra.com'
                ]
            }
        }


class DeepSeekProvider:
    """DeepSeek AI - Advanced reasoning models"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('DEEPSEEK_API_KEY', '')
        self.base_url = "https://api.deepseek.com/v1"
        self.models = [
            'deepseek-chat',
            'deepseek-coder',
            'deepseek-reasoner'
        ]
    
    def chat(self, message: str, model: str = None, system_prompt: str = None) -> Dict:
        """Send chat message to DeepSeek"""
        if not self.api_key:
            return self._get_signup_info()
        
        model = model or 'deepseek-chat'
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': model,
                'messages': [
                    {'role': 'system', 'content': system_prompt or 'You are a helpful AI assistant.'},
                    {'role': 'user', 'content': message}
                ],
                'temperature': 0.7,
                'max_tokens': 4096
            }
            
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'response': data['choices'][0]['message']['content'],
                    'model': model,
                    'provider': 'deepseek',
                    'usage': data.get('usage', {})
                }
            else:
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_signup_info(self) -> Dict:
        """Return signup information for DeepSeek"""
        return {
            'success': False,
            'error': 'No API key',
            'signup': {
                'url': 'https://platform.deepseek.com/',
                'pricing': 'Very affordable - $0.14/1M input tokens',
                'free_tier': '$5 free credits on signup',
                'models': self.models
            }
        }


class PerplexityProvider:
    """Perplexity AI - Search-augmented AI"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('PERPLEXITY_API_KEY', '')
        self.base_url = "https://api.perplexity.ai"
        self.models = [
            'llama-3.1-sonar-small-128k-online',
            'llama-3.1-sonar-large-128k-online',
            'llama-3.1-sonar-huge-128k-online'
        ]
    
    def search_chat(self, query: str, model: str = None) -> Dict:
        """Search-augmented chat"""
        if not self.api_key:
            return {'success': False, 'error': 'No API key', 'signup': 'https://www.perplexity.ai/'}
        
        model = model or self.models[0]
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': model,
                'messages': [{'role': 'user', 'content': query}]
            }
            
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'response': data['choices'][0]['message']['content'],
                    'citations': data.get('citations', []),
                    'model': model
                }
            else:
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}


class CohereProvider:
    """Cohere AI"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('COHERE_API_KEY', '')
        self.base_url = "https://api.cohere.ai/v1"
    
    def chat(self, message: str) -> Dict:
        """Send chat message"""
        if not self.api_key:
            return {'success': False, 'error': 'No API key', 'signup': 'https://dashboard.cohere.ai/'}
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'message': message,
                'model': 'command-r-plus'
            }
            
            response = requests.post(
                f'{self.base_url}/chat',
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'response': data.get('text', ''),
                    'provider': 'cohere'
                }
            else:
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}


class OllamaProvider:
    """Local Ollama models"""
    
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.available = self._check_available()
    
    def _check_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f'{self.host}/api/tags', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> Dict:
        """List available models"""
        if not self.available:
            return {'success': False, 'error': 'Ollama not running', 'install': 'curl -fsSL https://ollama.ai/install.sh | sh'}
        
        try:
            response = requests.get(f'{self.host}/api/tags', timeout=10)
            data = response.json()
            return {
                'success': True,
                'models': [m['name'] for m in data.get('models', [])]
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def chat(self, message: str, model: str = 'llama3') -> Dict:
        """Chat with local model"""
        if not self.available:
            return {'success': False, 'error': 'Ollama not running'}
        
        try:
            payload = {
                'model': model,
                'prompt': message,
                'stream': False
            }
            
            response = requests.post(
                f'{self.host}/api/generate',
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'response': data.get('response', ''),
                    'model': model,
                    'provider': 'ollama'
                }
            else:
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def pull_model(self, model: str) -> Dict:
        """Pull a model"""
        if not self.available:
            return {'success': False, 'error': 'Ollama not running'}
        
        try:
            response = requests.post(
                f'{self.host}/api/pull',
                json={'name': model},
                timeout=600
            )
            return {'success': response.status_code == 200, 'model': model}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class ExtendedProviderManager:
    """Manage all extended AI providers"""
    
    def __init__(self):
        self.dolphin = DolphinProvider()
        self.deepseek = DeepSeekProvider()
        self.perplexity = PerplexityProvider()
        self.cohere = CohereProvider()
        self.ollama = OllamaProvider()
        
        self.all_providers = {
            'dolphin': {
                'instance': self.dolphin,
                'description': 'Uncensored Dolphin models',
                'models': self.dolphin.models,
                'requires_key': True
            },
            'deepseek': {
                'instance': self.deepseek,
                'description': 'DeepSeek reasoning models',
                'models': self.deepseek.models,
                'requires_key': True
            },
            'perplexity': {
                'instance': self.perplexity,
                'description': 'Search-augmented AI',
                'models': self.perplexity.models,
                'requires_key': True
            },
            'cohere': {
                'instance': self.cohere,
                'description': 'Cohere Command models',
                'models': ['command-r-plus', 'command-r'],
                'requires_key': True
            },
            'ollama': {
                'instance': self.ollama,
                'description': 'Local Ollama models',
                'models': ['llama3', 'mixtral', 'codellama', 'dolphin-mixtral'],
                'requires_key': False,
                'available': self.ollama.available
            }
        }
    
    def get_status(self) -> Dict:
        """Get status of all providers"""
        status = {}
        for name, info in self.all_providers.items():
            if name == 'ollama':
                status[name] = {
                    'available': info['available'],
                    'description': info['description'],
                    'models': info['models']
                }
            else:
                has_key = bool(info['instance'].api_key) if hasattr(info['instance'], 'api_key') else False
                status[name] = {
                    'has_api_key': has_key,
                    'description': info['description'],
                    'models': info['models']
                }
        return status
    
    def chat(self, provider: str, message: str, **kwargs) -> Dict:
        """Chat with specified provider"""
        if provider not in self.all_providers:
            return {'success': False, 'error': f'Unknown provider: {provider}'}
        
        instance = self.all_providers[provider]['instance']
        
        if hasattr(instance, 'chat'):
            return instance.chat(message, **kwargs)
        elif hasattr(instance, 'search_chat'):
            return instance.search_chat(message, **kwargs)
        else:
            return {'success': False, 'error': 'Provider does not support chat'}
    
    def add_api_key(self, provider: str, api_key: str) -> Dict:
        """Add API key for provider"""
        if provider not in self.all_providers:
            return {'success': False, 'error': f'Unknown provider: {provider}'}
        
        instance = self.all_providers[provider]['instance']
        instance.api_key = api_key
        
        # Save to config
        self._save_key(provider, api_key)
        
        return {'success': True, 'provider': provider, 'message': 'API key added'}
    
    def _save_key(self, provider: str, api_key: str):
        """Save API key to config"""
        try:
            keys_path = '/app/config/provider_keys.json'
            keys = {}
            
            if os.path.exists(keys_path):
                with open(keys_path, 'r') as f:
                    keys = json.load(f)
            
            keys[provider] = api_key
            
            with open(keys_path, 'w') as f:
                json.dump(keys, f, indent=2)
        except:
            pass


# Export functions
def get_dolphin(api_key: str = None) -> DolphinProvider:
    return DolphinProvider(api_key)

def get_deepseek(api_key: str = None) -> DeepSeekProvider:
    return DeepSeekProvider(api_key)

def get_perplexity(api_key: str = None) -> PerplexityProvider:
    return PerplexityProvider(api_key)

def get_cohere(api_key: str = None) -> CohereProvider:
    return CohereProvider(api_key)

def get_ollama(host: str = None) -> OllamaProvider:
    return OllamaProvider(host or "http://localhost:11434")

def get_extended_providers() -> ExtendedProviderManager:
    return ExtendedProviderManager()
