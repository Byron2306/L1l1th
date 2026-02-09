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
- ✅ API Key Harvester UI integrated
- ✅ Service management via supervisor
- ✅ Route prefix fix (changed `/api/` to `/_dash/` to avoid Emergent proxy conflicts)
- ✅ FastAPI proxy layer for platform compatibility

### In Progress
- ⏳ Preview URL connectivity (platform-level issue)
- ⏳ AI provider API keys needed for chat functionality

### Blocked/Pending
- ❌ Core AI chat requires valid API keys
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
- `/_dash/backend/status` - Backend health check
- `/_dash/openclaw/skills` - OpenClaw skills list

### Backend APIs (port 5000)
- `/status` - Backend status
- `/chat` - AI chat endpoint
- `/learning/*` - Learning endpoints
- `/coding_agent/*` - Coding agent endpoints
- `/openclaw/*` - OpenClaw integration

## Known Issues
1. Preview URL shows "Unavailable" - platform connectivity issue
2. AI providers have invalid/expired API keys
3. Advanced capabilities are placeholder stubs

## Next Steps
1. Resolve preview URL connectivity
2. Use API Key Harvester to obtain valid keys
3. Test AI chat functionality
4. Implement advanced red-teaming capabilities

## Technical Notes
- Changed API routes from `/api/` to `/_dash/` because Emergent platform routes `/api/*` to port 8001
- Flask dashboard uses threaded mode for concurrent requests
- Services managed via Node.js launcher + supervisor
