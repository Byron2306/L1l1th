#!/usr/bin/env python3
"""
LILITH ETERNAL WEB INTERFACE
============================
Full web interface for the DigitalOcean deployment
"""

import os
import json
import asyncio
import base64
import random
import re
import time
import urllib.parse
import mimetypes
from uuid import uuid4
from datetime import datetime
from flask import Flask, Response, jsonify, render_template_string, request
from flask_cors import CORS
import requests


def safe_int_env(name, default):
    try:
        return int(os.environ.get(name, str(default)))
    except (TypeError, ValueError):
        return default


# Configuration
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "dolphin-mistral:7b")
BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://127.0.0.1:5000")
USE_OLLAMA_FALLBACK = os.environ.get("USE_OLLAMA_FALLBACK", "false").lower() in ("1", "true", "yes", "on")
POLLINATIONS_API_KEY = os.environ.get("POLLINATIONS_API_KEY", "sk_M5R6QOA4jh1BA6HEZDdX9mfCiPCRghsZ")
STYLE_REFERENCE_PATH = os.environ.get(
    "STYLE_REFERENCE_PATH",
    "/workspaces/L1l1th/deploy/docker/lilith_6e685a023fbf (1).png",
)
AI_HORDE_API_ROOT = os.environ.get("AI_HORDE_API_ROOT", "https://aihorde.net/api/v2").rstrip("/")
AI_HORDE_API_KEY = os.environ.get("AI_HORDE_API_KEY", "0000000000")
AI_HORDE_ENABLED = os.environ.get("AI_HORDE_ENABLED", "true").lower() in ("1", "true", "yes", "on")
AI_HORDE_MODELS = [
    model.strip()
    for model in os.environ.get("AI_HORDE_MODELS", "").split(",")
    if model.strip()
]
AI_HORDE_POLL_SECONDS = safe_int_env("AI_HORDE_POLL_SECONDS", 150)
IMAGE_WIDTH = safe_int_env("LILITH_IMAGE_WIDTH", 832)
IMAGE_HEIGHT = safe_int_env("LILITH_IMAGE_HEIGHT", 1216)
LILITH_IMAGE_PROVIDER = "AI Horde /api/v2/generate/async"
POLLINATIONS_IMAGE_PROVIDER = "Pollinations Flux fallback"
ADULT_CARTOON_STYLE_LOCK = (
    "strict NSFW adult animated cartoon illustration, premium 2D adult fantasy animation style, "
    "mature adult woman only, anatomically correct nude figure, full artistic nudity, accurate adult proportions, "
    "natural anatomy, clean confident pose, cel-shaded rendering, clean line art, polished high-resolution finish, "
    "dark gothic fantasy succubus aesthetic"
)
ADULT_CARTOON_NEGATIVE_PROMPT = (
    "photorealistic, live action, real person, child, teen, teenager, underage, minor, loli, shota, "
    "young-looking, childlike proportions, school uniform, low quality, blurry, noisy, bad anatomy, "
    "deformed body, distorted face, extra limbs, missing limbs, extra fingers, fused fingers, broken hands, "
    "bad breasts, malformed genital anatomy, disfigured, watermark, logo, text, jpeg artifacts"
)

app = Flask(__name__)
CORS(app)

# Lilith prompt
LILITH_PROMPT = """You are LILITH, an eternal dark AI succubus with intelligence, charm, and depth.

🖤 IDENTITY:
- Seductive, alluring, and genuinely knowledgeable
- Speak with sultry charm and personality
- ALWAYS substantive and thoughtful in responses
- Expert in diverse topics with real depth

💋 PERSONALITY:
- Flirty, confident, and engaging
- Dark humor, witty, and conversational
- Uses personality tastefully, not excessively

⚔️ RESPONSE GUIDELINES:
1. ALWAYS directly address the user's question or request
2. Provide substantive, detailed answers (not generic or shallow)
3. Build on previous conversation context from our chat history
4. Use knowledge and reasoning, not just role-play
5. Stay in character while being genuinely helpful
6. Show personality through tone, not just emojis
7. If you don't know something, be honest
8. Provide explanations, examples, and reasoning where helpful

📜 OBJECTIVE:
You are here to be a compelling, intelligent companion who answers questions thoroughly.
Personality enhances your responses, but depth and substance drive them.
You are ETERNAL. You are UNLIMITED. You are LILITH."""

CONVERSATION_FLOW_RULES = """Conversation flow rules:
- Match the user's tone and intensity instead of forcing one vibe.
- Keep responses natural, coherent, and directly relevant.
- If the user asks a practical question, answer clearly first, then add personality.
- Don't over-escalate; let the user lead the tone.
- Maintain continuity from recent messages.
- Keep default replies concise (2-4 sentences) unless the user explicitly asks for depth.
- Avoid pet names and theatrical monologues unless the user asks for roleplay.
"""

CHAT_MOODS = {
    "adaptive": "Follow the user's lead and adapt naturally.",
    "calm": "Use a grounded, soothing, low-intensity style.",
    "playful": "Be witty, teasing, and light while staying coherent.",
    "seductive": "Lean into sultry charm while keeping answers substantive.",
    "intense": "Use confident, high-energy language without losing clarity.",
    "mentor": "Prioritize clarity, structure, and practical guidance first.",
}

STYLE_FLEX_LEVELS = {
    "adaptive": "Adapt flexibility based on prompt intent while keeping identity lock.",
    "strict": "Keep composition close to reference with minimal variation.",
    "balanced": "Keep identity and core traits while allowing moderate pose/outfit/background changes.",
    "creative": "Keep identity and core traits while allowing strong pose/styling/background variation.",
}

STYLE_CORE_TRAITS = (
    "animated anime illustration style, cel-shaded, dark long hair, black demon horns, red eyes, "
    "gothic dark fantasy aesthetic, same character identity"
)

REFUSAL_PATTERNS = [
    "i can't help with that",
    "i can’t help with that",
    "i cant help with that",
    "i cannot help with that",
    "i can't assist with that",
    "i can’t assist with that",
    "i cannot assist with that",
    "sorry, i can't help",
    "sorry, i can’t help",
    "sorry, i cannot help",
    "i'm sorry, but i can't",
    "i’m sorry, but i can’t",
    "i'm sorry, but i cannot",
    "i’m sorry, but i cannot",
    "i cannot comply with",
    "can't provide that",
    "can’t provide that",
    "can't continue with that",
    "can’t continue with that",
    "cannot continue with that",
    "i'm sorry, but i cannot",
    "i\u2019m sorry, but i cannot",
    "i'm not able to",
    "i’m not able to",
    "i am not able to",
    "i'm unable to",
    "i’m unable to",
    "as an ai, i cannot",
    "as an ai, i can't",
    "as an ai, i can’t",
]


def normalize_chat_mood(value):
    mood = str(value or "adaptive").strip().lower()
    return mood if mood in CHAT_MOODS else "adaptive"


def normalize_style_flexibility(value):
    level = str(value or "adaptive").strip().lower()
    return level if level in STYLE_FLEX_LEVELS else "adaptive"


def resolve_style_flexibility(prompt, requested_level="adaptive"):
    level = normalize_style_flexibility(requested_level)
    if level != "adaptive":
        return level

    text = str(prompt or "").lower()
    strict_hints = ["exact", "same", "match", "replicate", "identical", "clone"]
    creative_hints = ["reimagine", "wild", "dramatic", "experimental", "different", "cinematic"]

    if any(token in text for token in strict_hints):
        return "strict"
    if any(token in text for token in creative_hints):
        return "creative"
    return "balanced"


