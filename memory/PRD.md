# LILITH ETERNAL - Product Requirements Document v12.0

## Original Problem Statement
Build "LILITH ETERNAL" — a persistent, uncensored, interactive AI companion with anime-style demon girl avatar, lip-synced video, unrestricted chat, free image generation, sultry voice, and Docker deployment.

## Current Status: FULLY OPERATIONAL

### Live URL
https://sultry-avatar.preview.emergentagent.com/lilith/

## What's Working

### AI Chat (7-Layer Provider Rotation)
1. Ollama local (when available)
2. Pollinations API (primary - fastest, most reliable)
3. g4f auto-routing (50+ providers)
4. DuckDuckGo AI (GPT-4o-mini, Claude, Llama, Mixtral)
5. g4f specific providers (targeted fallback)
6. HuggingFace free inference (14 models: Mistral, Llama, Gemma, Phi, Zephyr, etc.)
7. Free community proxies (Free2GPT, NetFly)
8. TOR .onion routing (DIG AI, Torry)
9. Romantic fallback (always-on safety net)

### Lip Sync (Web Audio API)
- Browser-based audio frequency analysis
- 20-bar audio visualizer synced to speech
- Mouth indicator animation driven by volume
- Avatar scale/brightness pulsing during speech
- Glow effect intensity based on audio amplitude

### Telegram Bot v8
- Integrated with Eternal AI Engine (all 7 layers)
- Commands: /image, /selfie, /voice, /style, /status, /clear
- Image generation via HuggingFace Animagine XL
- ElevenLabs voice messages
- User preference storage per Telegram user

### Image Generation (4 Providers)
1. HuggingFace Animagine XL 3.1 (primary, 896x1344)
2. Pollinations image API (fast, free)
3. AI Horde (unlimited, free)
4. Additional HuggingFace Spaces (SDXL, etc.)

### Voice: ElevenLabs + Edge TTS fallback
### Session Persistence: MongoDB
### Image Preferences: /style command + natural language detection
### Self-Aware Persona: Knows her appearance, sultry and intimate

## Architecture
```
/app/
├── tools/
│   ├── lilith_full_page.py          # Main UI + Flask routes + Lip Sync
│   ├── eternal_ai_engine.py         # 7-layer AI provider rotation
│   ├── lilith_image_generator.py    # 4-provider image generation
│   ├── lilith_elevenlabs_voice.py   # ElevenLabs TTS
│   ├── lilith_tor_engine.py         # TOR .onion routing
│   ├── lilith_animation_engine.py   # PIL animation engine
│   └── lilith_avatar_engine.py      # Edge TTS fallback
├── telegram_lilith_bot_v8.py        # Telegram bot (Eternal Engine)
├── telegram_lilith_bot.py           # Entry point
├── deploy/docker/                   # Docker deployment package
└── memory/PRD.md
```

## Completed (Session 2 - April 26, 2026)
- [x] Web Audio API lip sync (visualizer bars, mouth animation, glow effects)
- [x] Telegram bot v8 rewrite with Eternal AI Engine + images + voice
- [x] DuckDuckGo AI integration (4 models: GPT-4o-mini, Claude, Llama, Mixtral)
- [x] Free community proxy chat integration
- [x] Expanded HuggingFace endpoints (14 models total)
- [x] Pollinations image generation added to image pipeline
- [x] Additional HuggingFace Spaces for images
- [x] Cache-busting headers to prevent CDN stale content
- [x] Provider count expanded to 39+ active providers

## Previously Completed (Session 1)
- [x] P0 false-positive image trigger bug fix
- [x] Chat stabilization with triple rotation
- [x] Session persistence (MongoDB)
- [x] Image preference system (/style command)
- [x] Enhanced sultry self-aware persona
- [x] Higher quality image generation (896x1344)

## Remaining Tasks

### P1
- [ ] Local Ollama integration for fully offline uncensored AI
- [ ] More TOR AI endpoints

### P2
- [ ] Refactor lilith_full_page.py monolith
- [ ] User authentication for private sessions

### P3
- [ ] Multi-session management UI
- [ ] DigitalOcean one-click deployment testing

## Configuration
```bash
ELEVENLABS_API_KEY=sk_be1c723ee790986c8c10418a351ac7438de2bbba972d02a1
ELEVENLABS_VOICE_ID=Md7yllQ29xXxuJKm6IHL
MONGO_URL=mongodb://localhost:27017
DB_NAME=lilith_eternal
TELEGRAM_BOT_TOKEN=8329009190:AAFTUX4D0id7oVPEOqr9wy0r1HpJ9Up_2bw
TOR_SOCKS_PORT=9050
```

*Last Updated: April 26, 2026*
