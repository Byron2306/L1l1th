#!/usr/bin/env python3
"""
LILITH ANIMATION ENGINE - Video Generation
===========================================
Creates animated videos of LILITH using:
- Manim for 2D animations
- PIL for image processing
- Audio sync for lip animations

Generates talking avatar videos, reaction animations, etc.
"""

import os
import io
import math
import time
import base64
import tempfile
from typing import Optional, Dict, List, Tuple
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

# Try to import manim
MANIM_AVAILABLE = False
try:
    from manim import *
    MANIM_AVAILABLE = True
    print("[ANIMATION] Manim loaded successfully")
except ImportError as e:
    print(f"[ANIMATION] Manim not available: {e}")

# Animation settings
FRAME_RATE = 24
VIDEO_WIDTH = 512
VIDEO_HEIGHT = 512


class LilithAnimation:
    """
    Simple animation generator for LILITH avatar.
    Creates lip-sync and reaction animations.
    """
    
    def __init__(self, avatar_path: Optional[str] = None):
        self.avatar_path = avatar_path
        self.avatar_image = None
        self.temp_dir = tempfile.mkdtemp(prefix='lilith_anim_')
        
        if avatar_path and os.path.exists(avatar_path):
            try:
                self.avatar_image = Image.open(avatar_path).convert('RGBA')
                print(f"[ANIMATION] Loaded avatar: {avatar_path}")
            except Exception as e:
                print(f"[ANIMATION] Could not load avatar: {e}")
    
    def generate_lip_sync_frames(
        self, 
        audio_amplitudes: List[float],
        num_frames: int = 30
    ) -> List[Image.Image]:
        """
        Generate lip-sync animation frames based on audio amplitudes.
        Returns list of PIL Images showing mouth movement.
        """
        if not self.avatar_image:
            return []
        
        frames = []
        base_img = self.avatar_image.copy()
        
        for i, amplitude in enumerate(audio_amplitudes[:num_frames]):
            frame = base_img.copy()
            
            # Create mouth overlay based on amplitude
            # Higher amplitude = more open mouth
            mouth_openness = min(1.0, amplitude * 2)
            
            # Apply subtle face animation
            frame = self._animate_mouth(frame, mouth_openness)
            frames.append(frame)
        
        return frames
    
    def _animate_mouth(self, img: Image.Image, openness: float) -> Image.Image:
        """
        Animate the mouth area of the avatar.
        openness: 0.0 (closed) to 1.0 (fully open)
        """
        # Create a copy to modify
        animated = img.copy()
        
        # Get image dimensions
        w, h = animated.size
        
        # Mouth region (approximate - lower third of face)
        mouth_y = int(h * 0.65)
        mouth_height = int(h * 0.1 * openness)
        
        # Create a subtle "breathing" effect on the whole image
        # This gives life to the avatar even with small mouth movements
        scale = 1.0 + (openness * 0.02)  # Subtle scale
        
        if scale != 1.0:
            new_size = (int(w * scale), int(h * scale))
            temp = animated.resize(new_size, Image.LANCZOS)
            # Crop back to original size (centered)
            left = (new_size[0] - w) // 2
            top = (new_size[1] - h) // 2
            animated = temp.crop((left, top, left + w, top + h))
        
        return animated
    
    def generate_reaction_animation(
        self, 
        reaction_type: str,
        duration_frames: int = 24
    ) -> List[Image.Image]:
        """
        Generate a reaction animation.
        reaction_type: 'happy', 'thinking', 'aroused', 'surprised'
        """
        if not self.avatar_image:
            return []
        
        frames = []
        base_img = self.avatar_image.copy()
        
        for i in range(duration_frames):
            progress = i / duration_frames
            frame = base_img.copy()
            
            if reaction_type == 'happy':
                # Gentle bounce/pulse
                scale = 1.0 + 0.03 * math.sin(progress * math.pi * 2)
                frame = self._scale_image(frame, scale)
                
            elif reaction_type == 'thinking':
                # Slight tilt animation
                angle = 5 * math.sin(progress * math.pi)
                frame = frame.rotate(angle, expand=False, fillcolor=(0, 0, 0, 0))
                
            elif reaction_type == 'aroused':
                # Glow effect that pulses
                glow_intensity = 0.3 + 0.2 * math.sin(progress * math.pi * 2)
                frame = self._add_glow(frame, glow_intensity, color=(255, 100, 150))
                
            elif reaction_type == 'surprised':
                # Quick scale up then settle
                if progress < 0.3:
                    scale = 1.0 + 0.1 * (progress / 0.3)
                else:
                    scale = 1.1 - 0.1 * ((progress - 0.3) / 0.7)
                frame = self._scale_image(frame, scale)
            
            frames.append(frame)
        
        return frames
    
    def _scale_image(self, img: Image.Image, scale: float) -> Image.Image:
        """Scale image while keeping center"""
        w, h = img.size
        new_w, new_h = int(w * scale), int(h * scale)
        scaled = img.resize((new_w, new_h), Image.LANCZOS)
        
        # Create canvas and paste centered
        result = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        offset = ((w - new_w) // 2, (h - new_h) // 2)
        result.paste(scaled, offset)
        return result
    
    def _add_glow(
        self, 
        img: Image.Image, 
        intensity: float,
        color: Tuple[int, int, int] = (255, 0, 100)
    ) -> Image.Image:
        """Add a colored glow effect"""
        # Create glow layer
        glow = Image.new('RGBA', img.size, (*color, int(255 * intensity * 0.3)))
        glow = glow.filter(ImageFilter.GaussianBlur(radius=20))
        
        # Composite
        result = Image.alpha_composite(glow, img)
        return result
    
    def frames_to_gif(
        self, 
        frames: List[Image.Image],
        output_path: Optional[str] = None,
        fps: int = 24
    ) -> Optional[bytes]:
        """Convert frames to GIF, return as bytes"""
        if not frames:
            return None
        
        if output_path is None:
            output_path = os.path.join(self.temp_dir, 'animation.gif')
        
        try:
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=int(1000 / fps),
                loop=0,
                optimize=True
            )
            
            with open(output_path, 'rb') as f:
                return f.read()
                
        except Exception as e:
            print(f"[ANIMATION] GIF creation error: {e}")
            return None
    
    def frames_to_webm(
        self, 
        frames: List[Image.Image],
        audio_path: Optional[str] = None,
        output_path: Optional[str] = None,
        fps: int = 24
    ) -> Optional[bytes]:
        """Convert frames to WebM video with optional audio"""
        if not frames:
            return None
        
        try:
            import subprocess
            
            if output_path is None:
                output_path = os.path.join(self.temp_dir, 'animation.webm')
            
            # Save frames as images
            frame_paths = []
            for i, frame in enumerate(frames):
                path = os.path.join(self.temp_dir, f'frame_{i:04d}.png')
                frame.save(path)
                frame_paths.append(path)
            
            # Use ffmpeg to create video
            frame_pattern = os.path.join(self.temp_dir, 'frame_%04d.png')
            
            cmd = [
                'ffmpeg', '-y',
                '-framerate', str(fps),
                '-i', frame_pattern,
            ]
            
            if audio_path and os.path.exists(audio_path):
                cmd.extend(['-i', audio_path, '-c:a', 'libopus'])
            
            cmd.extend([
                '-c:v', 'libvpx-vp9',
                '-pix_fmt', 'yuva420p',
                '-b:v', '1M',
                output_path
            ])
            
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_path):
                with open(output_path, 'rb') as f:
                    return f.read()
                    
        except Exception as e:
            print(f"[ANIMATION] WebM creation error: {e}")
        
        return None