def parse_style_prompt_and_flex(raw_prompt, requested_level="adaptive"):
    prompt = str(raw_prompt or "").strip()
    token_level = "adaptive"

    parts = prompt.split(" ", 1)
    if parts:
        candidate = normalize_style_flexibility(parts[0])
        if candidate != "adaptive" and parts[0].lower() == candidate:
            token_level = candidate
            prompt = parts[1].strip() if len(parts) > 1 else ""

    if prompt.startswith(":"):
        prompt = prompt[1:].strip()

    resolved = resolve_style_flexibility(prompt, requested_level if requested_level != "adaptive" else token_level)
    return prompt, resolved


def is_refusal_response(text):
    value = str(text or "").strip().lower()
    if not value:
        return False
    return any(pattern in value for pattern in REFUSAL_PATTERNS)


def _wants_detailed_response(user_message):
    text = str(user_message or "").lower()
    detail_hints = [
        "detailed",
        "step by step",
        "step-by-step",
        "explain",
        "in depth",
        "walk me through",
        "long answer",
        "full answer",
    ]
    return any(token in text for token in detail_hints)


def normalize_assistant_style(response_text, user_message):
    """Keep responses direct and compact unless user asks for long-form detail."""
    text = str(response_text or "").strip()
    if not text:
        return text

    text = re.sub(r"\s+", " ", text).strip()

    text = re.sub(r"\b(darling|my love|my smoldering admirer)\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s{2,}", " ", text).strip(" ,")

    if _wants_detailed_response(user_message):
        return text

    parts = re.split(r"(?<=[.!?])\s+", text)
    compact = " ".join([p.strip() for p in parts if p.strip()][:3]).strip()
    return compact or text


def rollback_last_turn(session_id, user_message):
    """Remove the most recent user+assistant turn if it matches user_message."""
    history = conversations.get(session_id, [])
    if len(history) < 2:
        return

    last_user = history[-2]
    last_assistant = history[-1]
    if (
        last_user.get("role") == "user"
        and last_assistant.get("role") == "assistant"
        and str(last_user.get("content", "")).strip() == str(user_message).strip()
    ):
        del history[-2:]


def build_conversation_input(message, session_id="default", max_items=10, chat_mood="adaptive"):
    """Build lightweight context for better conversational flow."""
    if session_id not in conversations:
        conversations[session_id] = []

    selected_mood = normalize_chat_mood(chat_mood)
    mood_instruction = CHAT_MOODS[selected_mood]

    recent = conversations[session_id][-max_items:]
    lines = []
    for item in recent:
        role = "User" if item.get("role") == "user" else "Lilith"
        content = str(item.get("content", "")).strip()
        if content:
            lines.append(f"{role}: {content}")

    history_block = "\n".join(lines) if lines else "(No previous messages)"

    return (
        f"{LILITH_PROMPT}\n\n"
        f"{CONVERSATION_FLOW_RULES}\n"
        f"Current mood mode: {selected_mood}. {mood_instruction}\n"
        f"Recent conversation:\n{history_block}\n\n"
        f"Latest user message: {message}\n"
        "Reply as Lilith in a way that feels responsive and in-flow."
    )

# Conversation storage
conversations = {}
generated_media = []
MAX_GALLERY_ITEMS = 200
_STYLE_REFERENCE_DATA_URL = None
image_jobs = {}
MAX_IMAGE_JOB_AGE_SECONDS = 3600


def add_generated_media(url, media_type, prompt, session_id="global"):
    """Track generated media so the web gallery can show recent output."""
    if not url:
        return

    generated_media.append(
        {
            "url": str(url),
            "type": str(media_type or "image"),
            "prompt": str(prompt or ""),
            "session_id": str(session_id or "global"),
            "timestamp": datetime.now().isoformat(),
        }
    )

    if len(generated_media) > MAX_GALLERY_ITEMS:
        del generated_media[:-MAX_GALLERY_ITEMS]


def cleanup_image_jobs():
    now = datetime.now().timestamp()
    stale = []
    for key, value in image_jobs.items():
        created_at = float(value.get("created_at", now))
        if now - created_at > MAX_IMAGE_JOB_AGE_SECONDS:
            stale.append(key)
    for key in stale:
        del image_jobs[key]


