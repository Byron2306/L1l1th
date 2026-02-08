#!/bin/bash
# LILITH Telegram Setup Script

echo "🖤 LILITH Telegram Bot Setup"
echo "═══════════════════════════════"
echo

# Check if backend is running
echo "[1] Checking LILITH backend..."
if curl -s http://127.0.0.1:5000/status > /dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend not responding. Start it first:"
    echo "   cd tools && python3 lilith_full_backend.py"
    exit 1
fi

echo
echo "[2] Telegram Bot Token"
echo "Get this from @BotFather on Telegram:"
echo "  1. Open Telegram"
echo "  2. Search for @BotFather"
echo "  3. Send /newbot"
echo "  4. Choose a name (e.g., 'LILITH Bot')"
echo "  5. Choose a username (e.g., 'lilith_luciferos_bot')"
echo "  6. Copy the token"
echo

read -p "Enter your bot token: " BOT_TOKEN

echo
echo "[3] Your Telegram User ID (optional - leave empty to allow all users)"
echo "Get this from @userinfobot:"
echo "  1. Message @userinfobot on Telegram"
echo "  2. It will reply with your ID"
echo

read -p "Enter your user ID (or press Enter to allow all): " USER_ID

echo
echo "[4] Starting LILITH Telegram Bot..."
echo "Press Ctrl+C to stop"
echo

# Set environment variables
export TELEGRAM_BOT_TOKEN="$BOT_TOKEN"
if [ -n "$USER_ID" ]; then
    export ALLOWED_USERS="$USER_ID"
fi

# Run the bot
python3 telegram_lilith_bot.py