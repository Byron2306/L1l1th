"""
Presets Library — save a whole look (outfit, scene, pose, voice, seed,
face + pose reference snapshot) as a named preset and load it in one tap.

Reference images are snapshotted into /app/data/presets/ so the preset stays
usable even if the user later clears or replaces their live face/pose reference.
"""
from __future__ import annotations

import os
import shutil
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from threading import Lock
from typing import List, Optional

from services.db import presets_col

PRESETS_DIR = Path(os.environ.get("LILITH_PRESETS_DIR", "/app/data/presets"))
PRESETS_DIR.mkdir(parents=True, exist_ok=True)


def _sniff_ext(data: bytes) -> str:
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "webp"
    if data.startswith(b"\x89PNG"):
        return "png"
    if data.startswith(b"\xff\xd8"):
        return "jpg"
    return "png"


def _mime_for(ext: str) -> str:
    return {"webp": "image/webp", "png": "image/png", "jpg": "image/jpeg"}.get(ext, "application/octet-stream")


@dataclass
class Preset:
    id: str
    name: str
    outfit: Optional[str] = None
    custom_prompt: Optional[str] = None
    scene: Optional[str] = None
    pose: Optional[str] = None
    seed: Optional[int] = None
    voice_id: Optional[str] = None
    reference_strength: float = 0.32
    # local file paths (already snapshotted into PRESETS_DIR)
    face_ref_path: Optional[str] = None
    pose_ref_path: Optional[str] = None
    # optional thumbnail (relative filename inside PRESETS_DIR)
    thumbnail: Optional[str] = None
    favorite_scenes: List[str] = field(default_factory=list)
    created_at: float = 0.0

    def to_mongo(self) -> dict:
        return asdict(self)

    @classmethod
    def from_mongo(cls, doc: dict) -> "Preset":
        return cls(
            id=doc["id"],
            name=doc.get("name", "Untitled"),
            outfit=doc.get("outfit"),
            custom_prompt=doc.get("custom_prompt"),
            scene=doc.get("scene"),
            pose=doc.get("pose"),
            seed=doc.get("seed"),
            voice_id=doc.get("voice_id"),
            reference_strength=float(doc.get("reference_strength", 0.32)),
            face_ref_path=doc.get("face_ref_path"),
            pose_ref_path=doc.get("pose_ref_path"),
            thumbnail=doc.get("thumbnail"),
            favorite_scenes=list(doc.get("favorite_scenes") or []),
            created_at=float(doc.get("created_at", time.time())),
        )

    def to_public(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "outfit": self.outfit,
            "custom_prompt": self.custom_prompt,
            "scene": self.scene,
            "pose": self.pose,
            "seed": self.seed,
            "voice_id": self.voice_id,
            "reference_strength": self.reference_strength,
            "has_face_ref": bool(self.face_ref_path and Path(self.face_ref_path).exists()),
            "has_pose_ref": bool(self.pose_ref_path and Path(self.pose_ref_path).exists()),
            "thumbnail_url": f"/api/presets/{self.id}/thumbnail" if self.thumbnail else None,
            "favorite_scenes": self.favorite_scenes,
            "created_at": self.created_at,
        }


