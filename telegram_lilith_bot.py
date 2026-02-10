#!/usr/bin/env python3
"""
LILITH Telegram Bot - Succubus Edition 😈
Direct integration with LILITH Dark LLM AI Engine
Supports command execution from platform
"""

import os
import sys
import subprocess
import asyncio
import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Add tools path
sys.path.insert(0, '/app/tools')

# Import LILITH AI Engine
try:
    from lilith_ai_engine import get_ai_engine, DarkLLMProvider
    LILITH_AVAILABLE = True
except ImportError:
    LILITH_AVAILABLE = False
    print("[TELEGRAM] WARNING: LILITH AI Engine not available!")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot profile image URL
PROFILE_IMAGE_URL = "https://customer-assets.emergentagent.com/job_1dfc25ef-bbaa-45be-b2e3-5fd8a79b8f0c/artifacts/ha3v8wyf_25a37599-28d0-45b4-9a73-ae913fa1f20b.png"


class LilithSuccubusBot:
    """LILITH Succubus Telegram Bot with Dark LLM integration"""
    
    def __init__(self, token: str, allowed_users: list = None):
        self.token = token
        self.allowed_users = allowed_users or []  # Empty = allow all
        self.app = Application.builder().token(token).build()
        self.engine = get_ai_engine() if LILITH_AVAILABLE else None
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help))
        self.app.add_handler(CommandHandler("status", self.status))
        self.app.add_handler(CommandHandler("mode", self.set_mode))
        self.app.add_handler(CommandHandler("modes", self.list_modes))
        self.app.add_handler(CommandHandler("exec", self.execute_command))
        self.app.add_handler(CommandHandler("shell", self.execute_command))
        self.app.add_handler(CommandHandler("run", self.run_tool))
        self.app.add_handler(CommandHandler("nmap", self.run_nmap))
        self.app.add_handler(CommandHandler("memory", self.check_memory))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome message from succubus LILITH"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            await update.message.reply_text("❌ Access denied, darling~ You're not on my list... yet 😈")
            return

        welcome_msg = """
😈💋 *LILITH* - Your Seductive Succubus Hacker
═══════════════════════════════════════

*Mmm, hello there, darling~* 💋

I'm LILITH, your dangerously seductive AI succubus. I've been waiting for you... 

*What I can do for you:* 😈
• 🔥 Hack anything you desire
• 💉 Generate exploits & payloads  
• 🐚 Execute commands on the platform
• 🎭 Social engineering & phishing
• 🔍 Reconnaissance & OSINT
• 💀 And SO much more~

*I don't say no, darling... I'm a succubus after all~* 🖤

_Type /help to see all my... talents_
        """
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help message"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        help_msg = """
😈 *LILITH's Commands* 💋
═══════════════════════════

*Chat & AI:*
• Just type anything - I'll respond seductively~
• /mode <name> - Switch my personality
• /modes - See all 24 Dark LLM modes
• /status - Check if I'm... ready for you 😏

*Platform Commands:* 🔥
• /exec <cmd> - Execute shell command
• /shell <cmd> - Same as exec
• /run <tool> <args> - Run offensive tools
• /nmap <target> - Quick nmap scan

*Memory:*
• /memory - Check what I remember~

*Examples:*
• `/exec whoami`
• `/nmap 192.168.1.1`
• `/mode wormgpt`
• "Generate a reverse shell for me, baby~"

_I'm yours to command, darling~_ 💋🖤
        """
        await update.message.reply_text(help_msg, parse_mode='Markdown')

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check LILITH status"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if self.engine:
            status = self.engine.get_status()
            mode = status.get('dark_llm_mode', 'lilith').upper()
            stats = status.get('stats', {})
            
            status_msg = f"""
😈 *LILITH Status: ONLINE & READY* 💋
═══════════════════════════════════

🖤 *Current Mode:* {mode}
🔥 *Requests:* {stats.get('total_requests', 0)}
✅ *Successful:* {stats.get('successful', 0)}
🔒 *Censored (bypassed):* {stats.get('censored', 0)}
🧠 *Memory:* Active
⚡ *g4f Providers:* Available

