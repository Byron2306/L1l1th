"""
Reference image state — the "canonical face" used for img2img generation.

Only one reference is active at a time. It can be either:
- A gallery entry (by id), or
- An uploaded file stored under /tmp/lilith_reference/
"""
from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from threading import Lock
from typing import Optional

from services.gallery import get_gallery

REF_DIR = Path(os.environ.get("LILITH_REF_DIR", "/tmp/lilith_reference"))
REF_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class Reference:
    source: str          # "gallery" | "upload"
    gallery_id: Optional[str] = None   # if source == "gallery"
    upload_path: Optional[str] = None  # if source == "upload"
    strength: float = 0.32

    def local_path(self) -> Optional[str]:
        if self.source == "upload":
            return self.upload_path if self.upload_path and Path(self.upload_path).exists() else None
        if self.source == "gallery" and self.gallery_id:
            entry = get_gallery().get(self.gallery_id)
            return str(entry.path) if entry and entry.path.exists() else None
        return None

    def to_public(self) -> dict:
        d = asdict(self)
        d["available"] = self.local_path() is not None
        # URL clients can render (via existing gallery route if applicable)
        if self.source == "gallery" and self.gallery_id:
            d["url"] = f"/api/gallery/{self.gallery_id}"
        elif self.source == "upload" and self.upload_path:
            fn = Path(self.upload_path).name
            d["url"] = f"/api/reference/file/{fn}"
        else:
            d["url"] = None
        return d


class ReferenceStore:
    def __init__(self):
        self._ref: Optional[Reference] = None
        self._lock = Lock()

    def set_gallery(self, gallery_id: str, strength: float = 0.32) -> Reference:
        entry = get_gallery().get(gallery_id)
        if not entry:
            raise KeyError("gallery entry not found")
        with self._lock:
            self._ref = Reference(source="gallery", gallery_id=gallery_id, strength=strength)
            return self._ref

    def set_upload(self, data: bytes, ext_hint: str = "png", strength: float = 0.32) -> Reference:
        # Sniff extension from magic bytes
        if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
            ext = "webp"
        elif data.startswith(b"\x89PNG"):
            ext = "png"
        elif data.startswith(b"\xff\xd8"):
            ext = "jpg"
        else:
            ext = ext_hint or "png"
        fn = f"ref_{uuid.uuid4().hex[:12]}.{ext}"
        path = REF_DIR / fn
        path.write_bytes(data)
        with self._lock:
            self._ref = Reference(source="upload", upload_path=str(path), strength=strength)
            return self._ref

    def clear(self):
        with self._lock:
            self._ref = None

    def get(self) -> Optional[Reference]:
        with self._lock:
            return self._ref

    def set_strength(self, strength: float) -> Optional[Reference]:
        with self._lock:
            if self._ref:
                self._ref.strength = max(0.05, min(0.95, float(strength)))
            return self._ref


_store: Optional[ReferenceStore] = None


def get_reference_store() -> ReferenceStore:
    global _store
    if _store is None:
        _store = ReferenceStore()
    return _store
