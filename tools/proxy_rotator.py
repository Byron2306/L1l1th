#!/usr/bin/env python3
"""
LILITH PROXY ROTATION SYSTEM
============================
Manage and rotate proxies for anonymity and avoiding IP blocks.
Supports HTTP, HTTPS, SOCKS4, SOCKS5 proxies.
"""

import os
import json
import time
import random
import requests
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket


class ProxyRotator:
    """
    Proxy rotation manager with health checking and auto-rotation.
    """
    
    # Free proxy sources
    PROXY_SOURCES = [
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
        'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
        'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
        'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
        'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt',
    ]
    
    SOCKS_SOURCES = [
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
        'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt',
        'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt',
    ]
    
    def __init__(self, config_path: str = '/app/config/proxies.json'):
        self.config_path = config_path
        self.proxies = {
            'http': [],
            'https': [],
            'socks4': [],
            'socks5': []
        }
        self.working_proxies = []
        self.current_index = 0
        self.last_rotation = None
        self.stats = {
            'total_tested': 0,
            'working': 0,
            'failed': 0,
            'rotations': 0
        }
        self._lock = threading.Lock()
        self._load_config()
    
    def _load_config(self):
        """Load saved proxies from config"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self.proxies = data.get('proxies', self.proxies)
                    self.working_proxies = data.get('working', [])
        except Exception as e:
            print(f"[PROXY] Config load error: {e}")
    
    def _save_config(self):
        """Save proxies to config"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump({
                'proxies': self.proxies,
                'working': self.working_proxies,
                'last_update': datetime.now().isoformat()
            }, f, indent=2)
    
    def fetch_proxies(self, proxy_type: str = 'http') -> Dict:
        """Fetch fresh proxies from online sources"""
        sources = self.SOCKS_SOURCES if 'socks' in proxy_type else self.PROXY_SOURCES
        new_proxies = []
        
        for url in sources:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    lines = response.text.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if ':' in line and len(line) > 7:
                            new_proxies.append(line)
            except Exception as e:
                continue
        
        # Deduplicate
        new_proxies = list(set(new_proxies))
        
        if proxy_type in self.proxies:
            self.proxies[proxy_type].extend(new_proxies)
            self.proxies[proxy_type] = list(set(self.proxies[proxy_type]))
        
        self._save_config()
        
        return {
            'success': True,
            'type': proxy_type,
            'fetched': len(new_proxies),
            'total': len(self.proxies.get(proxy_type, []))
        }
    
    def add_proxy(self, proxy: str, proxy_type: str = 'http') -> Dict:
        """Add a single proxy"""
        if proxy_type not in self.proxies:
            self.proxies[proxy_type] = []
        
        if proxy not in self.proxies[proxy_type]:
            self.proxies[proxy_type].append(proxy)
            self._save_config()
            return {'success': True, 'message': f'Proxy {proxy} added'}
        
        return {'success': False, 'message': 'Proxy already exists'}
    
    def add_proxies_bulk(self, proxies: List[str], proxy_type: str = 'http') -> Dict:
        """Add multiple proxies"""
        added = 0
        for proxy in proxies:
            if proxy not in self.proxies.get(proxy_type, []):
                self.proxies.setdefault(proxy_type, []).append(proxy)
                added += 1
        
        self._save_config()
        return {'success': True, 'added': added, 'total': len(self.proxies[proxy_type])}
    
    def _test_proxy(self, proxy: str, proxy_type: str = 'http', timeout: int = 10) -> Tuple[str, bool, float]:
        """Test if a proxy is working"""
        test_url = 'http://httpbin.org/ip'
        start = time.time()
        
        try:
            if proxy_type in ['socks4', 'socks5']:
                proxies = {
                    'http': f'{proxy_type}://{proxy}',
                    'https': f'{proxy_type}://{proxy}'
                }
            else:
                proxies = {
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}'
                }
            
            response = requests.get(test_url, proxies=proxies, timeout=timeout)
            elapsed = time.time() - start
            
            if response.status_code == 200:
                return (proxy, True, elapsed)
        except:
            pass
        
        return (proxy, False, 0)
    
    def test_proxies(self, proxy_type: str = 'http', max_workers: int = 20,
                    timeout: int = 10, limit: int = None) -> Dict:
        """Test proxies in parallel"""
        proxies_to_test = self.proxies.get(proxy_type, [])
        if limit:
            proxies_to_test = proxies_to_test[:limit]
        
        if not proxies_to_test:
            return {'success': False, 'error': 'No proxies to test'}
        
        working = []
        failed = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._test_proxy, proxy, proxy_type, timeout): proxy
                for proxy in proxies_to_test
            }
            
            for future in as_completed(futures):
                proxy, is_working, latency = future.result()
                self.stats['total_tested'] += 1
                
                if is_working:
                    working.append({'proxy': proxy, 'latency': round(latency, 2)})
                    self.stats['working'] += 1
                else:
                    failed.append(proxy)
                    self.stats['failed'] += 1
        
        # Sort by latency
        working.sort(key=lambda x: x['latency'])
        
        # Update working proxies
        with self._lock:
            self.working_proxies = [p['proxy'] for p in working]
            self._save_config()
        
        return {
            'success': True,
            'tested': len(proxies_to_test),
            'working': len(working),
            'failed': len(failed),
            'working_list': working[:50],
            'best_proxy': working[0] if working else None
        }
    
    def get_proxy(self, proxy_type: str = 'http') -> Optional[Dict]:
        """Get a working proxy with rotation"""
        with self._lock:
            if not self.working_proxies:
                # Try to get from untested pool
                if self.proxies.get(proxy_type):
                    return {
                        'proxy': random.choice(self.proxies[proxy_type]),
                        'type': proxy_type,
                        'tested': False
                    }
                return None
            
            # Rotate through working proxies
            proxy = self.working_proxies[self.current_index % len(self.working_proxies)]
            self.current_index += 1
            self.stats['rotations'] += 1
            self.last_rotation = datetime.now()
            
            return {
                'proxy': proxy,
                'type': proxy_type,
                'tested': True,
                'format': {
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}',
                    'socks5': f'socks5://{proxy}'
                }
            }
    
    def get_random_proxy(self, proxy_type: str = 'http') -> Optional[Dict]:
        """Get a random working proxy"""
        with self._lock:
            pool = self.working_proxies or self.proxies.get(proxy_type, [])
            if pool:
                proxy = random.choice(pool)
                return {
                    'proxy': proxy,
                    'type': proxy_type,
                    'format': {
                        'http': f'http://{proxy}',
                        'https': f'http://{proxy}'
                    }
                }
        return None
    
    def get_request_proxies(self, proxy_type: str = 'http') -> Optional[Dict]:
        """Get proxy dict formatted for requests library"""
        proxy_info = self.get_proxy(proxy_type)
        if proxy_info:
            proxy = proxy_info['proxy']
            if proxy_type in ['socks4', 'socks5']:
                return {
                    'http': f'{proxy_type}://{proxy}',
                    'https': f'{proxy_type}://{proxy}'
                }
            return {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
        return None
    
    def remove_proxy(self, proxy: str) -> Dict:
        """Remove a proxy from all lists"""
        removed = False
        for ptype in self.proxies:
            if proxy in self.proxies[ptype]:
                self.proxies[ptype].remove(proxy)
                removed = True
        
        if proxy in self.working_proxies:
            self.working_proxies.remove(proxy)
            removed = True
        
        if removed:
            self._save_config()
            return {'success': True, 'message': 'Proxy removed'}
        return {'success': False, 'message': 'Proxy not found'}
    
    def clear_proxies(self, proxy_type: str = None) -> Dict:
        """Clear proxy lists"""
        if proxy_type:
            self.proxies[proxy_type] = []
        else:
            self.proxies = {'http': [], 'https': [], 'socks4': [], 'socks5': []}
            self.working_proxies = []
        
        self._save_config()
        return {'success': True, 'message': 'Proxies cleared'}
    
    def get_stats(self) -> Dict:
        """Get proxy statistics"""
        return {
            'success': True,
            'stats': self.stats,
            'counts': {
                'http': len(self.proxies.get('http', [])),
                'https': len(self.proxies.get('https', [])),
                'socks4': len(self.proxies.get('socks4', [])),
                'socks5': len(self.proxies.get('socks5', [])),
                'working': len(self.working_proxies)
            },
            'last_rotation': self.last_rotation.isoformat() if self.last_rotation else None
        }
    
    def make_request(self, url: str, method: str = 'GET', proxy_type: str = 'http',
                    **kwargs) -> Dict:
        """Make a request through rotating proxy"""
        max_retries = 3
        
        for attempt in range(max_retries):
            proxies = self.get_request_proxies(proxy_type)
            
            try:
                if method.upper() == 'GET':
                    response = requests.get(url, proxies=proxies, timeout=30, **kwargs)
                elif method.upper() == 'POST':
                    response = requests.post(url, proxies=proxies, timeout=30, **kwargs)
                else:
                    response = requests.request(method, url, proxies=proxies, timeout=30, **kwargs)
                
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'content': response.text[:5000],
                    'proxy_used': proxies
                }
            except Exception as e:
                # Remove failed proxy
                if proxies:
                    proxy = list(proxies.values())[0].split('://')[-1]
                    self.remove_proxy(proxy)
                continue
        
        return {'success': False, 'error': 'All proxy attempts failed'}


# Singleton
_rotator_instance = None

def get_proxy_rotator() -> ProxyRotator:
    """Get singleton proxy rotator"""
    global _rotator_instance
    if _rotator_instance is None:
        _rotator_instance = ProxyRotator()
    return _rotator_instance


if __name__ == '__main__':
    print("=== LILITH Proxy Rotator Test ===")
    
    rotator = ProxyRotator()
    
    # Fetch proxies
    print("\nFetching HTTP proxies...")
    result = rotator.fetch_proxies('http')
    print(f"  Fetched: {result['fetched']}")
    
    # Test a sample
    print("\nTesting proxies (sample of 10)...")
    result = rotator.test_proxies('http', limit=10, timeout=5)
    print(f"  Working: {result['working']}/{result['tested']}")
    
    # Get stats
    print(f"\nStats: {rotator.get_stats()}")
