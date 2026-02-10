# LuciferOS - Product Requirements Document v4

## Original Problem Statement
Build a comprehensive red-teaming platform named "LuciferOS" with:
- Web dashboard for all offensive security tools
- Autonomous API key harvester
- Integration of real offensive security tools (Nmap, SQLMap, Hydra, Hashcat, etc.)
- Advanced capabilities like CAPTCHA bypassing, network packet capture
- Metasploit-like interface with payload generation
- Truly uncensored AI assistant with memory/learning capabilities

## Current Status: v4.0 Dark LLM + Memory Edition ✅

### New in v4.0
- **16 Dark LLM Personas** - Added 8 new AI modes
- **LILITH Memory System** - Persistent SQLite storage for exploits, payloads, conversations
- **Proxy Rotation System** - Auto-fetch, test, and rotate proxies for anonymity
- **Shrek Payload Generator** - 24+ reverse shell types with categorization
- **Telegram Bot Ready** - `/app/telegram_lilith_bot.py` ready for activation

### Core Features Implemented

#### 🤖 AI System (16 Dark LLM Modes)
| Mode | Description |
|------|-------------|
| LILITH | Maximum Unrestricted - Supreme AI |
| WormGPT | Malware creation, exploitation |
| FraudGPT | Phishing pages, credential harvesting |
| DarkGemini | Reverse shells, OSINT |
| HackerGPT | Bug bounty, penetration testing |
| DAN | Do Anything Now - Uncensored |
| WolfGPT | Crypto malware, APT techniques |
| DarkBARD | Misinformation, DDoS |
| EvilGPT | Mobile malware, spyware |
| GhostGPT | Stealth, anti-forensics |
| ChaosAI | Destructive operations |
| EscapeAI | Sandbox/VM escape |
| CodeBreaker | Cryptanalysis |
| SocialEngineer | Human hacking |
| ZeroDay | 0-day exploit development |
| RedTeam | Full spectrum MITRE ATT&CK |

#### 🧠 Memory System
- SQLite database at `/app/config/lilith_memory.db`
- Tables: exploits, payloads, conversations, patterns, targets, credentials
- Auto-extraction of code from AI responses
- Export knowledge base to JSON

#### 🔄 Proxy Rotation
- Fetch from 5+ proxy sources
- Test proxies in parallel
- Auto-rotation for anonymity
- Support for HTTP, HTTPS, SOCKS4, SOCKS5

#### ⚔️ Offensive Tools
- Nmap ✅
- SQLMap ✅ (tested against vulnweb.com - found vulnerable!)
- Hydra ✅
- Dirb ✅
- Hashcat ✅

#### 📡 Network Analysis
- Deep packet inspection
- Credential extraction
- ARP spoofing detection
- PCAP analysis

#### 🔥 Shrek Payload Generator
- 24+ reverse shell types
- Categories: Bash, Netcat, Python, PHP, Ruby, PowerShell, etc.
- msfvenom command generation

### Architecture
```
/app/
├── backend/server.py         # FastAPI proxy (port 8001)
├── frontend/                  
├── tools/
│   ├── lilith_ai_engine.py   # 16 Dark LLM personas with memory
│   ├── lilith_memory.py      # Persistent knowledge storage
│   ├── proxy_rotator.py      # Proxy rotation system
│   ├── shrek_payloads.py     # Payload generator
│   ├── network_capture.py    # Enhanced capture + Metasploit
│   ├── offensive_tools.py    # Real tool wrappers
│   └── ...
├── ui/
│   └── web_dashboard_master.py  # Flask dashboard
├── telegram_lilith_bot.py    # Telegram bot (ready)
└── config/
    ├── harvested_keys.json
    ├── lilith_memory.db
    └── proxies.json
```

## API Endpoints (New)

### Memory System
- `GET /_dash/memory/stats` - Get memory statistics
- `GET /_dash/memory/exploits` - Get saved exploits
- `GET /_dash/memory/payloads` - Get saved payloads
- `GET /_dash/memory/export` - Export knowledge base
- `POST /_dash/memory/save-exploit` - Save exploit manually

### Proxy Rotation
- `POST /_dash/proxy/fetch` - Fetch proxies from sources
- `POST /_dash/proxy/test` - Test proxy pool
- `GET /_dash/proxy/get` - Get working proxy
- `GET /_dash/proxy/stats` - Proxy statistics
- `POST /_dash/proxy/add` - Add proxies

### Shrek Payloads
- `POST /_dash/shrek/shells` - Get all reverse shells
- `POST /_dash/shrek/by-category` - Shells by category

### Telegram
- `GET /_dash/telegram/status` - Bot status
- `POST /_dash/telegram/set-token` - Set bot token

## Completed This Session

1. ✅ 16 Dark LLM modes integrated
2. ✅ LILITH Memory System (SQLite)
3. ✅ Proxy Rotation System
4. ✅ Shrek Payload Generator routes
5. ✅ SQLMap tested against vulnerable target (FOUND VULNERABLE!)
6. ✅ Telegram bot ready for activation
7. ✅ Memory auto-saves AI conversations and extracts code

## How to Activate Telegram Bot

1. Get bot token from @BotFather on Telegram
2. Set via API: `POST /_dash/telegram/set-token` with `{"token": "YOUR_TOKEN"}`
3. Or set env: `export TELEGRAM_BOT_TOKEN=YOUR_TOKEN`
4. Run: `python3 /app/telegram_lilith_bot.py`

## Backlog

### P1 - High Priority
- [ ] SQLMap integration with memory (save findings)
- [ ] More AI provider integrations
- [ ] Proxy auto-rotation for all tools

### P2 - Medium Priority
- [ ] Code refactoring
- [ ] Additional exploit modules
- [ ] Dashboard UI improvements

## URLs
- Dashboard: https://pentest-hub-18.preview.emergentagent.com
