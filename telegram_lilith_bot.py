#!/usr/bin/env python3
"""
LILITH Telegram Bot
Direct integration with LILITH backend for free communication
"""

import os
import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# LILITH Backend URL
LILITH_URL = "http://localhost:5000/chat"

class LilithBot:
    def __init__(self, token: str, allowed_users: list = None):
        self.token = token
        self.allowed_users = allowed_users or []  # Empty list = allow all
        self.app = Application.builder().token(token).build()

        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help))
        self.app.add_handler(CommandHandler("status", self.status))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            await update.message.reply_text("❌ Access denied. You are not authorized to use this bot.")
            return

        welcome_msg = """
🖤 *LILITH* - LuciferOS AI Assistant
═══════════════════════════════════════

*Greetings, Master.*

I am LILITH, your autonomous red team AI. I can help with:
• Reconnaissance & intelligence gathering
• Attack planning & chain generation
• Command execution & automation
• Security analysis & vulnerability assessment
• Free-form conversation

*Send me any message to begin our conversation.*

_Type /help for available commands_
        """
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send help message."""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        help_msg = """
🖤 *LILITH Commands*
═══════════════════════

*/start* - Initialize conversation
*/help* - Show this help
*/status* - Check system status

*Direct Messages:*
Just type any message and I'll respond intelligently.

*Examples:*
• "Scan target.com for vulnerabilities"
• "Generate phishing email for CEO"
• "What's the best way to exploit this system?"
• "Tell me about red team tactics"

*Note:* All conversations are logged for security analysis.
        """
        await update.message.reply_text(help_msg, parse_mode='Markdown')

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check LILITH status."""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            return

        try:
            # Check if backend is running
            response = requests.get("http://localhost:5000/status", timeout=5)
            if response.status_code == 200:
                status_msg = "🟢 *LILITH Status: ONLINE*\n\nBackend API responding normally."
            else:
                status_msg = "🟡 *LILITH Status: DEGRADED*\n\nBackend API returned unexpected status."
        except:
            status_msg = "🔴 *LILITH Status: OFFLINE*\n\nCannot connect to backend API."

        await update.message.reply_text(status_msg, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages."""
        user = update.effective_user
        if self.allowed_users and user.id not in self.allowed_users:
            await update.message.reply_text("❌ Access denied.")
            return

        message_text = update.message.text

        # Send typing indicator
        await update.message.chat.send_action("typing")

        try:
            # Send to LILITH backend
            payload = {"message": message_text}
            response = requests.post(LILITH_URL, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                lilith_response = data.get('response', 'No response from LILITH')

                # Format response
                formatted_response = f"🖤 *LILITH:*\n\n{lilith_response}"

                # Add provider info if available
                if 'provider' in data:
                    formatted_response += f"\n\n_Provider: {data['provider']}_"

                await update.message.reply_text(formatted_response, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Error: Cannot communicate with LILITH backend.")

        except requests.exceptions.Timeout:
            await update.message.reply_text("⏰ LILITH took too long to respond. Try again.")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text("❌ An error occurred while processing your message.")

    def run(self):
        """Start the bot."""
        print("🖤 Starting LILITH Telegram Bot...")
        print(f"Allowed users: {self.allowed_users if self.allowed_users else 'ALL'}")
        self.app.run_polling()

def main():
    # Get bot token from environment or input
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        print("Enter your Telegram Bot Token (get from @BotFather):")
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
    bot = LilithBot(token, allowed_users)
    bot.run()

if __name__ == '__main__':
    main()