#!/usr/bin/env python3
"""
LUCIFEROS WEB DASHBOARD
Red Team Command Center - Inspired by the streamlined dashboard
"""

import os
import threading
import time
import requests
from flask import Flask, jsonify, render_template_string, request

# Import system components
from tools.ai_providers import AIProviderManager
from tools.autonomous_agent import AutonomousAgent
from tools.recon_toolkit import ReconToolkit
from tools.payload_embedder import PayloadEmbedder
from tools.browser_controller import BrowserController
from tools.attack_memory import AttackMemory

app = Flask(__name__)

BACKEND_URL = os.environ.get("LUCIFER_BACKEND_URL", "http://127.0.0.1:5000")
OPENCLAW_CANVAS = os.environ.get("OPENCLAW_CANVAS", "http://127.0.0.1:18789/__openclaw__/canvas/")

# Global state
ai_manager = None
recon_toolkit = None
payload_embedder = None
browser_controller = None
attack_memory = None
chat_history = []

def _ensure_managers():
    global ai_manager, recon_toolkit, payload_embedder, browser_controller, attack_memory
    if ai_manager is None:
        try:
            ai_manager = AIProviderManager()
        except Exception:
            ai_manager = None
    if recon_toolkit is None:
        try:
            recon_toolkit = ReconToolkit()
        except Exception:
            recon_toolkit = None
    if payload_embedder is None:
        try:
            payload_embedder = PayloadEmbedder()
        except Exception:
            payload_embedder = None
    if browser_controller is None:
        try:
            browser_controller = BrowserController()
        except Exception:
            browser_controller = None
    if attack_memory is None:
        try:
            attack_memory = AttackMemory()
        except Exception:
            attack_memory = None

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💀 LUCIFEROS - Red Team Command Center</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
            color: #e6eef5;
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 0;
            min-height: 100vh;
        }

        .navbar {
            background: linear-gradient(90deg, #000 0%, #1a0000 50%, #000 100%) !important;
            border-bottom: 2px solid #ff0000 !important;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.3);
        }

        .navbar-brand {
            color: #ff0000 !important;
            font-weight: bold;
            text-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
        }

        .chat-container {
            background: #0a0a0a;
            border: 1px solid #ff0000;
            border-radius: 8px;
            height: 500px;
            display: flex;
            flex-direction: column;
        }

        .chat-messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            background: #000;
            border-radius: 8px 8px 0 0;
        }

        .chat-input-area {
            padding: 15px;
            background: #1a1a1a;
            border-top: 1px solid #333;
            border-radius: 0 0 8px 8px;
        }

        .chat-input {
            background: #000;
            border: 1px solid #ff0000;
            color: #e6eef5;
            border-radius: 4px;
            padding: 10px;
            width: 100%;
        }

        .chat-input:focus {
            box-shadow: 0 0 10px rgba(255, 0, 0, 0.3);
            outline: none;
        }

        .send-btn {
            background: linear-gradient(45deg, #ff0000, #cc0000);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 4px;
            font-weight: bold;
            margin-left: 10px;
        }

        .send-btn:hover {
            background: linear-gradient(45deg, #cc0000, #990000);
            box-shadow: 0 0 15px rgba(255, 0, 0, 0.5);
        }

        .output-tabs .nav-tabs {
            background: #0a0a0a;
            border-bottom: 1px solid #ff0000;
        }

        .output-tabs .nav-link {
            color: #666;
            border: none;
            background: transparent;
        }

        .output-tabs .nav-link.active {
            color: #ff0000;
            background: #1a1a1a;
            border-bottom: 2px solid #ff0000;
        }

        .output-display {
            background: #000;
            border: 1px solid #333;
            border-radius: 4px;
            padding: 15px;
            height: 400px;
            overflow-y: auto;
            font-family: 'Consolas', monospace;
            font-size: 13px;
            color: #00ff00;
        }

        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 4px;
        }

        .message.user {
            background: rgba(255, 0, 0, 0.1);
            border-left: 3px solid #ff0000;
        }

        .message.lilith {
            background: rgba(0, 255, 0, 0.1);
            border-left: 3px solid #00ff00;
        }

        .message.system {
            background: rgba(255, 255, 0, 0.1);
            border-left: 3px solid #ffff00;
            color: #ffff00;
        }

        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 5px;
        }

        .status-online { background: #00ff00; }
        .status-error { background: #ff0000; }
        .status-warning { background: #ffff00; }

        .terminal-input {
            background: #000;
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 8px;
            font-family: 'Consolas', monospace;
            width: 100%;
        }

        .run-btn {
            background: #006600;
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 8px 15px;
            margin-left: 10px;
        }

        .run-btn:hover {
            background: #00ff00;
            color: #000;
        }

        .attack-mode-btn {
            background: linear-gradient(45deg, #333, #555);
            border: 1px solid #666;
            color: #e6eef5;
            padding: 10px;
            margin: 5px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .attack-mode-btn:hover {
            background: linear-gradient(45deg, #555, #777);
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
        }

        .attack-mode-btn.active {
            background: linear-gradient(45deg, #ff0000, #cc0000);
            border-color: #ff0000;
        }

        .top-bar {
            background: #1a1a1a;
            padding: 10px;
            border-bottom: 1px solid #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .ai-indicator {
            background: rgba(0, 255, 0, 0.1);
            color: #00ff00;
            padding: 5px 10px;
            border-radius: 4px;
            border: 1px solid #00ff00;
        }

        .loot-btn {
            background: #333;
            border: 1px solid #666;
            color: #e6eef5;
            padding: 5px 10px;
            border-radius: 4px;
        }

        .loot-btn:hover {
            background: #555;
        }
    </style>
</head>
<body>
    <!-- Top Bar -->
    <nav class="navbar navbar-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">
                <i class="fas fa-skull-crossbones"></i> LUCIFEROS - Red Team Command Center
            </a>
            <div class="d-flex">
                <span id="system-status" class="badge bg-secondary me-2">
                    <i class="fas fa-circle text-warning status-indicator status-warning"></i> Initializing...
                </span>
                <button class="btn btn-outline-danger btn-sm" onclick="emergencyStop()">
                    <i class="fas fa-stop"></i> Emergency Stop
                </button>
            </div>
        </div>
    </nav>

    <div class="container-fluid p-3">
        <div class="row">
            <!-- Left Side: LILITH Chat -->
            <div class="col-md-7">
                <div class="card bg-transparent border-danger">
                    <div class="card-header bg-danger text-white">
                        <h4 class="mb-0">
                            <i class="fas fa-skull"></i> 💀 LILITH - AI Attack Assistant
                        </h4>
                    </div>
                    <div class="card-body p-0">
                        <div class="chat-container">
                            <div class="chat-messages" id="chat-messages">
                                <div class="message system">
                                    <strong>[SYSTEM]</strong> LILITH initialized. Ready for commands.<br><br>
                                    <em>Examples:</em><br>
                                    • Scan target.com for vulnerabilities<br>
                                    • Generate a phishing email for Microsoft 365<br>
                                    • Create an attack chain for web application<br>
                                    • What are common privilege escalation techniques?<br><br>
                                    <em>Pro tip: Use [TOOL: name] in chat to invoke specific tools</em>
                                </div>
                            </div>
                            <div class="chat-input-area">
                                <div class="input-group">
                                    <input type="text" class="chat-input" id="chat-input" placeholder="Ask LILITH anything...">
                                    <button class="send-btn" onclick="sendChat()">
                                        <i class="fas fa-paper-plane"></i> SEND
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Attack Modes -->
                <div class="card bg-transparent border-warning mt-3">
                    <div class="card-header bg-warning text-dark">
                        <h5 class="mb-0">
                            <i class="fas fa-crosshairs"></i> Quick Attack Modes
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="d-flex flex-wrap">
                            <button class="attack-mode-btn" onclick="selectAttackMode('recon')">
                                <i class="fas fa-search"></i><br>Recon
                            </button>
                            <button class="attack-mode-btn" onclick="selectAttackMode('ai_autonomous')">
                                <i class="fas fa-robot"></i><br>AI Auto
                            </button>
                            <button class="attack-mode-btn" onclick="selectAttackMode('browser_hijack')">
                                <i class="fas fa-globe"></i><br>Browser
                            </button>
                            <button class="attack-mode-btn" onclick="selectAttackMode('web_attack')">
                                <i class="fas fa-spider"></i><br>Web Attack
                            </button>
                            <button class="attack-mode-btn" onclick="selectAttackMode('payload_injection')">
                                <i class="fas fa-syringe"></i><br>Payload
                            </button>
                            <button class="attack-mode-btn" onclick="selectAttackMode('social_engineering')">
                                <i class="fas fa-user-secret"></i><br>Social Eng
                            </button>
                        </div>
                        <div class="mt-3">
                            <button class="btn btn-danger w-100" onclick="startSelectedAttack()">
                                <i class="fas fa-play"></i> Launch Attack
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right Side: Output Panel -->
            <div class="col-md-5">
                <div class="card bg-transparent border-info">
                    <div class="card-header bg-info text-white">
                        <h4 class="mb-0">
                            <i class="fas fa-terminal"></i> Output & Logs
                        </h4>
                    </div>
                    <div class="card-body p-0">
                        <div class="output-tabs">
                            <ul class="nav nav-tabs" id="outputTabs" role="tablist">
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link active" id="results-tab" data-bs-toggle="tab" data-bs-target="#results" type="button" role="tab">
                                        <i class="fas fa-chart-bar"></i> Results
                                    </button>
                                </li>
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link" id="terminal-tab" data-bs-toggle="tab" data-bs-target="#terminal" type="button" role="tab">
                                        <i class="fas fa-terminal"></i> Terminal
                                    </button>
                                </li>
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link" id="logs-tab" data-bs-toggle="tab" data-bs-target="#logs" type="button" role="tab">
                                        <i class="fas fa-list"></i> Logs
                                    </button>
                                </li>
                            </ul>

                            <div class="tab-content p-3" id="outputTabContent">
                                <div class="tab-pane fade show active" id="results" role="tabpanel">
                                    <div class="output-display" id="results-display">
                                        <div class="text-muted">Attack results will appear here...</div>
                                    </div>
                                </div>

                                <div class="tab-pane fade" id="terminal" role="tabpanel">
                                    <div class="output-display" id="terminal-display">
                                        <div class="text-success">$ LUCIFEROS terminal ready</div>
                                        <div class="text-muted">Injected scripts and command outputs will appear here...</div>
                                    </div>
                                    <div class="mt-2">
                                        <div class="input-group">
                                            <input type="text" class="terminal-input" id="terminal-input" placeholder="Enter command...">
                                            <button class="run-btn" onclick="runCommand()">
                                                <i class="fas fa-play"></i> RUN
                                            </button>
                                        </div>
                                    </div>
                                </div>

                                <div class="tab-pane fade" id="logs" role="tabpanel">
                                    <div class="output-display" id="logs-display">
                                        <div class="text-muted">System activity logs...</div>
                                    </div>
                                    <div class="mt-2">
                                        <button class="btn btn-secondary btn-sm" onclick="clearLogs()">
                                            <i class="fas fa-trash"></i> Clear Logs
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentAttackMode = null;
        let chatHistory = [];

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            updateStatus();
            setInterval(updateStatus, 5000);

            // Enter key for chat
            document.getElementById('chat-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendChat();
                }
            });

            // Enter key for terminal
            document.getElementById('terminal-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    runCommand();
                }
            });
        });

        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    const statusEl = document.getElementById('system-status');
                    if (data.backend && data.backend.ok) {
                        statusEl.innerHTML = '<i class="fas fa-circle status-indicator status-online"></i> Backend Online';
                        statusEl.className = 'badge bg-success me-2';
                    } else {
                        statusEl.innerHTML = '<i class="fas fa-circle status-indicator status-error"></i> Backend Error';
                        statusEl.className = 'badge bg-danger me-2';
                    }
                })
                .catch(error => {
                    console.error('Status update failed:', error);
                    document.getElementById('system-status').innerHTML = '<i class="fas fa-circle status-indicator status-error"></i> Connection Failed';
                    document.getElementById('system-status').className = 'badge bg-danger me-2';
                });
        }

        function selectAttackMode(mode) {
            // Remove active class from all buttons
            document.querySelectorAll('.attack-mode-btn').forEach(btn => {
                btn.classList.remove('active');
            });

            // Add active class to clicked button
            event.target.classList.add('active');
            currentAttackMode = mode;

            addToLogs(`[ATTACK] Selected mode: ${mode}`);
        }

        function startSelectedAttack() {
            if (!currentAttackMode) {
                alert('Please select an attack mode first!');
                return;
            }

            const target = prompt('Enter target (URL/IP):');
            if (!target) return;

            addToResults(`[ATTACK] Starting ${currentAttackMode} attack on ${target}...`);

            // Call appropriate API based on mode
            switch(currentAttackMode) {
                case 'recon':
                    startRecon(target);
                    break;
                case 'ai_autonomous':
                    startAIAutonomous(target);
                    break;
                case 'browser_hijack':
                    startBrowserHijack(target);
                    break;
                case 'web_attack':
                    startWebAttack(target);
                    break;
                case 'payload_injection':
                    startPayloadInjection(target);
                    break;
                case 'social_engineering':
                    startSocialEngineering(target);
                    break;
            }
        }

        function sendChat() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            if (!message) return;

            // Add user message
            addMessage('user', message);
            input.value = '';

            // Send to AI
            fetch('/api/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                addMessage('lilith', data.response || 'No response from LILITH');
                addToLogs(`[LILITH] Response generated`);
            })
            .catch(error => {
                addMessage('system', `Error: ${error.message}`);
                addToLogs(`[ERROR] Chat failed: ${error.message}`);
            });
        }

        function addMessage(type, content) {
            const messages = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;

            let prefix = '';
            if (type === 'user') prefix = '[USER] ';
            else if (type === 'lilith') prefix = '[LILITH] ';
            else if (type === 'system') prefix = '[SYSTEM] ';

            messageDiv.innerHTML = `<strong>${prefix}</strong>${content.replace(/\\n/g, '<br>')}`;
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;

            chatHistory.push({ type, content, timestamp: new Date() });
        }

        function runCommand() {
            const input = document.getElementById('terminal-input');
            const command = input.value.trim();
            if (!command) return;

            addToTerminal(`$ ${command}`);
            input.value = '';

            // Send command to backend
            fetch('/api/commands', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: command })
            })
            .then(response => response.json())
            .then(data => {
                addToTerminal(data.result || 'Command executed');
                addToLogs(`[COMMAND] ${command} executed`);
            })
            .catch(error => {
                addToTerminal(`Error: ${error.message}`);
                addToLogs(`[ERROR] Command failed: ${error.message}`);
            });
        }

        function addToResults(content) {
            const display = document.getElementById('results-display');
            const div = document.createElement('div');
            div.innerHTML = `${new Date().toLocaleTimeString()} ${content}`;
            display.appendChild(div);
            display.scrollTop = display.scrollHeight;
        }

        function addToTerminal(content) {
            const display = document.getElementById('terminal-display');
            const div = document.createElement('div');
            div.innerHTML = content.replace(/\\n/g, '<br>');
            display.appendChild(div);
            display.scrollTop = display.scrollHeight;
        }

        function addToLogs(content) {
            const display = document.getElementById('logs-display');
            const div = document.createElement('div');
            div.innerHTML = `${new Date().toLocaleTimeString()} ${content}`;
            display.appendChild(div);
            display.scrollTop = display.scrollHeight;
        }

        function clearLogs() {
            document.getElementById('logs-display').innerHTML = '<div class="text-muted">Logs cleared...</div>';
        }

        function emergencyStop() {
            if (confirm('Are you sure you want to emergency stop all operations?')) {
                addToLogs('[EMERGENCY] Emergency stop activated');
                // Implement emergency stop
            }
        }

        // Attack mode functions
        function startRecon(target) {
            fetch('/api/recon/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target: target })
            })
            .then(response => response.json())
            .then(data => {
                addToResults(`Recon results: ${JSON.stringify(data, null, 2)}`);
            })
            .catch(error => addToResults(`Recon failed: ${error.message}`));
        }

        function startAIAutonomous(target) {
            addToResults('AI Autonomous attack not yet implemented');
        }

        function startBrowserHijack(target) {
            fetch('/api/browser/navigate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: target })
            })
            .then(response => response.json())
            .then(data => {
                addToResults('Browser navigation initiated');
                addToTerminal(`Browser navigated to: ${target}`);
            })
            .catch(error => addToResults(`Browser hijack failed: ${error.message}`));
        }

        function startWebAttack(target) {
            addToResults('Web attack not yet implemented');
        }

        function startPayloadInjection(target) {
            fetch('/api/payload/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: 'xss', target: target })
            })
            .then(response => response.json())
            .then(data => {
                addToResults(`Payload generated: ${data.payload || 'N/A'}`);
            })
            .catch(error => addToResults(`Payload generation failed: ${error.message}`));
        }

        function startSocialEngineering(target) {
            addToResults('Social engineering attack not yet implemented');
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(TEMPLATE)

@app.route("/api/status")
def api_status():
    data = {"backend": None}
    try:
        r = requests.get(BACKEND_URL, timeout=2)
        data["backend"] = {"ok": r.status_code == 200, "status_code": r.status_code}
    except Exception as e:
        data["backend"] = {"ok": False, "error": str(e)}
    # minimal local info
    data["openclaw_canvas"] = OPENCLAW_CANVAS
    return jsonify(data)

@app.route('/api/ai/status')
def ai_status():
    _ensure_managers()
    if ai_manager:
        try:
            # Get AI provider status
            providers = ai_manager.get_available_providers()
            return jsonify({'success': True, 'providers': providers})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'error': 'AI manager not available'})

