#!/usr/bin/env python3
"""
LILITH IMAGE GENERATOR v2 - High Quality Anime Art
====================================================
Uses HuggingFace Spaces (Animagine XL 3.1) with heavily refined prompts.
Fallback: AI Horde, Pollinations.
Priority: quality > speed. Strong negative prompts to prevent warping.
"""

import os
import time
import base64
import random
import requests
from typing import Optional, Dict

GRADIO_AVAILABLE = False
try:
    from gradio_client import Client
    GRADIO_AVAILABLE = True
    print("[IMAGE v2] Gradio client loaded")
except ImportError:
    print("[IMAGE v2] Gradio client not available")

# ============================================================
# CHARACTER DEFINITION
# ============================================================
LILITH_BASE = (
    "1girl, solo, demon girl, beautiful detailed face, "
    "red glowing eyes, long flowing black hair, small elegant horns, "
    "pale porcelain skin, seductive smile, large breasts, curvy figure, "
    "thick thighs, sharp features, dark fantasy"
)

# Sexy CLOTHED outfits — each carefully crafted for quality
# Named outfits — each is an ID -> full prompt fragment.
# Category tags let the UI group them (lingerie / swimwear / boudoir / themed).
OUTFITS: Dict[str, Dict[str, str]] = {
    "black_lace_lingerie":  {"category": "lingerie",  "label": "Black lace lingerie on silk bed",     "prompt": "black lace lingerie, cleavage, bedroom eyes, lying on silk bed, rose petals, dim candlelight"},
    "red_silk_negligee":    {"category": "boudoir",   "label": "Red silk negligee, wine & candles",   "prompt": "red silk negligee, sideboob, romantic atmosphere, wine glass nearby, soft lighting"},
    "black_corset":         {"category": "lingerie",  "label": "Black corset + garter + thigh-highs", "prompt": "black corset with lace trim, thigh-high stockings, garter belt, dominant confident pose"},
    "sheer_nightgown":      {"category": "boudoir",   "label": "Sheer nightgown, moonlight",          "prompt": "sheer see-through nightgown, backlit silhouette, moonlight through window, mysterious"},
    "leather_harness":      {"category": "lingerie",  "label": "Leather harness over lingerie",       "prompt": "leather harness over black lingerie, choker with gem, chains, dark dungeon aesthetic"},
    "bunny_girl":            {"category": "themed",    "label": "Bunny girl + fishnets",               "prompt": "bunny girl outfit, black fishnet stockings, bow tie, playful teasing pose"},
    "china_dress":          {"category": "themed",    "label": "China dress, high slit",              "prompt": "china dress with very high slit, elegant standing pose, lanterns"},
    "virgin_killer_sweater":{"category": "themed",    "label": "Virgin killer sweater",               "prompt": "virgin killer sweater, bare back exposed, looking over shoulder with shy smile"},
    "micro_bikini_beach":   {"category": "swimwear",  "label": "Micro bikini, beach sunset",          "prompt": "micro bikini, wet glistening skin, beach sunset, arched back, water droplets"},
    "classic_bikini_pool":  {"category": "swimwear",  "label": "Classic bikini poolside",             "prompt": "classic string bikini, poolside, wet hair, sunlight, glistening skin, playful smile"},
    "highwaist_bikini":     {"category": "swimwear",  "label": "High-waist retro bikini",             "prompt": "high-waist retro bikini, cat-eye sunglasses, tropical beach, vintage pin-up pose"},
    "monokini":             {"category": "swimwear",  "label": "Cutout monokini",                     "prompt": "black cutout monokini, standing at the water's edge, wet skin, golden hour lighting"},
    "wet_shirt_pool":       {"category": "swimwear",  "label": "Wet white shirt poolside",            "prompt": "wet see-through white shirt over bikini, poolside, water droplets, sunlit"},
    "apron_kitchen":        {"category": "themed",    "label": "Apron in morning kitchen",            "prompt": "wearing only a frilly apron over lingerie, kitchen setting, looking over shoulder, morning light, domestic"},
    "latex_bodysuit":       {"category": "lingerie",  "label": "Latex bodysuit, neon nightclub",      "prompt": "tight latex bodysuit, deep zipper cleavage, nightclub neon lighting, confident"},
    "bridal_lingerie":      {"category": "boudoir",   "label": "Bridal lingerie, white lace",         "prompt": "bridal lingerie, white lace, veil, wedding night atmosphere, blushing"},
    "silk_robe":            {"category": "boudoir",   "label": "Open silk robe, morning",             "prompt": "open silk robe over matching lingerie set, morning light, coffee cup, relaxed"},
    "gym_activewear":       {"category": "themed",    "label": "Sporty activewear",                   "prompt": "tight sports bra and yoga leggings, gym setting, athletic pose, healthy glow"},
}


