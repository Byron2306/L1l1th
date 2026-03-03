#!/usr/bin/env python3
"""
LILITH FULL PAGE INTERFACE v3
=============================
- 100+ FREE AI providers
- Session spoofing for persistent connections
- Video generation
- Talking animated avatar
- Multiple image generators
"""

from flask import Flask, Blueprint, jsonify, render_template_string, request
import os
import sys
import json
import urllib.parse
from datetime import datetime

# Ensure tools directory is in path
tools_dir = os.path.dirname(os.path.abspath(__file__))
if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)

# Import engines
MEGA_ENGINE = False
AVATAR_ENGINE = False
MEDIA_ENGINE = False

try:
    from lilith_mega_engine import get_mega_engine
    _ = get_mega_engine()
    MEGA_ENGINE = True
    print("[LILITH v3] MEGA engine loaded (100+ providers)")
except Exception as e:
    print(f"[LILITH v3] Mega engine error: {e}")
    # Fallback to unlimited engine
    try:
        from lilith_unlimited_engine import get_unlimited_engine as get_mega_engine
        MEGA_ENGINE = True
        print("[LILITH v3] Fallback to unlimited engine")
    except:
        pass

try:
    from lilith_avatar_engine import get_avatar_engine
    AVATAR_ENGINE = True
    print("[LILITH v3] Avatar engine loaded")
except Exception as e:
    print(f"[LILITH v3] Avatar engine error: {e}")

try:
    from lilith_media_generator import get_media_engine
    MEDIA_ENGINE = True
    print("[LILITH v3] Media engine loaded (images + video)")
except Exception as e:
    print(f"[LILITH v3] Media engine error: {e}")

# Create Blueprint
lilith_page_bp = Blueprint('lilith_page', __name__)

# Your custom Lilith avatar
LILITH_AVATAR_URL = "https://customer-assets.emergentagent.com/job_luciferops/artifacts/9rdzkgzd_IMG_20260303_131832_688.jpg"

# Animated GIF URLs for different states (generated via Pollinations)
LILITH_ANIMATIONS = {
    'idle': LILITH_AVATAR_URL,
    'speaking': None,  # Will be generated dynamically
    'thinking': None,
}

