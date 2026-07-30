"""
Image quality enhancer — CodeFormer face restoration + 2x upscale.

Uses the `sczhou/CodeFormer` HF Space. One call fixes:
  - Asymmetric eyes, lips, eyebrows (face restoration CNN)
  - General softness (background_enhance + face_upsample)
  - Low resolution (2x Real-ESRGAN upscale)

Runs as a post-processing pass on top of face-swap.
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
    print("[ENHANCE] gradio_client not available")

CODEFORMER_SPACE = os.environ.get("CODEFORMER_SPACE", "sczhou/CodeFormer")


class ImageEnhancer:
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
            kwargs = {"token": self.hf_token} if self.hf_token else {}
            self.client = Client(CODEFORMER_SPACE, **kwargs)
            print(f"[ENHANCE] connected to {CODEFORMER_SPACE}")
            return True
        except Exception as e:
            self.last_error = f"connect failed: {e}"
            print(f"[ENHANCE] {self.last_error}")
            self.client = None
            return False

    def enhance(self, image_bytes: bytes, *, upscale: float = 2.0,
                fidelity: float = 0.6) -> Optional[bytes]:
        """
        Run CodeFormer face+background restoration.
        `fidelity` in [0,1] — higher = more faithful to the original face
                              (0.5-0.7 is the sweet spot for style-consistent).
        Returns enhanced bytes or None on failure.
        """
        if not image_bytes or len(image_bytes) < 1000:
            self.last_error = "empty input"
            return None
        if not self._connect():
            return None
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
            tf.write(image_bytes)
            in_path = tf.name
        try:
            result = self.client.predict(
                handle_file(in_path),
                True,          # face_align
                True,          # background_enhance
                True,          # face_upsample
                float(upscale),
                float(fidelity),
                api_name="/inference",
            )
            # Returns (output_image_path, markdown_status)
            if isinstance(result, (list, tuple)) and result:
                candidate = result[0]
            else:
                candidate = result
            if isinstance(candidate, dict):
                candidate = candidate.get("path") or candidate.get("name")
            if not candidate or not Path(str(candidate)).exists():
                self.last_error = "no output"
                return None
            data = Path(str(candidate)).read_bytes()
            if len(data) < 1000:
                self.last_error = "output too small"
                return None
            print(f"[ENHANCE] restored {len(data)} bytes")
            return data
        except Exception as e:
            self.last_error = f"enhance failed: {e}"
            print(f"[ENHANCE] {self.last_error}")
            return None
        finally:
            try:
                Path(in_path).unlink(missing_ok=True)
            except Exception:
                pass

    def get_status(self) -> dict:
        return {
            "space": CODEFORMER_SPACE,
            "connected": self.client is not None,
            "gradio_available": GRADIO_AVAILABLE,
            "last_error": self.last_error,
        }


_engine: Optional[ImageEnhancer] = None


def get_image_enhancer() -> ImageEnhancer:
    global _engine
    if _engine is None:
        _engine = ImageEnhancer()
    return _engine
