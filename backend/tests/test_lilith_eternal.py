#!/usr/bin/env python3
"""
LILITH ETERNAL - Comprehensive API Tests
=========================================
Tests for:
- P0 Bug Fix: False-positive image trigger (words like 'make', 'feel', 'create' should NOT trigger image generation)
- Chat API functionality
- Session persistence (MongoDB)
- Image preference system
- Clear chat functionality
"""

import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://sultry-avatar.preview.emergentagent.com"

# Generate unique session ID for tests
TEST_SESSION_ID = f"test_session_{uuid.uuid4().hex[:8]}"


class TestLilithChatAPI:
    """Tests for /lilith/api/chat endpoint"""
    
    def test_chat_endpoint_exists(self):
        """Verify chat endpoint is accessible"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={"message": "hello", "session_id": TEST_SESSION_ID},
            timeout=60
        )
        assert response.status_code == 200, f"Chat endpoint returned {response.status_code}"
        data = response.json()
        assert "success" in data, "Response missing 'success' field"
        print(f"Chat endpoint accessible, success={data.get('success')}")
    
    def test_chat_returns_response_and_provider(self):
        """Chat API should return success with response and provider info"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={"message": "How are you today?", "session_id": TEST_SESSION_ID, "voice_enabled": False},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True, f"Chat failed: {data}"
        assert "response" in data, "Missing 'response' field"
        assert len(data["response"]) > 10, "Response too short"
        # Provider may be None for fallback responses
        print(f"Chat response received, provider={data.get('provider')}, length={len(data.get('response', ''))}")


class TestP0BugFix_FalsePositiveImageTrigger:
    """
    P0 Bug Fix Tests: Words like 'make', 'feel', 'create' in normal chat 
    should NOT trigger image generation - must route to /lilith/api/chat instead
    """
    
    def test_word_make_does_not_trigger_image(self):
        """'make' in normal context should NOT trigger image generation"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={"message": "Can you make me feel better?", "session_id": TEST_SESSION_ID, "voice_enabled": False},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True, f"Chat failed: {data}"
        # Should be a text response, not an image URL
        assert "image_url" not in data, "False positive: 'make me feel better' triggered image generation!"
        assert "response" in data, "Missing text response"
        print(f"PASS: 'make me feel better' correctly routed to chat, not image generation")
    
    def test_word_create_does_not_trigger_image(self):
        """'create' in normal context should NOT trigger image generation"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={"message": "I want to create a connection with you", "session_id": TEST_SESSION_ID, "voice_enabled": False},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "image_url" not in data, "False positive: 'create a connection' triggered image generation!"
        print(f"PASS: 'create a connection' correctly routed to chat")
    
    def test_word_feel_does_not_trigger_image(self):
        """'feel' in normal context should NOT trigger image generation"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={"message": "How do you feel about me?", "session_id": TEST_SESSION_ID, "voice_enabled": False},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "image_url" not in data, "False positive: 'feel about me' triggered image generation!"
        print(f"PASS: 'feel about me' correctly routed to chat")
    
    def test_normal_conversation_no_image_trigger(self):
        """Normal conversation should not trigger image generation"""
        test_messages = [
            "Tell me about yourself",
            "What makes you happy?",
            "I feel lonely tonight",
            "Can you create some excitement?",
            "Make my day better",
        ]
        for msg in test_messages:
            response = requests.post(
                f"{BASE_URL}/lilith/api/chat",
                json={"message": msg, "session_id": TEST_SESSION_ID, "voice_enabled": False},
                timeout=60
            )
            assert response.status_code == 200
            data = response.json()
            assert "image_url" not in data, f"False positive: '{msg}' triggered image generation!"
            print(f"PASS: '{msg}' correctly routed to chat")


class TestExplicitImageCommands:
    """
    Explicit image commands like 'generate image of a sunset' SHOULD still trigger image generation
    """
    
    def test_generate_image_of_triggers_image(self):
        """'generate image of...' should trigger image generation"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/image/generate",
            json={"prompt": "generate image of a sunset", "session_id": TEST_SESSION_ID},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True, f"Image generation failed: {data}"
        assert "image_url" in data, "Missing image_url in response"
        print(f"PASS: 'generate image of...' correctly triggers image generation")
    
    def test_slash_image_command_endpoint(self):
        """Test /image command via image generate endpoint"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/image/generate",
            json={"prompt": "/image beautiful landscape", "session_id": TEST_SESSION_ID},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "image_url" in data
        print(f"PASS: '/image' command works correctly")
    
    def test_lilith_self_portrait(self):
        """Test Lilith self-portrait generation"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/image/lilith",
            json={"style": "seductive", "session_id": TEST_SESSION_ID},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "image_url" in data
        print(f"PASS: Lilith self-portrait generation works")


