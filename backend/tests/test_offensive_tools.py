#!/usr/bin/env python3
"""
Backend API Tests for LuciferOS Red-Teaming Platform
Tests offensive security tools integration endpoints
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://demon-companion.preview.emergentagent.com')

class TestDashboardStatus:
    """Test dashboard status endpoints"""
    
    def test_dashboard_status(self):
        """Test /_dash/status endpoint"""
        response = requests.get(f"{BASE_URL}/_dash/status", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert 'backend' in data
        assert data['backend']['ok'] == True
    
    def test_backend_status(self):
        """Test /_dash/backend/status endpoint"""
        response = requests.get(f"{BASE_URL}/_dash/backend/status", timeout=10)
        assert response.status_code == 200
        data = response.json()
        # Should return AI providers info or error
        assert 'ai_providers' in data or 'error' in data


class TestNmapScanner:
    """Test Nmap scanning endpoints"""
    
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
        assert 'scan_info' in data
        # Verify we got scan results
        assert len(data['hosts']) > 0
        assert data['hosts'][0]['status'] == 'up'


class TestDirectoryBruter:
    """Test Dirb directory brute force endpoints"""
    
    def test_dirb_brute_force(self):
        """Test /_dash/offensive/dirs/brute endpoint"""
        response = requests.post(
            f"{BASE_URL}/_dash/offensive/dirs/brute",
            json={"target": "http://127.0.0.1:3000"},
            timeout=120
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert data['tool'] == 'dirb'
        assert 'found_paths' in data
        assert 'wordlist' in data


class TestHydraPasswordCracker:
    """Test Hydra password brute force endpoints"""
    
    def test_hydra_password_brute(self):
        """Test /_dash/offensive/password/brute endpoint"""
        response = requests.post(
            f"{BASE_URL}/_dash/offensive/password/brute",
            json={
                "target": "127.0.0.1",
                "service": "ssh",
                "username": "test",
                "password": "test"
            },
            timeout=120
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert data['tool'] == 'hydra'
        assert 'credentials_found' in data
        assert 'output' in data


class TestNetworkCapture:
    """Test Network packet capture endpoints"""
    
    def test_network_capture_start(self):
        """Test /_dash/network/capture/start endpoint"""
        response = requests.post(
            f"{BASE_URL}/_dash/network/capture/start",
            json={"count": 10, "timeout": 5},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'message' in data
        assert 'eth0' in data['message']
    
    def test_network_capture_status(self):
        """Test /_dash/network/capture/status endpoint"""
        # Wait a bit for capture to complete
        time.sleep(6)
        response = requests.get(
            f"{BASE_URL}/_dash/network/capture/status",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'capturing' in data
        assert 'packets_captured' in data
        assert 'interface' in data


class TestARPScanner:
    """Test ARP scanning endpoints"""
    
    def test_arp_scan(self):
        """Test /_dash/network/arp/scan endpoint"""
        response = requests.post(
            f"{BASE_URL}/_dash/network/arp/scan",
            json={"range": "127.0.0.1/32"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'hosts' in data
        assert 'hosts_found' in data


class TestHashcatIntegration:
    """Test Hashcat hash identification endpoints"""
    
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
        assert len(data['possible_types']) > 0
        # Should identify as MD5
        hash_types = [t['name'] for t in data['possible_types']]
        assert any('MD5' in t for t in hash_types)


class TestMetasploitLite:
    """Test Metasploit-lite integration endpoints (SIMULATED)"""
    
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
        assert 'count' in data
        # Should find SMB exploits
        assert data['count'] > 0
    
    def test_msf_payloads(self):
        """Test /_dash/msf/payloads endpoint"""
        response = requests.get(
            f"{BASE_URL}/_dash/msf/payloads?search=reverse",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'payloads' in data
    
    def test_msf_shells(self):
        """Test /_dash/msf/shells endpoint"""
        response = requests.post(
            f"{BASE_URL}/_dash/msf/shells",
            json={"lhost": "127.0.0.1", "lport": 4444},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'shells' in data


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


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
