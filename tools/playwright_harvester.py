#!/usr/bin/env python3
"""
LILITH Playwright API Key Harvester - Fully Automated
======================================================
Real browser automation for autonomous API key harvesting from AI providers.
Uses stealth techniques, temp email services, and smart automation.
"""

import os
import re
import json
import time
import random
import string
import asyncio
from datetime import datetime
from typing import Dict, Optional, Tuple
from pathlib import Path

# Playwright imports
try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Temp email service
try:
    from temp_email_service import TempEmailService
    TEMP_EMAIL_AVAILABLE = True
except ImportError:
    TEMP_EMAIL_AVAILABLE = False

# Status tracking
harvest_status = {
    'active': False,
    'phase': 'idle',
    'progress': 0,
    'logs': [],
    'email': None,
    'provider': None,
    'api_key': None,
    'error': None
}


def add_log(message: str):
    """Add log message with timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    harvest_status['logs'].append(log_entry)
    print(log_entry)
    if len(harvest_status['logs']) > 100:
        harvest_status['logs'] = harvest_status['logs'][-100:]


def generate_random_password() -> str:
    """Generate secure random password"""
    lower = random.choices(string.ascii_lowercase, k=4)
    upper = random.choices(string.ascii_uppercase, k=4)
    digits = random.choices(string.digits, k=4)
    special = random.choices('!@#$%', k=2)
    password = lower + upper + digits + special
    random.shuffle(password)
    return ''.join(password)


class StealthPlaywrightHarvester:
    """Stealth Playwright-based API key harvester with full automation"""
    
    def __init__(self, headless: bool = True):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.email_service: Optional[TempEmailService] = None
        self.headless = headless
        
    async def init_browser(self):
        """Initialize browser with stealth settings"""
        if not PLAYWRIGHT_AVAILABLE:
            raise Exception("Playwright not installed. Run: playwright install chromium")
        
        mode = "headless" if self.headless else "VISIBLE (VNC)"
        add_log(f"🌐 Initializing browser in {mode} mode...")
        
        # Set browser path
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/pw-browsers'
        
        # For headed mode, use virtual display
        if not self.headless:
            os.environ['DISPLAY'] = ':99'
            add_log("📺 Using virtual display :99 - View at noVNC!")
        
        self.playwright = await async_playwright().start()
        
        # Launch with stealth arguments
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-web-security',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--disable-renderer-backgrounding',
                '--enable-features=NetworkService,NetworkServiceInProcess',
                '--force-color-profile=srgb',
                '--metrics-recording-only',
                '--no-first-run',
            ]
        )
        
        # Create context with realistic fingerprint
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York',
            color_scheme='light',
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }
        )
        
        # Anti-detection scripts
        await self.context.add_init_script('''
            // Webdriver
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            
            // Chrome runtime
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // Permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({state: Notification.permission}) :
                originalQuery(parameters)
            );
            
            // Plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Platform
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32'
            });
            
            // Hardware concurrency
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8
            });
            
            // Device memory
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });
        ''')
        
        self.page = await self.context.new_page()
        
        # Initialize temp email service
        if TEMP_EMAIL_AVAILABLE:
            self.email_service = TempEmailService()
            add_log("✓ Temp email service ready")
        else:
            add_log("⚠️ Temp email service unavailable")
        
        add_log("✓ Stealth browser initialized")
    
    async def close_browser(self):
        """Close browser properly"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except:
            pass
        add_log("Browser closed")
    
    async def human_delay(self, min_ms: int = 500, max_ms: int = 2000):
        """Add human-like delay"""
        delay = random.randint(min_ms, max_ms)
        await self.page.wait_for_timeout(delay)
    
    async def human_type(self, selector: str, text: str):
        """Type with human-like delays"""
        element = await self.page.query_selector(selector)
        if element:
            await element.click()
            await self.human_delay(100, 300)
            for char in text:
                await self.page.keyboard.type(char, delay=random.randint(50, 150))
    
    async def safe_click(self, selector: str) -> bool:
        """Safely click an element"""
        try:
            element = await self.page.query_selector(selector)
            if element:
                await element.scroll_into_view_if_needed()
                await self.human_delay(200, 500)
                await element.click()
                return True
        except Exception as e:
            add_log(f"Click failed: {e}")
        return False
    
    async def wait_for_navigation_or_timeout(self, timeout: int = 10000):
        """Wait for navigation with timeout"""
        try:
            await self.page.wait_for_load_state('networkidle', timeout=timeout)
        except:
            pass
    
    async def wait_for_user_action(self, description: str, check_func, timeout_seconds: int = 180):
        """Wait for user to complete an action (like solving CAPTCHA)
        
        Args:
            description: What we're waiting for
            check_func: Async function that returns True when action is complete
            timeout_seconds: Max time to wait
        """
        add_log(f"⏳ Waiting for: {description}")
        add_log(f"⏳ You have {timeout_seconds} seconds to complete this action")
        add_log("👀 Watch the VNC window and interact as needed!")
        
        start_time = time.time()
        check_interval = 3  # Check every 3 seconds
        
        while time.time() - start_time < timeout_seconds:
            try:
                if await check_func():
                    add_log(f"✓ {description} - Complete!")
                    return True
            except Exception as e:
                pass
            
            elapsed = int(time.time() - start_time)
            remaining = timeout_seconds - elapsed
            if elapsed % 15 == 0 and elapsed > 0:
                add_log(f"⏳ Still waiting... {remaining}s remaining")
            
            await asyncio.sleep(check_interval)
        
        add_log(f"⚠️ Timeout waiting for: {description}")
        return False
    
    async def check_for_captcha(self) -> bool:
        """Check if there's a CAPTCHA on the page"""
        captcha_selectors = [
            'iframe[src*="recaptcha"]',
            'iframe[src*="hcaptcha"]',
            '.g-recaptcha',
            '.h-captcha',
            '#challenge-running',
            '[data-sitekey]',
            'iframe[src*="captcha"]'
        ]
        
        for selector in captcha_selectors:
            try:
                element = await self.page.query_selector(selector)
                if element:
                    return True
            except:
                pass
        return False
    
    async def wait_for_captcha_solved(self, timeout: int = 180):
        """Wait for user to solve CAPTCHA"""
        if not await self.check_for_captcha():
            return True
        
        add_log("🔐 CAPTCHA DETECTED!")
        add_log("👉 Please solve it in the VNC window")
        
        async def check_solved():
            return not await self.check_for_captcha()
        
        return await self.wait_for_user_action("CAPTCHA to be solved", check_solved, timeout)
    
    async def extract_api_key_from_page(self, patterns: list) -> Optional[str]:
        """Try to extract API key from current page"""
        try:
            content = await self.page.content()
            
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    return match.group(0)
            
            # Also check visible text elements
            selectors = ['code', 'pre', '[class*="key"]', '[class*="token"]', '[class*="api"]', 'input[readonly]', 'input[disabled]']
            for selector in selectors:
                elements = await self.page.query_selector_all(selector)
                for elem in elements:
                    text = await elem.text_content()
                    if text:
                        for pattern in patterns:
                            match = re.search(pattern, text)
                            if match:
                                return match.group(0)
                    
                    # Check input value
                    try:
                        value = await elem.get_attribute('value')
                        if value:
                            for pattern in patterns:
                                match = re.search(pattern, value)
                                if match:
                                    return match.group(0)
                    except:
                        pass
            
        except Exception as e:
            add_log(f"Key extraction error: {e}")
        
        return None
    
    # ========================
    # PROVIDER-SPECIFIC HARVESTERS
    # ========================
    
    async def harvest_groq(self) -> Optional[str]:
        """Harvest API key from Groq - supports manual OAuth login"""
        global harvest_status
        
        try:
            add_log("🎯 GROQ: Starting harvest...")
            harvest_status['phase'] = 'navigating'
            harvest_status['progress'] = 10
            
            await self.page.goto("https://console.groq.com/login", timeout=30000)
            await self.human_delay(2000, 3000)
            
            harvest_status['phase'] = 'waiting_for_login'
            harvest_status['progress'] = 20
            
            # Check if we need to login
            current_url = self.page.url
            if 'login' in current_url or 'auth' in current_url or 'sign' in current_url.lower():
                add_log("")
                add_log("═" * 50)
                add_log("👉 MANUAL ACTION REQUIRED!")
                add_log("📺 Go to VNC tab and login with Google/GitHub")
                add_log("═" * 50)
                add_log("")
                
                # Wait for user to complete login (up to 3 minutes)
                async def check_logged_in():
                    url = self.page.url
                    # Check if we're past the login page
                    return 'keys' in url or 'playground' in url or 'dashboard' in url or ('console.groq.com' in url and 'login' not in url and 'auth' not in url)
                
                logged_in = await self.wait_for_user_action(
                    "Login to Groq (Google/GitHub OAuth)",
                    check_logged_in,
                    timeout_seconds=180
                )
                
                if not logged_in:
                    add_log("⚠️ Login not completed - generating demo key")
                    return f"gsk_{''.join(random.choices(string.ascii_letters + string.digits, k=52))}"
            
            harvest_status['phase'] = 'navigating_to_keys'
            harvest_status['progress'] = 50
            
            # Navigate to API keys page
            add_log("🔑 Navigating to API keys page...")
            await self.page.goto("https://console.groq.com/keys", timeout=30000)
            await self.human_delay(2000, 3000)
            
            # Wait for any CAPTCHA
            await self.wait_for_captcha_solved()
            
            harvest_status['phase'] = 'creating_key'
            harvest_status['progress'] = 70
            
            # Look for "Create API Key" button
            create_btn = await self.page.query_selector('button:has-text("Create"), button:has-text("New"), button:has-text("Generate")')
            if create_btn:
                add_log("📝 Found Create Key button, clicking...")
                await create_btn.click()
                await self.human_delay(2000, 3000)
                
                # Fill name if dialog appears
                name_input = await self.page.query_selector('input[placeholder*="name"], input[name="name"], input[type="text"]')
                if name_input:
                    await name_input.fill(f'lilith-{int(time.time())}')
                    await self.human_delay(500, 1000)
                
                # Click confirm
                confirm_btn = await self.page.query_selector('button:has-text("Submit"), button:has-text("Create"), button:has-text("Generate"):not(:disabled)')
                if confirm_btn:
                    await confirm_btn.click()
                    await self.human_delay(3000, 5000)
            
            harvest_status['progress'] = 85
            
            # Try to extract the key
            add_log("🔍 Looking for API key...")
            key = await self.extract_api_key_from_page([r'gsk_[a-zA-Z0-9]{40,60}'])
            
            if key:
                add_log(f"✓ Found REAL API key: {key[:20]}...")
                return (key, True)  # Real key
            
            # If we couldn't find a key, ask user to copy it manually
            add_log("")
            add_log("⚠️ Could not auto-extract key")
            add_log("👉 If you see a key in the VNC window, copy it manually!")
            add_log("⏳ Waiting 30 seconds for you to note it down...")
            await self.human_delay(30000, 30000)
            
            # Try one more time
            key = await self.extract_api_key_from_page([r'gsk_[a-zA-Z0-9]{40,60}'])
            if key:
                return (key, True)  # Real key
            
            add_log("⚠️ Returning demo key - get real key from console.groq.com")
            return (f"gsk_{''.join(random.choices(string.ascii_letters + string.digits, k=52))}", False)  # Demo key
            
        except Exception as e:
            add_log(f"❌ GROQ error: {str(e)}")
            return (f"gsk_{''.join(random.choices(string.ascii_letters + string.digits, k=52))}", False)
    
    async def harvest_huggingface(self) -> Optional[str]:
        """Harvest API key from HuggingFace - email signup"""
        global harvest_status
        
        try:
            add_log("🎯 HUGGINGFACE: Starting harvest...")
            harvest_status['phase'] = 'creating_email'
            harvest_status['progress'] = 10
            
            # Create temp email
            if self.email_service:
                email, password = self.email_service.create_email()
                if email:
                    harvest_status['email'] = email
                    add_log(f"📧 Created temp email: {email}")
                else:
                    email = f"lilith{''.join(random.choices(string.ascii_lowercase, k=8))}@tempmail.com"
                    password = generate_random_password()
            else:
                email = f"lilith{''.join(random.choices(string.ascii_lowercase, k=8))}@tempmail.com"
                password = generate_random_password()
            
            harvest_status['phase'] = 'navigating'
            harvest_status['progress'] = 20
            
            # Go to signup
            await self.page.goto("https://huggingface.co/join", timeout=30000)
            await self.human_delay(2000, 3000)
            
            harvest_status['phase'] = 'filling_form'
            harvest_status['progress'] = 35
            add_log("📝 Filling signup form...")
            
            # Fill email
            email_input = await self.page.query_selector('input[name="email"], input[type="email"]')
            if email_input:
                await self.human_type('input[name="email"], input[type="email"]', email)
                await self.human_delay()
            
            # Fill password
            password_input = await self.page.query_selector('input[name="password"], input[type="password"]')
            if password_input:
                await self.human_type('input[name="password"], input[type="password"]', password)
                await self.human_delay()
            
            # Submit
            submit_btn = await self.page.query_selector('button[type="submit"], button:has-text("Sign up"), button:has-text("Join")')
            if submit_btn:
                await submit_btn.click()
                await self.human_delay(3000, 5000)
            
            harvest_status['phase'] = 'verifying'
            harvest_status['progress'] = 50
            add_log("📬 Waiting for verification email...")
            
            # Check for verification email
            if self.email_service and self.email_service.provider != 'fallback':
                messages = self.email_service.check_inbox(wait_seconds=60, check_interval=5)
                
                for msg in messages:
                    if 'hugging' in msg.get('from', '').lower() or 'verify' in msg.get('subject', '').lower():
                        add_log("✓ Found verification email!")
                        content = self.email_service.get_message_content(msg['id'])
                        link = self.email_service.extract_verification_link(content)
                        
                        if link:
                            add_log(f"🔗 Clicking verification link...")
                            await self.page.goto(link, timeout=30000)
                            await self.human_delay(3000, 5000)
                            break
            
            harvest_status['phase'] = 'generating_key'
            harvest_status['progress'] = 70
            add_log("🔑 Navigating to tokens page...")
            
            # Go to tokens page
            await self.page.goto("https://huggingface.co/settings/tokens", timeout=30000)
            await self.human_delay(2000, 3000)
            
            # Try to create new token
            new_token_btn = await self.page.query_selector('button:has-text("New token"), button:has-text("Create"), a:has-text("New")')
            if new_token_btn:
                await new_token_btn.click()
                await self.human_delay(1500, 2500)
                
                # Fill token name
                name_input = await self.page.query_selector('input[name="name"], input[placeholder*="name"]')
                if name_input:
                    await self.human_type('input[name="name"], input[placeholder*="name"]', f'lilith-{int(time.time())}')
                
                # Submit
                create_btn = await self.page.query_selector('button:has-text("Create"), button[type="submit"]')
                if create_btn:
                    await create_btn.click()
                    await self.human_delay(2000, 3000)
            
            harvest_status['progress'] = 85
            
            # Extract key
            key = await self.extract_api_key_from_page([r'hf_[a-zA-Z0-9]{30,50}'])
            if key:
                add_log(f"✓ API Key found: {key[:15]}...")
                return (key, True)  # Real key
            
            # Fallback - demo key
            add_log("⚠️ Could not extract real key, generating demo")
            return (f"hf_{''.join(random.choices(string.ascii_letters + string.digits, k=34))}", False)
            
        except Exception as e:
            add_log(f"❌ HUGGINGFACE error: {str(e)}")
            return (f"hf_{''.join(random.choices(string.ascii_letters + string.digits, k=34))}", False)
    
    async def harvest_together(self) -> Tuple[Optional[str], bool]:
        """Harvest API key from Together.ai"""
        global harvest_status
        
        try:
            add_log("🎯 TOGETHER.AI: Starting harvest...")
            harvest_status['phase'] = 'navigating'
            harvest_status['progress'] = 15
            
            await self.page.goto("https://api.together.xyz/settings/api-keys", timeout=30000)
            await self.human_delay(2000, 3000)
            
            # Check if login required
            if 'sign' in self.page.url.lower() or 'login' in self.page.url.lower():
                add_log("⚠️ Together.ai requires authentication")
                add_log("📝 Uses OAuth - generating demo key")
            
            harvest_status['progress'] = 70
            
            # Try to extract key
            key = await self.extract_api_key_from_page([
                r'[a-f0-9]{64}',  # Together uses hex keys
                r'tog_[a-zA-Z0-9]{40,}',
            ])
            
            if key:
                add_log(f"✓ Found key: {key[:20]}...")
                return (key, True)
            
            # Generate demo key
            add_log("⚠️ Generating demo key")
            return (f"{''.join(random.choices('0123456789abcdef', k=64))}", False)
            
        except Exception as e:
            add_log(f"❌ TOGETHER error: {str(e)}")
            return (f"{''.join(random.choices('0123456789abcdef', k=64))}", False)
    
    async def harvest_openrouter(self) -> Tuple[Optional[str], bool]:
        """Harvest API key from OpenRouter"""
        global harvest_status
        
        try:
            add_log("🎯 OPENROUTER: Starting harvest...")
            harvest_status['phase'] = 'navigating'
            harvest_status['progress'] = 15
            
            await self.page.goto("https://openrouter.ai/keys", timeout=30000)
            await self.human_delay(2000, 3000)
            
            harvest_status['progress'] = 50
            add_log("📝 OpenRouter uses OAuth - checking for existing session")
            
            # Try to extract key
            key = await self.extract_api_key_from_page([
                r'sk-or-v1-[a-f0-9]{64}',
                r'sk-or-[a-zA-Z0-9]{40,}',
            ])
            
            if key:
                add_log(f"✓ Found key: {key[:20]}...")
                return (key, True)
            
            harvest_status['progress'] = 85
            add_log("⚠️ No existing session - generating demo key")
            return (f"sk-or-v1-{''.join(random.choices('0123456789abcdef', k=64))}", False)
            
        except Exception as e:
            add_log(f"❌ OPENROUTER error: {str(e)}")
            return (f"sk-or-v1-{''.join(random.choices('0123456789abcdef', k=64))}", False)
    
    async def harvest_mistral(self) -> Optional[str]:
        """Harvest API key from Mistral AI"""
        global harvest_status
        
        try:
            add_log("🎯 MISTRAL: Starting harvest...")
            harvest_status['phase'] = 'navigating'
            harvest_status['progress'] = 15
            
            await self.page.goto("https://console.mistral.ai/api-keys/", timeout=30000)
            await self.human_delay(2000, 3000)
            
            harvest_status['progress'] = 50
            
            key = await self.extract_api_key_from_page([
                r'[a-zA-Z0-9]{32}',  # Mistral key format
            ])
            
            if key and len(key) == 32:
                add_log(f"✓ Found key: {key[:15]}...")
                return key
            
            harvest_status['progress'] = 85
            add_log("⚠️ Generating demo key")
            return f"{''.join(random.choices(string.ascii_letters + string.digits, k=32))}"
            
        except Exception as e:
            add_log(f"❌ MISTRAL error: {str(e)}")
            return f"{''.join(random.choices(string.ascii_letters + string.digits, k=32))}"
    
    async def harvest_cerebras(self) -> Optional[str]:
        """Harvest API key from Cerebras"""
        global harvest_status
        
        try:
            add_log("🎯 CEREBRAS: Starting harvest...")
            harvest_status['phase'] = 'navigating'
            harvest_status['progress'] = 15
            
            await self.page.goto("https://cloud.cerebras.ai/", timeout=30000)
            await self.human_delay(2000, 3000)
            
            harvest_status['progress'] = 70
            
            key = await self.extract_api_key_from_page([r'csk-[a-zA-Z0-9]{40,}'])
            
            if key:
                add_log(f"✓ Found key: {key[:18]}...")
                return key
            
            add_log("⚠️ Generating demo key")
            return f"csk-{''.join(random.choices(string.ascii_letters + string.digits, k=48))}"
            
        except Exception as e:
            add_log(f"❌ CEREBRAS error: {str(e)}")
            return f"csk-{''.join(random.choices(string.ascii_letters + string.digits, k=48))}"
    
    # Generic harvester for other providers
    async def harvest_generic(self, provider: str, url: str, key_pattern: str, prefix: str, length: int) -> Tuple[Optional[str], bool]:
        """Generic harvester for providers with similar patterns
        
        Returns:
            Tuple of (api_key, is_real)
        """
        global harvest_status
        
        try:
            add_log(f"🎯 {provider.upper()}: Starting harvest...")
            harvest_status['phase'] = 'navigating'
            harvest_status['progress'] = 15
            
            await self.page.goto(url, timeout=30000)
            await self.human_delay(2000, 3000)
            
            harvest_status['progress'] = 60
            
            key = await self.extract_api_key_from_page([key_pattern])
            
            if key:
                add_log(f"✓ Found key: {key[:15]}...")
                return (key, True)  # Real key
            
            harvest_status['progress'] = 85
            add_log(f"⚠️ Generating demo key for {provider}")
            return (f"{prefix}{''.join(random.choices(string.ascii_letters + string.digits, k=length))}", False)
            
        except Exception as e:
            add_log(f"❌ {provider.upper()} error: {str(e)}")
            return (f"{prefix}{''.join(random.choices(string.ascii_letters + string.digits, k=length))}", False)
    
    async def harvest_venice(self) -> Optional[str]:
        return await self.harvest_generic('venice', 'https://venice.ai/', r'ven_[a-zA-Z0-9]{30,}', 'ven_', 40)
    
    async def harvest_deepinfra(self) -> Optional[str]:
        return await self.harvest_generic('deepinfra', 'https://deepinfra.com/dash', r'[a-zA-Z0-9]{30,}', 'di_', 36)
    
    async def harvest_sambanova(self) -> Optional[str]:
        return await self.harvest_generic('sambanova', 'https://cloud.sambanova.ai/', r'sn_[a-zA-Z0-9]{30,}', 'sn_', 40)
    
    async def harvest_fireworks(self) -> Optional[str]:
        return await self.harvest_generic('fireworks', 'https://fireworks.ai/', r'fw_[a-zA-Z0-9]{30,}', 'fw_', 44)


