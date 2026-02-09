# LuciferOS - Product Requirements Document

## Original Problem Statement
Build a complex red-teaming platform called "LuciferOS" with:
- Web dashboard for LILITH AI Attack Assistant
- Backend services for AI-powered security testing
- API key harvesting system
- Integration with OpenClaw framework
- 15+ advanced red-teaming capabilities

## Current Architecture

### Services
- **Port 3000**: Flask Web Dashboard (`ui/web_dashboard_master.py`)
- **Port 5000**: LILITH Backend (`tools/lilith_full_backend.py`)  
- **Port 8001**: FastAPI Proxy (`backend/server.py`)

### Key Files
- `/app/ui/web_dashboard_master.py` - Main dashboard UI
- `/app/tools/lilith_full_backend.py` - Core backend logic
- `/app/tools/api_key_harvester.py` - API key automation
- `/app/tools/harvest_integration.py` - Harvester backend endpoints
- `/app/frontend/start_dashboard.js` - Service launcher

## What's Been Implemented

### Completed (Feb 9, 2026)
- ✅ Dashboard UI with all tabs (LILITH AI, Progress, Browser, Recon, Payload, Coding, Learning, Memory, Harvester)
- ✅ Backend services running and responding
- ✅ API Key Harvester UI with 10 providers:
  - Groq, HuggingFace, Together.ai, Mistral, Venice.ai
  - DeepInfra, OpenRouter, Cerebras, SambaNova, Fireworks.ai
- ✅ "Apply Keys to Session" button - loads harvested keys into running session
- ✅ "Restart Backend" button - restarts backend to reload providers
- ✅ Harvested Keys Database display in UI
- ✅ Dynamic API key addition endpoint (`/api/keys/add`)
- ✅ Service management via supervisor
- ✅ Route prefix fix (changed `/api/` to `/_dash/` to avoid Emergent proxy conflicts)

### In Progress
- ⏳ Preview URL connectivity (platform-level issue - session went idle)

### Blocked/Pending
- ❌ Real browser automation for actual key harvesting (currently simulated)
- ❌ 15 advanced capabilities are stubs (not implemented)

## API Endpoints

### Dashboard APIs (`/_dash/`)
- `/_dash/status` - System status
- `/_dash/ai/chat` - Chat with LILITH
- `/_dash/recon/start` - Start reconnaissance
- `/_dash/payload/generate` - Generate payloads
- `/_dash/learning/stats` - Learning statistics
- `/_dash/coding/status` - Coding agent status
- `/_dash/memory/save` - Save memory
- `/_dash/memory/recall` - Recall memory
- `/_dash/harvest/start` - Start API harvesting
- `/_dash/harvest/status` - Harvesting status
- `/_dash/harvest/keys` - List harvested keys
- `/_dash/harvest/apply` - Apply keys to session
- `/_dash/system/restart` - Restart backend
- `/_dash/backend/status` - Backend health check
- `/_dash/openclaw/skills` - OpenClaw skills list

### Backend APIs (port 5000)
- `/status` - Backend status
- `/chat` - AI chat endpoint
- `/api/keys/add` - Add API key dynamically
- `/reset-api-keys` - Reset and regenerate keys
- `/learning/*` - Learning endpoints
- `/coding_agent/*` - Coding agent endpoints
- `/openclaw/*` - OpenClaw integration

## Supported AI Providers (via Harvester)
1. Groq - Fast, Free, 70B Llama models
2. HuggingFace - Free, Unlimited  
3. Together.ai - $25 free credits
4. Mistral AI - Free tier available
5. Venice.ai - Uncensored models
6. DeepInfra - Free credits
7. OpenRouter - Multi-model access
8. Cerebras - Ultra-fast inference
9. SambaNova - Enterprise-grade
10. Fireworks.ai - Fast inference

## Known Issues
1. Preview URL shows "Unavailable" - platform went idle
2. AI providers have invalid/expired API keys (need real harvesting)
3. Advanced capabilities are placeholder stubs

## Next Steps
1. Resume session to restore preview URL
2. Run API Key Harvester for each provider
3. Apply harvested keys to activate AI chat
4. Implement real browser automation with Playwright
5. Implement advanced red-teaming capabilities

## Technical Notes
- Changed API routes from `/api/` to `/_dash/` because Emergent platform routes `/api/*` to port 8001
- Flask dashboard uses threaded mode for concurrent requests
- Services managed via Node.js launcher + supervisor
- Harvested keys stored in `/app/config/harvested_keys.json`
