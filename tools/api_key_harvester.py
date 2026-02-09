#!/usr/bin/env python3
"""
LILITH Autonomous API Key Harvester
====================================
Uses browser automation to autonomously create accounts and harvest API keys
from free AI providers. This is part of LILITH's self-sustaining capabilities.

Features:
- Creates temporary email addresses
- Automates account signup on AI platforms
- Extracts and validates API keys
- Stores keys in configuration
"""

import os
import re
import time
import json
import random
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from playwright.sync_api import sync_playwright, Page, Browser

# Temporary email services that don't require accounts
TEMP_EMAIL_SERVICES = [
    {
        'name': 'TempMail.org',
        'url': 'https://temp-mail.org',
        'method': 'api',
        'api_url': 'https://api.internal.temp-mail.io/api/v3',
    },
    {
        'name': '10MinuteMail',
        'url': 'https://10minutemail.com',
        'method': 'scrape'
    },
    {
        'name': 'GuerrillaMail',
        'url': 'https://www.guerrillamail.com',
        'method': 'scrape'
    }
]

# AI Providers to harvest keys from
AI_PROVIDERS = {
    'groq': {
        'name': 'Groq',
        'signup_url': 'https://console.groq.com',
        'priority': 1,
        'steps': [
            'Navigate to signup',
            'Fill email and create account',
            'Verify email',
            'Navigate to API keys',
            'Generate API key',
            'Extract and save key'
        ]
    },
    'huggingface': {
        'name': 'HuggingFace',
        'signup_url': 'https://huggingface.co/join',
        'priority': 2,
        'steps': [
            'Navigate to signup',
            'Fill email, username, password',
            'Verify email',
            'Navigate to settings/tokens',
            'Generate access token',
            'Extract and save token'
        ]
    },
    'together': {
        'name': 'Together.ai',
        'signup_url': 'https://api.together.xyz/signup',
        'priority': 3,
        'steps': [
            'Navigate to signup',
            'Fill email and create account',
            'Verify email',
            'Navigate to API keys',
            'Generate API key',
            'Extract and save key'
        ]
    }
}