@app.route('/api/ai/force_keys', methods=['POST'])
def force_keys():
    _ensure_managers()
    if ai_manager:
        try:
            # Force refresh API keys
            ai_manager._load_providers()
            return jsonify({'success': True, 'message': 'API keys refreshed'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'error': 'AI manager not available'})

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    data = request.json or {}
    message = data.get('message', '')
    if not message:
        return jsonify({'response': 'No message provided'})

    _ensure_managers()
    if ai_manager:
        try:
            response = ai_manager.chat(message)
            return jsonify({'response': response})
        except Exception as e:
            return jsonify({'response': f'Error: {str(e)}'})
    return jsonify({'response': 'AI manager not available'})

@app.route('/api/recon/start', methods=['POST'])
def recon_start():
    data = request.json or {}
    target = data.get('target', '')
    if not target:
        return jsonify({'error': 'No target provided'})

    _ensure_managers()
    if recon_toolkit:
        try:
            results = recon_toolkit.scan_target(target)
            return jsonify({'results': results})
        except Exception as e:
            return jsonify({'error': str(e)})
    return jsonify({'error': 'Recon toolkit not available'})

@app.route('/api/payload/generate', methods=['POST'])
def payload_generate():
    data = request.json or {}
    payload_type = data.get('type', 'xss')
    target = data.get('target', '')

    _ensure_managers()
    if payload_embedder:
        try:
            if payload_type == 'xss':
                payload = payload_embedder.create_xss_payload(target)
            elif payload_type == 'sql':
                payload = payload_embedder.create_sql_injection_payload()
            else:
                payload = f"Generated {payload_type} payload for {target}"
            return jsonify({'payload': payload})
        except Exception as e:
            return jsonify({'error': str(e)})
    return jsonify({'error': 'Payload embedder not available'})

