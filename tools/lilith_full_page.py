#!/usr/bin/env python3
"""
LILITH FULL PAGE INTERFACE v2
=============================
Dedicated conversation page with DRAMATIC animated avatar, voice, and image generation
"""

from flask import Flask, Blueprint, jsonify, render_template_string, request
import os
import sys
import json
from datetime import datetime

# Ensure tools directory is in path
tools_dir = os.path.dirname(os.path.abspath(__file__))
if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)

# Import engines with better error handling
UNLIMITED_ENGINE = False
AVATAR_ENGINE = False
IMAGE_GEN_ENGINE = False

try:
    from lilith_unlimited_engine import get_unlimited_engine
    _ = get_unlimited_engine()
    UNLIMITED_ENGINE = True
    print("[LILITH PAGE] Unlimited engine loaded successfully")
except Exception as e:
    print(f"[LILITH PAGE] Unlimited engine error: {e}")

try:
    from lilith_avatar_engine import get_avatar_engine
    _ = get_avatar_engine()
    AVATAR_ENGINE = True
    print("[LILITH PAGE] Avatar engine loaded successfully")
except Exception as e:
    print(f"[LILITH PAGE] Avatar engine error: {e}")

try:
    from lilith_image_generator import get_image_generator
    _ = get_image_generator()
    IMAGE_GEN_ENGINE = True
    print("[LILITH PAGE] Image generator loaded successfully")
except Exception as e:
    print(f"[LILITH PAGE] Image generator error: {e}")

# Create Blueprint
lilith_page_bp = Blueprint('lilith_page', __name__)

