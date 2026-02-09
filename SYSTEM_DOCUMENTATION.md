# LILITH / LuciferOS System Documentation

## System Overview

**LILITH** is an autonomous AI agent integrated into the LuciferOS red team platform. The system now includes:

### ✅ Core Components (OPERATIONAL)

1. **LILITH Backend** - Flask-based AI agent (Port 5000)
2. **Web Dashboard** - Real-time command center (Port 8080)
3. **OpenClaw Integration** - AI assistant framework
4. **API Key Generator** - Scans for working free providers
5. **API Key Harvester** - Autonomous account creation and key harvesting
6. **Self-Healing API System** - Automatically harvests new keys when providers fail

---

## Quick Start

### Start All Services

```bash
# Start backend
cd /app && python3 tools/lilith_full_backend.py &

# Start dashboard  
cd /app && python3 ui/web_dashboard.py &

# Run system tests
bash /app/test_lilith_system.sh
```

### Access Points

- **Backend API**: http://127.0.0.1:5000
- **Web Dashboard**: http://127.0.0.1:8080
- **Status Check**: http://127.0.0.1:5000/status

---

## API Key Management

### Automatic Key Generation

LILITH can autonomously generate API keys when providers fail:

```bash
# Scan for working providers
cd /app/tools && python3 api_key_generator.py

# Harvest keys automatically (requires browser)
cd /app/tools && python3 api_key_harvester.py
```

### Autonomous Harvesting Features

The API Key Harvester can:

1. **Create Temporary Email Accounts**
   - Uses GuerrillaMail or 10MinuteMail
   - No manual intervention needed
   - Automatically reads verification emails

2. **Automate Signup Process**
   - Fills forms automatically
   - Handles CAPTCHAs when possible
   - Completes email verification

3. **Extract API Keys**
   - Navigates to API settings
   - Generates new keys
   - Saves to configuration automatically

### Supported Providers

- **Groq** - Fast, free tier with 70B models
- **HuggingFace** - Free inference endpoints
- **Together.ai** - $25 free credits on signup
- **OpenRouter** - Free models available

### Manual Configuration

Edit `/app/config/lucifera.conf`:

```ini
[lilith]
groq_api_key = YOUR_GROQ_KEY
hf_token = YOUR_HF_TOKEN
together_api_key = YOUR_TOGETHER_KEY
```

---

## API Endpoints

### Core Endpoints

```bash
# System Status
curl http://127.0.0.1:5000/status

# Chat with LILITH
curl -X POST http://127.0.0.1:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello LILITH"}'

# OpenClaw Skills
curl http://127.0.0.1:5000/openclaw/redteam-skills

# Target Analysis
curl -X POST http://127.0.0.1:5000/analyze_target \
  -H "Content-Type: application/json" \
  -d '{"target": "example.com"}'

# Attack Recommendations
curl -X POST http://127.0.0.1:5000/recommend_attack \
  -H "Content-Type: application/json" \
  -d '{"target": "example.com", "context": "web application"}'
```

### Red Team Endpoints

```bash
# Deploy Malware
curl -X POST http://127.0.0.1:5000/deploy_malware \
  -H "Content-Type: application/json" \
  -d '{"type": "virus", "target": "192.168.1.100"}'

# Advanced Attacks
curl -X POST http://127.0.0.1:5000/deploy_advanced_attack \
  -H "Content-Type: application/json" \
  -d '{"attack_type": "availability", "target": "example.com"}'

# Autonomous Mode
curl -X POST http://127.0.0.1:5000/autogpt_loop \
  -H "Content-Type: application/json" \
  -d '{"objective": "Compromise target system", "max_iterations": 10}'
```

---

## OpenClaw Integration

OpenClaw provides additional AI assistant capabilities:

### Available Skills

- **lilith** - Main LILITH agent
- **coding-agent** - Code generation and analysis
- **browser-controller** - Web automation
- **github** - GitHub integration
- **discord/slack** - Communication platforms

### Using OpenClaw

```bash
# Navigate to OpenClaw directory
cd /app/openclaw

# Run OpenClaw gateway
node openclaw.mjs gateway --dev --port 3000

# Access UI (if available)
pnpm dev
```

---

## Self-Healing API System

LILITH automatically monitors API health and harvests new keys when needed:

### How It Works

1. **Monitors** all AI providers every 5 minutes
2. **Detects** when providers fail (5 consecutive failures)
3. **Triggers** autonomous key harvesting
4. **Harvests** new API keys using browser automation
5. **Updates** configuration automatically
6. **Reloads** providers with new keys

