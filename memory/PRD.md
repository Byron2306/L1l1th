# LILITH ETERNAL - Product Requirements Document v13.0

## Original Problem Statement
Build "LILITH ETERNAL" — a persistent, uncensored, interactive AI companion with anime-style demon girl avatar, lip-synced video, unrestricted chat, free image/video generation, sultry voice, and Docker deployment.

## Live URL
https://sultry-avatar.preview.emergentagent.com/lilith/

## What's Working

### AI Chat (7-Layer Provider Rotation)
1. Pollinations API (primary, fastest)
2. g4f auto-routing (50+ providers)
3. DuckDuckGo AI (GPT-4o-mini, Claude, Llama, Mixtral)
4. g4f specific providers
5. HuggingFace free inference (14 models)
6. Free community proxies (Free2GPT, NetFly)
7. TOR + clearnet free AIs (Venice AI, FreeGPT)
8. Romantic fallback (always-on)

### Image Generation (4 Providers, NSFW enabled)
1. HuggingFace Animagine XL 3.1 (896x1344)
2. Pollinations image API
3. AI Horde (nsfw=True, censor_nsfw=False)
4. Additional HuggingFace Spaces
- Styles: seductive, dark, sultry, fierce, playful, wet, elegant, intimate, **nude, erotic, bath, topless**

### Video Generation
- Pollinations Video API (Seedance model)
- Video player in chat with controls

### Lip Sync (Web Audio API)
- 20-bar audio visualizer
- Mouth indicator animation
- Avatar glow/pulse effects

### Voice: ElevenLabs + Edge TTS
### Session Persistence: MongoDB
### Image Preferences: /style command
### Telegram Bot v8: Full integration

### TOR/Free AI Endpoints
- DIG AI, Torry AI, Dark GPT, Not Evil AI (.onion)
- Venice AI, FreeGPT, Poe (clearnet free)

## Completed (Session 3 - April 26, 2026)
- [x] Fixed images downloading as .txt (proxy returns image/*, fallback is 1x1 PNG)
- [x] Fixed download endpoint (302 redirect instead of re-generating)
- [x] Removed NSFW content blocks (negative prompt, AI Horde settings)
- [x] Added nude/erotic/bath/topless selfie styles
- [x] Expanded preference detection for nude/erotic keywords
- [x] Video uses Pollinations Video API (Seedance)
- [x] Video player with controls in chat
- [x] Added Dark GPT, Not Evil AI .onion endpoints
- [x] Added clearnet free AIs (Venice AI, FreeGPT, Poe)
- [x] TOR engine falls back to clearnet when TOR unavailable

## Configuration
```bash
ELEVENLABS_API_KEY=sk_be1c723ee790986c8c10418a351ac7438de2bbba972d02a1
ELEVENLABS_VOICE_ID=Md7yllQ29xXxuJKm6IHL
MONGO_URL=mongodb://localhost:27017
DB_NAME=lilith_eternal
TELEGRAM_BOT_TOKEN=8329009190:AAFTUX4D0id7oVPEOqr9wy0r1HpJ9Up_2bw
```

## Remaining
- [ ] Local Ollama for fully offline uncensored AI
- [ ] Refactor monolithic lilith_full_page.py
- [ ] DigitalOcean deployment testing

*Last Updated: April 26, 2026*
