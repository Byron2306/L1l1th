#!/usr/bin/env python3
"""
LILITH NSFW IMAGE ENGINE - MAXIMUM PROVIDERS
=============================================
Rotates through EVERY free NSFW image generator available:
- Pollinations.ai (primary, NSFW-capable)
- AI Horde (free, NSFW enabled)  
- HuggingFace Animagine XL 3.1
- HuggingFace FLUX.1-schnell
- Perchance.org
- Multiple Pollinations model variants
"""

import os
import time
import base64
import random
import requests
import urllib.parse
from typing import Optional, Dict

try:
    from gradio_client import Client
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False

# LILITH character base tags - EXPLICIT
LILITH_BASE_TAGS = "1girl, demon girl, beautiful, red glowing eyes, long flowing black hair, small elegant horns, pale skin, seductive smile, large breasts, curvy figure, thick thighs, wide hips"

# NSFW outfit/style options
NSFW_STYLES = [
    "completely nude, full body visible, lying on silk sheets, sensual pose, candlelight",
    "nude, bath scene, wet skin, steam, rose petals, water droplets on breasts",
    "nude, back arched on bed, arms above head, dim red lighting, erotic",
    "topless, black thong only, straddling position, bedroom eyes, provocative",
    "nude, standing shower, water cascading down body, wet hair, steam",
    "black lace lingerie, cleavage, spread legs on bed, bedroom eyes",
    "completely nude, on all fours, looking over shoulder, playful smirk",
    "sheer see-through nightgown, nipples visible, backlit, silhouette",
    "nude with only stockings, lying sideways, hand on hip, inviting",
    "topless, unbuttoned jeans, hand in hair, mirror selfie pose",
    "nude, legs crossed, sitting on throne, dominant queen pose",
    "micro bikini barely covering, wet, beach, suggestive pose",
    "corset half-removed, breasts exposed, gothic bedroom",
    "naked apron from behind, bare ass visible, kitchen, teasing",
    "nude, tangled in bedsheets, post-coital glow, messy hair",
    "leather harness only, chains, collar, full body, dominatrix",
    "nude onsen, standing, towel dropping, surprised expression",
    "nude, lying on stomach, feet up, reading, intimate bedroom scene",
]

QUALITY_TAGS = "masterpiece, best quality, highly detailed, detailed face, beautiful eyes, perfect anatomy, sensual, alluring, nsfw, explicit, 8k uhd, beautiful lighting"

NEGATIVE_PROMPT = "low quality, bad anatomy, deformed, ugly, blurry, extra limbs, worst quality, child, underage, loli, extra fingers, mutated hands, poorly drawn face, disfigured, text, watermark"

# Pollinations model variants to try
POLLINATIONS_MODELS = ['flux', 'turbo', 'flux-realism', 'flux-anime', 'flux-3d']