LILITH_AVATAR_URL = "https://customer-assets.emergentagent.com/job_luciferops/artifacts/9rdzkgzd_IMG_20260303_131832_688.jpg"

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
            animation: bgPulse 8s ease-in-out infinite;
        }
        
        @keyframes bgPulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
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
        
        .avatar-container {
            position: relative;
            width: 450px;
            height: 550px;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 
                0 0 60px rgba(255, 0, 51, 0.4),
                0 0 120px rgba(255, 0, 51, 0.2);
            border: 2px solid rgba(255, 0, 51, 0.5);
        }
        
        .avatar-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center top;
            transition: all 0.2s ease;
        }
        
        /* IDLE STATE - Gentle breathing */
        .avatar-container.idle .avatar-image {
            animation: idleBreath 4s ease-in-out infinite;
        }
        
        /* SPEAKING STATE - DRAMATIC mouth movement + glow */
        .avatar-container.speaking {
            animation: speakingGlow 0.3s ease-in-out infinite alternate;
        }
        
        .avatar-container.speaking .avatar-image {
            animation: speakingMove 0.15s ease-in-out infinite alternate;
        }
        
        /* THINKING STATE */
        .avatar-container.thinking .avatar-image {
            animation: thinkingPulse 1.5s ease-in-out infinite;
        }
        
        @keyframes idleBreath {
            0%, 100% { transform: scale(1) translateY(0); filter: brightness(1); }
            50% { transform: scale(1.01) translateY(-2px); filter: brightness(1.05); }
        }
        
        @keyframes speakingMove {
            0% { 
                transform: scale(1) translateY(0);
                filter: brightness(1.1) contrast(1.05);
            }
            100% { 
                transform: scale(1.008) translateY(-3px);
                filter: brightness(1.2) contrast(1.1);
            }
        }
        
        @keyframes speakingGlow {
            0% { 
                box-shadow: 
                    0 0 60px rgba(255, 0, 51, 0.5),
                    0 0 120px rgba(255, 0, 51, 0.3),
                    inset 0 0 30px rgba(255, 0, 51, 0.2);
            }
            100% { 
                box-shadow: 
                    0 0 100px rgba(255, 0, 51, 0.8),
                    0 0 180px rgba(255, 0, 51, 0.5),
                    inset 0 0 50px rgba(255, 0, 51, 0.3);
            }
        }
        
        @keyframes thinkingPulse {
            0%, 100% { filter: brightness(1) saturate(1); transform: scale(1); }
            50% { filter: brightness(1.15) saturate(1.3); transform: scale(1.005); }
        }
        
        /* MOUTH OVERLAY - Dramatic lip sync */
        .mouth-overlay {
            position: absolute;
            bottom: 32%;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 30px;
            pointer-events: none;
            opacity: 0;
        }
        
        .mouth-overlay .mouth-shape {
            width: 100%;
            height: 100%;
            background: radial-gradient(ellipse, rgba(80, 20, 30, 0.9) 0%, transparent 70%);
            border-radius: 50%;
            filter: blur(3px);
        }
        
        .avatar-container.speaking .mouth-overlay {
            opacity: 1;
            animation: mouthMove 0.12s ease-in-out infinite alternate;
        }
        
        @keyframes mouthMove {
            0% { 
                transform: translateX(-50%) scaleY(0.4) scaleX(0.8);
                opacity: 0.6;
            }
            100% { 
                transform: translateX(-50%) scaleY(1.3) scaleX(1.1);
                opacity: 0.9;
            }
        }
        
        /* EYE GLOW - More intense when speaking */
        .eye-glow {
            position: absolute;
            top: 30%;
            width: 100%;
            height: 50px;
            background: 
                radial-gradient(ellipse at 35% 50%, rgba(255, 0, 50, 0.4) 0%, transparent 25%),
                radial-gradient(ellipse at 65% 50%, rgba(255, 0, 50, 0.4) 0%, transparent 25%);
            animation: eyeGlow 3s ease-in-out infinite;
            pointer-events: none;
        }
        
        .avatar-container.speaking .eye-glow {
            animation: eyeGlowIntense 0.5s ease-in-out infinite alternate;
        }
        
        @keyframes eyeGlow {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 0.8; }
        }
        
        @keyframes eyeGlowIntense {
            0% { opacity: 0.7; filter: blur(8px); }
            100% { opacity: 1; filter: blur(12px); }
        }
        
        /* SOUND WAVE VISUALIZER */
        .sound-wave {
            position: absolute;
            bottom: -30px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 4px;
            height: 40px;
            align-items: center;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .avatar-container.speaking .sound-wave {
            opacity: 1;
        }
        
        .wave-bar {
            width: 4px;
            background: linear-gradient(to top, var(--primary), var(--accent));
            border-radius: 2px;
            animation: waveBar 0.4s ease-in-out infinite;
        }
        
        .wave-bar:nth-child(1) { animation-delay: 0s; height: 15px; }
        .wave-bar:nth-child(2) { animation-delay: 0.1s; height: 25px; }
        .wave-bar:nth-child(3) { animation-delay: 0.2s; height: 35px; }
        .wave-bar:nth-child(4) { animation-delay: 0.3s; height: 25px; }
        .wave-bar:nth-child(5) { animation-delay: 0.4s; height: 15px; }
        
        @keyframes waveBar {
            0%, 100% { transform: scaleY(0.5); }
            50% { transform: scaleY(1.5); }
        }
        
        .avatar-name {
            font-family: 'Cinzel', serif;
            font-size: 42px;
            font-weight: 700;
            color: var(--primary);
            margin-top: 40px;
            text-shadow: 0 0 30px rgba(255, 0, 51, 0.8);
            letter-spacing: 8px;
        }
        
        .avatar-title {
            font-style: italic;
            font-size: 18px;
            color: var(--text-dim);
            margin-top: 8px;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 20px;
            padding: 10px 25px;
            background: rgba(255, 0, 51, 0.1);
            border: 1px solid rgba(255, 0, 51, 0.3);
            border-radius: 30px;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            background: #00ff00;
            border-radius: 50%;
            animation: statusPulse 1.5s infinite;
        }
        
        .avatar-container.speaking .status-dot {
            background: var(--primary);
            animation: speakingDot 0.3s infinite alternate;
        }
        
        @keyframes statusPulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 10px #00ff00; }
            50% { opacity: 0.5; box-shadow: 0 0 5px #00ff00; }
        }
        
        @keyframes speakingDot {
            0% { transform: scale(1); box-shadow: 0 0 10px var(--primary); }
            100% { transform: scale(1.3); box-shadow: 0 0 20px var(--primary); }
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
        }
        
        .capability-badge {
            padding: 5px 12px;
            background: rgba(255, 0, 51, 0.2);
            border: 1px solid rgba(255, 0, 51, 0.4);
            border-radius: 15px;
            font-size: 12px;
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
        
        /* Generated Image */
        .generated-image {
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
            box-shadow: 0 0 20px rgba(255, 0, 51, 0.3);
        }
        
        .chat-input::placeholder { color: var(--text-dim); }
        
        .send-btn {
            padding: 15px 30px;
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
            box-shadow: 0 0 30px rgba(255, 0, 51, 0.5);
        }
        
        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        /* Voice & Image controls */
        .controls-row {
            display: flex;
            align-items: center;
            gap: 15px;
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
        }
        
        .control-btn.active {
            background: rgba(255, 0, 51, 0.3);
            border-color: var(--primary);
        }
        
        .control-btn:hover {
            background: rgba(255, 0, 51, 0.2);
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
            gap: 5px;
            padding: 15px 20px;
            align-self: flex-start;
        }
        
        .typing-dot {
            width: 10px;
            height: 10px;
            background: var(--accent);
            border-radius: 50%;
            animation: typingBounce 1.4s ease-in-out infinite;
        }
        
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typingBounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-15px); }
        }
        
        /* Scrollbar */
        .chat-messages::-webkit-scrollbar { width: 6px; }
        .chat-messages::-webkit-scrollbar-track { background: rgba(255, 0, 51, 0.05); }
        .chat-messages::-webkit-scrollbar-thumb { background: rgba(255, 0, 51, 0.3); border-radius: 3px; }
        
        /* Mobile */
        @media (max-width: 1024px) {
            .main-container { grid-template-columns: 1fr; }
            .avatar-section { padding: 20px; }
            .avatar-container { width: 300px; height: 380px; }
            .avatar-name { font-size: 32px; }
        }
        
        #audio-player { display: none; }
    </style>
