"""
Face Swap Boost — remote face-swap post-processing pass.

Uses the public HuggingFace Space `felixrosberg/face-swap` via gradio_client.
No local model download, no disk usage beyond a tiny working buffer.

Contract:
  face_swap(target_bytes, source_face_path) -> swapped_bytes | None

Target: the freshly generated Lilith image (whose face we want to overwrite).
Source: the user's face reference photo (whose face we want to appear on Lilith).

The Space's `/run` (SwapFace) endpoint takes:
    target_image, source_image, doFaceEnhancer, faceIndex, api_name="/run"
Falls back to `.predict(...)` without api_name if the endpoint name changes.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional

GRADIO_AVAILABLE = False
try:
    from gradio_client import Client, handle_file
    GRADIO_AVAILABLE = True
except ImportError:
    print("[FACESWAP] gradio_client not available")

FACESWAP_SPACE = os.environ.get("FACESWAP_SPACE", "felixrosberg/face-swap")


class FaceSwapEngine:
    def __init__(self):
        self.client: Optional[Client] = None
        self.hf_token = os.environ.get("HF_TOKEN")
        self.last_error: Optional[str] = None

    def _connect(self) -> bool:
        if not GRADIO_AVAILABLE:
            self.last_error = "gradio_client not installed"
            return False
        if self.client is not None:
            return True
        try:
            # Some face-swap spaces require the HF token; pass it if we have one.
            kwargs = {"token": self.hf_token} if self.hf_token else {}
            self.client = Client(FACESWAP_SPACE, **kwargs)
            print(f"[FACESWAP] connected to {FACESWAP_SPACE}")
            return True
        except Exception as e:
            self.last_error = f"connect failed: {e}"
            print(f"[FACESWAP] {self.last_error}")
            self.client = None
            return False

    def swap(self, target_bytes: bytes, source_face_path: str) -> Optional[bytes]:
        """
        Apply face-swap. Returns swapped image bytes or None on failure.
        `target_bytes` is the raw image bytes (the generated Lilith).
        `source_face_path` is a local file path to the user's face reference.
        """
        if not target_bytes or not source_face_path:
            self.last_error = "missing inputs"
            return None
        if not Path(source_face_path).exists():
            self.last_error = f"source not found: {source_face_path}"
            return None
        if not self._connect():
            return None

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
            tf.write(target_bytes)
            target_path = tf.name

        try:
            client = self.client
            # felixrosberg/face-swap `/run` signature (as of Feb 2026):
            #   target_image, source_image, doFaceEnhancer, faceIndex
            attempts = [
                dict(api_name="/run",
                     args=[handle_file(target_path), handle_file(source_face_path), True, 0]),
                # fallback: unnamed predict (works on many forks)
                dict(api_name=None,
                     args=[handle_file(target_path), handle_file(source_face_path), True, 0]),
                # fallback: /predict style (simpler forks)
                dict(api_name="/predict",
                     args=[handle_file(source_face_path), handle_file(target_path)]),
            ]
            result_path: Optional[str] = None
            for attempt in attempts:
                try:
                    if attempt["api_name"]:
                        result = client.predict(*attempt["args"], api_name=attempt["api_name"])
                    else:
                        result = client.predict(*attempt["args"])
                    # Gradio may return a str path, a tuple, or a dict
                    if isinstance(result, (list, tuple)):
                        candidate = result[0]
                    else:
                        candidate = result
                    if isinstance(candidate, dict):
                        candidate = candidate.get("path") or candidate.get("name")
                    if candidate and Path(str(candidate)).exists():
                        result_path = str(candidate)
                        break
                except Exception as e:
                    self.last_error = f"predict failed ({attempt['api_name']}): {e}"
                    continue

            if not result_path:
                print(f"[FACESWAP] all attempts failed: {self.last_error}")
                return None

            data = Path(result_path).read_bytes()
            if len(data) < 1000:
                self.last_error = "swap output too small"
                return None
            print(f"[FACESWAP] swapped {len(data)} bytes")
            return data
        finally:
            try:
                Path(target_path).unlink(missing_ok=True)
            except Exception:
                pass

    def get_status(self) -> dict:
        return {
            "space": FACESWAP_SPACE,
            "connected": self.client is not None,
            "gradio_available": GRADIO_AVAILABLE,
            "last_error": self.last_error,
        }


_engine: Optional[FaceSwapEngine] = None


def get_face_swap_engine() -> FaceSwapEngine:
    global _engine
    if _engine is None:
        _engine = FaceSwapEngine()
    return _engine
