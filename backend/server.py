"""
Lilith Companion — Clean FastAPI backend.

Endpoints (all prefixed with /api):
  POST /api/chat              -> LLM chat via EternalAIEngine
  POST /api/clear             -> Clear conversation history
  GET  /api/status            -> Health / provider status
  POST /api/voice/speak       -> ElevenLabs (or Edge TTS fallback) audio
  POST /api/image/generate    -> Anime image generation (HF Space / Animagine / Pollinations / AI Horde)
  GET  /api/image/lilith      -> Random Lilith outfit image (returns bytes)
"""
from __future__ import annotations

import base64
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

# Load .env from backend/
load_dotenv(Path(__file__).parent / ".env")

# Make services importable
sys.path.insert(0, str(Path(__file__).parent))

from services.eternal_ai_engine import get_eternal_engine  # noqa: E402
from services.gallery import get_gallery  # noqa: E402
from services.lilith_elevenlabs_voice import get_voice_engine  # noqa: E402
from services.lilith_image_generator import OUTFITS, get_image_generator  # noqa: E402

app = FastAPI(title="Lilith Companion API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str = Field(default="default")


class VoiceRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class ImageRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)
    seed: Optional[int] = Field(default=None, ge=0, le=2**32 - 1)


class LilithImageRequest(BaseModel):
    outfit: Optional[str] = Field(default="random", max_length=200)
    custom_prompt: Optional[str] = Field(default=None, max_length=600)
    seed: Optional[int] = Field(default=None, ge=0, le=2**32 - 1)


class ClearRequest(BaseModel):
    session_id: str = Field(default="default")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/status")
def api_status():
    engine = get_eternal_engine()
    voice = get_voice_engine()
    image = get_image_generator()
    return {
        "status": "online",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "chat": engine.get_stats(),
        "voice": voice.get_status(),
        "image": image.get_status(),
    }


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    engine = get_eternal_engine()
    result = engine.chat(req.message)
    return {
        "success": bool(result.get("success")),
        "response": result.get("response", ""),
        "provider": result.get("provider"),
        "timestamp": result.get("timestamp", datetime.now(timezone.utc).isoformat()),
        "session_id": req.session_id,
    }


@app.post("/api/clear")
def api_clear(req: ClearRequest):
    engine = get_eternal_engine()
    engine.clear_history()
    return {"success": True, "session_id": req.session_id}


@app.post("/api/voice/speak")
def api_voice_speak(req: VoiceRequest):
    voice = get_voice_engine()
    audio_b64: Optional[str] = voice.generate_speech(req.text)
    if not audio_b64:
        raise HTTPException(status_code=503, detail="Voice synthesis unavailable")
    return {"success": True, "audio_base64": audio_b64, "format": "mp3"}


import random  # noqa: E402


def _resolve_seed(requested: Optional[int]) -> int:
    """Return a concrete seed to use (so we can record it in the gallery)."""
    if requested is not None:
        return int(requested)
    return random.randint(1, 2**31 - 1)


@app.post("/api/image/generate")
def api_image_generate(req: ImageRequest):
    image = get_image_generator()
    seed = _resolve_seed(req.seed)
    data = image.generate_image(req.prompt, seed=seed)
    if not data:
        raise HTTPException(status_code=503, detail="Image generation failed")
    entry = get_gallery().add(
        data,
        label=(req.prompt[:60] + "…") if len(req.prompt) > 60 else req.prompt,
        prompt=req.prompt,
        seed=seed,
        provider=image.last_provider,
    )
    return {
        "success": True,
        "provider": image.last_provider,
        "seed": seed,
        "gallery_id": entry.id,
        "url": entry.to_public()["url"],
        "mime": entry.mime,
    }


