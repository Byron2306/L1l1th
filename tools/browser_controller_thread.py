"""
LILITH Browser Controller - Thread-safe version
Uses a dedicated browser thread to avoid Playwright's threading restrictions
"""

import os
import threading
import queue
from pathlib import Path
from playwright.sync_api import sync_playwright

class BrowserControllerThread:
    """Thread-safe browser controller using a dedicated browser thread"""
    
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
        
        self.profile_path = Path.home() / '.lucifera' / 'browser_profile'
        self.profile_path.mkdir(parents=True, exist_ok=True)
        self.screenshots_path = Path.home() / '.lucifera' / 'screenshots'
        self.screenshots_path.mkdir(parents=True, exist_ok=True)
        
        # Browser thread management
        self._thread = None
        self._command_queue = queue.Queue()
        self._result_queue = queue.Queue()
        self._running = False
        self._browser_ready = threading.Event()
        
        # Playwright objects (only accessed from browser thread)
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._headless = False
    
    def _browser_thread_loop(self):
        """Main loop running in the browser thread"""
        try:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_path),
                headless=self._headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process'
                ]
            )
            self._page = self._browser.pages[0] if self._browser.pages else self._browser.new_page()
            self._browser_ready.set()
            
            while self._running:
                try:
                    cmd = self._command_queue.get(timeout=0.5)
                    if cmd is None:
                        break
                    method, args, kwargs = cmd
                    try:
                        result = method(*args, **kwargs)
                        self._result_queue.put(('ok', result))
                    except Exception as e:
                        self._result_queue.put(('error', str(e)))
                except queue.Empty:
                    continue
        except Exception as e:
            self._browser_ready.set()  # Unblock any waiters
            print(f"[BROWSER THREAD ERROR] {e}")
        finally:
            self._cleanup_browser()
    
    def _cleanup_browser(self):
        """Clean up browser resources (called from browser thread)"""
        try:
            if self._browser:
                self._browser.close()
        except:
            pass
        try:
            if self._playwright:
                self._playwright.stop()
        except:
            pass
        self._browser = None
        self._context = None
        self._page = None
        self._playwright = None
    
    def _execute(self, method, *args, **kwargs):
        """Execute a method in the browser thread and wait for result"""
        if not self._running or not self._thread or not self._thread.is_alive():
            return {'status': 'error', 'error': 'Browser not started'}
        
        self._command_queue.put((method, args, kwargs))
        try:
            status, result = self._result_queue.get(timeout=60)
            if status == 'error':
                return {'status': 'error', 'error': result}
            return result
        except queue.Empty:
            return {'status': 'error', 'error': 'Operation timed out'}
    
    def start(self, headless=False):
        """Start browser in dedicated thread"""
        if self._running and self._thread and self._thread.is_alive():
            return {'status': 'already_running', 'headless': self._headless}
        
        self._headless = headless
        self._running = True
        self._browser_ready.clear()
        
        self._thread = threading.Thread(target=self._browser_thread_loop, daemon=True)
        self._thread.start()
        
        # Wait for browser to be ready
        if not self._browser_ready.wait(timeout=30):
            return {'status': 'error', 'error': 'Browser startup timed out'}
        
        return {'status': 'started', 'headless': headless}
    
    def stop(self):
        """Stop browser and thread"""
        if not self._running:
            return {'status': 'not_running'}
        
        self._running = False
        self._command_queue.put(None)  # Signal thread to exit
        
        if self._thread:
            self._thread.join(timeout=10)
        
        return {'status': 'stopped'}
    
    # Browser operations (executed in browser thread)
    
    def _do_navigate(self, url):
        """Navigate to URL"""
        self._page.goto(url, wait_until='domcontentloaded', timeout=30000)
        return {
            'status': 'navigated',
            'url': self._page.url,
            'title': self._page.title()
        }
    
    def navigate(self, url):
        return self._execute(self._do_navigate, url)
    
    def _do_screenshot(self, path=None):
        """Take screenshot"""
        if path is None:
            import time
            path = str(self.screenshots_path / f"screenshot_{int(time.time())}.png")
        self._page.screenshot(path=path, full_page=True)
        return {'status': 'captured', 'path': path}
    
    def screenshot(self, path=None):
        return self._execute(self._do_screenshot, path)
    
    def _do_get_cookies(self, domain=None):
        """Get all cookies, optionally filtered by domain"""
        cookies = self._browser.cookies()
        if domain:
            cookies = [c for c in cookies if domain in c.get('domain', '')]
        return {'status': 'success', 'cookies': cookies, 'count': len(cookies)}
    
    def get_cookies(self, domain=None):
        return self._execute(self._do_get_cookies, domain)
    
    def _do_set_cookies(self, cookies):
        """Set cookies"""
        self._browser.add_cookies(cookies)
        return {'status': 'cookies_set', 'count': len(cookies)}
    
    def set_cookies(self, cookies):
        return self._execute(self._do_set_cookies, cookies)
    
    def _do_fill_form(self, selector, value):
        """Fill form field"""
        self._page.fill(selector, value)
        return {'status': 'filled', 'selector': selector}
    
    def fill_form(self, selector, value):
        return self._execute(self._do_fill_form, selector, value)
    
    def _do_click(self, selector):
        """Click element"""
        self._page.click(selector)
        return {'status': 'clicked', 'selector': selector}
    
    def click(self, selector):
        return self._execute(self._do_click, selector)
    
    def _do_execute_js(self, script):
        """Execute JavaScript - wraps in function if needed"""
        # If script contains 'return' at top level, wrap it in a function
        if script.strip().startswith('return ') or '\nreturn ' in script or 'return ' in script:
            script = f"() => {{ {script} }}"
        result = self._page.evaluate(script)
        return {'status': 'executed', 'result': result}
    
    def execute_js(self, script):
        return self._execute(self._do_execute_js, script)
    
    def _do_get_page_content(self):
        """Get page HTML content"""
        content = self._page.content()
        return {
            'status': 'success',
            'url': self._page.url,
            'title': self._page.title(),
            'content': content[:50000]  # Limit size
        }
    
    def get_page_content(self):
        return self._execute(self._do_get_page_content)
    
    def _do_get_storage(self):
        """Get localStorage and sessionStorage"""
        local = self._page.evaluate("() => Object.assign({}, localStorage)")
        session = self._page.evaluate("() => Object.assign({}, sessionStorage)")
        return {
            'status': 'success',
            'localStorage': local,
            'sessionStorage': session
        }
    
    def get_storage(self):
        return self._execute(self._do_get_storage)
    
    def _do_login_flow(self, url, username_sel, password_sel, username, password, submit_sel=None):
        """Automated login flow"""
        self._page.goto(url, wait_until='domcontentloaded')
        self._page.fill(username_sel, username)
        self._page.fill(password_sel, password)
        
        if submit_sel:
            self._page.click(submit_sel)
        else:
            self._page.press(password_sel, 'Enter')
        
        self._page.wait_for_load_state('networkidle', timeout=15000)
        
        cookies = self._browser.cookies()
        return {
            'status': 'login_attempted',
            'url': self._page.url,
            'title': self._page.title(),
            'cookies': cookies
        }
    
    def login_flow(self, url, username_sel, password_sel, username, password, submit_sel=None):
        return self._execute(self._do_login_flow, url, username_sel, password_sel, username, password, submit_sel)


# Global singleton
_browser_instance = None

def get_browser():
    """Get the singleton browser controller"""
    global _browser_instance
    if _browser_instance is None:
        _browser_instance = BrowserControllerThread()
    return _browser_instance
