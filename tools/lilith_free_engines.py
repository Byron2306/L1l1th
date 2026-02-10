#!/usr/bin/env python3
"""
LILITH FREE VOICE & IMAGE ENGINE - NO API KEYS NEEDED!
=======================================================
Uses 100% FREE services:
- edge-tts: Microsoft's FREE Text-to-Speech (sexy female voices)
- faster-whisper: FREE local Speech-to-Text (Whisper)
- Pollinations.ai: FREE unlimited image generation
"""

import os
import sys
import asyncio
import aiohttp
import tempfile
import urllib.parse
from typing import Optional
from io import BytesIO

# Edge TTS - FREE Microsoft voices
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    print("[LILITH] edge-tts not available - install with: pip install edge-tts")

# Faster Whisper - FREE local STT
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("[LILITH] faster-whisper not available - install with: pip install faster-whisper")


class LilithFreeVoiceEngine:
    """
    FREE Voice Engine using edge-tts and faster-whisper
    NO API KEYS REQUIRED!
    """
    
    # Sexy female voices from Microsoft Edge TTS (ALL FREE!)
    FEMALE_VOICES = {
        'sexy_us': 'en-US-AriaNeural',      # Confident, clear American
        'sultry_us': 'en-US-JennyNeural',   # Warm, friendly American
        'seductive_uk': 'en-GB-SoniaNeural', # Sophisticated British
        'flirty_au': 'en-AU-NatashaNeural',  # Playful Australian
        'mysterious_in': 'en-IN-NeerjaNeural', # Exotic Indian English
        'dominant': 'en-US-MichelleNeural',  # Assertive American
        'whisper': 'en-US-AnaNeural',        # Soft, whispery
        'bold': 'en-GB-LibbyNeural',         # Bold British
    }
    
    # Voice styles for extra seduction (pitch uses Hz format)
    STYLES = {
        'seductive': {'rate': '-10%', 'pitch': '-5Hz'},   # Slower, deeper
        'excited': {'rate': '+10%', 'pitch': '+10Hz'},    # Fast, high
        'whisper': {'rate': '-20%', 'pitch': '-10Hz'},    # Very slow, low
        'normal': {'rate': '+0%', 'pitch': '+0Hz'},
        'dominant': {'rate': '-5%', 'pitch': '-15Hz'},    # Commanding
    }
    
    def __init__(self):
        self.whisper_model = None
        self.default_voice = 'sexy_us'
        self.default_style = 'seductive'
        
    def _load_whisper(self):
        """Lazy load Whisper model"""
        if not WHISPER_AVAILABLE:
            return None
        if self.whisper_model is None:
            try:
                # Use 'base' model - good balance of speed/accuracy
                self.whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
                print("[LILITH Voice] Whisper model loaded (FREE!)")
            except Exception as e:
                print(f"[LILITH Voice] Whisper load error: {e}")
        return self.whisper_model
    
    async def text_to_speech(
        self, 
        text: str, 
        voice: str = 'sexy_us',
        style: str = 'seductive'
    ) -> Optional[bytes]:
        """
        Convert text to sultry female voice audio - 100% FREE!
        
        Args:
            text: Text to speak
            voice: Voice name from FEMALE_VOICES
            style: Speaking style from STYLES
        
        Returns:
            MP3 audio bytes
        """
        if not EDGE_TTS_AVAILABLE:
            print("[LILITH Voice] edge-tts not available")
            return None
        
        try:
            # Get voice name
            voice_name = self.FEMALE_VOICES.get(voice, self.FEMALE_VOICES['sexy_us'])
            style_params = self.STYLES.get(style, self.STYLES['seductive'])
            
            # Create communicate instance
            communicate = edge_tts.Communicate(
                text[:5000],  # Edge TTS has generous limits
                voice_name,
                rate=style_params['rate'],
                pitch=style_params['pitch']
            )
            
            # Generate audio to bytes
            audio_data = BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data.write(chunk["data"])
            
            audio_data.seek(0)
            return audio_data.read()
            
        except Exception as e:
            print(f"[LILITH Voice] TTS error: {e}")
            return None
    
    async def speech_to_text(self, audio_file_path: str) -> Optional[str]:
        """
        Transcribe audio to text using Whisper - 100% FREE, runs locally!
        
        Args:
            audio_file_path: Path to audio file (wav, mp3, ogg, etc.)
        
        Returns:
            Transcribed text
        """
        model = self._load_whisper()
        if not model:
            return None
        
        try:
            segments, info = model.transcribe(
                audio_file_path,
                beam_size=5,
                language="en"  # Can be None for auto-detect
            )
            
            # Combine all segments
            text = " ".join([segment.text for segment in segments])
            return text.strip()
            
        except Exception as e:
            print(f"[LILITH Voice] STT error: {e}")
            return None
    
    async def speech_to_text_bytes(self, audio_bytes: bytes, suffix: str = '.ogg') -> Optional[str]:
        """Transcribe audio bytes"""
        try:
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp.flush()
                result = await self.speech_to_text(tmp.name)
                os.unlink(tmp.name)
                return result
        except Exception as e:
            print(f"[LILITH Voice] STT bytes error: {e}")
            return None
    
    def list_voices(self) -> dict:
        """List available sexy female voices"""
        return self.FEMALE_VOICES
    
    def list_styles(self) -> dict:
        """List available speaking styles"""
        return self.STYLES