@app.post("/api/image/lilith")
def api_image_lilith_post(req: LilithImageRequest):
    """
    Generate a Lilith portrait.
    - If `custom_prompt` is provided, it's used as the outfit description (free-text).
    - Otherwise `outfit` is resolved from the named catalog.
    - `seed` pins the face across generations. Omit for random.
    """
    image = get_image_generator()
    seed = _resolve_seed(req.seed)

    if req.custom_prompt:
        from services.lilith_image_generator import LILITH_BASE, QUALITY_POSITIVE
        prompt = f"{LILITH_BASE}, {req.custom_prompt.strip()}, {QUALITY_POSITIVE}"
        data = image.generate_image(prompt, seed=seed)
        label = req.custom_prompt.strip()[:60]
        outfit_used = None
    else:
        outfit_id = (req.outfit or "random").strip()
        data = image.generate_lilith_image(outfit_style=outfit_id, seed=seed)
        entry_meta = OUTFITS.get(outfit_id)
        label = entry_meta["label"] if entry_meta else outfit_id
        outfit_used = outfit_id if outfit_id != "random" else None
        prompt = None

    if not data:
        raise HTTPException(status_code=503, detail="Image generation failed")

    entry = get_gallery().add(
        data,
        label=label,
        outfit=outfit_used,
        prompt=prompt,
        seed=seed,
        provider=image.last_provider,
    )
    return {
        "success": True,
        "provider": image.last_provider,
        "seed": seed,
        "outfit": outfit_used,
        "gallery_id": entry.id,
        "url": entry.to_public()["url"],
        "mime": entry.mime,
    }


@app.get("/api/image/outfits")
def api_image_outfits():
    """List all named outfits (id, label, category) for the outfit picker UI."""
    items = [
        {"id": oid, "label": data["label"], "category": data["category"]}
        for oid, data in OUTFITS.items()
    ]
    grouped: dict[str, list] = {}
    for it in items:
        grouped.setdefault(it["category"], []).append({"id": it["id"], "label": it["label"]})
    return {"outfits": items, "by_category": grouped, "count": len(items)}


@app.get("/api/image/lilith")
def api_image_lilith_get(outfit: str = "random", seed: Optional[int] = None):
    """Backwards-compatible GET — returns binary bytes. Also records in gallery."""
    image = get_image_generator()
    used_seed = _resolve_seed(seed)
    data = image.generate_lilith_image(outfit_style=outfit, seed=used_seed)
    if not data:
        raise HTTPException(status_code=503, detail="Image generation failed")
    entry_meta = OUTFITS.get(outfit)
    label = entry_meta["label"] if entry_meta else outfit
    get_gallery().add(
        data,
        label=label,
        outfit=outfit if outfit != "random" else None,
        seed=used_seed,
        provider=image.last_provider,
    )
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        mime = "image/webp"
    elif data.startswith(b"\x89PNG"):
        mime = "image/png"
    elif data.startswith(b"\xff\xd8"):
        mime = "image/jpeg"
    else:
        mime = "application/octet-stream"
    return Response(content=data, media_type=mime, headers={"X-Seed": str(used_seed)})


# ---------------------------------------------------------------------------
# Gallery
# ---------------------------------------------------------------------------

@app.get("/api/gallery")
def api_gallery_list():
    entries = get_gallery().list()
    return {"count": len(entries), "entries": entries}


@app.get("/api/gallery/{entry_id}")
def api_gallery_get(entry_id: str):
    entry = get_gallery().get(entry_id)
    if not entry or not entry.path.exists():
        raise HTTPException(status_code=404, detail="Not found")
    return Response(content=entry.path.read_bytes(), media_type=entry.mime)


@app.delete("/api/gallery/{entry_id}")
def api_gallery_delete(entry_id: str):
    ok = get_gallery().delete(entry_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    return {"success": True}


@app.get("/api/")
def api_root():
    return {
        "name": "Lilith Companion API",
        "endpoints": [
            "GET  /api/status",
            "POST /api/chat",
            "POST /api/clear",
            "POST /api/voice/speak",
            "POST /api/image/generate",
            "GET  /api/image/lilith?outfit=random",
        ],
    }