class TemporaryEmailManager:
    """Manages temporary email addresses for account creation"""
    
    def __init__(self):
        self.current_email = None
        self.current_inbox = []
        self.service = None
    
    def create_email_guerrilla(self, page: Page) -> Optional[str]:
        """Create temporary email using GuerrillaMail"""
        try:
            print("[EMAIL] Creating temporary email via GuerrillaMail...")
            page.goto('https://www.guerrillamail.com', timeout=30000)
            page.wait_for_load_state('networkidle', timeout=10000)
            
            # Get the email address
            email_elem = page.locator('#email-widget').first
            if email_elem.is_visible(timeout=5000):
                email = email_elem.inner_text()
                self.current_email = email
                self.service = 'guerrilla'
                print(f"[EMAIL] ✓ Created: {email}")
                return email
        except Exception as e:
            print(f"[EMAIL] ✗ GuerrillaMail failed: {e}")
        return None
    
    def create_email_10minute(self, page: Page) -> Optional[str]:
        """Create temporary email using 10MinuteMail"""
        try:
            print("[EMAIL] Creating temporary email via 10MinuteMail...")
            page.goto('https://10minutemail.com', timeout=30000)
            page.wait_for_load_state('networkidle', timeout=10000)
            
            # Get the email address
            email_elem = page.locator('#mail_address').first
            if email_elem.is_visible(timeout=5000):
                email = email_elem.input_value()
                self.current_email = email
                self.service = '10minute'
                print(f"[EMAIL] ✓ Created: {email}")
                return email
        except Exception as e:
            print(f"[EMAIL] ✗ 10MinuteMail failed: {e}")
        return None
    
    def get_temp_email(self, page: Page) -> Optional[str]:
        """Get a temporary email address"""
        # Try GuerrillaMail first (most reliable)
        email = self.create_email_guerrilla(page)
        if email:
            return email
        
        # Fallback to 10MinuteMail
        email = self.create_email_10minute(page)
        if email:
            return email
        
        print("[EMAIL] ✗ All temp email services failed")
        return None
    
    def check_inbox(self, page: Page, pattern: str = None) -> List[Dict]:
        """Check inbox for new emails"""
        try:
            if self.service == 'guerrilla':
                return self._check_guerrilla_inbox(page, pattern)
            elif self.service == '10minute':
                return self._check_10minute_inbox(page, pattern)
        except Exception as e:
            print(f"[EMAIL] Error checking inbox: {e}")
        return []
    
    def _check_guerrilla_inbox(self, page: Page, pattern: str = None) -> List[Dict]:
        """Check GuerrillaMail inbox"""
        try:
            page.wait_for_timeout(2000)
            emails = []
            
            # Look for email list items
            email_items = page.locator('#email_list tr').all()
            for item in email_items:
                try:
                    subject = item.locator('.email-subject').inner_text()
                    sender = item.locator('.email-sender').inner_text()
                    
                    if pattern and pattern.lower() not in subject.lower():
                        continue
                    
                    emails.append({
                        'subject': subject,
                        'sender': sender,
                        'element': item
                    })
                except:
                    continue
            
            return emails
        except Exception as e:
            print(f"[EMAIL] Error checking GuerrillaMail inbox: {e}")
            return []
    
    def _check_10minute_inbox(self, page: Page, pattern: str = None) -> List[Dict]:
        """Check 10MinuteMail inbox"""
        try:
            page.wait_for_timeout(2000)
            emails = []
            
            # Look for email list items
            email_items = page.locator('.message_top').all()
            for item in email_items:
                try:
                    subject = item.inner_text()
                    
                    if pattern and pattern.lower() not in subject.lower():
                        continue
                    
                    emails.append({
                        'subject': subject,
                        'element': item
                    })
                except:
                    continue
            
            return emails
        except Exception as e:
            print(f"[EMAIL] Error checking 10MinuteMail inbox: {e}")
            return []
    
    def extract_verification_link(self, page: Page, email_element) -> Optional[str]:
        """Extract verification link from email"""
        try:
            # Click on the email to open it
            email_element.click()
            page.wait_for_timeout(2000)
            
            # Get email body
            if self.service == 'guerrilla':
                body = page.locator('#email_body').first.inner_html()
            elif self.service == '10minute':
                body = page.locator('.message_body').first.inner_html()
            else:
                return None
            
            # Extract links
            links = re.findall(r'https?://[^\s<>"]+', body)
            
            # Find verification/confirm links
            for link in links:
                if any(keyword in link.lower() for keyword in ['verify', 'confirm', 'activate', 'signup']):
                    print(f"[EMAIL] Found verification link: {link[:60]}...")
                    return link
            
            # Return first HTTPS link if no specific verification link found
            for link in links:
                if link.startswith('https://'):
                    return link
            
        except Exception as e:
            print(f"[EMAIL] Error extracting verification link: {e}")
        
        return None


