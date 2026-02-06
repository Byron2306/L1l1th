#!/usr/bin/env python3
"""
LILITH Telegram Setup Script
Connects LILITH to Telegram via OpenClaw
"""
import subprocess
import os
import json
from pathlib import Path

OPENCLAW_DIR = Path(__file__).resolve().parents[1] / 'openclaw'
CONFIG_DIR = Path.home() / '.openclaw'

def print_banner():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║           LILITH TELEGRAM SETUP via OpenClaw                  ║
║                    LuciferOS Platform                         ║
╚═══════════════════════════════════════════════════════════════╝
""")

def get_telegram_credentials():
    print("\n[STEP 1] Telegram Bot Token")
    print("─" * 50)
    print("Get this from @BotFather on Telegram:")
    print("  1. Open Telegram → chat with @BotFather")
    print("  2. Send /newbot")
    print("  3. Name your bot (e.g., 'LILITH')")
    print("  4. Copy the token")
    print()
    
    token = input("Enter your Telegram Bot Token: ").strip()
    
    print("\n[STEP 2] Your Telegram User ID")
    print("─" * 50)
    print("Get this from @userinfobot on Telegram:")
    print("  1. Open Telegram → message @userinfobot")
    print("  2. It will reply with your numeric ID")
    print()
    
    user_id = input("Enter your Telegram User ID: ").strip()
    
    return token, user_id

def configure_openclaw(token, user_id):
    """Configure OpenClaw with Telegram settings"""
    print("\n[STEP 3] Configuring OpenClaw")
    print("─" * 50)
    
    # Set bot token
    cmd_token = f'node openclaw.mjs config set channels.telegram.botToken "{token}"'
    subprocess.run(cmd_token, shell=True, cwd=OPENCLAW_DIR)
    
    # Enable Telegram
    cmd_enable = 'node openclaw.mjs config set channels.telegram.enabled true'
    subprocess.run(cmd_enable, shell=True, cwd=OPENCLAW_DIR)
    
    # Set DM policy to open for master
    cmd_policy = 'node openclaw.mjs config set channels.telegram.dmPolicy "open"'
    subprocess.run(cmd_policy, shell=True, cwd=OPENCLAW_DIR)
    
    # Allow only master's user ID
    cmd_allow = f'node openclaw.mjs config set channels.telegram.allowFrom "[\\"{user_id}\\"]"'
    subprocess.run(cmd_allow, shell=True, cwd=OPENCLAW_DIR)
    
    print(f"\n[+] Telegram configured for user: {user_id}")

def setup_lilith_workspace():
    """Configure LILITH as the agent persona"""
    print("\n[STEP 4] Setting up LILITH persona")
    print("─" * 50)
    
    workspace_dir = OPENCLAW_DIR / 'lilith_workspace'
    workspace_dir.mkdir(exist_ok=True)
    
    # Set workspace
    cmd_workspace = f'node openclaw.mjs config set agents.defaults.workspace "{workspace_dir}"'
    subprocess.run(cmd_workspace, shell=True, cwd=OPENCLAW_DIR)
    
    print(f"[+] LILITH workspace: {workspace_dir}")

def print_next_steps(token):
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                    SETUP COMPLETE!                            ║
╚═══════════════════════════════════════════════════════════════╝

[NEXT STEPS]

1. Start the OpenClaw Gateway:
   
   cd openclaw
   node openclaw.mjs gateway --verbose

2. Open Telegram and message your bot!
   LILITH will respond through OpenClaw.

3. (Optional) Install as daemon for always-on:
   
   node openclaw.mjs onboard --install-daemon

[COMMANDS IN TELEGRAM]

  /status     - Check LILITH status
  /reset      - Reset conversation
  /model      - Show current model
  /help       - List all commands

[LILITH BRIDGE]

For direct LILITH backend queries via OpenClaw:
  
  python openclaw/lilith_bridge.py

[TROUBLESHOOTING]

- Check logs: node openclaw.mjs logs --follow
- Verify config: node openclaw.mjs config get channels.telegram
- Doctor check: node openclaw.mjs doctor
""")

def main():
    print_banner()
    
    # Check if running from correct directory
    if not OPENCLAW_DIR.exists():
        print(f"[!] OpenClaw not found at: {OPENCLAW_DIR}")
        print("[!] Run this script from LuciferOS_FULL directory")
        return
    
    token, user_id = get_telegram_credentials()
    
    if not token or not user_id:
        print("[!] Token and User ID are required")
        return
    
    configure_openclaw(token, user_id)
    setup_lilith_workspace()
    print_next_steps(token)
    
    # Offer to start gateway
    start = input("\nStart OpenClaw Gateway now? (y/n): ").strip().lower()
    if start == 'y':
        print("\n[*] Starting OpenClaw Gateway...")
        print("[*] Press Ctrl+C to stop\n")
        subprocess.run('node openclaw.mjs gateway --verbose', shell=True, cwd=OPENCLAW_DIR)

if __name__ == "__main__":
    main()
