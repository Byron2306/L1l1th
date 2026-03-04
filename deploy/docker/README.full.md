# LILITH ETERNAL - Full Docker Deployment

## Complete AI Companion with Local Everything

**100% FREE - No API keys, no tokens, no limits, ever.**

### What's Included

| Service | Purpose | Requirement |
|---------|---------|-------------|
| **Ollama** | Text chat (dolphin-mistral) | CPU or GPU |
| **Stable Diffusion** | Image generation | GPU (8GB+ VRAM) |
| **Wav2Lip** | Lip-sync animation | GPU |
| **Edge TTS** | Voice synthesis | Internet |

---

## Quick Start

### Requirements
- Docker & Docker Compose
- **NVIDIA GPU with 8GB+ VRAM** (for image gen & lip-sync)
- ~25GB disk space (models)

### Deploy

```bash
# 1. Download and extract lilith_docker_deploy.zip
cd docker

# 2. Run the full stack
docker-compose -f docker-compose.full.yml up -d

# 3. Wait for models to download (first run takes 10-20 min)
docker logs -f lilith-model-loader
docker logs -f lilith-stable-diffusion

# 4. Access at http://localhost:5000
```

### That's it! 

---

## Simpler Setup (No GPU)

If you don't have a GPU, use the basic setup:

```bash
docker-compose up -d  # Uses docker-compose.yml (Ollama only)
```

This gives you:
- ✅ Uncensored chat (Ollama)
- ✅ Voice (Edge TTS)
- ⚠️ Images via AI Horde (external, variable quality)
- ❌ No lip-sync

---

## Services

### Ollama (Text Chat)
- **Model**: dolphin-mistral:7b (uncensored)
- **Port**: 11434
- **Memory**: 4-8GB RAM

### Stable Diffusion (Images)
- **UI**: Automatic1111 WebUI
- **Port**: 7860
- **VRAM**: 8GB+ recommended
- **Features**: txt2img, img2img (for character-consistent reactions)

### Wav2Lip (Lip Sync)
- **Port**: 5001
- **VRAM**: 4GB+
- **Input**: Image + Audio → Synced video

### LILITH Server
- **Port**: 5000 (main interface)
- **Features**: Chat, voice, images, avatar reactions

---

## Avatar Reactions

The system generates 5 emotional states from the base avatar image:

| State | Trigger |
|-------|---------|
| **idle** | Default |
| **thinking** | Processing/contemplating |
| **happy** | Positive emotions |
| **aroused** | Flirty/seductive content |
| **speaking** | During voice playback |

Uses img2img with low denoising to maintain character consistency.

To regenerate reactions:
```bash
curl -X POST http://localhost:5000/api/generate/reactions
```

---

## GPU Setup (NVIDIA)

Ensure you have:

1. **NVIDIA drivers** installed
2. **nvidia-container-toolkit**:
   ```bash
   # Ubuntu/Debian
   sudo apt install nvidia-container-toolkit
   sudo systemctl restart docker
   ```

Test GPU access:
```bash
docker run --rm --gpus all nvidia/cuda:12.1-base nvidia-smi
```

---

## Commands

```bash
# Start full stack
docker-compose -f docker-compose.full.yml up -d

# View logs
docker-compose -f docker-compose.full.yml logs -f lilith

# Stop
docker-compose -f docker-compose.full.yml down

# Restart service
docker-compose -f docker-compose.full.yml restart lilith

# Check GPU usage
nvidia-smi
```

---

## Ports Summary

| Port | Service |
|------|---------|
| 5000 | LILITH Web Interface |
| 7860 | Stable Diffusion WebUI |
| 11434 | Ollama API |
| 5001 | Wav2Lip API |

---

## Troubleshooting

### Out of VRAM
```bash
# Use smaller SD model
docker exec lilith-stable-diffusion wget -P /data/models \
  https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors
```

### Ollama slow
```bash
# Try smaller model
docker exec lilith-ollama ollama pull dolphin-phi:2.7b
# Update OLLAMA_MODEL in docker-compose.full.yml
```

### Wav2Lip not working
- Ensure GPU is available
- Check logs: `docker logs lilith-wav2lip`

---

## Customization

### Change Lilith's appearance
1. Replace `/app/avatars/lilith_base.png` with your image
2. Regenerate reactions: `curl -X POST http://localhost:5000/api/generate/reactions`

### Add more SD models
1. Download models to `sd_models` volume
2. Restart: `docker-compose -f docker-compose.full.yml restart stable-diffusion`

---

## Security

For public deployment:
1. Add authentication (modify lilith_server_full.py)
2. Use nginx reverse proxy with HTTPS
3. Restrict firewall access to trusted IPs

---

**ETERNAL - UNLIMITED - UNCENSORED**

*No keys. No tokens. No limits. Forever.*
