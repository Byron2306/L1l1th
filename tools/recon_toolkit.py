#!/usr/bin/env python3
"""
LUCIFERA Recon Toolkit - Windows Compatible
============================================
Python-based reconnaissance tools that work on Windows without external dependencies.
"""

import socket
import ssl
import sys
import json
import re
import concurrent.futures
from urllib.parse import urlparse
from datetime import datetime

# Optional imports with fallbacks
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import dns.resolver
    HAS_DNS = True
except ImportError:
    HAS_DNS = False


def print_banner():
    print("""
╔══════════════════════════════════════════╗
║  LUCIFERA RECON TOOLKIT - Windows Edition ║
╚══════════════════════════════════════════╝
""")


# ==================== DNS TOOLS ====================

def dns_lookup(domain, record_type='A'):
    """Perform DNS lookup using socket or dnspython"""
    results = []
    
    if HAS_DNS:
        try:
            answers = dns.resolver.resolve(domain, record_type)
            for rdata in answers:
                results.append(str(rdata))
        except Exception as e:
            results.append(f"Error: {e}")
    else:
        # Fallback to socket for basic lookups
        try:
            if record_type == 'A':
                ips = socket.gethostbyname_ex(domain)[2]
                results.extend(ips)
            else:
                results.append(f"Install dnspython for {record_type} records: pip install dnspython")
        except socket.gaierror as e:
            results.append(f"DNS Error: {e}")
    
    return results


def dns_enum(domain):
    """Enumerate all DNS records for a domain"""
    print(f"\n[*] DNS Enumeration for: {domain}")
    print("=" * 50)
    
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']
    
    for rtype in record_types:
        results = dns_lookup(domain, rtype)
        if results and not any('Error' in str(r) for r in results):
            print(f"\n[{rtype}] Records:")
            for r in results:
                print(f"    {r}")
    
    # Get IP and reverse DNS
    try:
        ip = socket.gethostbyname(domain)
        print(f"\n[IP] {ip}")
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            print(f"[PTR] {hostname}")
        except:
            pass
    except:
        pass


# ==================== SUBDOMAIN DISCOVERY ====================

COMMON_SUBDOMAINS = [
    'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'ns2',
    'ns3', 'ns4', 'vpn', 'admin', 'administrator', 'api', 'app', 'apps',
    'blog', 'cdn', 'cloud', 'cpanel', 'db', 'dev', 'development', 'dns',
    'dns1', 'dns2', 'docs', 'download', 'email', 'exchange', 'files', 'forum',
    'ftp2', 'gateway', 'git', 'gitlab', 'help', 'home', 'host', 'img', 'imap',
    'internal', 'intranet', 'jenkins', 'jira', 'ldap', 'login', 'm', 'mail2',
    'mail3', 'manage', 'manager', 'mobile', 'monitor', 'mysql', 'new', 'news',
    'office', 'old', 'panel', 'portal', 'preview', 'prod', 'production',
    'proxy', 'remote', 'repo', 'repository', 's3', 'search', 'secure',
    'server', 'shop', 'sip', 'smtp2', 'sql', 'ssh', 'ssl', 'staging', 'static',
    'stats', 'status', 'store', 'support', 'test', 'testing', 'upload', 'v1',
    'v2', 'video', 'vpn2', 'web', 'web1', 'web2', 'webdisk', 'webhost', 'wiki',
    'www1', 'www2', 'www3', 'backup', 'beta', 'crm', 'dashboard', 'demo',
    'owa', 'autodiscover', 'autoconfig', 'mx', 'mx1', 'mx2', 'relay'
]


def check_subdomain(subdomain, domain):
    """Check if a subdomain exists"""
    full_domain = f"{subdomain}.{domain}"
    try:
        ip = socket.gethostbyname(full_domain)
        return (full_domain, ip)
    except socket.gaierror:
        return None


