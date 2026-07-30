"""
Pose ControlNet (pragmatic) — real skeleton-guided generation.

Real public ControlNet OpenPose HF Spaces are broken as of Feb 2026, so we
compose two remote calls:

  1. `SJTU-TES/OpenPose`  → extract a clean OpenPose skeleton from the user's
                             pose reference photo.
  2. LILITH ZeroGPU Space `/generate_reference` → img2img with the skeleton
                             as the reference image at high strength, so the
                             generated body follows the skeleton.

This is not literally a ControlNet pipeline, but from the user's perspective
the effect is the same: "her body follows the pose photo".

Face fidelity should be layered on top via the face-swap boost.
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
    print("[POSECTRL] gradio_client not available")

OPENPOSE_SPACE = os.environ.get("POSE_OPENPOSE_SPACE", "SJTU-TES/OpenPose")


class PoseControlNetEngine:
    """Extracts an OpenPose skeleton from a photo. The actual guided
    generation is performed by the caller (LILITH image generator) using
    the returned skeleton as an img2img reference at high strength."""

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
            self.client = Client(OPENPOSE_SPACE, **kwargs)
            print(f"[POSECTRL] connected to {OPENPOSE_SPACE}")
            return True
        except Exception as e:
            self.last_error = f"connect failed: {e}"
            print(f"[POSECTRL] {self.last_error}")
            self.client = None
            return False

    def extract_skeleton(self, pose_image_path: str) -> Optional[str]:
        """Extract an OpenPose skeleton from the given image.
        Returns a local filesystem path to the skeleton image (PNG) or None.
        """
        if not pose_image_path or not Path(pose_image_path).exists():
            self.last_error = "pose image not found"
            return None
        if not self._connect():
            return None
        try:
            result = self.client.predict(
                handle_file(pose_image_path), api_name="/pose_estimation",
            )
            # SJTU-TES/OpenPose returns (estimation_image_path, pose_json_path)
            if isinstance(result, (list, tuple)) and result:
                candidate = result[0]
            else:
                candidate = result
            if isinstance(candidate, dict):
                candidate = candidate.get("path") or candidate.get("name")
            if not candidate or not Path(str(candidate)).exists():
                self.last_error = "no skeleton returned"
                return None
            # Copy to /tmp so caller controls lifetime
            src = Path(str(candidate))
            with tempfile.NamedTemporaryFile(prefix="skeleton_", suffix=".png", delete=False) as tf:
                tf.write(src.read_bytes())
                out_path = tf.name
            print(f"[POSECTRL] skeleton extracted -> {out_path}")
            return out_path
        except Exception as e:
            self.last_error = f"extract failed: {e}"
            print(f"[POSECTRL] {self.last_error}")
            self.client = None
            return None

    def get_status(self) -> dict:
        return {
            "space": OPENPOSE_SPACE,
            "mode": "skeleton_extraction+img2img",
            "connected": self.client is not None,
            "gradio_available": GRADIO_AVAILABLE,
            "last_error": self.last_error,
        }


_engine: Optional[PoseControlNetEngine] = None


def get_pose_controlnet_engine() -> PoseControlNetEngine:
    global _engine
    if _engine is None:
        _engine = PoseControlNetEngine()
    return _engine
