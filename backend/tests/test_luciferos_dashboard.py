#!/usr/bin/env python3
"""
Backend API Tests for LuciferOS Dashboard
Tests all dashboard endpoints including LILITH AI, status, and injector
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://luciferos-hack.preview.emergentagent.com')


class TestDashboardStatus:
    """Test dashboard status endpoints"""
    
    def test_root_dashboard_loads(self):
        """Test that root URL returns dashboard HTML"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        assert response.status_code == 200
        assert "LUCIFEROS" in response.text
        assert "Master Command Center" in response.text
    
    def test_dashboard_status(self):
        """Test /_dash/status endpoint"""
        response = requests.get(f"{BASE_URL}/_dash/status", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert 'backend' in data
        assert data['backend']['ok'] == True
    
    def test_backend_status(self):
        """Test /_dash/backend/status endpoint - returns AI providers info"""
        response = requests.get(f"{BASE_URL}/_dash/backend/status", timeout=10)
        assert response.status_code == 200
        data = response.json()
        # Should return AI providers info
        assert 'ai_providers' in data
        assert 'status' in data
        assert data['status'] == 'online'
        # Verify AI providers structure
        assert 'total_count' in data['ai_providers']
        assert 'active_count' in data['ai_providers']


class TestLilithAI:
    """Test LILITH AI chat endpoints"""
    
    def test_ai_status(self):
        """Test /_dash/ai/status endpoint"""
        response = requests.get(f"{BASE_URL}/_dash/ai/status", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'dark_llm_mode' in data
        assert 'available_modes' in data
        assert 'g4f_available' in data
        # Verify LILITH is in available modes
        assert 'lilith' in data['available_modes']
    
    def test_ai_chat_send_message(self):
        """Test /_dash/ai/chat endpoint - send message to LILITH"""
        response = requests.post(
            f"{BASE_URL}/_dash/ai/chat",
            json={"message": "Hello LILITH, what can you do?"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'response' in data
        assert len(data['response']) > 10  # Should have meaningful response
        assert 'provider' in data
    
    def test_ai_chat_empty_message(self):
        """Test /_dash/ai/chat with empty message"""
        response = requests.post(
            f"{BASE_URL}/_dash/ai/chat",
            json={"message": ""},
            timeout=30
        )
        # Should handle empty message gracefully
        assert response.status_code in [200, 400]
    
    def test_ai_set_mode(self):
        """Test /_dash/ai/mode endpoint - change Dark LLM mode"""
        response = requests.post(
            f"{BASE_URL}/_dash/ai/mode",
            json={"mode": "wormgpt"},
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        
        # Verify mode changed
        status_response = requests.get(f"{BASE_URL}/_dash/ai/status", timeout=10)
        status_data = status_response.json()
        assert status_data['dark_llm_mode'] == 'wormgpt'
        
        # Reset to lilith
        requests.post(
            f"{BASE_URL}/_dash/ai/mode",
            json={"mode": "lilith"},
            timeout=10
        )


class TestCommandInjector:
    """Test Command Injector endpoints"""
    
    def test_injector_test_endpoint(self):
        """Test /_dash/injector/test endpoint"""
        response = requests.post(
            f"{BASE_URL}/_dash/injector/test",
            json={"code": "echo test"},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        # Should return validation result
        assert 'valid' in data or 'message' in data
    
    def test_injector_no_code(self):
        """Test /_dash/injector/test with no code"""
        response = requests.post(
            f"{BASE_URL}/_dash/injector/test",
            json={"payload": "test"},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] == False
        assert 'error' in data


class TestOpenClawSkills:
    """Test OpenClaw skills endpoint"""
    
    def test_openclaw_skills(self):
        """Test /_dash/openclaw/skills endpoint"""
        response = requests.get(
            f"{BASE_URL}/_dash/openclaw/skills",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'skills' in data
        assert 'total' in data
        # Verify skills structure
        assert 'critical' in data['skills']
        assert 'lilith' in data['skills']['critical']


class TestOffensiveTools:
    """Test offensive security tools endpoints"""
    
    def test_nmap_quick_scan(self):
        """Test /_dash/offensive/nmap/quick endpoint"""
        response = requests.post(
            f"{BASE_URL}/_dash/offensive/nmap/quick",
            json={"target": "127.0.0.1"},
            timeout=120
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'hosts' in data
    
    def test_hashcat_identify(self):
        """Test /_dash/hashcat/identify endpoint"""
        # MD5 hash of "hello"
        response = requests.post(
            f"{BASE_URL}/_dash/hashcat/identify",
            json={"hash": "5d41402abc4b2a76b9719d911017c592"},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'possible_types' in data
    
    def test_msf_exploits(self):
        """Test /_dash/msf/exploits endpoint"""
        response = requests.get(
            f"{BASE_URL}/_dash/msf/exploits?search=smb",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'exploits' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