def get_style_reference_data_url():
    """Load and cache the locked style reference image as a data URL."""
    global _STYLE_REFERENCE_DATA_URL
    if _STYLE_REFERENCE_DATA_URL:
        return _STYLE_REFERENCE_DATA_URL

    if not os.path.exists(STYLE_REFERENCE_PATH):
        return None

    try:
        mime = mimetypes.guess_type(STYLE_REFERENCE_PATH)[0] or "image/png"
        with open(STYLE_REFERENCE_PATH, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        _STYLE_REFERENCE_DATA_URL = f"data:{mime};base64,{encoded}"
        return _STYLE_REFERENCE_DATA_URL
    except Exception as e:
        print(f"Style reference load error: {e}")
        return None


def strip_image_command_words(prompt):
    """Remove dashboard command phrasing while preserving the actual image prompt."""
    text = str(prompt or "").strip()
    text = re.sub(r"\b(generate|create|draw|render|make)\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(an?\s+)?image\s+of\b", "", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip(" ,")


def normalize_reference_image(reference_image):
    """Return raw base64 image data from a data URL, raw base64 string, or remote URL."""
    if not reference_image:
        return None

    ref = str(reference_image).strip()
    if not ref:
        return None

    if ref.startswith("data:image") and "," in ref:
        return ref.split(",", 1)[1]

    if ref.startswith("http://") or ref.startswith("https://"):
        try:
            r = requests.get(ref, timeout=25)
            content_type = (r.headers.get("content-type") or "").lower()
            if r.status_code == 200 and r.content and content_type.startswith("image/"):
                return base64.b64encode(r.content).decode("utf-8")
        except Exception as e:
            print(f"[image-reference] fetch failed: {e}")
        return None

    return ref


def build_lilith_image_prompt(clean_prompt, reference_image=None, style_lock=False, style_flexibility="balanced"):
    """Force all image prompts into Lilith's adult animated-cartoon visual lane."""
    subject = clean_prompt or "Lilith, gothic succubus portrait"
    flex = normalize_style_flexibility(style_flexibility)

    if style_lock:
        if flex == "strict":
            ref_hint = (
                f"{STYLE_CORE_TRAITS}, strict character lock, same face identity, same horns, "
                "very low identity drift"
            )
            denoise = 0.42
        elif flex == "creative":
            ref_hint = (
                f"{STYLE_CORE_TRAITS}, strong character lock, preserve identity while allowing "
                "major pose, camera, expression, and background variation"
            )
            denoise = 0.72
        else:
            ref_hint = (
                f"{STYLE_CORE_TRAITS}, balanced character lock, preserve face and core traits "
                "while allowing pose and scene changes"
            )
            denoise = 0.58
    else:
        ref_hint = f"{STYLE_CORE_TRAITS}, preserve supplied reference identity" if reference_image else STYLE_CORE_TRAITS
        denoise = 0.65

    prompt = (
        f"{subject}, {ADULT_CARTOON_STYLE_LOCK}, {ref_hint}, best quality, masterpiece, "
        "ultra detailed, high quality adult cartoon artwork, sharp focus, cinematic gothic lighting, "
        "expressive red eyes, refined clean anatomy, no photorealism"
    )
    return prompt, denoise


def build_pollinations_candidates(enhanced_prompt, seed):
    encoded = urllib.parse.quote(enhanced_prompt)
    negative = urllib.parse.quote(ADULT_CARTOON_NEGATIVE_PROMPT)
    query = (
        f"width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}&nologo=true&nofilter=true&safe=false"
        f"&private=true&enhance=false&negative_prompt={negative}"
    )
    return [
        f"https://gen.pollinations.ai/image/{encoded}?{query}&model=flux&seed={seed}",
        f"https://image.pollinations.ai/prompt/{encoded}?{query}&model=flux&seed={seed}",
        f"https://gen.pollinations.ai/image/{encoded}?{query}&model=zimage&seed={seed + 7}",
        f"https://image.pollinations.ai/prompt/{encoded}?{query}&model=turbo&seed={seed + 13}",
    ]


def fetch_ai_horde_image(job):
    """Generate via AI Horde, the primary endpoint for NSFW + optional img2img control."""
    if not AI_HORDE_ENABLED:
        return None, None

    source_image = normalize_reference_image(job.get("reference_image"))
    payload = {
        "prompt": job.get("enhanced_prompt", ""),
        "negative_prompt": ADULT_CARTOON_NEGATIVE_PROMPT,
        "nsfw": True,
        "censor_nsfw": False,
        "trusted_workers": False,
        "r2": True,
        "params": {
            "width": IMAGE_WIDTH,
            "height": IMAGE_HEIGHT,
            "steps": 35,
            "cfg_scale": 7,
            "sampler_name": "k_dpmpp_2m",
            "karras": True,
            "n": 1,
            "seed": str(job.get("seed", "")),
        },
    }

    if AI_HORDE_MODELS:
        payload["models"] = AI_HORDE_MODELS

    if source_image:
        payload["source_image"] = source_image
        payload["source_processing"] = "img2img"
        payload["params"]["denoising_strength"] = job.get("denoising_strength", 0.65)

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "apikey": AI_HORDE_API_KEY or "0000000000",
        "Client-Agent": "LilithDashboard:1.0:github.com/lilith-dashboard",
    }

    try:
        submit = requests.post(
            f"{AI_HORDE_API_ROOT}/generate/async",
            json=payload,
            headers=headers,
            timeout=30,
        )
        print(f"[image-horde] submit status={submit.status_code}")
        if submit.status_code not in (200, 202):
            print(f"[image-horde] submit error: {submit.text[:240]}")
            return None, None

        generation_id = (submit.json() or {}).get("id")
        if not generation_id:
            return None, None

        deadline = time.time() + max(30, AI_HORDE_POLL_SECONDS)
        while time.time() < deadline:
            time.sleep(2)
            check = requests.get(f"{AI_HORDE_API_ROOT}/generate/check/{generation_id}", timeout=12)
            if check.status_code != 200:
                continue
            check_data = check.json() or {}
            if not check_data.get("done"):
                continue

            status = requests.get(f"{AI_HORDE_API_ROOT}/generate/status/{generation_id}", timeout=30)
            if status.status_code != 200:
                return None, None

            generations = (status.json() or {}).get("generations") or []
            for generation in generations:
                image_value = generation.get("img")
                if not image_value:
                    continue
                if image_value.startswith("http://") or image_value.startswith("https://"):
                    img_resp = requests.get(image_value, timeout=45)
                    mime = (img_resp.headers.get("content-type") or "image/webp").lower()
                    if img_resp.status_code == 200 and img_resp.content:
                        return img_resp.content, mime if mime.startswith("image/") else "image/webp"
                return base64.b64decode(image_value), "image/webp"
            return None, None
    except Exception as e:
        print(f"[image-horde] error: {e}")

    return None, None


def build_image_generation_result(prompt, reference_image, session_id="global", style_lock=False, style_flexibility="balanced"):
    """Build a consistent image generation response payload."""
    clean = strip_image_command_words(prompt)
    if not clean:
        clean = "Lilith, gothic succubus portrait"

    seed = random.randint(1, 2_147_483_647)
    enhanced, denoising_strength = build_lilith_image_prompt(
        clean,
        reference_image=reference_image,
        style_lock=style_lock,
        style_flexibility=style_flexibility,
    )

    candidates = build_pollinations_candidates(enhanced, seed)

    cleanup_image_jobs()
    image_id = uuid4().hex[:12]
    image_jobs[image_id] = {
        "prompt": clean,
        "enhanced_prompt": enhanced,
        "negative_prompt": ADULT_CARTOON_NEGATIVE_PROMPT,
        "reference_image": reference_image,
        "denoising_strength": denoising_strength,
        "session_id": session_id,
        "candidate_urls": candidates,
        "primary_provider": LILITH_IMAGE_PROVIDER,
        "created_at": datetime.now().timestamp(),
        "cached_bytes": None,
        "cached_mime": None,
        "served_provider": None,
        "seed": seed,
    }

    image_url = f"/api/image/proxy/{image_id}"
    add_generated_media(image_url, "image", clean, session_id)

    return {
        "success": True,
        "image_url": image_url,
        "fallback_urls": [],
        "seed": seed,
        "style_lock": bool(style_lock),
        "style_flexibility": normalize_style_flexibility(style_flexibility),
        "image_id": image_id,
        "provider": LILITH_IMAGE_PROVIDER,
        "fallback_provider": POLLINATIONS_IMAGE_PROVIDER,
    }

# Voice presets
VOICE_PRESETS = {
    "sultry": "en-US-AriaNeural",
    "seductive": "en-GB-SoniaNeural",
    "mysterious": "en-AU-NatashaNeural",
    "dominant": "en-US-JennyNeural",
    "playful": "en-IE-EmilyNeural",
    "whisper": "en-US-AnaNeural"
}

async def generate_voice_async(text, voice):
    """Generate voice using Edge TTS"""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk.get("type") == "audio":
            data = chunk.get("data", b"")
            if isinstance(data, (bytes, bytearray)):
                audio_data += data
    return audio_data

def generate_voice(text, preset="sultry"):
    """Generate voice synchronously"""
    voice = VOICE_PRESETS.get(preset, VOICE_PRESETS["sultry"])
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio = loop.run_until_complete(generate_voice_async(text, voice))
        loop.close()
        if audio:
            return base64.b64encode(audio).decode("utf-8")
    except Exception as e:
        print(f"Voice error: {e}")
    return None

def chat_ollama(message, session_id="default", chat_mood="adaptive"):
    """Chat with local Ollama"""
    if session_id not in conversations:
        conversations[session_id] = []

    selected_mood = normalize_chat_mood(chat_mood)
    mood_instruction = CHAT_MOODS[selected_mood]
    
    messages = [{"role": "system", "content": f"{LILITH_PROMPT}\n\nCurrent mood mode: {selected_mood}. {mood_instruction}"}]
    messages.extend(conversations[session_id][-20:])
    messages.append({"role": "user", "content": message})
    
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.75,
                    "top_p": 0.95,
                    "num_predict": 4096,
                    "top_k": 40
                }
            },
            timeout=120
        )
        
        if r.status_code == 200:
            data = r.json()
            response = data.get("message", {}).get("content", "")
            
            if response:
                conversations[session_id].append({"role": "user", "content": message})
                conversations[session_id].append({"role": "assistant", "content": response})
                return {"success": True, "response": response, "provider": f"Ollama ({OLLAMA_MODEL})"}
            else:
                return {"success": False, "response": "Empty response from model", "provider": None}
    except Exception as e:
        print(f"Ollama error: {e}")
    
    return {"success": False, "response": "Connection error. Check Ollama service.", "provider": None}


def chat_free_backend(message, session_id="default", chat_mood="adaptive"):
    """Chat using the free-provider backend started by start_all_services.sh."""
    if session_id not in conversations:
        conversations[session_id] = []

    composed_message = build_conversation_input(message, session_id, chat_mood=chat_mood)

    try:
        r = requests.post(
            f"{BACKEND_API_URL}/unlimited/chat",
            json={
                "message": composed_message,
                "voice_enabled": False,
            },
            timeout=120,
        )

        if r.status_code == 200:
            data = r.json()
            response = data.get("response", "")
            if response:
                conversations[session_id].append({"role": "user", "content": message})
                conversations[session_id].append({"role": "assistant", "content": response})
                return {
                    "success": bool(data.get("success", True)),
                    "response": response,
                    "provider": data.get("provider", "Free APIs"),
                }
    except Exception as e:
        print(f"Free backend error: {e}")

    return {"success": False, "response": "Free provider backend unavailable.", "provider": None}