def _outfit_prompt(outfit: Optional[str]) -> str:
    """Resolve an outfit ID (or 'random', or None) to a prompt fragment."""
    if not outfit or outfit == "random":
        return random.choice(list(OUTFITS.values()))["prompt"]
    entry = OUTFITS.get(outfit)
    if entry:
        return entry["prompt"]
    # Allow free-form outfit strings too
    return outfit

# Quality boosters
QUALITY_POSITIVE = (
    "masterpiece, best quality, extremely detailed, "
    "beautiful detailed eyes, intricate details, "
    "perfect lighting, professional illustration, "
    "sharp focus, vibrant colors, high contrast, "
    "anime style, detailed skin texture"
)

# STRONG negative prompt to prevent warping/deformation
QUALITY_NEGATIVE = (
    "lowres, bad anatomy, bad hands, text, error, missing fingers, "
    "extra digit, fewer digits, cropped, worst quality, low quality, "
    "normal quality, jpeg artifacts, signature, watermark, username, "
    "blurry, bad feet, mutated, deformed, ugly, duplicate, "
    "morbid, mutilated, extra fingers, fused fingers, too many fingers, "
    "long neck, poorly drawn hands, poorly drawn feet, poorly drawn face, "
    "out of frame, extra limbs, disfigured, gross proportions, "
    "malformed limbs, missing arms, missing legs, extra arms, extra legs, "
    "bad proportions, cross-eyed, body out of frame, "
    "3d, render, cgi, doll, cartoon, low detail, "
    "monochrome, flat color, sketch, simple background, "
    "child, underage, loli, shota, nude, naked, nipples, "
    "exposed genitals, penis, vagina, completely naked"
)