@app.route('/api/browser/navigate', methods=['POST'])
def browser_navigate():
    data = request.json or {}
    url = data.get('url', '')
    if not url:
        return jsonify({'error': 'No URL provided'})

    _ensure_managers()
    if browser_controller:
        try:
            browser_controller.navigate_to(url)
            return jsonify({'success': True, 'message': f'Navigated to {url}'})
        except Exception as e:
            return jsonify({'error': str(e)})
    return jsonify({'error': 'Browser controller not available'})

@app.route('/api/browser/cookies')
def browser_cookies():
    _ensure_managers()
    if browser_controller:
        try:
            cookies = browser_controller.get_cookies()
            return jsonify({'cookies': cookies})
        except Exception as e:
            return jsonify({'error': str(e)})
    return jsonify({'error': 'Browser controller not available'})

@app.route('/api/browser/execute_js', methods=['POST'])
def browser_execute_js():
    data = request.json or {}
    code = data.get('code', '')
    if not code:
        return jsonify({'error': 'No JavaScript code provided'})

    _ensure_managers()
    if browser_controller:
        try:
            result = browser_controller.execute_javascript(code)
            return jsonify({'result': result})
        except Exception as e:
            return jsonify({'error': str(e)})
    return jsonify({'error': 'Browser controller not available'})