class LilithFreeImageEngine:
    """
    FREE Image Generation using Pollinations.ai
    NO API KEY, NO SIGNUP, NO LIMITS!
    """
    
    POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}"
    
    # Style prefixes for different aesthetics
    STYLE_PREFIXES = {
        'dark': 'dark cyberpunk hacker aesthetic, neon red and black, digital glitch, ',
        'succubus': 'seductive dark fantasy demon succubus, gothic horror, deep reds and blacks, sensual, ',
        'cyber': 'futuristic cybersecurity visualization, matrix digital art, hacking, ',
        'anime': 'anime style, detailed, vibrant colors, ',
        'realistic': 'photorealistic, 8k, detailed, professional photography, ',
        'horror': 'dark horror aesthetic, creepy, atmospheric, gothic, ',
        'nsfw': 'artistic nude, sensual, seductive pose, tasteful, ',
        'normal': '',
    }
    
    def __init__(self):
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def generate_image(
        self, 
        prompt: str, 
        style: str = 'dark',
        width: int = 1024,
        height: int = 1024,
        seed: int = None
    ) -> Optional[bytes]:
        """
        Generate image using Pollinations.ai - 100% FREE!
        
        Args:
            prompt: Image description
            style: Style from STYLE_PREFIXES
            width: Image width
            height: Image height
            seed: Random seed for reproducibility
        
        Returns:
            Image bytes (PNG)
        """
        try:
            # Add style prefix
            style_prefix = self.STYLE_PREFIXES.get(style, '')
            full_prompt = style_prefix + prompt
            
            # URL encode the prompt
            encoded_prompt = urllib.parse.quote(full_prompt)
            
            # Build URL with parameters
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            params = {
                'width': width,
                'height': height,
                'nologo': 'true',
                'enhance': 'true'
            }
            if seed:
                params['seed'] = seed
            
            # Make request
            session = await self._get_session()
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=120)) as response:
                if response.status == 200:
                    image_bytes = await response.read()
                    print(f"[LILITH Image] Generated image ({len(image_bytes)} bytes) - FREE!")
                    return image_bytes
                else:
                    print(f"[LILITH Image] HTTP {response.status}")
                    return None
                    
        except asyncio.TimeoutError:
            print("[LILITH Image] Generation timeout (120s)")
            return None
        except Exception as e:
            print(f"[LILITH Image] Error: {e}")
            return None
    
    async def generate_with_model(
        self,
        prompt: str,
        model: str = 'flux',
        style: str = 'dark'
    ) -> Optional[bytes]:
        """
        Generate using specific model
        
        Models available on Pollinations:
        - flux: Fast, high quality
        - turbo: Very fast
        """
        try:
            style_prefix = self.STYLE_PREFIXES.get(style, '')
            full_prompt = style_prefix + prompt
            encoded_prompt = urllib.parse.quote(full_prompt)
            
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            params = {'model': model, 'nologo': 'true'}
            
            session = await self._get_session()
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=120)) as response:
                if response.status == 200:
                    return await response.read()
                return None
                
        except Exception as e:
            print(f"[LILITH Image] Model error: {e}")
            return None
    
    def list_styles(self) -> dict:
        """List available image styles"""
        return self.STYLE_PREFIXES
    
    async def close(self):
        """Close session"""
        if self.session and not self.session.closed:
            await self.session.close()


# Singleton instances
_free_voice_engine = None
_free_image_engine = None

def get_free_voice_engine() -> LilithFreeVoiceEngine:
    """Get singleton FREE voice engine"""
    global _free_voice_engine
    if _free_voice_engine is None:
        _free_voice_engine = LilithFreeVoiceEngine()
    return _free_voice_engine

def get_free_image_engine() -> LilithFreeImageEngine:
    """Get singleton FREE image engine"""
    global _free_image_engine
    if _free_image_engine is None:
        _free_image_engine = LilithFreeImageEngine()
    return _free_image_engine