### Configuration

The self-healing system runs automatically in the background. Adjust settings in `/app/tools/self_healing_api.py`:

```python
self.failure_threshold = 5  # Failures before auto-harvest
self.harvest_cooldown = 3600  # 1 hour between harvest attempts
```

---

## Browser Automation Features

LILITH uses Playwright for advanced browser control:

### Capabilities

- **Account Creation** - Automated signup flows
- **Email Management** - Temporary email handling
- **Form Filling** - Intelligent form completion
- **Link Extraction** - Email verification links
- **Screenshot Capture** - Visual debugging
- **Session Management** - Cookie/token handling

### Running Harvester

```bash
# Semi-automatic (browser visible for debugging)
cd /app/tools
python3 api_key_harvester.py

# Fully automatic (headless mode)
python3 << 'EOF'
from api_key_harvester import APIKeyHarvester

harvester = APIKeyHarvester()
harvester.start_browser(headless=True)
harvester.run_harvest_campaign(['groq', 'huggingface'])
harvester.close_browser()
EOF
```

---

## Troubleshooting

### Backend Not Starting

```bash
# Check logs
tail -f /app/backend_err.log

# Restart backend
pkill -f lilith_full_backend
cd /app && python3 tools/lilith_full_backend.py &
```

### Dashboard Not Loading

```bash
# Check dashboard logs  
tail -f /app/dashboard_err.log

# Restart dashboard
pkill -f web_dashboard
cd /app && python3 ui/web_dashboard.py &
```

### AI Providers Failing

```bash
# Check provider status
curl http://127.0.0.1:5000/status | jq '.ai_providers'

# Run API key generator
cd /app/tools && python3 api_key_generator.py

# Trigger manual harvest
cd /app/tools && python3 api_key_harvester.py
```

### OpenClaw Issues

```bash
# Reinstall dependencies
cd /app/openclaw && pnpm install

# Check OpenClaw availability
curl http://127.0.0.1:5000/openclaw/redteam-skills
```

---

## Security Notes

⚠️ **IMPORTANT**: This platform is for AUTHORIZED security testing only.

### Required:
- Written authorization from system/infrastructure owner
- Defined scope and timeframe
- Explicit list of permitted targets
- Legal review by organization counsel

### Prohibited:
- Unauthorized access to systems
- Attacks on systems without permission
- Illegal activities
- Violations of computer fraud laws

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    LILITH SYSTEM                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐      ┌──────────────┐               │
│  │   Backend    │◄────►│  Dashboard   │               │
│  │  (Port 5000) │      │  (Port 8080) │               │
│  └──────┬───────┘      └──────────────┘               │
│         │                                              │
│         ├─► AI Provider Manager                        │
│         │   ├─► Groq                                   │
│         │   ├─► HuggingFace                            │
│         │   ├─► Together.ai                            │
│         │   └─► OpenRouter                             │
│         │                                              │
│         ├─► Self-Healing System                        │
│         │   ├─► Health Monitor                         │
│         │   └─► Auto Harvester                         │
│         │                                              │
│         ├─► API Key Harvester                          │
│         │   ├─► Temp Email Manager                     │
│         │   ├─► Browser Automation                     │
│         │   └─► Key Extraction                         │
│         │                                              │
│         └─► OpenClaw Integration                       │
│             ├─► Skills Engine                          │
│             ├─► Browser Controller                     │
│             └─► Autonomous Agent                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Configuration Files

- `/app/config/lucifera.conf` - Main configuration
- `/app/config/harvested_keys.json` - Harvested API keys (auto-generated)
- `/tmp/api_scan_results.json` - Provider scan results

---

## Logs

- `/app/backend_out.log` - Backend stdout
- `/app/backend_err.log` - Backend errors
- `/app/dashboard_out.log` - Dashboard stdout
- `/app/dashboard_err.log` - Dashboard errors
- `/tmp/ollama.log` - Ollama service logs

---

## Next Steps

1. **Get Working API Keys**
   ```bash
   cd /app/tools && python3 api_key_generator.py
   cd /app/tools && python3 api_key_harvester.py
   ```

2. **Explore Dashboard**
   - Open http://127.0.0.1:8080 in browser
   - Test chat functionality
   - Run attack simulations

3. **Test API Endpoints**
   ```bash
   bash /app/test_lilith_system.sh
   ```

4. **Enable Self-Healing**
   - System automatically enabled on backend start
   - Monitor with: `curl http://127.0.0.1:5000/status`

---

Built for legitimate security testing. Use responsibly and legally.
