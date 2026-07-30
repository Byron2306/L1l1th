#!/usr/bin/env python3
"""
LILITH VOICE ENGINE - ElevenLabs Integration
=============================================
Uses ElevenLabs for high-quality, sultry voice synthesis.
"""

import os
import base64
from typing import Optional

# ElevenLabs configuration
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "")

# Try ElevenLabs first, fallback to Edge TTS
ELEVENLABS_AVAILABLE = False
EDGE_TTS_AVAILABLE = False

try:
    from elevenlabs import ElevenLabs
    from elevenlabs.core import ApiError
    ELEVENLABS_AVAILABLE = True
    print("[LILITH VOICE] ElevenLabs loaded successfully")
except ImportError:
    print("[LILITH VOICE] ElevenLabs not available, will try Edge TTS")

try:
    import edge_tts
    import asyncio
    EDGE_TTS_AVAILABLE = True
    print("[LILITH VOICE] Edge TTS available as fallback")
except ImportError:
    pass


class LilithVoiceEngine:
    """
    High-quality voice synthesis for LILITH.
    Primary: ElevenLabs (sultry, realistic)
    Fallback: Edge TTS (free, unlimited)
    """
    
    def __init__(self):
        self.elevenlabs_client = None
        self.voice_id = ELEVENLABS_VOICE_ID
        
        if ELEVENLABS_AVAILABLE and ELEVENLABS_API_KEY:
            try:
                self.elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
                print(f"[LILITH VOICE] ElevenLabs initialized with voice: {self.voice_id}")
            except Exception as e:
                print(f"[LILITH VOICE] ElevenLabs init error: {e}")
    
    def generate_speech(self, text: str, voice_id: Optional[str] = None) -> Optional[str]:
        """
        Generate speech audio from text.
        Returns base64-encoded MP3 audio.
        `voice_id` overrides the default voice for this call.
        """
        # Try ElevenLabs first
        if self.elevenlabs_client:
            try:
                audio_data = self._generate_elevenlabs(text, voice_id=voice_id or self.voice_id)
                if audio_data:
                    return base64.b64encode(audio_data).decode('utf-8')
            except Exception as e:
                print(f"[LILITH VOICE] ElevenLabs error: {e}")
        
        # Fallback to Edge TTS
        if EDGE_TTS_AVAILABLE:
            try:
                audio_data = self._generate_edge_tts(text)
                if audio_data:
                    return base64.b64encode(audio_data).decode('utf-8')
            except Exception as e:
                print(f"[LILITH VOICE] Edge TTS error: {e}")
        
        return None
    
    def _generate_elevenlabs(self, text: str, voice_id: Optional[str] = None) -> Optional[bytes]:
        """Generate audio using ElevenLabs API"""
        if not self.elevenlabs_client:
            return None
        
        try:
            # Use the text_to_speech.convert method
            audio_generator = self.elevenlabs_client.text_to_speech.convert(
                text=text,
                voice_id=voice_id or self.voice_id,
                model_id="eleven_multilingual_v2",
                voice_settings={
                    "stability": 0.5,
                    "similarity_boost": 0.8,
                    "style": 0.6,
                    "use_speaker_boost": True
                }
            )
            
            # Collect audio chunks
            audio_data = b""
            for chunk in audio_generator:
                audio_data += chunk
            
            if len(audio_data) > 0:
                print(f"[LILITH VOICE] ElevenLabs generated {len(audio_data)} bytes")
                return audio_data
                
        except Exception as e:
            print(f"[LILITH VOICE] ElevenLabs generation error: {e}")
        
        return None
    
    def _generate_edge_tts(self, text: str) -> Optional[bytes]:
        """Generate audio using Edge TTS (fallback)"""
        try:
            async def generate():
                voice = "en-US-AriaNeural"  # Sultry voice
                communicate = edge_tts.Communicate(text, voice)
                
                audio_data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data += chunk["data"]
                
                return audio_data
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(generate())
            loop.close()
            
            if result:
                print(f"[LILITH VOICE] Edge TTS generated {len(result)} bytes")
                return result
                
        except Exception as e:
            print(f"[LILITH VOICE] Edge TTS error: {e}")
        
        return None
    
    def get_status(self) -> dict:
        """Get voice engine status"""
        return {
            "elevenlabs_available": self.elevenlabs_client is not None,
            "edge_tts_available": EDGE_TTS_AVAILABLE,
            "voice_id": self.voice_id,
            "primary": "ElevenLabs" if self.elevenlabs_client else "Edge TTS"
        }

    def set_default_voice(self, voice_id: str) -> None:
        self.voice_id = voice_id

    def list_voices(self) -> list:
        """Return the available ElevenLabs voices for this account."""
        if not self.elevenlabs_client:
            return []
        try:
            result = self.elevenlabs_client.voices.get_all()
            items = []
            for v in getattr(result, "voices", []) or []:
                items.append({
                    "voice_id": getattr(v, "voice_id", None),
                    "name": getattr(v, "name", None),
                    "labels": getattr(v, "labels", {}) or {},
                    "category": getattr(v, "category", None),
                    "preview_url": getattr(v, "preview_url", None),
                    "description": getattr(v, "description", None),
                })
            return items
        except Exception as e:
            print(f"[LILITH VOICE] list_voices error: {e}")
            return []


# Singleton instance
_voice_engine = None

def get_voice_engine() -> LilithVoiceEngine:
    global _voice_engine
    if _voice_engine is None:
        _voice_engine = LilithVoiceEngine()
    return _voice_engine


# Quick test
if __name__ == "__main__":
    engine = get_voice_engine()
    print("Status:", engine.get_status())
    
    result = engine.generate_speech("Hello darling, I've been waiting for you...")
    if result:
        print(f"Generated audio: {len(result)} chars base64")
    else:
        print("Failed to generate audio")
