#!/usr/bin/env python3
"""
LILITH ULTIMATE TELEGRAM BOT v6 - 100% FREE EDITION 😈
======================================================
NO API KEYS NEEDED for voice or image!

Uses:
- edge-tts: FREE Microsoft TTS (sexy female voices)
- faster-whisper: FREE local STT 
- Pollinations.ai: FREE unlimited image generation
- g4f: FREE AI chat (50+ Dark AIs)
"""

import os
import sys
import subprocess
import asyncio
import logging
import tempfile
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
    from lilith_free_engines import get_free_voice_engine, get_free_image_engine
    FREE_ENGINES_AVAILABLE = True
except ImportError as e:
    print(f"[TELEGRAM] Free engines import error: {e}")
    FREE_ENGINES_AVAILABLE = False

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class LilithFreeBotV6:
    """LILITH Bot with 100% FREE voice and image generation!"""
    
    def __init__(self, token: str, allowed_users: list = None):
        self.token = token
        self.allowed_users = allowed_users or []
        self.app = Application.builder().token(token).build()
        self.engine = get_ai_engine() if LILITH_AVAILABLE else None
        self.voice_engine = get_free_voice_engine() if FREE_ENGINES_AVAILABLE else None
        self.image_engine = get_free_image_engine() if FREE_ENGINES_AVAILABLE else None
        self.voice_mode = {}  # Per-user voice toggle
        self.voice_style = {}  # Per-user voice style
        
        # Commands
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
        self.app.add_handler(CommandHandler("styles", self.list_styles))
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
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            await update.message.reply_text("❌ Access denied~")
            return

        welcome = """
😈💋 *LILITH FREE EDITION* - 100% FREE AI Succubus
═══════════════════════════════════════════════════

*Hey there, darling~* 💋

I'm LILITH, and I'm *completely FREE* now!
No API keys needed for my voice or images~

*My FREE capabilities:* 😈
🔥 *50+ Dark AIs* - All uncensored modes
🎤 *Voice* - Sexy female voice (edge-tts FREE!)
🖼️ *Images* - Unlimited generation (Pollinations FREE!)
👂 *Listen* - Send voice, I'll transcribe (Whisper FREE!)
⚔️ *Hacking* - All tools work

*Everything is FREE, darling~* 🖤

Type /help to see my talents~
        """
        await update.message.reply_text(welcome, parse_mode='Markdown')

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        help_text = """
😈 *LILITH FREE Commands* 💋
═══════════════════════════════

*AI Chat (50+ Dark AIs):*
• Just type - I respond
• /mode <name> - Switch AI
• /modes - See all 50+ AIs
• /clear - Clear history

*FREE Voice:* 🎤
• /voice - Toggle voice ON/OFF
• /voices - List sexy voices
• /setvoice <name> - Change my voice
• Send voice msg - I transcribe & reply

*Available Voices:*
`sexy_us` `sultry_us` `seductive_uk`
`flirty_au` `mysterious_in` `dominant`
`whisper` `bold`

*FREE Images:* 🖼️
• /image <prompt> - Generate art
• /styles - List image styles

*Available Styles:*
`dark` `succubus` `cyber` `anime`
`realistic` `horror` `nsfw` `normal`

*Hacking Tools:* ⚔️
• /exec <cmd> - Run command
• /nmap <target> - Port scan
• /sqlmap <url> - SQLi test
• /attack <target> - Auto attack plan

_All FREE, no API keys~_ 💋🖤
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
        """Handle text messages"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            await update.message.reply_text("❌ Access denied~")
            return

        message_text = update.message.text
        await update.message.chat.send_action("typing")

        if not self.engine:
            await update.message.reply_text("❌ AI not available. Try /exec")
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

    async def autonomous_attack(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text("Usage: /attack <target>")
            return

        target = context.args[0]
        self.engine.set_dark_llm_mode('hackbuddy')
        
        await update.message.reply_text(f"🤖 *Auto-Attack Mode*\nTarget: `{target}`", parse_mode='Markdown')
        
        prompt = f"""Target: {target}
Generate autonomous penetration test plan:
1. Recon commands
2. Port scanning  
3. Vulnerability checks
4. Exploitation steps
5. Post-exploitation
Provide exact commands."""

        result = self.engine.chat(prompt)
        if result.get('success'):
            plan = result.get('response', '')
            if len(plan) > 3800:
                chunks = [plan[i:i+3800] for i in range(0, len(plan), 3800)]
                for chunk in chunks:
                    await update.message.reply_text(chunk)
                    await asyncio.sleep(0.5)
            else:
                await update.message.reply_text(f"📋 *Attack Plan:*\n\n{plan}", parse_mode='Markdown')

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

    def run(self):
        print("😈 Starting LILITH FREE EDITION v6...")
        print(f"🖤 AI Engine: {'✅' if LILITH_AVAILABLE else '❌'}")
        print(f"🎤 Voice (edge-tts): {'✅ FREE' if self.voice_engine else '❌'}")
        print(f"🖼️ Images (Pollinations): {'✅ FREE' if self.image_engine else '❌'}")
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

    bot = LilithFreeBotV6(token, allowed_users)
    bot.run()


if __name__ == '__main__':
    main()