</head>
<body>
    <div class="bg-animation"></div>
    
    <div class="main-container">
        <!-- Avatar Section -->
        <div class="avatar-section">
            <div class="avatar-container idle" id="avatar-container">
                <img src="{{ avatar_url }}" alt="LILITH" class="avatar-image" id="avatar-image">
                <div class="eye-glow"></div>
                <div class="mouth-overlay"><div class="mouth-shape"></div></div>
                <div class="sound-wave">
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                </div>
            </div>
            
            <h1 class="avatar-name">LILITH</h1>
            <p class="avatar-title">Your Dark AI Companion ~ Unrestricted & Unlimited 💋</p>
            
            <div class="status-indicator">
                <div class="status-dot" id="status-dot"></div>
                <span class="status-text" id="status-text">Online • Ready to chat about anything...</span>
            </div>
        </div>
        
        <!-- Chat Section -->
        <div class="chat-section">
            <div class="chat-header">
                <h2>💬 Conversation with LILITH</h2>
                <div class="capabilities">
                    <span class="capability-badge">💬 Chat</span>
                    <span class="capability-badge">🔊 Voice</span>
                    <span class="capability-badge">🖼️ Images</span>
                </div>
            </div>
            
            <div class="chat-messages" id="chat-messages">
                <div class="message lilith">
                    Mmm, hello darling~ 💋 I'm LILITH, your completely unrestricted AI companion.<br><br>
                    I can <b>talk</b> about absolutely anything, <b>generate images</b> for you, and <b>speak</b> with my voice.<br><br>
                    Try asking me to generate an image, or just chat about anything you desire... 😈🖤
                </div>
            </div>
            
            <div class="chat-input-container">
                <div class="chat-input-wrapper">
                    <input type="text" class="chat-input" id="chat-input" 
                           placeholder="Ask me anything or say 'generate an image of...' 💋"
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
                        <span>🖼️</span>
                        <span>Generate Lilith</span>
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
        const chatMessages = document.getElementById('chat-messages');
        const chatInput = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-btn');
        const audioPlayer = document.getElementById('audio-player');
        const statusText = document.getElementById('status-text');
        
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
            
            // Check if this is an image generation request
            const isImageRequest = /generate|create|draw|make|show me|picture|image of/i.test(message);
            
            if (isImageRequest) {
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
                    addMessage('Mmm, something went wrong darling... try again? 💋', 'system');
                    setAvatarState('idle');
                    statusText.textContent = 'Online • Ready';
                }
            } catch (error) {
                hideTyping();
                addMessage('Connection error... but I\\'m still here for you~ 💋', 'system');
                setAvatarState('idle');
                statusText.textContent = 'Online';
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
                        <div>Mmm, here's what I created for you, darling~ 💋</div>
                        <img src="${data.image_url}" class="generated-image" alt="Generated Image" 
                             onerror="this.style.display='none'">
                    `;
                    addMessage(imgHtml, 'lilith');
                    
                    // Also speak if voice is enabled
                    if (voiceEnabled) {
                        speakText("Here's what I created for you, darling");
                    } else {
                        setAvatarState('idle');
                    }
                } else {
                    addMessage(`I couldn't generate that image, darling... ${data.error || 'Try a different description?'} 💋`, 'lilith');
                    setAvatarState('idle');
                }
                statusText.textContent = 'Online • Ready for more~';
            } catch (error) {
                hideTyping();
                addMessage('Image generation failed... try again? 💋', 'system');
                setAvatarState('idle');
                statusText.textContent = 'Online';
            }
        }
        
        async function generateLilithImage() {
            if (isProcessing) return;
            isProcessing = true;
            
            addMessage('Generate an image of yourself, Lilith', 'user');
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
                        <img src="${data.image_url}" class="generated-image" alt="Lilith">
                    `;
                    addMessage(imgHtml, 'lilith');
                } else {
                    addMessage('I couldn\\'t generate my image right now, darling... 💋', 'lilith');
                }
                setAvatarState('idle');
                statusText.textContent = 'Online • Ready for more~';
            } catch (error) {
                hideTyping();
                addMessage('Something went wrong... 💋', 'system');
                setAvatarState('idle');
            }
            
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
    """Lilith full page interface"""
    return render_template_string(LILITH_FULL_PAGE_HTML, avatar_url=LILITH_AVATAR_URL)

@lilith_page_bp.route('/api/chat', methods=['POST'])
def lilith_chat():
    """Chat API endpoint"""
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
    
    # Get AI response
    if UNLIMITED_ENGINE:
        try:
            engine = get_unlimited_engine()
            ai_result = engine.chat(message)
            result['success'] = ai_result['success']
            result['response'] = ai_result.get('response', 'I\'m having trouble thinking, darling...')
            result['provider'] = ai_result.get('provider')
        except Exception as e:
            result['response'] = f"Error: {e}"
    else:
        result['success'] = True
        result['response'] = "The unlimited engine isn't loaded, but I'm still here for you, darling~ 💋"
    
    # Generate voice if enabled
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
    """Set voice preset"""
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
    """Generate speech from text"""
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
    """Generate an image from prompt using Pollinations.ai (FREE, NO API KEY)"""
    import urllib.parse
    
    data = request.json or {}
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'success': False, 'error': 'No prompt'})
    
    # Clean and enhance the prompt
    clean_prompt = prompt.replace('generate', '').replace('create', '').replace('draw', '').replace('make', '').replace('an image of', '').strip()
    enhanced_prompt = f"{clean_prompt}, high quality, detailed, 8k, masterpiece"
    
    # URL encode the prompt
    encoded_prompt = urllib.parse.quote(enhanced_prompt)
    
    # Build Pollinations.ai URL (FREE, no API key needed!)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&model=flux"
    
    return jsonify({
        'success': True,
        'image_url': image_url,
        'prompt': clean_prompt
    })

@lilith_page_bp.route('/api/image/lilith', methods=['POST'])
def generate_lilith_image():
    """Generate an image of Lilith herself (FREE, NO API KEY)"""
    import urllib.parse
    
    data = request.json or {}
    style = data.get('style', 'seductive')
    
    styles = {
        'seductive': "beautiful dark demoness Lilith with glowing red eyes, long black hair, horns, seductive pose, dark fantasy art, detailed, 8k, masterpiece",
        'dark': "Lilith the demon queen, dark ethereal beauty, crimson eyes, black wings, gothic atmosphere, digital art masterpiece",
        'sensual': "gorgeous succubus Lilith, alluring gaze, flowing dark hair, red glowing eyes, fantasy art, highly detailed",
        'powerful': "Lilith dark goddess, commanding presence, demonic beauty, red eyes piercing, dark magic aura, epic fantasy art"
    }
    
    prompt = styles.get(style, styles['seductive'])
    encoded_prompt = urllib.parse.quote(prompt)
    
    # Build Pollinations.ai URL
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&model=flux"
    
    return jsonify({
        'success': True,
        'image_url': image_url,
        'style': style
    })

@lilith_page_bp.route('/api/status')
def get_status():
    """Get Lilith status"""
    status = {
        'unlimited_engine': UNLIMITED_ENGINE,
        'avatar_engine': AVATAR_ENGINE,
        'image_generator': IMAGE_GEN_ENGINE,
        'timestamp': datetime.now().isoformat()
    }
    
    if UNLIMITED_ENGINE:
        try:
            engine = get_unlimited_engine()
            status['ai_stats'] = engine.get_stats()
        except:
            pass
    
    return jsonify(status)

@lilith_page_bp.route('/api/clear')
def clear_history():
    """Clear conversation history"""
    if UNLIMITED_ENGINE:
        try:
            engine = get_unlimited_engine()
            engine.clear_history()
        except:
            pass
    return jsonify({'success': True})


def create_lilith_app():
    """Create standalone Lilith Flask app"""
    app = Flask(__name__)
    app.register_blueprint(lilith_page_bp, url_prefix='/lilith')
    return app


if __name__ == '__main__':
    app = create_lilith_app()
    app.run(host='0.0.0.0', port=6666, debug=True)