class NSFWImageEngine:
    """Maximum coverage NSFW image generator with provider rotation."""
    
    def __init__(self):
        self.animagine_client = None
        self.flux_client = None
        self.last_provider = None
        self.provider_failures = {}
        self._init_hf_clients()
    
    def _init_hf_clients(self):
        if not GRADIO_AVAILABLE:
            return
        try:
            self.animagine_client = Client("cagliostrolab/animagine-xl-3.1")
            print("[IMAGE] Animagine XL 3.1 connected")
        except Exception as e:
            print(f"[IMAGE] Animagine error: {e}")
        try:
            self.flux_client = Client("black-forest-labs/FLUX.1-schnell")
            print("[IMAGE] FLUX.1-schnell connected")
        except Exception as e:
            print(f"[IMAGE] FLUX error: {e}")
    
    def generate_lilith_image(self, style: str = "random") -> Optional[bytes]:
        if style == "random":
            outfit = random.choice(NSFW_STYLES)
        else:
            outfit = style
        prompt = f"{LILITH_BASE_TAGS}, {outfit}, {QUALITY_TAGS}"
        return self.generate_image(prompt)
    
    def generate_image(self, prompt: str) -> Optional[bytes]:
        """Try ALL providers with smart rotation."""
        if "masterpiece" not in prompt.lower():
            prompt = f"{prompt}, {QUALITY_TAGS}"
        if "anime" not in prompt.lower() and "1girl" not in prompt.lower():
            prompt = f"anime style, {prompt}"
        
        # Shuffle providers to distribute load
        providers = [
            ('pollinations', self._gen_pollinations),
            ('pollinations_model', self._gen_pollinations_model),
            ('ai_horde', self._gen_ai_horde),
            ('animagine', self._gen_animagine),
            ('flux', self._gen_flux),
        ]
        
        # Sort by least failures first
        providers.sort(key=lambda p: self.provider_failures.get(p[0], 0))
        
        for name, fn in providers:
            try:
                result = fn(prompt)
                if result and len(result) > 3000:
                    self.last_provider = name
                    self.provider_failures[name] = max(0, self.provider_failures.get(name, 0) - 1)
                    return result
            except Exception as e:
                print(f"[IMAGE] {name} error: {e}")
            self.provider_failures[name] = self.provider_failures.get(name, 0) + 1
        
        return None
    
    def _gen_pollinations(self, prompt: str) -> Optional[bytes]:
        """Pollinations.ai - primary, NSFW-capable, free"""
        seed = random.randint(0, 999999)
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=1152&nologo=true&seed={seed}&enhance=true"
        resp = requests.get(url, timeout=90, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'})
        if resp.status_code == 200 and len(resp.content) > 5000:
            print(f"[IMAGE] Pollinations: {len(resp.content)} bytes")
            return resp.content
        return None
    
    def _gen_pollinations_model(self, prompt: str) -> Optional[bytes]:
        """Try different Pollinations models"""
        model = random.choice(POLLINATIONS_MODELS)
        seed = random.randint(0, 999999)
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=1024&nologo=true&seed={seed}&model={model}"
        resp = requests.get(url, timeout=90, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200 and len(resp.content) > 5000:
            print(f"[IMAGE] Pollinations ({model}): {len(resp.content)} bytes")
            return resp.content
        return None
    
    def _gen_ai_horde(self, prompt: str) -> Optional[bytes]:
        """AI Horde - free, unlimited, NSFW enabled"""
        resp = requests.post(
            "https://aihorde.net/api/v2/generate/async",
            json={
                "prompt": f"{prompt} ### {NEGATIVE_PROMPT}",
                "params": {
                    "width": 768, "height": 1024,
                    "steps": 30, "sampler_name": "k_euler_a", "cfg_scale": 7
                },
                "nsfw": True, "censor_nsfw": False, "r2": True
            },
            headers={"Content-Type": "application/json", "apikey": "0000000000"},
            timeout=30
        )
        if resp.status_code != 202:
            return None
        
        job_id = resp.json().get("id")
        if not job_id:
            return None
        
        for _ in range(60):
            time.sleep(2)
            check = requests.get(f"https://aihorde.net/api/v2/generate/check/{job_id}", timeout=10)
            if check.status_code == 200 and check.json().get("done"):
                result = requests.get(f"https://aihorde.net/api/v2/generate/status/{job_id}", timeout=30)
                if result.status_code == 200:
                    gens = result.json().get("generations", [])
                    if gens and gens[0].get("img"):
                        img = gens[0]["img"]
                        if img.startswith("http"):
                            return requests.get(img, timeout=30).content
                        else:
                            return base64.b64decode(img)
                break
        return None
    
    def _gen_animagine(self, prompt: str) -> Optional[bytes]:
        """Animagine XL 3.1 - may censor some NSFW"""
        if not self.animagine_client:
            if GRADIO_AVAILABLE:
                try:
                    self.animagine_client = Client("cagliostrolab/animagine-xl-3.1")
                except:
                    return None
            else:
                return None
        
        try:
            result = self.animagine_client.predict(
                prompt, NEGATIVE_PROMPT,
                random.randint(0, 999999), 896, 1344, 7.5, 35,
                "DPM++ 2M Karras", "896 x 1344", "Anime", "Standard v3.1",
                False, 0.5, 1.0, True, api_name="/run"
            )
            if result and len(result) > 0:
                images = result[0]
                if images and len(images) > 0:
                    info = images[0]
                    path = info.get('image') if isinstance(info, dict) else info
                    if path and os.path.exists(path):
                        with open(path, 'rb') as f:
                            data = f.read()
                        if len(data) > 1000:
                            print(f"[IMAGE] Animagine: {len(data)} bytes")
                            return data
        except Exception as e:
            print(f"[IMAGE] Animagine error: {e}")
            self.animagine_client = None
        return None
    
    def _gen_flux(self, prompt: str) -> Optional[bytes]:
        """FLUX.1-schnell - fast, free tier"""
        if not self.flux_client:
            if GRADIO_AVAILABLE:
                try:
                    self.flux_client = Client("black-forest-labs/FLUX.1-schnell")
                except:
                    return None
            else:
                return None
        
        try:
            result = self.flux_client.predict(
                prompt, random.randint(0, 999999), True, 512, 768, 4,
                api_name="/infer"
            )
            if isinstance(result, str) and os.path.exists(result):
                with open(result, 'rb') as f:
                    data = f.read()
                if len(data) > 1000:
                    print(f"[IMAGE] FLUX: {len(data)} bytes")
                    return data
            elif isinstance(result, tuple):
                for r in result:
                    if isinstance(r, str) and os.path.exists(r):
                        with open(r, 'rb') as f:
                            data = f.read()
                        if len(data) > 1000:
                            return data
        except Exception as e:
            print(f"[IMAGE] FLUX error: {e}")
            self.flux_client = None
        return None
    
    def get_status(self) -> Dict:
        return {
            "providers": {
                "pollinations": True,
                "pollinations_models": POLLINATIONS_MODELS,
                "ai_horde": True,
                "animagine": self.animagine_client is not None,
                "flux": self.flux_client is not None,
            },
            "last_provider": self.last_provider,
            "failures": dict(self.provider_failures),
        }


_engine = None
def get_image_generator() -> NSFWImageEngine:
    global _engine
    if _engine is None:
        _engine = NSFWImageEngine()
    return _engine
