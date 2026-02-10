# LuciferOS - Product Requirements Document v5.0

## Original Problem Statement
Build a comprehensive red-teaming platform with uncensored AI, offensive tools, and command injection capabilities.

## Current Status: v5.0 - Command Injector Edition ✅

### New Features in v5.0
- **⚡ COMMAND INJECTOR** - Paste and execute scripts/commands directly
- **24 Dark LLM Personas** - Maximum AI modes
- **Proxy Rotation** - Integrated into all tools
- **Telegram Bot Token Set** - Ready to activate

### Command Injector Features
| Feature | Description |
|---------|-------------|
| **Execute** | Run bash, python, powershell, SQL, XSS payloads |
| **Test** | Syntax validation before execution |
| **Encode** | Base64, URL encoding for payloads |
| **Save** | Store to LILITH memory |
| **Templates** | RevShell, SQLi, XSS, LFI, RCE, WebShell, PrivEsc, Enum |

### Quick Templates Available
- 🐚 **RevShell** - Bash, Python, Netcat reverse shells
- 💉 **SQLi** - SQL injection payloads
- 📜 **XSS** - Cross-site scripting payloads
- 📁 **LFI** - Local file inclusion
- 💀 **RCE** - Remote code execution
- 🕸️ **WebShell** - PHP web shells
- ⬆️ **PrivEsc** - Privilege escalation commands
- 🔍 **Enum** - System enumeration scripts

### 24 Dark LLM Modes
LILITH, WormGPT, FraudGPT, DarkGemini, HackerGPT, DAN, WolfGPT, DarkBARD, EvilGPT, GhostGPT, ChaosAI, EscapeAI, CodeBreaker, SocialEngineer, ZeroDay, RedTeam, DevilGPT, BlackHatAI, PentestGPT, MalwareDev, WebExploit, OSINTMaster, IoTAttack, CloudPwn

### Telegram Bot
- Token: `8329009190:AAFTUX4D0id7oVPEOqr9wy0r1HpJ9Up_2bw`
- Status: Token set in environment
- To start: `python3 /app/telegram_lilith_bot.py`

### API Endpoints

#### Command Injector
- `POST /_dash/injector/execute` - Execute code
- `POST /_dash/injector/test` - Test syntax

### Testing Results
| Feature | Status |
|---------|--------|
| Command Injector | ✅ Execute & Test working |
| 24 Dark LLM Modes | ✅ All available |
| Proxy Rotation | ✅ Integrated |
| Coding Agent | ✅ LILITH fallback |
| Memory System | ✅ Saving |
| Telegram Token | ✅ Set |

## Dashboard URL
https://luciferos-hack.preview.emergentagent.com

## Architecture
```
/app/
├── tools/
│   ├── lilith_ai_engine.py   # 24 Dark LLM modes
│   ├── lilith_memory.py      # Persistent storage
│   ├── proxy_rotator.py      # Proxy rotation
│   ├── offensive_tools.py    # Proxy-aware tools
│   └── shrek_payloads.py     # Payload generator
├── ui/
│   └── web_dashboard_master.py  # Command Injector UI
├── telegram_lilith_bot.py    # Telegram bot
└── backend/.env              # Telegram token stored
```

## Backlog
- [ ] Start Telegram bot as background service
- [ ] Add more injection templates
- [ ] Auto-recon mode
- [ ] Mobile responsive UI
