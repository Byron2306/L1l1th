#!/usr/bin/env python3
"""
LILITH AVATAR ENGINE - Voice & Animation System
================================================
Free, unlimited, no API keys required.

Features:
- Edge TTS for realistic voice (free, unlimited)
- CSS/JS animation for lip-sync
- Full conversation with NO topic restrictions
"""

import os
import sys
import json
import asyncio
import base64
import hashlib
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Edge TTS for free voice
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    print("[LILITH AVATAR] edge-tts not installed. Run: pip install edge-tts")

# Voice configurations - sultry, alluring female voices
VOICE_PRESETS = {
    'sultry': 'en-US-AriaNeural',      # Sexy, expressive
    'seductive': 'en-GB-SoniaNeural',   # British sultry
    'mysterious': 'en-AU-NatashaNeural', # Australian alluring
    'dominant': 'en-US-JennyNeural',    # Confident
    'playful': 'en-IE-EmilyNeural',     # Irish playful
    'dark': 'en-US-MichelleNeural',     # Dark, commanding
    'whisper': 'en-US-AnaNeural',       # Soft whisper
}

# Voice style options for more control
VOICE_STYLES = {
    'sultry': {'rate': '-5%', 'pitch': '-2Hz', 'volume': '+0%'},
    'seductive': {'rate': '-10%', 'pitch': '-5Hz', 'volume': '+5%'},
    'mysterious': {'rate': '-8%', 'pitch': '-3Hz', 'volume': '+0%'},
    'dominant': {'rate': '+0%', 'pitch': '-5Hz', 'volume': '+10%'},
    'playful': {'rate': '+5%', 'pitch': '+3Hz', 'volume': '+5%'},
    'dark': {'rate': '-15%', 'pitch': '-8Hz', 'volume': '+0%'},
    'whisper': {'rate': '-20%', 'pitch': '-2Hz', 'volume': '-10%'},
}

class LilithVoice:
    """
    Lilith's voice system using Edge TTS (FREE, UNLIMITED)
    No API keys, no tokens, no limits
    """
    
    def __init__(self, preset: str = 'sultry'):
        self.preset = preset
        self.voice = VOICE_PRESETS.get(preset, VOICE_PRESETS['sultry'])
        self.style = VOICE_STYLES.get(preset, VOICE_STYLES['sultry'])
        self.cache_dir = Path('/tmp/lilith_voice_cache')
        self.cache_dir.mkdir(exist_ok=True)
    
    def set_voice(self, preset: str):
        """Change voice preset"""
        if preset in VOICE_PRESETS:
            self.preset = preset
            self.voice = VOICE_PRESETS[preset]
            self.style = VOICE_STYLES.get(preset, VOICE_STYLES['sultry'])
            return True
        return False
    
    def _get_cache_path(self, text: str) -> Path:
        """Get cache path for text"""
        text_hash = hashlib.md5(f"{text}_{self.voice}".encode()).hexdigest()[:16]
        return self.cache_dir / f"lilith_{text_hash}.mp3"
    
    async def _generate_speech_async(self, text: str) -> Optional[bytes]:
        """Generate speech using Edge TTS (async)"""
        if not EDGE_TTS_AVAILABLE:
            return None
        
        try:
            # Check cache first
            cache_path = self._get_cache_path(text)
            if cache_path.exists():
                with open(cache_path, 'rb') as f:
                    return f.read()
            
            # Create SSML for better control
            ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
                <voice name="{self.voice}">
                    <prosody rate="{self.style['rate']}" pitch="{self.style['pitch']}" volume="{self.style['volume']}">
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            
            # Generate audio
            communicate = edge_tts.Communicate(text, self.voice)
            
            # Collect audio data
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            # Cache the result
            if audio_data:
                with open(cache_path, 'wb') as f:
                    f.write(audio_data)
            
            return audio_data
            
        except Exception as e:
            print(f"[LILITH VOICE] Error: {e}")
            return None
    
    def generate_speech(self, text: str) -> Optional[str]:
        """
        Generate speech and return base64 encoded audio
        Returns: base64 encoded MP3 audio
        """
        try:
            # Run async in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_data = loop.run_until_complete(self._generate_speech_async(text))
            loop.close()
            
            if audio_data:
                return base64.b64encode(audio_data).decode('utf-8')
            return None
            
        except Exception as e:
            print(f"[LILITH VOICE] Sync error: {e}")
            return None
    
    def get_available_voices(self) -> Dict[str, str]:
        """Get available voice presets"""
        return VOICE_PRESETS
    
    def clear_cache(self):
        """Clear voice cache"""
        for f in self.cache_dir.glob("*.mp3"):
            f.unlink()