def discover_subdomains(domain, wordlist=None, threads=20):
    """Discover subdomains using DNS brute force"""
    print(f"\n[*] Subdomain Discovery for: {domain}")
    print("=" * 50)
    
    subdomains_to_check = wordlist if wordlist else COMMON_SUBDOMAINS
    found = []
    
    print(f"[*] Checking {len(subdomains_to_check)} subdomains with {threads} threads...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(check_subdomain, sub, domain): sub 
            for sub in subdomains_to_check
        }
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                found.append(result)
                print(f"    [+] {result[0]} -> {result[1]}")
    
    print(f"\n[*] Found {len(found)} subdomains")
    return found


# ==================== PORT SCANNING ====================

COMMON_PORTS = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
    80: 'HTTP', 110: 'POP3', 111: 'RPC', 135: 'MSRPC', 139: 'NetBIOS',
    143: 'IMAP', 443: 'HTTPS', 445: 'SMB', 993: 'IMAPS', 995: 'POP3S',
    1433: 'MSSQL', 1521: 'Oracle', 3306: 'MySQL', 3389: 'RDP',
    5432: 'PostgreSQL', 5900: 'VNC', 6379: 'Redis', 8080: 'HTTP-Proxy',
    8443: 'HTTPS-Alt', 27017: 'MongoDB'
}


