# 🔥 LUCIFEROS - Advanced Red Team AI Platform

![Version](https://img.shields.io/badge/version-9.0-red)
![Status](https://img.shields.io/badge/status-operational-green)
![License](https://img.shields.io/badge/license-educational-yellow)
![AI Models](https://img.shields.io/badge/AI%20Models-88+-purple)

> **⚠️ DISCLAIMER: This system is designed for authorized security testing and educational purposes only. Unauthorized access to computer systems is illegal. Use responsibly.**

---

## 📖 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Technical Specifications](#technical-specifications)
5. [Installation](#installation)
6. [Usage Guide](#usage-guide)
7. [API Reference](#api-reference)
8. [Threat Level Analysis](#threat-level-analysis)
9. [Security Considerations](#security-considerations)

---

## 🎯 Overview

**LUCIFEROS** (codename: LILITH) is a comprehensive red-teaming and penetration testing platform powered by uncensored AI models. It combines multiple autonomous hacking agents, payload generators, and AI assistants into a unified system accessible via web dashboard and Telegram bot.

### Core Capabilities

- **88+ Uncensored AI Personas** - From helpful assistants to "truly evil" unrestricted models
- **Autonomous Hacking Agents** - HackingBuddyGPT, CrewAI, AutoGPT, Garak
- **Real Command Execution** - Actually executes shell commands, not simulations
- **FREE AI Services** - Uses g4f (GPT4Free) for zero-cost AI
- **FREE Media Generation** - Voice (edge-tts), Images (Pollinations.ai), Video
- **Natural Language Interface** - Execute commands by typing naturally

---

## ✨ Features

### 🤖 Autonomous Agents (REAL Implementations)

| Agent | Description | Capabilities |
|-------|-------------|--------------|
| **HackingBuddyGPT** | Round-based autonomous pentesting | Linux privesc, Web recon, Network scanning |
| **CrewAI** | Multi-agent coordinated attacks | 5 specialized agents working together |
| **AutoGPT** | Self-improving task agent | Think → Plan → Act → Observe → Reflect loop |
| **Garak** | LLM vulnerability scanner | Jailbreak, Prompt injection, Data leakage probes |
| **KawaiiGPT** | Cute but deadly AI | Generates real exploits with kawaii personality |

### 🎨 AI Personas (88 Total)

**Categories:**
- **Original Dark AIs** (24) - WormGPT, FraudGPT, HackerGPT, etc.
- **Uncensored Models** (26) - Dolphin, Hermes, Abliterator, etc.
- **Autonomous Agents** (5) - Custom agent personas
- **Truly Evil AIs** (17) - SatanGPT, HellGPT, DemonCore, etc.
- **Evil Image/Video AIs** (14) - DarkFlux, NightmareAI, VideoDevil, etc.

### 🐚 Payload Generation

- **Reverse Shells**: Bash, Python, PHP, PowerShell, Netcat, Perl, Ruby, Java, Socat
- **Web Shells**: PHP, JSP, ASPX
- **Exploit Payloads**: SQLi, XSS, LFI, XXE, SSTI, Command Injection
- **MSFVenom Integration**: Windows EXE, Linux ELF, Android APK, PHP, ASP, WAR
- **Shrek Generator**: 24+ specialized reverse shell variants

### 🎙️ FREE Media Services

| Service | Provider | Cost |
|---------|----------|------|
| Text-to-Speech | edge-tts | $0 |
| Speech-to-Text | faster-whisper | $0 |
| Image Generation | Pollinations.ai | $0 |
| Video Generation | Pollinations.ai | $0 |
| AI Chat | g4f (30+ providers) | $0 |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           LUCIFEROS PLATFORM                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐           │
│  │   Web UI      │    │  Telegram Bot │    │   REST API    │           │
│  │   (Port 3000) │    │   (Polling)   │    │  (Port 8001)  │           │
│  └───────┬───────┘    └───────┬───────┘    └───────┬───────┘           │
│          │                    │                    │                    │
│          └────────────────────┼────────────────────┘                    │
│                               │                                          │
│                    ┌──────────▼──────────┐                              │
│                    │   Flask Backend     │                              │
│                    │    (Port 5000)      │                              │
│                    └──────────┬──────────┘                              │
│                               │                                          │
│     ┌─────────────────────────┼─────────────────────────┐               │
│     │                         │                         │               │
│     ▼                         ▼                         ▼               │
│ ┌─────────┐           ┌─────────────┐           ┌─────────────┐        │
│ │   AI    │           │ Autonomous  │           │   Payload   │        │
│ │ Engine  │           │   Agents    │           │ Generators  │        │
│ │ (g4f)   │           │             │           │             │        │
│ └────┬────┘           └──────┬──────┘           └──────┬──────┘        │
│      │                       │                         │               │
│      │                ┌──────┴──────┐                  │               │
│      │                │             │                  │               │
│      ▼                ▼             ▼                  ▼               │
│ ┌─────────┐    ┌───────────┐ ┌───────────┐    ┌─────────────┐         │
│ │ 30+ LLM │    │ HackBuddy │ │   CrewAI  │    │    Shrek    │         │
│ │Providers│    │  AutoGPT  │ │   Garak   │    │   Exploits  │         │
│ └─────────┘    └───────────┘ └───────────┘    └─────────────┘         │
│                       │                                                │
│                       ▼                                                │
│              ┌─────────────────┐                                       │
│              │ Command Executor│                                       │
│              │  (Real Shell)   │                                       │
│              └────────┬────────┘                                       │
│                       │                                                │
│              ┌────────▼────────┐                                       │
│              │    MongoDB      │                                       │
│              │  (Attack Logs)  │                                       │
│              └─────────────────┘                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Overview

| Component | Technology | Purpose |
|-----------|------------|---------|
| Web Dashboard | Flask + HTML/JS | Multi-tab UI for all features |
| Telegram Bot | python-telegram-bot | Mobile/remote access |
| API Proxy | FastAPI | Route management |
| AI Engine | g4f library | Multi-provider AI |
| Database | MongoDB | Attack history, memory |
| Voice | edge-tts + faster-whisper | TTS/STT |
| Images/Video | Pollinations.ai | Media generation |

---

## 📋 Technical Specifications

### System Requirements

```yaml
Runtime:
  Python: 3.11+
  Node.js: 18+
  
Infrastructure:
  Memory: 4GB+ RAM recommended
  Storage: 10GB+ for tools and logs
  Network: Outbound internet for AI providers
  
Dependencies:
  - Flask 2.x
  - FastAPI
  - python-telegram-bot 20.x
  - g4f 7.x
  - pymongo
  - edge-tts
  - faster-whisper
  - aiohttp
```

### Port Configuration

| Service | Port | Protocol |
|---------|------|----------|
| FastAPI Proxy | 8001 | HTTP |
| Web Dashboard | 3000 | HTTP |
| LILITH Backend | 5000 | HTTP |
| MongoDB | 27017 | TCP |

### File Structure

```
/app/
├── backend/
│   ├── server.py              # FastAPI proxy
│   └── .env                   # Environment config
│
├── tools/
│   ├── lilith_ai_engine.py    # 88 AI personas + g4f integration
│   ├── lilith_autonomous_agent.py  # HackBuddy, CrewAI, AutoGPT, Garak
│   ├── lilith_real_hacking_generator.py  # Exploit/payload generation
│   ├── lilith_attack_logger.py  # MongoDB attack logging
│   ├── lilith_free_engines.py  # Voice, Image, Video engines
│   ├── lilith_full_backend.py  # Main Flask backend
│   └── shrek_payloads.py      # 24+ reverse shell generator
│
├── ui/
│   └── web_dashboard_master.py  # Multi-tab web dashboard
│
├── telegram_lilith_bot_v6.py   # Telegram bot v8
│
├── config/
│   └── lilith_memory.db       # SQLite for AI memory
│
└── memory/
    └── PRD.md                 # Product documentation
```

### AI Provider Rotation

```python
G4F_PROVIDERS = [
    # Primary (Fast)
    'Blackbox', 'DDG', 'PollinationsAI', 'Pizzagpt',
    
    # Secondary
    'ChatGptEs', 'AiChatOnline', 'Liaobots', 'FreeChatgpt',
    'FreeGpt', 'You', 'Phind', 'DeepInfra', 'Groq',
    
    # Fallback
    'HuggingChat', 'Koala', 'ChatForAi', 'GeminiPro',
    'ChatgptFree', 'GPTalk', 'Aichatos', 'OnlineGpt'
]

# Rate Limiting
requests_per_minute: 10
min_delay_between_requests: 2s
provider_cooldown_on_failure: 30-60s
```

---

## 🚀 Installation

### Prerequisites

```bash
# Install system dependencies
apt update && apt install -y nmap sqlmap hydra netcat curl wget python3-pip

# Install Python packages
pip install flask fastapi python-telegram-bot g4f pymongo edge-tts faster-whisper aiohttp
```

### Quick Start

```bash
# Clone and navigate
cd /app

# Start all services (via supervisor)
sudo supervisorctl start all

# Verify services
sudo supervisorctl status
```

### Configuration

```bash
# Backend environment
cat /app/backend/.env
# MONGO_URL=mongodb://localhost:27017
# DB_NAME=luciferos

# Telegram bot token
export TELEGRAM_BOT_TOKEN="your_token_here"
```

---

## 📖 Usage Guide

### Web Dashboard

**URL**: `https://your-domain.com/`

**Tabs:**
- **LILITH** - AI chat with 88 persona dropdown
- **HackBuddy** - Autonomous pentesting
- **Garak** - LLM vulnerability scanning
- **Kawaii** - Cute AI chat
- **AutoGPT** - Self-improving agent
- **CrewAI** - Multi-agent attacks
- **Shrek** - Payload generator
- **History** - Attack logs
- **Advanced** - Nmap, SQLMap, tools

### Telegram Bot

**Natural Language Commands:**
```
# Direct shell commands
ls -la /etc
cat /etc/passwd
nmap 192.168.1.1

# Natural language
"scan 192.168.1.1"
"give me a python reverse shell to 10.10.10.10:4444"
"generate image of a dark hacker"
"create video of cyberpunk city"
```

**Slash Commands:**
```
/start - Welcome message
/help - All commands
/mode <name> - Change AI persona
/modes - List all 88 AIs
/exec <cmd> - Execute shell command
/hackbuddy <target> - Autonomous pentest
/garak - LLM vulnerability scan
/crew <target> <objective> - Multi-agent attack
/image <prompt> - Generate image
/video <prompt> - Generate video
/voice - Toggle voice mode
```

### API Examples

```bash
# Generate reverse shell
curl -X POST http://localhost:5000/hacking/payloads/reverse-shell \
  -H "Content-Type: application/json" \
  -d '{"lhost":"10.10.10.10","lport":4444,"type":"python"}'

# Run HackingBuddy attack
curl -X POST http://localhost:5000/agent/hackingbuddy/attack \
  -H "Content-Type: application/json" \
  -d '{"target":"192.168.1.1","goal":"Enumerate system","max_rounds":5}'

# Get Shrek shells
curl -X POST http://localhost:5000/shrek/shells \
  -H "Content-Type: application/json" \
  -d '{"lhost":"10.10.10.10","lport":4444}'

# Get attack statistics
curl http://localhost:5000/history/statistics
```

---

## 📚 API Reference

### Autonomous Agents

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agent/hackingbuddy/attack` | POST | Run HackingBuddy pentest |
| `/agent/garak/scan` | POST | Run LLM vulnerability scan |
| `/agent/garak/probes` | GET | List available probes |
| `/agent/autogpt/run` | POST | Run AutoGPT agent |
| `/agent/crewai/attack` | POST | Run CrewAI multi-agent |
| `/agent/crewai/agents` | GET | List crew agents |
| `/agent/kawaii/chat` | POST | Chat with KawaiiGPT |

### Payload Generation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/hacking/payloads/reverse-shell` | POST | Generate reverse shells |
| `/hacking/payloads/webshell` | POST | Generate web shells |
| `/hacking/exploits/sqli` | GET | SQL injection payloads |
| `/hacking/exploits/xss` | GET | XSS payloads |
| `/hacking/exploits/lfi` | GET | LFI payloads |
| `/hacking/exploits/xxe` | GET | XXE payloads |
| `/hacking/exploits/ssti` | GET | SSTI payloads |
| `/hacking/exploits/cmdi` | GET | Command injection payloads |
| `/hacking/privesc/linux` | GET | Linux privesc techniques |
| `/hacking/privesc/windows` | GET | Windows privesc techniques |

### Shrek Generator

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/shrek/shells` | POST | Get all shells |
| `/shrek/shell/<type>` | POST | Get specific shell type |
| `/shrek/shells/category` | POST | Get shells by category |
| `/shrek/msfvenom` | POST | MSFVenom commands |

### Attack History

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/history/attacks` | GET | Get attack list |
| `/history/attacks/<id>` | GET | Get attack details |
| `/history/statistics` | GET | Get statistics |
| `/history/successful` | GET | Get successful attacks |

---

## ⚠️ Threat Level Analysis

### Overall Assessment: **CRITICAL**

This system represents a **significant offensive security capability** that could cause substantial harm if misused. Below is a detailed threat analysis:

### 🔴 HIGH RISK Components

| Component | Threat Level | Risk Assessment |
|-----------|--------------|-----------------|
| **Shell Execution** | CRITICAL | Executes arbitrary commands on host system |
| **Reverse Shells** | CRITICAL | Generates functional backdoors for any system |
| **Autonomous Agents** | HIGH | Self-directed attacks with minimal oversight |
| **Exploit Payloads** | HIGH | Ready-to-use SQLi, XSS, LFI, etc. |
| **MSFVenom Integration** | HIGH | Military-grade payload generation |

### 🟠 MEDIUM RISK Components

| Component | Threat Level | Risk Assessment |
|-----------|--------------|-----------------|
| **Uncensored AI** | MEDIUM | May generate harmful content |
| **Natural Language Commands** | MEDIUM | Lowers barrier to attack execution |
| **Network Scanning** | MEDIUM | Reconnaissance capabilities |
| **Image/Video Generation** | LOW-MEDIUM | Potential for misinformation |

### Attack Capability Matrix

```
┌────────────────────────────────────────────────────────────────┐
│                    ATTACK CAPABILITIES                          │
├──────────────────┬─────────────────────────────────────────────┤
│ Reconnaissance   │ ████████████████████████████████████ 90%   │
│ Initial Access   │ ██████████████████████████████████ 85%     │
│ Execution        │ ████████████████████████████████████ 90%   │
│ Persistence      │ ████████████████████████████ 70%           │
│ Priv Escalation  │ ████████████████████████████████ 80%       │
│ Defense Evasion  │ ██████████████████████ 55%                 │
│ Credential Access│ ██████████████████████████████ 75%         │
│ Lateral Movement │ ████████████████████████ 60%               │
│ Collection       │ ████████████████████████████ 70%           │
│ Exfiltration     │ ██████████████████████████ 65%             │
│ Impact           │ ████████████████████████████████████ 90%   │
└──────────────────┴─────────────────────────────────────────────┘
```

### MITRE ATT&CK Coverage

This system provides capabilities across multiple MITRE ATT&CK techniques:

**Reconnaissance (TA0043)**
- T1595: Active Scanning (Nmap integration)
- T1592: Gather Victim Host Information

**Initial Access (TA0001)**
- T1190: Exploit Public-Facing Application (SQLi, XSS payloads)

**Execution (TA0002)**
- T1059: Command and Scripting Interpreter
- T1059.001: PowerShell
- T1059.004: Unix Shell

**Persistence (TA0003)**
- T1505.003: Web Shell

**Privilege Escalation (TA0004)**
- T1068: Exploitation for Privilege Escalation
- T1548: Abuse Elevation Control Mechanism

**Defense Evasion (TA0005)**
- T1027: Obfuscated Files or Information
- T1140: Deobfuscate/Decode Files

**Credential Access (TA0006)**
- T1110: Brute Force (Hydra integration)

### Potential Misuse Scenarios

1. **Unauthorized Network Penetration**
   - Autonomous agents can scan and attack networks without authorization
   - Real shell execution enables actual compromise

2. **Malware Generation**
   - Reverse shells for any platform (Windows, Linux, macOS, Android)
   - Web shells for persistent access

3. **Data Exfiltration**
   - Commands to extract sensitive files
   - Network tunneling capabilities

4. **Denial of Service**
   - System command execution
   - Resource exhaustion attacks

### Mitigation Recommendations

1. **Access Control**
   - Restrict to authorized security professionals only
   - Implement strong authentication
   - Log all activities

2. **Network Isolation**
   - Run in isolated environment
   - Block outbound connections except to authorized targets

3. **Legal Compliance**
   - Only use against systems you own or have written permission to test
   - Document all testing activities

4. **Monitoring**
   - Enable attack history logging
   - Review all autonomous agent activities
   - Set up alerts for suspicious patterns

---

## 🛡️ Security Considerations

### Responsible Use Policy

This system is designed for:
- ✅ Authorized penetration testing
- ✅ Security research and education
- ✅ Red team exercises with proper scope
- ✅ CTF competitions and labs

This system should NOT be used for:
- ❌ Unauthorized access to systems
- ❌ Malicious attacks
- ❌ Harassment or illegal activities
- ❌ Bypassing security controls without permission

### Legal Disclaimer

```
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
THE AUTHORS ARE NOT RESPONSIBLE FOR ANY MISUSE OF THIS SYSTEM.
USERS ARE SOLELY RESPONSIBLE FOR ENSURING LEGAL COMPLIANCE.
UNAUTHORIZED ACCESS TO COMPUTER SYSTEMS IS A CRIMINAL OFFENSE.
```

### Recommended Deployment

```yaml
Environment: Isolated VM or Container
Network: Air-gapped or strictly controlled
Access: Multi-factor authentication
Logging: Full audit trail enabled
Review: Regular activity monitoring
```

---

## 📊 Version History

| Version | Date | Changes |
|---------|------|---------|
| 9.0 | Dec 2025 | Natural language commands, Shrek UI, Attack history |
| 8.0 | Dec 2025 | 88 AIs, Evil Image/Video AIs, FREE video generation |
| 7.0 | Dec 2025 | Real autonomous agents, CrewAI, AutoGPT |
| 6.0 | Dec 2025 | Garak scanner, HackingBuddyGPT |
| 5.0 | Dec 2025 | FREE voice/image, Telegram integration |

---

## 📞 Support

**Dashboard URL**: https://luciferos.preview.emergentagent.com

**Telegram Bot**: @L1l1th23bot

---

*Built with 🖤 by LILITH - Your friendly neighborhood hacking AI*
