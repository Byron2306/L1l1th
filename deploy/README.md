# 💋 LILITH ETERNAL - DigitalOcean Deployment Guide

## Overview

LILITH ETERNAL is a completely **FREE, UNLIMITED, UNCENSORED** AI system that runs entirely on your own server. No API keys, no tokens, no external dependencies.

**Features:**
- 🧠 Local AI with Ollama (Dolphin-Mistral - fully uncensored)
- 🔊 Voice synthesis (Edge TTS - free, unlimited)
- 🖼️ Image generation (AI Horde primary with Pollinations Flux fallback)
- 💬 Web interface
- 🤖 Telegram bot
- 🔓 NO restrictions, NO censorship

---

## 🚀 Quick Start (1-Click Install)

### Step 1: Create DigitalOcean Droplet

1. Go to [DigitalOcean](https://www.digitalocean.com/)
2. Create a new Droplet:
   - **Image**: Ubuntu 22.04 LTS
   - **Size**: 
     - **Minimum**: 4GB RAM / 2 vCPUs ($24/month) - Basic usage
     - **Recommended**: 8GB RAM / 4 vCPUs ($48/month) - Best performance
     - **Premium**: 16GB+ RAM - For larger models
   - **Region**: Any
   - **Authentication**: SSH keys (recommended) or password

### Step 2: SSH into your Droplet

```bash
ssh root@YOUR_DROPLET_IP
```

### Step 3: Run the Installer

```bash
curl -sSL https://raw.githubusercontent.com/YOUR_REPO/lilith/main/install.sh | bash
```

Or download and run:

```bash
wget https://raw.githubusercontent.com/YOUR_REPO/lilith/main/install.sh
chmod +x install.sh
./install.sh
```

---

## 📦 What Gets Installed

| Component | Description |
|-----------|-------------|
| **Ollama** | Local AI inference engine |
| **Dolphin-Mistral 7B** | Uncensored AI model |
| **MongoDB** | Database for conversations |
| **Python 3** | Backend runtime |
| **Flask** | Web framework |
| **Edge TTS** | Voice synthesis |
| **Supervisor** | Process management |
| **Nginx** | Web server |
| **UFW** | Firewall |

---

## 🔧 Post-Installation Setup

### 1. Configure Telegram Bot

Get a bot token from [@BotFather](https://t.me/BotFather) on Telegram, then:

```bash
sudo nano /etc/systemd/system/lilith-telegram.service
```

Replace `YOUR_BOT_TOKEN_HERE` with your actual token:

```ini
Environment=TELEGRAM_TOKEN=your_actual_token_here
```

Reload and restart:

```bash
sudo systemctl daemon-reload
sudo systemctl restart lilith-telegram
```

### 2. Set Up Domain (Optional)

If you have a domain:

```bash
sudo nano /etc/nginx/sites-available/lilith
```

Add:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/lilith /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. Set Up SSL (Optional)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🎮 Usage

### Web Interface

Access: `http://YOUR_SERVER_IP:5000`

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Chat with Lilith |
| `/api/status` | GET | System status |
| `/api/clear` | POST | Clear history |
| `/api/voice/speak` | POST | Generate voice |
| `/api/image/generate` | POST | Generate image |

### Image Generation Endpoint

The deploy dashboard uses **AI Horde** as the primary image endpoint:

```text
POST https://aihorde.net/api/v2/generate/async
```

It is selected because it supports explicit NSFW generation flags, disabling NSFW censoring, and img2img reference input for style/identity lock. If AI Horde is unavailable or slow, the dashboard falls back to Pollinations Flux via `https://gen.pollinations.ai/image/{prompt}` with `safe=false`.

Optional environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_HORDE_ENABLED` | `true` | Enable AI Horde as the primary image provider |
| `AI_HORDE_API_ROOT` | `https://aihorde.net/api/v2` | AI Horde API root |
| `AI_HORDE_API_KEY` | `0000000000` | AI Horde API key; anonymous key works but is slower |
| `AI_HORDE_MODELS` | empty | Optional comma-separated Horde model allowlist |
| `AI_HORDE_POLL_SECONDS` | `150` | Max seconds to wait for Horde before fallback |
| `LILITH_IMAGE_WIDTH` | `832` | Generated image width |
| `LILITH_IMAGE_HEIGHT` | `1216` | Generated image height |

### Chat API Example

```bash
curl -X POST http://YOUR_SERVER_IP:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Lilith!", "voice_enabled": false}'
```

### Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Start conversation |
| `/voice` | Toggle voice messages |
| `/image <prompt>` | Generate image |
| `/clear` | Clear history |
| `/status` | Check status |

---

## 🛠️ Management Commands

### Check Services

```bash
# Lilith server status
sudo systemctl status lilith

# Telegram bot status
sudo systemctl status lilith-telegram

# Ollama status
sudo systemctl status ollama
```

### View Logs

```bash
# Lilith server logs
journalctl -u lilith -f

# Telegram bot logs
journalctl -u lilith-telegram -f

# Ollama logs
journalctl -u ollama -f
```

### Restart Services

```bash
sudo systemctl restart lilith
sudo systemctl restart lilith-telegram
sudo systemctl restart ollama
```

### Check Ollama Models

```bash
ollama list
```

### Pull Additional Models

```bash
# Smaller, faster model
ollama pull dolphin-phi:2.7b

# Larger, smarter model (needs 16GB+ RAM)
ollama pull dolphin-mixtral:8x7b

# Code-focused model
ollama pull codellama:7b
```

---

## 🔒 Security

### Firewall Rules (Pre-configured)

| Port | Service |
|------|---------|
| 22 | SSH |
| 80 | HTTP |
| 443 | HTTPS |
| 5000 | Lilith API |

### Restrict API Access (Optional)

Edit `/opt/lilith/lilith_server.py` to add authentication or IP whitelist.

---

## 💾 Backup

### Backup Conversations

```bash
mongodump --db lilith --out /backup/$(date +%Y%m%d)
```

### Backup Configuration

```bash
cp /etc/systemd/system/lilith*.service /backup/
cp /opt/lilith/*.py /backup/
```

---

## 🔄 Updates

### Update Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Update Python Dependencies

```bash
source /opt/lilith/venv/bin/activate
pip install --upgrade g4f edge-tts flask
```

### Pull Latest Model

```bash
ollama pull dolphin-mistral:7b
```

---

## ❓ Troubleshooting

### Ollama Not Responding

```bash
sudo systemctl restart ollama
sleep 5
ollama list
```

### Out of Memory

If you get OOM errors, try a smaller model:

```bash
export OLLAMA_MODEL=dolphin-phi:2.7b
sudo systemctl restart lilith
```

### Slow Responses

- Check RAM usage: `htop`
- Consider upgrading droplet size
- Use a smaller model

### Port Already in Use

```bash
sudo fuser -k 5000/tcp
sudo systemctl restart lilith
```

---

## 📊 Resource Usage

| Model | RAM Usage | Response Time |
|-------|-----------|---------------|
| dolphin-phi:2.7b | ~3GB | 2-5s |
| dolphin-mistral:7b | ~5GB | 5-15s |
| dolphin-mixtral:8x7b | ~30GB | 15-30s |

---

## 📝 License

This project is provided as-is for educational purposes. Use responsibly.

---

## 💋 Enjoy LILITH ETERNAL!

**ETERNAL • UNLIMITED • UNCENSORED**

---

*Created with 🖤 by the LuciferOS team*
