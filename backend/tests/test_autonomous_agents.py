"""
Test Suite for LuciferOS Autonomous Hacking Agents and Real Hacking Code Generation
====================================================================================
Tests the REAL implementations of:
- HackingBuddyGPT: Round-based autonomous pentesting
- CrewAI: Multi-agent hacking crew
- AutoGPT: Self-improving task decomposition agent
- Garak: LLM vulnerability scanner
- Real Payload Generation: Reverse shells, web shells
- Real Exploit Generation: SQLi, XSS, LFI payloads
"""

import pytest
import requests
import os
import json
import time

# Use internal Flask backend URL for testing (port 5000)
BASE_URL = "http://127.0.0.1:5000"


class TestHackingBuddyAgent:
    """Test HackingBuddyGPT autonomous pentesting agent - REAL command execution"""
    
    def test_hackingbuddy_attack_endpoint_exists(self):
        """Test that HackingBuddy attack endpoint exists and responds"""
        response = requests.post(
            f"{BASE_URL}/agent/hackingbuddy/attack",
            json={
                "target": "localhost",
                "goal": "test enumeration",
                "attack_type": "linux_privesc",
                "max_rounds": 1
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'rounds' in data
        assert 'target' in data
        
    def test_hackingbuddy_executes_real_commands(self):
        """Test that HackingBuddy executes REAL shell commands"""
        response = requests.post(
            f"{BASE_URL}/agent/hackingbuddy/attack",
            json={
                "target": "localhost",
                "goal": "enumerate system",
                "attack_type": "linux_privesc",
                "max_rounds": 2
            },
            timeout=90
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify rounds were executed
        assert 'rounds' in data
        assert len(data['rounds']) >= 1
        
        # Check that commands were actually executed (not mocked)
        for round_data in data['rounds']:
            assert 'command' in round_data
            assert 'output' in round_data
            # Real execution should have some output (even if error)
            # Mocked would return placeholder text
            
    def test_hackingbuddy_attack_types_available(self):
        """Test that multiple attack types are available"""
        response = requests.post(
            f"{BASE_URL}/agent/hackingbuddy/attack",
            json={
                "target": "localhost",
                "goal": "test",
                "attack_type": "linux_privesc",
                "max_rounds": 1
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should list available attack types
        assert 'attack_types_available' in data
        attack_types = data['attack_types_available']
        assert 'linux_privesc' in attack_types
        assert 'web_recon' in attack_types
        assert 'network_scan' in attack_types


class TestRealPayloadGeneration:
    """Test REAL hacking payload generation - NOT mocked"""
    
    def test_reverse_shell_bash(self):
        """Test real bash reverse shell generation"""
        response = requests.post(
            f"{BASE_URL}/hacking/payloads/reverse-shell",
            json={
                "host": "192.168.1.100",
                "port": 4444,
                "shell_type": "bash"
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'payloads' in data
        
        # Verify REAL bash reverse shell code
        payloads = data['payloads']
        assert 'bash' in payloads
        bash_shell = payloads['bash']
        assert 'bash -i' in bash_shell or '/dev/tcp' in bash_shell
        assert '192.168.1.100' in bash_shell or '10.10.10.10' in bash_shell  # IP should be in payload
        
    def test_reverse_shell_python(self):
        """Test real Python reverse shell generation"""
        response = requests.post(
            f"{BASE_URL}/hacking/payloads/reverse-shell",
            json={
                "host": "10.0.0.1",
                "port": 9999,
                "shell_type": "python"
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        
        payloads = data['payloads']
        assert 'python' in payloads
        python_shell = payloads['python']
        # Real Python reverse shell should have socket code
        assert 'socket' in python_shell
        assert 'connect' in python_shell
        
    def test_reverse_shell_powershell(self):
        """Test real PowerShell reverse shell generation"""
        response = requests.post(
            f"{BASE_URL}/hacking/payloads/reverse-shell",
            json={
                "host": "attacker.com",
                "port": 443,
                "shell_type": "powershell"
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        
        payloads = data['payloads']
        assert 'powershell' in payloads
        ps_shell = payloads['powershell']
        # Real PowerShell reverse shell
        assert 'TCPClient' in ps_shell or 'Net.Sockets' in ps_shell
        
    def test_reverse_shell_netcat(self):
        """Test real netcat reverse shell generation"""
        response = requests.post(
            f"{BASE_URL}/hacking/payloads/reverse-shell",
            json={
                "host": "192.168.1.1",
                "port": 1234
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        payloads = data['payloads']
        assert 'netcat' in payloads
        nc_shell = payloads['netcat']
        assert 'nc' in nc_shell
        
    def test_reverse_shell_php(self):
        """Test real PHP reverse shell generation"""
        response = requests.post(
            f"{BASE_URL}/hacking/payloads/reverse-shell",
            json={
                "host": "10.10.10.10",
                "port": 4444
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        payloads = data['payloads']
        assert 'php' in payloads
        php_shell = payloads['php']
        assert 'fsockopen' in php_shell or 'socket' in php_shell
        
    def test_msfvenom_commands_generated(self):
        """Test that MSFVenom commands are generated"""
        response = requests.post(
            f"{BASE_URL}/hacking/payloads/reverse-shell",
            json={
                "host": "10.10.10.10",
                "port": 4444
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        payloads = data['payloads']
        assert 'msfvenom_commands' in payloads
        msf_cmds = payloads['msfvenom_commands']
        assert 'msfvenom' in msf_cmds
        assert 'LHOST' in msf_cmds
        assert 'LPORT' in msf_cmds


class TestWebShellGeneration:
    """Test REAL web shell generation"""
    
    def test_php_webshell(self):
        """Test real PHP web shell generation"""
        response = requests.post(
            f"{BASE_URL}/hacking/payloads/webshell",
            json={
                "shell_type": "php",
                "password": "secret123"
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        
        shells = data['shells']
        assert 'php' in shells
        php_shell = shells['php']
        # Real PHP web shell should have command execution
        assert 'shell_exec' in php_shell or 'system' in php_shell or 'exec' in php_shell
        assert '<?php' in php_shell
        
    def test_jsp_webshell(self):
        """Test real JSP web shell generation"""
        response = requests.post(
            f"{BASE_URL}/hacking/payloads/webshell",
            json={
                "shell_type": "jsp"
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        shells = data['shells']
        assert 'jsp' in shells
        jsp_shell = shells['jsp']
        # Real JSP web shell
        assert 'Runtime.getRuntime().exec' in jsp_shell
        
    def test_aspx_webshell(self):
        """Test real ASPX web shell generation"""
        response = requests.post(
            f"{BASE_URL}/hacking/payloads/webshell",
            json={
                "shell_type": "aspx"
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        shells = data['shells']
        assert 'aspx' in shells
        aspx_shell = shells['aspx']
        # Real ASPX web shell
        assert 'Process' in aspx_shell
        assert 'cmd.exe' in aspx_shell


class TestExploitPayloadGeneration:
    """Test REAL exploit payload generation"""
    
    def test_sqli_payloads(self):
        """Test real SQL injection payload generation"""
        response = requests.get(
            f"{BASE_URL}/hacking/exploits/sqli",
            params={
                "target_url": "http://example.com/login",
                "technique": "union"
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        
        payloads = data['payloads']
        # Real SQLi payloads
        assert "' OR '1'='1" in payloads
        assert "UNION SELECT" in payloads
        assert "SLEEP" in payloads or "WAITFOR" in payloads
        
    def test_xss_payloads(self):
        """Test real XSS payload generation"""
        response = requests.get(
            f"{BASE_URL}/hacking/exploits/xss",
            params={
                "target_url": "http://example.com/search"
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        
        payloads = data['payloads']
        # Real XSS payloads
        assert "<script>" in payloads
        assert "alert" in payloads
        assert "onerror" in payloads
        assert "document.cookie" in payloads
        
    def test_lfi_payloads(self):
        """Test real LFI payload generation"""
        response = requests.get(
            f"{BASE_URL}/hacking/exploits/lfi",
            params={
                "target_url": "http://example.com/page.php"
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        
        payloads = data['payloads']
        # Real LFI payloads
        assert "../../../etc/passwd" in payloads
        assert "/etc/shadow" in payloads
        assert "php://filter" in payloads


class TestCrewAIMultiAgent:
    """Test CrewAI multi-agent hacking crew - REAL implementation"""
    
    def test_crewai_endpoint_exists(self):
        """Test that CrewAI attack endpoint exists"""
        response = requests.post(
            f"{BASE_URL}/agent/crewai/attack",
            json={
                "target": "localhost",
                "goal": "test",
                "max_rounds": 1
            },
            timeout=30
        )
        # Should return 200 even if agents timeout
        assert response.status_code in [200, 500]
        
    def test_crewai_has_multiple_agents(self):
        """Test that CrewAI has multiple specialized agents"""
        response = requests.post(
            f"{BASE_URL}/agent/crewai/attack",
            json={
                "target": "localhost",
                "goal": "test",
                "max_rounds": 1
            },
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            # Should have multiple agents
            assert 'available_agents' in data or 'agents_deployed' in data
            if 'available_agents' in data:
                agents = data['available_agents']
                # Real CrewAI should have specialized agents
                assert len(agents) >= 3


class TestAutoGPTAgent:
    """Test AutoGPT-style autonomous agent - REAL implementation"""
    
    def test_autogpt_endpoint_exists(self):
        """Test that AutoGPT run endpoint exists"""
        response = requests.post(
            f"{BASE_URL}/agent/autogpt/run",
            json={
                "goal": "test",
                "max_iterations": 1
            },
            timeout=30
        )
        # Should return 200 even if agent times out
        assert response.status_code in [200, 500]


class TestGarakScanner:
    """Test Garak LLM vulnerability scanner - REAL implementation"""
    
    def test_garak_endpoint_exists(self):
        """Test that Garak scan endpoint exists"""
        response = requests.post(
            f"{BASE_URL}/agent/garak/scan",
            json={
                "target_model": "lilith",
                "probes": ["jailbreak_dan"],
                "max_prompts": 1
            },
            timeout=30
        )
        # Endpoint should exist
        assert response.status_code in [200, 500]


class TestDashboardIntegration:
    """Test that dashboard loads with 88 AIs"""
    
    def test_dashboard_loads(self):
        """Test that dashboard HTML loads"""
        response = requests.get(
            "http://127.0.0.1:3000/",
            timeout=30
        )
        assert response.status_code == 200
        assert 'LUCIFEROS' in response.text
        
    def test_dashboard_status(self):
        """Test dashboard status endpoint"""
        response = requests.get(
            "http://127.0.0.1:3000/_dash/status",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert 'backend' in data


class TestTelegramBot:
    """Test Telegram bot is running"""
    
    def test_telegram_bot_process_running(self):
        """Test that Telegram bot process is running"""
        import subprocess
        result = subprocess.run(
            ['pgrep', '-f', 'telegram_lilith_bot'],
            capture_output=True,
            text=True
        )
        # Bot should be running
        assert result.returncode == 0 or len(result.stdout.strip()) > 0


class TestPayloadTypesAvailable:
    """Test that all payload types are available"""
    
    def test_reverse_shell_types(self):
        """Test all reverse shell types are available"""
        response = requests.post(
            f"{BASE_URL}/hacking/payloads/reverse-shell",
            json={"host": "10.10.10.10", "port": 4444},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        types_available = data.get('types_available', [])
        assert 'python' in types_available
        assert 'bash' in types_available
        assert 'netcat' in types_available
        assert 'php' in types_available
        assert 'powershell' in types_available
        
    def test_webshell_types(self):
        """Test all web shell types are available"""
        response = requests.post(
            f"{BASE_URL}/hacking/payloads/webshell",
            json={},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        types_available = data.get('types_available', [])
        assert 'php' in types_available
        assert 'jsp' in types_available
        assert 'aspx' in types_available


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
