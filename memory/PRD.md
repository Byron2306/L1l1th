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
| Chat (multi-turn, Claude Sonnet 4.5, restart-persistent) | ✅ live |
| Voice (ElevenLabs + Edge TTS fallback) | ✅ live |
| **Voice Picker** (34 ElevenLabs voices, choice persisted) | ✅ live |
| Image gen (HF Space → Pollinations/Flux → Animagine → AI Horde) | ✅ live |
| Wardrobe picker (18 outfits, 4 categories) | ✅ live |
| Image Gallery (persistent, scroll, thumb → restore, delete, star) | ✅ live |
| Seed Lock | ✅ live |
| Custom Outfits (free-text) | ✅ live |
| Scene catalog (16 scenes) | ✅ live |
| Pose catalog (15 text poses) | ✅ live |
| Face Reference (img2img via HF `/generate_reference` or Pollinations) | ✅ live |
| **Pose Reference upload** (BETA — prompt hint; ControlNet backend upgrade P2) | ✅ live |
| **Talking Avatar** (Web Audio API → avatar scale/brightness/glow pulse) | ✅ live |
| **Persistence** — Mongo `chat_sessions` / `gallery_entries` / `system_state`; files under `/app/data/gallery/` and `/app/data/references/` | ✅ live |
| Age gate | ✅ localStorage-persisted |

## Recent changes (Feb 2026)
- **Image quality** — tightened positive/negative prompts, bumped HF Space steps 24→30 and guidance 5.5→6.5, and baked anti-deformity anchors into the Pollinations Flux fallback (which ignores negative prompts) to fix reported deformities.
- **Voice Preview button** — `/api/voice/list` now returns `preview_url` per voice; a ▶/■ preview button next to the voice dropdown plays the ElevenLabs sample. Cross-origin preview URLs bypass the WebAudio analyser to avoid CORS warnings.
- **Presets Library** — new Mongo collection `presets` + full CRUD (`GET/POST/DELETE /api/presets`, `POST /api/presets/:id/apply`, `GET /api/presets/:id/thumbnail`). Preserves outfit, custom prompt, scene, pose, seed, voice, and snapshots the current face + pose references so a preset survives later reference changes. Seeded with 8 starter looks: Rooftop Date, Evening at Home, Beach Sunset, Wine Cellar Confession, Rainy Night In, Alpine Escape, Opera Box, Sunday Morning. New `PresetsDrawer.jsx` opens via a "Presets" button in the avatar side.
- **Face-Swap Boost** — new `services/face_swap.py` uses remote HF Space `felixrosberg/face-swap`. Runs after primary generation whenever the toggle is on and a face reference is set. No local disk usage.
- **Pose "ControlNet"** — new `services/pose_controlnet.py`. Because every public ControlNet OpenPose HF Space was broken as of Feb 2026, we compose two remote calls: (1) `SJTU-TES/OpenPose` extracts a clean OpenPose skeleton from the user's pose photo, (2) that skeleton is fed to the user's own LILITH ZeroGPU Space `/generate_reference` at strength 0.62 so the pose dominates. Face fidelity can be layered back on via the face-swap boost, giving a real pose+face pipeline.
- Regression covered by `/app/backend/tests/backend_test.py` (voice list/select/speak, chat, image gen).

## Backlog / P1
- Telegram bot back under supervisor (safe subset only)
- Watch HF Space stability — if `SJTU-TES/OpenPose` or `felixrosberg/face-swap` go down, add secondary fallbacks (env `POSE_OPENPOSE_SPACE`, `FACESWAP_SPACE`)

## Backlog / P2
- Real ControlNet endpoint on the user's own ZeroGPU space (`/generate_pose_ctrl`) for perfect pose fidelity without the skeleton-as-reference hack
- Streaming SSE chat replies
- Streaming SSE chat replies
- Mobile layout polish
- Multi-session support in UI
- Rate limiting
- Move image files to object storage for cross-container persistence

## What I will NOT build
- Explicit NSFW image generation (removing safety negative prompts, integrating unfiltered SD/Flux endpoints)
- Uncensored erotic-prose chat (bypassing model content limits)
- Any offensive/security tooling
