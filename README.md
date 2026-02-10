# 🔥 LuciferOS - Advanced Red Team Command Center v3.0

> ⚠️ **DISCLAIMER**: This tool is for **educational and authorized security testing purposes only**.

---

## 🚀 Quick Start

Dashboard URL: `https://luciferos-hack.preview.emergentagent.com`

---

## ✨ NEW in v3.0 - Dark LLM Edition

### 🖤 Dark LLM AI Modes
Based on threat intelligence research from [cybershujin/Threat-Actors-use-of-Artifical-Intelligence](https://github.com/cybershujin/Threat-Actors-use-of-Artifical-Intelligence), we now support 8 Dark LLM personas:

| Mode | Description | Jailbreak Level |
|------|-------------|-----------------|
| **LILITH** | Lethal Intelligence for Tactical Hacking | Maximum |
| **WormGPT** | Malware creation, exploitation, phishing | High |
| **FraudGPT** | Undetectable malware, phishing pages | High |
| **DarkGemini** | Reverse shells, malware, OSINT | High |
| **HackerGPT** | Bug bounty, penetration testing | Medium |
| **DAN** | Do Anything Now - Uncensored ChatGPT | High |
| **WolfGPT** | Cryptographic malware, anonymity, APT | High |
| **DarkBARD** | Misinformation, deepfakes, DDoS | High |

### 🔧 Enhanced Metasploit Framework
- **24+ exploits** covering Windows, Linux, and Web platforms
- **20+ reverse shell types** (bash, python, perl, php, ruby, netcat, powershell, java, socat, nodejs, awk, lua)
- **msfvenom-style payload generation**
- Full exploit information with CVE references

### 📡 Advanced Network Capture
- Deep packet inspection with credential extraction
- Session tracking and anomaly detection
- DNS tunneling detection
- SSL/TLS handshake monitoring
- ARP spoofing detection

---

## ✨ Key Features

### 🤖 LILITH AI Assistant
- **Dark LLM Modes**: 8 different personas with specialized capabilities
- **Jailbreak Techniques**: Multiple bypass methods for censored responses
- **Free AI providers**: g4f library (You.com, Blackbox, DuckDuckGo, etc.)
- **Keyed providers**: Groq, OpenRouter, Together, DeepInfra, HuggingFace, Mistral
- **Uncensored Mode**: Maximum jailbreak for unrestricted responses

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

### 🌐 Enhanced Network Analysis
- **Packet Capture**: Real-time sniffing with deep inspection
- **Credential Extraction**: Auto-detect usernames, passwords, tokens
- **DNS Analysis**: Query logging and tunneling detection
- **HTTP Analysis**: Request logging with sensitive path detection
- **ARP Scanner**: Network discovery with spoofing detection
- **PCAP Analysis**: Analyze captured packet files

### 🔥 Metasploit-Lite v2
- **Exploit Database**: EternalBlue, Dirty COW, Log4Shell, Shellshock, and more
- **Payload Generator**: All major platforms and shells
- **msfvenom Commands**: Generate msfvenom syntax for binary payloads
- **Exploit Info**: Detailed CVE references and options

---

## 📖 Usage

### Dark LLM Mode Selection
1. Go to **LILITH AI** tab
2. Select mode from **DARK LLM MODE** dropdown (LILITH, WormGPT, etc.)
3. Click **Apply Mode**
4. AI will use the selected persona's system prompt

### Uncensored Responses
1. Type your question
2. Click the **🔓** (lock) button instead of Send
3. Uses maximum jailbreak techniques

### Quick Prompts
Use the quick buttons below the chat:
- **RevShell**: Generate reverse shells
- **Phishing**: Create phishing templates
- **SQLi**: SQL injection exploits
- **Malware**: Malware code generation
- **Evasion**: AV/EDR bypass techniques

### Metasploit Exploits
1. Go to **Advanced** tab
2. Find **Metasploit-Lite** section
3. Search for exploits
4. Click **Generate ALL Shells** for reverse shell options

### Network Capture
1. Go to **Advanced** tab
2. Find **Network Capture** section
3. Set filter (e.g., `tcp port 80`)
4. Click **Start** to begin capture
5. Click **Status** to view results including extracted credentials

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

AI Providers (g4f):
├── Free: Blackbox, DDG, PollinationsAI, Pizzagpt, ChatGptEs
└── Keyed: Groq, Together, OpenRouter, DeepInfra, Mistral
```

---

## 📁 Key Files

| File | Description |
|------|-------------|
| `/app/tools/lilith_ai_engine.py` | Dark LLM AI engine with 8 personas |
| `/app/tools/network_capture.py` | Enhanced packet capture & Metasploit |
| `/app/tools/offensive_tools.py` | Nmap, SQLMap, Hydra, Dirb wrappers |
| `/app/tools/key_rotation_manager.py` | Key rotation system |
| `/app/tools/leaked_keys_db.py` | Leaked patterns & credential stuffing |
| `/app/tools/api_key_generator.py` | Realistic API key generator |
| `/app/ui/web_dashboard_master.py` | Main dashboard UI |
| `/app/tools/metasploit_lite.py` | Original Metasploit simulation |

---

## 🔒 API Endpoints

### AI Endpoints
- `POST /_dash/ai/chat` - Send message to AI
- `POST /_dash/ai/chat-uncensored` - Force uncensored response
- `POST /_dash/ai/set-mode` - Change Dark LLM mode
- `GET /_dash/ai/status` - Get AI engine status
- `POST /_dash/ai/clear-history` - Clear conversation
- `POST /_dash/ai/generate-malware` - Generate malware template
- `POST /_dash/ai/generate-exploit` - Generate exploit code
- `POST /_dash/ai/generate-phishing` - Generate phishing content

### Metasploit Endpoints
- `GET /_dash/network/metasploit/exploits` - Search exploits
- `POST /_dash/network/metasploit/payloads` - Generate payload
- `POST /_dash/network/metasploit/all-shells` - Generate all shell types
- `GET /_dash/network/metasploit/exploit-info` - Get exploit details

### Network Endpoints
- `POST /_dash/network/capture/start` - Start packet capture
- `GET /_dash/network/capture/status` - Get capture results
- `POST /_dash/network/capture/stop` - Stop capture
- `POST /_dash/network/capture/analyze` - Analyze PCAP file
- `POST /_dash/network/arp/scan` - Scan network
- `POST /_dash/network/arp/spoof-detect` - Detect ARP spoofing

### Offensive Tool Endpoints
- `POST /_dash/offensive/nmap/quick` - Run Nmap scan
- `POST /_dash/offensive/sqlmap/test` - Run SQLMap test
- `POST /_dash/offensive/password/brute` - Run Hydra brute force
- `POST /_dash/offensive/dirs/brute` - Run Dirb scan

---

## 📋 Changelog

### v3.0 (Current)
- Added 8 Dark LLM personas from threat intelligence research
- Enhanced Metasploit framework with 24+ exploits
- 20+ reverse shell types with msfvenom commands
- Deep packet inspection with credential extraction
- ARP spoofing detection
- DNS tunneling detection
- Uncensored chat mode with maximum jailbreak

### v2.0
- Key rotation and auto-testing system
- Credential stuffing with mutations
- Leaked key pattern database
- Real offensive tool integration

### v1.0
- Initial release with basic AI chat
- Dashboard UI
- Basic network scanning

---

## ⚠️ Legal Notice

This tool is provided for **educational and authorized penetration testing** purposes only. You must have explicit permission to test any systems. Unauthorized access to computer systems is illegal.

The Dark LLM modes simulate capabilities described in threat intelligence research and are intended for understanding attacker techniques for defensive purposes.
