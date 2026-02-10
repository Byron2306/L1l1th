# LuciferOS - Product Requirements Document v4.5

## Original Problem Statement
Build a comprehensive red-teaming platform with:
- Web dashboard for all offensive security tools
- Autonomous API key harvester with learning
- Integration of real offensive security tools
- Metasploit-like interface with payload generation
- Uncensored AI assistant with persistent memory

## Current Status: v4.5 - 24 Dark LLM Modes ✅

### What's New in v4.5
- **24 Dark LLM Personas** (8 new additions)
- **Proxy Rotation Integration** into all offensive tools
- **Coding Agent with LILITH Fallback** (works without Groq key)
- **Enhanced Memory System** auto-saves exploits from AI

### 24 Dark LLM Modes
| Category | Modes |
|----------|-------|
| **Maximum** | LILITH, DevilGPT |
| **Malware** | WormGPT, EvilGPT, MalwareDev, WolfGPT |
| **Web** | FraudGPT, WebExploit |
| **Network** | DarkGemini, IoTAttack, CloudPwn |
| **Stealth** | GhostGPT, ChaosAI, EscapeAI |
| **Recon** | HackerGPT, PentestGPT, OSINTMaster |
| **Exploit** | ZeroDay, RedTeam |
| **Social** | SocialEngineer |
| **Crypto** | CodeBreaker |
| **General** | DAN, BlackHatAI, DarkBARD |

### Core Features

#### 🤖 AI System
- 24 Dark LLM personas with specialized prompts
- g4f integration for free AI access
- Memory auto-saves conversations and extracts exploits
- Coding agent with LILITH fallback

#### 🔄 Proxy Rotation (NEW)
- Integrated into SQLMap, requests
- Auto-fetch from 5+ proxy sources
- Parallel testing and rotation
- HTTP, HTTPS, SOCKS4/5 support

#### ⚔️ Offensive Tools
- Nmap ✅ (proxy-aware)
- SQLMap ✅ (proxy-aware, saves findings to memory)
- Hydra ✅
- Dirb ✅
- Hashcat ✅

#### 🧠 Memory System
- SQLite database
- Auto-extract code from AI responses
- Save targets, credentials, exploits
- Export knowledge base

#### 🔥 Shrek Payloads
- 24+ reverse shell types
- msfvenom command generation

#### 📱 Telegram Bot
- Ready at `/app/telegram_lilith_bot.py`
- Needs bot token from @BotFather
- Set via: `POST /_dash/telegram/set-token`

### Architecture
```
/app/
├── tools/
│   ├── lilith_ai_engine.py   # 24 Dark LLM modes
│   ├── lilith_memory.py      # Persistent storage
│   ├── proxy_rotator.py      # Proxy rotation
│   ├── offensive_tools.py    # Proxy-aware tools
│   ├── shrek_payloads.py     # Payload generator
│   └── lilith_full_backend.py # Coding agent fallback
├── ui/
│   └── web_dashboard_master.py
└── telegram_lilith_bot.py    # Ready for activation
```

### API Endpoints

#### New/Updated
- `POST /_dash/proxy/fetch` - Fetch proxies
- `POST /_dash/proxy/test` - Test proxies
- `GET /_dash/proxy/get` - Get working proxy
- `GET /_dash/memory/stats` - Memory statistics
- `POST /_dash/memory/save-exploit` - Save exploit
- `POST /_dash/shrek/shells` - All shells
- `POST /skill/run` - Coding agent (LILITH fallback)

## Testing Results

| Feature | Status |
|---------|--------|
| 24 Dark LLM Modes | ✅ Working |
| Memory System | ✅ Saving |
| Proxy Rotation | ✅ Integrated |
| Shrek Payloads | ✅ 24 types |
| Coding Agent | ✅ LILITH fallback |
| SQLMap | ✅ Found vuln on testphp.vulnweb.com |
| Telegram Bot | ⏳ Needs token |

## How to Activate Telegram

1. Message @BotFather on Telegram
2. Create new bot: `/newbot`
3. Get token (format: `123456789:ABC...`)
4. Set via API:
```bash
curl -X POST "/_dash/telegram/set-token" \
  -H "Content-Type: application/json" \
  -d '{"token": "YOUR_BOT_TOKEN"}'
```
5. Run: `python3 /app/telegram_lilith_bot.py`

## Dashboard
https://pentest-hub-18.preview.emergentagent.com

## Backlog
- [ ] More AI provider integrations
- [ ] Auto-recon mode (chain tools)
- [ ] Dashboard UI improvements
- [ ] Additional exploit modules
