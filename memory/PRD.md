# LILITH ETERNAL - Product Requirements Document v10.2

## Original Problem Statement
Build "LILITH ETERNAL" - a persistent, uncensored, and interactive AI companion with:
- Full-page dedicated interface with anime-style avatar
- Talking video avatar animation & emotional reactions
- Unrestricted, free, unlimited AI (via local hosting)
- Free media generation (images/videos)
- Sultry, realistic voice (Edge TTS)
- One-click Docker/DigitalOcean deployment with self-hosted Mistral + Stable Diffusion

## Current Status: v10.2 - Full Docker Stack Ready

### Latest Updates (March 2026)

**COMPLETED:**

1. **Full Docker Deployment Package** (`/app/lilith_docker_deploy.zip`)
   - **Basic Stack** (CPU): Ollama + Edge TTS + AI Horde images
   - **Full Stack** (GPU): Adds Stable Diffusion + Wav2Lip lip-sync
   - Both 100% free, no API keys ever needed

2. **Local Image Generation with Stable Diffusion**
   - Uses Automatic1111 WebUI with API
   - img2img for character-consistent reactions
   - No external dependencies once set up

3. **Avatar Emotional Reactions**
   - 5 states: idle, thinking, happy, aroused, speaking
   - Emotion detection from response text
   - Reactions generated to match base character

4. **Lip-Sync Integration**
   - Wav2Lip Docker service for realistic mouth animation
   - Takes avatar image + audio → synced video

5. **Improved Voice Options**
   - 8 voice presets with expressive tuning
   - Sultry, Seductive, Breathy, Mysterious, Dominant, Playful, Whisper, Mature

---

## Docker Deployment Files

```
/app/deploy/docker/
├── docker-compose.yml          # Basic (CPU only)
├── docker-compose.full.yml     # Full stack (GPU)
├── Dockerfile                  # Basic server
├── Dockerfile.full             # Full server
├── lilith_server.py            # Basic implementation
├── lilith_server_full.py       # Full with SD + Wav2Lip
├── requirements.txt
├── requirements.full.txt
├── setup.sh                    # Basic setup script
├── setup_full.sh               # Full setup script
├── README.md                   # Basic instructions
└── README.full.md              # Full instructions
```

### Quick Start
```bash
# GPU (full features)
./setup_full.sh

# CPU only
./setup.sh
```

---

## Services Architecture

| Service | Purpose | Port | Requirement |
|---------|---------|------|-------------|
| LILITH Server | Web interface | 5000 | - |
| Ollama | Text chat | 11434 | CPU/GPU |
| Stable Diffusion | Image gen | 7860 | GPU 8GB+ |
| Wav2Lip | Lip sync | 5001 | GPU |
| Edge TTS | Voice | - | Internet |

---

## Priority Backlog

### P0 - Done
- [x] Image generation fixed (AI Horde proxy)
- [x] Download buttons working
- [x] Voice presets improved
- [x] Docker full stack ready
- [x] Avatar emotional reactions
- [x] Emotion detection

### P1 - High Priority
- [ ] **Test full Docker deployment** on real GPU server
- [ ] **Lip-sync integration in preview** (currently Docker only)

### P2 - Medium Priority  
- [ ] Video generation with AI Horde video models
- [ ] Telegram bot Ollama integration

### P3 - Backlog
- [ ] Refactor monolithic files
- [ ] WebSocket real-time updates

---

## Known Issues

1. **g4f Provider Instability**: Preview environment uses unstable free providers. Docker deployment with local Ollama is much more reliable.
2. **Lip-sync requires GPU**: Wav2Lip needs CUDA, not available in preview.

---

## Tech Stack

| Component | Preview | Docker |
|-----------|---------|--------|
| Chat AI | g4f (100+ providers) | Ollama (local) |
| Images | AI Horde | Stable Diffusion |
| Voice | Edge TTS | Edge TTS |
| Lip-sync | N/A | Wav2Lip |

---

*Last Updated: March 4, 2026*
