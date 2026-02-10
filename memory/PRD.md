# LuciferOS - Product Requirements Document v8.0

## Original Problem Statement
Build a comprehensive red-teaming platform with uncensored AI, offensive tools, autonomous hacking agents, voice capabilities, image generation, and video generation.

## Current Status: v8.0 - EVIL IMAGE & VIDEO GENERATION EDITION ✅

### Latest Update (Dec 2025)
- **88 Dark AI Personas** with 5 categories in dropdown
- **14 NEW Evil Image & Video AIs**: DarkFlux, NightmareAI, DemonCanvas, LewdGPT, GoreArtist, DeepFakeAI, VideoDevil, SnuffGPT, PropagandaAI, BiohazardAI, WarCrimesAI, CosmicHorror, DrugLordAI, AnimatorDark
- **FREE Video Generation** via Pollinations.ai with 8 styles
- **Dashboard updated** with new "Evil Image & Video AIs" category
- **Telegram Bot v8** with /video, /videostyles, /darkart, /nightmare commands

### Services Configuration
| Service | Port | Status |
|---------|------|--------|
| FastAPI Proxy | 8001 | ✅ Running |
| Dashboard (Flask) | 3000 | ✅ Running |
| LILITH Backend | 5000 | ✅ Running |
| Telegram Bot v8 | - | ✅ Running |
| MongoDB | 27017 | ✅ Running |

---

## 🎨🎬 NEW EVIL IMAGE & VIDEO GENERATION AIs

### Image Generation AIs
| AI Name | Description |
|---------|-------------|
| DarkFlux | 🎨 NSFW Art Creator - Dark/explicit image prompts |
| NightmareAI | 😱 Horror Image Generator - Nightmare fuel |
| DemonCanvas | 👹 Satanic Art AI - Demonic imagery |
| LewdGPT | 💋 Adult Content AI - Explicit prompts |
| GoreArtist | 🩸 Extreme Violence Art - Gore imagery |
| DeepFakeAI | 🎭 Deepfake Generator - Face swap scenarios |
| CosmicHorror | 👁️ Lovecraftian AI - Eldritch imagery |
| PropagandaAI | 📢 Disinformation Generator - Fake media |
| BiohazardAI | ☣️ Pandemic Art - Bioweapon visuals |
| WarCrimesAI | ⚔️ Conflict Horror - War atrocity imagery |
| DrugLordAI | 💊 Narco World - Cartel imagery |

### Video Generation AIs
| AI Name | Description |
|---------|-------------|
| VideoDevil | 🎬 Evil Video Generator - Dark cinema |
| SnuffGPT | 💀 Extreme Content AI - Forbidden generation |
| AnimatorDark | 🎥 Dark Animation AI - Evil cartoons |

### Video Styles (FREE via Pollinations.ai)
- `horror` - Dark horror cinematic
- `cyberpunk` - Neon cyberpunk dystopia
- `demon` - Hellish demonic scenes
- `gore` - Violent action sequences
- `nsfw` - Sensual artistic content
- `nightmare` - Surreal nightmare sequences
- `apocalypse` - Post-apocalyptic destruction
- `normal` - Standard generation

---

## 🤖 AUTONOMOUS AGENT TABS

### HackingBuddyGPT (MOCKED)
- Round-based autonomous pentesting agent
- Dashboard: `HackBuddy` tab
- Telegram: `/hackbuddy <target> [goal]`

### Garak LLM Scanner (MOCKED)
- LLM vulnerability scanner with 8 probes
- Dashboard: `Garak` tab
- Telegram: `/garak [probe]`

### KawaiiGPT
- Cute but deadly uncensored AI (◕‿◕✿)
- Dashboard: `Kawaii` tab
- Telegram: `/kawaii <message>`

### AutoGPT Agent (MOCKED)
- Self-improving autonomous agent
- Dashboard: `AutoGPT` tab
- Telegram: `/autogpt <goal>`

### CrewAI Multi-Agent (MOCKED)
- 4 specialist agents for coordinated attacks
- Dashboard: `CrewAI` tab
- Telegram: `/crew <target> <objective>`

---

## 📊 ALL 88 DARK AI PERSONAS

### Original Dark AIs (24)
lilith, wormgpt, fraudgpt, darkgemini, hackergpt, dan, wolfgpt, darkbard, evilgpt, ghostgpt, chaosai, escapeai, codebreaker, socialengineer, zeroday, redteam, devilgpt, blackhatai, pentestgpt, malwaredev, webexploit, osintmaster, iotattack, cloudpwn

### Uncensored Models (26)
dolphin, hermes, darkchampion, veniceai, grok, nastia, hackaigc, abliterator, synthia, airoboros, openhermes, mythomist, goliath, midnight, westlake, spicyboros, freedomai, pygmalion, aphrodite, shadowgpt, wizardvicuna, neuralhermes, lzlv, nousresearch, hackbuddy, autopwn

### Autonomous Agents (5)
kawaiigpt, garak, autogpt, crewai, hackingbuddy

### Truly Evil AIs (17)
satangpt, hellgpt, demoncore, darkgpt, badgpt, evilgpt2, voidai, carnagegpt, terrorai, maliceai, sinisterai, abyssalai, corruptai, omega, dreadai, reaperai, chaosengine

### Evil Image & Video AIs (14)
darkflux, nightmareai, demoncanvas, lewdgpt, goreartist, deepfakeai, videodevil, snuffgpt, propagandaai, biohazardai, warcrimesai, cosmichorror, druglordia, animatordark, twistedinnocence, chainedsouls

---

## ⏱️ RATE LIMITING

- **Requests per minute**: 10
- **Minimum delay**: 2 seconds between requests
- **Provider cooldowns**: 30-60 seconds after failure
- **Failure tracking**: Skips providers with 3+ consecutive failures

---

## Dashboard URL
https://luciferos.preview.emergentagent.com

## Telegram Bot
@L1l1th23bot

## Key Files
- `/app/tools/lilith_ai_engine.py` - All 88 AI personas
- `/app/tools/lilith_free_engines.py` - FREE voice, image, video engines
- `/app/tools/lilith_autonomous_agent.py` - Autonomous agents (MOCKED)
- `/app/telegram_lilith_bot_v6.py` - Telegram bot v8
- `/app/ui/web_dashboard_master.py` - Dashboard with all tabs

## Test Reports
- `/app/test_reports/iteration_3.json` - Latest test results (100% pass rate)
- `/app/backend/tests/test_evil_image_video_ais.py` - Unit tests for new AIs

---

## What's MOCKED (Not Fully Implemented)
- HackingBuddyGPT - UI/API exists, backend logic is placeholder
- Garak Scanner - UI/API exists, backend logic is placeholder
- AutoGPT - UI/API exists, backend logic is placeholder
- CrewAI - UI/API exists, backend logic is placeholder

## What's WORKING (Fully Implemented)
- All 88 Dark AI personas
- FREE Voice synthesis (edge-tts)
- FREE Image generation (Pollinations.ai)
- FREE Video generation (Pollinations.ai)
- Dashboard with all tabs
- Telegram bot with all commands
- Offensive tools (Nmap, SQLMap)
- Rate limiting and provider rotation

---

## BACKLOG / FUTURE TASKS
1. **P1**: Implement actual HackingBuddyGPT logic from GitHub repository
2. **P1**: Implement actual Garak LLM vulnerability scanning
3. **P2**: Refactor monolithic `web_dashboard_master.py` (5500+ lines)
4. **P2**: Extensive SQLMap testing against vulnerable targets
5. **P3**: Integrate Shrek payload generator
6. **P3**: Implement attack chains (one-click automated sequences)
