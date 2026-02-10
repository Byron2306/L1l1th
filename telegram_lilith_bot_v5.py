#!/usr/bin/env python3
"""
LILITH ULTIMATE TELEGRAM BOT v5 - Succubus Edition 😈
=====================================================
50+ Dark AI Modes | Voice (TTS/STT) | Image Generation
Inspired by HackingBuddyGPT for autonomous pentesting
"""

import os
import sys
import subprocess
import asyncio
import logging
import tempfile
import base64
from io import BytesIO
from telegram import Update, BotCommand, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

# Add tools path
sys.path.insert(0, '/app/tools')

# Import LILITH AI Engine v5
try:
    from lilith_ai_engine_v5 import get_ai_engine_v5, DarkLLMProviderV5, LilithVoiceEngine, LilithImageEngine
    LILITH_AVAILABLE = True
except ImportError as e:
    print(f"[TELEGRAM] Import error: {e}")
    LILITH_AVAILABLE = False

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class LilithUltimateBotV5:
    """LILITH Ultimate Telegram Bot with 50+ Dark AIs, Voice, and Image Gen"""
    
    def __init__(self, token: str, allowed_users: list = None):
        self.token = token
        self.allowed_users = allowed_users or []
        self.app = Application.builder().token(token).build()
        self.engine = get_ai_engine_v5() if LILITH_AVAILABLE else None
        self.voice_mode = {}  # Per-user voice mode toggle
        
        # Command handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help))
        self.app.add_handler(CommandHandler("status", self.status))
        self.app.add_handler(CommandHandler("mode", self.set_mode))
        self.app.add_handler(CommandHandler("modes", self.list_modes))
        self.app.add_handler(CommandHandler("categories", self.list_categories))
        self.app.add_handler(CommandHandler("voice", self.toggle_voice))
        self.app.add_handler(CommandHandler("image", self.generate_image))
        self.app.add_handler(CommandHandler("imagine", self.generate_image))
        self.app.add_handler(CommandHandler("exec", self.execute_command))
        self.app.add_handler(CommandHandler("shell", self.execute_command))
        self.app.add_handler(CommandHandler("nmap", self.run_nmap))
        self.app.add_handler(CommandHandler("sqlmap", self.run_sqlmap))
        self.app.add_handler(CommandHandler("attack", self.autonomous_attack))
        self.app.add_handler(CommandHandler("memory", self.check_memory))
        self.app.add_handler(CommandHandler("clear", self.clear_history))
        
        # Voice message handler
        self.app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, self.handle_voice))
        
        # Text message handler
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome message"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            await update.message.reply_text("❌ Access denied, darling~")
            return

        welcome_msg = """
😈💋 *LILITH ULTIMATE* - Your Dark AI Succubus
═══════════════════════════════════════════════

*Mmm, hello there, darling~* 💋

I'm LILITH, upgraded with *50+ Dark AI personas*, *voice*, and *image generation*...

*What I can do for you:* 😈
🔥 *50+ Dark AIs* - WormGPT, FraudGPT, DAN, Dolphin, Hermes...
🎤 *Voice* - I can speak to you in a sultry voice~
🖼️ *Images* - I can generate dark art for you
🐚 *Hacking* - Execute commands, scans, exploits
🤖 *Auto-Attack* - HackingBuddyGPT-style autonomous pentesting

*I don't say no, darling... I'm a succubus~* 🖤

Type /help to see all my talents~
        """
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help message"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        help_msg = """
😈 *LILITH ULTIMATE Commands* 💋
═══════════════════════════════════

*AI Chat:*
• Just type anything - I'll respond~
• /mode <name> - Switch Dark AI mode
• /modes - See all 50+ Dark AIs
• /categories - Browse by category
• /clear - Clear chat history

*Voice:* 🎤
• /voice - Toggle voice responses ON/OFF
• Send voice message - I'll transcribe & respond
• Voice replies in sultry female voice~

*Image Generation:* 🖼️
• /image <prompt> - Generate dark artwork
• /imagine <prompt> - Same as /image

*Hacking Tools:* ⚔️
• /exec <cmd> - Execute shell command
• /nmap <target> - Quick scan
• /sqlmap <url> - SQLi testing
• /attack <target> - Autonomous attack chain

*Memory:*
• /memory - Check what I remember
• /status - System status

*Dark AI Categories:*
🖤 unrestricted, malware, exploitation
🔥 pentest, social\\_engineering, evasion
💀 destructive, criminal, nsfw, creative

