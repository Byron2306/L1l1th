"""
Persistent image gallery.
- Metadata: MongoDB `gallery_entries`.
- Image bytes: /app/data/gallery/<id>.<ext> (survives restarts).
- Loads existing entries from Mongo on startup.
"""
from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import List, Optional

from services.db import gallery_col

GALLERY_DIR = Path(os.environ.get("LILITH_GALLERY_DIR", "/app/data/gallery"))
GALLERY_DIR.mkdir(parents=True, exist_ok=True)


def _sniff_ext(data: bytes) -> str:
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "webp"
    if data.startswith(b"\x89PNG"):
        return "png"
    if data.startswith(b"\xff\xd8"):
        return "jpg"
    return "bin"


def _mime_for(ext: str) -> str:
    return {"webp": "image/webp", "png": "image/png", "jpg": "image/jpeg"}.get(ext, "application/octet-stream")


@dataclass
class GalleryEntry:
    id: str
    ext: str
    label: str
    outfit: Optional[str]
    prompt: Optional[str]
    seed: Optional[int]
    provider: Optional[str]
    created_at: float

    @property
    def filename(self) -> str:
        return f"{self.id}.{self.ext}"

    @property
    def path(self) -> Path:
        return GALLERY_DIR / self.filename

    @property
    def mime(self) -> str:
        return _mime_for(self.ext)

    def to_public(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "outfit": self.outfit,
            "prompt": self.prompt,
            "seed": self.seed,
            "provider": self.provider,
            "created_at": self.created_at,
            "url": f"/api/gallery/{self.id}",
        }

    def to_mongo(self) -> dict:
        return {
            "id": self.id,
            "ext": self.ext,
            "label": self.label,
            "outfit": self.outfit,
            "prompt": self.prompt,
            "seed": self.seed,
            "provider": self.provider,
            "created_at": self.created_at,
        }

    @classmethod
    def from_mongo(cls, doc: dict) -> "GalleryEntry":
        return cls(
            id=doc["id"], ext=doc["ext"], label=doc.get("label", ""),
            outfit=doc.get("outfit"), prompt=doc.get("prompt"),
            seed=doc.get("seed"), provider=doc.get("provider"),
            created_at=doc.get("created_at", time.time()),
        )


class Gallery:
    def __init__(self, max_entries: int = 500):
        self._lock = Lock()
        self._max_entries = max_entries

    def add(self, data: bytes, *, label: str, outfit: Optional[str] = None,
            prompt: Optional[str] = None, seed: Optional[int] = None,
            provider: Optional[str] = None) -> GalleryEntry:
        ext = _sniff_ext(data)
        entry = GalleryEntry(
            id=uuid.uuid4().hex[:12],
            ext=ext, label=label[:120],
            outfit=outfit, prompt=prompt, seed=seed, provider=provider,
            created_at=time.time(),
        )
        entry.path.write_bytes(data)

        with self._lock:
            gallery_col().insert_one(entry.to_mongo())
            # Cap total count — delete oldest excess
            total = gallery_col().count_documents({})
            if total > self._max_entries:
                excess = total - self._max_entries
                oldest = list(gallery_col().find().sort("created_at", 1).limit(excess))
                for doc in oldest:
                    e = GalleryEntry.from_mongo(doc)
                    try: e.path.unlink(missing_ok=True)
                    except Exception: pass
                    gallery_col().delete_one({"id": e.id})
        return entry

    def list(self) -> List[dict]:
        docs = list(gallery_col().find({}, {"_id": 0}).sort("created_at", -1))
        return [GalleryEntry.from_mongo(d).to_public() for d in docs]

    def get(self, entry_id: str) -> Optional[GalleryEntry]:
        doc = gallery_col().find_one({"id": entry_id}, {"_id": 0})
        return GalleryEntry.from_mongo(doc) if doc else None

    def delete(self, entry_id: str) -> bool:
        with self._lock:
            entry = self.get(entry_id)
            if not entry:
                return False
            try: entry.path.unlink(missing_ok=True)
            except Exception: pass
            gallery_col().delete_one({"id": entry_id})
            return True


_gallery: Optional[Gallery] = None


def get_gallery() -> Gallery:
    global _gallery
    if _gallery is None:
        _gallery = Gallery()
    return _gallery
