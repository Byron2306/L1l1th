# LuciferOS - Red Team Platform

## Overview
LuciferOS is a comprehensive red-teaming platform featuring an AI attack assistant (LILITH), autonomous API key harvesting, and multiple offensive security capabilities.

## What's Been Implemented

### Core Features
- [x] Web Dashboard with multiple tabs
- [x] AI Chat Interface (LILITH)
- [x] Attack mode selection and execution
- [x] System monitoring and live logs

### API Key Harvester (NEW Hybrid Mode)
**MANUAL MODE (Recommended)**
- [x] "Open Provider Website" - Opens signup in YOUR browser
- [x] "Keys Page" - Direct link to API keys page  
- [x] Paste and save your API key manually
- [x] Keys marked as REAL/verified

**AUTO MODE**
- [x] Server-side Playwright automation
- [x] Temp email service integration
- [x] VNC tab for monitoring

**Providers Supported:**
- Groq, HuggingFace, Together.ai, Mistral, OpenRouter, Cerebras, DeepInfra, SambaNova, Fireworks
- **NEW: Dolphin (uncensored), DeepSeek (coding/reasoning)**

### Advanced Capabilities (FULLY WORKING)
**Offensive Tools:**
- [x] Nmap - Real port scanning (TCP connect)
- [x] SQLMap - SQL injection testing
- [x] DirBrute - Directory enumeration

**Network Capture (NEW):**
- [x] Packet capture with filters
- [x] ARP Scanner for network discovery
- [x] Payload Generator (reverse shells)

**Other:**
- [x] Advanced Recon (Passive/Active)
- [x] Social Engineering (Phishing, Vishing)
- [x] Exploit Framework
- [x] Crypto Analysis (hash identification)
- [x] Evasion Techniques

### Security Tools Installed
- nmap, sqlmap, hydra, john, dirb
- scapy, pyshark (Python network libraries)
- Playwright for browser automation

## How to Use

### Harvesting API Keys (Manual Mode - RECOMMENDED)
1. Go to **Harvester** tab
2. Select a provider (e.g., Groq)
3. Click **"OPEN PROVIDER WEBSITE"** - Opens in YOUR browser
4. Complete signup, login, solve any CAPTCHAs
5. Go to Keys page, create a new API key
6. Copy the key and paste it in the input field
7. Click **"SAVE API KEY"**
8. Click **"APPLY KEYS TO SESSION"** to activate

### Running Security Scans
1. Go to **Advanced** tab
2. Enter target in Offensive Tools card
3. Click **Nmap**, **SQLMap**, or **DirBrute**
4. Results appear in Results Output panel

### Network Capture
1. Go to **Advanced** tab
2. In Network Capture card:
   - Set filter (e.g., "tcp port 80")
   - Set packet count
   - Click **Start**
3. Use **ARP Scanner** for network discovery
4. Use **Payload Generator** for reverse shells

## Architecture
```
/app/
├── tools/
│   ├── playwright_harvester.py   # Browser automation
│   ├── temp_email_service.py     # Multi-provider temp email
│   ├── offensive_tools.py        # Nmap, SQLMap wrappers
│   ├── network_capture.py        # Packet capture, ARP scan
│   └── ...
└── ui/
    └── web_dashboard_master.py   # Dashboard (port 3000)
```

## Pending/Future Work

### P2 (Future)
- [ ] Metasploit integration (blocked - requires installation)
- [ ] GPU hash cracking (requires GPU)
- [ ] Code refactoring

## Date
Last Updated: February 2025