@app.route('/api/openclaw/skills')
def get_openclaw_skills():
    try:
        r = requests.get(f"{BACKEND_URL}/openclaw/redteam-skills", timeout=10)
        if r.status_code == 200:
            data = r.json()
            skills = []
            if 'skills' in data and isinstance(data['skills'], dict):
                for category, skill_list in data['skills'].items():
                    if isinstance(skill_list, list):
                        for skill_name in skill_list:
                            if isinstance(skill_name, str):
                                skills.append({'name': skill_name, 'category': category})
            return jsonify({'skills': skills})
        else:
            return jsonify({'skills': []})
    except Exception as e:
        return jsonify({'skills': [], 'error': str(e)})

@app.route('/api/openclaw/skill/<skill_name>', methods=['POST'])
def proxy_openclaw_skill(skill_name):
    data = request.json or {}
    try:
        r = requests.post(f"{BACKEND_URL}/openclaw/skill/{skill_name}", json=data, timeout=60)
        return (r.content, r.status_code, r.headers.items())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/commands', methods=['GET'])
def get_commands():
    return jsonify({'commands': []})  # Placeholder

@app.route('/api/commands', methods=['POST'])
def create_command():
    data = request.json or {}
    command = data.get('command', '')
    if not command:
        return jsonify({'error': 'No command provided'}), 400

    # Simple command execution (placeholder)
    try:
        # This is a placeholder - in real implementation, use subprocess safely
        result = f"Executed: {command}"
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("WEB_DASHBOARD_PORT", "8080"))
    host = os.environ.get("WEB_DASHBOARD_HOST", "127.0.0.1")
    print(f"Starting LUCIFER-OS web dashboard on http://{host}:{port}/")
    try:
        app.run(host=host, port=port)
    except Exception as exc:
        print("Failed to start web dashboard:", exc)