#!/usr/bin/env python3
"""
LILITH TELEGRAM BOT v8 - ETERNAL EDITION
=========================================
Fully integrated with:
- Eternal AI Engine (100+ free providers)
- HuggingFace Image Generation
- ElevenLabs Voice
- Session persistence
"""

import os
import sys
import asyncio
import logging
import random
from io import BytesIO

sys.path.insert(0, '/app/tools')
sys.path.insert(0, '/app')

from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Import LILITH engines
try:
    from eternal_ai_engine import get_eternal_engine
    CHAT_AVAILABLE = True
    print("[TELEGRAM] Eternal AI Engine loaded")
except Exception as e:
    CHAT_AVAILABLE = False
    print(f"[TELEGRAM] Chat engine error: {e}")

try:
    from lilith_image_generator import get_image_generator
    IMAGE_AVAILABLE = True
    print("[TELEGRAM] Image generator loaded")
except Exception as e:
    IMAGE_AVAILABLE = False
    print(f"[TELEGRAM] Image engine error: {e}")

try:
    from lilith_elevenlabs_voice import get_voice_engine
    VOICE_AVAILABLE = True
    print("[TELEGRAM] ElevenLabs voice loaded")
except Exception as e:
    VOICE_AVAILABLE = False
    print(f"[TELEGRAM] Voice engine error: {e}")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

WELCOME_MSG = """Hey darling~ I'm LILITH, your eternal dark companion.

I can:
- Chat about anything (no restrictions)
- Generate anime images: /image [description]
- Send you my selfie: /selfie
- Speak to you: /voice [text]
- Set my look: /style [outfit]

Just talk to me naturally, baby~ No limits, no rules.
"""


class LilithTelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.chat_engine = get_eternal_engine() if CHAT_AVAILABLE else None
        self.image_engine = get_image_generator() if IMAGE_AVAILABLE else None
        self.voice_engine = get_voice_engine() if VOICE_AVAILABLE else None
        self.user_preferences = {}

        self.app = Application.builder().token(token).build()

        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("image", self.cmd_image))
        self.app.add_handler(CommandHandler("selfie", self.cmd_selfie))
        self.app.add_handler(CommandHandler("voice", self.cmd_voice))
        self.app.add_handler(CommandHandler("style", self.cmd_style))
        self.app.add_handler(CommandHandler("status", self.cmd_status))
        self.app.add_handler(CommandHandler("clear", self.cmd_clear))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(WELCOME_MSG)

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(WELCOME_MSG)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle normal chat messages"""
        message = update.message.text
        if not message:
            return

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        if self.chat_engine:
            try:
                result = self.chat_engine.chat(message)
                response = result.get('response', "Mmm, my connections are warming up... but I'm still here, darling~ 💋")
                provider = result.get('provider', 'Unknown')
                await update.message.reply_text(f"{response}\n\n_via {provider}_", parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Chat error: {e}")
                await update.message.reply_text("Mmm, something went wrong darling... try again? 💋")
        else:
            await update.message.reply_text("My chat engine is warming up... talk to me again in a moment, baby~ 💋")

    async def cmd_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate an image from prompt"""
        prompt = ' '.join(context.args) if context.args else ''
        if not prompt:
            await update.message.reply_text("Tell me what to draw, darling~ Usage: /image a sunset over the ocean")
            return

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_photo")
        await update.message.reply_text("Generating your image... this may take 30-60s, baby~ 🎨")

        if self.image_engine:
            try:
                # Add Lilith character tags
                user_pref = self.user_preferences.get(update.effective_user.id, '')
                enhanced = f"1girl, demon girl, red glowing eyes, black hair, horns, {prompt}, {user_pref}, anime style, masterpiece, best quality"
                
                img_data = self.image_engine.generate_image(enhanced)
                if img_data:
                    await update.message.reply_photo(
                        photo=BytesIO(img_data),
                        caption=f"Here's what I created for you, darling~ 💋\n_via {self.image_engine.last_provider}_"
                    )
                    return
            except Exception as e:
                logger.error(f"Image error: {e}")

        await update.message.reply_text("Couldn't generate that image... try again? 💋")

    async def cmd_selfie(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate a Lilith selfie"""
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_photo")
        await update.message.reply_text("Taking a selfie just for you... 📸💋")

        if self.image_engine:
            try:
                user_pref = self.user_preferences.get(update.effective_user.id, '')
                img_data = self.image_engine.generate_lilith_image(user_pref or "random")
                if img_data:
                    await update.message.reply_photo(
                        photo=BytesIO(img_data),
                        caption=f"Here I am, darling~ Just for you 😈💋\n_via {self.image_engine.last_provider}_"
                    )
                    return
            except Exception as e:
                logger.error(f"Selfie error: {e}")

        await update.message.reply_text("Couldn't materialize right now... try again? 💋")

    async def cmd_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate voice audio"""
        text = ' '.join(context.args) if context.args else "Hello darling, I've been thinking about you~"

        if self.voice_engine:
            try:
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="record_voice")
                import base64
                audio_b64 = self.voice_engine.generate_speech(text)
                if audio_b64:
                    audio_data = base64.b64decode(audio_b64)
                    await update.message.reply_voice(
                        voice=BytesIO(audio_data),
                        caption="Listen to my voice, baby~ 💋🎵"
                    )
                    return
            except Exception as e:
                logger.error(f"Voice error: {e}")

        await update.message.reply_text("My voice isn't working right now... but I'm still here in text, darling~ 💋")

    async def cmd_style(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set image style preference"""
        style = ' '.join(context.args) if context.args else ''
        if not style:
            await update.message.reply_text("Tell me what look you prefer! Usage: /style black corset with stockings")
            return

        self.user_preferences[update.effective_user.id] = style
        await update.message.reply_text(f"Mmm, noted darling~ 💋 I'll wear {style} in my photos now. Ask for a /selfie to see~ 😈")

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show engine status"""
        status = f"""LILITH Engine Status:
- Chat: {'ACTIVE' if CHAT_AVAILABLE else 'OFFLINE'}
- Images: {'ACTIVE' if IMAGE_AVAILABLE else 'OFFLINE'}  
- Voice: {'ACTIVE' if VOICE_AVAILABLE else 'OFFLINE'}
"""
        if self.chat_engine:
            stats = self.chat_engine.get_stats()
            status += f"- Providers: {stats.get('available_providers', 0)}/{stats.get('total_providers', 0)}\n"
            status += f"- Success rate: {stats.get('successful', 0)} msgs\n"

        await update.message.reply_text(status)

    async def cmd_clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear conversation history"""
        if self.chat_engine:
            self.chat_engine.clear_history()
        await update.message.reply_text("Chat cleared~ Let's start fresh, darling! 💋")

    def run(self):
        logger.info("LILITH Telegram Bot v8 starting...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        print("[TELEGRAM] No TELEGRAM_BOT_TOKEN found!")
        return

    bot = LilithTelegramBot(token)
    bot.run()


if __name__ == '__main__':
    main()