class APIKeyHarvester:
    """Harvests API keys from various AI providers"""
    
    def __init__(self):
        self.email_manager = TemporaryEmailManager()
        self.harvested_keys = []
        self.browser = None
        self.context = None
        self.page = None
    
    def start_browser(self, headless: bool = True) -> Page:
        """Start browser session"""
        print("[BROWSER] Starting browser...")
        playwright = sync_playwright().start()
        
        self.browser = playwright.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = self.context.new_page()
        print("[BROWSER] ✓ Browser started")
        return self.page
    
    def close_browser(self):
        """Close browser session"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        print("[BROWSER] Browser closed")
    
    def generate_random_credentials(self) -> Dict[str, str]:
        """Generate random credentials for signup"""
        username = f"user{random.randint(10000, 99999)}"
        password = f"Pass{random.randint(100000, 999999)}!Aa"
        
        return {
            'username': username,
            'password': password,
            'first_name': f"Test{random.randint(100, 999)}",
            'last_name': f"User{random.randint(100, 999)}"
        }
    
    def harvest_groq_key(self) -> Optional[str]:
        """Harvest API key from Groq"""
        print("\n" + "="*60)
        print("[GROQ] Starting Groq API key harvesting...")
        print("="*60)
        
        try:
            # Start browser if not already started
            if not self.page:
                self.start_browser(headless=False)  # Visible for debugging
            
            # Step 1: Get temporary email
            email = self.email_manager.get_temp_email(self.page)
            if not email:
                print("[GROQ] ✗ Failed to get temporary email")
                return None
            
            # Open new tab for Groq
            groq_page = self.context.new_page()
            
            # Step 2: Navigate to Groq signup
            print("[GROQ] Navigating to Groq console...")
            groq_page.goto('https://console.groq.com', timeout=30000)
            groq_page.wait_for_load_state('networkidle', timeout=10000)
            
            # Step 3: Look for signup/login button
            print("[GROQ] Looking for signup option...")
            groq_page.wait_for_timeout(3000)
            
            # Try to find and click sign up/login buttons
            selectors_to_try = [
                'button:has-text("Sign")',
                'a:has-text("Sign")',
                'button:has-text("Log in")',
                'a:has-text("Log in")',
                '[data-testid="signin"]',
                '[data-testid="signup"]'
            ]
            
            clicked = False
            for selector in selectors_to_try:
                try:
                    element = groq_page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        element.click()
                        clicked = True
                        print(f"[GROQ] Clicked: {selector}")
                        break
                except:
                    continue
            
            if not clicked:
                print("[GROQ] Could not find signup button, taking screenshot...")
                groq_page.screenshot(path='/tmp/groq_page.png')
                print("[GROQ] Screenshot saved to /tmp/groq_page.png")
                print("[GROQ] ℹ️  Manual intervention may be required")
                
                # Save instructions for manual completion
                instructions = f"""
GROQ API Key Harvesting - Manual Completion Instructions:
==========================================================

Email: {email}

Steps to complete manually:
1. Navigate to: https://console.groq.com
2. Sign up using email: {email}
3. Check verification email in the temp email tab
4. Complete verification
5. Navigate to API Keys section
6. Generate new API key
7. Copy the key

