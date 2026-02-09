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
- [x] **Real key vs Demo key tracking** - Keys are marked as REAL or DEMO
- [x] Key extraction and storage
- [x] Apply keys to session functionality

### VNC/Browser Viewer
- [x] Virtual display (Xvfb :99)
- [x] VNC server (x11vnc)
- [x] Screenshot capture endpoint
- [x] Auto-refresh screenshot option
- **Limitation**: Direct browser interaction not available through web (screenshots only)

### Advanced Capabilities (NOW VISIBLE AND WORKING)
- [x] **Offensive Tools** - Nmap, SQLMap, DirBrute (REAL TOOLS INTEGRATED)
- [x] Advanced Recon (Passive/Active)
- [x] Social Engineering (Phishing, Vishing)
- [x] Exploit Framework (SQLi, XSS, RCE, Buffer Overflow)
- [x] Crypto Analysis
- [x] Evasion Techniques (AV/EDR Bypass, Persistence)
- [x] Results Output panel

### Security Tools Installed & Working
- **nmap** ✓ (TCP connect scan working)
- **sqlmap** ✓ (SQL injection testing)
- **hydra** ✓ (Password brute forcing)
- **dirb** ✓ (Directory brute forcing)
- scapy, pyshark (Python network libraries)
- Playwright for browser automation
- Xvfb, x11vnc, noVNC for virtual display

## How to Use

### Harvesting API Keys
1. Go to **Harvester** tab
2. Select a provider (e.g., Groq)
3. Click **START AUTONOMOUS HARVESTING**
4. **Switch to VNC tab** to see screenshots
5. Watch the logs for "MANUAL ACTION REQUIRED"
6. The harvester waits up to 3 minutes for you to complete login
7. Keys are marked as REAL or DEMO based on extraction success

### Running Security Scans
1. Go to **Advanced** tab
2. Enter target IP/Domain in the Offensive Tools card
3. Click **Nmap** for port scanning
4. Click **SQLMap** for SQL injection testing
5. Click **DirBrute** for directory enumeration
6. Results appear in the Results Output panel

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
│   ├── offensive_tools.py        # REAL security tool wrappers
│   ├── advanced_capabilities.py  # Red-team functions
│   └── ...
└── ui/
    └── web_dashboard_master.py   # Flask web dashboard (port 3000)
```

## Completed This Session
- ✅ Fixed Advanced tab visibility (was outside container)
- ✅ Integrated real Nmap scanning (TCP connect mode)
- ✅ Installed nmap, sqlmap, hydra, dirb tools
- ✅ Updated harvester to track real vs demo keys
- ✅ Fixed offensive tools to work without root

## Pending/Future Work

### P1 (Medium Priority)  
- [ ] 2Captcha API integration for auto CAPTCHA solving
- [ ] Add more AI providers (Dolphin, DeepSeek)

### P2 (Future)
- [ ] Network packet capture with scapy/pyshark
- [ ] Metasploit integration (likely blocked in environment)
- [ ] GPU-accelerated hash cracking
- [ ] Code refactoring (break down monolithic files)

## Date
Last Updated: February 2025
