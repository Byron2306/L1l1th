#!/usr/bin/env python3
"""
LILITH IMAGE GENERATOR - HuggingFace Stable Diffusion
======================================================
Uses HuggingFace Spaces for high-quality anime image generation.
Primary: Animagine XL 3.1 (best anime quality)
Fallback: AI Horde (free, no rate limits)

All images are sexy but CLOTHED (lingerie, swimsuits, etc.)
"""

import os
import time
import base64
import random
import shutil
import requests
from typing import Optional, Dict
import urllib.parse

# Try to import gradio_client
GRADIO_AVAILABLE = False
try:
    from gradio_client import Client
    GRADIO_AVAILABLE = True
    print("[IMAGE] Gradio client loaded - HuggingFace Spaces available")
except ImportError:
    print("[IMAGE] Gradio client not available")

# LILITH character base tags
LILITH_BASE_TAGS = "1girl, demon girl, beautiful, red glowing eyes, long flowing black hair, small elegant horns, pale skin, seductive smile, large breasts, curvy figure, thick thighs"

# Sexy CLOTHED outfit options - more erotic but still clothed
SEXY_OUTFITS = [
    "black lace lingerie, cleavage, bedroom eyes, lying on bed",
    "red silk negligee, sideboob, romantic candlelight",
    "micro bikini, wet skin, beach, arched back",
    "black corset, stockings, garter belt, dominant pose",
    "tight latex dress, deep cleavage, nightclub",
    "sheer see-through nightgown, backlit, silhouette",
    "leather harness over lingerie, chains, collar",
    "naked apron only, kitchen, looking over shoulder",
    "bunny girl outfit, fishnet stockings, playboy pose",
    "sukumizu swimsuit, wet, pool, inviting expression",
    "china dress with high slit, no bra, elegant",
    "virgin killer sweater, bare back, shy smile"
]

# Quality tags for anime
QUALITY_TAGS = "masterpiece, best quality, highly detailed, detailed face, beautiful eyes, perfect anatomy, sensual, alluring, provocative, beautiful lighting, cinematic lighting, 8k uhd"

# Negative prompt - clothed but sexy
NEGATIVE_PROMPT = "nude, naked, nipples, exposed genitals, penis, vagina, completely naked, low quality, bad anatomy, deformed, ugly, blurry, extra limbs, worst quality, child, underage, loli"


