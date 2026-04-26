# LILITH ETERNAL - PRD v14.0

## Live URL
https://sultry-avatar.preview.emergentagent.com/lilith/

## What's Working
- **Chat**: 7-layer AI rotation (Pollinations → g4f → DuckDuckGo → HF → Free Proxies → TOR → Fallback)
- **Language Mirroring**: Lilith matches user's tone — swears when they swear, gets explicit when they do
- **Images**: Pollinations primary (NSFW-capable), AI Horde, Animagine XL, HF Spaces. 12 styles including nude/erotic/bath/topless
- **Video**: CSS Ken Burns animation on generated images (no API key needed)
- **Voice**: ElevenLabs + Edge TTS
- **Lip Sync**: Web Audio API with visualizer
- **Session Persistence**: MongoDB
- **Image Preferences**: /style command + natural language
- **Telegram Bot v8**: Full Eternal Engine integration
- **TOR**: DIG AI, Torry, Dark GPT, Not Evil AI + clearnet free AIs

## Session 4 Changes (April 26, 2026)
- [x] Pollinations made PRIMARY image generator (NSFW-capable, Animagine was censoring)
- [x] Removed all NSFW blocks from negative prompt and AI Horde
- [x] Much more explicit selfie prompts (nude/erotic/bath/topless with actual nudity tags)
- [x] NSFW detection in user prompts auto-adds explicit tags
- [x] Language mirroring: Lilith matches swearing/dirty talk intensity
- [x] Dirty fallback responses when user uses explicit language  
- [x] Video uses CSS Ken Burns animation (no Pollinations video API key needed)
- [x] Frontend renders animated images with smooth zoom/glow effects

## Config
```
ELEVENLABS_API_KEY=sk_be1c723ee790986c8c10418a351ac7438de2bbba972d02a1
ELEVENLABS_VOICE_ID=Md7yllQ29xXxuJKm6IHL
MONGO_URL=mongodb://localhost:27017
DB_NAME=lilith_eternal
TELEGRAM_BOT_TOKEN=8329009190:AAFTUX4D0id7oVPEOqr9wy0r1HpJ9Up_2bw
```

## Remaining
- [ ] Local Ollama for fully offline AI
- [ ] Refactor monolithic lilith_full_page.py
- [ ] DigitalOcean deployment testing

*Last Updated: April 26, 2026*
