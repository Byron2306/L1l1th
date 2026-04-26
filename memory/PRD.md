# LILITH ETERNAL - PRD v15.0

## Live URL
https://sultry-avatar.preview.emergentagent.com/lilith/

## What's Working

### Chat - FULLY EXPLICIT
- 7-layer AI rotation (g4f auto, Pollinations, DuckDuckGo, HF, Proxies, TOR, Fallback)
- System prompt: raw, graphic, sexually explicit descriptions
- Language mirroring: matches and EXCEEDS user's dirty talk level
- Explicit fallback responses with graphic sexual descriptions

### Images - NSFW GALORE
- **Pollinations** (PRIMARY - NSFW-capable, no key, free)
- **Pollinations model variants** (flux, turbo, flux-realism, flux-anime, flux-3d)
- **AI Horde** (nsfw=True, censor_nsfw=False, free unlimited)
- **HuggingFace Animagine XL 3.1** (fallback, may censor some NSFW)
- **HuggingFace FLUX.1-schnell** (fast, free tier)
- Smart provider rotation with failure tracking
- 18 NSFW outfit/style options from lingerie to full nude
- 12 selfie styles: seductive, dark, sultry, fierce, playful, wet, elegant, intimate, nude, bath, topless, erotic
- Auto NSFW tag detection from user prompts
- Images always download as images (never .txt)

### Video - Animated Images
- CSS Ken Burns animation (zoom/glow/pulse on generated images)
- No API key needed - works with any image provider
- `is_animated` flag enables smooth animation in chat

### Voice, Lip Sync, Sessions, Telegram, TOR - All working

## Session 5 Changes (April 26, 2026)
- [x] Rewrote entire image generator (lilith_image_generator.py) with 5 providers + smart rotation
- [x] Pollinations made absolute primary (NSFW-capable, Animagine was censoring)
- [x] Added 5 Pollinations model variants for diversity
- [x] Added FLUX.1-schnell as provider
- [x] 18 NSFW style options in NSFW_STYLES list
- [x] Rewrote system prompt to be raw, explicit, graphic
- [x] Fallback responses now sexually explicit with physical descriptions
- [x] NSFW auto-detection adds explicit/nsfw/erotic tags
- [x] Video uses CSS animation (no broken Pollinations video API)

## Config
```
ELEVENLABS_API_KEY=sk_be1c723ee790986c8c10418a351ac7438de2bbba972d02a1
ELEVENLABS_VOICE_ID=Md7yllQ29xXxuJKm6IHL
MONGO_URL=mongodb://localhost:27017
DB_NAME=lilith_eternal
TELEGRAM_BOT_TOKEN=8329009190:AAFTUX4D0id7oVPEOqr9wy0r1HpJ9Up_2bw
```

*Last Updated: April 26, 2026*