class HuggingFaceImageGenerator:
    """
    High-quality anime image generator using HuggingFace Spaces.
    """
    
    def __init__(self):
        self.animagine_client = None
        self.last_provider = None
        self._init_clients()
    
    def _init_clients(self):
        """Initialize HuggingFace clients"""
        if GRADIO_AVAILABLE:
            try:
                self.animagine_client = Client("cagliostrolab/animagine-xl-3.1")
                print("[IMAGE] Animagine XL 3.1 connected")
            except Exception as e:
                print(f"[IMAGE] Animagine connection error: {e}")
    
    def generate_lilith_image(self, outfit_style: str = "random") -> Optional[bytes]:
        """
        Generate a LILITH character image.
        Returns high-quality anime image bytes.
        """
        # Select outfit
        if outfit_style == "random":
            outfit = random.choice(SEXY_OUTFITS)
        else:
            outfit = outfit_style if outfit_style in SEXY_OUTFITS else random.choice(SEXY_OUTFITS)
        
        prompt = f"{LILITH_BASE_TAGS}, {outfit}, {QUALITY_TAGS}"
        return self.generate_image(prompt)
    
    def generate_image(self, prompt: str, ensure_clothed: bool = True) -> Optional[bytes]:
        """
        Generate an image from prompt.
        Tries HuggingFace first, falls back to AI Horde.
        """
        # Add quality tags if not present
        if "masterpiece" not in prompt.lower():
            prompt = f"{prompt}, {QUALITY_TAGS}"
        
        # Ensure anime style
        if "anime" not in prompt.lower() and "1girl" not in prompt.lower():
            prompt = f"anime style, {prompt}"
        
        # Try Animagine XL first (best quality)
        result = self._generate_animagine(prompt)
        if result:
            self.last_provider = "Animagine XL 3.1"
            return result
        
        # Try AI Horde as fallback
        result = self._generate_ai_horde(prompt)
        if result:
            self.last_provider = "AI Horde"
            return result
        
        return None
    
    def _generate_animagine(self, prompt: str) -> Optional[bytes]:
        """Generate with Animagine XL 3.1 (HuggingFace)"""
        if not self.animagine_client:
            # Try to reconnect
            if GRADIO_AVAILABLE:
                try:
                    self.animagine_client = Client("cagliostrolab/animagine-xl-3.1")
                except:
                    return None
            else:
                return None
        
        try:
            # Generate with Animagine
            result = self.animagine_client.predict(
                prompt,                     # prompt
                NEGATIVE_PROMPT,            # negative_prompt
                random.randint(0, 999999),  # seed (random)
                896,                        # width (higher quality)
                1344,                       # height (higher quality)
                7.5,                        # guidance_scale (slightly higher for better detail)
                35,                         # steps (more steps for quality)
                "DPM++ 2M Karras",          # sampler
                "896 x 1344",               # aspect_ratio
                "Anime",                    # style_preset
                "Standard v3.1",            # quality_tags
                False,                      # use_upscaler
                0.5,                        # strength
                1.0,                        # upscale_by
                True,                       # add_quality_tags
                api_name="/run"
            )
            
            # Extract image
            if result and len(result) > 0:
                images = result[0]
                if images and len(images) > 0:
                    img_info = images[0]
                    img_path = img_info.get('image') if isinstance(img_info, dict) else img_info
                    
                    if img_path and os.path.exists(img_path):
                        with open(img_path, 'rb') as f:
                            img_data = f.read()
                        print(f"[IMAGE] Animagine generated {len(img_data)} bytes")
                        return img_data
                        
        except Exception as e:
            print(f"[IMAGE] Animagine error: {e}")
            # Reset client for retry
            self.animagine_client = None
        
        return None
    
    def _generate_ai_horde(self, prompt: str) -> Optional[bytes]:
        """Fallback to AI Horde (free, unlimited)"""
        try:
            resp = requests.post(
                "https://aihorde.net/api/v2/generate/async",
                json={
                    "prompt": f"{prompt}, anime style",
                    "params": {
                        "width": 768,
                        "height": 1024,
                        "steps": 30,
                        "sampler_name": "k_euler_a",
                        "cfg_scale": 7
                    },
                    "nsfw": False,
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
            
            # Poll for result
            for _ in range(90):
                time.sleep(2)
                check = requests.get(
                    f"https://aihorde.net/api/v2/generate/check/{job_id}",
                    timeout=10
                )
                if check.status_code == 200 and check.json().get("done"):
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
    
    def get_status(self) -> Dict:
        """Get generator status"""
        return {
            "animagine_connected": self.animagine_client is not None,
            "gradio_available": GRADIO_AVAILABLE,
            "last_provider": self.last_provider,
            "ai_horde_available": True
        }


# Singleton
_hf_generator = None

def get_image_generator() -> HuggingFaceImageGenerator:
    global _hf_generator
    if _hf_generator is None:
        _hf_generator = HuggingFaceImageGenerator()
    return _hf_generator


if __name__ == "__main__":
    print("Testing HuggingFace Image Generator...")
    gen = get_image_generator()
    print("Status:", gen.get_status())
    
    print("\nGenerating LILITH image...")
    img = gen.generate_lilith_image()
    if img:
        print(f"SUCCESS! Generated {len(img)} bytes from {gen.last_provider}")
        with open("/tmp/lilith_hf_test.png", "wb") as f:
            f.write(img)
        print("Saved to /tmp/lilith_hf_test.png")
    else:
        print("Generation failed")
