# Deploying Lilith Companion

Lilith is a full-stack app: **FastAPI backend + React (Vite) frontend + MongoDB**. This guide covers three deployment paths in order of easiest → most control.

- [Path A — Deploy from Emergent (recommended)](#path-a--deploy-from-emergent-recommended)
- [Path B — Self-host with Docker Compose](#path-b--self-host-with-docker-compose)
- [Path C — Manual (bare VM: systemd + nginx)](#path-c--manual-bare-vm-systemd--nginx)

---

## Environment variables

Before any deploy, prepare these. **Bold** = required. The rest have working defaults.

### Backend (`backend/.env`)

| Var | Required | Notes |
|---|---|---|
| **`MONGO_URL`** | ✅ | e.g. `mongodb://localhost:27017` or `mongodb+srv://…` for Atlas |
| **`DB_NAME`** | ✅ | Any name, e.g. `luciferos` |
| **`EMERGENT_LLM_KEY`** | ✅ | Powers Claude Sonnet 4.5 chat. Get from Emergent → Profile → Universal Key |
| `EMERGENT_MODEL` |  | Default: `claude-sonnet-4-5-20250929` |
| `EMERGENT_PROVIDER` |  | Default: `anthropic` |
| **`ELEVENLABS_API_KEY`** | ✅ | ElevenLabs voice TTS. Get at https://elevenlabs.io → Profile → API Key |
| `ELEVENLABS_VOICE_ID` |  | Default female voice. Overridden per-session via the UI |
| **`HF_TOKEN`** | ✅ | Hugging Face token (Read scope). Powers image gen + face-swap + skeleton + CodeFormer. Get at https://huggingface.co/settings/tokens |
| `LILITH_IMAGE_SPACE` |  | Default: `Byron230686/lilith-image-forge` (change to your own fork) |
| `FACESWAP_SPACE` |  | Default: `felixrosberg/face-swap` |
| `POSE_OPENPOSE_SPACE` |  | Default: `SJTU-TES/OpenPose` |
| `CODEFORMER_SPACE` |  | Default: `sczhou/CodeFormer` |
| `LILITH_GALLERY_DIR` |  | Default: `/app/data/gallery` — persistent image storage |
| `LILITH_REF_DIR` |  | Default: `/app/data/references` |
| `LILITH_PRESETS_DIR` |  | Default: `/app/data/presets` |

### Frontend (`frontend/.env`)

| Var | Required | Notes |
|---|---|---|
| **`REACT_APP_BACKEND_URL`** | ✅ | Public URL of the backend (e.g. `https://api.mysite.com`). Do NOT include a trailing `/api` |

> ⚠️ The frontend calls the backend at `${REACT_APP_BACKEND_URL}/api/...`. In production, everything under `/api/*` on the backend URL must reach FastAPI on port 8001.

---

## Path A — Deploy from Emergent (recommended)

**5-minute deploy. Zero infrastructure.**

1. Open your app in Emergent.
2. Click **Deploy** in the chat input area.
3. Emergent provisions a subdomain, deploys the backend + frontend as one service, and provisions a MongoDB instance for you. The `MONGO_URL` and `EMERGENT_LLM_KEY` are auto-injected.
4. On the deployment settings screen, add the three secrets that are not auto-injected:
   - `ELEVENLABS_API_KEY`
   - `HF_TOKEN`
5. Click **Deploy**. First build takes ~5 min; subsequent deploys ~90 s.
6. Copy the public URL Emergent gives you. That's it — Lilith is live.

To update after code changes, just click Deploy again.

> 💡 Emergent hosts the app on its own infrastructure. If you're only using this for personal/prototype use, this is the simplest and cheapest path.

---

## Path B — Self-host with Docker Compose

**Best for VPS deploys (Hetzner, DigitalOcean, Linode). Full control, ~15 min.**

### 1. Get the code onto your server

Use **Save to Github** from Emergent's chat input to push the codebase to your own repo, then:

```bash
git clone https://github.com/<you>/lilith-companion.git
cd lilith-companion
```

### 2. Create `.env` files

```bash
cat > backend/.env <<'EOF'
MONGO_URL=mongodb://mongo:27017
DB_NAME=luciferos
EMERGENT_LLM_KEY=your-emergent-llm-key
ELEVENLABS_API_KEY=your-elevenlabs-key
HF_TOKEN=hf_your_token
EOF

cat > frontend/.env <<'EOF'
REACT_APP_BACKEND_URL=https://your-domain.com
EOF
```

### 3. Create `docker-compose.yml`

```yaml
services:
  mongo:
    image: mongo:7
    restart: unless-stopped
    volumes:
      - mongo_data:/data/db

  backend:
    build: ./backend
    restart: unless-stopped
    env_file: ./backend/.env
    volumes:
      - lilith_data:/app/data
    depends_on: [mongo]
    ports:
      - "127.0.0.1:8001:8001"

  frontend:
    build:
      context: ./frontend
      args:
        REACT_APP_BACKEND_URL: ${REACT_APP_BACKEND_URL}
    restart: unless-stopped
    ports:
      - "127.0.0.1:3000:3000"

volumes:
  mongo_data:
  lilith_data:
```

### 4. Backend Dockerfile (`backend/Dockerfile`)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libjpeg-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir emergentintegrations \
       --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
COPY . .
RUN mkdir -p /app/data/gallery /app/data/references /app/data/presets
EXPOSE 8001
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

### 5. Frontend Dockerfile (`frontend/Dockerfile`)

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
ARG REACT_APP_BACKEND_URL
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile
COPY . .
RUN yarn build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
```

Create `frontend/nginx.conf`:

```nginx
server {
  listen 3000;
  root /usr/share/nginx/html;
  location / {
    try_files $uri $uri/ /index.html;
  }
}
```

### 6. Reverse proxy (host-level nginx or Caddy)

Put nginx or Caddy in front, terminating TLS and routing:

- `https://your-domain.com/` → frontend `127.0.0.1:3000`
- `https://your-domain.com/api/*` → backend `127.0.0.1:8001`

Example with **Caddy** (`/etc/caddy/Caddyfile`):

```
your-domain.com {
    handle /api/* {
        reverse_proxy 127.0.0.1:8001
    }
    handle {
        reverse_proxy 127.0.0.1:3000
    }
}
```

Caddy handles Let's Encrypt automatically.

### 7. Launch

```bash
docker compose up -d --build
sudo systemctl reload caddy   # or nginx
```

Visit `https://your-domain.com`. Done.

### 8. Updates

```bash
git pull
docker compose up -d --build
```

Volumes persist Mongo and generated images across rebuilds.

---

## Path C — Manual (bare VM: systemd + nginx)

Skip Docker if you prefer. Ubuntu 22.04+ example.

### 1. System packages

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv nodejs npm nginx mongodb
sudo npm install -g yarn
```

### 2. Clone + install

```bash
cd /opt
sudo git clone https://github.com/<you>/lilith-companion.git
sudo chown -R $USER lilith-companion
cd lilith-companion

# Backend
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
deactivate

# Frontend
cd ../frontend
yarn install
REACT_APP_BACKEND_URL=https://your-domain.com yarn build
```

Fill in `backend/.env` and `frontend/.env` (see the Environment section).

### 3. systemd unit for backend

`/etc/systemd/system/lilith-backend.service`:

```ini
[Unit]
Description=Lilith FastAPI backend
After=network.target mongod.service

[Service]
Type=simple
User=lilith
WorkingDirectory=/opt/lilith-companion/backend
EnvironmentFile=/opt/lilith-companion/backend/.env
ExecStart=/opt/lilith-companion/backend/.venv/bin/uvicorn server:app --host 127.0.0.1 --port 8001
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo useradd -r -s /usr/sbin/nologin lilith
sudo chown -R lilith:lilith /opt/lilith-companion
sudo systemctl daemon-reload
sudo systemctl enable --now lilith-backend
```

### 4. nginx (`/etc/nginx/sites-available/lilith`)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Serve pre-built frontend
    root /opt/lilith-companion/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Streaming chat (SSE) — critical
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 3600s;
        chunked_transfer_encoding on;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/lilith /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d your-domain.com    # add HTTPS
```

### 5. Updates

```bash
cd /opt/lilith-companion
git pull
(cd backend && source .venv/bin/activate && pip install -r requirements.txt && deactivate)
(cd frontend && yarn install && REACT_APP_BACKEND_URL=https://your-domain.com yarn build)
sudo systemctl restart lilith-backend
```

---

## Post-deploy checks

Run these against your live URL to confirm everything works:

```bash
BASE=https://your-domain.com

# 1. Backend alive
curl -s $BASE/api/status | jq '.status, .chat.provider'

# 2. Voice list (should include preview_url per voice)
curl -s $BASE/api/voice/list | jq '.count'

# 3. Chat
curl -s -X POST $BASE/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"say hi"}' | jq '.response'

# 4. Streaming chat (should show event: chunk lines)
curl -sN -X POST $BASE/api/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{"message":"say hi in two sentences"}' | head -30

# 5. Presets seeded
curl -s $BASE/api/presets | jq '.count'   # should be ≥ 8

# 6. Image gen (takes 30-90s with CodeFormer)
curl -s -X POST $BASE/api/image/lilith \
  -H 'Content-Type: application/json' \
  -d '{"outfit":"black_lace_lingerie","use_enhance":true}' | jq '.provider, .used_enhance'
```

If step 4 doesn't stream, your reverse proxy is buffering — add `proxy_buffering off;` and `X-Accel-Buffering: no` allowed through your ingress.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Chat replies say "the line went quiet" | `EMERGENT_LLM_KEY` missing or out of credit. Top up at Emergent → Profile → Universal Key. |
| Voice preview button silent | Autoplay policy — click anywhere on the page first, or check `ELEVENLABS_API_KEY`. |
| Images fail with "Image generation failed" 503 | HF Space cold-started; wait 30 s and retry. If persistent, check `HF_TOKEN` scope (needs Read). |
| Face-Swap or CodeFormer never runs (`used_face_swap: false`) | Remote HF Space is in error state. Override via env: `FACESWAP_SPACE=someone-else/face-swap`. |
| Streaming chat looks like one big reveal (no typewriter) | Reverse proxy is buffering. See step 4 fix above. |
| Presets thumbnails don't show | The preset needs an image in the gallery to snapshot. Generate one first, then save a preset. |
| Disk fills up fast | `/app/data/gallery` grows unbounded. Add a cron job to trim: `find /app/data/gallery -mtime +30 -delete` |

---

## Backups

Just two things to back up:

1. **MongoDB** — `mongodump --uri="$MONGO_URL"` daily
2. **`/app/data/`** (or `lilith_data` docker volume) — the gallery, references, and preset snapshots

Everything else is code + env.
