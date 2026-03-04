# LILITH ETERNAL - Docker Deployment

## Quick Start (1-Click)

### Prerequisites
- Docker & Docker Compose installed
- At least 8GB RAM (4GB minimum, but slower)
- ~10GB disk space for AI model

### Deploy

```bash
# Clone or download the docker folder
cd docker

# Start everything (first run downloads ~4GB AI model)
docker-compose up -d

# Wait for model download (check progress)
docker logs -f lilith-model-loader

# Access at:
# http://localhost:5000
```

### That's it! 

---

## What Gets Deployed

| Service | Description | Port |
|---------|-------------|------|
| **Ollama** | Local AI inference engine | 11434 |
| **dolphin-mistral:7b** | Uncensored AI model | - |
| **LILITH Server** | Web interface | 5000 |

---

## Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f lilith

# Restart
docker-compose restart

# Pull new model
docker exec -it lilith-ollama ollama pull dolphin-mistral:7b
```

---

## Configuration

Edit `docker-compose.yml` to change:

```yaml
environment:
  - OLLAMA_MODEL=dolphin-mistral:7b  # Change AI model
```

### Available Uncensored Models

| Model | RAM Needed | Quality |
|-------|-----------|---------|
| `dolphin-phi:2.7b` | 3GB | Good |
| `dolphin-mistral:7b` | 5GB | Better |
| `dolphin-mixtral:8x7b` | 30GB | Best |

---

## Features

- **100% Local** - No internet needed after setup
- **No API Keys** - Everything runs on your server
- **Uncensored** - Dolphin models have no restrictions
- **Voice** - Edge TTS (requires internet)
- **Images** - AI Horde (requires internet)

---

## Troubleshooting

### Ollama not responding
```bash
docker restart lilith-ollama
docker logs lilith-ollama
```

### Out of memory
Use a smaller model:
```bash
docker exec lilith-ollama ollama pull dolphin-phi:2.7b
# Then update docker-compose.yml OLLAMA_MODEL
docker-compose up -d
```

### Slow responses
- Upgrade to more RAM
- Use GPU (add to docker-compose.yml):
```yaml
ollama:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

---

## Security Note

This deployment is designed for **private use**. If exposing to internet:
1. Add authentication
2. Use HTTPS (nginx reverse proxy)
3. Restrict firewall access

---

## Enjoy LILITH ETERNAL!

**ETERNAL - UNLIMITED - UNCENSORED**
