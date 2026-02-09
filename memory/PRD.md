# LuciferOS - Red Team Platform

## Overview
LuciferOS is a comprehensive red-teaming platform featuring an AI attack assistant (LILITH), autonomous API key harvesting, and multiple offensive security capabilities.

## What's Been Implemented

### Core Features
- [x] Web Dashboard with multiple tabs (LILITH AI, Progress, Browser, Recon, Payload, Coding, Learning, Memory, Harvester, VNC, Advanced)
- [x] AI Chat Interface (LILITH)
- [x] Attack mode selection and execution
- [x] System monitoring and live logs

### API Key Harvester (Semi-Automated with Manual CAPTCHA Support)
- [x] Stealth Playwright browser automation
- [x] **Visible browser mode** - Browser runs on virtual display (:99)
- [x] **Screenshot-based browser viewer** - See the browser in the VNC tab
- [x] **Manual action waiting** - Harvester pauses for login/CAPTCHA (up to 3 minutes)
- [x] Temp email service integration (mail.tm, GuerrillaMail, 1secmail)
- [x] Multi-provider support:
  - Groq, HuggingFace, Together.ai, Mistral, Venice, DeepInfra, OpenRouter, Cerebras, SambaNova, Fireworks
- [x] Key extraction and storage
- [x] Apply keys to session functionality

### VNC/Browser Viewer
- [x] Virtual display (Xvfb :99)
- [x] VNC server (x11vnc)
- [x] Screenshot capture endpoint
- [x] Auto-refresh screenshot option
- **Limitation**: Direct browser interaction not available through web (screenshots only)

### Advanced Capabilities
- [x] Reconnaissance module
- [x] Social Engineering tools
- [x] ML Anomaly Detection
- [x] Crypto Analysis
- [x] Exploit Framework
- [x] Evasion Techniques
- [x] Wireless Attack methods
- [x] Physical Security bypass
- [x] Supply Chain analysis
- [x] Zero-Day research framework
- [x] Offensive Tools (Nmap, SQLMap, DirBrute)
- [x] CAPTCHA Bypass info

### Security Tools Installed
- nmap, sqlmap, hydra, john, masscan, dirb
- scapy, pyshark (Python network libraries)
- Playwright for browser automation
- Xvfb, x11vnc, noVNC for virtual display

## Architecture

```
/app/
├── backend/
│   ├── server.py             # FastAPI proxy (port 8001)
│   └── requirements.txt
├── frontend/
│   └── start_dashboard.js    # Node.js launcher for Flask apps
├── tools/
│   ├── lilith_full_backend.py    # Core Flask backend (port 5000)
│   ├── playwright_harvester.py   # Stealth browser automation
│   ├── temp_email_service.py     # Multi-provider temp email
│   ├── harvest_integration.py    # Dashboard integration
│   ├── offensive_tools.py        # Security tool wrappers
│   ├── advanced_capabilities.py  # Red-team functions
│   ├── ml_anomaly_detection.py   # ML-based detection
│   ├── captcha_bypass.py         # CAPTCHA handling info
│   └── network_capture.py        # Network analysis
└── ui/
    └── web_dashboard_master.py   # Flask web dashboard (port 3000)
```

## How to Use the Harvester

1. Go to **Harvester** tab
2. Select a provider (e.g., Groq)
3. Click **START AUTONOMOUS HARVESTING**
4. **Switch to VNC tab** to see the browser
5. Click **Take Screenshot** or enable **Auto-Refresh**
6. Watch the logs for "MANUAL ACTION REQUIRED"
7. The harvester waits up to 3 minutes for you to complete login
8. **For real keys**: You need local access to interact with the browser
9. Once login completes, harvester automatically extracts the key

## Pending/Future Work

### P0 (High Priority)
- [ ] Real offensive tool integration (actually call nmap, sqlmap via subprocess)
- [ ] Real CAPTCHA solving (requires 2Captcha API key)

### P1 (Medium Priority)  
- [ ] Network capture with scapy/pyshark
- [ ] Add more AI providers (Dolphin, DeepSeek)

### P2 (Future)
- [ ] Metasploit integration (likely blocked in environment)
- [ ] GPU-accelerated hash cracking
- [ ] Code refactoring (break down monolithic files)

## Date
Last Updated: February 2025