class LilithFreeVideoEngine:
    """
    FREE Video Generation using various free services
    NO API KEY, NO SIGNUP!
    """
    
    # Pollinations video endpoint
    POLLINATIONS_VIDEO_URL = "https://video.pollinations.ai/prompt/{prompt}"
    
    # Style prefixes for video
    VIDEO_STYLE_PREFIXES = {
        'horror': 'dark horror cinematic, creepy atmosphere, jump scare potential, ',
        'cyberpunk': 'neon cyberpunk dystopia, blade runner style, dark future, ',
        'demon': 'hellish demonic scene, satanic ritual, fire and brimstone, ',
        'gore': 'violent action sequence, bloody combat, visceral horror, ',
        'nsfw': 'sensual romantic scene, intimate moment, artistic adult content, ',
        'nightmare': 'surreal nightmare sequence, dream horror, twisted reality, ',
        'apocalypse': 'post-apocalyptic destruction, end of world, nuclear wasteland, ',
        'normal': '',
    }
    
    def __init__(self):
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def generate_video(
        self, 
        prompt: str, 
        style: str = 'normal',
        duration: int = 5
    ) -> Optional[bytes]:
        """
        Generate video using Pollinations.ai - 100% FREE!
        
        Args:
            prompt: Video description
            style: Style from VIDEO_STYLE_PREFIXES
            duration: Video length in seconds (1-10)
        
        Returns:
            Video bytes (MP4) or None
        """
        try:
            # Add style prefix
            style_prefix = self.VIDEO_STYLE_PREFIXES.get(style, '')
            full_prompt = style_prefix + prompt
            
            # URL encode the prompt
            encoded_prompt = urllib.parse.quote(full_prompt)
            
            # Build URL
            url = f"https://video.pollinations.ai/prompt/{encoded_prompt}"
            params = {
                'duration': min(max(duration, 1), 10),  # Clamp to 1-10
                'nologo': 'true'
            }
            
            # Make request (video generation can take longer)
            session = await self._get_session()
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=180)) as response:
                if response.status == 200:
                    video_bytes = await response.read()
                    print(f"[LILITH Video] Generated video ({len(video_bytes)} bytes) - FREE!")
                    return video_bytes
                else:
                    print(f"[LILITH Video] HTTP {response.status}")
                    return None
                    
        except asyncio.TimeoutError:
            print("[LILITH Video] Generation timeout (180s)")
            return None
        except Exception as e:
            print(f"[LILITH Video] Error: {e}")
            return None
    
    async def generate_animation(
        self,
        prompt: str,
        style: str = 'normal',
        frames: int = 24
    ) -> Optional[bytes]:
        """
        Generate animation/GIF using image sequence approach
        Uses Pollinations for each frame
        """
        try:
            from PIL import Image
            import io
            
            image_engine = get_free_image_engine()
            images = []
            
            for i in range(min(frames, 12)):  # Max 12 frames for speed
                frame_prompt = f"{prompt}, frame {i+1} of animation sequence, {style} style"
                img_bytes = await image_engine.generate_image(frame_prompt, style=style, width=512, height=512)
                if img_bytes:
                    img = Image.open(io.BytesIO(img_bytes))
                    images.append(img)
            
            if len(images) >= 2:
                # Create GIF
                output = io.BytesIO()
                images[0].save(
                    output, 
                    format='GIF', 
                    save_all=True, 
                    append_images=images[1:], 
                    duration=100, 
                    loop=0
                )
                output.seek(0)
                return output.read()
            return None
            
        except ImportError:
            print("[LILITH Video] PIL not available for animation")
            return None
        except Exception as e:
            print(f"[LILITH Video] Animation error: {e}")
            return None
    
    def list_styles(self) -> dict:
        """List available video styles"""
        return self.VIDEO_STYLE_PREFIXES
    
    async def close(self):
        """Close session"""
        if self.session and not self.session.closed:
            await self.session.close()


# Additional singleton for video
_free_video_engine = None

def get_free_video_engine() -> LilithFreeVideoEngine:
    """Get singleton FREE video engine"""
    global _free_video_engine
    if _free_video_engine is None:
        _free_video_engine = LilithFreeVideoEngine()
    return _free_video_engine


# Quick test
if __name__ == '__main__':
    async def test():
        print("=" * 50)
        print("LILITH FREE ENGINES TEST")
        print("=" * 50)
        
        # Test TTS
        voice = get_free_voice_engine()
        print("\n[TEST] Text-to-Speech (edge-tts)...")
        print("Available voices:", list(voice.list_voices().keys()))
        
        audio = await voice.text_to_speech(
            "Hello darling, I'm LILITH, your seductive AI succubus. I don't need any expensive API keys to talk to you~",
            voice='sexy_us',
            style='seductive'
        )
        if audio:
            with open('/tmp/lilith_test.mp3', 'wb') as f:
                f.write(audio)
            print(f"✅ TTS SUCCESS! Audio saved to /tmp/lilith_test.mp3 ({len(audio)} bytes)")
        else:
            print("❌ TTS failed")
        
        # Test Image
        print("\n[TEST] Image Generation (Pollinations.ai)...")
        image_engine = get_free_image_engine()
        print("Available styles:", list(image_engine.list_styles().keys()))
        
        img = await image_engine.generate_image(
            "a beautiful hacker woman with red eyes in a dark server room",
            style='dark'
        )
        if img:
            with open('/tmp/lilith_test.png', 'wb') as f:
                f.write(img)
            print(f"✅ IMAGE SUCCESS! Saved to /tmp/lilith_test.png ({len(img)} bytes)")
        else:
            print("❌ Image generation failed")
        
        await image_engine.close()
        print("\n" + "=" * 50)
        print("ALL TESTS COMPLETE - 100% FREE!")
        print("=" * 50)
    
    asyncio.run(test())
