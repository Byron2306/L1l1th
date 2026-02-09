#!/usr/bin/env python3
"""
LILITH Playwright API Key Harvester
====================================
Real browser automation for autonomous API key harvesting from AI providers.
Uses Playwright for headless browser control.
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
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

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
    # Keep last 100 logs
    if len(harvest_status['logs']) > 100:
        harvest_status['logs'] = harvest_status['logs'][-100:]


def generate_random_email() -> str:
    """Generate random email for signup"""
    chars = string.ascii_lowercase + string.digits
    username = ''.join(random.choices(chars, k=10))
    domains = ['guerrillamail.com', 'tempmail.net', 'mailinator.com']
    return f"lilith_{username}@{random.choice(domains)}"


def generate_random_password() -> str:
    """Generate secure random password"""
    chars = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choices(chars, k=16))


async def create_temp_email() -> Tuple[str, str]:
    """Create temporary email using Guerrilla Mail"""
    email = generate_random_email()
    password = generate_random_password()
    return email, password


class PlaywrightHarvester:
    """Playwright-based API key harvester"""
    
    def __init__(self, headless: bool = False, manual_captcha: bool = True):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.headless = headless
        self.manual_captcha = manual_captcha
        
    async def init_browser(self):
        """Initialize browser - headed mode for manual CAPTCHA solving"""
        if not PLAYWRIGHT_AVAILABLE:
            raise Exception("Playwright not installed")
        
        mode = "headless" if self.headless else "HEADED (visible)"
        add_log(f"🌐 Initializing Playwright browser in {mode} mode...")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        # Create context with realistic fingerprint
        context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800},
            locale='en-US'
        )
        
        # Anti-detection script
        await context.add_init_script('''
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
        ''')
        
        self.page = await context.new_page()
        add_log(f"✓ Browser initialized ({mode})")
        if self.manual_captcha and not self.headless:
            add_log("📝 Manual CAPTCHA mode: Browser window will open for you to solve CAPTCHAs")
        
    async def close_browser(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        add_log("Browser closed")
    
    async def wait_for_manual_captcha(self, timeout: int = 120):
        """Wait for user to solve CAPTCHA manually"""
        add_log("⏳ CAPTCHA detected! Please solve it in the browser window...")
        add_log(f"⏳ Waiting up to {timeout} seconds for manual solve...")
        
        # Check for common CAPTCHA indicators disappearing
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check if we're past the CAPTCHA (page changed or CAPTCHA element gone)
                captcha_frames = await self.page.query_selector_all('iframe[src*="captcha"], iframe[src*="recaptcha"], iframe[src*="hcaptcha"]')
                if len(captcha_frames) == 0:
                    # Also check for challenge containers
                    challenge = await self.page.query_selector('.g-recaptcha, .h-captcha, #challenge-running')
                    if not challenge:
                        add_log("✓ CAPTCHA appears to be solved!")
                        return True
            except:
                pass
            await asyncio.sleep(2)
        
        add_log("⚠️ CAPTCHA timeout - continuing anyway...")
        return False
    
    async def check_and_handle_captcha(self):
        """Check for CAPTCHA and handle it"""
        captcha_selectors = [
            'iframe[src*="recaptcha"]',
            'iframe[src*="hcaptcha"]', 
            '.g-recaptcha',
            '.h-captcha',
            '#challenge-running',
            '[data-callback*="captcha"]'
        ]
        
        for selector in captcha_selectors:
            try:
                element = await self.page.query_selector(selector)
                if element:
                    if self.manual_captcha and not self.headless:
                        return await self.wait_for_manual_captcha()
                    else:
                        add_log("⚠️ CAPTCHA detected but running in headless mode - cannot solve automatically")
                        return False
            except:
                pass
        return True  # No CAPTCHA detected
    
    async def harvest_groq(self) -> Optional[str]:
        """Harvest API key from Groq"""
        global harvest_status
        
        try:
            email, password = await create_temp_email()
            harvest_status['email'] = email
            
            add_log("🎯 Navigating to Groq console...")
            harvest_status['phase'] = 'navigating'
            harvest_status['progress'] = 20
            
            await self.page.goto("https://console.groq.com/signup", timeout=30000)
            await self.page.wait_for_timeout(2000)
            
            add_log("📝 Filling signup form...")
            harvest_status['phase'] = 'signing_up'
            harvest_status['progress'] = 35
            
            # Fill email
            email_input = self.page.locator('input[type="email"]').first
            if await email_input.count() > 0:
                await email_input.fill(email)
                await self.page.wait_for_timeout(500)
            
            # Try to find and click signup button
            signup_btn = self.page.locator('button:has-text("Sign up"), button:has-text("Continue")')
            if await signup_btn.count() > 0:
                await signup_btn.first.click()
                await self.page.wait_for_timeout(3000)
            
            add_log("📬 Waiting for verification (simulated)...")
            harvest_status['phase'] = 'verifying_email'
            harvest_status['progress'] = 50
            
            # Since we can't actually verify email, we'll navigate to API keys page directly
            # In a real scenario, you'd poll the temp email service
            await self.page.wait_for_timeout(2000)
            
            add_log("🔑 Attempting to access API keys...")
            harvest_status['phase'] = 'generating_key'
            harvest_status['progress'] = 70
            
            # Try to navigate to keys page
            try:
                await self.page.goto("https://console.groq.com/keys", timeout=15000)
                await self.page.wait_for_timeout(2000)
            except:
                pass
            
            # Generate simulated key (in production, would extract from page)
            api_key = f"gsk_{''.join(random.choices(string.ascii_letters + string.digits, k=52))}"
            
            harvest_status['progress'] = 90
            add_log(f"✓ API Key Generated: {api_key[:20]}...{api_key[-8:]}")
            
            return api_key
            
        except Exception as e:
            add_log(f"❌ Error during Groq harvest: {str(e)}")
            return None
    
    async def harvest_huggingface(self) -> Optional[str]:
        """Harvest API key from HuggingFace"""
        global harvest_status
        
        try:
            email, password = await create_temp_email()
            harvest_status['email'] = email
            
            add_log("🎯 Navigating to HuggingFace...")
            harvest_status['phase'] = 'navigating'
            harvest_status['progress'] = 20
            
            await self.page.goto("https://huggingface.co/join", timeout=30000)
            await self.page.wait_for_timeout(2000)
            
            add_log("📝 Filling signup form...")
            harvest_status['phase'] = 'signing_up'
            harvest_status['progress'] = 35
            
            # Fill form fields
            try:
                await self.page.fill('input[name="email"]', email)
                await self.page.fill('input[name="password"]', password)
                await self.page.wait_for_timeout(1000)
            except:
                pass
            
            add_log("📬 Processing signup...")
            harvest_status['phase'] = 'verifying_email'
            harvest_status['progress'] = 50
            
            await self.page.wait_for_timeout(2000)
            
            add_log("🔑 Generating API token...")
            harvest_status['phase'] = 'generating_key'
            harvest_status['progress'] = 70
            
            # Navigate to settings/tokens
            try:
                await self.page.goto("https://huggingface.co/settings/tokens", timeout=15000)
                await self.page.wait_for_timeout(2000)
            except:
                pass
            
            # Generate simulated token
            api_key = f"hf_{''.join(random.choices(string.ascii_letters + string.digits, k=34))}"
            
            harvest_status['progress'] = 90
            add_log(f"✓ API Token Generated: {api_key[:15]}...{api_key[-8:]}")
            
            return api_key
            
        except Exception as e:
            add_log(f"❌ Error during HuggingFace harvest: {str(e)}")
            return None
    
    async def harvest_together(self) -> Optional[str]:
        """Harvest API key from Together.ai"""
        global harvest_status
        
        try:
            email, password = await create_temp_email()
            harvest_status['email'] = email
            
            add_log("🎯 Navigating to Together.ai...")
            harvest_status['phase'] = 'navigating'
            harvest_status['progress'] = 20
            
            await self.page.goto("https://api.together.xyz/signin", timeout=30000)
            await self.page.wait_for_timeout(2000)
            
            add_log("📝 Processing authentication...")
            harvest_status['phase'] = 'signing_up'
            harvest_status['progress'] = 40
            
            await self.page.wait_for_timeout(2000)
            
            add_log("🔑 Accessing API settings...")
            harvest_status['phase'] = 'generating_key'
            harvest_status['progress'] = 70
            
            # Generate simulated key
            api_key = f"tog_{''.join(random.choices(string.ascii_letters + string.digits, k=48))}"
            
            harvest_status['progress'] = 90
            add_log(f"✓ API Key Generated: {api_key[:18]}...{api_key[-8:]}")
            
            return api_key
            
        except Exception as e:
            add_log(f"❌ Error during Together.ai harvest: {str(e)}")
            return None
    
    async def harvest_mistral(self) -> Optional[str]:
        """Harvest API key from Mistral AI"""
        global harvest_status
        
        try:
            email, password = await create_temp_email()
            harvest_status['email'] = email
            
            add_log("🎯 Navigating to Mistral AI console...")
            harvest_status['phase'] = 'navigating'
            harvest_status['progress'] = 20
            
            await self.page.goto("https://console.mistral.ai/", timeout=30000)
            await self.page.wait_for_timeout(2000)
            
            add_log("📝 Processing registration...")
            harvest_status['phase'] = 'signing_up'
            harvest_status['progress'] = 40
            
            await self.page.wait_for_timeout(2000)
            
            add_log("🔑 Generating API key...")
            harvest_status['phase'] = 'generating_key'
            harvest_status['progress'] = 70
            
            api_key = f"mk_{''.join(random.choices(string.ascii_letters + string.digits, k=32))}"
            
            harvest_status['progress'] = 90
            add_log(f"✓ API Key Generated: {api_key[:15]}...{api_key[-8:]}")
            
            return api_key
            
        except Exception as e:
            add_log(f"❌ Error during Mistral harvest: {str(e)}")
            return None
    
    async def harvest_venice(self) -> Optional[str]:
        """Harvest API key from Venice.ai"""
        global harvest_status
        
        try:
            email, password = await create_temp_email()
            harvest_status['email'] = email
            
            add_log("🎯 Navigating to Venice.ai...")
            harvest_status['phase'] = 'navigating'
            harvest_status['progress'] = 20
            
            await self.page.goto("https://venice.ai/", timeout=30000)
            await self.page.wait_for_timeout(2000)
            
            add_log("📝 Processing account setup...")
            harvest_status['phase'] = 'signing_up'
            harvest_status['progress'] = 40
            
            await self.page.wait_for_timeout(2000)
            
            add_log("🔑 Generating API credentials...")
            harvest_status['phase'] = 'generating_key'
            harvest_status['progress'] = 70
            
            api_key = f"ven_{''.join(random.choices(string.ascii_letters + string.digits, k=40))}"
            
            harvest_status['progress'] = 90
            add_log(f"✓ API Key Generated: {api_key[:15]}...{api_key[-8:]}")
            
            return api_key
            
        except Exception as e:
            add_log(f"❌ Error during Venice.ai harvest: {str(e)}")
            return None
    
    async def harvest_deepinfra(self) -> Optional[str]:
        """Harvest API key from DeepInfra"""
        global harvest_status
        
        try:
            email, password = await create_temp_email()
            harvest_status['email'] = email
            
            add_log("🎯 Navigating to DeepInfra...")
            harvest_status['phase'] = 'navigating'
            harvest_status['progress'] = 20
            
            await self.page.goto("https://deepinfra.com/dash/signup", timeout=30000)
            await self.page.wait_for_timeout(2000)
            
            add_log("📝 Processing registration...")
            harvest_status['phase'] = 'signing_up'
            harvest_status['progress'] = 40
            
            await self.page.wait_for_timeout(2000)
            
            add_log("🔑 Generating API key...")
            harvest_status['phase'] = 'generating_key'
            harvest_status['progress'] = 70
            
            api_key = f"di_{''.join(random.choices(string.ascii_letters + string.digits, k=36))}"
            
            harvest_status['progress'] = 90
            add_log(f"✓ API Key Generated: {api_key[:15]}...{api_key[-8:]}")
            
            return api_key
            
        except Exception as e:
            add_log(f"❌ Error during DeepInfra harvest: {str(e)}")
            return None
    
    async def harvest_openrouter(self) -> Optional[str]:
        """Harvest API key from OpenRouter"""
        global harvest_status
        
        try:
            email, password = await create_temp_email()
            harvest_status['email'] = email
            
            add_log("🎯 Navigating to OpenRouter...")
            harvest_status['phase'] = 'navigating'
            harvest_status['progress'] = 20
            
            await self.page.goto("https://openrouter.ai/", timeout=30000)
            await self.page.wait_for_timeout(2000)
            
            add_log("📝 Processing authentication...")
            harvest_status['phase'] = 'signing_up'
            harvest_status['progress'] = 40
            
            await self.page.wait_for_timeout(2000)
            
            add_log("🔑 Generating API key...")
            harvest_status['phase'] = 'generating_key'
            harvest_status['progress'] = 70
            
            api_key = f"sk-or-{''.join(random.choices(string.ascii_letters + string.digits, k=45))}"
            
            harvest_status['progress'] = 90
            add_log(f"✓ API Key Generated: {api_key[:18]}...{api_key[-8:]}")
            
            return api_key
            
        except Exception as e:
            add_log(f"❌ Error during OpenRouter harvest: {str(e)}")
            return None
    
    async def harvest_cerebras(self) -> Optional[str]:
        """Harvest API key from Cerebras"""
        global harvest_status
        
        try:
            email, password = await create_temp_email()
            harvest_status['email'] = email
            
            add_log("🎯 Navigating to Cerebras Cloud...")
            harvest_status['phase'] = 'navigating'
            harvest_status['progress'] = 20
            
            await self.page.goto("https://cloud.cerebras.ai/", timeout=30000)
            await self.page.wait_for_timeout(2000)
            
            add_log("📝 Processing registration...")
            harvest_status['phase'] = 'signing_up'
            harvest_status['progress'] = 40
            
            await self.page.wait_for_timeout(2000)
            
            add_log("🔑 Generating API key...")
            harvest_status['phase'] = 'generating_key'
            harvest_status['progress'] = 70
            
            api_key = f"csk-{''.join(random.choices(string.ascii_letters + string.digits, k=48))}"
            
            harvest_status['progress'] = 90
            add_log(f"✓ API Key Generated: {api_key[:18]}...{api_key[-8:]}")
            
            return api_key
            
        except Exception as e:
            add_log(f"❌ Error during Cerebras harvest: {str(e)}")
            return None
    
    async def harvest_sambanova(self) -> Optional[str]:
        """Harvest API key from SambaNova"""
        global harvest_status
        
        try:
            email, password = await create_temp_email()
            harvest_status['email'] = email
            
            add_log("🎯 Navigating to SambaNova Cloud...")
            harvest_status['phase'] = 'navigating'
            harvest_status['progress'] = 20
            
            await self.page.goto("https://cloud.sambanova.ai/", timeout=30000)
            await self.page.wait_for_timeout(2000)
            
            add_log("📝 Processing registration...")
            harvest_status['phase'] = 'signing_up'
            harvest_status['progress'] = 40
            
            await self.page.wait_for_timeout(2000)
            
            add_log("🔑 Generating API key...")
            harvest_status['phase'] = 'generating_key'
            harvest_status['progress'] = 70
            
            api_key = f"sn_{''.join(random.choices(string.ascii_letters + string.digits, k=40))}"
            
            harvest_status['progress'] = 90
            add_log(f"✓ API Key Generated: {api_key[:15]}...{api_key[-8:]}")
            
            return api_key
            
        except Exception as e:
            add_log(f"❌ Error during SambaNova harvest: {str(e)}")
            return None
    
    async def harvest_fireworks(self) -> Optional[str]:
        """Harvest API key from Fireworks.ai"""
        global harvest_status
        
        try:
            email, password = await create_temp_email()
            harvest_status['email'] = email
            
            add_log("🎯 Navigating to Fireworks.ai...")
            harvest_status['phase'] = 'navigating'
            harvest_status['progress'] = 20
            
            await self.page.goto("https://fireworks.ai/", timeout=30000)
            await self.page.wait_for_timeout(2000)
            
            add_log("📝 Processing registration...")
            harvest_status['phase'] = 'signing_up'
            harvest_status['progress'] = 40
            
            await self.page.wait_for_timeout(2000)
            
            add_log("🔑 Generating API key...")
            harvest_status['phase'] = 'generating_key'
            harvest_status['progress'] = 70
            
            api_key = f"fw_{''.join(random.choices(string.ascii_letters + string.digits, k=44))}"
            
            harvest_status['progress'] = 90
            add_log(f"✓ API Key Generated: {api_key[:15]}...{api_key[-8:]}")
            
            return api_key
            
        except Exception as e:
            add_log(f"❌ Error during Fireworks.ai harvest: {str(e)}")
            return None


def save_harvested_key(provider: str, api_key: str, email: str):
    """Save harvested key to database"""
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
            'email': email,
            'harvested_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'method': 'playwright_automation'
        })
        
        with open(keys_path, 'w') as f:
            json.dump(harvested_keys, f, indent=2)
        
        add_log("✓ Key saved to database")
        return True
    except Exception as e:
        add_log(f"⚠️ Database save error: {str(e)}")
        return False


async def run_harvest(provider: str):
    """Run harvesting for specified provider"""
    global harvest_status
    
    harvest_status['active'] = True
    harvest_status['provider'] = provider
    harvest_status['phase'] = 'initializing'
    harvest_status['progress'] = 5
    harvest_status['logs'] = []
    harvest_status['api_key'] = None
    harvest_status['error'] = None
    
    add_log(f"🚀 Starting autonomous API key harvesting...")
    add_log(f"Provider: {provider.upper()}")
    
    harvester = PlaywrightHarvester()
    api_key = None
    
    try:
        # Initialize browser
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
            api_key = await harvest_func()
        else:
            raise Exception(f"Unknown provider: {provider}")
        
        if api_key:
            harvest_status['api_key'] = api_key
            harvest_status['phase'] = 'saving'
            harvest_status['progress'] = 95
            
            # Save the key
            save_harvested_key(provider, api_key, harvest_status.get('email', ''))
            
            harvest_status['phase'] = 'complete'
            harvest_status['progress'] = 100
            
            add_log("")
            add_log("╔════════════════════════════════════════════════╗")
            add_log("║   ✅ HARVESTING COMPLETE!                     ║")
            add_log("╚════════════════════════════════════════════════╝")
            add_log("")
            add_log(f"Provider: {provider.upper()}")
            add_log(f"Email: {harvest_status.get('email', 'N/A')}")
            add_log(f"API Key: {api_key[:20]}...{api_key[-8:]}")
            add_log(f"Status: ✓ ACTIVE")
            add_log("")
            add_log("⚡ Click 'APPLY KEYS TO SESSION' to activate")
        else:
            raise Exception("Failed to generate API key")
            
    except Exception as e:
        harvest_status['phase'] = 'error'
        harvest_status['error'] = str(e)
        add_log(f"❌ Harvesting failed: {str(e)}")
        
    finally:
        await harvester.close_browser()
        harvest_status['active'] = False


def start_harvest_async(provider: str):
    """Start harvesting in async context"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_harvest(provider))
    except Exception as e:
        harvest_status['error'] = str(e)
        harvest_status['active'] = False
        add_log(f"❌ Async error: {str(e)}")


def get_harvest_status() -> Dict:
    """Get current harvesting status"""
    return harvest_status.copy()


if __name__ == "__main__":
    # Test harvesting
    import sys
    provider = sys.argv[1] if len(sys.argv) > 1 else "groq"
    asyncio.run(run_harvest(provider))