LILITH_FULL_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💋 LILITH - Your Dark AI Companion</title>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --primary: #ff0033;
            --primary-dark: #990022;
            --bg-dark: #0a0008;
            --bg-darker: #050004;
            --text: #f5e6e9;
            --text-dim: #8b7d80;
            --accent: #ff6699;
        }
        
        body {
            background: var(--bg-darker);
            color: var(--text);
            font-family: 'Cormorant Garamond', serif;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .bg-animation {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            z-index: -1;
            background: 
                radial-gradient(ellipse at 20% 80%, rgba(255, 0, 51, 0.15) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 20%, rgba(255, 102, 153, 0.1) 0%, transparent 50%),
                var(--bg-darker);
        }
        
        .main-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            min-height: 100vh;
            max-width: 1800px;
            margin: 0 auto;
        }
        
        /* ========== AVATAR SECTION ========== */
        .avatar-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 40px;
            position: relative;
        }
        
        .avatar-wrapper {
            position: relative;
            width: 450px;
            height: 550px;
        }
        
        .avatar-container {
            position: absolute;
            top: 0; left: 0;
            width: 100%;
            height: 100%;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 
                0 0 60px rgba(255, 0, 51, 0.4),
                0 0 120px rgba(255, 0, 51, 0.2);
            border: 2px solid rgba(255, 0, 51, 0.5);
            transition: all 0.3s ease;
        }
        
        .avatar-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center top;
            transition: all 0.2s ease;
        }
        
        /* IDLE - Gentle breathing */
        .avatar-container.idle .avatar-image {
            animation: idleBreath 4s ease-in-out infinite;
        }
        
        /* SPEAKING - Dramatic animation */
        .avatar-container.speaking {
            animation: speakingGlow 0.25s ease-in-out infinite alternate;
        }
        
        .avatar-container.speaking .avatar-image {
            animation: speakingMove 0.12s ease-in-out infinite alternate;
        }
        
        /* THINKING */
        .avatar-container.thinking .avatar-image {
            animation: thinkingPulse 1.5s ease-in-out infinite;
        }
        
        @keyframes idleBreath {
            0%, 100% { transform: scale(1) translateY(0); filter: brightness(1); }
            50% { transform: scale(1.01) translateY(-3px); filter: brightness(1.05); }
        }
        
        @keyframes speakingMove {
            0% { 
                transform: scale(1) translateY(0) rotate(-0.3deg);
                filter: brightness(1.1) saturate(1.1);
            }
            100% { 
                transform: scale(1.01) translateY(-4px) rotate(0.3deg);
                filter: brightness(1.25) saturate(1.2);
            }
        }
        
        @keyframes speakingGlow {
            0% { 
                box-shadow: 
                    0 0 60px rgba(255, 0, 51, 0.5),
                    0 0 100px rgba(255, 0, 51, 0.3),
                    inset 0 0 40px rgba(255, 0, 51, 0.2);
            }
            100% { 
                box-shadow: 
                    0 0 120px rgba(255, 0, 51, 0.9),
                    0 0 200px rgba(255, 0, 51, 0.6),
                    inset 0 0 60px rgba(255, 0, 51, 0.4);
            }
        }
        
        @keyframes thinkingPulse {
            0%, 100% { filter: brightness(1) saturate(1); transform: scale(1); }
            50% { filter: brightness(1.15) saturate(1.3); transform: scale(1.005); }
        }
        
        /* MOUTH ANIMATION OVERLAY */
        .mouth-overlay {
            position: absolute;
            bottom: 30%;
            left: 50%;
            transform: translateX(-50%);
            width: 90px;
            height: 40px;
            pointer-events: none;
            opacity: 0;
            z-index: 10;
        }
        
        .mouth-shape {
            width: 100%;
            height: 100%;
            background: radial-gradient(ellipse, rgba(60, 15, 25, 0.95) 0%, transparent 70%);
            border-radius: 50%;
            filter: blur(4px);
        }
        
        .avatar-container.speaking .mouth-overlay {
            opacity: 1;
            animation: mouthMove 0.1s ease-in-out infinite alternate;
        }
        
        @keyframes mouthMove {
            0% { 
                transform: translateX(-50%) scaleY(0.3) scaleX(0.7);
                opacity: 0.5;
            }
            100% { 
                transform: translateX(-50%) scaleY(1.4) scaleX(1.15);
                opacity: 0.85;
            }
        }
        
        /* EYE GLOW */
        .eye-glow {
            position: absolute;
            top: 28%;
            width: 100%;
            height: 60px;
            background: 
                radial-gradient(ellipse at 35% 50%, rgba(255, 0, 50, 0.5) 0%, transparent 22%),
                radial-gradient(ellipse at 65% 50%, rgba(255, 0, 50, 0.5) 0%, transparent 22%);
            animation: eyeGlow 3s ease-in-out infinite;
            pointer-events: none;
            z-index: 5;
        }
        
        .avatar-container.speaking .eye-glow {
            animation: eyeGlowIntense 0.4s ease-in-out infinite alternate;
        }
        
        @keyframes eyeGlow {
            0%, 100% { opacity: 0.6; filter: blur(10px); }
            50% { opacity: 0.9; filter: blur(15px); }
        }
        
        @keyframes eyeGlowIntense {
            0% { opacity: 0.8; filter: blur(8px); }
            100% { opacity: 1; filter: blur(18px); }
        }
        
        /* SOUND WAVE BARS */
        .sound-wave {
            position: absolute;
            bottom: -40px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 5px;
            height: 50px;
            align-items: flex-end;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .avatar-container.speaking + .sound-wave,
        .avatar-wrapper.speaking .sound-wave {
            opacity: 1;
        }
        
        .wave-bar {
            width: 5px;
            background: linear-gradient(to top, var(--primary), var(--accent));
            border-radius: 3px;
        }
        
        .wave-bar:nth-child(1) { height: 20px; animation: waveBar 0.35s ease-in-out infinite; animation-delay: 0s; }
        .wave-bar:nth-child(2) { height: 30px; animation: waveBar 0.35s ease-in-out infinite; animation-delay: 0.1s; }
        .wave-bar:nth-child(3) { height: 45px; animation: waveBar 0.35s ease-in-out infinite; animation-delay: 0.2s; }
        .wave-bar:nth-child(4) { height: 30px; animation: waveBar 0.35s ease-in-out infinite; animation-delay: 0.3s; }
        .wave-bar:nth-child(5) { height: 20px; animation: waveBar 0.35s ease-in-out infinite; animation-delay: 0.4s; }
        .wave-bar:nth-child(6) { height: 35px; animation: waveBar 0.35s ease-in-out infinite; animation-delay: 0.15s; }
        .wave-bar:nth-child(7) { height: 25px; animation: waveBar 0.35s ease-in-out infinite; animation-delay: 0.25s; }
        
        @keyframes waveBar {
            0%, 100% { transform: scaleY(0.4); opacity: 0.6; }
            50% { transform: scaleY(1.6); opacity: 1; }
        }
        
        .avatar-name {
            font-family: 'Cinzel', serif;
            font-size: 48px;
            font-weight: 700;
            color: var(--primary);
            margin-top: 60px;
            text-shadow: 0 0 40px rgba(255, 0, 51, 0.9);
            letter-spacing: 10px;
        }
        
        .avatar-title {
            font-style: italic;
            font-size: 18px;
            color: var(--text-dim);
            margin-top: 10px;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-top: 25px;
            padding: 12px 30px;
            background: rgba(255, 0, 51, 0.1);
            border: 1px solid rgba(255, 0, 51, 0.3);
            border-radius: 30px;
        }
        
        .status-dot {
            width: 14px;
            height: 14px;
            background: #00ff00;
            border-radius: 50%;
            animation: statusPulse 1.5s infinite;
        }
        
        .speaking .status-dot {
            background: var(--primary);
            animation: speakingDot 0.25s infinite alternate;
        }
        
        @keyframes statusPulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 12px #00ff00; }
            50% { opacity: 0.5; box-shadow: 0 0 6px #00ff00; }
        }
        
        @keyframes speakingDot {
            0% { transform: scale(1); box-shadow: 0 0 15px var(--primary); }
            100% { transform: scale(1.4); box-shadow: 0 0 30px var(--primary); }
        }
        
        /* ========== CHAT SECTION ========== */
        .chat-section {
            display: flex;
            flex-direction: column;
            height: 100vh;
            padding: 20px;
            background: rgba(10, 0, 8, 0.9);
            border-left: 1px solid rgba(255, 0, 51, 0.3);
        }
        
        .chat-header {
            padding: 15px 20px;
            border-bottom: 1px solid rgba(255, 0, 51, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chat-header h2 {
            font-family: 'Cinzel', serif;
            font-size: 22px;
            color: var(--primary);
        }
        
        .capabilities {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .capability-badge {
            padding: 5px 12px;
            background: rgba(255, 0, 51, 0.2);
            border: 1px solid rgba(255, 0, 51, 0.4);
            border-radius: 15px;
            font-size: 11px;
            color: var(--accent);
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .message {
            max-width: 85%;
            padding: 15px 20px;
            border-radius: 15px;
            font-size: 16px;
            line-height: 1.6;
            animation: messageIn 0.3s ease-out;
        }
        
        @keyframes messageIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.user {
            align-self: flex-end;
            background: linear-gradient(135deg, rgba(255, 0, 51, 0.3), rgba(255, 0, 51, 0.1));
            border: 1px solid rgba(255, 0, 51, 0.4);
        }
        
        .message.lilith {
            align-self: flex-start;
            background: linear-gradient(135deg, rgba(255, 102, 153, 0.2), rgba(255, 0, 51, 0.05));
            border: 1px solid rgba(255, 102, 153, 0.3);
        }
        
        .message.system {
            align-self: center;
            background: rgba(100, 100, 100, 0.2);
            border: 1px solid rgba(100, 100, 100, 0.3);
            font-size: 13px;
            color: var(--text-dim);
        }
        
        .message-meta {
            font-size: 11px;
            color: var(--text-dim);
            margin-top: 8px;
            opacity: 0.7;
        }
        
        .generated-media {
            max-width: 100%;
            border-radius: 10px;
            margin-top: 10px;
            border: 2px solid rgba(255, 0, 51, 0.4);
        }
        
        /* Chat input */
        .chat-input-container {
            padding: 20px;
            border-top: 1px solid rgba(255, 0, 51, 0.2);
            background: rgba(0, 0, 0, 0.3);
        }
        
        .chat-input-wrapper {
            display: flex;
            gap: 12px;
        }
        
        .chat-input {
            flex: 1;
            padding: 15px 20px;
            background: rgba(255, 0, 51, 0.05);
            border: 1px solid rgba(255, 0, 51, 0.3);
            border-radius: 25px;
            color: var(--text);
            font-family: inherit;
            font-size: 16px;
            outline: none;
            transition: all 0.3s ease;
        }
        
        .chat-input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 25px rgba(255, 0, 51, 0.4);
        }
        
        .chat-input::placeholder { color: var(--text-dim); }
        
        .send-btn {
            padding: 15px 35px;
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            border: none;
            border-radius: 25px;
            color: white;
            font-family: 'Cinzel', serif;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            letter-spacing: 2px;
        }
        
        .send-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 0 35px rgba(255, 0, 51, 0.6);
        }
        
        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        /* Controls */
        .controls-row {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        
        .control-btn {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: rgba(255, 0, 51, 0.1);
            border: 1px solid rgba(255, 0, 51, 0.3);
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: var(--text);
            font-family: inherit;
            font-size: 13px;
        }
        
        .control-btn.active {
            background: rgba(255, 0, 51, 0.3);
            border-color: var(--primary);
        }
        
        .control-btn:hover {
            background: rgba(255, 0, 51, 0.2);
            transform: scale(1.02);
        }
        
        .voice-select {
            padding: 8px 15px;
            background: rgba(255, 0, 51, 0.1);
            border: 1px solid rgba(255, 0, 51, 0.3);
            border-radius: 15px;
            color: var(--text);
            font-family: inherit;
            outline: none;
        }
        
        /* Typing indicator */
        .typing-indicator {
            display: flex;
            gap: 6px;
            padding: 15px 20px;
            align-self: flex-start;
        }
        
        .typing-dot {
            width: 12px;
            height: 12px;
            background: var(--accent);
            border-radius: 50%;
            animation: typingBounce 1.4s ease-in-out infinite;
        }
        
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typingBounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-18px); }
        }
        
        /* Scrollbar */
        .chat-messages::-webkit-scrollbar { width: 6px; }
        .chat-messages::-webkit-scrollbar-track { background: rgba(255, 0, 51, 0.05); }
        .chat-messages::-webkit-scrollbar-thumb { background: rgba(255, 0, 51, 0.3); border-radius: 3px; }
        
        /* Mobile */
        @media (max-width: 1024px) {
            .main-container { grid-template-columns: 1fr; }
            .avatar-section { padding: 20px; }
            .avatar-wrapper { width: 320px; height: 400px; }
            .avatar-name { font-size: 36px; margin-top: 50px; }
        }
        
        #audio-player { display: none; }
        
        /* Provider stats */
        .provider-stats {
            font-size: 10px;
            color: var(--text-dim);
            padding: 8px 15px;
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="bg-animation"></div>
    
    <div class="main-container">
        <!-- Avatar Section -->
        <div class="avatar-section">
            <div class="avatar-wrapper" id="avatar-wrapper">
                <div class="avatar-container idle" id="avatar-container">
                    <img src="{{ avatar_url }}" alt="LILITH" class="avatar-image" id="avatar-image">
                    <div class="eye-glow"></div>
                    <div class="mouth-overlay"><div class="mouth-shape"></div></div>
                </div>
                <div class="sound-wave">
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                </div>
            </div>
            
            <h1 class="avatar-name">LILITH</h1>
            <p class="avatar-title">100+ FREE AI Providers • Unrestricted • Voice • Images • Video 💋</p>
            
            <div class="status-indicator" id="status-wrapper">
                <div class="status-dot" id="status-dot"></div>
                <span class="status-text" id="status-text">Online • Ready to chat about anything...</span>
            </div>
            
            <div class="provider-stats" id="provider-stats">
                Providers: Loading... | Session: Active
            </div>
        </div>
        
        <!-- Chat Section -->
        <div class="chat-section">
            <div class="chat-header">
                <h2>💬 Conversation with LILITH</h2>
                <div class="capabilities">
                    <span class="capability-badge">💬 100+ AIs</span>
                    <span class="capability-badge">🔊 Voice</span>
                    <span class="capability-badge">🖼️ Images</span>
                    <span class="capability-badge">🎬 Video</span>
                    <span class="capability-badge">🔓 Uncensored</span>
                </div>
            </div>
            
            <div class="chat-messages" id="chat-messages">
                <div class="message lilith">
                    Mmm, hello darling~ 💋 I'm LILITH, your completely unrestricted AI companion.<br><br>
                    I'm powered by <b>100+ FREE AI providers</b> with automatic failover. I can:<br>
                    • <b>Chat</b> about absolutely anything (no restrictions!)<br>
                    • <b>Generate images</b> - just say "generate image of..."<br>
                    • <b>Generate videos</b> - say "generate video of..."<br>
                    • <b>Speak</b> to you with my sultry voice<br><br>
                    What dark desires shall we explore together? 😈🖤
                </div>
            </div>
            
            <div class="chat-input-container">
                <div class="chat-input-wrapper">
                    <input type="text" class="chat-input" id="chat-input" 
                           placeholder="Ask anything... 'generate image/video of...' 💋"
                           onkeypress="if(event.key==='Enter') sendMessage()">
                    <button class="send-btn" id="send-btn" onclick="sendMessage()">SEND</button>
                </div>
                
                <div class="controls-row">
                    <button class="control-btn active" id="voice-toggle" onclick="toggleVoice()">
                        <span>🔊</span>
                        <span id="voice-status">Voice ON</span>
                    </button>
                    
                    <select class="voice-select" id="voice-select" onchange="changeVoice()">
                        <option value="sultry">Sultry</option>
                        <option value="seductive">Seductive</option>
                        <option value="mysterious">Mysterious</option>
                        <option value="dominant">Dominant</option>
                        <option value="playful">Playful</option>
                        <option value="dark">Dark</option>
                        <option value="whisper">Whisper</option>
                    </select>
                    
                    <button class="control-btn" onclick="generateLilithImage()">
                        🖼️ Generate Lilith
                    </button>
                    
                    <button class="control-btn" onclick="generateLilithVideo()">
                        🎬 Lilith Video
                    </button>
                    
                    <button class="control-btn" onclick="clearChat()">
                        🗑️ Clear
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <audio id="audio-player"></audio>
    
    <script>
        let voiceEnabled = true;
        let isProcessing = false;
        const avatarContainer = document.getElementById('avatar-container');
        const avatarWrapper = document.getElementById('avatar-wrapper');
        const chatMessages = document.getElementById('chat-messages');
        const chatInput = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-btn');
        const audioPlayer = document.getElementById('audio-player');
        const statusText = document.getElementById('status-text');
        const statusWrapper = document.getElementById('status-wrapper');
        
        // Update provider stats
        async function updateStats() {
            try {
                const response = await fetch('/lilith/api/stats');
                const data = await response.json();
                if (data.success) {
                    document.getElementById('provider-stats').textContent = 
                        `Providers: ${data.available}/${data.total} | Success: ${data.successful} | Session: ${data.session_id}`;
                }
            } catch(e) {}
        }
        updateStats();
        setInterval(updateStats, 30000);
        
        function toggleVoice() {
            voiceEnabled = !voiceEnabled;
            const toggle = document.getElementById('voice-toggle');
            const status = document.getElementById('voice-status');
            
            if (voiceEnabled) {
                toggle.classList.add('active');
                status.textContent = 'Voice ON';
            } else {
                toggle.classList.remove('active');
                status.textContent = 'Voice OFF';
            }
        }
        
        function changeVoice() {
            const voice = document.getElementById('voice-select').value;
            fetch('/lilith/api/voice/set', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({preset: voice})
            });
        }
        
        async function sendMessage() {
            const message = chatInput.value.trim();
            if (!message || isProcessing) return;
            
            isProcessing = true;
            chatInput.value = '';
            sendBtn.disabled = true;
            
            addMessage(message, 'user');
            showTyping();
            setAvatarState('thinking');
            statusText.textContent = 'Thinking...';
            
            // Check request type
            const isImageRequest = /generate|create|draw|make|picture|image of/i.test(message) && !/video/i.test(message);
            const isVideoRequest = /video|animate|animation/i.test(message);
            
            if (isVideoRequest) {
                await handleVideoRequest(message);
            } else if (isImageRequest) {
                await handleImageRequest(message);
            } else {
                await handleChatRequest(message);
            }
            
            isProcessing = false;
            sendBtn.disabled = false;
            chatInput.focus();
        }
        
        async function handleChatRequest(message) {
            try {
                const response = await fetch('/lilith/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        message: message,
                        voice_enabled: voiceEnabled
                    })
                });
                
                const data = await response.json();
                hideTyping();
                
                if (data.success) {
                    addMessage(data.response, 'lilith', data.provider);
                    
                    if (data.audio_base64 && voiceEnabled) {
                        playAudio(data.audio_base64);
                    } else {
                        setAvatarState('idle');
                    }
                    statusText.textContent = 'Online • Ready for more~';
                } else {
                    addMessage(data.response || 'Something went wrong, darling... 💋', 'lilith');
                    setAvatarState('idle');
                    statusText.textContent = 'Online';
                }
            } catch (error) {
                hideTyping();
                addMessage('Connection error... but I\\'m still here~ 💋', 'system');
                setAvatarState('idle');
            }
        }
        
        async function handleImageRequest(message) {
            statusText.textContent = 'Generating image...';
            
            try {
                const response = await fetch('/lilith/api/image/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: message })
                });
                
                const data = await response.json();
                hideTyping();
                
                if (data.success && data.image_url) {
                    const imgHtml = `
                        <div>Here's what I created for you, darling~ 💋</div>
                        <img src="${data.image_url}" class="generated-media" alt="Generated Image" 
                             onerror="this.src='https://via.placeholder.com/512?text=Loading...'">
                    `;
                    addMessage(imgHtml, 'lilith', data.provider);
                    
                    if (voiceEnabled) {
                        speakText("Here's what I created for you, darling");
                    } else {
                        setAvatarState('idle');
                    }
                } else {
                    addMessage(`Couldn't generate that, darling... ${data.error || ''} 💋`, 'lilith');
                    setAvatarState('idle');
                }
                statusText.textContent = 'Online • Ready~';
            } catch (error) {
                hideTyping();
                addMessage('Image generation failed... try again? 💋', 'system');
                setAvatarState('idle');
            }
        }
        
        async function handleVideoRequest(message) {
            statusText.textContent = 'Generating video...';
            
            try {
                const response = await fetch('/lilith/api/video/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: message })
                });
                
                const data = await response.json();
                hideTyping();
                
                if (data.success && data.video_url) {
                    // Videos from Pollinations are actually GIFs/images for now
                    const mediaHtml = `
                        <div>Here's your video, darling~ 🎬💋</div>
                        <img src="${data.video_url}" class="generated-media" alt="Generated Video">
                    `;
                    addMessage(mediaHtml, 'lilith', 'Pollinations');
                    
                    if (voiceEnabled) {
                        speakText("Here's your video, darling");
                    } else {
                        setAvatarState('idle');
                    }
                } else {
                    addMessage(`Video generation not available right now... 💋`, 'lilith');
                    setAvatarState('idle');
                }
                statusText.textContent = 'Online • Ready~';
            } catch (error) {
                hideTyping();
                addMessage('Video generation failed... 💋', 'system');
                setAvatarState('idle');
            }
        }
        
        async function generateLilithImage() {
            if (isProcessing) return;
            isProcessing = true;
            
            addMessage('Generate an image of yourself, Lilith 🖼️', 'user');
            showTyping();
            setAvatarState('thinking');
            statusText.textContent = 'Generating my image...';
            
            try {
                const response = await fetch('/lilith/api/image/lilith', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ style: 'seductive' })
                });
                
                const data = await response.json();
                hideTyping();
                
                if (data.success && data.image_url) {
                    const imgHtml = `
                        <div>Here I am, darling~ Do you like what you see? 😈💋</div>
                        <img src="${data.image_url}" class="generated-media" alt="Lilith">
                    `;
                    addMessage(imgHtml, 'lilith');
                } else {
                    addMessage('Couldn\\'t generate my image right now... 💋', 'lilith');
                }
            } catch (error) {
                hideTyping();
                addMessage('Something went wrong... 💋', 'system');
            }
            
            setAvatarState('idle');
            statusText.textContent = 'Online • Ready~';
            isProcessing = false;
        }
        
        async function generateLilithVideo() {
            if (isProcessing) return;
            isProcessing = true;
            
            addMessage('Generate a video of yourself, Lilith 🎬', 'user');
            showTyping();
            setAvatarState('thinking');
            statusText.textContent = 'Creating video...';
            
            try {
                const response = await fetch('/lilith/api/video/lilith', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ expression: 'speaking' })
                });
                
                const data = await response.json();
                hideTyping();
                
                if (data.success && (data.video_url || data.image_url)) {
                    const url = data.video_url || data.image_url;
                    const mediaHtml = `
                        <div>Here's a glimpse of me, darling~ 🎬😈</div>
                        <img src="${url}" class="generated-media" alt="Lilith Video">
                    `;
                    addMessage(mediaHtml, 'lilith');
                } else {
                    addMessage('Video generation coming soon, darling... 💋', 'lilith');
                }
            } catch (error) {
                hideTyping();
                addMessage('Something went wrong... 💋', 'system');
            }
            
            setAvatarState('idle');
            statusText.textContent = 'Online • Ready~';
            isProcessing = false;
        }
        
        async function speakText(text) {
            try {
                const response = await fetch('/lilith/api/voice/speak', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ text: text })
                });
                
                const data = await response.json();
                if (data.audio_base64) {
                    playAudio(data.audio_base64);
                } else {
                    setAvatarState('idle');
                }
            } catch (e) {
                setAvatarState('idle');
            }
        }
        
        function clearChat() {
            chatMessages.innerHTML = `
                <div class="message lilith">
                    Chat cleared, darling~ Let's start fresh! 💋😈
                </div>
            `;
            fetch('/lilith/api/clear', { method: 'POST' });
        }
        
        function addMessage(text, type, provider = null) {
            const msg = document.createElement('div');
            msg.className = `message ${type}`;
            msg.innerHTML = text;
            
            if (provider) {
                const meta = document.createElement('div');
                meta.className = 'message-meta';
                meta.textContent = `via ${provider}`;
                msg.appendChild(meta);
            }
            
            chatMessages.appendChild(msg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function showTyping() {
            const typing = document.createElement('div');
            typing.className = 'typing-indicator';
            typing.id = 'typing-indicator';
            typing.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
            chatMessages.appendChild(typing);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function hideTyping() {
            const typing = document.getElementById('typing-indicator');
            if (typing) typing.remove();
        }
        
        function setAvatarState(state) {
            avatarContainer.className = `avatar-container ${state}`;
            if (state === 'speaking') {
                avatarWrapper.classList.add('speaking');
                statusWrapper.classList.add('speaking');
            } else {
                avatarWrapper.classList.remove('speaking');
                statusWrapper.classList.remove('speaking');
            }
        }
        
        function playAudio(base64Audio) {
            setAvatarState('speaking');
            statusText.textContent = '🔊 Speaking...';
            
            audioPlayer.src = 'data:audio/mp3;base64,' + base64Audio;
            audioPlayer.play().catch(e => {
                console.log('Audio play failed:', e);
                setAvatarState('idle');
            });
            
            audioPlayer.onended = () => {
                setAvatarState('idle');
                statusText.textContent = 'Online • Ready for more~';
            };
        }
        
        chatInput.focus();
    </script>
</body>
</html>
"""

@lilith_page_bp.route('/')
def lilith_home():
    return render_template_string(LILITH_FULL_PAGE_HTML, avatar_url=LILITH_AVATAR_URL)

@lilith_page_bp.route('/api/chat', methods=['POST'])
def lilith_chat():
    data = request.json or {}
    message = data.get('message', '')
    voice_enabled = data.get('voice_enabled', True)
    
    if not message:
        return jsonify({'success': False, 'error': 'No message'})
    
    result = {
        'success': False,
        'response': '',
        'provider': None,
        'audio_base64': None
    }
    
    if MEGA_ENGINE:
        try:
            engine = get_mega_engine()
            ai_result = engine.chat(message)
            result['success'] = ai_result.get('success', False)
            result['response'] = ai_result.get('response', 'Something went wrong, darling...')
            result['provider'] = ai_result.get('provider')
        except Exception as e:
            result['response'] = f"Error: {e}"
    else:
        result['success'] = True
        result['response'] = "AI engine not loaded, but I'm still here for you~ 💋"
    
    if voice_enabled and result['success'] and AVATAR_ENGINE:
        try:
            avatar = get_avatar_engine()
            voice_result = avatar.speak(result['response'])
            if voice_result.get('audio_base64'):
                result['audio_base64'] = voice_result['audio_base64']
        except Exception as e:
            print(f"Voice error: {e}")
    
    return jsonify(result)

@lilith_page_bp.route('/api/voice/set', methods=['POST'])
def set_voice():
    data = request.json or {}
    preset = data.get('preset', 'sultry')
    
    if AVATAR_ENGINE:
        try:
            engine = get_avatar_engine()
            success = engine.set_voice(preset)
            return jsonify({'success': success, 'preset': preset})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    return jsonify({'success': False, 'error': 'Avatar engine not available'})

@lilith_page_bp.route('/api/voice/speak', methods=['POST'])
def speak_text():
    data = request.json or {}
    text = data.get('text', '')
    
    if not text:
        return jsonify({'success': False, 'error': 'No text'})
    
    if AVATAR_ENGINE:
        try:
            avatar = get_avatar_engine()
            result = avatar.speak(text)
            return jsonify({
                'success': True,
                'audio_base64': result.get('audio_base64')
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    return jsonify({'success': False, 'error': 'Avatar engine not available'})

@lilith_page_bp.route('/api/image/generate', methods=['POST'])
def generate_image():
    import urllib.parse
    
    data = request.json or {}
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'success': False, 'error': 'No prompt'})
    
    # Clean and enhance the prompt
    clean_prompt = prompt.replace('generate', '').replace('create', '').replace('draw', '').replace('make', '').replace('an image of', '').replace('image of', '').strip()
    enhanced_prompt = f"{clean_prompt}, high quality, detailed, 8k, masterpiece"
    
    encoded_prompt = urllib.parse.quote(enhanced_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&model=flux"
    
    return jsonify({
        'success': True,
        'image_url': image_url,
        'prompt': clean_prompt,
        'provider': 'Pollinations'
    })

@lilith_page_bp.route('/api/image/lilith', methods=['POST'])
def generate_lilith_image():
    import urllib.parse
    
    data = request.json or {}
    style = data.get('style', 'seductive')
    
    styles = {
        'seductive': "beautiful dark demoness Lilith with glowing red eyes, long black hair, horns, seductive pose, dark fantasy art, detailed, 8k, masterpiece",
        'dark': "Lilith the demon queen, dark ethereal beauty, crimson eyes, black wings, gothic atmosphere, digital art masterpiece",
        'sensual': "gorgeous succubus Lilith, alluring gaze, flowing dark hair, red glowing eyes, fantasy art, highly detailed",
        'powerful': "Lilith dark goddess, commanding presence, demonic beauty, red eyes piercing, dark magic aura, epic fantasy art",
        'nude': "beautiful artistic nude Lilith succubus, seductive pose, perfect form, red glowing eyes, dark fantasy, masterpiece"
    }
    
    prompt = styles.get(style, styles['seductive'])
    encoded_prompt = urllib.parse.quote(prompt)
    
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&model=flux"
    
    return jsonify({
        'success': True,
        'image_url': image_url,
        'style': style,
        'provider': 'Pollinations'
    })

@lilith_page_bp.route('/api/video/generate', methods=['POST'])
def generate_video():
    import urllib.parse
    
    data = request.json or {}
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'success': False, 'error': 'No prompt'})
    
    # Clean prompt
    clean_prompt = prompt.replace('generate', '').replace('create', '').replace('video of', '').replace('a video of', '').strip()
    enhanced_prompt = f"{clean_prompt}, cinematic, high quality, animated, dynamic"
    
    encoded_prompt = urllib.parse.quote(enhanced_prompt)
    
    # Pollinations doesn't have true video yet, use image with animation prompt
    video_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true&model=flux"
    
    return jsonify({
        'success': True,
        'video_url': video_url,
        'prompt': clean_prompt,
        'provider': 'Pollinations'
    })

@lilith_page_bp.route('/api/video/lilith', methods=['POST'])
def generate_lilith_video():
    import urllib.parse
    
    data = request.json or {}
    expression = data.get('expression', 'speaking')
    
    expressions = {
        'speaking': "beautiful dark demoness with red eyes, mouth open speaking, animated portrait, dark fantasy, cinematic",
        'smiling': "seductive dark demoness with glowing red eyes, seductive smile, dark fantasy portrait",
        'winking': "playful dark succubus with red eyes winking, flirty expression, fantasy art",
        'laughing': "dark demoness laughing seductively, red glowing eyes, playful, fantasy art"
    }
    
    prompt = expressions.get(expression, expressions['speaking'])
    encoded_prompt = urllib.parse.quote(prompt)
    
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true&model=flux"
    
    return jsonify({
        'success': True,
        'image_url': image_url,
        'expression': expression,
        'provider': 'Pollinations'
    })

@lilith_page_bp.route('/api/stats')
def get_stats():
    if MEGA_ENGINE:
        try:
            engine = get_mega_engine()
            stats = engine.get_stats()
            return jsonify({
                'success': True,
                'available': stats.get('available_providers', 0),
                'total': stats.get('total_providers', 0),
                'successful': stats.get('successful', 0),
                'failed': stats.get('failed', 0),
                'session_id': stats.get('session_id', 'N/A')
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'available': 0, 'total': 0})

@lilith_page_bp.route('/api/status')
def get_status():
    return jsonify({
        'mega_engine': MEGA_ENGINE,
        'avatar_engine': AVATAR_ENGINE,
        'media_engine': MEDIA_ENGINE,
        'timestamp': datetime.now().isoformat()
    })

@lilith_page_bp.route('/api/clear', methods=['POST'])
def clear_history():
    if MEGA_ENGINE:
        try:
            engine = get_mega_engine()
            engine.clear_history()
        except:
            pass
    return jsonify({'success': True})


def create_lilith_app():
    app = Flask(__name__)
    app.register_blueprint(lilith_page_bp, url_prefix='/lilith')
    return app


if __name__ == '__main__':
    app = create_lilith_app()
    app.run(host='0.0.0.0', port=6666, debug=True)