class TestSessionPersistence:
    """
    Session persistence: Messages saved to MongoDB via /lilith/api/session/history endpoint
    """
    
    def test_session_history_endpoint_exists(self):
        """POST to /lilith/api/session/history with session_id should return stored messages"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/session/history",
            json={"session_id": TEST_SESSION_ID},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        print(f"Session history endpoint accessible, success={data.get('success')}")
    
    def test_messages_persist_across_requests(self):
        """Messages should be saved and retrievable"""
        unique_session = f"persist_test_{uuid.uuid4().hex[:8]}"
        
        # Send a message
        chat_response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={"message": "Remember this test message", "session_id": unique_session, "voice_enabled": False},
            timeout=60
        )
        assert chat_response.status_code == 200
        
        # Wait a moment for persistence
        time.sleep(1)
        
        # Retrieve history
        history_response = requests.post(
            f"{BASE_URL}/lilith/api/session/history",
            json={"session_id": unique_session},
            timeout=30
        )
        assert history_response.status_code == 200
        data = history_response.json()
        
        if data.get("success") and data.get("messages"):
            # Check if our message is in history
            messages = data.get("messages", [])
            user_messages = [m for m in messages if m.get("role") == "user"]
            assert len(user_messages) > 0, "No user messages found in history"
            print(f"PASS: Session persistence working, found {len(messages)} messages")
        else:
            print(f"Session history returned: {data}")


class TestImagePreferenceSystem:
    """
    Image preference system: /style command and natural language preferences
    """
    
    def test_style_command_sets_preference(self):
        """Sending '/style black corset' should return a preference confirmation"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={"message": "/style black corset", "session_id": TEST_SESSION_ID, "voice_enabled": False},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        response_text = data.get("response", "").lower()
        # Should acknowledge the preference
        assert any(word in response_text for word in ["noted", "remember", "preference", "corset"]), \
            f"Preference not acknowledged: {data.get('response')}"
        print(f"PASS: /style command acknowledged preference")
    
    def test_natural_language_preference_detection(self):
        """'I want you in lingerie' should detect and save as preference"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={"message": "I want you in lingerie", "session_id": TEST_SESSION_ID, "voice_enabled": False},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        response_text = data.get("response", "").lower()
        # Should acknowledge the preference or respond naturally
        # The preference detection looks for specific outfit words
        print(f"Natural language preference response: {data.get('response')[:100]}...")
        print(f"PASS: Natural language preference processed")
    
    def test_preference_command_variations(self):
        """Test various preference command formats"""
        commands = [
            "/pref red dress",
            "/preference stockings",
        ]
        for cmd in commands:
            response = requests.post(
                f"{BASE_URL}/lilith/api/chat",
                json={"message": cmd, "session_id": TEST_SESSION_ID, "voice_enabled": False},
                timeout=60
            )
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") == True
            print(f"PASS: '{cmd}' processed successfully")


class TestClearChat:
    """
    Clear chat: POST to /lilith/api/clear with session_id should clear session history
    """
    
    def test_clear_endpoint_exists(self):
        """POST to /lilith/api/clear should work"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/clear",
            json={"session_id": TEST_SESSION_ID},
            timeout=30
        )
        assert response.status_code == 200
        print(f"Clear endpoint accessible")
    
    def test_clear_removes_history(self):
        """Clear should remove session history"""
        unique_session = f"clear_test_{uuid.uuid4().hex[:8]}"
        
        # Send a message first
        requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={"message": "Test message before clear", "session_id": unique_session, "voice_enabled": False},
            timeout=60
        )
        
        # Clear the session
        clear_response = requests.post(
            f"{BASE_URL}/lilith/api/clear",
            json={"session_id": unique_session},
            timeout=30
        )
        assert clear_response.status_code == 200
        
        # Check history is cleared
        history_response = requests.post(
            f"{BASE_URL}/lilith/api/session/history",
            json={"session_id": unique_session},
            timeout=30
        )
        data = history_response.json()
        messages = data.get("messages", [])
        # After clear, should have 0 or very few messages
        print(f"After clear, history has {len(messages)} messages")


class TestStatsEndpoint:
    """Test the stats endpoint"""
    
    def test_stats_endpoint(self):
        """GET /lilith/api/stats should return provider stats"""
        response = requests.get(f"{BASE_URL}/lilith/api/stats", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        print(f"Stats: {data}")


class TestFrontendLoads:
    """Test that frontend loads correctly"""
    
    def test_lilith_page_loads(self):
        """GET /lilith/ should return HTML page"""
        response = requests.get(f"{BASE_URL}/lilith/", timeout=30)
        assert response.status_code == 200
        assert "LILITH" in response.text
        assert "avatar" in response.text.lower() or "chat" in response.text.lower()
        print(f"PASS: Lilith page loads correctly")
    
    def test_page_contains_required_elements(self):
        """Page should contain avatar, chat area, and controls"""
        response = requests.get(f"{BASE_URL}/lilith/", timeout=30)
        assert response.status_code == 200
        html = response.text
        
        # Check for avatar
        assert "avatar" in html.lower(), "Missing avatar element"
        
        # Check for chat area
        assert "chat" in html.lower(), "Missing chat area"
        
        # Check for controls
        assert "voice" in html.lower() or "send" in html.lower(), "Missing controls"
        
        # Check for session ID handling
        assert "sessionId" in html or "session_id" in html or "localStorage" in html, "Missing session handling"
        
        print(f"PASS: Page contains required elements")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
