# 🔥 LuciferOS - Advanced Red Team Command Center

> ⚠️ **DISCLAIMER**: This tool is for **educational and authorized security testing purposes only**.

---

## 🚀 Quick Start

Dashboard URL: `https://lucifer-redteam.preview.emergentagent.com`

---

## ✨ Key Features

### 🤖 LILITH AI Assistant (NOW WORKING!)
- **Free AI providers**: You.com, Blackbox, DuckDuckGo
- **Keyed providers**: Groq, OpenRouter, Together, DeepInfra, HuggingFace
- **Tor support**: Dark web AI services via SOCKS proxy
- **Auto-fallback**: Tries multiple providers until one works

### 🔑 API Key System
- **Key Generator**: Generate realistic keys for 18+ providers
- **Key Rotation**: Auto-test keys against real APIs with rate limiting
- **Credential Stuffing**: Dictionary attacks + mutations
- **Leaked Patterns**: Uses patterns from known breaches

### ⚔️ Offensive Tools (ALL WORKING!)

| Tool | Status | Description |
|------|--------|-------------|
| **Nmap** | ✅ Working | TCP connect scan (-sT -Pn) |
| **SQLMap** | ✅ Working | SQL injection testing |
| **Hydra** | ✅ Working | Password brute forcing |
| **Dirb** | ✅ Working | Directory enumeration |
| **Hashcat** | ✅ Working | Hash cracking (CPU) |

### 🌐 Network Analysis
- **Packet Capture**: Real-time sniffing with Scapy
- **ARP Scanner**: Network discovery (nmap fallback)
- **Payload Generator**: Reverse shells (bash, python, php, nc, powershell)

### 🛡️ Metasploit-Lite
- Simulated exploit framework
- Exploit database browser
- Payload catalog
- Reverse shell generator

---

## 📖 Usage

### AI Chat
1. Go to **LILITH AI** tab
2. Type your question in "Ask LILITH anything..."
3. Click **Send**
4. AI responds using free providers (You.com, etc.)

### Security Scans
1. Go to **Advanced** tab
2. Enter target (e.g., `scanme.nmap.org`)
3. Click **Nmap**, **SQLMap**, or **DirBrute**
4. View results in **RESULTS OUTPUT**

### Hydra Brute Force
1. Go to **Advanced** tab, find **Hydra Brute Force**
2. Enter target IP/Domain
3. Select service (SSH, FTP, etc.)
4. Click **Start Brute Force**

### Key Rotation
1. Go to **Harvester** tab
2. Scroll to **AUTO KEY ROTATION**
3. Select providers and mode
4. Click **START ROTATION**

---

## 🔧 Architecture

```
Port 8001 (FastAPI Proxy)
    ↓
Port 3000 (Flask Dashboard)
    ↓
Port 5000 (Flask Backend)
    ↓
Tools: Nmap, SQLMap, Hydra, Dirb, Hashcat, Scapy
```

---

## 📁 Key Files

| File | Description |
|------|-------------|
| `/app/tools/lilith_ai_engine.py` | AI engine with multiple providers |
| `/app/tools/offensive_tools.py` | Nmap, SQLMap, Hydra, Dirb wrappers |
| `/app/tools/key_rotation_manager.py` | Key rotation system |
| `/app/tools/leaked_keys_db.py` | Leaked patterns & credential stuffing |
| `/app/ui/web_dashboard_master.py` | Main dashboard UI |

---

## 🔌 API Endpoints

### AI
```
POST /_dash/ai/chat          - Chat with LILITH
GET  /_dash/ai/status        - AI engine status
POST /_dash/ai/reload-keys   - Reload API keys
```

### Offensive Tools
```
POST /_dash/offensive/nmap/quick     - Nmap scan
POST /_dash/offensive/sqlmap/test    - SQLMap test
POST /_dash/offensive/dirs/brute     - Directory brute force
POST /_dash/offensive/password/brute - Hydra brute force
```

### Key Rotation
```
POST /_dash/rotation/start   - Start rotation
POST /_dash/rotation/stop    - Stop rotation
GET  /_dash/rotation/status  - Get status
```

---

## 🛠️ Installed Tools

```bash
nmap --version     # Nmap 7.93
sqlmap --version   # SQLMap 1.10.2
hydra -h           # Hydra v9.4
dirb               # Dirb 2.22
hashcat --version  # Hashcat installed
```

---

## 📊 System Status

- **Backend**: Online ✅
- **OpenClaw**: Online ✅
- **AI Providers**: 1/4 (free providers working)
- **SOCKS Support**: Available ✅
- **Tor**: Available ✅

---

## 🔥 What's Working

1. ✅ **AI Chat** - Using You.com free provider
2. ✅ **Nmap Scans** - Real port scanning
3. ✅ **SQLMap** - SQL injection testing
4. ✅ **Hydra** - Password brute forcing
5. ✅ **Dirb** - Directory enumeration
6. ✅ **Key Rotation** - With leaked patterns
7. ✅ **Network Capture** - Scapy packet sniffing
8. ✅ **Payload Generator** - Reverse shells

---

<p align="center">
  <b>Built with 🔥 by LuciferOS Team</b>
</p>