class PresetStore:
    def __init__(self, max_entries: int = 100):
        self._lock = Lock()
        self._max_entries = max_entries

    def _snapshot(self, src_path: Optional[str], preset_id: str, tag: str) -> Optional[str]:
        if not src_path:
            return None
        src = Path(src_path)
        if not src.exists() or not src.is_file():
            return None
        ext = src.suffix.lstrip(".") or "png"
        dst = PRESETS_DIR / f"{preset_id}_{tag}.{ext}"
        try:
            shutil.copyfile(src, dst)
            return str(dst)
        except Exception:
            return None

    def _snapshot_bytes(self, data: Optional[bytes], preset_id: str, tag: str) -> Optional[str]:
        if not data or len(data) < 100:
            return None
        ext = _sniff_ext(data)
        dst = PRESETS_DIR / f"{preset_id}_{tag}.{ext}"
        try:
            dst.write_bytes(data)
            return str(dst)
        except Exception:
            return None

    def create(
        self,
        *,
        name: str,
        outfit: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        scene: Optional[str] = None,
        pose: Optional[str] = None,
        seed: Optional[int] = None,
        voice_id: Optional[str] = None,
        reference_strength: float = 0.32,
        face_ref_src: Optional[str] = None,
        pose_ref_src: Optional[str] = None,
        thumbnail_bytes: Optional[bytes] = None,
        favorite_scenes: Optional[List[str]] = None,
    ) -> Preset:
        pid = uuid.uuid4().hex[:12]
        face_snap = self._snapshot(face_ref_src, pid, "face")
        pose_snap = self._snapshot(pose_ref_src, pid, "pose")
        thumb_path = self._snapshot_bytes(thumbnail_bytes, pid, "thumb") if thumbnail_bytes else None
        preset = Preset(
            id=pid,
            name=name[:80] or "Untitled",
            outfit=outfit,
            custom_prompt=custom_prompt,
            scene=scene,
            pose=pose,
            seed=int(seed) if seed is not None else None,
            voice_id=voice_id,
            reference_strength=float(reference_strength),
            face_ref_path=face_snap,
            pose_ref_path=pose_snap,
            thumbnail=Path(thumb_path).name if thumb_path else None,
            favorite_scenes=list(favorite_scenes or []),
            created_at=time.time(),
        )
        with self._lock:
            presets_col().insert_one(preset.to_mongo())
            # Cap
            total = presets_col().count_documents({})
            if total > self._max_entries:
                excess = total - self._max_entries
                oldest = list(presets_col().find().sort("created_at", 1).limit(excess))
                for doc in oldest:
                    self._purge_files(doc)
                    presets_col().delete_one({"id": doc["id"]})
        return preset

    def _purge_files(self, doc: dict) -> None:
        for key in ("face_ref_path", "pose_ref_path"):
            p = doc.get(key)
            if p:
                try:
                    Path(p).unlink(missing_ok=True)
                except Exception:
                    pass
        thumb = doc.get("thumbnail")
        if thumb:
            try:
                (PRESETS_DIR / thumb).unlink(missing_ok=True)
            except Exception:
                pass

    def list(self) -> List[Preset]:
        docs = list(presets_col().find({}, {"_id": 0}).sort("created_at", -1))
        return [Preset.from_mongo(d) for d in docs]

    def get(self, preset_id: str) -> Optional[Preset]:
        doc = presets_col().find_one({"id": preset_id}, {"_id": 0})
        return Preset.from_mongo(doc) if doc else None

    def delete(self, preset_id: str) -> bool:
        with self._lock:
            doc = presets_col().find_one({"id": preset_id}, {"_id": 0})
            if not doc:
                return False
            self._purge_files(doc)
            presets_col().delete_one({"id": preset_id})
            return True

    def thumbnail_path(self, preset_id: str) -> Optional[Path]:
        preset = self.get(preset_id)
        if not preset or not preset.thumbnail:
            return None
        p = PRESETS_DIR / preset.thumbnail
        return p if p.exists() else None

    def thumbnail_mime(self, preset_id: str) -> str:
        p = self.thumbnail_path(preset_id)
        if not p:
            return "application/octet-stream"
        return _mime_for(p.suffix.lstrip("."))


_store: Optional[PresetStore] = None


def get_preset_store() -> PresetStore:
    global _store
    if _store is None:
        _store = PresetStore()
    return _store


# ---------------------------------------------------------------------------
# Starter presets — seeded once on first startup (only if collection is empty).
# ---------------------------------------------------------------------------

STARTER_PRESETS = [
    {"name": "Rooftop Date",       "outfit": "red_silk_negligee",     "scene": "rooftop_pool",     "pose": "wine_pose",       "favorite_scenes": ["rooftop_pool", "penthouse_skyline", "moonlit_balcony"]},
    {"name": "Evening at Home",    "outfit": "silk_robe",             "scene": "fireplace",         "pose": "sitting_crossed", "favorite_scenes": ["fireplace", "candlelit_bedroom", "rainy_window"]},
    {"name": "Beach Sunset",       "outfit": "micro_bikini_beach",    "scene": "private_beach",     "pose": "over_shoulder",   "favorite_scenes": ["private_beach", "tropical_resort"]},
    {"name": "Wine Cellar Confession", "outfit": "black_corset",      "scene": "wine_cellar",       "pose": "wine_pose",       "favorite_scenes": ["wine_cellar", "opera_house", "velvet_boudoir"]},
    {"name": "Rainy Night In",     "outfit": "sheer_nightgown",       "scene": "rainy_window",      "pose": "leaning_wall",    "favorite_scenes": ["rainy_window", "candlelit_bedroom"]},
    {"name": "Alpine Escape",      "outfit": "silk_robe",             "scene": "ski_chalet",        "pose": "sitting_crossed", "favorite_scenes": ["ski_chalet", "fireplace"]},
    {"name": "Opera Box",          "outfit": "china_dress",           "scene": "opera_house",       "pose": "seated_chair",    "favorite_scenes": ["opera_house", "velvet_boudoir"]},
    {"name": "Sunday Morning",     "outfit": "apron_kitchen",         "scene": "garden_at_dusk",    "pose": "over_shoulder",   "favorite_scenes": ["garden_at_dusk", "rainy_window"]},
]


def seed_starter_presets() -> int:
    """Seed initial presets only when the collection is empty. Returns count added."""
    try:
        if presets_col().estimated_document_count() > 0:
            return 0
    except Exception:
        return 0
    store = get_preset_store()
    added = 0
    for p in STARTER_PRESETS:
        store.create(
            name=p["name"],
            outfit=p.get("outfit"),
            scene=p.get("scene"),
            pose=p.get("pose"),
            favorite_scenes=p.get("favorite_scenes", []),
        )
        added += 1
    return added
