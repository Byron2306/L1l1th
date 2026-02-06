#!/usr/bin/env python3
"""
LILITH Browser Controller - Real Browser Automation
Uses Playwright for full browser control with session persistence
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright, Browser, Page, BrowserContext

class BrowserController:
    """Browser automation controller for LILITH"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.user_data_dir = Path.home() / ".lucifera" / "browser_profile"
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        
    async def start(self, headless=False):
        """Start browser with persistent profile"""
        if self.browser:
            return {"status": "already_running"}
            
        self.playwright = await async_playwright().start()
        
        # Launch persistent context (keeps cookies, sessions, etc.)
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=headless,
            viewport={"width": 1920, "height": 1080},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        
        # Get or create page
        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = await self.context.new_page()
            
        return {"status": "started", "headless": headless}
    
    async def stop(self):
        """Stop browser"""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
        self.browser = None
        self.context = None
        self.page = None
        return {"status": "stopped"}
    
    async def navigate(self, url: str):
        """Navigate to URL"""
        if not self.page:
            return {"error": "Browser not started"}
        await self.page.goto(url, wait_until="domcontentloaded")
        return {
            "status": "navigated",
            "url": self.page.url,
            "title": await self.page.title()
        }
    
    async def screenshot(self, path: str = None):
        """Take screenshot"""
        if not self.page:
            return {"error": "Browser not started"}
        if not path:
            path = str(Path.home() / ".lucifera" / "screenshot.png")
        await self.page.screenshot(path=path, full_page=True)
        return {"status": "captured", "path": path}
    
    async def get_cookies(self, domain: str = None):
        """Get cookies (for session hijacking)"""
        if not self.context:
            return {"error": "Browser not started"}
        cookies = await self.context.cookies()
        if domain:
            cookies = [c for c in cookies if domain in c.get('domain', '')]
        return {"cookies": cookies}
    
    async def set_cookies(self, cookies: list):
        """Set cookies"""
        if not self.context:
            return {"error": "Browser not started"}
        await self.context.add_cookies(cookies)
        return {"status": "cookies_set", "count": len(cookies)}
    
    async def fill_form(self, selector: str, value: str):
        """Fill a form field"""
        if not self.page:
            return {"error": "Browser not started"}
        await self.page.fill(selector, value)
        return {"status": "filled", "selector": selector}
    
    async def click(self, selector: str):
        """Click an element"""
        if not self.page:
            return {"error": "Browser not started"}
        await self.page.click(selector)
        return {"status": "clicked", "selector": selector}
    
    async def type_text(self, selector: str, text: str, delay: int = 50):
        """Type text with human-like delay"""
        if not self.page:
            return {"error": "Browser not started"}
        await self.page.type(selector, text, delay=delay)
        return {"status": "typed", "selector": selector}
    
    async def execute_js(self, script: str):
        """Execute JavaScript"""
        if not self.page:
            return {"error": "Browser not started"}
        result = await self.page.evaluate(script)
        return {"status": "executed", "result": result}
    
    async def get_page_content(self):
        """Get page HTML"""
        if not self.page:
            return {"error": "Browser not started"}
        return {
            "url": self.page.url,
            "title": await self.page.title(),
            "html": await self.page.content()
        }
    
    async def get_storage(self):
        """Get localStorage and sessionStorage"""
        if not self.page:
            return {"error": "Browser not started"}
        local = await self.page.evaluate("() => Object.fromEntries(Object.entries(localStorage))")
        session = await self.page.evaluate("() => Object.fromEntries(Object.entries(sessionStorage))")
        return {"localStorage": local, "sessionStorage": session}
    
    async def intercept_requests(self, url_pattern: str):
        """Set up request interception"""
        if not self.page:
            return {"error": "Browser not started"}
        
        captured = []
        
        async def handle_route(route):
            captured.append({
                "url": route.request.url,
                "method": route.request.method,
                "headers": route.request.headers,
                "post_data": route.request.post_data
            })
            await route.continue_()
        
        await self.page.route(url_pattern, handle_route)
        return {"status": "intercepting", "pattern": url_pattern}
    
    async def login_flow(self, url: str, username_selector: str, password_selector: str, 
                         username: str, password: str, submit_selector: str = None):
        """Automated login flow"""
        if not self.page:
            return {"error": "Browser not started"}
        
        await self.page.goto(url, wait_until="domcontentloaded")
        await self.page.fill(username_selector, username)
        await self.page.fill(password_selector, password)
        
        if submit_selector:
            await self.page.click(submit_selector)
        else:
            await self.page.press(password_selector, "Enter")
        
        await self.page.wait_for_load_state("networkidle")
        
        cookies = await self.context.cookies()
        return {
            "status": "login_attempted",
            "final_url": self.page.url,
            "cookies": cookies
        }

# Global instance
_browser = BrowserController()

async def main():
    """CLI interface"""
    import argparse
    parser = argparse.ArgumentParser(description="LILITH Browser Controller")
    parser.add_argument("command", choices=[
        "start", "stop", "navigate", "screenshot", "cookies", 
        "content", "js", "login", "storage", "click", "fill"
    ])
    parser.add_argument("--url", help="URL to navigate to")
    parser.add_argument("--selector", help="CSS selector")
    parser.add_argument("--value", help="Value to fill/type")
    parser.add_argument("--script", help="JavaScript to execute")
    parser.add_argument("--domain", help="Cookie domain filter")
    parser.add_argument("--headless", action="store_true", help="Run headless")
    parser.add_argument("--username", help="Login username")
    parser.add_argument("--password", help="Login password")
    parser.add_argument("--username-selector", help="Username field selector")
    parser.add_argument("--password-selector", help="Password field selector")
    parser.add_argument("--submit-selector", help="Submit button selector")
    
    args = parser.parse_args()
    
    if args.command == "start":
        result = await _browser.start(headless=args.headless)
    elif args.command == "stop":
        result = await _browser.stop()
    elif args.command == "navigate":
        if not args.url:
            print("Error: --url required")
            return
        result = await _browser.navigate(args.url)
    elif args.command == "screenshot":
        result = await _browser.screenshot()
    elif args.command == "cookies":
        result = await _browser.get_cookies(args.domain)
    elif args.command == "content":
        result = await _browser.get_page_content()
    elif args.command == "js":
        if not args.script:
            print("Error: --script required")
            return
        result = await _browser.execute_js(args.script)
    elif args.command == "storage":
        result = await _browser.get_storage()
    elif args.command == "click":
        if not args.selector:
            print("Error: --selector required")
            return
        result = await _browser.click(args.selector)
    elif args.command == "fill":
        if not args.selector or not args.value:
            print("Error: --selector and --value required")
            return
        result = await _browser.fill_form(args.selector, args.value)
    elif args.command == "login":
        if not all([args.url, args.username, args.password, args.username_selector, args.password_selector]):
            print("Error: --url, --username, --password, --username-selector, --password-selector required")
            return
        result = await _browser.login_flow(
            args.url, args.username_selector, args.password_selector,
            args.username, args.password, args.submit_selector
        )
    else:
        result = {"error": "Unknown command"}
    
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())