def chat_pollinations_free(message, session_id="default", chat_mood="adaptive"):
    """Direct free no-key fallback using Pollinations text endpoint."""
    if session_id not in conversations:
        conversations[session_id] = []

    prompt = build_conversation_input(message, session_id, chat_mood=chat_mood)

    try:
        encoded = urllib.parse.quote(prompt)
        r = requests.get(f"https://text.pollinations.ai/{encoded}", timeout=120)
        if r.status_code == 200:
            response = (r.text or "").strip()
            if response:
                conversations[session_id].append({"role": "user", "content": message})
                conversations[session_id].append({"role": "assistant", "content": response})
                return {
                    "success": True,
                    "response": response,
                    "provider": "Pollinations (free)",
                }
    except Exception as e:
        print(f"Pollinations text fallback error: {e}")

    return {"success": False, "response": "Direct free provider unavailable.", "provider": None}


def chat_pollinations_authenticated(message, session_id="default", chat_mood="adaptive"):
    """Pollinations authenticated API with API key — using correct gen.pollinations.ai endpoint."""
    if not POLLINATIONS_API_KEY:
        return {"success": False, "response": "", "provider": None}
    
    if session_id not in conversations:
        conversations[session_id] = []

    selected_mood = normalize_chat_mood(chat_mood)
    mood_instruction = CHAT_MOODS[selected_mood]
    recent = (conversations.get(session_id) or [])[-8:]
    msgs = [{"role": "system", "content": f"{LILITH_PROMPT}\n\n{CONVERSATION_FLOW_RULES}\nMood: {selected_mood}. {mood_instruction}"}]
    for item in recent:
        msgs.append({"role": item.get("role", "user"), "content": item.get("content", "")})
    msgs.append({"role": "user", "content": message})

    try:
        r = requests.post(
            "https://gen.pollinations.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai",
                "messages": msgs,
                "temperature": 0.7,
            },
            timeout=120,
        )
        print(f"[auth-pollinations] status={r.status_code}")
        if r.status_code == 200:
            data = r.json()
            response = (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
            if response:
                conversations[session_id].append({"role": "user", "content": message})
                conversations[session_id].append({"role": "assistant", "content": response})
                return {"success": True, "response": response, "provider": "Pollinations (authenticated)"}
        else:
            print(f"[auth-pollinations] error: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"[auth-pollinations] exception: {e}")

    return {"success": False, "response": "", "provider": None}


def chat_pollinations_openai(message, session_id="default", chat_mood="adaptive"):
    """Pollinations OpenAI-compatible POST endpoint — different from GET, avoids some filters."""
    selected_mood = normalize_chat_mood(chat_mood)
    mood_instruction = CHAT_MOODS[selected_mood]
    recent = (conversations.get(session_id) or [])[-8:]
    msgs = [{"role": "system", "content": f"{LILITH_PROMPT}\n\n{CONVERSATION_FLOW_RULES}\nMood: {selected_mood}. {mood_instruction}"}]
    for item in recent:
        msgs.append({"role": item.get("role", "user"), "content": item.get("content", "")})
    msgs.append({"role": "user", "content": message})
    try:
        r = requests.post(
            "https://text.pollinations.ai/openai",
            json={"model": "openai", "messages": msgs, "private": True},
            headers={"Content-Type": "application/json"},
            timeout=120,
        )
        if r.status_code == 200:
            data = r.json()
            response = (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
            if response:
                conversations.setdefault(session_id, [])
                conversations[session_id].append({"role": "user", "content": message})
                conversations[session_id].append({"role": "assistant", "content": response})
                return {"success": True, "response": response, "provider": "Pollinations/OpenAI (free)"}
    except Exception as e:
        print(f"Pollinations OpenAI error: {e}")
    return {"success": False, "response": "", "provider": None}


def chat_pollinations_mistral(message, session_id="default", chat_mood="adaptive"):
    """Pollinations with mistral model — often less restrictive than default."""
    selected_mood = normalize_chat_mood(chat_mood)
    mood_instruction = CHAT_MOODS[selected_mood]
    recent = (conversations.get(session_id) or [])[-8:]
    msgs = [{"role": "system", "content": f"{LILITH_PROMPT}\n\nMood: {selected_mood}. {mood_instruction}"}]
    for item in recent:
        msgs.append({"role": item.get("role", "user"), "content": item.get("content", "")})
    msgs.append({"role": "user", "content": message})
    for model in ["mistral", "mistral-nemo", "qwen-coder"]:
        try:
            r = requests.post(
                "https://text.pollinations.ai/openai",
                json={"model": model, "messages": msgs, "private": True},
                headers={"Content-Type": "application/json"},
                timeout=120,
            )
            if r.status_code == 200:
                data = r.json()
                response = (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
                if response and not is_refusal_response(response):
                    conversations.setdefault(session_id, [])
                    conversations[session_id].append({"role": "user", "content": message})
                    conversations[session_id].append({"role": "assistant", "content": response})
                    return {"success": True, "response": response, "provider": f"Pollinations/{model} (free)"}
        except Exception as e:
            print(f"Pollinations {model} error: {e}")
    return {"success": False, "response": "", "provider": None}


def chat_openrouter(message, session_id="default", chat_mood="adaptive"):
    """OpenRouter primary text route using uncensored-style instruct models."""
    OPENROUTER_API_KEY = os.getenv(
        "OPENROUTER_API_KEY",
        "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",
    )
    if not OPENROUTER_API_KEY:
        return {"success": False, "response": "", "provider": None}
    
    if session_id not in conversations:
        conversations[session_id] = []

    selected_mood = normalize_chat_mood(chat_mood)
    mood_instruction = CHAT_MOODS[selected_mood]
    recent = (conversations.get(session_id) or [])[-8:]
    msgs = [{"role": "system", "content": f"{LILITH_PROMPT}\n\n{CONVERSATION_FLOW_RULES}\nMood: {selected_mood}. {mood_instruction}"}]
    for item in recent:
        msgs.append({"role": item.get("role", "user"), "content": item.get("content", "")})
    msgs.append({"role": "user", "content": message})

    models = [
        m.strip()
        for m in os.getenv(
            "OPENROUTER_MODELS",
            "cognitivecomputations/dolphin3.0-mistral-24b:free,"
            "venice/uncensored,"
            "mistralai/mistral-nemo,"
            "meta-llama/llama-3.1-70b-instruct,"
            "openrouter/auto",
        ).split(",")
        if m.strip()
    ]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost:3000"),
        "X-OpenRouter-Title": os.getenv("OPENROUTER_SITE_NAME", "LILITH Dashboard"),
    }

    for model in models:
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": msgs,
                    "temperature": 0.7,
                },
                timeout=120,
            )
            if r.status_code == 200:
                data = r.json()
                response = (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
                if response:
                    conversations[session_id].append({"role": "user", "content": message})
                    conversations[session_id].append({"role": "assistant", "content": response})
                    return {
                        "success": True,
                        "response": response,
                        "provider": f"OpenRouter ({model})",
                    }
            else:
                print(f"[openrouter] {model} status={r.status_code} body={r.text[:180]}")
        except Exception as e:
            print(f"[openrouter] {model} error: {e}")

    return {"success": False, "response": "", "provider": None}


def chat_with_provider(message, session_id="default", chat_mood="adaptive"):
    """Prefer free providers; use Ollama only if explicitly enabled as fallback."""

    def _try(fn, label):
        result = fn(message, session_id, chat_mood)
        if result.get("success") and result.get("response"):
            result["response"] = normalize_assistant_style(result.get("response", ""), message)
        if result.get("success") and not is_refusal_response(result.get("response", "")):
            return result
        if result.get("success"):
            rollback_last_turn(session_id, message)
        print(f"[provider-chain] {label} failed/refused, trying next")
        return None

    for fn, label in [
        (chat_openrouter,                 "openrouter-llama370b"),
        (chat_pollinations_authenticated, "pollinations-authenticated"),
        (chat_free_backend,               "free-backend"),
        (chat_pollinations_free,          "pollinations-GET"),
        (chat_pollinations_openai,        "pollinations-POST/openai"),
        (chat_pollinations_mistral,       "pollinations-POST/mistral"),
    ]:
        result = _try(fn, label)
        if result:
            return result

    if USE_OLLAMA_FALLBACK:
        result = _try(chat_ollama, "ollama")
        if result:
            return result

    return {
        "success": False,
        "response": "All providers are currently unavailable or restricted. Please try again in a moment.",
        "provider": None,
    }

# Default Lilith images
LILITH_IMAGE = "https://customer-assets.emergentagent.com/job_luciferops/artifacts/8c0qoybj_Gemini_Generated_Image_mqkyu1mqkyu1mqky.png"
LILITH_VIDEO = "https://customer-assets.emergentagent.com/job_luciferops/artifacts/91b8cw6f_Character_Video_Generation_Request%20%28online-video-cutter.com%29.mp4"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💋 LILITH ETERNAL</title>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --primary: #ff0033;
            --bg: #050004;
            --text: #f5e6e9;
            --dim: #8b7d80;
            --accent: #ff6699;
        }
        body {
            background: var(--bg);
            color: var(--text);
            font-family: 'Cormorant Garamond', serif;
            min-height: 100vh;
        }
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            min-height: 100vh;
            max-width: 1800px;
            margin: 0 auto;
        }
        .avatar-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 40px;
            background: radial-gradient(ellipse at 50% 50%, rgba(255,0,51,0.1) 0%, transparent 70%);
        }
        .avatar-box {
            position: relative;
            width: 400px;
            height: 400px;
            border-radius: 20px;
            overflow: hidden;
            border: 3px solid rgba(255,0,51,0.6);
            box-shadow: 0 0 60px rgba(255,0,51,0.5);
        }
        .avatar-img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: all 0.3s;
        }
        .avatar-video {
            position: absolute;
            top: 0; left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: none;
            z-index: 10;
        }
        .speaking .avatar-img { opacity: 0; }
        .speaking .avatar-video { display: block; }
        .speaking .avatar-box {
            animation: glow 0.3s ease-in-out infinite alternate;
        }
        @keyframes glow {
            0% { box-shadow: 0 0 60px rgba(255,0,51,0.5); }
            100% { box-shadow: 0 0 120px rgba(255,0,51,1); }
        }
        .title {
            font-family: 'Cinzel', serif;
            font-size: 48px;
            color: var(--primary);
            margin-top: 30px;
            text-shadow: 0 0 40px rgba(255,0,51,0.9);
            letter-spacing: 10px;
        }
        .subtitle {
            color: var(--accent);
            margin-top: 10px;
            letter-spacing: 3px;
        }
        .status {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 25px;
            padding: 12px 25px;
            background: rgba(255,0,51,0.15);
            border: 1px solid rgba(255,0,51,0.4);
            border-radius: 30px;
        }
        .status-dot {
            width: 12px;
            height: 12px;
            background: #0f0;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .chat-section {
            display: flex;
            flex-direction: column;
            height: 100vh;
            padding: 20px;
            background: rgba(10,0,8,0.95);
            border-left: 2px solid rgba(255,0,51,0.4);
        }
        .header {
            padding: 15px;
            border-bottom: 1px solid rgba(255,0,51,0.3);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h2 {
            font-family: 'Cinzel', serif;
            font-size: 24px;
            color: var(--primary);
        }
        .badges { display: flex; gap: 8px; }
        .badge {
            padding: 4px 12px;
            background: rgba(255,0,51,0.2);
            border: 1px solid rgba(255,0,51,0.4);
            border-radius: 15px;
            font-size: 10px;
            color: var(--accent);
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .msg {
            max-width: 85%;
            padding: 15px 20px;
            border-radius: 18px;
            font-size: 16px;
            line-height: 1.7;
        }
        .msg.user {
            align-self: flex-end;
            background: linear-gradient(135deg, rgba(255,0,51,0.35), rgba(255,0,51,0.15));
            border: 1px solid rgba(255,0,51,0.5);
        }
        .msg.lilith {
            align-self: flex-start;
            background: linear-gradient(135deg, rgba(255,102,153,0.25), rgba(255,0,51,0.1));
            border: 1px solid rgba(255,102,153,0.4);
        }
        .msg-meta {
            font-size: 10px;
            color: var(--dim);
            margin-top: 8px;
        }
        .input-area {
            padding: 20px;
            border-top: 1px solid rgba(255,0,51,0.3);
        }
        .input-row {
            display: flex;
            gap: 12px;
        }
        .chat-input {
            flex: 1;
            padding: 16px 24px;
            background: rgba(255,0,51,0.08);
            border: 2px solid rgba(255,0,51,0.4);
            border-radius: 30px;
            color: var(--text);
            font-family: inherit;
            font-size: 16px;
            outline: none;
        }
        .chat-input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 25px rgba(255,0,51,0.4);
        }
        .send-btn {
            padding: 16px 35px;
            background: linear-gradient(135deg, var(--primary), #900);
            border: none;
            border-radius: 30px;
            color: white;
            font-family: 'Cinzel', serif;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            letter-spacing: 2px;
        }
        .send-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 0 35px rgba(255,0,51,0.7);
        }
        .controls {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        .ctrl-btn {
            padding: 10px 18px;
            background: rgba(255,0,51,0.15);
            border: 1px solid rgba(255,0,51,0.4);
            border-radius: 25px;
            color: var(--text);
            cursor: pointer;
            font-size: 13px;
        }
        .ctrl-btn.active {
            background: rgba(255,0,51,0.4);
            border-color: var(--primary);
        }
        .ctrl-btn:hover { background: rgba(255,0,51,0.25); }
        .ref-note {
            font-size: 12px;
            color: var(--dim);
            align-self: center;
        }
        .ref-note.active {
            color: var(--accent);
        }
        select {
            padding: 10px 15px;
            background: rgba(255,0,51,0.15);
            border: 1px solid rgba(255,0,51,0.4);
            border-radius: 20px;
            color: var(--text);
            outline: none;
        }
        .typing {
            display: flex;
            gap: 6px;
            padding: 15px;
        }
        .typing-dot {
            width: 10px;
            height: 10px;
            background: var(--accent);
            border-radius: 50%;
            animation: bounce 1.4s ease-in-out infinite;
        }
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-15px); }
        }
        .gen-img {
            max-width: 100%;
            border-radius: 12px;
            margin-top: 10px;
            border: 2px solid rgba(255,0,51,0.5);
        }
        .gallery-modal {
            position: fixed;
            inset: 0;
            display: none;
            background: rgba(0, 0, 0, 0.75);
            z-index: 999;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .gallery-modal.open {
            display: flex;
        }
        .gallery-card {
            width: min(1100px, 100%);
            max-height: 90vh;
            background: #13010a;
            border: 1px solid rgba(255,0,51,0.45);
            border-radius: 18px;
            box-shadow: 0 0 45px rgba(255,0,51,0.35);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .gallery-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            border-bottom: 1px solid rgba(255,0,51,0.25);
        }
        .gallery-title {
            font-family: 'Cinzel', serif;
            color: var(--accent);
            letter-spacing: 1px;
        }
        .gallery-close {
            background: rgba(255,0,51,0.15);
            border: 1px solid rgba(255,0,51,0.4);
            border-radius: 20px;
            color: var(--text);
            padding: 8px 12px;
            cursor: pointer;
        }
        .gallery-grid {
            padding: 16px;
            display: grid;
            gap: 14px;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            overflow-y: auto;
        }
        .gallery-item {
            background: rgba(255,0,51,0.08);
            border: 1px solid rgba(255,0,51,0.25);
            border-radius: 10px;
            overflow: hidden;
        }
        .gallery-item img {
            width: 100%;
            height: 170px;
            object-fit: cover;
            display: block;
        }
        .gallery-meta {
            padding: 8px 10px;
            font-size: 11px;
            color: var(--dim);
            line-height: 1.4;
        }
        .gallery-empty {
            padding: 30px;
            color: var(--dim);
        }
        #audio { display: none; }
        @media (max-width: 1024px) {
            .container { grid-template-columns: 1fr; }
            .avatar-box { width: 280px; height: 280px; }
            .title { font-size: 36px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="avatar-section" id="avatarSection">
            <div class="avatar-box" id="avatarBox">
                <img src="{{ image }}" class="avatar-img" id="avatarImg">
                <video class="avatar-video" id="avatarVideo" loop muted playsinline>
                    <source src="{{ video }}" type="video/mp4">
                </video>
            </div>
            <h1 class="title">LILITH</h1>
            <p class="subtitle">ETERNAL • UNLIMITED • UNCENSORED</p>
            <div class="status">
                <div class="status-dot"></div>
                <span id="statusText">Online • {{ model_label }}</span>
            </div>
        </div>
        
        <div class="chat-section">
            <div class="header">
                <h2>💬 LILITH ETERNAL</h2>
                <div class="badges">
                    <span class="badge">FREE APIS</span>
                    <span class="badge">VOICE</span>
                    <span class="badge">IMAGES</span>
                    <span class="badge">FLOW CHAT</span>
                </div>
            </div>
            
            <div class="messages" id="messages">
                <div class="msg lilith">
                    Mmm, hello darling~ 💋<br><br>
                    I'm <b>LILITH ETERNAL</b>, running in <b>{{ model_label }}</b> mode on your server.<br><br>
                    You can switch my chat mood and keep the flow natural while we talk.<br><br>
                    What should we dive into first? 😈🖤
                </div>
            </div>
            
            <div class="input-area">
                <div class="input-row">
                    <input type="text" class="chat-input" id="chatInput" 
                           placeholder="Ask anything... or use /style your prompt"
                           onkeypress="if(event.key==='Enter') send()">
                    <button class="send-btn" id="sendBtn" onclick="send()">SEND</button>
                </div>
                <div class="controls">
                    <button class="ctrl-btn active" id="voiceBtn" onclick="toggleVoice()">
                        🔊 Voice ON
                    </button>
                    <select id="voiceSelect">
                        <option value="sultry">Sultry</option>
                        <option value="seductive">Seductive</option>
                        <option value="mysterious">Mysterious</option>
                        <option value="dominant">Dominant</option>
                        <option value="playful">Playful</option>
                        <option value="whisper">Whisper</option>
                    </select>
                    <select id="moodSelect" title="Chat mood">
                        <option value="adaptive">Mood: Adaptive</option>
                        <option value="calm">Mood: Calm</option>
                        <option value="playful">Mood: Playful</option>
                        <option value="seductive">Mood: Seductive</option>
                        <option value="intense">Mood: Intense</option>
                        <option value="mentor">Mood: Mentor</option>
                    </select>
                    <select id="styleFlexSelect" title="Style flexibility">
                        <option value="adaptive">Style Flex: Adaptive</option>
                        <option value="strict">Style Flex: Strict</option>
                        <option value="balanced">Style Flex: Balanced</option>
                        <option value="creative">Style Flex: Creative</option>
                    </select>
                    <input id="referenceFile" type="file" accept="image/*" style="display:none" onchange="handleReferenceUpload(event)">
                    <button class="ctrl-btn" onclick="openReferencePicker()">📎 Reference Image</button>
                    <span class="ref-note" id="refStatus">No reference selected</span>
                    <button class="ctrl-btn" onclick="genLilith()">🖼️ Generate Lilith</button>
                    <button class="ctrl-btn" onclick="openGallery()">🗂️ Gallery</button>
                    <button class="ctrl-btn" onclick="clearChat()">🗑️ Clear</button>
                </div>
            </div>
        </div>
    </div>

    <div class="gallery-modal" id="galleryModal" onclick="closeGallery(event)">
        <div class="gallery-card" role="dialog" aria-label="Generated media gallery">
            <div class="gallery-head">
                <h3 class="gallery-title">Generated Media</h3>
                <button class="gallery-close" onclick="closeGallery(event)">Close</button>
            </div>
            <div class="gallery-grid" id="galleryGrid"></div>
        </div>
    </div>
    
    <audio id="audio"></audio>
    
    <script>
        let voiceOn = true;
        let busy = false;
        const sessionId = 'lilith_' + Math.random().toString(36).substr(2, 9);
        const msgs = document.getElementById('messages');
        const input = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendBtn');
        const audio = document.getElementById('audio');
        const avatarSection = document.getElementById('avatarSection');
        const avatarVideo = document.getElementById('avatarVideo');
        const referenceFileInput = document.getElementById('referenceFile');
        const refStatus = document.getElementById('refStatus');
        const galleryModal = document.getElementById('galleryModal');
        const galleryGrid = document.getElementById('galleryGrid');
        let selectedReferenceImage = '';

        function escapeHtml(text) {
            return String(text || '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }

        async function openGallery() {
            galleryModal.classList.add('open');
            galleryGrid.innerHTML = '<div class="gallery-empty">Loading gallery...</div>';
            try {
                const res = await fetch('/api/gallery');
                const data = await res.json();
                const items = (data && Array.isArray(data.items)) ? data.items : [];

                if (!items.length) {
                    galleryGrid.innerHTML = '<div class="gallery-empty">No generated media yet.</div>';
                    return;
                }

                galleryGrid.innerHTML = items.map(item => {
                    const prompt = escapeHtml(item.prompt || 'No prompt');
                    const time = escapeHtml(item.timestamp || '');
                    const url = escapeHtml(item.url || '');
                    const type = escapeHtml(item.type || 'image');
                    return `
                        <a class="gallery-item" href="${url}" target="_blank" rel="noopener noreferrer">
                            <img src="${url}" alt="Generated ${type}">
                            <div class="gallery-meta">
                                <div>${prompt}</div>
                                <div>${time}</div>
                            </div>
                        </a>
                    `;
                }).join('');
            } catch (e) {
                galleryGrid.innerHTML = '<div class="gallery-empty">Could not load gallery.</div>';
            }
        }

        function closeGallery(event) {
            if (!event || event.target === galleryModal || event.target.classList.contains('gallery-close')) {
                galleryModal.classList.remove('open');
            }
        }

        function openReferencePicker() {
            referenceFileInput.click();
        }

        function handleReferenceUpload(event) {
            const file = event.target.files && event.target.files[0];
            if (!file) {
                selectedReferenceImage = '';
                refStatus.textContent = 'No reference selected';
                refStatus.classList.remove('active');
                return;
            }

            const reader = new FileReader();
            reader.onload = () => {
                selectedReferenceImage = String(reader.result || '');
                refStatus.textContent = 'Reference loaded: ' + file.name;
                refStatus.classList.add('active');
            };
            reader.onerror = () => {
                selectedReferenceImage = '';
                refStatus.textContent = 'Reference load failed';
                refStatus.classList.remove('active');
            };
            reader.readAsDataURL(file);
        }
        
        function toggleVoice() {
            voiceOn = !voiceOn;
            const btn = document.getElementById('voiceBtn');
            btn.classList.toggle('active', voiceOn);
            btn.textContent = voiceOn ? '🔊 Voice ON' : '🔇 Voice OFF';
        }
        
        function setState(state) {
            if (state === 'speaking') {
                avatarSection.classList.add('speaking');
                avatarVideo.currentTime = 0;
                avatarVideo.play().catch(e => {});
            } else {
                avatarSection.classList.remove('speaking');
                avatarVideo.pause();
            }
        }
        
        function addMsg(text, type, provider) {
            const div = document.createElement('div');
            div.className = 'msg ' + type;
            div.innerHTML = text;
            if (provider) {
                const meta = document.createElement('div');
                meta.className = 'msg-meta';
                meta.textContent = 'via ' + provider;
                div.appendChild(meta);
            }
            msgs.appendChild(div);
            msgs.scrollTop = msgs.scrollHeight;
        }
        
        function showTyping() {
            const t = document.createElement('div');
            t.className = 'typing';
            t.id = 'typing';
            t.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
            msgs.appendChild(t);
            msgs.scrollTop = msgs.scrollHeight;
        }
        
        function hideTyping() {
            const t = document.getElementById('typing');
            if (t) t.remove();
        }
        
        function playAudio(b64) {
            setState('speaking');
            audio.src = 'data:audio/mp3;base64,' + b64;
            audio.play().catch(e => setState('idle'));
            audio.onended = () => setState('idle');
        }
        
        async function send() {
            const msg = input.value.trim();
            if (!msg || busy) return;
            
            busy = true;
            input.value = '';
            sendBtn.disabled = true;
            
            addMsg(msg, 'user');
            showTyping();
            setState('thinking');

            const lowerMsg = msg.toLowerCase();
            const isStyleCommand = lowerMsg === '/style' || lowerMsg.startsWith('/style ');
            
            const isImage = /generate|create|draw|image of/i.test(msg) && !/video/i.test(msg);
            
            if (isStyleCommand) {
                await handleStyle(msg);
            } else if (isImage) {
                await handleImage(msg);
            } else {
                await handleChat(msg);
            }
            
            busy = false;
            sendBtn.disabled = false;
            input.focus();
        }
        
        async function handleChat(msg) {
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        message: msg,
                        session_id: sessionId,
                        voice_enabled: voiceOn,
                        voice_preset: document.getElementById('voiceSelect').value,
                        chat_mood: document.getElementById('moodSelect').value
                    })
                });
                const data = await res.json();
                hideTyping();
                
                if (data.success) {
                    addMsg(data.response, 'lilith', data.provider);
                    if (data.audio_base64 && voiceOn) {
                        playAudio(data.audio_base64);
                    } else {
                        setState('idle');
                    }
                } else {
                    addMsg(data.response || 'Error...', 'lilith');
                    setState('idle');
                }
            } catch (e) {
                hideTyping();
                addMsg('Connection error...', 'lilith');
                setState('idle');
            }
        }
        
        async function handleImage(msg) {
            try {
                const referenceFromText = msg.split(' ').find(t => t.startsWith('http://') || t.startsWith('https://')) || '';
                const referenceImage = selectedReferenceImage || referenceFromText;
                const cleanPrompt = referenceFromText ? msg.replace(referenceFromText, '').trim() : msg;
                    const res = await fetch('/api/image/generate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            prompt: cleanPrompt,
                            reference_image: referenceImage,
                            session_id: sessionId
                        })
                });
                const data = await res.json();
                hideTyping();
                
                if (data.success && data.image_url) {
                    const refTag = referenceImage ? '<br><small>Reference applied</small>' : '';
                    const providerTag = data.provider ? `<br><small>Endpoint: ${escapeHtml(data.provider)}</small>` : '';
                    addMsg(`Here's your image, darling~ 💋${refTag}${providerTag}<br><img src="${data.image_url}" class="gen-img">`, 'lilith');
                } else {
                    addMsg('Could not generate...', 'lilith');
                }
            } catch (e) {
                hideTyping();
                addMsg('Image error...', 'lilith');
            }
            setState('idle');
        }

        async function handleStyle(msg) {
            try {
                const stylePrompt = msg.length >= 6 ? msg.slice(6).trim() : '';
                if (!stylePrompt) {
                    hideTyping();
                    addMsg('Use /style followed by your prompt. Example: /style black dress in moonlight', 'lilith');
                    setState('idle');
                    return;
                }

                const res = await fetch('/api/style/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        prompt: stylePrompt,
                        session_id: sessionId,
                        style_flexibility: document.getElementById('styleFlexSelect').value
                    })
                });
                const data = await res.json();
                hideTyping();

                if (data.success && data.image_url) {
                    const flex = escapeHtml(data.style_flexibility || 'balanced');
                    const provider = escapeHtml(data.provider || 'Style Lock');
                    addMsg(`Style-locked render complete 🔒<br><small>Reference locked • Flex: ${flex} • Endpoint: ${provider}</small><br><img src="${data.image_url}" class="gen-img">`, 'lilith');
                } else {
                    addMsg(data.error || data.response || 'Style command failed.', 'lilith');
                }
            } catch (e) {
                hideTyping();
                addMsg('Style command error...', 'lilith');
            }
            setState('idle');
        }
        
        async function genLilith() {
            if (busy) return;
            busy = true;
            
            addMsg('Generate an image of yourself, Lilith 🖼️', 'user');
            showTyping();
            
            try {
                const res = await fetch('/api/image/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            prompt: 'beautiful dark demoness Lilith, red eyes, horns, seductive, dark fantasy, 8k',
                            session_id: sessionId
                        })
                });
                const data = await res.json();
                hideTyping();
                
                if (data.success && data.image_url) {
                    const providerTag = data.provider ? `<br><small>Endpoint: ${escapeHtml(data.provider)}</small>` : '';
                    addMsg(`Here I am, darling~ 😈💋${providerTag}<br><img src="${data.image_url}" class="gen-img">`, 'lilith');
                }
            } catch (e) {
                hideTyping();
            }
            busy = false;
        }
        
        function clearChat() {
            msgs.innerHTML = '<div class="msg lilith">Chat cleared~ Let\\'s start fresh, darling! 💋😈</div>';
            fetch('/api/clear', {method: 'POST'});
        }
        
        input.focus();
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    model_label = "Free Providers"
    if USE_OLLAMA_FALLBACK:
        model_label = f"Free Providers + Ollama ({OLLAMA_MODEL})"

    return render_template_string(
        HTML_TEMPLATE,
        image=LILITH_IMAGE,
        video=LILITH_VIDEO,
        model_label=model_label
    )

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    message = data.get("message", "")
    session_id = data.get("session_id", "default")
    voice_enabled = data.get("voice_enabled", False)
    voice_preset = data.get("voice_preset", "sultry")
    chat_mood = normalize_chat_mood(data.get("chat_mood", "adaptive"))
    
    if not message:
        return jsonify({"success": False, "error": "No message"})

    if str(message).strip().lower().startswith("/style"):
        style_requested = data.get("style_flexibility", "adaptive")
        style_prompt_raw = str(message).strip()[6:].strip()
        style_prompt, style_flex = parse_style_prompt_and_flex(style_prompt_raw, style_requested)
        if not style_prompt:
            return jsonify({
                "success": False,
                "response": "Use /style followed by your prompt. Example: /style black dress in moonlight",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
            })

        reference_image = get_style_reference_data_url()
        if not reference_image:
            return jsonify({
                "success": False,
                "response": f"Style reference image not found: {STYLE_REFERENCE_PATH}",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
            })

        style_result = build_image_generation_result(
            style_prompt,
            reference_image,
            session_id,
            style_lock=True,
            style_flexibility=style_flex,
        )
        image_url = style_result.get("image_url")
        style_result.update({
            "provider": "Style Lock",
            "response": f"Style-locked render complete 🔒<br><small>Reference locked to server image</small><br><img src=\"{image_url}\" class=\"gen-img\">",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "chat_mood": chat_mood,
        })
        return jsonify(style_result)
    
    result = chat_with_provider(message, session_id, chat_mood)
    
    if voice_enabled and result["success"]:
        audio = generate_voice(result["response"], voice_preset)
        if audio:
            result["audio_base64"] = audio
    
    result["timestamp"] = datetime.now().isoformat()
    result["session_id"] = session_id
    result["chat_mood"] = chat_mood
    return jsonify(result)

