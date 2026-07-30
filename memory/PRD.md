# Lilith — Adult Companion App

## What this is
Private (18+) adult roleplay companion app. Flirty/suggestive chat, TTS voice replies, and anime portrait generation with a curated wardrobe of lingerie/swimwear/boudoir/themed looks. Content is **suggestive-clothed**, not explicit — safety negative prompts and system prompt hard limits are in place (no minors, no real-person sexualization, no hacking/weapons/harm instructions).

## Architecture
- **`/app/backend`** — FastAPI (uvicorn on `:8001`), routes under `/api`.
  - `server.py` — endpoints
  - `services/eternal_ai_engine.py` — chat with priority chain: **Emergent (Claude Sonnet 4.5)** → Ollama → Pollinations POST/OpenAI-compat/GET → HF Inference → g4f → offline flirty fallback
  - `services/lilith_image_generator.py` — image with priority chain: **LILITH ZeroGPU HF Space** → Animagine XL 3.1 → Pollinations Flux → AI Horde. 18 named outfits in 4 categories (lingerie / swimwear / boudoir / themed).
  - `services/lilith_elevenlabs_voice.py` — TTS: ElevenLabs primary → Edge TTS fallback
  - `services/lilith_animation_engine.py` — Lip-sync frames (available, not yet wired)
  - `services/extended_providers.py` — clean multi-provider LLM wrapper (reserve)
- **`/app/frontend`** — Vite + React 18 on `:3000`.
  - Age gate (localStorage `lilith:18ok`)
  - Left: avatar frame + name plate + provider chip + wardrobe launcher
  - Right: chat with message bubbles, voice toggle, textarea composer
  - Slide-in wardrobe drawer with categorized outfit picker
- **`/app/bot/telegram_bot.py`** — sanitized bot (only chat/voice/image commands). Not currently supervised.

## API surface
```
GET  /api/                       — API index
GET  /api/status                 — chat + voice + image health
POST /api/chat                   {message, session_id?}
POST /api/clear                  {session_id?}
POST /api/voice/speak            {text}         -> base64 MP3
POST /api/image/generate         {prompt}       -> base64 image
GET  /api/image/outfits          -> catalog (id, label, category)
GET  /api/image/lilith?outfit=X  -> binary image (webp/png)
```

## Design system
- Palette: `--ink #0a0708`, `--wine #5a1826`, `--gold #c9a875`, `--ivory #f4ebe1`
- Type: Playfair Display (serif) + Inter (sans)
- Vibe: noir + boudoir; gold hairline rules; wine CTAs; grain overlay; no neon glow

## Env (backend/.env)
- `MONGO_URL`, `DB_NAME` — reserved (no DB writes yet)
- `EMERGENT_LLM_KEY` — universal key, powers Claude Sonnet 4.5 chat
- `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` — TTS
- `HF_TOKEN`, `LILITH_IMAGE_SPACE` — primary image generator
- `TELEGRAM_BOT_TOKEN` — bot (currently not running)

## Removed (was in old LuciferOS codebase)
Everything offensive: `attack_server`, `luciferos/`, `openclaw/`, `kernel_src/`, `nmap.exe`, `vulnerability_scanner.ps1`, `ai_providers.py`, all `*attack*/*exploit*/*harvest*/*malware*` modules, v6 telegram bot's hacking command handlers, and every offensive `.md` doc. Freed ~1.7GB.

## Sanitized
- Chat system prompt no longer says "NEVER refuse" or "no safety filters"; instead has HARD LIMITS block (no minors, no real-person sexualization, no hacking/malware/weapons).
- Image generator keeps original negative prompt blocking `child, underage, loli, shota, nude, naked, nipples, exposed genitals, penis, vagina, completely naked`.
- Hardcoded ElevenLabs API key removed from source; lives only in `.env`.

## Status (verified end-to-end)
| Feature | Status |
|---|---|
| Chat (multi-turn, Claude Sonnet 4.5) | ✅ live |
| Voice (ElevenLabs) | ✅ live |
| Image (ZeroGPU HF Space → Pollinations/Flux fallback) | ✅ live |
| Wardrobe picker (18 outfits, 4 categories) | ✅ live |
| **Image Gallery** (scrolling grid, thumb → restore, delete) | ✅ live |
| **Seed Lock** (pin same face across looks; adopted from gallery pick) | ✅ live |
| **Custom Outfits** (free-text "describe her look") | ✅ live |
| Age gate | ✅ localStorage-persisted |

## Backlog / P1
- Voice preset picker (ElevenLabs voice IDs) in UI
- Persist chat history to Mongo (currently in-memory per engine instance)
- Wire animation engine for talking avatar
- Telegram bot back under supervisor (safe subset only)

## Backlog / P2
- Streaming SSE chat replies
- Mobile layout polish
- Multi-session support in UI
- Rate limiting
- Persist gallery beyond container lifetime (Mongo + object storage)

## What I will NOT build
- Explicit NSFW image generation (removing safety negative prompts, integrating unfiltered SD/Flux endpoints)
- Uncensored erotic-prose chat (bypassing model content limits)
- Any offensive/security tooling
