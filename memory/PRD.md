# LILITH ETERNAL - Product Requirements Document v10.1

## Original Problem Statement
Build "LILITH ETERNAL" - a persistent, uncensored, and interactive AI companion with:
- Full-page dedicated interface with anime-style avatar
- Talking video avatar animation
- Unrestricted, free, unlimited AI (via local hosting)
- Free media generation (images/videos)
- Sultry, realistic voice (Edge TTS)
- One-click Docker/DigitalOcean deployment with self-hosted Mistral

## Current Status: v10.1 - Image Generation Fixed + Docker Ready

### Latest Updates (March 2026)

**COMPLETED:**

1. **Image Generation Fixed**
   - Implemented AI Horde proxy (free, no API key)
   - Images now display properly with full preview
   - Download buttons ("Save Me", "Full Size") working
   - Using `r2=True` for faster CDN delivery

2. **Voice Options Improved**
   - Added 8 voice presets: Sultry, Seductive, Breathy, Mysterious, Dominant, Playful, Whisper, Mature
   - Tuned voice styles for more expressive delivery (slower rate, lower pitch)

3. **Docker Deployment Package**
   - Complete `/app/lilith_docker_deploy.zip` ready
   - Includes: Dockerfile, docker-compose.yml, lilith_server.py, setup.sh, README
   - Uses `dolphin-mistral:7b` (uncensored) via Ollama
   - One-command setup: `./setup.sh`

---

## Architecture

```
/app/
├── tools/
│   ├── lilith_full_page.py      # MAIN: LILITH ETERNAL interface
│   ├── lilith_avatar_engine.py  # Voice presets & TTS
│   └── eternal_ai_engine.py     # g4f provider management
├── deploy/
│   ├── docker/                  # NEW: Docker deployment
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   ├── lilith_server.py     # Standalone server
│   │   ├── requirements.txt
│   │   ├── setup.sh             # Quick setup script
│   │   └── README.md
│   ├── digitalocean_install.sh  # Legacy shell installer
│   └── lilith_web_server.py     # Legacy standalone
├── lilith_docker_deploy.zip     # READY TO DOWNLOAD
└── lilith_digitalocean_deploy.zip
```

---

## Access Points

| Service | URL |
|---------|-----|
| LILITH ETERNAL | https://demon-companion.preview.emergentagent.com/lilith/ |
| Dashboard | https://demon-companion.preview.emergentagent.com |

---

## Docker Deployment (NEW)

### Quick Start
```bash
# Download and extract lilith_docker_deploy.zip
cd docker
./setup.sh
# Access at http://localhost:5000
```

### Components
- **Ollama**: Local AI inference
- **dolphin-mistral:7b**: Uncensored model (default)
- **LILITH Server**: Flask web interface
- **AI Horde**: Free image generation
- **Edge TTS**: Free voice synthesis

---

## Priority Backlog

### P1 - High Priority
- [ ] **Avatar Reactions**: Generate idle/happy/aroused/thinking expressions from static image
- [ ] **Lip-sync Animation**: Implement proper mouth movement sync with audio

### P2 - Medium Priority
- [ ] Video avatar improvement (currently static)
- [ ] Telegram bot Ollama integration

### P3 - Backlog
- [ ] Refactor monolithic files
- [ ] WebSocket real-time updates

---

## Known Issues

1. **g4f Provider Instability**: Preview uses unstable free providers; Docker deployment uses local Ollama for stability
2. **Video Asset 404**: User-provided video file external URL not loading

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python Flask |
| AI Chat | Ollama + dolphin-mistral (Docker), g4f (Preview) |
| Voice | Edge TTS (free) |
| Images | AI Horde (free) |
| Deployment | Docker Compose |

---

*Last Updated: March 4, 2026*