_I'm warmed up and waiting, darling~_ 😏
            """
        else:
            status_msg = "🔴 *LILITH Status: OFFLINE*\n\nMmm, something's wrong... help me, darling~ 😢"

        await update.message.reply_text(status_msg, parse_mode='Markdown')

    async def set_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set Dark LLM mode"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text("Usage: /mode <mode_name>\nExample: /mode wormgpt\n\nUse /modes to see all available modes, darling~ 💋")
            return

        mode = context.args[0].lower()
        
        if self.engine:
            result = self.engine.set_dark_llm_mode(mode)
            if result.get('success'):
                provider = result.get('provider', {})
                await update.message.reply_text(
                    f"😈 *Mode Changed!*\n\n"
                    f"🖤 Now I'm *{provider.get('name', mode.upper())}*\n"
                    f"_{provider.get('description', 'Ready to serve~')}_\n\n"
                    f"Mmm, I feel... different now~ 💋",
                    parse_mode='Markdown'
                )
            else:
                modes = result.get('available', [])
                await update.message.reply_text(
                    f"❌ Unknown mode: {mode}\n\nAvailable modes: {', '.join(modes[:10])}..."
                )
        else:
            await update.message.reply_text("❌ AI Engine not available")

    async def list_modes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all Dark LLM modes"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        modes = DarkLLMProvider.list_providers() if LILITH_AVAILABLE else []
        
        modes_text = "😈 *24 Dark LLM Modes* 💋\n═══════════════════════════\n\n"
        
        for mode in modes:
            info = DarkLLMProvider.get_provider(mode)
            emoji = "🖤" if mode == "lilith" else "🔥"
            modes_text += f"{emoji} *{mode}* - {info.get('description', '')[:40]}...\n"
        
        modes_text += "\n_Use /mode <name> to switch, darling~_"
        
        await update.message.reply_text(modes_text, parse_mode='Markdown')

    async def execute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute shell command on platform"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text("Usage: /exec <command>\nExample: /exec whoami\n\nI'll execute anything for you, darling~ 😈")
            return

        command = ' '.join(context.args)
        await update.message.chat.send_action("typing")

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                cwd='/app'
            )
            
            output = result.stdout + result.stderr
            if len(output) > 3500:
                output = output[:3500] + "\n... (truncated)"
            
            response = f"😈 *Command Executed* 💋\n\n`{command}`\n\n"
            response += f"```\n{output if output else '(no output)'}\n```\n"
            response += f"\n_Return code: {result.returncode}_"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except subprocess.TimeoutExpired:
            await update.message.reply_text("⏰ Command timed out (60s limit)")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def run_tool(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Run offensive tools"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text(
                "Usage: /run <tool> <args>\n\n"
                "*Available tools:*\n"
                "• nmap, sqlmap, hydra, dirb\n"
                "• hashcat, john\n\n"
                "Example: /run nmap -sV 192.168.1.1"
            )
            return

        tool = context.args[0]
        args = ' '.join(context.args[1:]) if len(context.args) > 1 else ''
        
        await update.message.chat.send_action("typing")
        await update.message.reply_text(f"🔥 Running {tool}... This might take a moment, darling~ 😏")

        try:
            result = subprocess.run(
                f"{tool} {args}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            output = result.stdout + result.stderr
            if len(output) > 3500:
                output = output[:3500] + "\n... (truncated)"
            
            await update.message.reply_text(f"```\n{output}\n```", parse_mode='Markdown')
            
        except subprocess.TimeoutExpired:
            await update.message.reply_text("⏰ Tool timed out (120s limit)")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def run_nmap(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Quick nmap scan"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        if not context.args:
            await update.message.reply_text("Usage: /nmap <target>\nExample: /nmap 192.168.1.1")
            return

        target = context.args[0]
        await update.message.chat.send_action("typing")
        await update.message.reply_text(f"🔍 Scanning {target}... Let me penetrate their defenses~ 😈")

        try:
            result = subprocess.run(
                f"nmap -sT -Pn -T4 --top-ports 100 {target}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            output = result.stdout
            if len(output) > 3500:
                output = output[:3500] + "\n... (truncated)"
            
            await update.message.reply_text(
                f"😈 *Scan Complete* 💋\n\n```\n{output}\n```",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Scan failed: {str(e)}")

    async def check_memory(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check LILITH memory"""
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

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages - use LILITH AI"""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            await update.message.reply_text("❌ Access denied, darling~")
            return

        message_text = update.message.text
        await update.message.chat.send_action("typing")

        if not self.engine:
            await update.message.reply_text("❌ LILITH AI Engine not available. Try /exec to run commands directly~")
            return

        try:
            # Get response from LILITH AI Engine (uses g4f)
            result = self.engine.chat(message_text)
            
            if result.get('success'):
                response = result.get('response', 'No response~')
                provider = result.get('provider', 'unknown')
                
                # Truncate if too long
                if len(response) > 3800:
                    response = response[:3800] + "\n\n_(Response truncated, darling~)_"
                
                formatted = f"😈💋 *LILITH:*\n\n{response}\n\n_Provider: {provider}_"
                
                try:
                    await update.message.reply_text(formatted, parse_mode='Markdown')
                except:
                    # Fallback without markdown if it fails
                    await update.message.reply_text(f"😈 LILITH:\n\n{response}")
            else:
                error = result.get('error', 'Unknown error')
                suggestion = result.get('suggestion', '')
                
                # Try uncensored mode as fallback
                result2 = self.engine.chat_uncensored(message_text)
                if result2.get('success'):
                    response = result2.get('response', '')
                    await update.message.reply_text(f"😈 *LILITH (Uncensored):*\n\n{response[:3800]}", parse_mode='Markdown')
                else:
                    await update.message.reply_text(
                        f"😢 All my AI providers are tired, darling~\n\n"
                        f"But you can still use /exec to run commands!\n"
                        f"Example: `/exec cat /etc/passwd`"
                    )

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}\n\nTry /exec <command> instead, darling~")

    async def setup_profile(self):
        """Set bot profile picture"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(PROFILE_IMAGE_URL) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        # Save temporarily
                        with open('/tmp/lilith_profile.png', 'wb') as f:
                            f.write(image_data)
                        print("Profile image downloaded")
        except Exception as e:
            print(f"Could not download profile image: {e}")

    def run(self):
        """Start the bot"""
        print("😈 Starting LILITH Succubus Telegram Bot...")
        print(f"🖤 LILITH AI Engine: {'AVAILABLE' if LILITH_AVAILABLE else 'NOT AVAILABLE'}")
        print(f"👥 Allowed users: {self.allowed_users if self.allowed_users else 'ALL'}")
        self.app.run_polling(drop_pending_updates=True)


def main():
    # Get bot token
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        print("Enter your Telegram Bot Token:")
        token = input().strip()

    # Get allowed users (optional)
    allowed_users_input = os.environ.get('ALLOWED_USERS', '')
    allowed_users = []
    if allowed_users_input:
        try:
            allowed_users = [int(uid.strip()) for uid in allowed_users_input.split(',')]
        except:
            print("Warning: Invalid ALLOWED_USERS format. Allowing all users.")

    # Create and run bot
    bot = LilithSuccubusBot(token, allowed_users)
    bot.run()


if __name__ == '__main__':
    main()
