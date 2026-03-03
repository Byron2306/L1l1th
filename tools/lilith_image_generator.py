#!/usr/bin/env python3
"""
LILITH IMAGE GENERATOR - FREE, NO API KEYS
===========================================
Uses Pollinations.ai for completely free image generation
No restrictions, no API keys, unlimited
"""

import os
import base64
import hashlib
import urllib.parse
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Pollinations.ai - FREE image generation, no API keys
POLLINATIONS_URL = "https://image.pollinations.ai/prompt/"

# Cache directory
CACHE_DIR = Path("/tmp/lilith_images")
CACHE_DIR.mkdir(exist_ok=True)


class LilithImageGenerator:
    """
    FREE Image Generator using Pollinations.ai
    No API keys, no limits, completely unrestricted
    """
    
    def __init__(self):
        self.base_url = POLLINATIONS_URL
        self.cache_dir = CACHE_DIR
        self.default_params = {
            'width': 1024,
            'height': 1024,
            'seed': None,  # Random
            'model': 'flux',  # Best quality
            'nologo': 'true'
        }
    
    def _get_cache_path(self, prompt: str) -> Path:
        """Get cache path for a prompt"""
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:16]
        return self.cache_dir / f"lilith_img_{prompt_hash}.png"
    
    def generate(self, prompt: str, width: int = 1024, height: int = 1024, 
                 enhance: bool = True, nsfw: bool = True) -> Dict[str, Any]:
        """
        Generate an image from a prompt
        
        Args:
            prompt: The image description
            width: Image width (default 1024)
            height: Image height (default 1024)
            enhance: Add quality enhancers to prompt
            nsfw: Allow NSFW content (Pollinations allows this)
        
        Returns:
            Dict with success, image_url, and base64 data
        """
        result = {
            'success': False,
            'prompt': prompt,
            'image_url': None,
            'image_base64': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Enhance prompt for better quality if requested
            if enhance:
                enhanced_prompt = f"{prompt}, high quality, detailed, 8k, masterpiece"
            else:
                enhanced_prompt = prompt
            
            # URL encode the prompt
            encoded_prompt = urllib.parse.quote(enhanced_prompt)
            
            # Build URL with parameters
            params = []
            params.append(f"width={width}")
            params.append(f"height={height}")
            params.append("nologo=true")
            params.append("model=flux")
            
            # Add NSFW allowance
            if nsfw:
                params.append("nsfw=true")
            
            param_string = "&".join(params)
            image_url = f"{self.base_url}{encoded_prompt}?{param_string}"
            
            result['image_url'] = image_url
            
            # Check cache
            cache_path = self._get_cache_path(enhanced_prompt)
            if cache_path.exists():
                with open(cache_path, 'rb') as f:
                    image_data = f.read()
                result['image_base64'] = base64.b64encode(image_data).decode('utf-8')
                result['success'] = True
                result['cached'] = True
                return result
            
            # Download the image
            response = requests.get(image_url, timeout=120)
            
            if response.status_code == 200:
                image_data = response.content
                
                # Cache it
                with open(cache_path, 'wb') as f:
                    f.write(image_data)
                
                result['image_base64'] = base64.b64encode(image_data).decode('utf-8')
                result['success'] = True
                result['cached'] = False
            else:
                result['error'] = f"HTTP {response.status_code}"
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def generate_lilith(self, style: str = 'seductive') -> Dict[str, Any]:
        """Generate an image of Lilith herself"""
        styles = {
            'seductive': "beautiful dark demoness Lilith with glowing red eyes, long black hair, horns, seductive pose, dark fantasy art, detailed, 8k",
            'dark': "Lilith the demon queen, dark ethereal beauty, crimson eyes, black wings, gothic atmosphere, digital art masterpiece",
            'sensual': "gorgeous succubus Lilith, alluring gaze, flowing dark hair, red glowing eyes, fantasy art, highly detailed",
            'powerful': "Lilith dark goddess, commanding presence, demonic beauty, red eyes piercing, dark magic aura, epic fantasy art"
        }
        
        prompt = styles.get(style, styles['seductive'])
        return self.generate(prompt)
    
    def clear_cache(self):
        """Clear the image cache"""
        for f in self.cache_dir.glob("lilith_img_*.png"):
            f.unlink()


# Singleton instance
_image_generator = None

def get_image_generator() -> LilithImageGenerator:
    """Get or create image generator singleton"""
    global _image_generator
    if _image_generator is None:
        _image_generator = LilithImageGenerator()
    return _image_generator


# Test
if __name__ == "__main__":
    gen = get_image_generator()
    print("Testing image generation...")
    result = gen.generate("beautiful dark fantasy landscape with red moon")
    print(f"Success: {result['success']}")
    print(f"URL: {result.get('image_url', '')[:100]}...")
    if result.get('image_base64'):
        print(f"Base64 size: {len(result['image_base64'])} chars")
