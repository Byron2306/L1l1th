"""
Reference image state (persistent).
Two independent references are supported:
  - Face reference: primary anchor for `/generate_reference` img2img (key='reference')
  - Pose reference: an uploaded pose skeleton or body-position photo (key='pose_reference')

Both are stored in Mongo `system_state` and files under /app/data/references/.
"""
from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from threading import Lock
from typing import Optional

from services.db import state_col
from services.gallery import get_gallery

REF_DIR = Path(os.environ.get("LILITH_REF_DIR", "/app/data/references"))
REF_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class Reference:
    source: str
    gallery_id: Optional[str] = None
    upload_path: Optional[str] = None
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
        if self.source == "gallery" and self.gallery_id:
            d["url"] = f"/api/gallery/{self.gallery_id}"
        elif self.source == "upload" and self.upload_path:
            fn = Path(self.upload_path).name
            d["url"] = f"/api/reference/file/{fn}"
        else:
            d["url"] = None
        return d


class _KindedStore:
    """Backing store for a single named reference (face or pose)."""

    def __init__(self, key: str):
        self._key = key
        self._lock = Lock()

    def _load(self) -> Optional[Reference]:
        doc = state_col().find_one({"key": self._key}, {"_id": 0, "key": 0})
        return Reference(**doc) if doc else None

    def _save(self, ref: Optional[Reference]) -> None:
        if ref is None:
            state_col().delete_one({"key": self._key})
            return
        state_col().update_one(
            {"key": self._key}, {"$set": {"key": self._key, **asdict(ref)}}, upsert=True,
        )

    def set_gallery(self, gallery_id: str, strength: float = 0.32) -> Reference:
        entry = get_gallery().get(gallery_id)
        if not entry:
            raise KeyError("gallery entry not found")
        with self._lock:
            ref = Reference(source="gallery", gallery_id=gallery_id, strength=strength)
            self._save(ref)
            return ref

    def set_upload(self, data: bytes, strength: float = 0.32) -> Reference:
        if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
            ext = "webp"
        elif data.startswith(b"\x89PNG"):
            ext = "png"
        elif data.startswith(b"\xff\xd8"):
            ext = "jpg"
        else:
            ext = "png"
        fn = f"{self._key}_{uuid.uuid4().hex[:12]}.{ext}"
        path = REF_DIR / fn
        path.write_bytes(data)
        with self._lock:
            ref = Reference(source="upload", upload_path=str(path), strength=strength)
            self._save(ref)
            return ref

    def clear(self):
        with self._lock:
            existing = self._load()
            if existing and existing.source == "upload" and existing.upload_path:
                try:
                    Path(existing.upload_path).unlink(missing_ok=True)
                except Exception:
                    pass
            self._save(None)

    def get(self) -> Optional[Reference]:
        with self._lock:
            return self._load()

    def set_strength(self, strength: float) -> Optional[Reference]:
        with self._lock:
            ref = self._load()
            if ref:
                ref.strength = max(0.05, min(0.95, float(strength)))
                self._save(ref)
            return ref


class ReferenceStore(_KindedStore):
    def __init__(self):
        super().__init__("reference")


class PoseReferenceStore(_KindedStore):
    def __init__(self):
        super().__init__("pose_reference")


_face_store: Optional[ReferenceStore] = None
_pose_store: Optional[PoseReferenceStore] = None


def get_reference_store() -> ReferenceStore:
    global _face_store
    if _face_store is None:
        _face_store = ReferenceStore()
    return _face_store


def get_pose_reference_store() -> PoseReferenceStore:
    global _pose_store
    if _pose_store is None:
        _pose_store = PoseReferenceStore()
    return _pose_store