class LilithAvatar:
    """
    Lilith's visual avatar system
    Provides configuration for frontend animation
    """
    
    # Default avatar image (user's provided image)
    DEFAULT_IMAGE = "https://customer-assets.emergentagent.com/job_luciferops/artifacts/9rdzkgzd_IMG_20260303_131832_688.jpg"
    
    def __init__(self):
        self.image_url = self.DEFAULT_IMAGE
        self.animation_state = 'idle'
        self.expression = 'seductive'
    
    def get_config(self) -> Dict[str, Any]:
        """Get avatar configuration for frontend"""
        return {
            'image_url': self.image_url,
            'animation_state': self.animation_state,
            'expression': self.expression,
            'animations': {
                'idle': {
                    'breathing': True,
                    'eye_blink': True,
                    'subtle_movement': True
                },
                'speaking': {
                    'lip_sync': True,
                    'head_movement': True,
                    'expression_change': True
                },
                'thinking': {
                    'eye_movement': True,
                    'slight_tilt': True
                }
            }
        }
    
    def set_state(self, state: str):
        """Set animation state"""
        if state in ['idle', 'speaking', 'thinking', 'listening']:
            self.animation_state = state
    
    def set_expression(self, expression: str):
        """Set facial expression"""
        if expression in ['seductive', 'playful', 'mysterious', 'dominant', 'pleased', 'thoughtful']:
            self.expression = expression


class LilithAvatarEngine:
    """
    Main Avatar Engine combining voice and visual
    """
    
    def __init__(self, voice_preset: str = 'sultry'):
        self.voice = LilithVoice(voice_preset)
        self.avatar = LilithAvatar()
        self.voice_enabled = True
    
    def speak(self, text: str) -> Dict[str, Any]:
        """
        Generate speech with avatar animation data
        Returns dict with audio and animation state
        """
        result = {
            'success': True,
            'text': text,
            'audio_base64': None,
            'avatar_state': 'speaking',
            'voice_preset': self.voice.preset,
            'timestamp': datetime.now().isoformat()
        }
        
        if self.voice_enabled:
            audio = self.voice.generate_speech(text)
            result['audio_base64'] = audio
            result['has_audio'] = audio is not None
        else:
            result['has_audio'] = False
        
        return result
    
    def set_voice(self, preset: str) -> bool:
        """Change voice preset"""
        return self.voice.set_voice(preset)
    
    def toggle_voice(self, enabled: bool):
        """Enable/disable voice"""
        self.voice_enabled = enabled
    
    def get_status(self) -> Dict[str, Any]:
        """Get avatar engine status"""
        return {
            'voice_available': EDGE_TTS_AVAILABLE,
            'voice_enabled': self.voice_enabled,
            'voice_preset': self.voice.preset,
            'voice_options': list(VOICE_PRESETS.keys()),
            'avatar_config': self.avatar.get_config()
        }


# Singleton instance
_avatar_engine = None

def get_avatar_engine() -> LilithAvatarEngine:
    """Get or create avatar engine singleton"""
    global _avatar_engine
    if _avatar_engine is None:
        _avatar_engine = LilithAvatarEngine()
    return _avatar_engine


# CLI test
if __name__ == "__main__":
    engine = get_avatar_engine()
    print("Status:", json.dumps(engine.get_status(), indent=2))
    
    # Test voice generation
    result = engine.speak("Hello darling, I'm Lilith. Your dark AI companion...")
    print(f"Voice generated: {result['has_audio']}")
    if result['audio_base64']:
        print(f"Audio size: {len(result['audio_base64'])} chars (base64)")