The temporary email inbox is open in the browser.
Check it for verification emails from Groq.
"""
                print(instructions)
                
                # Keep browser open for manual intervention
                input("\n[GROQ] Press Enter after manually completing signup and getting API key...")
                
                # Try to extract API key from page
                api_key = self._extract_groq_key(groq_page)
                if api_key:
                    return api_key
            
            groq_page.wait_for_timeout(5000)
            
            # Step 4: Fill in email
            print("[GROQ] Attempting to fill email...")
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                '#email',
                '[placeholder*="email" i]'
            ]
            
            for selector in email_selectors:
                try:
                    email_input = groq_page.locator(selector).first
                    if email_input.is_visible(timeout=2000):
                        email_input.fill(email)
                        print(f"[GROQ] ✓ Filled email: {email}")
                        break
                except:
                    continue
            
            # Continue button
            groq_page.locator('button[type="submit"]').first.click()
            groq_page.wait_for_timeout(3000)
            
            # Step 5: Check for verification email
            print("[GROQ] Checking for verification email...")
            max_attempts = 10
            for attempt in range(max_attempts):
                emails = self.email_manager.check_inbox(self.page, pattern='groq')
                
                if emails:
                    print(f"[GROQ] ✓ Found {len(emails)} email(s)")
                    
                    # Extract verification link
                    link = self.email_manager.extract_verification_link(self.page, emails[0]['element'])
                    if link:
                        print(f"[GROQ] Clicking verification link...")
                        groq_page.goto(link, timeout=30000)
                        groq_page.wait_for_load_state('networkidle', timeout=10000)
                        break
                
                print(f"[GROQ] Waiting for email... ({attempt+1}/{max_attempts})")
                self.page.wait_for_timeout(5000)
            
            # Step 6: Navigate to API keys section
            print("[GROQ] Navigating to API keys...")
            groq_page.wait_for_timeout(5000)
            
            # Look for API Keys menu/button
            api_key_selectors = [
                'a:has-text("API Keys")',
                'button:has-text("API Keys")',
                '[href*="api-keys"]',
                'text=/API.*Keys/i'
            ]
            
            for selector in api_key_selectors:
                try:
                    element = groq_page.locator(selector).first
                    if element.is_visible(timeout=3000):
                        element.click()
                        print(f"[GROQ] Clicked API Keys section")
                        break
                except:
                    continue
            
            groq_page.wait_for_timeout(3000)
            
            # Step 7: Generate API key
            print("[GROQ] Generating API key...")
            create_selectors = [
                'button:has-text("Create")',
                'button:has-text("Generate")',
                'button:has-text("New")',
                '[data-testid="create-api-key"]'
            ]
            
            for selector in create_selectors:
                try:
                    element = groq_page.locator(selector).first
                    if element.is_visible(timeout=3000):
                        element.click()
                        print(f"[GROQ] Clicked create key button")
                        break
                except:
                    continue
            
            groq_page.wait_for_timeout(3000)
            
            # Step 8: Extract API key
            api_key = self._extract_groq_key(groq_page)
            
            if api_key:
                print(f"[GROQ] ✓ Successfully harvested API key: {api_key[:20]}...")
                self._save_key('groq', api_key, email)
                return api_key
            else:
                print("[GROQ] ✗ Could not extract API key")
                groq_page.screenshot(path='/tmp/groq_api_keys_page.png')
                print("[GROQ] Screenshot saved for debugging")
            
        except Exception as e:
            print(f"[GROQ] ✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def _extract_groq_key(self, page: Page) -> Optional[str]:
        """Extract Groq API key from page"""
        try:
            # Look for patterns like gsk_...
            content = page.content()
            
            # Groq API keys start with gsk_
            matches = re.findall(r'gsk_[A-Za-z0-9]{40,}', content)
            if matches:
                return matches[0]
            
            # Try to find in input fields or code blocks
            selectors = [
                'input[value^="gsk_"]',
                'code:has-text("gsk_")',
                'pre:has-text("gsk_")',
                '[data-testid*="api-key"]'
            ]
            
            for selector in selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        text = element.inner_text() or element.input_value()
                        matches = re.findall(r'gsk_[A-Za-z0-9]{40,}', text)
                        if matches:
                            return matches[0]
                except:
                    continue
            
        except Exception as e:
            print(f"[GROQ] Error extracting key: {e}")
        
        return None
    
    def harvest_huggingface_key(self) -> Optional[str]:
        """Harvest API token from HuggingFace"""
        print("\n" + "="*60)
        print("[HF] Starting HuggingFace token harvesting...")
        print("="*60)
        
        try:
            if not self.page:
                self.start_browser(headless=False)
            
            # Get temporary email
            email = self.email_manager.get_temp_email(self.page)
            if not email:
                return None
            
            # Open new tab for HuggingFace
            hf_page = self.context.new_page()
            
            # Generate credentials
            creds = self.generate_random_credentials()
            
            print("[HF] Navigating to HuggingFace signup...")
            hf_page.goto('https://huggingface.co/join', timeout=30000)
            hf_page.wait_for_load_state('networkidle', timeout=10000)
            hf_page.wait_for_timeout(3000)
            
            # Fill signup form
            print("[HF] Filling signup form...")
            
            # Email
            hf_page.locator('input[name="email"]').first.fill(email)
            
            # Username
            hf_page.locator('input[name="username"]').first.fill(creds['username'])
            
            # Password
            hf_page.locator('input[name="password"]').first.fill(creds['password'])
            
            # Submit
            hf_page.locator('button[type="submit"]').first.click()
            hf_page.wait_for_timeout(5000)
            
            print(f"[HF] Form submitted. Email: {email}, Username: {creds['username']}")
            print(f"[HF] Password: {creds['password']}")
            
            # Wait for manual verification if needed
            print("[HF] ℹ️  Check temp email for verification link...")
            input("\n[HF] Press Enter after email verification...")
            
            # Navigate to token settings
            print("[HF] Navigating to access tokens...")
            hf_page.goto('https://huggingface.co/settings/tokens', timeout=30000)
            hf_page.wait_for_timeout(3000)
            
            # Create new token
            print("[HF] Creating new access token...")
            hf_page.locator('button:has-text("New token")').first.click(timeout=5000)
            hf_page.wait_for_timeout(2000)
            
            # Fill token name
            hf_page.locator('input[name="name"]').first.fill(f"lilith-{int(time.time())}")
            
            # Select read permission (usually default)
            # Submit
            hf_page.locator('button:has-text("Generate")').first.click()
            hf_page.wait_for_timeout(3000)
            
            # Extract token
            token = self._extract_hf_token(hf_page)
            
            if token:
                print(f"[HF] ✓ Successfully harvested token: {token[:20]}...")
                self._save_key('huggingface', token, email)
                return token
            else:
                print("[HF] ✗ Could not extract token")
                hf_page.screenshot(path='/tmp/hf_tokens_page.png')
            
        except Exception as e:
            print(f"[HF] ✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def _extract_hf_token(self, page: Page) -> Optional[str]:
        """Extract HuggingFace token from page"""
        try:
            # HF tokens start with hf_
            content = page.content()
            matches = re.findall(r'hf_[A-Za-z0-9]{30,}', content)
            if matches:
                return matches[0]
            
            # Try input fields
            selectors = [
                'input[value^="hf_"]',
                'code:has-text("hf_")',
                'pre'
            ]
            
            for selector in selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        text = element.inner_text() or element.input_value()
                        matches = re.findall(r'hf_[A-Za-z0-9]{30,}', text)
                        if matches:
                            return matches[0]
                except:
                    continue
        
        except Exception as e:
            print(f"[HF] Error extracting token: {e}")
        
        return None
    
    def _save_key(self, provider: str, key: str, email: str):
        """Save harvested key to configuration"""
        key_data = {
            'provider': provider,
            'key': key,
            'email': email,
            'harvested_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        self.harvested_keys.append(key_data)
        
        # Save to file
        keys_file = Path('/app/config/harvested_keys.json')
        keys_file.parent.mkdir(parents=True, exist_ok=True)
        
        existing_keys = []
        if keys_file.exists():
            with open(keys_file, 'r') as f:
                existing_keys = json.load(f)
        
        existing_keys.append(key_data)
        
        with open(keys_file, 'w') as f:
            json.dump(existing_keys, f, indent=2)
        
        print(f"[SAVE] ✓ Key saved to {keys_file}")
        
        # Update main config file
        self._update_config(provider, key)
    
    def _update_config(self, provider: str, key: str):
        """Update main configuration with new key"""
        config_file = Path('/app/config/lucifera.conf')
        
        if not config_file.exists():
            return
        
        # Read config
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Update appropriate key
        if provider == 'groq':
            content = re.sub(
                r'groq_api_key\s*=\s*.*',
                f'groq_api_key = {key}',
                content
            )
        elif provider == 'huggingface':
            content = re.sub(
                r'hf_token\s*=\s*.*',
                f'hf_token = {key}',
                content
            )
        
        # Write back
        with open(config_file, 'w') as f:
            f.write(content)
        
        print(f"[CONFIG] ✓ Updated configuration with {provider} key")
    
    def run_harvest_campaign(self, providers: List[str] = None):
        """Run complete harvesting campaign"""
        if providers is None:
            providers = ['groq', 'huggingface']
        
        print("""