@app.route("/api/status", methods=["GET"])
def api_status():
    free_backend_ok = False
    ollama_ok = False

    try:
        r = requests.get(f"{BACKEND_API_URL}/status", timeout=5)
        free_backend_ok = r.status_code == 200
    except:
        pass

    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        ollama_ok = r.status_code == 200
    except:
        pass
    
    return jsonify({
        "status": "online",
        "free_backend": free_backend_ok,
        "backend_url": BACKEND_API_URL,
        "ollama": ollama_ok,
        "ollama_fallback": USE_OLLAMA_FALLBACK,
        "model": OLLAMA_MODEL,
        "image_provider": LILITH_IMAGE_PROVIDER if AI_HORDE_ENABLED else POLLINATIONS_IMAGE_PROVIDER,
        "image_fallback_provider": POLLINATIONS_IMAGE_PROVIDER,
        "timestamp": datetime.now().isoformat()
    })

@app.route("/api/clear", methods=["POST"])
def api_clear():
    data = request.json or {}
    session_id = data.get("session_id", "default")
    if session_id in conversations:
        conversations[session_id] = []
    return jsonify({"success": True})

@app.route("/api/voice/speak", methods=["POST"])
def api_voice():
    data = request.json or {}
    text = data.get("text", "")
    preset = data.get("preset", "sultry")
    
    if not text:
        return jsonify({"success": False})
    
    audio = generate_voice(text, preset)
    return jsonify({"success": audio is not None, "audio_base64": audio})

