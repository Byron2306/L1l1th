#!/usr/bin/env python3
"""
LILITH IMAGE GENERATOR - Multi-Provider System
===============================================
Uses multiple free HuggingFace spaces and APIs for reliable
high-quality anime image generation.

All images are "sexy clothed" - lingerie, swimsuits, suggestive poses.
NOT nude.
"""

import os
import time
import base64
import hashlib
import requests
from typing import Optional, List, Dict
import urllib.parse

# HuggingFace Inference API (free tier)
HF_TOKEN = os.environ.get("HF_TOKEN", "")  # Optional, works without token too

# Known working anime image generators
HUGGINGFACE_SPACES = [
    {
        "name": "Animagine XL 3.1",
        "url": "https://cagliostrolab-animagine-xl-3-1.hf.space/api/predict",
        "type": "gradio",
        "quality": "high"
    },
    {
        "name": "Counterfeit V3",
        "url": "https://gsdf-counterfeit-v30.hf.space/api/predict",
        "type": "gradio",
        "quality": "high"
    },
    {
        "name": "NovelAI Diffusion",
        "url": "https://novelai-anime.hf.space/api/predict",
        "type": "gradio",
        "quality": "high"
    }
]

# Direct inference API endpoints (more reliable)
INFERENCE_ENDPOINTS = [
    {
        "name": "Stable Diffusion XL",
        "model": "stabilityai/stable-diffusion-xl-base-1.0",
        "url": "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    },
    {
        "name": "Animagine XL",
        "model": "cagliostrolab/animagine-xl-3.1",
        "url": "https://api-inference.huggingface.co/models/cagliostrolab/animagine-xl-3.1"
    },
    {
        "name": "Waifu Diffusion",
        "model": "hakurei/waifu-diffusion",
        "url": "https://api-inference.huggingface.co/models/hakurei/waifu-diffusion"
    },
    {
        "name": "Anything V5",
        "model": "stablediffusionapi/anything-v5",
        "url": "https://api-inference.huggingface.co/models/stablediffusionapi/anything-v5"
    },
    {
        "name": "Dreamlike Anime",
        "model": "dreamlike-art/dreamlike-anime-1.0",
        "url": "https://api-inference.huggingface.co/models/dreamlike-art/dreamlike-anime-1.0"
    }
]

# LILITH character tags for consistency
LILITH_BASE_TAGS = "anime style, beautiful demoness, red glowing eyes, long flowing black hair, small elegant horns, demon wings, pale skin, seductive smile"

# Clothing/pose modifiers (NOT nude)
SEXY_CLOTHED_TAGS = [
    "black lace lingerie, elegant, seductive pose",
    "silk nightgown, bedroom setting, alluring",
    "bikini, beach setting, playful pose",
    "corset and stockings, gothic aesthetic",
    "tight dress, elegant pose, showing curves",
    "sheer robe, suggestive, romantic lighting",
    "leather outfit, dominant pose, confident",
    "maid outfit, teasing expression, cute and sexy"
]

# Negative prompt to ensure clothed
NEGATIVE_PROMPT = "nude, naked, nsfw, explicit, genitals, nipples exposed, completely nude, undressed, low quality, blurry, deformed"


class LilithImageGenerator:
    """
    Multi-provider image generator for LILITH.
    Generates sexy but clothed anime images.
    """
    
    def __init__(self):
        self.hf_token = HF_TOKEN
        self.last_provider = None
        self.cache = {}
    
    def generate_lilith_image(self, style: str = "seductive") -> Optional[bytes]:
        """
        Generate a LILITH character image.
        Returns image bytes or None if all providers fail.
        """
        import random
        
        # Build prompt with clothing
        clothing = random.choice(SEXY_CLOTHED_TAGS)
        prompt = f"{LILITH_BASE_TAGS}, {clothing}, masterpiece, best quality, highly detailed"
        
        return self.generate_image(prompt)
    
    def generate_image(self, prompt: str, ensure_clothed: bool = True) -> Optional[bytes]:
        """
        Generate an image from prompt.
        Tries multiple providers until one succeeds.
        """
        # Add quality tags if not present
        if "masterpiece" not in prompt.lower():
            prompt = f"{prompt}, masterpiece, best quality, highly detailed, anime style"
        
        # Ensure clothed content
        if ensure_clothed:
            prompt = f"{prompt}, clothed, wearing outfit"
        
        # Try AI Horde first (most reliable)
        result = self._try_ai_horde(prompt)
        if result:
            self.last_provider = "AI Horde"
            return result
        
        # Try HuggingFace Inference API
        for endpoint in INFERENCE_ENDPOINTS:
            result = self._try_hf_inference(endpoint, prompt)
            if result:
                self.last_provider = endpoint["name"]
                return result
        
        # Try Pollinations as last resort
        result = self._try_pollinations(prompt)
        if result:
            self.last_provider = "Pollinations"
            return result
        
        return None
    
    def _try_ai_horde(self, prompt: str) -> Optional[bytes]:
        """Try AI Horde (reliable, free)"""
        try:
            # Submit request
            resp = requests.post(
                "https://aihorde.net/api/v2/generate/async",
                json={
                    "prompt": prompt,
                    "params": {
                        "width": 768,
                        "height": 1024,
                        "steps": 30,
                        "sampler_name": "k_euler_a",
                        "cfg_scale": 7
                    },
                    "nsfw": False,  # Keep clothed
                    "censor_nsfw": True,
                    "r2": True
                },
                headers={
                    "Content-Type": "application/json",
                    "apikey": "0000000000"
                },
                timeout=30
            )
            
            if resp.status_code != 202:
                return None
            
            job_id = resp.json().get("id")
            if not job_id:
                return None
            
            # Poll for completion
            for _ in range(90):
                time.sleep(2)
                check = requests.get(
                    f"https://aihorde.net/api/v2/generate/check/{job_id}",
                    timeout=10
                )
                if check.status_code == 200:
                    status = check.json()
                    if status.get("done"):
                        # Get result
                        result = requests.get(
                            f"https://aihorde.net/api/v2/generate/status/{job_id}",
                            timeout=30
                        )
                        if result.status_code == 200:
                            gens = result.json().get("generations", [])
                            if gens and gens[0].get("img"):
                                img = gens[0]["img"]
                                if img.startswith("http"):
                                    img_resp = requests.get(img, timeout=30)
                                    if img_resp.status_code == 200:
                                        return img_resp.content
                                else:
                                    return base64.b64decode(img)
                        break
                        
        except Exception as e:
            print(f"[IMAGE] AI Horde error: {e}")
        
        return None
    
    def _try_hf_inference(self, endpoint: Dict, prompt: str) -> Optional[bytes]:
        """Try HuggingFace Inference API"""
        try:
            headers = {"Content-Type": "application/json"}
            if self.hf_token:
                headers["Authorization"] = f"Bearer {self.hf_token}"
            
            resp = requests.post(
                endpoint["url"],
                headers=headers,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "negative_prompt": NEGATIVE_PROMPT,
                        "num_inference_steps": 30,
                        "guidance_scale": 7.5
                    }
                },
                timeout=120
            )
            
            if resp.status_code == 200:
                # Response is image bytes directly
                if len(resp.content) > 1000:
                    return resp.content
                    
        except Exception as e:
            print(f"[IMAGE] HF {endpoint['name']} error: {e}")
        
        return None
    
    def _try_pollinations(self, prompt: str) -> Optional[bytes]:
        """Try Pollinations API (free)"""
        try:
            # Add SFW modifier
            safe_prompt = f"{prompt}, sfw, clothed"
            encoded = urllib.parse.quote(safe_prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=1024&nologo=true"
            
            resp = requests.get(url, timeout=90)
            if resp.status_code == 200 and len(resp.content) > 5000:
                return resp.content
                
        except Exception as e:
            print(f"[IMAGE] Pollinations error: {e}")
        
        return None
    
    def get_status(self) -> Dict:
        """Get generator status"""
        return {
            "providers_available": len(INFERENCE_ENDPOINTS) + 2,  # +AI Horde +Pollinations
            "last_provider": self.last_provider,
            "hf_token_set": bool(self.hf_token)
        }


# Singleton
_image_generator = None

def get_image_generator() -> LilithImageGenerator:
    global _image_generator
    if _image_generator is None:
        _image_generator = LilithImageGenerator()
    return _image_generator


if __name__ == "__main__":
    gen = get_image_generator()
    print("Status:", gen.get_status())
    
    print("Generating test image...")
    img = gen.generate_lilith_image()
    if img:
        print(f"Success! Generated {len(img)} bytes from {gen.last_provider}")
        with open("/tmp/lilith_test.png", "wb") as f:
            f.write(img)
        print("Saved to /tmp/lilith_test.png")
    else:
        print("All providers failed")
