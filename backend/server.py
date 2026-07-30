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
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

# Load .env from backend/
load_dotenv(Path(__file__).parent / ".env")

# Make services importable
sys.path.insert(0, str(Path(__file__).parent))

from services.eternal_ai_engine import get_eternal_engine  # noqa: E402
from services.face_swap import get_face_swap_engine  # noqa: E402
from services.gallery import get_gallery  # noqa: E402
from services.lilith_elevenlabs_voice import get_voice_engine  # noqa: E402
from services.lilith_image_generator import OUTFITS, POSES, SCENES, get_image_generator  # noqa: E402
from services.pose_controlnet import get_pose_controlnet_engine  # noqa: E402
from services.presets import PRESETS_DIR, get_preset_store, seed_starter_presets  # noqa: E402
from services.reference import get_pose_reference_store, get_reference_store  # noqa: E402

app = FastAPI(title="Lilith Companion API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _restore_state() -> None:
    """Load persisted preferences (voice_id) from Mongo at startup."""
    try:
        from services.db import state_col
        doc = state_col().find_one({"key": "voice_id"}, {"_id": 0, "voice_id": 1})
        if doc and doc.get("voice_id"):
            get_voice_engine().set_default_voice(doc["voice_id"])
    except Exception:
        pass
    # Seed starter presets on first boot
    try:
        added = seed_starter_presets()
        if added:
            print(f"[STARTUP] seeded {added} starter presets")
    except Exception as e:
        print(f"[STARTUP] preset seeding skipped: {e}")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str = Field(default="default")


class VoiceRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    voice_id: Optional[str] = Field(default=None, max_length=64)


class SetVoiceRequest(BaseModel):
    voice_id: str = Field(..., min_length=1, max_length=64)


class ImageRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)
    seed: Optional[int] = Field(default=None, ge=0, le=2**32 - 1)


class LilithImageRequest(BaseModel):
    outfit: Optional[str] = Field(default="random", max_length=200)
    custom_prompt: Optional[str] = Field(default=None, max_length=600)
    scene: Optional[str] = Field(default=None, max_length=200)
    pose: Optional[str] = Field(default=None, max_length=200)
    seed: Optional[int] = Field(default=None, ge=0, le=2**32 - 1)
    use_reference: bool = Field(default=True)
    reference_strength: Optional[float] = Field(default=None, ge=0.05, le=0.95)
    use_face_swap: bool = Field(default=False)
    use_pose_controlnet: bool = Field(default=False)


class SetGalleryReferenceRequest(BaseModel):
    gallery_id: str = Field(..., min_length=1, max_length=64)
    strength: float = Field(default=0.32, ge=0.05, le=0.95)


class SetStrengthRequest(BaseModel):
    strength: float = Field(..., ge=0.05, le=0.95)


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
        "face_swap": get_face_swap_engine().get_status(),
        "pose_controlnet": get_pose_controlnet_engine().get_status(),
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
    audio_b64: Optional[str] = voice.generate_speech(req.text, voice_id=req.voice_id)
    if not audio_b64:
        raise HTTPException(status_code=503, detail="Voice synthesis unavailable")
    return {"success": True, "audio_base64": audio_b64, "format": "mp3"}


@app.get("/api/voice/list")
def api_voice_list():
    voice = get_voice_engine()
    voices = voice.list_voices()
    # Persist chosen voice into state_col for restoration on reload
    from services.db import state_col
    doc = state_col().find_one({"key": "voice_id"}, {"_id": 0, "voice_id": 1})
    current = (doc or {}).get("voice_id") or voice.voice_id
    voice.set_default_voice(current)
    return {"count": len(voices), "voices": voices, "current": current}


