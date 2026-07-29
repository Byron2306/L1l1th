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
from services.lilith_elevenlabs_voice import get_voice_engine  # noqa: E402
from services.lilith_image_generator import get_image_generator  # noqa: E402

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


@app.post("/api/image/generate")
def api_image_generate(req: ImageRequest):
    image = get_image_generator()
    data = image.generate_image(req.prompt)
    if not data:
        raise HTTPException(status_code=503, detail="Image generation failed")
    b64 = base64.b64encode(data).decode("utf-8")
    return {
        "success": True,
        "provider": image.last_provider,
        "image_base64": b64,
        "mime": "image/png",
    }


@app.get("/api/image/outfits")
def api_image_outfits():
    """List all named outfits (id, label, category) for the outfit picker UI."""
    from services.lilith_image_generator import OUTFITS
    items = [
        {"id": oid, "label": data["label"], "category": data["category"]}
        for oid, data in OUTFITS.items()
    ]
    # Grouped view for convenience
    grouped: dict[str, list] = {}
    for it in items:
        grouped.setdefault(it["category"], []).append({"id": it["id"], "label": it["label"]})
    return {"outfits": items, "by_category": grouped, "count": len(items)}


@app.get("/api/image/lilith")
def api_image_lilith(outfit: str = "random"):
    image = get_image_generator()
    data = image.generate_lilith_image(outfit_style=outfit)
    if not data:
        raise HTTPException(status_code=503, detail="Image generation failed")
    # HF ZeroGPU Space returns WebP; Animagine/Pollinations return PNG/JPEG.
    # Sniff from magic bytes so browsers render correctly.
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        mime = "image/webp"
    elif data.startswith(b"\x89PNG"):
        mime = "image/png"
    elif data.startswith(b"\xff\xd8"):
        mime = "image/jpeg"
    else:
        mime = "application/octet-stream"
    return Response(content=data, media_type=mime)


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