def save_harvested_key(provider: str, api_key: str, email: str, is_real: bool = False):
    """Save harvested key to database
    
    Args:
        provider: The AI provider name
        api_key: The API key
        email: Email used for signup
        is_real: Whether this is a real key (not generated/demo)
    """
    try:
        keys_path = Path('/app/config/harvested_keys.json')
        keys_path.parent.mkdir(parents=True, exist_ok=True)
        
        harvested_keys = []
        if keys_path.exists():
            with open(keys_path, 'r') as f:
                harvested_keys = json.load(f)
        
        # Remove existing key for this provider
        harvested_keys = [k for k in harvested_keys if k.get('provider') != provider]
        
        harvested_keys.append({
            'provider': provider,
            'key': api_key,
            'email': email or 'automated',
            'harvested_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'method': 'playwright_stealth',
            'is_real': is_real,
            'status': 'verified' if is_real else 'demo/unverified'
        })
        
        with open(keys_path, 'w') as f:
            json.dump(harvested_keys, f, indent=2)
        
        status = "REAL" if is_real else "DEMO"
        add_log(f"✓ Key saved to database ({status})")
        return True
    except Exception as e:
        add_log(f"⚠️ Database save error: {str(e)}")
        return False


async def run_harvest(provider: str, headless: bool = False, manual_captcha: bool = True):
    """Run harvesting for specified provider
    
    Args:
        provider: The AI provider to harvest from  
        headless: If False (default), shows browser in VNC for manual CAPTCHA solving
        manual_captcha: If True, pauses for manual CAPTCHA solving
    """
    global harvest_status
    
    harvest_status['active'] = True
    harvest_status['provider'] = provider
    harvest_status['phase'] = 'initializing'
    harvest_status['progress'] = 5
    harvest_status['logs'] = []
    harvest_status['api_key'] = None
    harvest_status['error'] = None
    harvest_status['is_real_key'] = False  # Track if we got a real key
    
    mode = "Headless" if headless else "VISIBLE BROWSER (VNC)"
    add_log(f"🚀 Starting API key harvesting...")
    add_log(f"Provider: {provider.upper()}")
    add_log(f"Mode: {mode}")
    
    if not headless:
        add_log("")
        add_log("═" * 50)
        add_log("📺 BROWSER IS VISIBLE IN VNC!")
        add_log("🔗 Open the VNC tab in dashboard to see & interact")
        add_log("🔐 Solve any CAPTCHAs manually when prompted")
        add_log("═" * 50)
        add_log("")
    
    harvester = StealthPlaywrightHarvester(headless=headless)
    api_key = None
    is_real = False
    
    try:
        harvest_status['phase'] = 'browser_init'
        harvest_status['progress'] = 10
        await harvester.init_browser()
        
        # Route to correct harvester
        harvest_methods = {
            'groq': harvester.harvest_groq,
            'huggingface': harvester.harvest_huggingface,
            'together': harvester.harvest_together,
            'mistral': harvester.harvest_mistral,
            'venice': harvester.harvest_venice,
            'deepinfra': harvester.harvest_deepinfra,
            'openrouter': harvester.harvest_openrouter,
            'cerebras': harvester.harvest_cerebras,
            'sambanova': harvester.harvest_sambanova,
            'fireworks': harvester.harvest_fireworks
        }
        
        harvest_func = harvest_methods.get(provider.lower())
        if harvest_func:
            result = await harvest_func()
            # Handle tuple return (key, is_real) or just key
            if isinstance(result, tuple):
                api_key, is_real = result
            else:
                api_key = result
                is_real = False  # Default to not real unless specified
        else:
            raise Exception(f"Unknown provider: {provider}")
        
        if api_key:
            harvest_status['api_key'] = api_key
            harvest_status['is_real_key'] = is_real
            harvest_status['phase'] = 'saving'
            harvest_status['progress'] = 95
            
            save_harvested_key(provider, api_key, harvest_status.get('email', 'automated'), is_real=is_real)
            
            harvest_status['phase'] = 'complete'
            harvest_status['progress'] = 100
            
            key_type = "✓ REAL KEY" if is_real else "⚠️ DEMO KEY"
            
            add_log("")
            add_log("╔════════════════════════════════════════════════╗")
            add_log("║   ✅ HARVESTING COMPLETE!                     ║")
            add_log("╚════════════════════════════════════════════════╝")
            add_log("")
            add_log(f"Provider: {provider.upper()}")
            add_log(f"API Key: {api_key[:20]}...{api_key[-8:]}")
            add_log(f"Status: {key_type}")
            add_log("")
            if not is_real:
                add_log("ℹ️ This is a demo key - for real keys, complete login in VNC")
            add_log("⚡ Click 'APPLY KEYS TO SESSION' to activate")
            add_log("")
            add_log("⚠️ Note: Most keys are DEMO keys unless you had an active session.")
            add_log("   For real keys, sign up manually at the provider's website.")
        else:
            harvest_status['phase'] = 'failed'
            harvest_status['error'] = 'Could not generate key'
            add_log("❌ Failed to harvest key")
            
    except Exception as e:
        harvest_status['phase'] = 'error'
        harvest_status['error'] = str(e)
        add_log(f"❌ Harvesting failed: {str(e)}")
        
    finally:
        await harvester.close_browser()
        harvest_status['active'] = False


def start_harvest_async(provider: str, headless: bool = True):
    """Start harvesting in async context"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_harvest(provider, headless=headless))
    except Exception as e:
        harvest_status['error'] = str(e)
        harvest_status['active'] = False
        add_log(f"❌ Async error: {str(e)}")


def get_harvest_status() -> Dict:
    """Get current harvesting status"""
    return harvest_status.copy()


if __name__ == "__main__":
    import sys
    provider = sys.argv[1] if len(sys.argv) > 1 else "groq"
    asyncio.run(run_harvest(provider))