@app.post("/api/voice/select")
def api_voice_select(req: SetVoiceRequest):
    voice = get_voice_engine()
    voice.set_default_voice(req.voice_id)
    from services.db import state_col
    state_col().update_one(
        {"key": "voice_id"}, {"$set": {"key": "voice_id", "voice_id": req.voice_id}}, upsert=True,
    )
    return {"current": req.voice_id}


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
    - `custom_prompt` (if set) is used as the outfit description; otherwise `outfit` is used.
    - `scene` and `pose` are optional catalog IDs (or free-text) appended to the prompt.
    - `seed` pins the face across generations. Omit for random.
    - When a reference image is set and `use_reference` is true, uses img2img.
    """
    image = get_image_generator()
    seed = _resolve_seed(req.seed)

    # Resolve reference image (if enabled)
    ref_path: Optional[str] = None
    ref_strength: float = 0.32
    if req.use_reference:
        ref = get_reference_store().get()
        if ref:
            ref_path = ref.local_path()
            ref_strength = req.reference_strength if req.reference_strength is not None else ref.strength

    # Resolve pose reference (secondary — anchors body position)
    pose_ref = get_pose_reference_store().get()
    pose_ref_path = pose_ref.local_path() if pose_ref else None

    # Build the prompt (outfit vs custom_prompt) with optional pose/scene
    from services.lilith_image_generator import (  # noqa: E402
        LILITH_BASE, QUALITY_POSITIVE, _pose_prompt, _scene_prompt,
    )
    pose_frag = _pose_prompt(req.pose)
    scene_frag = _scene_prompt(req.scene)
    if pose_ref_path:
        # Bake a hint so plain img2img/txt2img providers still respect the pose intent.
        pose_hint = "matching the exact body pose and framing of the reference photo, faithful body language"
        pose_frag = f"{pose_frag}, {pose_hint}" if pose_frag else pose_hint

    if req.custom_prompt:
        parts = [LILITH_BASE, req.custom_prompt.strip()]
        if pose_frag: parts.append(pose_frag)
        if scene_frag: parts.append(scene_frag)
        parts.append(QUALITY_POSITIVE)
        prompt = ", ".join(parts)
        used_pose_ctrl = False
        gen_ref_path = ref_path
        gen_ref_strength = ref_strength
        if req.use_pose_controlnet and pose_ref_path:
            skeleton = get_pose_controlnet_engine().extract_skeleton(pose_ref_path)
            if skeleton:
                # Use the extracted skeleton as the img2img reference at high
                # strength so the pose dominates. Face fidelity is then layered
                # back on top via face-swap post-processing.
                gen_ref_path = skeleton
                gen_ref_strength = 0.62
                used_pose_ctrl = True
        data = image.generate_image(
            prompt, seed=seed,
            reference_path=gen_ref_path, reference_strength=gen_ref_strength,
        )
        label = req.custom_prompt.strip()[:60]
        outfit_used = None
    else:
        outfit_id = (req.outfit or "random").strip()
        used_pose_ctrl = False
        gen_ref_path = ref_path
        gen_ref_strength = ref_strength
        if req.use_pose_controlnet and pose_ref_path:
            skeleton = get_pose_controlnet_engine().extract_skeleton(pose_ref_path)
            if skeleton:
                gen_ref_path = skeleton
                gen_ref_strength = 0.62
                used_pose_ctrl = True
        data = image.generate_lilith_image(
            outfit_style=outfit_id, seed=seed,
            scene=req.scene, pose=req.pose,
            reference_path=gen_ref_path, reference_strength=gen_ref_strength,
        )
        entry_meta = OUTFITS.get(outfit_id)
        label_bits = [entry_meta["label"] if entry_meta else outfit_id]
        if req.scene and SCENES.get(req.scene): label_bits.append(SCENES[req.scene]["label"])
        if req.pose and POSES.get(req.pose): label_bits.append(POSES[req.pose]["label"])
        label = " · ".join(label_bits)
        outfit_used = outfit_id if outfit_id != "random" else None
        prompt = None

    if not data:
        raise HTTPException(status_code=503, detail="Image generation failed")

    # Optional face-swap post-processing (requires an active face reference).
    # Runs on top of whatever we just generated — including pose-ControlNet output.
    used_face_swap = False
    if req.use_face_swap and ref_path:
        swapped = get_face_swap_engine().swap(data, ref_path)
        if swapped:
            data = swapped
            used_face_swap = True

    provider_label = image.last_provider or ""
    if used_pose_ctrl:
        provider_label = f"OpenPose skeleton → {provider_label}" if provider_label else "OpenPose skeleton"
    if used_face_swap:
        provider_label = f"{provider_label} + FaceSwap" if provider_label else "FaceSwap"

    entry = get_gallery().add(
        data,
        label=label,
        outfit=outfit_used,
        prompt=prompt,
        seed=seed,
        provider=provider_label or image.last_provider,
    )
    return {
        "success": True,
        "provider": provider_label or image.last_provider,
        "seed": seed,
        "outfit": outfit_used,
        "scene": req.scene,
        "pose": req.pose,
        "used_reference": ref_path is not None,
        "used_pose_reference": pose_ref_path is not None,
        "used_pose_controlnet": used_pose_ctrl,
        "used_face_swap": used_face_swap,
        "gallery_id": entry.id,
        "url": entry.to_public()["url"],
        "mime": entry.mime,
    }


@app.get("/api/image/outfits")
def api_image_outfits():
    items = [
        {"id": oid, "label": data["label"], "category": data["category"]}
        for oid, data in OUTFITS.items()
    ]
    grouped: dict[str, list] = {}
    for it in items:
        grouped.setdefault(it["category"], []).append({"id": it["id"], "label": it["label"]})
    return {"outfits": items, "by_category": grouped, "count": len(items)}


@app.get("/api/image/scenes")
def api_image_scenes():
    items = [{"id": sid, "label": data["label"]} for sid, data in SCENES.items()]
    return {"scenes": items, "count": len(items)}


@app.get("/api/image/poses")
def api_image_poses():
    items = [{"id": pid, "label": data["label"]} for pid, data in POSES.items()]
    return {"poses": items, "count": len(items)}


# ---------------------------------------------------------------------------
# Reference (face anchor) image
# ---------------------------------------------------------------------------

@app.get("/api/reference")
def api_reference_get():
    ref = get_reference_store().get()
    if not ref:
        return {"active": False}
    return {"active": True, **ref.to_public()}


@app.post("/api/reference/gallery")
def api_reference_set_gallery(req: SetGalleryReferenceRequest):
    try:
        ref = get_reference_store().set_gallery(req.gallery_id, strength=req.strength)
    except KeyError:
        raise HTTPException(status_code=404, detail="Gallery entry not found")
    return {"active": True, **ref.to_public()}


@app.post("/api/reference/upload")
async def api_reference_upload(
    file: UploadFile = File(...),
    strength: float = 0.32,
):
    data = await file.read()
    if not data or len(data) < 100:
        raise HTTPException(status_code=400, detail="Empty upload")
    if len(data) > 15 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 15MB)")
    ref = get_reference_store().set_upload(data, strength=max(0.05, min(0.95, strength)))
    return {"active": True, **ref.to_public()}


@app.post("/api/reference/strength")
def api_reference_strength(req: SetStrengthRequest):
    ref = get_reference_store().set_strength(req.strength)
    if not ref:
        raise HTTPException(status_code=400, detail="No active reference")
    return {"active": True, **ref.to_public()}


@app.delete("/api/reference")
def api_reference_clear():
    get_reference_store().clear()
    return {"active": False}


# ---- Pose reference (secondary anchor) ----------------------------------

@app.get("/api/pose_reference")
def api_pose_reference_get():
    ref = get_pose_reference_store().get()
    if not ref:
        return {"active": False}
    return {"active": True, **ref.to_public()}


@app.post("/api/pose_reference/upload")
async def api_pose_reference_upload(file: UploadFile = File(...)):
    data = await file.read()
    if not data or len(data) < 100:
        raise HTTPException(status_code=400, detail="Empty upload")
    if len(data) > 15 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 15MB)")
    ref = get_pose_reference_store().set_upload(data)
    return {"active": True, **ref.to_public()}


@app.delete("/api/pose_reference")
def api_pose_reference_clear():
    get_pose_reference_store().clear()
    return {"active": False}


@app.get("/api/reference/file/{filename}")
def api_reference_file(filename: str):
    # Only serve files inside REF_DIR
    from services.reference import REF_DIR
    safe = REF_DIR / Path(filename).name
    if not safe.exists() or not safe.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    data = safe.read_bytes()
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        mime = "image/webp"
    elif data.startswith(b"\x89PNG"):
        mime = "image/png"
    elif data.startswith(b"\xff\xd8"):
        mime = "image/jpeg"
    else:
        mime = "application/octet-stream"
    return Response(content=data, media_type=mime)


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
            "GET  /api/presets",
            "POST /api/presets",
            "POST /api/presets/{id}/apply",
            "DELETE /api/presets/{id}",
        ],
    }


# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------

class PresetCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    outfit: Optional[str] = Field(default=None, max_length=200)
    custom_prompt: Optional[str] = Field(default=None, max_length=600)
    scene: Optional[str] = Field(default=None, max_length=200)
    pose: Optional[str] = Field(default=None, max_length=200)
    seed: Optional[int] = Field(default=None, ge=0, le=2**32 - 1)
    voice_id: Optional[str] = Field(default=None, max_length=64)
    reference_strength: float = Field(default=0.32, ge=0.05, le=0.95)
    favorite_scenes: Optional[list] = Field(default=None)
    # If true, also snapshot the currently-active face + pose reference
    include_face_reference: bool = Field(default=True)
    include_pose_reference: bool = Field(default=True)
    # Optional gallery entry id used as the thumbnail
    thumbnail_gallery_id: Optional[str] = Field(default=None, max_length=64)


@app.get("/api/presets")
def api_presets_list():
    presets = get_preset_store().list()
    return {"count": len(presets), "presets": [p.to_public() for p in presets]}


@app.post("/api/presets")
def api_presets_create(req: PresetCreateRequest):
    face_src: Optional[str] = None
    pose_src: Optional[str] = None
    if req.include_face_reference:
        fr = get_reference_store().get()
        face_src = fr.local_path() if fr else None
    if req.include_pose_reference:
        pr = get_pose_reference_store().get()
        pose_src = pr.local_path() if pr else None

    thumb_bytes: Optional[bytes] = None
    if req.thumbnail_gallery_id:
        entry = get_gallery().get(req.thumbnail_gallery_id)
        if entry and entry.path.exists():
            thumb_bytes = entry.path.read_bytes()

    preset = get_preset_store().create(
        name=req.name,
        outfit=req.outfit,
        custom_prompt=req.custom_prompt,
        scene=req.scene,
        pose=req.pose,
        seed=req.seed,
        voice_id=req.voice_id,
        reference_strength=req.reference_strength,
        face_ref_src=face_src,
        pose_ref_src=pose_src,
        thumbnail_bytes=thumb_bytes,
        favorite_scenes=req.favorite_scenes or [],
    )
    return preset.to_public()


@app.delete("/api/presets/{preset_id}")
def api_presets_delete(preset_id: str):
    ok = get_preset_store().delete(preset_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Preset not found")
    return {"success": True}


@app.get("/api/presets/{preset_id}/thumbnail")
def api_presets_thumbnail(preset_id: str):
    store = get_preset_store()
    p = store.thumbnail_path(preset_id)
    if not p:
        raise HTTPException(status_code=404, detail="No thumbnail")
    return Response(content=p.read_bytes(), media_type=store.thumbnail_mime(preset_id))


@app.post("/api/presets/{preset_id}/apply")
def api_presets_apply(preset_id: str):
    """
    Load a preset into the live state:
      - switches active voice (persisted)
      - restores face/pose reference from the preset's snapshot
      - returns the outfit/scene/pose/seed the frontend should use for the next generation
    """
    preset = get_preset_store().get(preset_id)
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")

    # Voice
    if preset.voice_id:
        try:
            get_voice_engine().set_default_voice(preset.voice_id)
            from services.db import state_col
            state_col().update_one(
                {"key": "voice_id"},
                {"$set": {"key": "voice_id", "voice_id": preset.voice_id}},
                upsert=True,
            )
        except Exception:
            pass

    # Face + pose references (snapshot -> live)
    if preset.face_ref_path and Path(preset.face_ref_path).exists():
        try:
            data = Path(preset.face_ref_path).read_bytes()
            get_reference_store().set_upload(data, strength=preset.reference_strength)
        except Exception:
            pass
    if preset.pose_ref_path and Path(preset.pose_ref_path).exists():
        try:
            data = Path(preset.pose_ref_path).read_bytes()
            get_pose_reference_store().set_upload(data)
        except Exception:
            pass

    return {
        "success": True,
        "preset": preset.to_public(),
        "apply": {
            "outfit": preset.outfit,
            "custom_prompt": preset.custom_prompt,
            "scene": preset.scene,
            "pose": preset.pose,
            "seed": preset.seed,
            "voice_id": preset.voice_id,
            "reference_strength": preset.reference_strength,
        },
    }