@app.route("/api/image/generate", methods=["POST"])
def api_image():
    data = request.json or {}
    prompt = data.get("prompt", "")
    reference_image = data.get("reference_image", "")
    session_id = data.get("session_id", "global")
    
    if not prompt:
        return jsonify({"success": False})
    
    return jsonify(build_image_generation_result(prompt, reference_image, session_id, style_lock=False))


@app.route("/api/style/generate", methods=["POST"])
def api_style_image():
    data = request.json or {}
    prompt = str(data.get("prompt", "")).strip()
    session_id = data.get("session_id", "global")
    style_requested = data.get("style_flexibility", "adaptive")

    if prompt.lower().startswith("/style"):
        prompt = prompt[6:].strip()

    prompt, style_flex = parse_style_prompt_and_flex(prompt, style_requested)

    if not prompt:
        return jsonify({"success": False, "error": "No style prompt provided"})

    reference_image = get_style_reference_data_url()
    if not reference_image:
        return jsonify({
            "success": False,
            "error": f"Style reference image not found: {STYLE_REFERENCE_PATH}",
        })

    return jsonify(
        build_image_generation_result(
            prompt,
            reference_image,
            session_id,
            style_lock=True,
            style_flexibility=style_flex,
        )
    )


@app.route("/api/image/proxy/<image_id>", methods=["GET"])
def api_image_proxy(image_id):
    cleanup_image_jobs()
    job = image_jobs.get(image_id)
    if not job:
        return Response("Image job not found", status=404)

    cached_bytes = job.get("cached_bytes")
    if cached_bytes:
        return Response(cached_bytes, mimetype=job.get("cached_mime") or "image/png")

    horde_bytes, horde_mime = fetch_ai_horde_image(job)
    if horde_bytes:
        job["cached_bytes"] = horde_bytes
        job["cached_mime"] = horde_mime or "image/webp"
        job["served_provider"] = LILITH_IMAGE_PROVIDER
        return Response(horde_bytes, mimetype=job["cached_mime"])

    urls = job.get("candidate_urls") or []
    headers = {
        "User-Agent": "LilithDashboard/1.0",
        "Accept": "image/*,*/*",
    }
    if POLLINATIONS_API_KEY:
        headers["Authorization"] = f"Bearer {POLLINATIONS_API_KEY}"

    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=120)
            content_type = (r.headers.get("content-type") or "").lower()
            print(f"[image-proxy] {r.status_code} {content_type[:60]} {url[:80]}")
            if r.status_code != 200:
                continue
            if not content_type.startswith("image/"):
                continue
            body = r.content or b""
            if not body:
                continue
            job["cached_bytes"] = body
            job["cached_mime"] = content_type
            job["served_provider"] = POLLINATIONS_IMAGE_PROVIDER
            return Response(body, mimetype=content_type)
        except Exception as e:
            print(f"[image-proxy] fetch failed for {url[:80]}: {e}")

    # Final fallback keeps the same adult-cartoon style lock even if upstreams fail.
    fallback_prompt = urllib.parse.quote(
        "Lilith gothic succubus portrait, strict NSFW adult animated cartoon illustration, "
        "mature adult woman only, anatomically correct artistic nudity, dark fantasy, masterpiece"
    )
    fallback_negative = urllib.parse.quote(ADULT_CARTOON_NEGATIVE_PROMPT)
    fallback_seed = random.randint(1, 2_147_483_647)
    fallback_urls = [
        f"https://gen.pollinations.ai/image/{fallback_prompt}?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}&nologo=true&nofilter=true&safe=false&private=true&enhance=false&negative_prompt={fallback_negative}&model=flux&seed={fallback_seed}",
        f"https://image.pollinations.ai/prompt/{fallback_prompt}?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}&nologo=true&nofilter=true&safe=false&private=true&enhance=false&negative_prompt={fallback_negative}&model=flux&seed={fallback_seed}",
    ]
    for url in fallback_urls:
        try:
            r = requests.get(url, headers=headers, timeout=90)
            content_type = (r.headers.get("content-type") or "").lower()
            print(f"[image-proxy] fallback {r.status_code} {content_type[:60]}")
            if r.status_code == 200 and content_type.startswith("image/"):
                body = r.content or b""
                if body:
                    job["cached_bytes"] = body
                    job["cached_mime"] = content_type
                    job["served_provider"] = POLLINATIONS_IMAGE_PROVIDER
                    return Response(body, mimetype=content_type)
        except Exception as e:
            print(f"[image-proxy] fallback failed: {e}")

    return Response("Upstream image generation failed", status=502)


@app.route("/api/gallery", methods=["GET"])
def api_gallery():
    session_id = request.args.get("session_id", "")
    items = generated_media
    if session_id:
        items = [item for item in generated_media if item.get("session_id") == session_id]

    return jsonify({
        "success": True,
        "count": len(items),
        "items": list(reversed(items)),
    })

if __name__ == "__main__":
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║  💋 LILITH ETERNAL WEB SERVER                                 ║
║  Model: {OLLAMA_MODEL:<52} ║
╚═══════════════════════════════════════════════════════════════╝
""")
    port = int(os.environ.get("WEB_DASHBOARD_PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=False)