def audio_to_amplitudes(audio_data: bytes, num_samples: int = 100) -> List[float]:
    """
    Extract amplitude envelope from audio data.
    Returns list of normalized amplitudes (0.0 to 1.0).
    """
    try:
        # Try to decode audio and get amplitudes
        # This is a simplified approach - just uses the raw bytes as amplitude proxy
        chunk_size = max(1, len(audio_data) // num_samples)
        amplitudes = []
        
        for i in range(num_samples):
            start = i * chunk_size
            end = min(start + chunk_size, len(audio_data))
            chunk = audio_data[start:end]
            
            if chunk:
                # Calculate RMS of chunk as amplitude
                values = list(chunk)
                rms = math.sqrt(sum(v*v for v in values) / len(values)) / 255.0
                amplitudes.append(rms)
            else:
                amplitudes.append(0.0)
        
        return amplitudes
        
    except Exception as e:
        print(f"[ANIMATION] Audio analysis error: {e}")
        return [0.5] * num_samples


# Singleton
_animation_engine = None

def get_animation_engine(avatar_path: Optional[str] = None) -> LilithAnimation:
    global _animation_engine
    if _animation_engine is None or avatar_path:
        _animation_engine = LilithAnimation(avatar_path)
    return _animation_engine


if __name__ == "__main__":
    print("Testing Animation Engine...")
    
    # Test with a dummy image
    engine = LilithAnimation()
    
    # Create a test image
    test_img = Image.new('RGBA', (512, 512), (100, 50, 80, 255))
    draw = ImageDraw.Draw(test_img)
    draw.ellipse([150, 150, 362, 362], fill=(200, 100, 150, 255))
    test_img.save('/tmp/test_avatar.png')
    
    engine = LilithAnimation('/tmp/test_avatar.png')
    
    # Generate happy reaction
    frames = engine.generate_reaction_animation('happy', 24)
    if frames:
        gif_data = engine.frames_to_gif(frames)
        if gif_data:
            with open('/tmp/happy_reaction.gif', 'wb') as f:
                f.write(gif_data)
            print(f"Created animation: {len(gif_data)} bytes")
