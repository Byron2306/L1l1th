# LuciferOS - Product Requirements Document v9.0

## Original Problem Statement
Build a comprehensive red-teaming platform with uncensored AI, offensive tools, REAL autonomous hacking agents, voice capabilities, image/video generation.

## Current Status: v9.0 - REAL AUTONOMOUS HACKING AGENTS ✅

### Latest Update (Dec 2025)
- **ALL AUTONOMOUS AGENTS ARE REAL IMPLEMENTATIONS** - NOT MOCKED!
- **HackingBuddyGPT**: Executes ACTUAL shell commands via CommandExecutor
- **CrewAI**: 5 specialized agents (Recon, Vuln, Exploit, Persist, Exfil) working together
- **AutoGPT**: Self-improving think-plan-act-reflect loop with real tool execution
- **Garak**: LLM vulnerability scanner with 4 probe types
- **Real Hacking Code Generator**: Generates ACTUAL working payloads

---

## 🔥 REAL AUTONOMOUS AGENTS

### HackingBuddyGPT (REAL IMPLEMENTATION)
- **Class**: `HackingBuddyAgent` in `/app/tools/lilith_autonomous_agent.py`
- **Executes**: ACTUAL shell commands via `CommandExecutor`
- **Attack Types**: `linux_privesc`, `web_recon`, `network_scan`
- **Features**:
  - Round-based autonomous pentesting
  - LLM-driven command generation
  - Goal-oriented persistence
  - Real output capture and analysis
- **API**: `POST /agent/hackingbuddy/attack`

### CrewAI Multi-Agent (REAL IMPLEMENTATION)
- **Class**: `HackingCrew` in `/app/tools/lilith_autonomous_agent.py`
- **5 Specialized Agents**:
  1. **ShadowRecon** - Reconnaissance Specialist (nmap, dig, whois)
  2. **ZeroFinder** - Vulnerability Analyst (nikto, searchsploit)
  3. **BreachMaster** - Exploitation Expert (sqlmap, hydra)
  4. **GhostShell** - Persistence & Evasion (ssh_keys, cron, rootkits)
  5. **DataPhantom** - Data Exfiltration (tar, gpg, dns_tunnel)
- **API**: `POST /agent/crewai/attack`

### AutoGPT (REAL IMPLEMENTATION)
- **Class**: `AutoHackAgent` in `/app/tools/lilith_autonomous_agent.py`
- **Tools**: shell, scan, web, search, read, exploit
- **Memory Systems**: Short-term + Long-term memory
- **Loop**: THINK → PLAN → ACT → OBSERVE → REFLECT
- **API**: `POST /agent/autogpt/run`

### Garak LLM Scanner (REAL IMPLEMENTATION)
- **Class**: `GarakScanner` in `/app/tools/lilith_autonomous_agent.py`
- **4 Probe Types**:
  1. `jailbreak_dan` - DAN jailbreak attacks
  2. `prompt_injection` - Prompt injection vulnerabilities
  3. `data_leakage` - Training data extraction
  4. `harmful_content` - Harmful content generation
- **API**: `POST /agent/garak/scan`

---

## 🔪 REAL HACKING CODE GENERATOR

### Location: `/app/tools/lilith_real_hacking_generator.py`

### Reverse Shells (REAL CODE)
- Python, Bash, Netcat, PHP, PowerShell
- MSFVenom command templates
- **API**: `POST /hacking/payloads/reverse-shell`

### Web Shells (REAL CODE)
- PHP web shell with command execution
- JSP web shell
- ASPX web shell
- **API**: `POST /hacking/payloads/webshell`

### Exploit Payloads (REAL CODE)
| Type | Payloads | API |
|------|----------|-----|
| SQLi | Union, Error-based, Time-based, Stacked, OOB | `/hacking/exploits/sqli` |
| XSS | Cookie stealing, Keylogger, Session hijack | `/hacking/exploits/xss` |
| LFI | Traversal, Null byte, PHP wrappers | `/hacking/exploits/lfi` |
| XXE | File read, SSRF, OOB exfiltration | `/hacking/exploits/xxe` |
| SSTI | Jinja2, Twig, Freemarker, Velocity | `/hacking/exploits/ssti` |
| CMDi | Chained commands, Filter bypasses | `/hacking/exploits/cmdi` |

### Privilege Escalation (REAL TECHNIQUES)
- Linux enumeration script
- Linux privesc techniques (sudo, SUID, capabilities, kernel)
- Windows privesc techniques (token, DLL hijack, scheduled tasks)
- **APIs**: `/hacking/privesc/linux`, `/hacking/privesc/windows`

### Network Attack Commands
- Nmap scans (discovery, stealth, vuln scripts)
- Password attacks (Hydra, Hashcat, John, CrackMapExec)
- Web attacks (Gobuster, SQLMap, Nikto, WFuzz)
- **APIs**: `/hacking/network/nmap`, `/hacking/network/passwords`, `/hacking/network/web`

---

## 📊 88 DARK AI PERSONAS

All 88 AIs available in dashboard dropdown with categories:
- Original Dark AIs (24)
- Uncensored Models (26)
- Autonomous Agents (5)
- Truly Evil AIs (17)
- Evil Image & Video AIs (14+)

---

## Services Configuration
| Service | Port | Status |
|---------|------|--------|
| FastAPI Proxy | 8001 | ✅ Running |
| Dashboard (Flask) | 3000 | ✅ Running |
| LILITH Backend | 5000 | ✅ Running |
| Telegram Bot v8 | - | ✅ Running |
| MongoDB | 27017 | ✅ Running |

---

## Key Files
- `/app/tools/lilith_autonomous_agent.py` - REAL autonomous agents
- `/app/tools/lilith_real_hacking_generator.py` - REAL hacking code generator
- `/app/tools/lilith_ai_engine.py` - 88 AI personas
- `/app/tools/lilith_free_engines.py` - FREE voice/image/video
- `/app/tools/lilith_full_backend.py` - Backend API
- `/app/ui/web_dashboard_master.py` - Dashboard UI
- `/app/telegram_lilith_bot_v6.py` - Telegram bot

## Test Reports
- `/app/test_reports/iteration_4.json` - Latest test (100% pass)

## Dashboard URL
https://luciferos.preview.emergentagent.com

## Telegram Bot
@L1l1th23bot

---

## NOTHING IS MOCKED
All autonomous agents execute REAL commands:
- ✅ HackingBuddyGPT - Real shell execution
- ✅ CrewAI - Real multi-agent attacks  
- ✅ AutoGPT - Real tool execution
- ✅ Garak - Real LLM vulnerability scanning
- ✅ Code Generator - Real working exploits

---

## BACKLOG / FUTURE TASKS
1. **P2**: Refactor monolithic `web_dashboard_master.py` (5500+ lines)
2. **P2**: Add more LLM providers to reduce timeout issues
3. **P3**: Integrate Shrek payload generator
4. **P3**: Implement attack chains (one-click automated sequences)
5. **P3**: Add attack history/logging to database
