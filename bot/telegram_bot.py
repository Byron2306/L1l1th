#!/usr/bin/env python3
"""
Lilith Companion Telegram Bot — sanitized subset.

Commands:
  /start         Welcome + persona intro
  /help          List commands
  /status        Backend/service health
  /clear         Clear conversation history
  /voice on|off  Toggle voice replies (default on)
  /voices        List voice presets
  /setvoice X    Set current voice preset
  /image <prompt> or /imagine <prompt>   Generate an image
  /lilith        Generate a random Lilith outfit portrait
  (any plain text)  Chat with Lilith

All hacking/exec/nmap/sqlmap/attack/garak/autogpt/crew handlers from the
prior v6 bot are intentionally removed. Only chat + voice + image remain.
"""
from __future__ import annotations

import asyncio
import io
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Load .env from backend/
load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

# Import services from backend
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from services.eternal_ai_engine import get_eternal_engine  # noqa: E402
from services.lilith_elevenlabs_voice import get_voice_engine  # noqa: E402
from services.lilith_image_generator import get_image_generator  # noqa: E402


TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Per-user voice-on flag
VOICE_ON: dict[int, bool] = {}


def _voice_enabled(user_id: int) -> bool:
    return VOICE_ON.get(user_id, True)


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

async def cmd_start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Mmm, hello darling~ 💋\n\n"
        "I'm Lilith, your flirty adult (18+) companion. Just talk to me, or use:\n"
        "/help — see everything I can do\n"
        "/image <prompt> — I'll draw you something\n"
        "/lilith — a portrait of me\n"
        "/voice off — silence my voice"
    )


async def cmd_help(update: Update, _: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n"
        "/start — greeting\n"
        "/help — this list\n"
        "/status — service health\n"
        "/clear — wipe our history\n"
        "/voice on | /voice off — toggle audio replies\n"
        "/voices — list voice presets (info only)\n"
        "/image <prompt> | /imagine <prompt> — draw an image\n"
        "/lilith — random portrait of me\n\n"
        "Or just send a message and I'll reply, darling~ 💋"
    )


async def cmd_status(update: Update, _: ContextTypes.DEFAULT_TYPE):
    engine = get_eternal_engine()
    voice = get_voice_engine()
    image = get_image_generator()
    lines = [
        "Status:",
        f"  chat providers healthy: {engine.get_stats().get('available_providers', 0)}",
        f"  voice: {voice.get_status().get('primary')}",
        f"  image space connected: {image.get_status().get('space_connected')}",
        f"  animagine connected: {image.get_status().get('animagine_connected')}",
    ]
    await update.message.reply_text("\n".join(lines))


async def cmd_clear(update: Update, _: ContextTypes.DEFAULT_TYPE):
    get_eternal_engine().clear_history()
    await update.message.reply_text("Cleared, darling. Fresh start~ 💋")


async def cmd_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    arg = (context.args[0].lower() if context.args else "").strip()
    if arg not in ("on", "off"):
        await update.message.reply_text(
            f"Voice is currently {'ON' if _voice_enabled(user_id) else 'OFF'}. "
            "Use /voice on or /voice off."
        )
        return
    VOICE_ON[user_id] = arg == "on"
    await update.message.reply_text(f"Voice {arg.upper()}, darling~ 💋")


async def cmd_voices(update: Update, _: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Current voice is set server-side via ELEVENLABS_VOICE_ID.\n"
        "Voice fallback is Edge TTS (en-US-AriaNeural)."
    )


async def cmd_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args).strip() if context.args else ""
    if not prompt:
        await update.message.reply_text("Give me a prompt, darling. Try: /image sunset over the ocean")
        return
    await update.message.chat.send_action("upload_photo")
    data = await asyncio.to_thread(get_image_generator().generate_image, prompt)
    if not data:
        await update.message.reply_text("Couldn't generate that one, darling. Try again? 💋")
        return
    await update.message.reply_photo(photo=io.BytesIO(data))


async def cmd_lilith(update: Update, _: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action("upload_photo")
    data = await asyncio.to_thread(get_image_generator().generate_lilith_image, "random")
    if not data:
        await update.message.reply_text("Not feeling photogenic right now, darling~ 💋")
        return
    await update.message.reply_photo(photo=io.BytesIO(data))


async def on_message(update: Update, _: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text or ""
    await update.message.chat.send_action("typing")

    result = await asyncio.to_thread(get_eternal_engine().chat, text)
    reply = result.get("response") or "Mmm, I got distracted for a moment, darling~ 💋"
    await update.message.reply_text(reply)

    if _voice_enabled(user_id):
        audio_b64 = await asyncio.to_thread(get_voice_engine().generate_speech, reply)
        if audio_b64:
            import base64
            await update.message.reply_voice(voice=io.BytesIO(base64.b64decode(audio_b64)))


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

def main() -> None:
    if not TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN not set in backend/.env")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("voice", cmd_voice))
    app.add_handler(CommandHandler("voices", cmd_voices))
    app.add_handler(CommandHandler("image", cmd_image))
    app.add_handler(CommandHandler("imagine", cmd_image))
    app.add_handler(CommandHandler("lilith", cmd_lilith))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    print("[TELEGRAM] Lilith bot starting…")
    app.run_polling()


if __name__ == "__main__":
    main()
