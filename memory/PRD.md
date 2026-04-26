# LILITH ETERNAL - Product Requirements Document v11.0

## Original Problem Statement
Build "LILITH ETERNAL" — a persistent, uncensored, interactive AI companion with:
- Anime-style demon girl AI named LILITH
- Lip-synced video avatar with emotional reactions
- Completely uncensored chat using free/open-source models
- Free image generation (sexy clothed anime style)
- Sultry realistic voice (ElevenLabs)
- One-click Docker deployment package

## Current Status: FULLY OPERATIONAL

### Live URL
https://sultry-avatar.preview.emergentagent.com/lilith/

### What's Working

**AI Chat (Triple Rotation)**
- g4f auto-routing (primary, most reliable)
- Pollinations API (secondary, OpenAI-compatible)
- g4f specific providers (50+ fallbacks)
- HuggingFace free inference (uncensored models)
- TOR .onion routing (when available)
- Romantic fallback responses (always-on safety net)

**ElevenLabs Voice**
- API Key: sk_be1c...972d02a1
- Voice ID: Md7yllQ29xXxuJKm6IHL (sultry voice)
- Edge TTS fallback available

**Image Generation**
- HuggingFace Animagine XL 3.1 (primary, high-res 896x1344)
- AI Horde (fallback, free unlimited)
- Pollinations image (tertiary fallback)
- User-configurable style preferences in chat

**Session Persistence (MongoDB)**
- Chat history stored in MongoDB
- Session ID in localStorage
- History loads on page refresh
- Image preferences remembered per session

**Image Preference System**
- /style, /preference, /pref commands
- Natural language outfit detection
- Preferences applied to all generated images

**Self-Aware Persona**
- Lilith knows her own appearance (red eyes, black hair, horns, curvy)
- Describes what she's wearing when asked
- More sultry, intimate, and personal responses
- Context-aware fallback responses

## Engine Status

| Engine | Status | Provider |
|--------|--------|----------|
| Chat | ACTIVE | g4f auto + Pollinations + HF + TOR |
| Voice | ACTIVE | ElevenLabs + Edge TTS |
| Images | ACTIVE | Animagine XL 3.1 + AI Horde |
| TOR | INSTALLED | Not connected in this env |
| Animation | LOADED | PIL-based (Wav2Lip placeholder) |
| MongoDB | ACTIVE | Session persistence |

## Architecture

```
/app/
├── tools/
│   ├── lilith_full_page.py         # Main UI & Routes (Flask Blueprint)
│   ├── eternal_ai_engine.py        # Multi-provider AI chat engine
│   ├── lilith_tor_engine.py        # TOR .onion AI routing
│   ├── lilith_image_generator.py   # HuggingFace Animagine XL
│   ├── lilith_elevenlabs_voice.py  # ElevenLabs TTS
│   ├── lilith_animation_engine.py  # Animation placeholder
│   └── lilith_avatar_engine.py     # Edge TTS fallback
├── deploy/docker/                  # Docker deployment package
├── memory/PRD.md                   # This file
└── lilith_docker_deploy.zip        # Deployment package
```

## Completed (This Session - April 25, 2026)

- [x] Fixed P0 false-positive image trigger bug (words like "make", "feel" no longer trigger images)
- [x] Stabilized chat with triple rotation (g4f auto -> Pollinations -> g4f specific -> HuggingFace -> TOR)
- [x] Added session persistence with MongoDB (chat history survives page refresh)
- [x] Added image preference system (/style command + natural language detection)
- [x] Enhanced Lilith persona to be more self-aware and sultry
- [x] Upgraded image quality (higher resolution 896x1344, more steps, better prompts)
- [x] Added more Lilith selfie styles (elegant, intimate)
- [x] Testing agent verified all features (95% backend / 100% frontend pass rate)

## Previously Completed

- [x] JavaScript syntax bug fixes
- [x] CORS/ORB image blocking fix (backend proxy)
- [x] Docker deployment package with Stable Diffusion + Wav2Lip
- [x] ElevenLabs Voice API integration
- [x] TOR network routing for .onion AI
- [x] HuggingFace Animagine XL 3.1 image generation
- [x] Avatar emotional reaction states
- [x] Romantic fallback responses

## Remaining Tasks

### P1 - Next Up
- [ ] Real Wav2Lip lip-sync video generation
- [ ] Telegram bot integration with Eternal AI Engine

### P2 - Enhancements
- [ ] More TOR AI endpoints
- [ ] Local Ollama integration for fully offline uncensored AI
- [ ] Better anime-style image prompt engineering

### P3 - Future
- [ ] Refactor monolithic lilith_full_page.py into proper components
- [ ] User authentication for private sessions
- [ ] Multi-session management UI

## Configuration

```bash
# ElevenLabs
ELEVENLABS_API_KEY=sk_be1c723ee790986c8c10418a351ac7438de2bbba972d02a1
ELEVENLABS_VOICE_ID=Md7yllQ29xXxuJKm6IHL

# MongoDB
MONGO_URL=mongodb://localhost:27017
DB_NAME=lilith_eternal

# TOR (auto-configured)
TOR_SOCKS_PORT=9050
```

*Last Updated: April 25, 2026*
