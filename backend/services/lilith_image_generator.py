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


# ---------------------------------------------------------------------------
# Scenes — environments / settings, appended to the prompt
# ---------------------------------------------------------------------------

SCENES: Dict[str, Dict[str, str]] = {
    "candlelit_bedroom":   {"label": "Candlelit bedroom",     "prompt": "in a candlelit bedroom, silk sheets, warm amber lighting, rose petals scattered"},
    "moonlit_balcony":     {"label": "Moonlit balcony",       "prompt": "on a moonlit stone balcony, city lights behind, cool blue tones, soft breeze in hair"},
    "penthouse_skyline":   {"label": "Penthouse skyline",     "prompt": "in a modern penthouse, floor-to-ceiling windows, night skyline of a metropolis, ambient warm lamp light"},
    "private_beach":       {"label": "Private beach at sunset","prompt": "on a private white-sand beach at sunset, golden hour, gentle waves, tropical palms in soft focus"},
    "wine_cellar":         {"label": "Wine cellar",            "prompt": "in a stone wine cellar, oak barrels lining the walls, low warm lighting, holding a glass of red"},
    "velvet_boudoir":      {"label": "Velvet boudoir",         "prompt": "in a velvet-draped boudoir, deep burgundy tones, gilded mirror, ornate chaise, candlelight"},
    "opera_house":         {"label": "Opera house balcony",    "prompt": "in a grand opera house private balcony, red velvet curtains, chandeliers, gilded ornaments"},
    "garden_at_dusk":      {"label": "Garden at dusk",         "prompt": "in a lush garden at dusk, string lights overhead, roses, warm twilight sky"},
    "rooftop_pool":        {"label": "Rooftop pool at night",  "prompt": "beside a rooftop infinity pool at night, city skyline glowing, water reflections, cinematic lighting"},
    "rainy_window":        {"label": "Rainy window",           "prompt": "sitting by a large window with rain streaming down, cozy warm interior, moody bluish light outside"},
    "fireplace":           {"label": "By the fireplace",       "prompt": "beside a stone fireplace with roaring flames, thick fur throw, warm firelight glow on skin"},
    "library":             {"label": "Old library",            "prompt": "in an old library, floor-to-ceiling wooden bookshelves, ladder, dust motes in a shaft of afternoon light"},
    "ski_chalet":          {"label": "Ski chalet",             "prompt": "inside a cozy alpine ski chalet, exposed wooden beams, snow visible through the window, fireplace glow"},
    "tropical_resort":     {"label": "Tropical resort suite",  "prompt": "in a luxurious tropical resort suite, open doors to the ocean, sheer curtains billowing, palm shadows"},
    "victorian_bathroom":  {"label": "Victorian bathroom",     "prompt": "in an ornate victorian bathroom, clawfoot tub, brass fixtures, black-and-white tile, candlelit steam"},
    "dressing_room":       {"label": "Vintage dressing room",  "prompt": "in a vintage dressing room, art deco vanity, hollywood mirror bulbs, fresh flowers, silk hanging"},
}


# ---------------------------------------------------------------------------
# Poses — body language / composition, appended to the prompt
# ---------------------------------------------------------------------------

