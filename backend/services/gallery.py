"""
In-memory + on-disk image gallery.

Entries are stored newest-first. Image bytes live on disk under
/tmp/lilith_gallery/ (survives backend restart within the container's uptime
but is intentionally ephemeral — not user data we should persist forever).
"""
from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from threading import Lock
from typing import List, Optional

GALLERY_DIR = Path(os.environ.get("LILITH_GALLERY_DIR", "/tmp/lilith_gallery"))
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
    label: str          # short human label — outfit id or truncated custom prompt
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


class Gallery:
    def __init__(self, max_entries: int = 200):
        self._entries: List[GalleryEntry] = []
        self._lock = Lock()
        self._max_entries = max_entries

    def add(self, data: bytes, *, label: str, outfit: Optional[str] = None,
            prompt: Optional[str] = None, seed: Optional[int] = None,
            provider: Optional[str] = None) -> GalleryEntry:
        ext = _sniff_ext(data)
        entry = GalleryEntry(
            id=uuid.uuid4().hex[:12],
            ext=ext,
            label=label[:80],
            outfit=outfit,
            prompt=prompt,
            seed=seed,
            provider=provider,
            created_at=time.time(),
        )
        entry.path.write_bytes(data)

        with self._lock:
            self._entries.insert(0, entry)
            # Prune old entries (LRU-ish, by insertion order)
            if len(self._entries) > self._max_entries:
                dead = self._entries[self._max_entries:]
                self._entries = self._entries[: self._max_entries]
                for e in dead:
                    try:
                        e.path.unlink(missing_ok=True)
                    except Exception:
                        pass
        return entry

    def list(self) -> List[dict]:
        with self._lock:
            return [e.to_public() for e in self._entries]

    def get(self, entry_id: str) -> Optional[GalleryEntry]:
        with self._lock:
            for e in self._entries:
                if e.id == entry_id:
                    return e
        return None

    def delete(self, entry_id: str) -> bool:
        with self._lock:
            for i, e in enumerate(self._entries):
                if e.id == entry_id:
                    self._entries.pop(i)
                    try:
                        e.path.unlink(missing_ok=True)
                    except Exception:
                        pass
                    return True
        return False


_gallery: Optional[Gallery] = None


def get_gallery() -> Gallery:
    global _gallery
    if _gallery is None:
        _gallery = Gallery()
    return _gallery
