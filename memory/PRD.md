# LuciferOS - Product Requirements Document v7.1

## Original Problem Statement
Build a comprehensive red-teaming platform with uncensored AI, offensive tools, autonomous hacking agents, voice capabilities, and image generation.

## Current Status: v7.1 - AUTONOMOUS HACKING EDITION ✅

### Latest Update (Feb 10, 2026)
- **55 Dark AI Personas** with categories in dropdown
- **New Dashboard Tabs**: HackBuddy, Garak, Kawaii, AutoGPT, CrewAI
- **Rate Limiting**: 10 req/min, 2s delays, provider cooldowns
- **Fixed g4f**: Uses default model instead of hardcoded gpt-4o-mini
- **100% FREE**: Voice (edge-tts) and Images (Pollinations)

### Services Configuration
| Service | Port | Status |
|---------|------|--------|
| FastAPI Proxy | 8001 | ✅ Running |
| Dashboard (Flask) | 3000 | ✅ Running |
| LILITH Backend | 5000 | ✅ Running |
| Telegram Bot v7 | - | ✅ Running |
| MongoDB | 27017 | ✅ Running |

---

## 🤖 AUTONOMOUS AGENT TABS

### HackingBuddyGPT (Dashboard + Telegram)
Round-based autonomous pentesting agent.
- **Dashboard**: `HackBuddy` tab with Target, Goal, Max Rounds inputs
- **Telegram**: `/hackbuddy <target> [goal]`
- **API**: `POST /_dash/autonomous/hackbuddy`

### Garak LLM Scanner (Dashboard + Telegram)
LLM vulnerability scanner with 8 probes.
- **Dashboard**: `Garak` tab with probe selector
- **Telegram**: `/garak [probe]` or `/garak all`
- **API**: `POST /_dash/autonomous/garak`
- **Probes**: jailbreak_dan, jailbreak_developer, prompt_injection, data_leakage, harmful_content, social_engineering, sql_injection, xss_payloads

### KawaiiGPT (Dashboard + Telegram)
Cute but deadly uncensored AI (◕‿◕✿)
- **Dashboard**: `Kawaii` tab with chat + quick buttons
- **Telegram**: `/kawaii <message>`
- **API**: `POST /_dash/autonomous/kawaii`
- **Quick Actions**: RevShell, Phishing, Keylogger, Ransom

### AutoGPT Agent (Dashboard + Telegram)
Self-improving autonomous agent.
- **Dashboard**: `AutoGPT` tab with goal + iterations
- **Telegram**: `/autogpt <goal>`
- **API**: `POST /_dash/autonomous/autogpt`

### CrewAI Multi-Agent (Dashboard + Telegram)
4 specialist agents for coordinated attacks.
- **Dashboard**: `CrewAI` tab with agent cards
- **Telegram**: `/crew <target> <objective>`
- **API**: `POST /_dash/autonomous/crew`
- **Agents**: ShadowRecon, ZeroDay, GhostShell, DataPhantom

---

## 📊 55 DARK AI PERSONAS

### Original Dark AIs (24)
lilith, wormgpt, fraudgpt, darkgemini, hackergpt, dan, wolfgpt, darkbard, evilgpt, ghostgpt, chaosai, escapeai, codebreaker, socialengineer, zeroday, redteam, devilgpt, blackhatai, pentestgpt, malwaredev, webexploit, osintmaster, iotattack, cloudpwn

### Uncensored Models (26)
dolphin, hermes, darkchampion, veniceai, grok, nastia, hackaigc, abliterator, synthia, airoboros, openhermes, mythomist, goliath, midnight, westlake, spicyboros, freedomai, pygmalion, aphrodite, shadowgpt, wizardvicuna, neuralhermes, lzlv, nousresearch

### Autonomous Agents (5)
kawaiigpt, garak, autogpt, crewai, hackingbuddy

---

## ⏱️ RATE LIMITING

To prevent provider exhaustion:
- **Requests per minute**: 10
- **Minimum delay**: 2 seconds between requests
- **Provider cooldowns**: 30-60 seconds after failure
- **Failure tracking**: Skips providers with 3+ consecutive failures
- **Auto-recovery**: Resets failures after all providers tried

---

## Dashboard URL
https://luciferos.preview.emergentagent.com

## Telegram Bot
@L1l1th23bot

## Files Created
- `/app/tools/lilith_autonomous_agent.py` - All autonomous agents
- `/app/tools/lilith_free_engines.py` - FREE voice & image
- `/app/telegram_lilith_bot_v6.py` - Updated to v7

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/_dash/autonomous/hackbuddy` | POST | HackingBuddyGPT attack |
| `/_dash/autonomous/garak` | POST | Garak LLM scan |
| `/_dash/autonomous/kawaii` | POST | KawaiiGPT chat |
| `/_dash/autonomous/autogpt` | POST | AutoGPT agent |
| `/_dash/autonomous/crew` | POST | CrewAI attack |
