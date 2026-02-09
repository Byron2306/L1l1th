#!/usr/bin/env python3
"""
LUCIFEROS MASTER WEB DASHBOARD
Combines all features from luciferos_master_dashboard in web format
Full integration with Backend, OpenClaw, Attack Server
"""

import os
import sys
import json
import socket
import requests
from datetime import datetime
from flask import Flask, jsonify, render_template_string, request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

BACKEND_URL = os.environ.get("LUCIFER_BACKEND_URL", "http://127.0.0.1:5000")
OPENCLAW_CANVAS = os.environ.get("OPENCLAW_CANVAS", "http://127.0.0.1:18789/__openclaw__/canvas/")

# Enhanced HTML Template with ALL Master Dashboard Features
MASTER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💀 LUCIFEROS - Master Command Center</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-red: #ff0000;
            --dark-bg: #0a0a0a;
            --darker-bg: #000000;
            --border-red: #ff0000;
            --text-green: #00ff00;
            --text-yellow: #ffff00;
        }

        body {
            background: linear-gradient(135deg, var(--darker-bg) 0%, var(--dark-bg) 100%);
            color: #e6eef5;
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .navbar {
            background: linear-gradient(90deg, #000 0%, #1a0000 50%, #000 100%) !important;
            border-bottom: 3px solid var(--primary-red) !important;
            box-shadow: 0 0 30px rgba(255, 0, 0, 0.5);
            padding: 15px;
        }

        .navbar-brand {
            color: var(--primary-red) !important;
            font-weight: bold;
            font-size: 24px;
            text-shadow: 0 0 15px rgba(255, 0, 0, 0.8);
            letter-spacing: 2px;
        }

        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-left: 10px;
            animation: pulse 2s infinite;
        }

        .status-online { background: #00ff00; }
        .status-offline { background: #666; }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .main-container {
            display: grid;
            grid-template-columns: 280px 1fr 320px;
            gap: 15px;
            padding: 20px;
            height: calc(100vh - 80px);
        }

        .left-panel, .center-panel, .right-panel {
            background: var(--dark-bg);
            border: 2px solid var(--primary-red);
            border-radius: 10px;
            padding: 15px;
            overflow-y: auto;
        }

        .panel-title {
            color: var(--primary-red);
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--primary-red);
            text-transform: uppercase;
        }

        .collapsible-section {
            margin-bottom: 15px;
            border: 1px solid #333;
            border-radius: 5px;
        }

        .section-header {
            background: #1a1a1a;
            padding: 10px;
            cursor: pointer;
            color: var(--primary-red);
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .section-header:hover {
            background: #222;
        }

        .section-content {
            padding: 10px;
            display: none;
        }

        .section-content.active {
            display: block;
        }

        .attack-mode-btn {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            background: linear-gradient(45deg, #1a0000, #0a0000);
            border: 1px solid var(--primary-red);
            color: #fff;
            cursor: pointer;
            border-radius: 5px;
            font-size: 14px;
            transition: all 0.3s;
        }

        .attack-mode-btn:hover {
            background: linear-gradient(45deg, #ff0000, #cc0000);
            box-shadow: 0 0 15px rgba(255, 0, 0, 0.5);
            transform: translateY(-2px);
        }

        .attack-mode-btn.active {
            background: linear-gradient(45deg, #ff0000, #990000);
            border-color: #ffff00;
        }

        .launch-attack-btn {
            width: 100%;
            padding: 20px;
            background: linear-gradient(45deg, #ff0000, #cc0000);
            border: 2px solid #ffff00;
            color: white;
            font-size: 18px;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 15px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .launch-attack-btn:hover {
            background: linear-gradient(45deg, #cc0000, #990000);
            box-shadow: 0 0 25px rgba(255, 0, 0, 0.8);
            transform: scale(1.02);
        }

        .tabs {
            display: flex;
            border-bottom: 2px solid var(--primary-red);
            margin-bottom: 15px;
        }

        .tab {
            padding: 10px 20px;
            cursor: pointer;
            background: transparent;
            border: none;
            color: #666;
            font-weight: bold;
        }

        .tab.active {
            color: var(--primary-red);
            border-bottom: 3px solid var(--primary-red);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .chat-container {
            background: var(--darker-bg);
            border: 1px solid var(--primary-red);
            border-radius: 8px;
            height: 400px;
            display: flex;
            flex-direction: column;
        }

        .chat-messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            background: var(--darker-bg);
        }

        .message {
            margin-bottom: 12px;
            padding: 8px;
            border-radius: 4px;
            font-size: 13px;
        }

        .message.user {
            background: rgba(255, 0, 0, 0.1);
            border-left: 3px solid var(--primary-red);
        }

        .message.lilith {
            background: rgba(0, 255, 0, 0.1);
            border-left: 3px solid var(--text-green);
            color: var(--text-green);
        }

        .message.system {
            background: rgba(255, 255, 0, 0.1);
            border-left: 3px solid var(--text-yellow);
            color: var(--text-yellow);
        }

        .chat-input-area {
            padding: 10px;
            background: #1a1a1a;
            border-top: 1px solid #333;
            display: flex;
            gap: 10px;
        }

        .chat-input {
            flex: 1;
            background: var(--darker-bg);
            border: 1px solid var(--primary-red);
            color: #e6eef5;
            padding: 8px;
            border-radius: 4px;
        }

        .send-btn {
            background: var(--primary-red);
            border: none;
            color: white;
            padding: 8px 20px;
            border-radius: 4px;
            cursor: pointer;
        }

        .input-group {
            margin-bottom: 12px;
        }

        .input-group label {
            display: block;
            color: #999;
            font-size: 12px;
            margin-bottom: 5px;
        }

        .input-group input, .input-group select, .input-group textarea {
            width: 100%;
            background: var(--darker-bg);
            border: 1px solid #333;
            color: #e6eef5;
            padding: 8px;
            border-radius: 4px;
        }

        .output-display {
            background: var(--darker-bg);
            border: 1px solid #333;
            border-radius: 4px;
            padding: 15px;
            height: 350px;
            overflow-y: auto;
            font-size: 12px;
            color: var(--text-green);
            font-family: 'Consolas', monospace;
        }

        .progress-bar-custom {
            background: var(--darker-bg);
            border: 1px solid var(--primary-red);
            height: 25px;
            border-radius: 5px;
            margin: 10px 0;
            position: relative;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary-red), #ff6600);
            width: 0%;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 12px;
        }

        .skill-btn {
            padding: 8px 12px;
            margin: 5px;
            background: #1a1a1a;
            border: 1px solid var(--primary-red);
            color: #fff;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }

        .skill-btn:hover {
            background: var(--primary-red);
        }

        .status-box {
            background: #1a1a1a;
            border: 1px solid #333;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }

        .status-item {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #222;
        }

        .status-label {
            color: #999;
        }

        .status-value {
            color: var(--text-green);
            font-weight: bold;
        }

        .emergency-stop-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            background: #ff0000;
            border: 3px solid #ffff00;
            border-radius: 50%;
            color: white;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.8);
            z-index: 1000;
        }

        .emergency-stop-btn:hover {
            background: #cc0000;
            transform: scale(1.1);
        }

        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: var(--darker-bg);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--primary-red);
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar">
        <span class="navbar-brand">
            💀 LUCIFEROS - MASTER COMMAND CENTER
            <span class="status-indicator status-online" id="backend-status"></span>
        </span>
        <div style="color: #999;">
            <small>Backend: <span id="backend-url">{{ backend_url }}</span> | OpenClaw: <span id="openclaw-status">Checking...</span></small>
        </div>
    </nav>

    <!-- Main Container -->
    <div class="main-container">
        <!-- LEFT PANEL: Controls -->
        <div class="left-panel">
            <div class="panel-title">🎯 CONTROL CENTER</div>

            <!-- Target Configuration -->
            <div class="collapsible-section">
                <div class="section-header" onclick="toggleSection(this)">
                    <span>🎯 TARGET CONFIG</span>
                    <span>▼</span>
                </div>
                <div class="section-content active">
                    <div class="input-group">
                        <label>Target URL/IP</label>
                        <input type="text" id="target-input" placeholder="example.com or 192.168.1.1">
                    </div>
                    <div class="input-group">
                        <label>Port</label>
                        <input type="number" id="port-input" value="80" min="1" max="65535">
                    </div>
                    <div class="input-group">
                        <label>Protocol</label>
                        <select id="protocol-select">
                            <option>http</option>
                            <option>https</option>
                            <option>tcp</option>
                            <option>udp</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- Attack Modes -->
            <div class="collapsible-section">
                <div class="section-header" onclick="toggleSection(this)">
                    <span>⚔️ ATTACK MODES</span>
                    <span>▼</span>
                </div>
                <div class="section-content active">
                    <button class="attack-mode-btn" onclick="selectAttackMode('recon')">
                        🔍 Reconnaissance
                    </button>
                    <button class="attack-mode-btn" onclick="selectAttackMode('ai_autonomous')">
                        🤖 AI Autonomous
                    </button>
                    <button class="attack-mode-btn" onclick="selectAttackMode('payload')">
                        💣 Payload Engineering
                    </button>
                    <button class="attack-mode-btn" onclick="selectAttackMode('browser')">
                        🦠 Browser Hijack
                    </button>
                    <button class="attack-mode-btn" onclick="selectAttackMode('web')">
                        🌐 Web Application
                    </button>
                    <button class="attack-mode-btn" onclick="selectAttackMode('social')">
                        📧 Social Engineering
                    </button>
                    
                    <button class="launch-attack-btn" onclick="launchAttack()">
                        🚀 LAUNCH ATTACK
                    </button>
                </div>
            </div>

            <!-- OpenClaw Skills -->
            <div class="collapsible-section">
                <div class="section-header" onclick="toggleSection(this)">
                    <span>🦞 OPENCLAW SKILLS</span>
                    <span>▼</span>
                </div>
                <div class="section-content" id="openclaw-skills">
                    <button class="skill-btn" onclick="runSkill('lilith')">LILITH</button>
                    <button class="skill-btn" onclick="runSkill('coding-agent')">Code Gen</button>
                    <button class="skill-btn" onclick="runSkill('browser')">Browser</button>
                    <button class="skill-btn" onclick="runSkill('github')">GitHub</button>
                    <button class="skill-btn" onclick="runSkill('discord')">Discord</button>
                </div>
            </div>
        </div>

        <!-- CENTER PANEL: Main Workspace -->
        <div class="center-panel">
            <div class="tabs">
                <button class="tab active" onclick="switchTab('lilith')">💬 LILITH AI</button>
                <button class="tab" onclick="switchTab('progress')">📊 Progress</button>
                <button class="tab" onclick="switchTab('browser')">🌐 Browser</button>
                <button class="tab" onclick="switchTab('recon')">🔍 Recon</button>
                <button class="tab" onclick="switchTab('payload')">💣 Payload</button>
                <button class="tab" onclick="switchTab('coding')">👨‍💻 Coding</button>
                <button class="tab" onclick="switchTab('learning')">🧠 Learning</button>
                <button class="tab" onclick="switchTab('memory')">💾 Memory</button>
                <button class="tab" onclick="switchTab('harvester')">🔑 Harvester</button>
                <button class="tab" onclick="switchTab('advanced')">⚔️ Advanced</button>
            </div>

            <!-- LILITH Tab -->
            <div class="tab-content active" id="tab-lilith">
                <div class="panel-title">🖤 LILITH - AI ATTACK ASSISTANT</div>
                <div class="chat-container">
                    <div class="chat-messages" id="chat-messages"></div>
                    <div class="chat-input-area">
                        <input type="text" class="chat-input" id="chat-input" placeholder="Ask LILITH anything..." onkeypress="if(event.key==='Enter') sendChat()">
                        <button class="send-btn" onclick="sendChat()">Send</button>
                    </div>
                </div>
            </div>

            <!-- Progress Tab -->
            <div class="tab-content" id="tab-progress">
                <div class="panel-title">📊 ATTACK PROGRESS</div>
                <div id="progress-container">
                    <div class="status-box">
                        <div class="status-item">
                            <span class="status-label">Current Phase:</span>
                            <span class="status-value" id="current-phase">Idle</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">Progress:</span>
                            <span class="status-value" id="progress-percent">0%</span>
                        </div>
                    </div>
                    <div class="progress-bar-custom">
                        <div class="progress-fill" id="progress-bar">0%</div>
                    </div>
                    <div class="output-display" id="progress-log"></div>
                </div>
            </div>

            <!-- Browser Tab -->
            <div class="tab-content" id="tab-browser">
                <div class="panel-title">🌐 BROWSER CONTROL</div>
                <div class="input-group">
                    <label>URL to Navigate</label>
                    <input type="text" id="browser-url" placeholder="https://example.com">
                    <button class="attack-mode-btn" onclick="browserNavigate()">Navigate</button>
                </div>
                <div class="output-display" id="browser-output"></div>
            </div>

            <!-- Recon Tab -->
            <div class="tab-content" id="tab-recon">
                <div class="panel-title">🔍 RECONNAISSANCE</div>
                <div class="input-group">
                    <label>Target for Recon</label>
                    <input type="text" id="recon-target" placeholder="example.com">
                    <button class="attack-mode-btn" onclick="startRecon()">Start Recon</button>
                </div>
                <div class="output-display" id="recon-output"></div>
            </div>

            <!-- Payload Tab -->
            <div class="tab-content" id="tab-payload">
                <div class="panel-title">💣 PAYLOAD ENGINEERING</div>
                <div class="input-group">
                    <label>Payload Type</label>
                    <select id="payload-type">
                        <option>xss</option>
                        <option>sql-injection</option>
                        <option>reverse-shell</option>
                        <option>trojan</option>
                    </select>
                </div>
                <div class="input-group">
                    <label>Target</label>
                    <input type="text" id="payload-target" placeholder="Target system">
                    <button class="attack-mode-btn" onclick="generatePayload()">Generate</button>
                </div>
                <div class="output-display" id="payload-output"></div>
            </div>

            <!-- Coding Agent Tab -->
            <div class="tab-content" id="tab-coding">
                <div class="panel-title">👨‍💻 CODING AGENT</div>
                <div class="status-box">
                    <div class="status-item">
                        <span class="status-label">Status:</span>
                        <span class="status-value" id="coding-status">Checking...</span>
                    </div>
                </div>
                <div class="input-group">
                    <label>Code Generation Request</label>
                    <textarea id="coding-prompt" rows="4" placeholder="Describe what code you want to generate..."></textarea>
                    <button class="attack-mode-btn" onclick="generateCode()">Generate Code</button>
                </div>
                <div class="output-display" id="coding-output"></div>
            </div>

            <!-- Learning Tab -->
            <div class="tab-content" id="tab-learning">
                <div class="panel-title">🧠 LILITH LEARNING SYSTEM</div>
                <div class="status-box">
                    <h6 style="color: var(--primary-red);">Learning Statistics</h6>
                    <div class="status-item">
                        <span class="status-label">Total Attacks:</span>
                        <span class="status-value" id="learning-attacks">0</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Success Rate:</span>
                        <span class="status-value" id="learning-success">0%</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Insights Generated:</span>
                        <span class="status-value" id="learning-insights-count">0</span>
                    </div>
                </div>
                <button class="attack-mode-btn" onclick="loadLearningData()">Refresh Learning Data</button>
                <div class="panel-title" style="font-size: 14px; margin-top: 20px;">Recent Insights</div>
                <div class="output-display" id="learning-insights"></div>
            </div>

            <!-- Memory Tab -->
            <div class="tab-content" id="tab-memory">
                <div class="panel-title">💾 ATTACK MEMORY</div>
                <div class="input-group">
                    <label>Save Memory</label>
                    <textarea id="memory-input" rows="3" placeholder="Save attack data, techniques, or notes..."></textarea>
                    <button class="attack-mode-btn" onclick="saveMemory()">Save to Memory</button>
                </div>
                <div class="panel-title" style="font-size: 14px; margin-top: 20px;">Memory Recall</div>
                <button class="attack-mode-btn" onclick="recallMemory()">Recall Memories</button>
                <div class="output-display" id="memory-output"></div>
            </div>

            <!-- API Key Harvester Tab -->
            <div class="tab-content" id="tab-harvester">
                <div class="panel-title">🔑 AUTONOMOUS API KEY HARVESTER</div>
                <div class="status-box">
                    <h6 style="color: var(--primary-red);">Harvesting Status</h6>
                    <div class="status-item">
                        <span class="status-label">Status:</span>
                        <span class="status-value" id="harvest-status">Idle</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Phase:</span>
                        <span class="status-value" id="harvest-phase">-</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Progress:</span>
                        <span class="status-value" id="harvest-progress">0%</span>
                    </div>
                </div>
                <div class="progress-bar-custom" style="margin: 15px 0;">
                    <div class="progress-fill" id="harvest-progress-bar">0%</div>
                </div>
                <div class="input-group">
                    <label>Select Provider</label>
                    <select id="harvest-provider">
                        <option value="groq">Groq (Fast, Free, 70B Llama models)</option>
                        <option value="huggingface">HuggingFace (Free, Unlimited)</option>
                        <option value="together">Together.ai ($25 free credits)</option>
                        <option value="mistral">Mistral AI (Free tier available)</option>
                        <option value="venice">Venice.ai (Uncensored models)</option>
                        <option value="deepinfra">DeepInfra (Free credits)</option>
                        <option value="openrouter">OpenRouter (Multi-model access)</option>
                        <option value="cerebras">Cerebras (Ultra-fast inference)</option>
                        <option value="sambanova">SambaNova (Enterprise-grade)</option>
                        <option value="fireworks">Fireworks.ai (Fast inference)</option>
                    </select>
                </div>
                <button class="launch-attack-btn" onclick="startHarvesting()" id="harvest-btn">
                    🚀 START AUTONOMOUS HARVESTING
                </button>
                
                <div style="margin-top: 15px; display: flex; gap: 10px;">
                    <button class="attack-mode-btn" onclick="applyHarvestedKeys()" id="apply-keys-btn">
                        ⚡ APPLY KEYS TO SESSION
                    </button>
                    <button class="attack-mode-btn" onclick="restartBackend()" id="restart-btn">
                        🔄 RESTART BACKEND
                    </button>
                </div>
                
                <div class="status-box" style="margin-top: 15px;">
                    <h6 style="color: var(--text-green);">Harvested Keys Database</h6>
                    <div id="harvested-keys-list" style="font-size: 11px; max-height: 100px; overflow-y: auto;">
                        Loading...
                    </div>
                </div>
                <div class="panel-title" style="font-size: 14px; margin-top: 20px;">Live Harvesting Log</div>
                <div class="output-display" id="harvest-log" style="height: 300px;"></div>
            </div>
        </div>

        <!-- RIGHT PANEL: Monitoring -->
        <div class="right-panel">
            <div class="panel-title">📊 SYSTEM MONITOR</div>

            <!-- System Status -->
            <div class="status-box">
                <h6 style="color: var(--primary-red); margin-bottom: 10px;">System Status</h6>
                <div class="status-item">
                    <span class="status-label">Backend:</span>
                    <span class="status-value" id="status-backend">●</span>
                </div>
                <div class="status-item">
                    <span class="status-label">OpenClaw:</span>
                    <span class="status-value" id="status-openclaw">●</span>
                </div>
                <div class="status-item">
                    <span class="status-label">AI Providers:</span>
                    <span class="status-value" id="status-ai">0/0</span>
                </div>
            </div>

            <!-- Live Logs -->
            <div style="margin-top: 20px;">
                <div class="panel-title" style="font-size: 14px;">📝 LIVE LOGS</div>
                <div class="output-display" id="live-logs" style="height: 250px;"></div>
            </div>

            <!-- Active Attacks -->
            <div style="margin-top: 20px;">
                <div class="panel-title" style="font-size: 14px;">⚔️ ACTIVE ATTACKS</div>
                <div id="active-attacks" style="font-size: 12px; color: #999;">
                    No active attacks
                </div>
            </div>
        </div>
    </div>

    <!-- Advanced Capabilities Tab -->
    <div class="tab-content" id="tab-advanced">
        <div class="panel-title">⚔️ ADVANCED RED TEAM CAPABILITIES</div>
        <div class="advanced-grid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; padding: 15px;">
            
            <!-- Recon Module -->
            <div class="capability-card" style="background: #1a1a2e; border: 1px solid #333; border-radius: 8px; padding: 15px;">
                <h3 style="color: #00ff00; margin: 0 0 10px 0; font-size: 14px;">🔍 Advanced Recon</h3>
                <input type="text" id="recon-target" placeholder="Target domain" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 10px;">
                <div style="display: flex; gap: 5px;">
                    <button onclick="runPassiveRecon()" style="flex: 1; padding: 8px; background: #1a4d1a; border: none; color: #fff; cursor: pointer; font-size: 11px;">Passive</button>
                    <button onclick="runActiveRecon()" style="flex: 1; padding: 8px; background: #4d1a1a; border: none; color: #fff; cursor: pointer; font-size: 11px;">Active</button>
                    <button onclick="runFullRecon()" style="flex: 1; padding: 8px; background: #4d4d1a; border: none; color: #fff; cursor: pointer; font-size: 11px;">Full</button>
                </div>
            </div>
            
            <!-- NLP Social Engineering -->
            <div class="capability-card" style="background: #1a1a2e; border: 1px solid #333; border-radius: 8px; padding: 15px;">
                <h3 style="color: #ff00ff; margin: 0 0 10px 0; font-size: 14px;">🎭 Social Engineering</h3>
                <input type="text" id="phish-name" placeholder="Target name" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 5px;">
                <input type="text" id="phish-company" placeholder="Company" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 10px;">
                <div style="display: flex; gap: 5px;">
                    <button onclick="genPhishing()" style="flex: 1; padding: 8px; background: #4d1a4d; border: none; color: #fff; cursor: pointer; font-size: 11px;">Phishing</button>
                    <button onclick="genVishing()" style="flex: 1; padding: 8px; background: #1a4d4d; border: none; color: #fff; cursor: pointer; font-size: 11px;">Vishing</button>
                </div>
            </div>
            
            <!-- ML Anomaly Detection -->
            <div class="capability-card" style="background: #1a1a2e; border: 1px solid #333; border-radius: 8px; padding: 15px;">
                <h3 style="color: #00ffff; margin: 0 0 10px 0; font-size: 14px;">🤖 ML Detection</h3>
                <textarea id="ml-data" placeholder='[{"hour": 3, "geo_anomaly": true}]' style="width: 100%; height: 60px; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; font-size: 10px;"></textarea>
                <button onclick="runAnomalyDetection()" style="width: 100%; padding: 8px; background: #1a4d4d; border: none; color: #fff; cursor: pointer; margin-top: 10px;">Detect Anomalies</button>
            </div>
            
            <!-- Crypto Analysis -->
            <div class="capability-card" style="background: #1a1a2e; border: 1px solid #333; border-radius: 8px; padding: 15px;">
                <h3 style="color: #ffff00; margin: 0 0 10px 0; font-size: 14px;">🔐 Crypto Analysis</h3>
                <input type="text" id="hash-input" placeholder="Hash to analyze" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 10px;">
                <div style="display: flex; gap: 5px;">
                    <button onclick="analyzeHash()" style="flex: 1; padding: 8px; background: #4d4d1a; border: none; color: #fff; cursor: pointer; font-size: 11px;">Analyze</button>
                    <button onclick="generateKeys()" style="flex: 1; padding: 8px; background: #1a4d1a; border: none; color: #fff; cursor: pointer; font-size: 11px;">Gen Keys</button>
                </div>
            </div>
            
            <!-- Exploit Framework -->
            <div class="capability-card" style="background: #1a1a2e; border: 1px solid #333; border-radius: 8px; padding: 15px;">
                <h3 style="color: #ff0000; margin: 0 0 10px 0; font-size: 14px;">💥 Exploit Framework</h3>
                <select id="exploit-type" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 10px;">
                    <option value="sqli">SQL Injection</option>
                    <option value="xss">XSS</option>
                    <option value="rce">RCE</option>
                    <option value="buffer_overflow">Buffer Overflow</option>
                </select>
                <button onclick="generateExploit()" style="width: 100%; padding: 8px; background: #4d1a1a; border: none; color: #fff; cursor: pointer;">Generate Exploit</button>
            </div>
            
            <!-- Evasion Techniques -->
            <div class="capability-card" style="background: #1a1a2e; border: 1px solid #333; border-radius: 8px; padding: 15px;">
                <h3 style="color: #ff6600; margin: 0 0 10px 0; font-size: 14px;">🛡️ Evasion</h3>
                <button onclick="getEvasionTechniques()" style="width: 100%; padding: 8px; background: #4d2a1a; border: none; color: #fff; cursor: pointer; margin-bottom: 5px;">AV/EDR Bypass</button>
                <button onclick="getPersistence()" style="width: 100%; padding: 8px; background: #2a4d1a; border: none; color: #fff; cursor: pointer;">Persistence Methods</button>
            </div>
            
            <!-- Wireless Attacks -->
            <div class="capability-card" style="background: #1a1a2e; border: 1px solid #333; border-radius: 8px; padding: 15px;">
                <h3 style="color: #0099ff; margin: 0 0 10px 0; font-size: 14px;">📡 Wireless</h3>
                <button onclick="getWirelessAttacks()" style="width: 100%; padding: 8px; background: #1a2a4d; border: none; color: #fff; cursor: pointer;">WiFi Attack Methods</button>
            </div>
            
            <!-- Physical Security -->
            <div class="capability-card" style="background: #1a1a2e; border: 1px solid #333; border-radius: 8px; padding: 15px;">
                <h3 style="color: #9900ff; margin: 0 0 10px 0; font-size: 14px;">🚪 Physical</h3>
                <button onclick="getPhysicalBypass()" style="width: 100%; padding: 8px; background: #2a1a4d; border: none; color: #fff; cursor: pointer;">Bypass Techniques</button>
            </div>
            
            <!-- Supply Chain -->
            <div class="capability-card" style="background: #1a1a2e; border: 1px solid #333; border-radius: 8px; padding: 15px;">
                <h3 style="color: #ff0099; margin: 0 0 10px 0; font-size: 14px;">🔗 Supply Chain</h3>
                <input type="text" id="supply-target" placeholder="Target" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 10px;">
                <button onclick="analyzeSupplyChain()" style="width: 100%; padding: 8px; background: #4d1a2a; border: none; color: #fff; cursor: pointer;">Analyze Vectors</button>
            </div>
            
            <!-- Zero-Day Research -->
            <div class="capability-card" style="background: #1a1a2e; border: 1px solid #333; border-radius: 8px; padding: 15px;">
                <h3 style="color: #00ff99; margin: 0 0 10px 0; font-size: 14px;">🔬 0-Day Research</h3>
                <button onclick="getZeroDayMethodology()" style="width: 100%; padding: 8px; background: #1a4d2a; border: none; color: #fff; cursor: pointer;">Research Framework</button>
            </div>
        </div>
        
        <!-- Results Panel -->
        <div class="status-box" style="margin: 15px; max-height: 300px; overflow-y: auto;">
            <h6 style="color: var(--text-green);">Results Output</h6>
            <pre id="advanced-results" style="font-size: 11px; color: #0f0; white-space: pre-wrap; word-wrap: break-word;">Ready for operations...</pre>
        </div>
    </div>

    <!-- Emergency Stop Button -->
    <button class="emergency-stop-btn" onclick="emergencyStop()" title="Emergency Stop">
        <i class="fas fa-stop"></i>
    </button>

    <script>
        let selectedAttackMode = null;
        let currentTarget = null;

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            checkSystemStatus();
            loadOpenClawSkills();
            checkCodingAgent();
            loadLearningData();
            setInterval(checkSystemStatus, 5000);
            addLog('[SYSTEM] LUCIFEROS Master Dashboard initialized');
        });

        function toggleSection(header) {
            const content = header.nextElementSibling;
            const arrow = header.querySelector('span:last-child');
            content.classList.toggle('active');
            arrow.textContent = content.classList.contains('active') ? '▼' : '▶';
        }

        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('tab-' + tabName).classList.add('active');
        }

        function selectAttackMode(mode) {
            selectedAttackMode = mode;
            document.querySelectorAll('.attack-mode-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            addLog(`[SYSTEM] Selected attack mode: ${mode.toUpperCase()}`);
        }

        function launchAttack() {
            if (!selectedAttackMode) {
                addLog('[ERROR] Please select an attack mode first');
                return;
            }

            const target = document.getElementById('target-input').value;
            if (!target) {
                addLog('[ERROR] Please enter a target');
                return;
            }

            currentTarget = target;
            addLog(`[ATTACK] Launching ${selectedAttackMode} attack on ${target}`);
            updateProgress('Launching', 10);

            // Execute based on mode
            switch(selectedAttackMode) {
                case 'recon':
                    startReconAttack(target);
                    break;
                case 'ai_autonomous':
                    startAIAutonomous(target);
                    break;
                case 'payload':
                    startPayloadAttack(target);
                    break;
                case 'browser':
                    startBrowserHijack(target);
                    break;
                case 'web':
                    startWebAttack(target);
                    break;
                case 'social':
                    startSocialEngineering(target);
                    break;
            }
        }

        async function sendChat() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            if (!message) return;

            addMessage('user', message);
            input.value = '';

            try {
                const response = await fetch('/_dash/ai/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
                
                const data = await response.json();
                const responseText = data.response || 'No response';
                addMessage('lilith', responseText);
                
                if (!data.success) {
                    addLog('[CHAT] AI providers unavailable - add API keys');
                }
            } catch (error) {
                addMessage('system', `Error: ${error.message}`);
            }
        }

        function addMessage(type, content) {
            const messages = document.getElementById('chat-messages');
            const div = document.createElement('div');
            div.className = `message ${type}`;
            const prefix = type === 'user' ? '[USER]' : type === 'lilith' ? '[LILITH]' : '[SYSTEM]';
            div.innerHTML = `<strong>${prefix}</strong> ${content.replace(/\\n/g, '<br>')}`;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        function addLog(message) {
            const logs = document.getElementById('live-logs');
            const timestamp = new Date().toLocaleTimeString();
            logs.innerHTML += `[${timestamp}] ${message}\\n`;
            logs.scrollTop = logs.scrollHeight;
        }

        function updateProgress(phase, percent) {
            document.getElementById('current-phase').textContent = phase;
            document.getElementById('progress-percent').textContent = percent + '%';
            document.getElementById('progress-bar').style.width = percent + '%';
            document.getElementById('progress-bar').textContent = percent + '%';
        }

        async function checkSystemStatus() {
            try {
                const response = await fetch('/_dash/status');
                const data = await response.json();
                
                document.getElementById('status-backend').textContent = data.backend.ok ? '✓ Online' : '✗ Offline';
                document.getElementById('status-backend').style.color = data.backend.ok ? '#00ff00' : '#ff0000';
                document.getElementById('backend-status').className = data.backend.ok ? 'status-indicator status-online' : 'status-indicator status-offline';
                
                // Get AI status through proxy
                const aiResponse = await fetch('/_dash/backend/status');
                const aiData = await aiResponse.json();
                if (aiData.ai_providers) {
                    const aiProviders = aiData.ai_providers;
                    document.getElementById('status-ai').textContent = `${aiProviders.active_count}/${aiProviders.total_count}`;
                }
                
            } catch (error) {
                document.getElementById('status-backend').textContent = '✗ Error';
                document.getElementById('status-backend').style.color = '#ff0000';
            }
        }

        async function loadOpenClawSkills() {
            try {
                const response = await fetch('/_dash/openclaw/skills');
                const data = await response.json();
                if (data.success && data.skills) {
                    const container = document.getElementById('openclaw-skills');
                    container.innerHTML = '';
                    Object.values(data.skills).flat().slice(0, 15).forEach(skill => {
                        const btn = document.createElement('button');
                        btn.className = 'skill-btn';
                        btn.textContent = skill;
                        btn.onclick = () => runSkill(skill);
                        container.appendChild(btn);
                    });
                    document.getElementById('status-openclaw').textContent = '✓ Online';
                    document.getElementById('status-openclaw').style.color = '#00ff00';
                    document.getElementById('openclaw-status').textContent = `${data.total} skills`;
                }
            } catch (error) {
                document.getElementById('status-openclaw').textContent = '✗ Offline';
                document.getElementById('status-openclaw').style.color = '#ff0000';
            }
        }

        async function runSkill(skillName) {
            addLog(`[OPENCLAW] Running skill: ${skillName}`);
            addMessage('system', `Executing OpenClaw skill: ${skillName}`);
            // Implementation would call backend OpenClaw endpoint
        }

        async function startReconAttack(target) {
            addLog('[RECON] Starting reconnaissance...');
            updateProgress('Reconnaissance', 30);
            
            try {
                const response = await fetch('/_dash/recon/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ target })
                });
                const data = await response.json();
                document.getElementById('recon-output').textContent = JSON.stringify(data, null, 2);
                updateProgress('Reconnaissance Complete', 100);
                addLog('[RECON] Complete');
            } catch (error) {
                addLog(`[RECON] Error: ${error.message}`);
            }
        }

        function startAIAutonomous(target) {
            addLog('[AI] Starting autonomous AI attack...');
            updateProgress('AI Autonomous Mode', 50);
            addMessage('lilith', `Analyzing target: ${target}. Initiating autonomous attack chain...`);
        }

        function startPayloadAttack(target) {
            addLog('[PAYLOAD] Engineering payload...');
            updateProgress('Payload Generation', 40);
        }

        function startBrowserHijack(target) {
            addLog('[BROWSER] Initiating browser hijack...');
            updateProgress('Browser Hijack', 60);
        }

        function startWebAttack(target) {
            addLog('[WEB] Starting web application attack...');
            updateProgress('Web Attack', 70);
        }

        function startSocialEngineering(target) {
            addLog('[SOCIAL] Generating social engineering content...');
            updateProgress('Social Engineering', 55);
        }

        function browserNavigate() {
            const url = document.getElementById('browser-url').value;
            addLog(`[BROWSER] Navigating to: ${url}`);
            document.getElementById('browser-output').textContent = `Navigating to ${url}...`;
        }

        function startRecon() {
            const target = document.getElementById('recon-target').value;
            startReconAttack(target);
        }

        async function generatePayload() {
            const type = document.getElementById('payload-type').value;
            const target = document.getElementById('payload-target').value;
            addLog(`[PAYLOAD] Generating ${type} payload for ${target}`);
            
            try {
                const response = await fetch('/_dash/payload/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ type, target })
                });
                const data = await response.json();
                document.getElementById('payload-output').textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                addLog(`[PAYLOAD] Error: ${error.message}`);
            }
        }

        function emergencyStop() {
            if (confirm('⚠️ EMERGENCY STOP - This will halt all active attacks. Continue?')) {
                addLog('[EMERGENCY] ALL ATTACKS STOPPED');
                addMessage('system', 'EMERGENCY STOP ACTIVATED - All operations halted');
                updateProgress('Stopped', 0);
                selectedAttackMode = null;
                document.querySelectorAll('.attack-mode-btn').forEach(btn => btn.classList.remove('active'));
            }
        }

        // Coding Agent Functions
        async function checkCodingAgent() {
            try {
                const response = await fetch('/_dash/coding/status');
                const data = await response.json();
                if (data.available) {
                    document.getElementById('coding-status').textContent = '✓ Available';
                    document.getElementById('coding-status').style.color = '#00ff00';
                } else {
                    document.getElementById('coding-status').textContent = '✗ Unavailable';
                    document.getElementById('coding-status').style.color = '#ff0000';
                }
            } catch (error) {
                document.getElementById('coding-status').textContent = '✗ Error';
            }
        }

        async function generateCode() {
            const prompt = document.getElementById('coding-prompt').value;
            if (!prompt) {
                addLog('[CODING] Please enter a code generation request');
                return;
            }

            addLog('[CODING] Generating code...');
            document.getElementById('coding-output').textContent = 'Generating code...';

            try {
                const response = await fetch('/_dash/coding/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt })
                });
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('coding-output').textContent = data.output || JSON.stringify(data, null, 2);
                    addLog('[CODING] Code generated successfully');
                } else {
                    document.getElementById('coding-output').textContent = `Error: ${data.error || 'Failed to generate code'}`;
                    addLog('[CODING] Code generation failed');
                }
            } catch (error) {
                document.getElementById('coding-output').textContent = `Error: ${error.message}`;
                addLog(`[CODING] Error: ${error.message}`);
            }
        }

        // Learning Functions
        async function loadLearningData() {
            try {
                // Get stats
                const statsResponse = await fetch('/_dash/learning/stats');
                const stats = await statsResponse.json();
                
                if (stats.success !== false) {
                    document.getElementById('learning-attacks').textContent = stats.total_attacks || 0;
                    document.getElementById('learning-success').textContent = (stats.success_rate || 0) + '%';
                    document.getElementById('learning-insights-count').textContent = stats.total_insights || 0;
                }

                // Get insights
                const insightsResponse = await fetch('/_dash/learning/insights');
                const insights = await insightsResponse.json();
                
                if (insights.insights) {
                    const output = document.getElementById('learning-insights');
                    output.innerHTML = '';
                    insights.insights.forEach(insight => {
                        output.innerHTML += `[${insight.timestamp}] ${insight.category}: ${insight.insight}\\n`;
                    });
                } else {
                    document.getElementById('learning-insights').textContent = 'No insights available yet';
                }

                addLog('[LEARNING] Learning data loaded');
            } catch (error) {
                addLog(`[LEARNING] Error loading data: ${error.message}`);
            }
        }

        // Memory Functions
        async function saveMemory() {
            const content = document.getElementById('memory-input').value;
            if (!content) {
                addLog('[MEMORY] Please enter content to save');
                return;
            }

            try {
                const response = await fetch('/_dash/memory/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        content: content,
                        timestamp: new Date().toISOString(),
                        target: currentTarget
                    })
                });
                const data = await response.json();
                
                if (data.success) {
                    addLog('[MEMORY] Saved to attack memory');
                    document.getElementById('memory-input').value = '';
                    addMessage('system', 'Memory saved successfully');
                } else {
                    addLog('[MEMORY] Failed to save');
                }
            } catch (error) {
                addLog(`[MEMORY] Error: ${error.message}`);
            }
        }

        async function recallMemory() {
            addLog('[MEMORY] Recalling memories...');
            
            try {
                const response = await fetch('/_dash/memory/recall');
                const data = await response.json();
                
                if (data.success && data.memories) {
                    const output = document.getElementById('memory-output');
                    if (data.memories.length === 0) {
                        output.textContent = 'No memories stored yet';
                    } else {
                        output.innerHTML = '';
                        data.memories.forEach(mem => {
                            output.innerHTML += `[${mem.timestamp}] ${mem.content}\\n\\n`;
                        });
                    }
                    addLog('[MEMORY] Memories recalled');
                } else {
                    document.getElementById('memory-output').textContent = 'No memories available';
                }
            } catch (error) {
                document.getElementById('memory-output').textContent = `Error: ${error.message}`;
                addLog(`[MEMORY] Error: ${error.message}`);
            }
        }

        // Add welcome message
        setTimeout(() => {
            addMessage('lilith', 'LILITH AI Attack Assistant online. All systems operational. Ready for tasking.');
            addMessage('lilith', '🧠 Learning system active | 💾 Memory system ready | 👨‍💻 Coding agent available');
        }, 1000);

        // Harvesting Functions
        let harvestInterval = null;

        async function startHarvesting() {
            const provider = document.getElementById('harvest-provider').value;
            const btn = document.getElementById('harvest-btn');
            
            btn.disabled = true;
            btn.textContent = '⏳ HARVESTING IN PROGRESS...';
            
            addLog(`[HARVESTER] Starting autonomous harvesting for ${provider}`);
            
            try {
                const response = await fetch('/_dash/harvest/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ provider })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    addLog('[HARVESTER] Harvesting initiated successfully');
                    
                    // Start polling for status updates
                    harvestInterval = setInterval(updateHarvestStatus, 1000);
                } else {
                    addLog(`[HARVESTER] Error: ${data.error}`);
                    btn.disabled = false;
                    btn.textContent = '🚀 START AUTONOMOUS HARVESTING';
                }
            } catch (error) {
                addLog(`[HARVESTER] Error: ${error.message}`);
                btn.disabled = false;
                btn.textContent = '🚀 START AUTONOMOUS HARVESTING';
            }
        }

        async function updateHarvestStatus() {
            try {
                const response = await fetch('/_dash/harvest/status');
                const status = await response.json();
                
                // Update status display
                document.getElementById('harvest-status').textContent = status.active ? 'Active' : 'Idle';
                document.getElementById('harvest-phase').textContent = status.phase || '-';
                document.getElementById('harvest-progress').textContent = status.progress + '%';
                document.getElementById('harvest-progress-bar').style.width = status.progress + '%';
                document.getElementById('harvest-progress-bar').textContent = status.progress + '%';
                
                // Update log
                const logDiv = document.getElementById('harvest-log');
                logDiv.textContent = status.logs.join('\\n');
                logDiv.scrollTop = logDiv.scrollHeight;
                
                // Check if complete
                if (!status.active && status.progress === 100) {
                    clearInterval(harvestInterval);
                    document.getElementById('harvest-btn').disabled = false;
                    document.getElementById('harvest-btn').textContent = '🚀 START AUTONOMOUS HARVESTING';
                    
                    addLog('[HARVESTER] ✓ Harvesting complete!');
                    if (status.api_key) {
                        addMessage('system', `API Key harvested successfully: ${status.api_key.substring(0, 20)}...`);
                        addMessage('system', 'Click "APPLY KEYS TO SESSION" to activate');
                        loadHarvestedKeys();
                    }
                } else if (status.error) {
                    clearInterval(harvestInterval);
                    document.getElementById('harvest-btn').disabled = false;
                    document.getElementById('harvest-btn').textContent = '🚀 START AUTONOMOUS HARVESTING';
                    addLog(`[HARVESTER] ✗ Error: ${status.error}`);
                }
            } catch (error) {
                console.error('Status update error:', error);
            }
        }

        async function loadHarvestedKeys() {
            try {
                const response = await fetch('/_dash/harvest/keys');
                const data = await response.json();
                
                const listDiv = document.getElementById('harvested-keys-list');
                if (data.keys && data.keys.length > 0) {
                    listDiv.innerHTML = data.keys.map(k => 
                        `<div style="padding: 3px; border-bottom: 1px solid #333;">
                            <span style="color: #00ff00;">✓</span> 
                            <strong>${k.provider}</strong>: ${k.key.substring(0, 15)}... 
                            <span style="color: #666; font-size: 10px;">(${k.harvested_at})</span>
                        </div>`
                    ).join('');
                } else {
                    listDiv.innerHTML = '<div style="color: #666;">No keys harvested yet</div>';
                }
            } catch (error) {
                document.getElementById('harvested-keys-list').innerHTML = '<div style="color: #ff0000;">Error loading keys</div>';
            }
        }

        async function applyHarvestedKeys() {
            addLog('[SYSTEM] Applying harvested keys to active session...');
            
            try {
                const response = await fetch('/_dash/harvest/apply', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    addLog('[SYSTEM] ✓ Keys applied successfully!');
                    addLog(`[SYSTEM] Active providers: ${data.active_count}/${data.total_count}`);
                    addMessage('system', 'API keys loaded into session. AI providers are now active!');
                    checkSystemStatus();
                } else {
                    addLog(`[SYSTEM] ✗ Error: ${data.error}`);
                }
            } catch (error) {
                addLog(`[SYSTEM] ✗ Error: ${error.message}`);
            }
        }

        async function restartBackend() {
            addLog('[SYSTEM] Restarting backend services...');
            
            try {
                const response = await fetch('/_dash/system/restart', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    addLog('[SYSTEM] ✓ Backend restart initiated');
                    addMessage('system', 'Backend restarting... Please wait 5 seconds.');
                    
                    setTimeout(() => {
                        checkSystemStatus();
                        addLog('[SYSTEM] ✓ Backend restart complete');
                    }, 5000);
                } else {
                    addLog(`[SYSTEM] ✗ Error: ${data.error}`);
                }
            } catch (error) {
                addLog(`[SYSTEM] ✗ Error: ${error.message}`);
            }
        }

        // Load harvested keys on page load
        setTimeout(loadHarvestedKeys, 2000);

        // ==================== ADVANCED CAPABILITIES FUNCTIONS ====================
        
        function showAdvancedResult(data) {
            const resultsEl = document.getElementById('advanced-results');
            resultsEl.textContent = JSON.stringify(data, null, 2);
        }

        async function runPassiveRecon() {
            const target = document.getElementById('recon-target').value;
            if (!target) { alert('Enter target domain'); return; }
            
            showAdvancedResult({status: 'Running passive recon on ' + target + '...'});
            
            try {
                const response = await fetch('/_dash/capabilities/recon/passive', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({target: target})
                });
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function runActiveRecon() {
            const target = document.getElementById('recon-target').value;
            if (!target) { alert('Enter target domain'); return; }
            
            showAdvancedResult({status: 'Running active recon on ' + target + '...'});
            
            try {
                const response = await fetch('/_dash/capabilities/recon/active', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({target: target})
                });
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function runFullRecon() {
            const target = document.getElementById('recon-target').value;
            if (!target) { alert('Enter target domain'); return; }
            
            showAdvancedResult({status: 'Running FULL recon suite on ' + target + '...'});
            
            try {
                const response = await fetch('/_dash/capabilities/recon/full', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({target: target})
                });
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function genPhishing() {
            const name = document.getElementById('phish-name').value || 'Target User';
            const company = document.getElementById('phish-company').value || 'Target Company';
            
            showAdvancedResult({status: 'Generating phishing campaign...'});
            
            try {
                const response = await fetch('/_dash/capabilities/nlp/phishing', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({target_info: {name, company}})
                });
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function genVishing() {
            const name = document.getElementById('phish-name').value || 'Target User';
            const company = document.getElementById('phish-company').value || 'Target Company';
            
            try {
                const response = await fetch('/_dash/capabilities/nlp/vishing', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({target_info: {name, company}})
                });
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function runAnomalyDetection() {
            let data;
            try {
                data = JSON.parse(document.getElementById('ml-data').value || '[]');
            } catch (e) {
                showAdvancedResult({error: 'Invalid JSON data'});
                return;
            }
            
            try {
                const response = await fetch('/_dash/capabilities/ml/anomaly', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({data: data})
                });
                const result = await response.json();
                showAdvancedResult(result);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function analyzeHash() {
            const hash = document.getElementById('hash-input').value;
            if (!hash) { alert('Enter a hash to analyze'); return; }
            
            try {
                const response = await fetch('/_dash/capabilities/crypto/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({hash: hash})
                });
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function generateKeys() {
            try {
                const response = await fetch('/_dash/capabilities/crypto/keygen', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({algorithm: 'AES', bits: 256})
                });
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function generateExploit() {
            const vulnType = document.getElementById('exploit-type').value;
            
            try {
                const response = await fetch('/_dash/capabilities/exploit/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({vuln_type: vulnType, target_info: {}})
                });
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function getEvasionTechniques() {
            try {
                const response = await fetch('/_dash/capabilities/evasion/techniques');
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function getPersistence() {
            try {
                const response = await fetch('/_dash/capabilities/persistence/methods?os=linux');
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function getWirelessAttacks() {
            try {
                const response = await fetch('/_dash/capabilities/wireless/attacks');
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function getPhysicalBypass() {
            try {
                const response = await fetch('/_dash/capabilities/physical/bypass');
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function analyzeSupplyChain() {
            const target = document.getElementById('supply-target').value || 'target';
            
            try {
                const response = await fetch('/_dash/capabilities/supply-chain/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({target: target})
                });
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function getZeroDayMethodology() {
            try {
                const response = await fetch('/_dash/capabilities/zeroday/methodology');
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(MASTER_TEMPLATE, backend_url=BACKEND_URL)

@app.route("/_dash/status")
def api_status():
    data = {"backend": None}
    try:
        r = requests.get(f"{BACKEND_URL}/status", timeout=2)
        data["backend"] = {"ok": r.status_code == 200, "status_code": r.status_code}
    except Exception as e:
        data["backend"] = {"ok": False, "error": str(e)}
    data["openclaw_canvas"] = OPENCLAW_CANVAS
    return jsonify(data)

@app.route('/_dash/ai/chat', methods=['POST'])
def ai_chat():
    data = request.json or {}
    message = data.get('message', '')
    if not message:
        return jsonify({'success': False, 'response': 'No message provided'})

    # Try backend first
    try:
        backend_response = requests.post(
            f"{BACKEND_URL}/chat",
            json={'message': message},
            timeout=30
        )
        if backend_response.status_code == 200:
            backend_data = backend_response.json()
            return jsonify({
                'success': backend_data.get('success', False),
                'response': backend_data.get('response', ''),
                'provider': backend_data.get('provider'),
                'model': backend_data.get('model')
            })
    except Exception as e:
        print(f"Backend chat error: {e}")
    
    return jsonify({'success': False, 'response': 'No AI providers available. Please add API keys using the harvester or manually.'})

@app.route('/_dash/recon/start', methods=['POST'])
def recon_start():
    data = request.json or {}
    target = data.get('target', '')
    
    if not target:
        return jsonify({'success': False, 'error': 'No target specified'})
    
    try:
        # Perform basic recon
        import socket
        
        results = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'dns': {},
            'ports': []
        }
        
        # Try to resolve hostname
        try:
            ip = socket.gethostbyname(target)
            results['dns']['ip'] = ip
            results['dns']['resolved'] = True
        except:
            results['dns']['resolved'] = False
            results['dns']['error'] = 'Could not resolve hostname'
        
        # Check common ports
        common_ports = [21, 22, 80, 443, 3306, 8080]
        for port in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target, port))
            if result == 0:
                results['ports'].append({'port': port, 'state': 'open'})
            sock.close()
        
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/payload/generate', methods=['POST'])
def payload_generate():
    data = request.json or {}
    payload_type = data.get('type', 'xss')
    target = data.get('target', '')
    
    return jsonify({
        'success': True,
        'payload': f'<script>/* {payload_type.upper()} payload for {target} */</ script>',
        'type': payload_type
    })

@app.route('/_dash/learning/stats', methods=['GET'])
def learning_stats():
    """Get LILITH learning statistics"""
    try:
        response = requests.get(f"{BACKEND_URL}/learning/stats", timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/learning/insights', methods=['GET'])
def learning_insights():
    """Get LILITH learning insights"""
    try:
        response = requests.get(f"{BACKEND_URL}/learning/insights", timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/coding/status', methods=['GET'])
def coding_status():
    """Get coding agent status"""
    try:
        response = requests.get(f"{BACKEND_URL}/coding_agent/status", timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/coding/generate', methods=['POST'])
def coding_generate():
    """Generate code using coding agent"""
    data = request.json or {}
    prompt = data.get('prompt', '')
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/skill/run",
            json={'skill': 'coding-agent', 'task': prompt},
            timeout=60
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/memory/save', methods=['POST'])
def memory_save():
    """Save to attack memory"""
    data = request.json or {}
    
    return jsonify({
        'success': True,
        'message': 'Memory saved',
        'data': data
    })

@app.route('/_dash/memory/recall', methods=['GET'])
def memory_recall():
    """Recall from attack memory"""
    return jsonify({
        'success': True,
        'memories': []
    })

@app.route('/_dash/backend/status', methods=['GET'])
def backend_status():
    """Proxy backend status to avoid CORS"""
    try:
        response = requests.get(f"{BACKEND_URL}/status", timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e), 'ai_providers': {'active_count': 0, 'total_count': 0}})

@app.route('/_dash/openclaw/skills', methods=['GET'])
def openclaw_skills():
    """Proxy OpenClaw skills to avoid CORS"""
    try:
        response = requests.get(f"{BACKEND_URL}/openclaw/redteam-skills", timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/harvest/start', methods=['POST'])
def start_harvest():
    """Start autonomous API key harvesting"""
    try:
        sys.path.insert(0, '/app/tools')
        from harvest_integration import start_harvesting_thread
        
        data = request.json or {}
        provider = data.get('provider', 'groq')
        
        success = start_harvesting_thread(provider)
        
        if success:
            return jsonify({'success': True, 'message': f'Harvesting started for {provider}'})
        else:
            return jsonify({'success': False, 'error': 'Harvesting already in progress'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/harvest/status', methods=['GET'])
def harvest_status():
    """Get harvesting status"""
    try:
        sys.path.insert(0, '/app/tools')
        from harvest_integration import get_harvest_status
        
        status = get_harvest_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'active': False, 'error': str(e), 'logs': [], 'progress': 0})

@app.route('/_dash/harvest/keys', methods=['GET'])
def get_harvested_keys():
    """Get list of harvested API keys"""
    try:
        import json
        keys_path = '/app/config/harvested_keys.json'
        
        if os.path.exists(keys_path):
            with open(keys_path, 'r') as f:
                keys = json.load(f)
            return jsonify({'success': True, 'keys': keys})
        else:
            return jsonify({'success': True, 'keys': []})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'keys': []})

@app.route('/_dash/harvest/apply', methods=['POST'])
def apply_harvested_keys():
    """Apply harvested keys to the running backend session"""
    try:
        import json
        keys_path = '/app/config/harvested_keys.json'
        
        if not os.path.exists(keys_path):
            return jsonify({'success': False, 'error': 'No harvested keys found'})
        
        with open(keys_path, 'r') as f:
            keys = json.load(f)
        
        if not keys:
            return jsonify({'success': False, 'error': 'No keys in database'})
        
        # Apply keys to the backend
        applied_count = 0
        for key_data in keys:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/keys/add",
                    json={
                        'provider': key_data['provider'],
                        'api_key': key_data['key']
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    applied_count += 1
            except:
                pass
        
        # Get updated status
        try:
            status_resp = requests.get(f"{BACKEND_URL}/status", timeout=5)
            status_data = status_resp.json()
            active_count = status_data.get('ai_providers', {}).get('active_count', 0)
            total_count = status_data.get('ai_providers', {}).get('total_count', 0)
        except:
            active_count = applied_count
            total_count = len(keys)
        
        return jsonify({
            'success': True,
            'applied': applied_count,
            'total': len(keys),
            'active_count': active_count,
            'total_count': total_count
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/system/restart', methods=['POST'])
def restart_backend():
    """Restart the backend service"""
    try:
        import subprocess
        
        # Restart the backend via pkill and restart
        subprocess.run(['pkill', '-f', 'lilith_full_backend'], capture_output=True)
        
        # Start it again
        subprocess.Popen(
            ['/root/.venv/bin/python3', '/app/tools/lilith_full_backend.py'],
            env={**os.environ, 'BACKEND_HOST': '0.0.0.0', 'BACKEND_PORT': '5000'},
            cwd='/app',
            stdout=open('/app/backend_out.log', 'w'),
            stderr=open('/app/backend_err.log', 'w')
        )
        
        return jsonify({'success': True, 'message': 'Backend restart initiated'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("WEB_DASHBOARD_PORT", "3000"))
    host = os.environ.get("WEB_DASHBOARD_HOST", "0.0.0.0")
    print(f"Starting LUCIFEROS Master Dashboard on http://{host}:{port}/")
    try:
        app.run(host=host, port=port, debug=False, threaded=True)
    except Exception as exc:
        print("Failed to start dashboard:", exc)
