#!/usr/bin/env python3
"""
LILITH Browser Controller - Real Browser Automation
Uses Playwright SYNC API for Flask compatibility
"""

import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext

class BrowserController:
    """Browser automation controller for LILITH - Sync Version"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.playwright = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.user_data_dir = Path.home() / ".lucifera" / "browser_profile"
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        
    def start(self, headless=False):
        """Start browser with persistent profile"""
        if self.context:
            return {"status": "already_running"}
            
        self.playwright = sync_playwright().start()
        
        # Launch persistent context (keeps cookies, sessions, etc.)
        self.context = self.playwright.chromium.launch_persistent_context(
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
            self.page = self.context.new_page()
            
        return {"status": "started", "headless": headless}
    
    def stop(self):
        """Stop browser"""
        if self.context:
            self.context.close()
            self.context = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
        self.page = None
        return {"status": "stopped"}
    
    def navigate(self, url: str):
        """Navigate to URL"""
        if not self.page:
            return {"error": "Browser not started. Call /browser/start first."}
        self.page.goto(url, wait_until="domcontentloaded")
        return {
            "status": "navigated",
            "url": self.page.url,
            "title": self.page.title()
        }
    
    def screenshot(self, path: str = None):
        """Take screenshot"""
        if not self.page:
            return {"error": "Browser not started"}
        if not path:
            path = str(Path.home() / ".lucifera" / "screenshot.png")
        self.page.screenshot(path=path, full_page=True)
        return {"status": "captured", "path": path}
    
    def get_cookies(self, domain: str = None):
        """Get cookies (for session hijacking)"""
        if not self.context:
            return {"error": "Browser not started"}
        cookies = self.context.cookies()
        if domain:
            cookies = [c for c in cookies if domain in c.get('domain', '')]
        return {"cookies": cookies}
    
    def set_cookies(self, cookies: list):
        """Set cookies"""
        if not self.context:
            return {"error": "Browser not started"}
        self.context.add_cookies(cookies)
        return {"status": "cookies_set", "count": len(cookies)}
    
    def fill_form(self, selector: str, value: str):
        """Fill a form field"""
        if not self.page:
            return {"error": "Browser not started"}
        self.page.fill(selector, value)
        return {"status": "filled", "selector": selector}
    
    def click(self, selector: str):
        """Click an element"""
        if not self.page:
            return {"error": "Browser not started"}
        self.page.click(selector)
        return {"status": "clicked", "selector": selector}
    
    def type_text(self, selector: str, text: str, delay: int = 50):
        """Type text with human-like delay"""
        if not self.page:
            return {"error": "Browser not started"}
        self.page.type(selector, text, delay=delay)
        return {"status": "typed", "selector": selector}
    
    def execute_js(self, script: str):
        """Execute JavaScript"""
        if not self.page:
            return {"error": "Browser not started"}
        result = self.page.evaluate(script)
        return {"status": "executed", "result": result}
    
    def get_page_content(self):
        """Get page HTML"""
        if not self.page:
            return {"error": "Browser not started"}
        return {
            "url": self.page.url,
            "title": self.page.title(),
            "html": self.page.content()
        }
    
    def get_storage(self):
        """Get localStorage and sessionStorage"""
        if not self.page:
            return {"error": "Browser not started"}
        local = self.page.evaluate("() => Object.fromEntries(Object.entries(localStorage))")
        session = self.page.evaluate("() => Object.fromEntries(Object.entries(sessionStorage))")
        return {"localStorage": local, "sessionStorage": session}
    
    def login_flow(self, url: str, username_selector: str, password_selector: str, 
                   username: str, password: str, submit_selector: str = None):
        """Automated login flow"""
        if not self.page:
            return {"error": "Browser not started"}
        
        self.page.goto(url, wait_until="domcontentloaded")
        self.page.fill(username_selector, username)
        self.page.fill(password_selector, password)
        
        if submit_selector:
            self.page.click(submit_selector)
        else:
            self.page.press(password_selector, "Enter")
        
        self.page.wait_for_load_state("networkidle")
        
        cookies = self.context.cookies()
        return {
            "status": "login_attempted",
            "final_url": self.page.url,
            "cookies": cookies
        }

# Global singleton instance
_browser = BrowserController()

def get_browser():
    return _browser
