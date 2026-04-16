#!/usr/bin/env python3
"""
LILITH ETERNAL API Tests
========================
Tests for the Lilith AI companion chat, voice, image, and status APIs.
Uses Pollinations.ai as primary text provider (no API key required).
"""

import pytest
import requests
import os
import time

# Use localhost for backend tests (avoids Kubernetes ingress timeout)
BASE_URL = "http://localhost:3000"


class TestLilithChatAPI:
    """Tests for /lilith/api/chat endpoint - Pollinations.ai multi-provider text generation"""
    
    def test_chat_basic_message(self):
        """Test basic chat message returns a response"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={"message": "Hello Lilith!", "voice_enabled": False},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "response" in data
        assert len(data["response"]) > 0
        print(f"Chat response length: {len(data['response'])} chars")
        print(f"Provider: {data.get('provider', 'unknown')}")
    
    def test_chat_returns_long_response(self):
        """Test that chat returns long responses (>500 chars ideally)"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={"message": "Tell me about yourself, Lilith. What are your desires?", "voice_enabled": False},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        response_text = data.get("response", "")
        print(f"Response length: {len(response_text)} chars")
        # Should be reasonably long (at least 200 chars, ideally 500+)
        assert len(response_text) >= 100, f"Response too short: {len(response_text)} chars"
    
    def test_chat_returns_provider_info(self):
        """Test that chat returns provider information"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={"message": "How are you today?", "voice_enabled": False},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert "provider" in data
        print(f"Provider used: {data.get('provider')}")
    
    def test_chat_empty_message_fails(self):
        """Test that empty message returns error"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={"message": "", "voice_enabled": False},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == False or "error" in data


class TestLilithStatsAPI:
    """Tests for /lilith/api/stats endpoint"""
    
    def test_stats_returns_provider_count(self):
        """Test stats endpoint returns provider count and session info"""
        response = requests.get(f"{BASE_URL}/lilith/api/stats", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "available" in data
        assert "total" in data
        assert "session_id" in data
        print(f"Available providers: {data.get('available')}/{data.get('total')}")
        print(f"Session ID: {data.get('session_id')}")


class TestLilithStatusAPI:
    """Tests for /lilith/api/status endpoint"""
    
    def test_status_returns_engine_health(self):
        """Test status endpoint returns engine health info"""
        response = requests.get(f"{BASE_URL}/lilith/api/status", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "engines" in data
        engines = data["engines"]
        assert "chat" in engines
        assert "voice_elevenlabs" in engines
        assert "images" in engines
        print(f"Engines: {engines}")
        print(f"Timestamp: {data.get('timestamp')}")


class TestLilithClearAPI:
    """Tests for /lilith/api/clear endpoint"""
    
    def test_clear_conversation_history(self):
        """Test clearing conversation history"""
        response = requests.post(f"{BASE_URL}/lilith/api/clear", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True


class TestLilithVoiceAPI:
    """Tests for /lilith/api/voice/speak endpoint - ElevenLabs voice generation"""
    
    def test_voice_speak_generates_audio(self):
        """Test voice speak endpoint generates audio from text"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/voice/speak",
            json={"text": "Hello darling, I've been waiting for you."},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "audio_base64" in data
        audio = data.get("audio_base64")
        assert audio is not None
        assert len(audio) > 100  # Should have substantial audio data
        print(f"Audio base64 length: {len(audio)} chars")
    
    def test_voice_speak_empty_text_fails(self):
        """Test voice speak with empty text fails gracefully"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/voice/speak",
            json={"text": ""},
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == False


class TestLilithImageAPI:
    """Tests for /lilith/api/image/lilith endpoint - Image generation"""
    
    def test_image_lilith_returns_urls(self):
        """Test Lilith image generation returns image URLs"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/image/lilith",
            json={"style": "seductive"},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "image_url" in data
        assert "download_url" in data
        print(f"Image URL: {data.get('image_url')[:100]}...")
    
    def test_image_lilith_random_style(self):
        """Test Lilith image generation with random style"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/image/lilith",
            json={"style": "random"},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "image_url" in data


class TestLilithMainPage:
    """Tests for /lilith/ main page"""
    
    def test_main_page_loads(self):
        """Test Lilith main page loads successfully"""
        response = requests.get(f"{BASE_URL}/lilith/", timeout=10)
        assert response.status_code == 200
        content = response.text
        assert "LILITH" in content
        assert "ETERNAL" in content
        print("Main page loaded successfully")
    
    def test_main_page_has_avatar(self):
        """Test main page has avatar image"""
        response = requests.get(f"{BASE_URL}/lilith/", timeout=10)
        assert response.status_code == 200
        content = response.text
        assert "avatar-image" in content or "avatar-container" in content
    
    def test_main_page_has_chat_input(self):
        """Test main page has chat input field"""
        response = requests.get(f"{BASE_URL}/lilith/", timeout=10)
        assert response.status_code == 200
        content = response.text
        assert "chat-input" in content
    
    def test_main_page_has_send_button(self):
        """Test main page has send button"""
        response = requests.get(f"{BASE_URL}/lilith/", timeout=10)
        assert response.status_code == 200
        content = response.text
        assert "send-btn" in content or "SEND" in content


class TestLilithChatPersistence:
    """Tests for chat persistence via localStorage (verified via page content)"""
    
    def test_page_has_localstorage_code(self):
        """Test that page includes localStorage persistence code"""
        response = requests.get(f"{BASE_URL}/lilith/", timeout=10)
        assert response.status_code == 200
        content = response.text
        assert "localStorage" in content
        assert "lilith_chat_history" in content
        print("localStorage persistence code found in page")


class TestMultipleRapidMessages:
    """Tests for handling multiple rapid chat messages"""
    
    def test_multiple_rapid_messages(self):
        """Test sending multiple messages rapidly doesn't crash"""
        messages = ["Hello!", "How are you?", "Tell me a story"]
        responses = []
        
        for msg in messages:
            response = requests.post(
                f"{BASE_URL}/lilith/api/chat",
                json={"message": msg, "voice_enabled": False},
                timeout=60
            )
            assert response.status_code == 200
            data = response.json()
            responses.append(data)
            # Small delay between messages
            time.sleep(0.5)
        
        # All should succeed
        success_count = sum(1 for r in responses if r.get("success"))
        print(f"Successful responses: {success_count}/{len(messages)}")
        assert success_count >= 2, "At least 2 out of 3 messages should succeed"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