POSES: Dict[str, Dict[str, str]] = {
    "portrait":            {"label": "Simple portrait",          "prompt": "upper body portrait, gentle smile, direct gaze at viewer, elegant posture"},
    "over_shoulder":       {"label": "Over the shoulder",         "prompt": "looking back over her shoulder, sultry expression, hair sweeping to one side"},
    "hands_on_hips":       {"label": "Hands on hips",              "prompt": "standing with hands on hips, confident stance, chin slightly tilted up"},
    "leaning_wall":        {"label": "Leaning against a wall",     "prompt": "casually leaning against a wall, one leg crossed over the other, playful smirk"},
    "sitting_crossed":     {"label": "Sitting cross-legged",       "prompt": "sitting cross-legged, hands resting on her knees, relaxed and inviting"},
    "kneeling_silk":       {"label": "Kneeling on silk",           "prompt": "kneeling gracefully on silk sheets, hands on thighs, chest slightly forward, looking up at viewer"},
    "lying_back":          {"label": "Lying on her back",          "prompt": "lying on her back, one knee bent upward, hair fanned out, arm raised above her head"},
    "lying_stomach":       {"label": "Lying on her stomach",       "prompt": "lying on her stomach, propped on elbows, ankles crossed in the air behind her, soft smile"},
    "seated_chair":        {"label": "Seated on a chair",           "prompt": "seated in an ornate chair, legs crossed elegantly, one arm draped over the backrest"},
    "walking_toward":      {"label": "Walking toward viewer",       "prompt": "walking toward the camera, hips swaying, dynamic motion, one hand brushing hair back"},
    "wine_pose":           {"label": "Holding wine glass",          "prompt": "holding a glass of red wine, sultry gaze over the rim of the glass, other hand at her side"},
    "mirror_look":         {"label": "Looking in a mirror",         "prompt": "posing in front of a mirror, applying lipstick or adjusting an earring, viewer sees reflection"},
    "hair_up":             {"label": "Arms up, hair up",             "prompt": "both arms raised to gather her hair up, back slightly arched, side profile"},
    "seated_floor":        {"label": "Sitting on the floor",         "prompt": "sitting on the floor, knees to one side, one hand propping her up, tousled hair"},
    "kissing_finger":      {"label": "Finger to lips",                "prompt": "one finger raised to her lips, playful shushing gesture, mischievous look in her eyes"},
}


def _scene_prompt(scene: Optional[str]) -> Optional[str]:
    if not scene or scene == "none":
        return None
    entry = SCENES.get(scene)
    return entry["prompt"] if entry else scene


def _pose_prompt(pose: Optional[str]) -> Optional[str]:
    if not pose or pose == "none":
        return None
    entry = POSES.get(pose)
    return entry["prompt"] if entry else pose

# Quality boosters — anatomy-focused positive tags reduce deformity risk
# even on providers (like Pollinations Flux URL API) that ignore negative prompts.
QUALITY_POSITIVE = (
    "masterpiece, best quality, extremely detailed, "
    "beautiful detailed eyes, symmetric face, correct anatomy, "
    "well-proportioned body, five fingers per hand, "
    "perfectly rendered hands, natural finger joints, elegant fingers, "
    "natural pose, intricate details, perfect lighting, "
    "professional illustration, sharp focus, vibrant colors, high contrast, "
    "anime style, detailed skin texture, crisp linework, sharp fine details"
)

