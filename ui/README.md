# LuciferOS Web Dashboard

A modern web-based interface for the LuciferOS red team platform, converted from the original PyQt5 desktop application.

## Features

✅ **Full Web Interface** - Access LuciferOS from any web browser
✅ **Real-time Chat** - Interact with LILITH AI assistant
✅ **Command Execution** - Execute detected commands directly
✅ **Live Status Monitoring** - Backend and attack server status
✅ **Harvest Statistics** - Track captured credentials and data
✅ **Responsive Design** - Works on desktop and mobile devices
✅ **Dark Theme** - Authentic red team aesthetic

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │────│  Flask Web App  │────│ Backend API     │
│                 │    │  (Port 3000)    │    │ (Port 5000)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              └────────────────────────┘
                                       │
                          ┌─────────────────┐
                          │ Attack Server   │
                          │ (Port 8888)     │
                          └─────────────────┘
```

## Access Points

- **Web Dashboard**: http://127.0.0.1:3000
- **Backend API**: http://127.0.0.1:5000
- **Attack Server**: http://127.0.0.1:8888

## API Endpoints

### Chat & Commands
- `POST /api/chat` - Send message to LILITH AI
- `GET /api/commands` - Get command queue
- `POST /api/commands/<id>` - Execute specific command

### Status & Monitoring
- `GET /api/status` - Get system status
- `POST /api/harvest/refresh` - Refresh harvest statistics
- `GET /api/chat/history` - Get chat history

## Usage

1. **Start the system**:
   ```bash
   # Backend (Port 5000)
   cd tools && python3 lilith_full_backend.py

   # Attack Server (Port 8888)
   cd tools && python3 attack_server.py

   # Web Dashboard (Port 3000)
   cd ui && python3 web_dashboard.py
   ```

2. **Access the dashboard**:
   - Open http://127.0.0.1:3000 in your web browser
   - Use the sidebar to access different attack categories
   - Chat with LILITH for AI-powered assistance
   - Execute commands detected in AI responses

## Interface Components

### Sidebar Navigation
- **Reconnaissance** - Scanning and enumeration tools
- **Attack Vectors** - Various attack techniques
- **Payloads & Malware** - Malware generation and deployment
- **Data Exfiltration** - Data theft methods
- **Tools & Utilities** - Helper utilities
- **Danger Zone** - High-risk operations

### Main Interface
- **Top Bar** - Mode, loot counter, AI provider status
- **Chat Panel** - LILITH AI interaction
- **Output Panel** - Logs and command results
- **Command Queue** - Detected executable commands

## Security Note

⚠️ **This is a red team platform for authorized security testing only**

- Requires explicit authorization from system owners
- Define scope and timeframe for testing
- Document all activities and findings
- Follow legal and ethical guidelines

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Custom dark theme with red team aesthetics
- **Icons**: Font Awesome
- **Communication**: RESTful API with JSON

Built for professional red team operations with modern web technologies.