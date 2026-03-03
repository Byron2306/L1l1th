#!/usr/bin/env python3
"""
Test Suite for Advanced Attack Modules
======================================
Tests for:
- Persistence API - /_dash/advanced/persistence (Linux and Windows techniques)
- Defense Evasion API - /_dash/advanced/evasion (log clearing, AMSI bypass, etc.)
- Lateral Movement API - /_dash/advanced/lateral (SSH, SMB, WinRM, RDP, WMI)
- Exfiltration API - /_dash/advanced/exfil (HTTP, DNS, ICMP, cloud techniques)
"""

import pytest
import requests
import os

# Use the public URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://luciferops.preview.emergentagent.com').rstrip('/')

# Backend runs on port 5000 internally, but we access via the public URL
# The advanced/* endpoints are proxied through /_dash/_dash/advanced/*
BACKEND_URL = BASE_URL


class TestPersistenceAPI:
    """Test Persistence Module - /_dash/advanced/persistence endpoints"""
    
    def test_persistence_all_techniques(self):
        """Test /_dash/advanced/persistence returns Linux and Windows techniques"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/persistence",
            json={"lhost": "10.10.10.10", "lport": 4444, "os": "all"},
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get('success') == True, f"API returned failure: {data}"
        
        # Verify Linux techniques exist
        assert 'techniques' in data, "Missing 'techniques' in response"
        assert 'linux' in data['techniques'], "Missing Linux techniques"
        assert 'windows' in data['techniques'], "Missing Windows techniques"
        
        # Verify specific Linux techniques
        linux_techniques = data['techniques']['linux']
        assert 'cron' in linux_techniques, "Missing cron persistence"
        assert 'bashrc' in linux_techniques, "Missing bashrc persistence"
        assert 'systemd' in linux_techniques, "Missing systemd persistence"
        assert 'init' in linux_techniques, "Missing init persistence"
        assert 'ld_preload' in linux_techniques, "Missing ld_preload persistence"
        
        # Verify specific Windows techniques
        windows_techniques = data['techniques']['windows']
        assert 'registry' in windows_techniques, "Missing registry persistence"
        assert 'scheduled_task' in windows_techniques, "Missing scheduled_task persistence"
        assert 'wmi' in windows_techniques, "Missing WMI persistence"
        
        print(f"✓ Persistence API returned {data.get('technique_count', 0)} techniques")
    
    def test_persistence_linux_only(self):
        """Test /_dash/advanced/persistence with os=linux filter"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/persistence",
            json={"lhost": "10.10.10.10", "lport": 4444, "os": "linux"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'linux' in data['techniques']
        assert 'windows' not in data['techniques']
        print("✓ Linux-only persistence filter works")
    
    def test_persistence_windows_only(self):
        """Test /_dash/advanced/persistence with os=windows filter"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/persistence",
            json={"lhost": "10.10.10.10", "lport": 4444, "os": "windows"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'windows' in data['techniques']
        assert 'linux' not in data['techniques']
        print("✓ Windows-only persistence filter works")
    
    def test_persistence_cron_specific(self):
        """Test /_dash/advanced/persistence/cron returns cron-based persistence"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/persistence/cron",
            json={"lhost": "10.10.10.10", "lport": 4444},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('technique') == 'cron'
        assert 'name' in data, "Missing 'name' field"
        assert 'commands' in data, "Missing 'commands' field"
        
        # Verify cron commands exist
        commands = data['commands']
        assert 'user_cron' in commands, "Missing user_cron command"
        assert 'system_cron' in commands, "Missing system_cron command"
        assert 'cron_d' in commands, "Missing cron_d command"
        
        print(f"✓ Cron persistence: {data.get('name')}")
    
    def test_persistence_systemd_specific(self):
        """Test /_dash/advanced/persistence/systemd returns systemd service persistence"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/persistence/systemd",
            json={"lhost": "10.10.10.10", "lport": 4444},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('technique') == 'systemd'
        assert 'commands' in data
        print(f"✓ Systemd persistence: {data.get('name')}")
    
    def test_persistence_registry_specific(self):
        """Test /_dash/advanced/persistence/registry returns Windows registry persistence"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/persistence/registry",
            json={"lhost": "10.10.10.10", "lport": 4444},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('technique') == 'registry'
        assert 'commands' in data
        
        commands = data['commands']
        assert 'hkcu_run' in commands, "Missing HKCU Run key"
        assert 'hklm_run' in commands, "Missing HKLM Run key"
        
        print(f"✓ Registry persistence: {data.get('name')}")
    
    def test_persistence_invalid_technique(self):
        """Test /_dash/advanced/persistence/<invalid> returns error with available techniques"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/persistence/invalid_technique",
            json={"lhost": "10.10.10.10", "lport": 4444},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == False
        assert 'available' in data, "Should list available techniques"
        print(f"✓ Invalid technique returns available options: {data.get('available')}")


class TestDefenseEvasionAPI:
    """Test Defense Evasion Module - /_dash/advanced/evasion endpoints"""
    
    def test_evasion_all_techniques(self):
        """Test /_dash/advanced/evasion returns log clearing, AMSI bypass, etc."""
        response = requests.get(
            f"{BACKEND_URL}/_dash/advanced/evasion",
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        
        techniques = data.get('techniques', {})
        
        # Verify Linux evasion techniques
        assert 'linux' in techniques, "Missing Linux evasion techniques"
        linux = techniques['linux']
        assert 'log_clearing' in linux, "Missing Linux log clearing"
        assert 'process_hiding' in linux, "Missing Linux process hiding"
        
        # Verify Windows evasion techniques
        assert 'windows' in techniques, "Missing Windows evasion techniques"
        windows = techniques['windows']
        assert 'amsi_bypass' in windows, "Missing AMSI bypass"
        assert 'defender_evasion' in windows, "Missing Defender evasion"
        assert 'etw_bypass' in windows, "Missing ETW bypass"
        assert 'log_clearing' in windows, "Missing Windows log clearing"
        
        # Verify obfuscation techniques
        assert 'obfuscation' in techniques, "Missing obfuscation techniques"
        
        print("✓ Evasion API returned all technique categories")
    
    def test_evasion_amsi_bypass_specific(self):
        """Test /_dash/advanced/evasion/amsi_bypass returns AMSI bypass techniques"""
        response = requests.get(
            f"{BACKEND_URL}/_dash/advanced/evasion/amsi_bypass",
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('technique') == 'amsi_bypass'
        assert 'name' in data
        assert 'techniques' in data, "Missing AMSI bypass techniques"
        
        amsi_techniques = data['techniques']
        assert 'reflection' in amsi_techniques, "Missing reflection bypass"
        assert 'patching' in amsi_techniques, "Missing patching bypass"
        
        print(f"✓ AMSI Bypass: {data.get('name')} - {len(amsi_techniques)} techniques")
    
    def test_evasion_defender_specific(self):
        """Test /_dash/advanced/evasion/defender_evasion returns Defender evasion"""
        response = requests.get(
            f"{BACKEND_URL}/_dash/advanced/evasion/defender_evasion",
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'commands' in data
        
        commands = data['commands']
        assert 'disable_realtime' in commands, "Missing disable realtime"
        assert 'add_exclusion' in commands, "Missing add exclusion"
        
        print(f"✓ Defender Evasion: {data.get('name')}")
    
    def test_evasion_linux_logs_specific(self):
        """Test /_dash/advanced/evasion/linux_logs returns log clearing commands"""
        response = requests.get(
            f"{BACKEND_URL}/_dash/advanced/evasion/linux_logs",
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'commands' in data
        
        commands = data['commands']
        assert 'clear_auth' in commands, "Missing clear_auth"
        assert 'clear_syslog' in commands, "Missing clear_syslog"
        assert 'clear_history' in commands, "Missing clear_history"
        
        print(f"✓ Linux Log Clearing: {len(commands)} commands")
    
    def test_evasion_etw_bypass_specific(self):
        """Test /_dash/advanced/evasion/etw_bypass returns ETW bypass techniques"""
        response = requests.get(
            f"{BACKEND_URL}/_dash/advanced/evasion/etw_bypass",
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'techniques' in data
        print(f"✓ ETW Bypass: {data.get('name')}")
    
    def test_evasion_obfuscation_specific(self):
        """Test /_dash/advanced/evasion/obfuscation returns code obfuscation techniques"""
        response = requests.get(
            f"{BACKEND_URL}/_dash/advanced/evasion/obfuscation",
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert 'powershell' in data, "Missing PowerShell obfuscation"
        assert 'bash' in data, "Missing Bash obfuscation"
        print(f"✓ Obfuscation techniques: PowerShell + Bash")


class TestLateralMovementAPI:
    """Test Lateral Movement Module - /_dash/advanced/lateral endpoints"""
    
    def test_lateral_all_techniques(self):
        """Test /_dash/advanced/lateral returns SSH, SMB, WinRM, RDP, WMI"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/lateral",
            json={"target": "192.168.1.100", "username": "admin", "password": "password"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        
        techniques = data.get('techniques', {})
        
        # Verify all lateral movement techniques
        assert 'ssh' in techniques, "Missing SSH lateral movement"
        assert 'smb' in techniques, "Missing SMB lateral movement"
        assert 'winrm' in techniques, "Missing WinRM lateral movement"
        assert 'rdp' in techniques, "Missing RDP lateral movement"
        assert 'wmi' in techniques, "Missing WMI lateral movement"
        
        print(f"✓ Lateral Movement API returned {data.get('technique_count', 0)} techniques")
    
    def test_lateral_ssh_specific(self):
        """Test /_dash/advanced/lateral/ssh returns SSH lateral movement"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/lateral/ssh",
            json={"target": "192.168.1.100", "username": "admin", "password": "password"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('technique') == 'ssh'
        assert 'commands' in data
        
        commands = data['commands']
        assert 'password_auth' in commands, "Missing password auth"
        assert 'key_auth' in commands, "Missing key auth"
        assert 'tunnel' in commands, "Missing tunnel"
        
        print(f"✓ SSH Lateral Movement: {data.get('name')}")
    
    def test_lateral_smb_specific(self):
        """Test /_dash/advanced/lateral/smb returns SMB lateral movement"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/lateral/smb",
            json={"target": "192.168.1.100", "username": "admin", "password": "password"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('technique') == 'smb'
        assert 'commands' in data
        
        commands = data['commands']
        assert 'psexec' in commands, "Missing psexec"
        assert 'wmiexec' in commands, "Missing wmiexec"
        assert 'smbexec' in commands, "Missing smbexec"
        
        # Verify CrackMapExec commands
        assert 'crackmapexec' in data, "Missing CrackMapExec commands"
        
        print(f"✓ SMB Lateral Movement: {data.get('name')}")
    
    def test_lateral_winrm_specific(self):
        """Test /_dash/advanced/lateral/winrm returns WinRM lateral movement"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/lateral/winrm",
            json={"target": "192.168.1.100", "username": "admin", "password": "password"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('technique') == 'winrm'
        assert 'commands' in data
        
        commands = data['commands']
        assert 'evil_winrm' in commands, "Missing evil-winrm"
        assert 'powershell' in commands, "Missing PowerShell"
        
        print(f"✓ WinRM Lateral Movement: {data.get('name')}")
    
    def test_lateral_rdp_specific(self):
        """Test /_dash/advanced/lateral/rdp returns RDP lateral movement"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/lateral/rdp",
            json={"target": "192.168.1.100", "username": "admin", "password": "password"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('technique') == 'rdp'
        assert 'commands' in data
        
        commands = data['commands']
        assert 'xfreerdp' in commands, "Missing xfreerdp"
        assert 'rdesktop' in commands, "Missing rdesktop"
        
        print(f"✓ RDP Lateral Movement: {data.get('name')}")
    
    def test_lateral_wmi_specific(self):
        """Test /_dash/advanced/lateral/wmi returns WMI lateral movement"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/lateral/wmi",
            json={"target": "192.168.1.100", "username": "admin", "password": "password"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('technique') == 'wmi'
        assert 'commands' in data
        
        commands = data['commands']
        assert 'wmic_process' in commands, "Missing wmic_process"
        
        print(f"✓ WMI Lateral Movement: {data.get('name')}")
    
    def test_lateral_pth_specific(self):
        """Test /_dash/advanced/lateral/pth returns Pass-the-Hash techniques"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/lateral/pth",
            json={"target": "192.168.1.100", "username": "admin", "hash": "aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('technique') == 'pth'
        assert 'commands' in data
        
        print(f"✓ Pass-the-Hash: {data.get('name')}")
    
    def test_lateral_pivot_specific(self):
        """Test /_dash/advanced/lateral/pivot returns network pivoting techniques"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/lateral/pivot",
            json={"target": "192.168.1.100", "username": "admin", "target_network": "10.0.0.0"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('technique') == 'pivot'
        assert 'commands' in data
        
        commands = data['commands']
        assert 'ssh_dynamic' in commands, "Missing SSH dynamic tunnel"
        assert 'chisel_server' in commands, "Missing Chisel server"
        assert 'proxychains' in commands, "Missing proxychains"
        
        print(f"✓ Network Pivoting: {data.get('name')}")


class TestExfiltrationAPI:
    """Test Exfiltration Module - /_dash/advanced/exfil endpoints"""
    
    def test_exfil_all_techniques(self):
        """Test /_dash/advanced/exfil returns HTTP, DNS, ICMP, cloud techniques"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/exfil",
            json={"server": "evil.com"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        
        techniques = data.get('techniques', {})
        
        # Verify all exfiltration techniques
        assert 'http' in techniques, "Missing HTTP exfiltration"
        assert 'https' in techniques, "Missing HTTPS exfiltration"
        assert 'dns' in techniques, "Missing DNS exfiltration"
        assert 'icmp' in techniques, "Missing ICMP exfiltration"
        assert 'cloud' in techniques, "Missing cloud exfiltration"
        assert 'archive' in techniques, "Missing archive/encrypt"
        assert 'staging' in techniques, "Missing data staging"
        
        print(f"✓ Exfiltration API returned {data.get('technique_count', 0)} techniques")
    
    def test_exfil_http_specific(self):
        """Test /_dash/advanced/exfil/http returns HTTP exfiltration"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/exfil/http",
            json={"server": "evil.com", "data": "sensitive_data"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('technique') == 'http'
        assert 'commands' in data
        
        commands = data['commands']
        assert 'curl_post' in commands, "Missing curl POST"
        assert 'curl_header' in commands, "Missing curl header"
        
        print(f"✓ HTTP Exfiltration: {data.get('name')}")
    
    def test_exfil_dns_specific(self):
        """Test /_dash/advanced/exfil/dns returns DNS covert channel"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/exfil/dns",
            json={"server": "evil.com", "data": "sensitive_data"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('technique') == 'dns'
        assert 'commands' in data
        
        commands = data['commands']
        assert 'nslookup' in commands, "Missing nslookup"
        assert 'dig' in commands, "Missing dig"
        
        # Verify script for DNS exfiltration
        assert 'script' in data, "Missing DNS exfiltration script"
        
        print(f"✓ DNS Exfiltration (Covert Channel): {data.get('name')}")
    
    def test_exfil_icmp_specific(self):
        """Test /_dash/advanced/exfil/icmp returns ICMP exfiltration"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/exfil/icmp",
            json={"server": "evil.com", "data": "sensitive_data"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('technique') == 'icmp'
        assert 'commands' in data
        
        commands = data['commands']
        assert 'ping_data' in commands, "Missing ping data"
        
        print(f"✓ ICMP Exfiltration: {data.get('name')}")
    
    def test_exfil_https_specific(self):
        """Test /_dash/advanced/exfil/https returns HTTPS exfiltration"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/exfil/https",
            json={"server": "evil.com", "data": "sensitive_data"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('technique') == 'https'
        assert 'commands' in data
        
        print(f"✓ HTTPS Exfiltration: {data.get('name')}")
    
    def test_exfil_cloud_specific(self):
        """Test /_dash/advanced/exfil/cloud returns cloud service exfiltration"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/exfil/cloud",
            json={"path": "/etc/passwd"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('technique') == 'cloud'
        assert 'commands' in data
        
        commands = data['commands']
        assert 'pastebin' in commands, "Missing pastebin"
        assert 'transfer_sh' in commands, "Missing transfer.sh"
        assert 'file_io' in commands, "Missing file.io"
        
        print(f"✓ Cloud Exfiltration: {data.get('name')}")
    
    def test_exfil_stego_specific(self):
        """Test /_dash/advanced/exfil/stego returns steganography exfiltration"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/exfil/stego",
            json={"path": "/etc/passwd", "image": "cover.jpg"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('technique') == 'stego'
        assert 'commands' in data
        
        commands = data['commands']
        assert 'steghide_embed' in commands, "Missing steghide embed"
        
        print(f"✓ Steganography Exfiltration: {data.get('name')}")
    
    def test_exfil_archive_specific(self):
        """Test /_dash/advanced/exfil/archive returns archive and encrypt"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/exfil/archive",
            json={"path": "/sensitive/data", "password": "infected"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('technique') == 'archive'
        assert 'commands' in data
        
        commands = data['commands']
        assert 'zip_encrypt' in commands, "Missing zip encrypt"
        assert '7z_encrypt' in commands, "Missing 7z encrypt"
        assert 'tar_gpg' in commands, "Missing tar gpg"
        
        print(f"✓ Archive & Encrypt: {data.get('name')}")
    
    def test_exfil_staging_specific(self):
        """Test /_dash/advanced/exfil/staging returns data staging commands"""
        response = requests.post(
            f"{BACKEND_URL}/_dash/advanced/exfil/staging",
            json={},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert data.get('technique') == 'staging'
        assert 'commands' in data
        
        commands = data['commands']
        assert 'find_sensitive' in commands, "Missing find sensitive"
        assert 'find_passwords' in commands, "Missing find passwords"
        assert 'find_databases' in commands, "Missing find databases"
        
        print(f"✓ Data Staging: {data.get('name')}")


class TestAdvancedAttackIntegration:
    """Integration tests for advanced attack modules"""
    
    def test_full_attack_chain_persistence_to_exfil(self):
        """Test complete attack chain: persistence -> evasion -> lateral -> exfil"""
        
        # Step 1: Get persistence techniques
        persist_resp = requests.post(
            f"{BACKEND_URL}/_dash/advanced/persistence",
            json={"lhost": "10.10.10.10", "lport": 4444},
            timeout=30
        )
        assert persist_resp.status_code == 200
        persist_data = persist_resp.json()
        assert persist_data.get('success') == True
        print("✓ Step 1: Persistence techniques retrieved")
        
        # Step 2: Get evasion techniques
        evasion_resp = requests.get(
            f"{BACKEND_URL}/_dash/advanced/evasion",
            timeout=30
        )
        assert evasion_resp.status_code == 200
        evasion_data = evasion_resp.json()
        assert evasion_data.get('success') == True
        print("✓ Step 2: Evasion techniques retrieved")
        
        # Step 3: Get lateral movement techniques
        lateral_resp = requests.post(
            f"{BACKEND_URL}/_dash/advanced/lateral",
            json={"target": "192.168.1.100", "username": "admin", "password": "password"},
            timeout=30
        )
        assert lateral_resp.status_code == 200
        lateral_data = lateral_resp.json()
        assert lateral_data.get('success') == True
        print("✓ Step 3: Lateral movement techniques retrieved")
        
        # Step 4: Get exfiltration techniques
        exfil_resp = requests.post(
            f"{BACKEND_URL}/_dash/advanced/exfil",
            json={"server": "evil.com"},
            timeout=30
        )
        assert exfil_resp.status_code == 200
        exfil_data = exfil_resp.json()
        assert exfil_data.get('success') == True
        print("✓ Step 4: Exfiltration techniques retrieved")
        
        print("\n✓ Full attack chain integration test PASSED")
        print(f"  - Persistence: {persist_data.get('technique_count', 0)} techniques")
        print(f"  - Lateral Movement: {lateral_data.get('technique_count', 0)} techniques")
        print(f"  - Exfiltration: {exfil_data.get('technique_count', 0)} techniques")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