class HuggingFaceImageGenerator:
    """High-quality anime image generator."""

    def __init__(self):
        self.animagine_client = None
        self.space_client = None
        self.last_provider = None
        self.hf_token = os.environ.get("HF_TOKEN")
        self.space_id = os.environ.get("LILITH_IMAGE_SPACE")
        self._connect_space()
        self._connect_animagine()

    def _connect_space(self):
        """Connect to the user's private ZeroGPU Space (primary, uncensored)."""
        if not GRADIO_AVAILABLE or not self.space_id:
            return
        try:
            self.space_client = Client(self.space_id, token=self.hf_token)
            print(f"[IMAGE v2] LILITH Space connected: {self.space_id}")
        except Exception as e:
            print(f"[IMAGE v2] LILITH Space connection error: {e}")
            self.space_client = None

    def _connect_animagine(self):
        if not GRADIO_AVAILABLE:
            return
        try:
            self.animagine_client = Client("cagliostrolab/animagine-xl-3.1")
            print("[IMAGE v2] Animagine XL 3.1 connected")
        except Exception as e:
            print(f"[IMAGE v2] Animagine connection error: {e}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_lilith_image(self, outfit_style: str = "random",
                              seed: Optional[int] = None) -> Optional[bytes]:
        outfit = _outfit_prompt(outfit_style)
        prompt = f"{LILITH_BASE}, {outfit}, {QUALITY_POSITIVE}"
        return self.generate_image(prompt, seed=seed)

    def generate_image(self, prompt: str, ensure_clothed: bool = True,
                       seed: Optional[int] = None) -> Optional[bytes]:
        # Ensure quality tags
        if "masterpiece" not in prompt.lower():
            prompt = f"{prompt}, {QUALITY_POSITIVE}"
        if "anime" not in prompt.lower() and "1girl" not in prompt.lower():
            prompt = f"anime style, {prompt}"

        # Try LILITH Space (user's private ZeroGPU, uncensored, best quality)
        result = self._generate_space(prompt, seed=seed)
        if result:
            self.last_provider = "LILITH Space (ZeroGPU)"
            return result

        # Try Animagine (best quality)
        result = self._generate_animagine(prompt, seed=seed)
        if result:
            self.last_provider = "Animagine XL 3.1"
            return result

        # Fallback: Pollinations image (uses Flux, decent quality)
        result = self._generate_pollinations(prompt, seed=seed)
        if result:
            self.last_provider = "Pollinations/Flux"
            return result

        # Fallback: AI Horde
        result = self._generate_ai_horde(prompt)
        if result:
            self.last_provider = "AI Horde"
            return result

        return None

    # ------------------------------------------------------------------
    # LILITH Space (user's private ZeroGPU, uncensored) - PRIMARY
    # ------------------------------------------------------------------

    def _generate_space(self, prompt: str, seed: Optional[int] = None) -> Optional[bytes]:
        if not self.space_client:
            self._connect_space()
            if not self.space_client:
                return None
        try:
            used_seed = seed if seed is not None else random.randint(1, 999999)
            result = self.space_client.predict(
                prompt,             # prompt
                QUALITY_NEGATIVE,   # negative_prompt
                768,                # width
                1152,               # height
                24,                 # steps
                5.5,                # guidance_scale
                used_seed,          # seed
                api_name="/generate",
            )
            img_path = result[0] if isinstance(result, (list, tuple)) else result
            if img_path and os.path.exists(str(img_path)):
                with open(str(img_path), "rb") as f:
                    data = f.read()
                if len(data) > 1000:
                    print(f"[IMAGE v2] LILITH Space generated {len(data)} bytes")
                    return data
        except Exception as e:
            print(f"[IMAGE v2] LILITH Space error: {e}")
            self.space_client = None
        return None

    # ------------------------------------------------------------------
    # Animagine XL 3.1 (HuggingFace Space)
    # ------------------------------------------------------------------

    def _generate_animagine(self, prompt: str, seed: Optional[int] = None) -> Optional[bytes]:
        if not self.animagine_client:
            self._connect_animagine()
            if not self.animagine_client:
                return None
        try:
            used_seed = seed if seed is not None else random.randint(0, 2**32)
            result = self.animagine_client.predict(
                prompt,                     # positive prompt
                QUALITY_NEGATIVE,           # negative prompt
                used_seed,                  # seed
                832,                        # width
                1216,                       # height
                7.5,                        # guidance_scale (slightly higher for better adherence)
                35,                         # steps (increased from 28 for quality)
                "DPM++ 2M Karras",          # sampler
                "832 x 1216",               # aspect_ratio
                "Anime",                    # style_preset
                "Standard v3.1",            # quality_tags
                False,                      # use_upscaler
                0.55,                       # strength
                1.0,                        # upscale_by
                True,                       # add_quality_tags
                api_name="/run",
            )
            if result and len(result) > 0:
                images = result[0]
                if images and len(images) > 0:
                    img_info = images[0]
                    img_path = img_info.get("image") if isinstance(img_info, dict) else img_info
                    if img_path and os.path.exists(str(img_path)):
                        with open(str(img_path), "rb") as f:
                            data = f.read()
                        if len(data) > 1000:
                            print(f"[IMAGE v2] Animagine generated {len(data)} bytes")
                            return data
        except Exception as e:
            print(f"[IMAGE v2] Animagine error: {e}")
            self.animagine_client = None
        return None

    # ------------------------------------------------------------------
    # Pollinations Image (uses Flux, free, reliable)
    # ------------------------------------------------------------------

    def _generate_pollinations(self, prompt: str, seed: Optional[int] = None) -> Optional[bytes]:
        try:
            import urllib.parse
            encoded = urllib.parse.quote(prompt)
            seed_qs = f"&seed={seed}" if seed is not None else ""
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=1024&nologo=true&enhance=true&model=flux{seed_qs}"
            r = requests.get(
                url,
                timeout=90,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"},
            )
            if r.status_code == 200 and len(r.content) > 5000:
                print(f"[IMAGE v2] Pollinations generated {len(r.content)} bytes")
                return r.content
        except Exception as e:
            print(f"[IMAGE v2] Pollinations error: {e}")
        return None

    # ------------------------------------------------------------------
    # AI Horde (free, community-powered)
    # ------------------------------------------------------------------

    def _generate_ai_horde(self, prompt: str) -> Optional[bytes]:
        try:
            resp = requests.post(
                "https://aihorde.net/api/v2/generate/async",
                json={
                    "prompt": f"{prompt} ### {QUALITY_NEGATIVE}",
                    "params": {
                        "width": 768,
                        "height": 1024,
                        "steps": 35,
                        "sampler_name": "k_dpmpp_2m",
                        "cfg_scale": 7.5,
                        "denoising_strength": 0.75,
                    },
                    "nsfw": False,
                    "censor_nsfw": True,
                    "r2": True,
                    "models": ["Animagine XL 3.1", "PonyDiffusionXL", "Anything Diffusion"],
                },
                headers={
                    "Content-Type": "application/json",
                    "apikey": "0000000000",
                },
                timeout=30,
            )
            if resp.status_code != 202:
                return None
            job_id = resp.json().get("id")
            if not job_id:
                return None

            for _ in range(90):
                time.sleep(2)
                check = requests.get(
                    f"https://aihorde.net/api/v2/generate/check/{job_id}",
                    timeout=10,
                )
                if check.status_code == 200 and check.json().get("done"):
                    result = requests.get(
                        f"https://aihorde.net/api/v2/generate/status/{job_id}",
                        timeout=30,
                    )
                    if result.status_code == 200:
                        gens = result.json().get("generations", [])
                        if gens and gens[0].get("img"):
                            img = gens[0]["img"]
                            if img.startswith("http"):
                                ir = requests.get(img, timeout=30)
                                if ir.status_code == 200 and len(ir.content) > 1000:
                                    print(f"[IMAGE v2] AI Horde generated {len(ir.content)} bytes")
                                    return ir.content
                            else:
                                data = base64.b64decode(img)
                                if len(data) > 1000:
                                    print(f"[IMAGE v2] AI Horde generated {len(data)} bytes")
                                    return data
                    break
        except Exception as e:
            print(f"[IMAGE v2] AI Horde error: {e}")
        return None

    def get_status(self) -> Dict:
        return {
            "space_connected": self.space_client is not None,
            "space_id": self.space_id,
            "animagine_connected": self.animagine_client is not None,
            "gradio_available": GRADIO_AVAILABLE,
            "last_provider": self.last_provider,
            "pollinations_available": True,
            "ai_horde_available": True,
        }


# Singleton
_generator: Optional[HuggingFaceImageGenerator] = None


def get_image_generator() -> HuggingFaceImageGenerator:
    global _generator
    if _generator is None:
        _generator = HuggingFaceImageGenerator()
    return _generator


if __name__ == "__main__":
    gen = get_image_generator()
    print("Status:", gen.get_status())
    print("Testing image generation...")
    img = gen.generate_lilith_image()
    if img:
        print(f"SUCCESS: {len(img)} bytes from {gen.last_provider}")
    else:
        print("Generation failed")