# STRONG negative prompt to prevent warping/deformation (used by providers
# that accept a negative prompt: HF Space, Animagine, AI Horde).
QUALITY_NEGATIVE = (
    "lowres, bad anatomy, bad hands, text, error, missing fingers, "
    "extra digit, fewer digits, cropped, worst quality, low quality, "
    "normal quality, jpeg artifacts, signature, watermark, username, "
    "blurry, soft focus, out of focus, hazy, bad feet, mutated, deformed, ugly, duplicate, "
    "morbid, mutilated, extra fingers, fused fingers, too many fingers, "
    "six fingers, seven fingers, four fingers, mangled fingers, bent fingers, "
    "distorted hands, malformed hands, warped hands, extra hands, missing hands, "
    "twisted hands, tangled limbs, claw hands, ugly fingers, "
    "long neck, poorly drawn hands, poorly drawn feet, poorly drawn face, "
    "asymmetric face, cross-eyed, wall-eyed, wrong eyes, mismatched eyes, "
    "uneven eyes, lopsided face, crooked face, "
    "out of frame, extra limbs, disfigured, gross proportions, "
    "malformed limbs, missing arms, missing legs, extra arms, extra legs, "
    "bad proportions, body out of frame, floating limbs, disconnected limbs, "
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
                              seed: Optional[int] = None,
                              scene: Optional[str] = None,
                              pose: Optional[str] = None,
                              reference_path: Optional[str] = None,
                              reference_strength: float = 0.32) -> Optional[bytes]:
        outfit = _outfit_prompt(outfit_style)
        parts = [LILITH_BASE, outfit]
        pose_p = _pose_prompt(pose)
        if pose_p:
            parts.append(pose_p)
        scene_p = _scene_prompt(scene)
        if scene_p:
            parts.append(scene_p)
        parts.append(QUALITY_POSITIVE)
        prompt = ", ".join(parts)
        return self.generate_image(
            prompt, seed=seed,
            reference_path=reference_path, reference_strength=reference_strength,
        )

    def generate_image(self, prompt: str, ensure_clothed: bool = True,
                       seed: Optional[int] = None,
                       reference_path: Optional[str] = None,
                       reference_strength: float = 0.32) -> Optional[bytes]:
        # Ensure quality tags
        if "masterpiece" not in prompt.lower():
            prompt = f"{prompt}, {QUALITY_POSITIVE}"
        if "anime" not in prompt.lower() and "1girl" not in prompt.lower():
            prompt = f"anime style, {prompt}"

        # Reference-image path (img2img) — most face-consistent
        if reference_path:
            result = self._generate_space_reference(prompt, reference_path, reference_strength, seed=seed)
            if result:
                self.last_provider = "LILITH Space (Reference)"
                return result
            # Pollinations supports img2img via ?image=<url>
            result = self._generate_pollinations(prompt, seed=seed, reference_url=reference_path)
            if result:
                self.last_provider = "Pollinations/Flux (Reference)"
                return result
            # If reference-only path fails entirely, fall through to txt2img
            print("[IMAGE v2] Reference path failed, falling back to txt2img")

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
    # LILITH Space — reference / img2img endpoint (best face fidelity)
    # ------------------------------------------------------------------

    def _generate_space_reference(self, prompt: str, reference_path: str,
                                  strength: float, seed: Optional[int] = None) -> Optional[bytes]:
        if not self.space_client:
            self._connect_space()
            if not self.space_client:
                return None
        try:
            used_seed = seed if seed is not None else random.randint(1, 999999)
            # Space accepts local filepath OR public URL for reference_image.
            result = self.space_client.predict(
                reference_path,     # reference_image
                prompt,             # prompt
                QUALITY_NEGATIVE,   # negative_prompt
                float(strength),    # strength
                768,                # width
                1152,               # height
                40,                 # steps (bumped 30->40 for cleaner anatomy)
                7.5,                # guidance_scale (7.5 sweet spot)
                used_seed,          # seed
                api_name="/generate_reference",
            )
            img_path = result[0] if isinstance(result, (list, tuple)) else result
            if img_path and os.path.exists(str(img_path)):
                with open(str(img_path), "rb") as f:
                    data = f.read()
                if len(data) > 1000:
                    print(f"[IMAGE v2] LILITH Space (reference) generated {len(data)} bytes")
                    return data
        except Exception as e:
            print(f"[IMAGE v2] LILITH Space reference error: {e}")
            self.space_client = None
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
                40,                 # steps (bumped 30->40 for cleaner anatomy + fingers)
                7.5,                # guidance_scale (clamped to sweet spot for style stability)
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
                7.5,                        # guidance_scale
                40,                         # steps (bumped 35->40 for hands/anatomy)
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

    def _generate_pollinations(self, prompt: str, seed: Optional[int] = None,
                               reference_url: Optional[str] = None) -> Optional[bytes]:
        try:
            import urllib.parse
            # Pollinations Flux ignores negative_prompt (URL API). Bake anti-deformity
            # anchors into the positive prompt so anatomy stays clean.
            anti_deform = (
                "highly detailed, anatomically correct, symmetric face, "
                "well-formed hands with five fingers, proper limb proportions, "
                "sharp clean line-art, no distortion"
            )
            enriched = f"{prompt}, {anti_deform}"
            encoded = urllib.parse.quote(enriched)
            seed_qs = f"&seed={seed}" if seed is not None else ""
            ref_qs = f"&image={urllib.parse.quote(reference_url, safe='')}" if reference_url else ""
            url = (
                f"https://image.pollinations.ai/prompt/{encoded}"
                f"?width=768&height=1024&nologo=true&nofeed=true&enhance=true&model=flux"
                f"{seed_qs}{ref_qs}"
            )
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
