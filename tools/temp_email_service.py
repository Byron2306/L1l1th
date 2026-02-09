#!/usr/bin/env python3
"""
Temporary Email Service for Automated Signups
Uses multiple temp email providers for reliability
"""

import re
import time
import random
import string
import requests
from typing import Optional, Tuple, List
from datetime import datetime


class TempEmailService:
    """Multi-provider temporary email service"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.current_email = None
        self.email_token = None
        self.provider = None
    
    def create_email(self) -> Tuple[Optional[str], Optional[str]]:
        """Create a temporary email address"""
        
        # Try multiple providers
        providers = [
            self._create_mail_tm,
            self._create_guerrilla_mail,
            self._create_1secmail,
        ]
        
        random.shuffle(providers)
        
        for provider_func in providers:
            try:
                result = provider_func()
                if result and result[0]:
                    return result
            except Exception as e:
                print(f"Provider failed: {e}")
                continue
        
        # Fallback: generate a plausible-looking email
        return self._generate_fallback_email()
    
    def _create_mail_tm(self) -> Tuple[Optional[str], Optional[str]]:
        """Create email using mail.tm API"""
        try:
            # Get available domains
            domains_resp = self.session.get('https://api.mail.tm/domains', timeout=10)
            if domains_resp.status_code != 200:
                return None, None
            
            domains = domains_resp.json().get('hydra:member', [])
            if not domains:
                return None, None
            
            domain = domains[0]['domain']
            
            # Generate random address
            username = 'lilith' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            email = f"{username}@{domain}"
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            
            # Create account
            create_resp = self.session.post(
                'https://api.mail.tm/accounts',
                json={'address': email, 'password': password},
                timeout=10
            )
            
            if create_resp.status_code == 201:
                # Get token
                token_resp = self.session.post(
                    'https://api.mail.tm/token',
                    json={'address': email, 'password': password},
                    timeout=10
                )
                
                if token_resp.status_code == 200:
                    token = token_resp.json().get('token')
                    self.current_email = email
                    self.email_token = token
                    self.provider = 'mail.tm'
                    return email, password
            
            return None, None
            
        except Exception as e:
            print(f"mail.tm error: {e}")
            return None, None
    
    def _create_guerrilla_mail(self) -> Tuple[Optional[str], Optional[str]]:
        """Create email using Guerrilla Mail API"""
        try:
            # Get email address
            resp = self.session.get(
                'https://api.guerrillamail.com/ajax.php',
                params={'f': 'get_email_address'},
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json()
                email = data.get('email_addr')
                sid_token = data.get('sid_token')
                
                if email:
                    self.current_email = email
                    self.email_token = sid_token
                    self.provider = 'guerrillamail'
                    return email, 'no_password'
            
            return None, None
            
        except Exception as e:
            print(f"Guerrilla Mail error: {e}")
            return None, None
    
    def _create_1secmail(self) -> Tuple[Optional[str], Optional[str]]:
        """Create email using 1secmail API"""
        try:
            # Get available domains
            domains_resp = self.session.get(
                'https://www.1secmail.com/api/v1/?action=getDomainList',
                timeout=10
            )
            
            if domains_resp.status_code != 200:
                return None, None
            
            domains = domains_resp.json()
            if not domains:
                return None, None
            
            domain = random.choice(domains)
            username = 'lilith' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            email = f"{username}@{domain}"
            
            self.current_email = email
            self.email_token = f"{username}:{domain}"
            self.provider = '1secmail'
            
            return email, 'no_password'
            
        except Exception as e:
            print(f"1secmail error: {e}")
            return None, None
    
    def _generate_fallback_email(self) -> Tuple[str, str]:
        """Generate a fallback email (for testing/simulation)"""
        username = 'lilith' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        domains = ['gmail.com', 'outlook.com', 'protonmail.com']
        email = f"{username}@{random.choice(domains)}"
        password = ''.join(random.choices(string.ascii_letters + string.digits + '!@#$', k=16))
        self.current_email = email
        self.provider = 'fallback'
        return email, password
    
    def check_inbox(self, wait_seconds: int = 60, check_interval: int = 5) -> List[dict]:
        """Check inbox for new emails"""
        
        if not self.current_email or not self.provider:
            return []
        
        start_time = time.time()
        
        while time.time() - start_time < wait_seconds:
            try:
                if self.provider == 'mail.tm':
                    messages = self._check_mail_tm()
                elif self.provider == 'guerrillamail':
                    messages = self._check_guerrilla()
                elif self.provider == '1secmail':
                    messages = self._check_1secmail()
                else:
                    return []
                
                if messages:
                    return messages
                    
            except Exception as e:
                print(f"Inbox check error: {e}")
            
            time.sleep(check_interval)
        
        return []
    
    def _check_mail_tm(self) -> List[dict]:
        """Check mail.tm inbox"""
        try:
            headers = {'Authorization': f'Bearer {self.email_token}'}
            resp = self.session.get(
                'https://api.mail.tm/messages',
                headers=headers,
                timeout=10
            )
            
            if resp.status_code == 200:
                messages = resp.json().get('hydra:member', [])
                return [{'subject': m.get('subject', ''), 'from': m.get('from', {}).get('address', ''), 'id': m.get('id')} for m in messages]
            
            return []
        except:
            return []
    
    def _check_guerrilla(self) -> List[dict]:
        """Check Guerrilla Mail inbox"""
        try:
            resp = self.session.get(
                'https://api.guerrillamail.com/ajax.php',
                params={'f': 'check_email', 'sid_token': self.email_token, 'seq': 0},
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json()
                messages = data.get('list', [])
                return [{'subject': m.get('mail_subject', ''), 'from': m.get('mail_from', ''), 'id': m.get('mail_id')} for m in messages]
            
            return []
        except:
            return []
    
    def _check_1secmail(self) -> List[dict]:
        """Check 1secmail inbox"""
        try:
            if not self.email_token or ':' not in self.email_token:
                return []
            
            username, domain = self.email_token.split(':')
            resp = self.session.get(
                'https://www.1secmail.com/api/v1/',
                params={'action': 'getMessages', 'login': username, 'domain': domain},
                timeout=10
            )
            
            if resp.status_code == 200:
                messages = resp.json()
                return [{'subject': m.get('subject', ''), 'from': m.get('from', ''), 'id': m.get('id')} for m in messages]
            
            return []
        except:
            return []
    
    def get_message_content(self, message_id: str) -> Optional[str]:
        """Get full message content"""
        
        if not self.provider:
            return None
        
        try:
            if self.provider == 'mail.tm':
                headers = {'Authorization': f'Bearer {self.email_token}'}
                resp = self.session.get(
                    f'https://api.mail.tm/messages/{message_id}',
                    headers=headers,
                    timeout=10
                )
                if resp.status_code == 200:
                    return resp.json().get('text', '') or resp.json().get('html', '')
            
            elif self.provider == 'guerrillamail':
                resp = self.session.get(
                    'https://api.guerrillamail.com/ajax.php',
                    params={'f': 'fetch_email', 'sid_token': self.email_token, 'email_id': message_id},
                    timeout=10
                )
                if resp.status_code == 200:
                    return resp.json().get('mail_body', '')
            
            elif self.provider == '1secmail':
                username, domain = self.email_token.split(':')
                resp = self.session.get(
                    'https://www.1secmail.com/api/v1/',
                    params={'action': 'readMessage', 'login': username, 'domain': domain, 'id': message_id},
                    timeout=10
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get('textBody', '') or data.get('htmlBody', '')
            
            return None
            
        except Exception as e:
            print(f"Get message error: {e}")
            return None
    
    def extract_verification_link(self, content: str) -> Optional[str]:
        """Extract verification link from email content"""
        if not content:
            return None
        
        # Common patterns for verification links
        patterns = [
            r'https?://[^\s<>"]+verify[^\s<>"]*',
            r'https?://[^\s<>"]+confirm[^\s<>"]*',
            r'https?://[^\s<>"]+activate[^\s<>"]*',
            r'https?://[^\s<>"]+token=[^\s<>"]+',
            r'https?://[^\s<>"]+code=[^\s<>"]+',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(0).rstrip('.')
        
        return None
    
    def extract_verification_code(self, content: str) -> Optional[str]:
        """Extract verification code from email content"""
        if not content:
            return None
        
        # Common patterns for codes
        patterns = [
            r'(?:code|Code|CODE)[:\s]+([A-Z0-9]{4,8})',
            r'(?:verification|Verification)[:\s]+([A-Z0-9]{4,8})',
            r'\b([0-9]{6})\b',  # 6-digit code
            r'\b([A-Z0-9]{6,8})\b',  # Alphanumeric code
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return None


# Singleton instance
_email_service = None

def get_email_service() -> TempEmailService:
    global _email_service
    if _email_service is None:
        _email_service = TempEmailService()
    return _email_service
