#!/usr/bin/env python3
"""
LILITH ETERNAL v8 - Backend API Tests
======================================
Tests for:
- Chat API stability (3 consecutive messages)
- P0 Bug Fix (words like 'make', 'feel', 'create' don't trigger image)
- /style command for image preferences
- Session persistence
- Provider count (>20)
- Telegram bot status
"""

import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://sultry-avatar.preview.emergentagent.com"

# Test session ID
TEST_SESSION_ID = f"test_session_{uuid.uuid4().hex[:8]}"


class TestLilithStats:
    """Test /lilith/api/stats endpoint - Provider count verification"""
    
    def test_stats_endpoint_returns_success(self):
        """Stats endpoint should return success"""
        response = requests.get(f"{BASE_URL}/lilith/api/stats", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        print(f"Stats response: {data}")
    
    def test_provider_count_greater_than_20(self):
        """Provider count should be > 20 (expanded providers)"""
        response = requests.get(f"{BASE_URL}/lilith/api/stats", timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        # Check available providers
        available = data.get('available', 0)
        total = data.get('total', 0)
        
        print(f"Available providers: {available}, Total: {total}")
        assert available > 20, f"Expected >20 providers, got {available}"
        assert total > 20, f"Expected >20 total providers, got {total}"


class TestChatAPIStability:
    """Test Chat API stability with 3 consecutive messages"""
    
    def test_chat_message_1(self):
        """First chat message should return success"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={
                "message": "Hello Lilith, how are you?",
                "voice_enabled": False,
                "session_id": TEST_SESSION_ID
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'response' in data
        assert len(data['response']) > 10
        print(f"Chat 1 - Provider: {data.get('provider')}, Response length: {len(data['response'])}")
    
    def test_chat_message_2(self):
        """Second chat message should return success"""
        time.sleep(2)  # Small delay between messages
        response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={
                "message": "Tell me something interesting",
                "voice_enabled": False,
                "session_id": TEST_SESSION_ID
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'response' in data
        assert len(data['response']) > 10
        print(f"Chat 2 - Provider: {data.get('provider')}, Response length: {len(data['response'])}")
    
    def test_chat_message_3(self):
        """Third chat message should return success"""
        time.sleep(2)  # Small delay between messages
        response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={
                "message": "What's your favorite thing to do?",
                "voice_enabled": False,
                "session_id": TEST_SESSION_ID
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'response' in data
        assert len(data['response']) > 10
        print(f"Chat 3 - Provider: {data.get('provider')}, Response length: {len(data['response'])}")


class TestP0BugFix:
    """Test P0 Bug Fix - Words like 'make', 'feel', 'create' should NOT trigger image generation"""
    
    def test_make_word_does_not_trigger_image(self):
        """'Can you make me feel better?' should go to chat, not image"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={
                "message": "Can you make me feel better?",
                "voice_enabled": False,
                "session_id": TEST_SESSION_ID
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        # Should be a text response, not an image URL
        assert 'response' in data
        assert 'image_url' not in data or data.get('image_url') is None
        print(f"'make' test - Got chat response: {data['response'][:100]}...")
    
    def test_feel_word_does_not_trigger_image(self):
        """'How do you feel about me?' should go to chat, not image"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={
                "message": "How do you feel about me?",
                "voice_enabled": False,
                "session_id": TEST_SESSION_ID
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'response' in data
        assert 'image_url' not in data or data.get('image_url') is None
        print(f"'feel' test - Got chat response: {data['response'][:100]}...")
    
    def test_create_word_does_not_trigger_image(self):
        """'I want to create a connection with you' should go to chat, not image"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={
                "message": "I want to create a connection with you",
                "voice_enabled": False,
                "session_id": TEST_SESSION_ID
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'response' in data
        assert 'image_url' not in data or data.get('image_url') is None
        print(f"'create' test - Got chat response: {data['response'][:100]}...")


class TestStyleCommand:
    """Test /style command for image preferences"""
    
    def test_style_command_recognized(self):
        """/style command should be recognized and acknowledged"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={
                "message": "/style black corset with stockings",
                "voice_enabled": False,
                "session_id": TEST_SESSION_ID
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'response' in data
        # Should acknowledge the preference
        response_lower = data['response'].lower()
        assert any(word in response_lower for word in ['noted', 'remember', 'preference', 'corset', 'stockings'])
        print(f"/style command response: {data['response'][:150]}...")
    
    def test_pref_command_recognized(self):
        """/pref command should also work"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={
                "message": "/pref red lingerie",
                "voice_enabled": False,
                "session_id": TEST_SESSION_ID
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'response' in data
        print(f"/pref command response: {data['response'][:150]}...")


class TestSessionPersistence:
    """Test session persistence - messages should be stored and retrievable"""
    
    def test_session_history_endpoint(self):
        """Session history endpoint should return stored messages"""
        # First send a message to create history
        requests.post(
            f"{BASE_URL}/lilith/api/chat",
            json={
                "message": "This is a test message for history",
                "voice_enabled": False,
                "session_id": TEST_SESSION_ID
            },
            timeout=60
        )
        
        time.sleep(1)
        
        # Now check history
        response = requests.post(
            f"{BASE_URL}/lilith/api/session/history",
            json={"session_id": TEST_SESSION_ID},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        
        # Should have messages
        messages = data.get('messages', [])
        count = data.get('count', 0)
        print(f"Session history - Count: {count}, Messages: {len(messages)}")
        assert count > 0 or len(messages) > 0, "Expected at least 1 message in history"


class TestClearChat:
    """Test clear chat functionality"""
    
    def test_clear_endpoint(self):
        """Clear endpoint should work"""
        response = requests.post(
            f"{BASE_URL}/lilith/api/clear",
            json={"session_id": TEST_SESSION_ID},
            timeout=30
        )
        assert response.status_code == 200
        print("Clear chat endpoint working")


class TestTelegramBotStatus:
    """Test Telegram bot is running (via supervisor)"""
    
    def test_telegram_bot_running(self):
        """Telegram bot should be running in supervisor"""
        import subprocess
        result = subprocess.run(
            ['sudo', 'supervisorctl', 'status', 'telegram_bot'],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout + result.stderr
        print(f"Telegram bot status: {output}")
        assert 'RUNNING' in output, f"Telegram bot not running: {output}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