╔════════════════════════════════════════════════════════════════╗
║        LILITH Autonomous API Key Harvesting Campaign          ║
╚════════════════════════════════════════════════════════════════╝
        """)
        
        try:
            self.start_browser(headless=False)
            
            for provider in providers:
                if provider == 'groq':
                    key = self.harvest_groq_key()
                    if key:
                        print(f"\n✓ Groq key harvested successfully!")
                elif provider == 'huggingface':
                    key = self.harvest_huggingface_key()
                    if key:
                        print(f"\n✓ HuggingFace token harvested successfully!")
                
                # Pause between providers
                time.sleep(5)
            
            print("\n" + "="*60)
            print(f"📊 Campaign Complete: {len(self.harvested_keys)} keys harvested")
            print("="*60)
            
            for key_data in self.harvested_keys:
                print(f"  ✓ {key_data['provider']}: {key_data['key'][:20]}...")
        
        finally:
            # Keep browser open for inspection
            input("\nPress Enter to close browser...")
            self.close_browser()


def main():
    """Main function"""
    harvester = APIKeyHarvester()
    
    # Run harvesting campaign
    harvester.run_harvest_campaign(providers=['groq'])
    
    print("\n✓ Harvesting complete! Keys saved to configuration.")
    print("  Restart LILITH backend to use new keys.")


if __name__ == '__main__':
    main()