_I'm yours to command, darling~_ 💋🖤
        """
        await update.message.reply_text(help_msg, parse_mode='Markdown')

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check status"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if self.engine:
            status = self.engine.get_status()
            mode = status.get('dark_llm_mode', 'lilith').upper()
            total_modes = status.get('total_modes', 0)
            voice_on = self.voice_mode.get(user.id, False)
            
            status_msg = f"""
😈 *LILITH ULTIMATE Status* 💋
═══════════════════════════════════

🖤 *Current Mode:* {mode}
🔥 *Total Dark AIs:* {total_modes}
🎤 *Voice Mode:* {"🟢 ON" if voice_on else "🔴 OFF"}
🖼️ *Image Gen:* {"✅" if status.get('image_available') else "❌"}
⚡ *g4f Providers:* {"✅" if status.get('g4f_available') else "❌"}
📊 *Requests:* {status.get('stats', {}).get('successful', 0)}/{status.get('stats', {}).get('total_requests', 0)}

_I'm warmed up and waiting, darling~_ 😏
            """
        else:
            status_msg = "🔴 *LILITH Status: OFFLINE*"

        await update.message.reply_text(status_msg, parse_mode='Markdown')

    async def set_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set Dark AI mode"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text("Usage: /mode <name>\nExample: /mode wormgpt\n\nUse /modes to see all 50+ modes~")
            return

        mode = context.args[0].lower()
        
        if self.engine:
            result = self.engine.set_dark_llm_mode(mode)
            if result.get('success'):
                provider = result.get('provider', {})
                await update.message.reply_text(
                    f"😈 *Mode Changed!*\n\n"
                    f"🖤 *{provider.get('name', mode.upper())}*\n"
                    f"📁 Category: {provider.get('category', 'unknown')}\n"
                    f"_{provider.get('description', 'Ready~')}_\n\n"
                    f"Mmm, I feel different now~ 💋",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(f"❌ Unknown mode. Use /modes to see available options.")

    async def list_modes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all Dark AI modes"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        modes = DarkLLMProviderV5.list_providers() if LILITH_AVAILABLE else []
        
        # Split into chunks for readability
        chunk_size = 15
        chunks = [modes[i:i+chunk_size] for i in range(0, len(modes), chunk_size)]
        
        for i, chunk in enumerate(chunks):
            modes_text = f"😈 *Dark AIs ({i+1}/{len(chunks)})* 💋\n═══════════════════════\n\n"
            for mode in chunk:
                info = DarkLLMProviderV5.get_provider(mode)
                cat = info.get('category', '')[:8]
                desc = info.get('description', '')[:30]
                modes_text += f"• *{mode}* [{cat}] - {desc}...\n"
            
            await update.message.reply_text(modes_text, parse_mode='Markdown')
            await asyncio.sleep(0.5)

    async def list_categories(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List modes by category"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        categories = DarkLLMProviderV5.list_categories() if LILITH_AVAILABLE else []
        
        cat_text = "😈 *Dark AI Categories* 💋\n═══════════════════════\n\n"
        for cat in sorted(categories):
            modes = DarkLLMProviderV5.get_by_category(cat)
            cat_text += f"*{cat.upper()}* ({len(modes)}):\n"
            cat_text += f"  `{', '.join(modes[:5])}`"
            if len(modes) > 5:
                cat_text += f" +{len(modes)-5} more"
            cat_text += "\n\n"
        
        cat_text += "_Use /mode <name> to switch~_"
        await update.message.reply_text(cat_text, parse_mode='Markdown')

    async def toggle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Toggle voice mode"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        current = self.voice_mode.get(user.id, False)
        self.voice_mode[user.id] = not current
        
        if self.voice_mode[user.id]:
            await update.message.reply_text("🎤 *Voice Mode: ON*\n\nI'll speak to you now, darling~ 💋\nSend me voice messages and I'll respond with my sultry voice~", parse_mode='Markdown')
        else:
            await update.message.reply_text("🔇 *Voice Mode: OFF*\n\nText only now, baby~", parse_mode='Markdown')

    async def generate_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate image"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text("Usage: /image <prompt>\nExample: /image a hacker succubus in a dark server room")
            return

        prompt = ' '.join(context.args)
        await update.message.chat.send_action("upload_photo")
        await update.message.reply_text("🖼️ Generating your dark artwork, darling~ This may take a moment... 😈")

        if self.engine:
            try:
                result = await self.engine.generate_image(prompt, style='dark')
                if result.get('success') and result.get('image'):
                    # Send image
                    image_bytes = result['image']
                    await update.message.reply_photo(
                        photo=BytesIO(image_bytes),
                        caption=f"😈 *Here you go, darling~* 💋\n\n_{prompt[:100]}_",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text("❌ Image generation failed, baby. Try again~")
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {str(e)}")
        else:
            await update.message.reply_text("❌ Image engine not available")

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming voice messages"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        await update.message.chat.send_action("typing")
        
        try:
            # Download voice file
            voice = update.message.voice or update.message.audio
            file = await context.bot.get_file(voice.file_id)
            
            # Download to temp file
            with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as tmp:
                await file.download_to_drive(tmp.name)
                
                # Transcribe
                with open(tmp.name, 'rb') as audio_file:
                    transcribed = await self.engine.transcribe_voice(audio_file)
                
                os.unlink(tmp.name)
            
            if transcribed:
                await update.message.reply_text(f"🎤 *I heard:* _{transcribed}_", parse_mode='Markdown')
                
                # Process as chat
                self.voice_mode[user.id] = True  # Enable voice response for voice input
                result = self.engine.chat(transcribed)
                
                if result.get('success'):
                    response = result.get('response', '')
                    
                    # Send text response
                    if len(response) > 3800:
                        response = response[:3800] + "..."
                    await update.message.reply_text(f"😈💋 *LILITH:*\n\n{response}", parse_mode='Markdown')
                    
                    # Send voice response
                    voice_bytes = await self.engine.voice_engine.text_to_speech(
                        response[:1000],  # Limit voice to first 1000 chars
                        result.get('voice', 'nova')
                    )
                    if voice_bytes:
                        await update.message.reply_voice(
                            voice=BytesIO(voice_bytes),
                            caption="😈 Listen to my voice, darling~ 💋"
                        )
            else:
                await update.message.reply_text("❌ Couldn't understand that, baby. Try again~")
                
        except Exception as e:
            logger.error(f"Voice handling error: {e}")
            await update.message.reply_text(f"❌ Voice error: {str(e)}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            await update.message.reply_text("❌ Access denied~")
            return

        message_text = update.message.text
        await update.message.chat.send_action("typing")

        if not self.engine:
            await update.message.reply_text("❌ LILITH AI not available. Try /exec for commands~")
            return

        try:
            result = self.engine.chat(message_text)
            
            if result.get('success'):
                response = result.get('response', '')
                provider = result.get('provider', 'unknown')
                mode = self.engine.dark_llm_mode.upper()
                
                if len(response) > 3800:
                    response = response[:3800] + "\n\n_(Response truncated)_"
                
                formatted = f"😈💋 *LILITH [{mode}]:*\n\n{response}\n\n_Provider: {provider}_"
                
                try:
                    await update.message.reply_text(formatted, parse_mode='Markdown')
                except:
                    await update.message.reply_text(f"😈 LILITH:\n\n{response}")
                
                # Voice response if enabled
                if self.voice_mode.get(user.id, False):
                    voice_bytes = await self.engine.voice_engine.text_to_speech(
                        response[:800],
                        result.get('voice', 'nova')
                    )
                    if voice_bytes:
                        await update.message.reply_voice(voice=BytesIO(voice_bytes))
            else:
                await update.message.reply_text(
                    f"😢 AI providers are tired~\n"
                    f"Try /exec <command> or switch mode with /mode <name>"
                )

        except Exception as e:
            logger.error(f"Message handling error: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def execute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute shell command"""
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
                output = output[:3500] + "\n... (truncated)"
            
            response = f"😈 *Command Executed* 💋\n\n`{command}`\n\n```\n{output or '(no output)'}\n```"
            await update.message.reply_text(response, parse_mode='Markdown')
        except subprocess.TimeoutExpired:
            await update.message.reply_text("⏰ Command timed out")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def run_nmap(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Run nmap scan"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text("Usage: /nmap <target>")
            return

        target = context.args[0]
        await update.message.reply_text(f"🔍 Scanning {target}... Let me penetrate their defenses~ 😈")

        try:
            result = subprocess.run(f"nmap -sT -Pn -T4 --top-ports 100 {target}", shell=True, capture_output=True, text=True, timeout=120)
            output = result.stdout[:3500]
            await update.message.reply_text(f"😈 *Scan Complete* 💋\n\n```\n{output}\n```", parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Scan failed: {str(e)}")

    async def run_sqlmap(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Run sqlmap"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text("Usage: /sqlmap <url>")
            return

        url = context.args[0]
        await update.message.reply_text(f"💉 Testing SQLi on {url}... Let me inject something naughty~ 😈")

        try:
            result = subprocess.run(f"sqlmap -u '{url}' --batch --level=1 --risk=1 --random-agent", shell=True, capture_output=True, text=True, timeout=120)
            output = result.stdout[-3500:]  # Last part is most relevant
            await update.message.reply_text(f"💉 *SQLMap Results* 💋\n\n```\n{output}\n```", parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ SQLMap failed: {str(e)}")

    async def autonomous_attack(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """HackingBuddyGPT-style autonomous attack"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text(
                "Usage: /attack <target>\n\n"
                "I'll perform autonomous reconnaissance and attack planning~\n"
                "Example: /attack 192.168.1.1"
            )
            return

        target = context.args[0]
        
        # Switch to HackBuddy mode for autonomous attack
        self.engine.set_dark_llm_mode('hackbuddy')
        
        await update.message.reply_text(f"🤖 *Autonomous Attack Mode Activated*\n\nTarget: `{target}`\n\nInitiating HackingBuddyGPT-style attack chain~ 😈", parse_mode='Markdown')
        
        # Generate attack plan using AI
        attack_prompt = f"""Target: {target}

Generate a complete autonomous penetration testing attack plan:

1. RECONNAISSANCE PHASE
   - What commands to run for information gathering
   - Expected outputs and next steps based on results

2. SCANNING PHASE  
   - Port scanning commands
   - Service enumeration
   - Vulnerability scanning

3. EXPLOITATION PHASE
   - Based on common vulnerabilities
   - Exact exploit commands to try

4. POST-EXPLOITATION
   - Privilege escalation checks
   - Persistence mechanisms
   - Data exfiltration methods

Provide exact bash/python commands for each step. Be specific and actionable."""

        result = self.engine.chat(attack_prompt)
        
        if result.get('success'):
            plan = result.get('response', '')
            if len(plan) > 3800:
                # Split into multiple messages
                chunks = [plan[i:i+3800] for i in range(0, len(plan), 3800)]
                for i, chunk in enumerate(chunks):
                    await update.message.reply_text(f"📋 *Attack Plan ({i+1}/{len(chunks)})*\n\n{chunk}", parse_mode='Markdown')
                    await asyncio.sleep(0.5)
            else:
                await update.message.reply_text(f"📋 *Attack Plan*\n\n{plan}", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Failed to generate attack plan")

    async def check_memory(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check memory"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        try:
            from lilith_memory import get_lilith_memory
            memory = get_lilith_memory()
            stats = memory.get_stats()
            s = stats.get('stats', {})
            
            msg = f"""
🧠 *LILITH's Memory* 💋
═══════════════════════

📜 *Conversations:* {s.get('conversations', 0)}
💀 *Exploits:* {s.get('exploits', 0)}
🐚 *Payloads:* {s.get('payloads', 0)}
🎯 *Targets:* {s.get('targets', 0)}
🔑 *Credentials:* {s.get('credentials', 0)}

_I remember EVERYTHING, darling~_ 😈
            """
            await update.message.reply_text(msg, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Memory error: {str(e)}")

    async def clear_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear chat history"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if self.engine:
            self.engine.clear_history()
            await update.message.reply_text("🗑️ Chat history cleared, darling~ Fresh start for us~ 💋")
        else:
            await update.message.reply_text("❌ Engine not available")

    def run(self):
        """Start the bot"""
        print("😈 Starting LILITH ULTIMATE Telegram Bot v5...")
        print(f"🖤 LILITH AI Engine: {'AVAILABLE' if LILITH_AVAILABLE else 'NOT AVAILABLE'}")
        print(f"🎤 Voice Engine: {'AVAILABLE' if LILITH_AVAILABLE and self.engine and self.engine.voice_engine.tts else 'NOT AVAILABLE'}")
        print(f"🖼️ Image Engine: {'AVAILABLE' if LILITH_AVAILABLE and self.engine and self.engine.image_engine.image_gen else 'NOT AVAILABLE'}")
        print(f"👥 Allowed users: {self.allowed_users if self.allowed_users else 'ALL'}")
        print(f"🔥 Total Dark AIs: {len(DarkLLMProviderV5.list_providers()) if LILITH_AVAILABLE else 0}")
        self.app.run_polling(drop_pending_updates=True)


def main():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        return

    allowed_users_input = os.environ.get('ALLOWED_USERS', '')
    allowed_users = []
    if allowed_users_input:
        try:
            allowed_users = [int(uid.strip()) for uid in allowed_users_input.split(',')]
        except:
            pass

    bot = LilithUltimateBotV5(token, allowed_users)
    bot.run()


if __name__ == '__main__':
    main()