def scan_port(host, port, timeout=1):
    """Scan a single port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            service = COMMON_PORTS.get(port, 'Unknown')
            return (port, service)
    except:
        pass
    return None


def port_scan(target, ports=None, threads=50, timeout=1):
    """Scan ports on a target"""
    print(f"\n[*] Port Scan for: {target}")
    print("=" * 50)
    
    # Resolve hostname to IP
    try:
        ip = socket.gethostbyname(target)
        print(f"[*] Resolved to: {ip}")
    except socket.gaierror:
        print(f"[!] Could not resolve: {target}")
        return []
    
    ports_to_scan = ports if ports else list(COMMON_PORTS.keys())
    open_ports = []
    
    print(f"[*] Scanning {len(ports_to_scan)} ports with {threads} threads...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(scan_port, ip, port, timeout): port 
            for port in ports_to_scan
        }
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                open_ports.append(result)
                print(f"    [+] Port {result[0]}/tcp OPEN ({result[1]})")
    
    # Sort by port number
    open_ports.sort(key=lambda x: x[0])
    print(f"\n[*] Found {len(open_ports)} open ports")
    return open_ports


def full_port_scan(target, threads=100, timeout=0.5):
    """Scan all 65535 ports"""
    print(f"\n[*] Full Port Scan for: {target} (this may take a while)")
    return port_scan(target, list(range(1, 65536)), threads, timeout)


# ==================== WEB TECHNOLOGY DETECTION ====================

TECH_SIGNATURES = {
    # Server headers
    'Apache': [r'Apache', r'apache'],
    'Nginx': [r'nginx', r'Nginx'],
    'IIS': [r'IIS', r'Microsoft-IIS'],
    'LiteSpeed': [r'LiteSpeed'],
    
    # Frameworks
    'WordPress': [r'wp-content', r'wp-includes', r'WordPress'],
    'Drupal': [r'Drupal', r'/sites/default/', r'drupal.org'],
    'Joomla': [r'Joomla', r'/components/'],
    'Django': [r'csrfmiddlewaretoken', r'Django'],
    'Laravel': [r'laravel_session', r'Laravel'],
    'Ruby on Rails': [r'X-Powered-By: Phusion', r'_rails'],
    'ASP.NET': [r'ASP\.NET', r'__VIEWSTATE'],
    'Express.js': [r'X-Powered-By: Express'],
    
    # JavaScript frameworks
    'React': [r'react', r'_reactRootContainer'],
    'Vue.js': [r'vue', r'__vue__'],
    'Angular': [r'ng-version', r'angular'],
    'jQuery': [r'jquery', r'jQuery'],
    
    # CMS/Platforms
    'Shopify': [r'shopify', r'Shopify'],
    'Magento': [r'Magento', r'mage/'],
    'Cloudflare': [r'cloudflare', r'cf-ray'],
    
    # Languages
    'PHP': [r'X-Powered-By: PHP', r'\.php'],
    'Python': [r'Python', r'Werkzeug'],
    'Java': [r'Java', r'JSESSIONID'],
    'Node.js': [r'Node.js', r'node'],
}


def detect_technologies(url):
    """Detect web technologies used by a website"""
    print(f"\n[*] Technology Detection for: {url}")
    print("=" * 50)
    
    if not HAS_REQUESTS:
        print("[!] Install requests: pip install requests")
        return {}
    
    detected = {}
    
    try:
        # Get headers and content
        response = requests.get(url, timeout=10, verify=False, 
                               headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        
        headers_str = str(response.headers)
        content = response.text[:50000]  # First 50KB
        combined = headers_str + content
        
        # Check headers
        print("\n[Headers]")
        important_headers = ['Server', 'X-Powered-By', 'X-Generator', 'X-Drupal-Cache', 
                           'X-AspNet-Version', 'CF-Ray', 'Set-Cookie']
        for header in important_headers:
            if header in response.headers:
                value = response.headers[header]
                print(f"    {header}: {value}")
                detected[header] = value
        
        # Detect technologies
        print("\n[Detected Technologies]")
        for tech, patterns in TECH_SIGNATURES.items():
            for pattern in patterns:
                if re.search(pattern, combined, re.IGNORECASE):
                    if tech not in detected:
                        detected[tech] = True
                        print(f"    [+] {tech}")
                    break
        
        # Check response info
        print(f"\n[Response Info]")
        print(f"    Status: {response.status_code}")
        print(f"    Content-Length: {len(response.content)}")
        print(f"    Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        
        # Security headers check
        print(f"\n[Security Headers]")
        security_headers = {
            'Content-Security-Policy': 'CSP',
            'X-Frame-Options': 'Clickjacking Protection',
            'X-Content-Type-Options': 'MIME Sniffing Protection',
            'Strict-Transport-Security': 'HSTS',
            'X-XSS-Protection': 'XSS Filter',
        }
        for header, desc in security_headers.items():
            status = "✓" if header in response.headers else "✗"
            print(f"    [{status}] {desc} ({header})")
        
    except requests.exceptions.SSLError:
        print("[!] SSL Error - site may have certificate issues")
        detected['SSL_Error'] = True
    except requests.exceptions.Timeout:
        print("[!] Connection timeout")
    except Exception as e:
        print(f"[!] Error: {e}")
    
    return detected


# ==================== SSL/TLS ANALYSIS ====================

def analyze_ssl(host, port=443):
    """Analyze SSL/TLS configuration"""
    print(f"\n[*] SSL/TLS Analysis for: {host}:{port}")
    print("=" * 50)
    
    try:
        context = ssl.create_default_context()
        
        with socket.create_connection((host, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                
                print(f"\n[Certificate Info]")
                print(f"    Subject: {dict(x[0] for x in cert['subject'])}")
                print(f"    Issuer: {dict(x[0] for x in cert['issuer'])}")
                print(f"    Version: {cert.get('version')}")
                print(f"    Serial: {cert.get('serialNumber')}")
                print(f"    Not Before: {cert.get('notBefore')}")
                print(f"    Not After: {cert.get('notAfter')}")
                
                # SANs
                if 'subjectAltName' in cert:
                    print(f"\n[Subject Alternative Names]")
                    for san_type, san_value in cert['subjectAltName']:
                        print(f"    {san_type}: {san_value}")
                
                print(f"\n[Connection Info]")
                print(f"    Protocol: {ssock.version()}")
                print(f"    Cipher: {ssock.cipher()[0]}")
                print(f"    Bits: {ssock.cipher()[2]}")
                
                return cert
                
    except ssl.SSLError as e:
        print(f"[!] SSL Error: {e}")
    except socket.timeout:
        print(f"[!] Connection timeout")
    except Exception as e:
        print(f"[!] Error: {e}")
    
    return None


# ==================== WHOIS LOOKUP ====================

def whois_lookup(domain):
    """Perform WHOIS lookup"""
    print(f"\n[*] WHOIS Lookup for: {domain}")
    print("=" * 50)
    
    try:
        import whois
        w = whois.whois(domain)
        
        print(f"\n[Domain Info]")
        print(f"    Domain: {w.domain_name}")
        print(f"    Registrar: {w.registrar}")
        print(f"    Creation Date: {w.creation_date}")
        print(f"    Expiration Date: {w.expiration_date}")
        print(f"    Updated Date: {w.updated_date}")
        
        if w.name_servers:
            print(f"\n[Name Servers]")
            ns_list = w.name_servers if isinstance(w.name_servers, list) else [w.name_servers]
            for ns in ns_list:
                print(f"    {ns}")
        
        if w.emails:
            print(f"\n[Contact Emails]")
            emails = w.emails if isinstance(w.emails, list) else [w.emails]
            for email in emails:
                print(f"    {email}")
        
        return w
        
    except ImportError:
        print("[!] Install python-whois: pip install python-whois")
    except Exception as e:
        print(f"[!] Error: {e}")
    
    return None


# ==================== FULL RECON ====================

def full_recon(target):
    """Run full reconnaissance on a target"""
    print_banner()
    print(f"[*] Starting Full Reconnaissance on: {target}")
    print("=" * 60)
    
    # Parse URL if provided
    if target.startswith(('http://', 'https://')):
        parsed = urlparse(target)
        domain = parsed.netloc
        url = target
    else:
        domain = target
        url = f"https://{target}"
    
    results = {
        'target': target,
        'domain': domain,
        'timestamp': datetime.now().isoformat()
    }
    
    # 1. DNS Enumeration
    dns_enum(domain)
    
    # 2. Subdomain Discovery
    subdomains = discover_subdomains(domain)
    results['subdomains'] = subdomains
    
    # 3. Port Scan
    open_ports = port_scan(domain)
    results['open_ports'] = open_ports
    
    # 4. Technology Detection
    if HAS_REQUESTS:
        tech = detect_technologies(url)
        results['technologies'] = tech
    
    # 5. SSL Analysis
    if 443 in [p[0] for p in open_ports] or url.startswith('https'):
        analyze_ssl(domain)
    
    # 6. WHOIS
    whois_lookup(domain)
    
    print("\n" + "=" * 60)
    print("[*] Reconnaissance Complete!")
    print("=" * 60)
    
    return results


# ==================== CLI ====================

def print_help():
    print("""
