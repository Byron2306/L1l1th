#!/usr/bin/env python3
"""
LILITH CAPTCHA Bypass Module
=============================
Multi-method CAPTCHA solving:
1. 2Captcha/Anti-Captcha API integration
2. Local ML-based OCR for simple CAPTCHAs
3. Audio CAPTCHA solver
4. reCAPTCHA v2/v3 bypass techniques
5. hCaptcha bypass
6. Cloudflare challenge bypass
"""

import os
import re
import json
import time
import base64
import random
import string
import asyncio
from typing import Dict, Optional, Tuple, List
from datetime import datetime
from pathlib import Path

# ML imports for local solving
try:
    import cv2
    import numpy as np
    from PIL import Image
    import io
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# 2Captcha integration
try:
    from twocaptcha import TwoCaptcha
    TWOCAPTCHA_AVAILABLE = True
except ImportError:
    TWOCAPTCHA_AVAILABLE = False


class CaptchaBypass:
    """Multi-method CAPTCHA bypass system"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('CAPTCHA_API_KEY', '')
        self.solver = None
        self.stats = {
            'solved': 0,
            'failed': 0,
            'methods_used': {}
        }
        
        if TWOCAPTCHA_AVAILABLE and self.api_key:
            self.solver = TwoCaptcha(self.api_key)
    
    async def solve_captcha(self, captcha_data: Dict) -> Dict:
        """
        Universal CAPTCHA solver
        
        captcha_data should contain:
        - type: 'image', 'recaptcha_v2', 'recaptcha_v3', 'hcaptcha', 'cloudflare', 'text'
        - image_base64: base64 encoded image (for image type)
        - site_key: site key for reCAPTCHA/hCaptcha
        - page_url: URL of the page
        - action: action for reCAPTCHA v3
        """
        captcha_type = captcha_data.get('type', 'image')
        
        methods = {
            'image': self._solve_image_captcha,
            'recaptcha_v2': self._solve_recaptcha_v2,
            'recaptcha_v3': self._solve_recaptcha_v3,
            'hcaptcha': self._solve_hcaptcha,
            'cloudflare': self._solve_cloudflare,
            'text': self._solve_text_captcha,
            'audio': self._solve_audio_captcha
        }
        
        solver = methods.get(captcha_type)
        if not solver:
            return {'success': False, 'error': f'Unknown CAPTCHA type: {captcha_type}'}
        
        try:
            result = await solver(captcha_data)
            if result.get('success'):
                self.stats['solved'] += 1
                self.stats['methods_used'][captcha_type] = self.stats['methods_used'].get(captcha_type, 0) + 1
            else:
                self.stats['failed'] += 1
            return result
        except Exception as e:
            self.stats['failed'] += 1
            return {'success': False, 'error': str(e)}
    
    async def _solve_image_captcha(self, data: Dict) -> Dict:
        """Solve image-based CAPTCHA"""
        image_data = data.get('image_base64', '')
        
        if not image_data:
            return {'success': False, 'error': 'No image data provided'}
        
        # Try local ML first (for simple CAPTCHAs)
        if ML_AVAILABLE:
            result = self._local_ocr_solve(image_data)
            if result.get('success') and result.get('confidence', 0) > 0.8:
                return result
        
        # Fall back to 2Captcha API
        if self.solver:
            try:
                result = self.solver.normal(image_data)
                return {
                    'success': True,
                    'solution': result['code'],
                    'method': '2captcha_api',
                    'captcha_id': result.get('captchaId')
                }
            except Exception as e:
                return {'success': False, 'error': f'2Captcha error: {str(e)}'}
        
        # If no API, try heuristic solving
        return self._heuristic_solve(image_data)
    
    async def _solve_recaptcha_v2(self, data: Dict) -> Dict:
        """Solve reCAPTCHA v2"""
        site_key = data.get('site_key', '')
        page_url = data.get('page_url', '')
        
        if not site_key or not page_url:
            return {'success': False, 'error': 'site_key and page_url required'}
        
        if self.solver:
            try:
                result = self.solver.recaptcha(
                    sitekey=site_key,
                    url=page_url,
                    invisible=data.get('invisible', False)
                )
                return {
                    'success': True,
                    'solution': result['code'],
                    'method': '2captcha_recaptcha_v2'
                }
            except Exception as e:
                return {'success': False, 'error': f'reCAPTCHA v2 error: {str(e)}'}
        
        # Fallback: Return bypass techniques
        return {
            'success': False,
            'error': 'No API key configured',
            'bypass_techniques': [
                'Use audio challenge instead',
                'Try browser fingerprint spoofing',
                'Implement token harvesting',
                'Use residential proxies'
            ]
        }
    
    async def _solve_recaptcha_v3(self, data: Dict) -> Dict:
        """Solve reCAPTCHA v3 (score-based)"""
        site_key = data.get('site_key', '')
        page_url = data.get('page_url', '')
        action = data.get('action', 'verify')
        min_score = data.get('min_score', 0.7)
        
        if not site_key or not page_url:
            return {'success': False, 'error': 'site_key and page_url required'}
        
        if self.solver:
            try:
                result = self.solver.recaptcha(
                    sitekey=site_key,
                    url=page_url,
                    version='v3',
                    action=action,
                    score=min_score
                )
                return {
                    'success': True,
                    'solution': result['code'],
                    'method': '2captcha_recaptcha_v3',
                    'score': min_score
                }
            except Exception as e:
                return {'success': False, 'error': f'reCAPTCHA v3 error: {str(e)}'}
        
        return {
            'success': False,
            'error': 'No API key configured',
            'bypass_techniques': [
                'Mimic human behavior patterns',
                'Use aged browser profiles',
                'Implement mouse movement simulation',
                'Add realistic timing delays'
            ]
        }
    
    async def _solve_hcaptcha(self, data: Dict) -> Dict:
        """Solve hCaptcha"""
        site_key = data.get('site_key', '')
        page_url = data.get('page_url', '')
        
        if not site_key or not page_url:
            return {'success': False, 'error': 'site_key and page_url required'}
        
        if self.solver:
            try:
                result = self.solver.hcaptcha(
                    sitekey=site_key,
                    url=page_url
                )
                return {
                    'success': True,
                    'solution': result['code'],
                    'method': '2captcha_hcaptcha'
                }
            except Exception as e:
                return {'success': False, 'error': f'hCaptcha error: {str(e)}'}
        
        return {
            'success': False,
            'error': 'No API key configured',
            'bypass_techniques': [
                'Use accessibility cookie',
                'Implement browser automation with human-like behavior',
                'Token harvesting from solved sessions'
            ]
        }
    
    async def _solve_cloudflare(self, data: Dict) -> Dict:
        """Bypass Cloudflare challenge"""
        page_url = data.get('page_url', '')
        
        if not page_url:
            return {'success': False, 'error': 'page_url required'}
        
        if self.solver:
            try:
                result = self.solver.turnstile(
                    sitekey=data.get('site_key', ''),
                    url=page_url
                )
                return {
                    'success': True,
                    'solution': result['code'],
                    'method': '2captcha_turnstile'
                }
            except Exception as e:
                pass
        
        # Return Cloudflare bypass techniques
        return {
            'success': False,
            'method': 'cloudflare_bypass_info',
            'techniques': {
                'browser_automation': {
                    'description': 'Use undetected-chromedriver or Playwright stealth',
                    'code': '''
from playwright.async_api import async_playwright
import asyncio

async def bypass_cloudflare(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Headed mode better
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        await page.goto(url)
        await page.wait_for_timeout(10000)  # Wait for challenge
        cookies = await context.cookies()
        return cookies
'''
                },
                'cookie_extraction': {
                    'description': 'Extract cf_clearance cookie after manual solve',
                    'cookies_needed': ['cf_clearance', '__cf_bm']
                },
                'flaresolverr': {
                    'description': 'Use FlareSolverr proxy service',
                    'docker': 'docker run -p 8191:8191 ghcr.io/flaresolverr/flaresolverr:latest'
                }
            }
        }
    
    async def _solve_text_captcha(self, data: Dict) -> Dict:
        """Solve text-based CAPTCHA (math, logic, etc.)"""
        question = data.get('question', '')
        
        if not question:
            return {'success': False, 'error': 'question required'}
        
        # Try to solve common patterns
        solution = self._solve_text_pattern(question)
        
        if solution:
            return {
                'success': True,
                'solution': solution,
                'method': 'pattern_matching'
            }
        
        # Fall back to API
        if self.solver:
            try:
                result = self.solver.text(question)
                return {
                    'success': True,
                    'solution': result['code'],
                    'method': '2captcha_text'
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        return {'success': False, 'error': 'Could not solve text CAPTCHA'}
    
    async def _solve_audio_captcha(self, data: Dict) -> Dict:
        """Solve audio CAPTCHA using speech recognition"""
        audio_data = data.get('audio_base64', '')
        
        if not audio_data:
            return {'success': False, 'error': 'audio_base64 required'}
        
        # Try speech recognition
        try:
            import speech_recognition as sr
            
            # Decode audio
            audio_bytes = base64.b64decode(audio_data)
            
            # Save temporarily
            temp_path = f'/tmp/captcha_audio_{int(time.time())}.wav'
            with open(temp_path, 'wb') as f:
                f.write(audio_bytes)
            
            # Recognize
            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_path) as source:
                audio = recognizer.record(source)
            
            text = recognizer.recognize_google(audio)
            os.remove(temp_path)
            
            return {
                'success': True,
                'solution': text,
                'method': 'speech_recognition'
            }
        except ImportError:
            return {
                'success': False,
                'error': 'speech_recognition not installed',
                'install': 'pip install SpeechRecognition'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _local_ocr_solve(self, image_base64: str) -> Dict:
        """Local OCR solving using OpenCV and image processing"""
        try:
            # Decode image
            image_data = base64.b64decode(image_base64)
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return {'success': False, 'error': 'Could not decode image'}
            
            # Preprocessing
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Thresholding
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Noise removal
            kernel = np.ones((1, 1), np.uint8)
            opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            # Try pytesseract if available
            try:
                import pytesseract
                text = pytesseract.image_to_string(opening, config='--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
                text = re.sub(r'[^a-zA-Z0-9]', '', text)
                
                if text:
                    return {
                        'success': True,
                        'solution': text,
                        'method': 'local_ocr',
                        'confidence': 0.7
                    }
            except ImportError:
                pass
            
            return {'success': False, 'error': 'OCR failed', 'confidence': 0}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _heuristic_solve(self, image_base64: str) -> Dict:
        """Heuristic solving for simple CAPTCHAs"""
        try:
            # Decode image
            image_data = base64.b64decode(image_base64)
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return {'success': False, 'error': 'Could not decode image'}
            
            # Analyze image characteristics
            height, width = img.shape[:2]
            
            # Character segmentation attempt
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
            
            # Find contours (potential characters)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            char_boxes = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 5 and h > 10:  # Filter noise
                    char_boxes.append((x, y, w, h))
            
            # Sort by x position
            char_boxes.sort(key=lambda b: b[0])
            
            return {
                'success': False,
                'error': 'Heuristic analysis only',
                'analysis': {
                    'image_size': f'{width}x{height}',
                    'detected_chars': len(char_boxes),
                    'char_positions': char_boxes[:10],
                    'recommendation': 'Use 2Captcha API for accurate solving'
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _solve_text_pattern(self, question: str) -> Optional[str]:
        """Solve common text CAPTCHA patterns"""
        question = question.lower().strip()
        
        # Math questions
        math_match = re.search(r'(\d+)\s*[\+\-\*\/x]\s*(\d+)', question)
        if math_match:
            a, b = int(math_match.group(1)), int(math_match.group(2))
            if '+' in question or 'plus' in question or 'add' in question:
                return str(a + b)
            elif '-' in question or 'minus' in question or 'subtract' in question:
                return str(a - b)
            elif '*' in question or 'x' in question or 'times' in question or 'multiply' in question:
                return str(a * b)
            elif '/' in question or 'divide' in question:
                return str(a // b) if b != 0 else None
        
        # Color questions
        if 'color' in question:
            colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'black', 'white']
            for color in colors:
                if color in question:
                    return color
        
        # Day/month questions
        if 'day' in question:
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for day in days:
                if day in question:
                    return day.capitalize()
        
        # Capital of country
        capitals = {
            'france': 'Paris', 'germany': 'Berlin', 'italy': 'Rome',
            'spain': 'Madrid', 'uk': 'London', 'japan': 'Tokyo',
            'china': 'Beijing', 'russia': 'Moscow', 'usa': 'Washington'
        }
        for country, capital in capitals.items():
            if country in question:
                return capital
        
        return None
    
    def get_stats(self) -> Dict:
        """Get solving statistics"""
        total = self.stats['solved'] + self.stats['failed']
        return {
            **self.stats,
            'total_attempts': total,
            'success_rate': self.stats['solved'] / total if total > 0 else 0
        }


class BrowserAutomationEnhanced:
    """Enhanced browser automation with anti-detection"""
    
    def __init__(self):
        self.captcha_solver = CaptchaBypass()
    
    async def stealth_browser_session(self, headless: bool = True) -> Dict:
        """Create stealth browser session with anti-detection"""
        try:
            from playwright.async_api import async_playwright
            
            playwright = await async_playwright().start()
            
            # Stealth browser arguments
            browser = await playwright.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process'
                ]
            )
            
            # Create context with realistic fingerprint
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
                geolocation={'latitude': 40.7128, 'longitude': -74.0060},
                permissions=['geolocation']
            )
            
            # Add stealth scripts
            await context.add_init_script('''
                // Override navigator properties
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                
                // Override chrome
                window.chrome = {runtime: {}};
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                    Promise.resolve({state: Notification.permission}) :
                    originalQuery(parameters)
                );
            ''')
            
            page = await context.new_page()
            
            return {
                'success': True,
                'browser': browser,
                'context': context,
                'page': page,
                'playwright': playwright
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def human_like_interaction(self, page, actions: List[Dict]) -> Dict:
        """Perform human-like interactions"""
        results = []
        
        for action in actions:
            action_type = action.get('type', '')
            
            if action_type == 'move_mouse':
                # Random mouse movements
                for _ in range(random.randint(2, 5)):
                    x = random.randint(100, 1800)
                    y = random.randint(100, 900)
                    await page.mouse.move(x, y, steps=random.randint(10, 30))
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                results.append({'action': 'move_mouse', 'success': True})
                
            elif action_type == 'type':
                selector = action.get('selector', '')
                text = action.get('text', '')
                
                await page.click(selector)
                await asyncio.sleep(random.uniform(0.2, 0.5))
                
                # Type with human-like delays
                for char in text:
                    await page.keyboard.type(char, delay=random.randint(50, 150))
                    
                results.append({'action': 'type', 'success': True})
                
            elif action_type == 'click':
                selector = action.get('selector', '')
                
                # Move to element first
                element = await page.query_selector(selector)
                if element:
                    box = await element.bounding_box()
                    if box:
                        # Random point within element
                        x = box['x'] + random.uniform(5, box['width'] - 5)
                        y = box['y'] + random.uniform(5, box['height'] - 5)
                        await page.mouse.move(x, y, steps=random.randint(5, 15))
                        await asyncio.sleep(random.uniform(0.1, 0.3))
                        await page.mouse.click(x, y)
                        results.append({'action': 'click', 'success': True})
                    else:
                        results.append({'action': 'click', 'success': False, 'error': 'No bounding box'})
                else:
                    results.append({'action': 'click', 'success': False, 'error': 'Element not found'})
                    
            elif action_type == 'wait':
                duration = action.get('duration', 1000)
                # Add randomness to wait
                actual_wait = duration + random.randint(-200, 200)
                await page.wait_for_timeout(max(100, actual_wait))
                results.append({'action': 'wait', 'success': True})
                
            elif action_type == 'scroll':
                direction = action.get('direction', 'down')
                amount = action.get('amount', 300)
                
                for _ in range(random.randint(2, 4)):
                    scroll_amount = amount + random.randint(-50, 50)
                    if direction == 'down':
                        await page.mouse.wheel(0, scroll_amount)
                    else:
                        await page.mouse.wheel(0, -scroll_amount)
                    await asyncio.sleep(random.uniform(0.2, 0.5))
                    
                results.append({'action': 'scroll', 'success': True})
        
        return {'success': True, 'results': results}


# Export
def get_captcha_bypass(api_key: str = None) -> CaptchaBypass:
    return CaptchaBypass(api_key)

def get_enhanced_automation() -> BrowserAutomationEnhanced:
    return BrowserAutomationEnhanced()