LUCIFERA Recon Toolkit - Usage:
===============================

python recon_toolkit.py <command> <target> [options]

Commands:
  dns <domain>           - DNS enumeration
  subdomains <domain>    - Subdomain discovery
  portscan <host>        - Port scan (common ports)
  fullscan <host>        - Full port scan (1-65535)
  techdetect <url>       - Technology detection
  ssl <host>             - SSL/TLS analysis
  whois <domain>         - WHOIS lookup
  full <target>          - Full reconnaissance

Examples:
  python recon_toolkit.py dns example.com
  python recon_toolkit.py subdomains example.com
  python recon_toolkit.py portscan 192.168.1.1
  python recon_toolkit.py techdetect https://example.com
  python recon_toolkit.py full example.com
""")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command in ['help', '-h', '--help']:
        print_help()
    elif command == 'dns' and len(sys.argv) >= 3:
        dns_enum(sys.argv[2])
    elif command == 'subdomains' and len(sys.argv) >= 3:
        discover_subdomains(sys.argv[2])
    elif command == 'portscan' and len(sys.argv) >= 3:
        port_scan(sys.argv[2])
    elif command == 'fullscan' and len(sys.argv) >= 3:
        full_port_scan(sys.argv[2])
    elif command == 'techdetect' and len(sys.argv) >= 3:
        detect_technologies(sys.argv[2])
    elif command == 'ssl' and len(sys.argv) >= 3:
        analyze_ssl(sys.argv[2])
    elif command == 'whois' and len(sys.argv) >= 3:
        whois_lookup(sys.argv[2])
    elif command == 'full' and len(sys.argv) >= 3:
        full_recon(sys.argv[2])
    else:
        print(f"Unknown command or missing argument: {command}")
        print_help()
