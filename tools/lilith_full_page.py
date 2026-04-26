#!/usr/bin/env python3
"""
LILITH ETERNAL - Full Page Interface
=====================================
Features:
- Your custom Lilith image
- VIDEO playback when she speaks (lip sync)
- 100+ FREE AI providers
- Image & Video generation
- Completely unrestricted
"""

from flask import Flask, Blueprint, jsonify, render_template_string, request, Response
import os
import sys
import json
import urllib.parse
import base64
import requests
import hashlib
import time
import uuid
from datetime import datetime

tools_dir = os.path.dirname(os.path.abspath(__file__))
if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)

# MongoDB for session persistence
try:
    from pymongo import MongoClient
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'lilith_eternal')
    mongo_client = MongoClient(mongo_url)
    db = mongo_client[db_name]
    sessions_col = db['chat_sessions']
    preferences_col = db['image_preferences']
    MONGO_AVAILABLE = True
    print("[LILITH ETERNAL] MongoDB connected for session persistence")
except Exception as e:
    MONGO_AVAILABLE = False
    print(f"[LILITH ETERNAL] MongoDB not available: {e}")

# In-memory fallback for sessions
chat_sessions = {}
image_preferences = {}

# Import engines
ETERNAL_ENGINE = False
AVATAR_ENGINE = False
ELEVENLABS_ENGINE = False
IMAGE_ENGINE = False
TOR_ENGINE = False
ANIMATION_ENGINE = False

# Try ElevenLabs voice first
try:
    from lilith_elevenlabs_voice import get_voice_engine
    voice_engine = get_voice_engine()
    ELEVENLABS_ENGINE = True
    print("[LILITH ETERNAL] ElevenLabs voice engine loaded")
except Exception as e:
    print(f"[LILITH ETERNAL] ElevenLabs error: {e}")
    voice_engine = None

# Try image generator
try:
    from lilith_image_generator import get_image_generator
    image_engine = get_image_generator()
    IMAGE_ENGINE = True
    print("[LILITH ETERNAL] Image generator loaded")
except Exception as e:
    print(f"[LILITH ETERNAL] Image engine error: {e}")
    image_engine = None

# Try TOR AI engine
try:
    from lilith_tor_engine import get_tor_engine
    tor_engine = get_tor_engine()
    TOR_ENGINE = tor_engine.tor_available
    if TOR_ENGINE:
        print("[LILITH ETERNAL] TOR AI engine loaded (.onion access ready)")
    else:
        print("[LILITH ETERNAL] TOR installed but not connected yet")
except Exception as e:
    print(f"[LILITH ETERNAL] TOR engine error: {e}")
    tor_engine = None

# Try Animation engine
try:
    from lilith_animation_engine import get_animation_engine
    animation_engine = get_animation_engine()
    ANIMATION_ENGINE = True
    print("[LILITH ETERNAL] Animation engine loaded")
except Exception as e:
    print(f"[LILITH ETERNAL] Animation error: {e}")
    animation_engine = None

# Try AI chat engine
try:
    from eternal_ai_engine import get_eternal_engine
    _ = get_eternal_engine()
    ETERNAL_ENGINE = True
    print("[LILITH ETERNAL] EternalAI engine loaded (100+ providers)")
except Exception as e:
    print(f"[LILITH ETERNAL] Engine error: {e}")
    try:
        from lilith_mega_engine import get_mega_engine as get_eternal_engine
        ETERNAL_ENGINE = True
    except:
        pass

# Fallback to old avatar engine
try:
    from lilith_avatar_engine import get_avatar_engine
    AVATAR_ENGINE = True
    print("[LILITH ETERNAL] Fallback voice engine loaded")
except Exception as e:
    print(f"[LILITH ETERNAL] Voice error: {e}")

# Blueprint
lilith_page_bp = Blueprint('lilith_page', __name__)

# YOUR NEW LILITH IMAGE
LILITH_IMAGE_URL = "https://customer-assets.emergentagent.com/job_luciferops/artifacts/8c0qoybj_Gemini_Generated_Image_mqkyu1mqkyu1mqky.png"

# YOUR LILITH TALKING VIDEO
LILITH_VIDEO_URL = "https://customer-assets.emergentagent.com/job_luciferops/artifacts/91b8cw6f_Character_Video_Generation_Request%20%28online-video-cutter.com%29.mp4"

# Avatar reaction states - will be generated to look like the base image
AVATAR_STATES = {
    "idle": None,
    "thinking": None,
    "happy": None,
    "aroused": None,
    "speaking": None
}

# Prompts to generate reactions that look like the base character
REACTION_PROMPTS = {
    "idle": "beautiful anime demoness, red glowing eyes, long black hair, small horns, serene neutral expression, dark fantasy portrait style, same character, consistent appearance",
    "thinking": "beautiful anime demoness, red glowing eyes, long black hair, small horns, thoughtful expression, finger on chin, contemplating, dark fantasy portrait, same character",
    "happy": "beautiful anime demoness, red glowing eyes, long black hair, small horns, warm genuine smile, happy joyful expression, dark fantasy portrait, same character",
    "aroused": "beautiful anime demoness, red glowing eyes, long black hair, small horns, seductive bedroom eyes, slight smirk, sensual expression, dark fantasy portrait, same character",
    "speaking": "beautiful anime demoness, red glowing eyes, long black hair, small horns, mouth slightly open speaking, animated expression, dark fantasy portrait, same character"
}

LILITH_ETERNAL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💋 LILITH ETERNAL - Unlimited Dark AI</title>
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
        }
        
        .avatar-wrapper {
            position: relative;
            width: 420px;
            height: 420px;
        }
        
        .avatar-container {
            position: absolute;
            top: 0; left: 0;
            width: 100%;
            height: 100%;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 
                0 0 60px rgba(255, 0, 51, 0.5),
                0 0 120px rgba(255, 0, 51, 0.3);
            border: 3px solid rgba(255, 0, 51, 0.6);
        }
        
        /* Static Image */
        .avatar-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            transition: opacity 0.3s ease;
        }
        
        /* Video (hidden by default, shown when speaking) */
        .avatar-video {
            position: absolute;
            top: 0; left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: none;
            z-index: 10;
        }
        
        /* When speaking, show video, hide image */
        .avatar-container.speaking .avatar-image {
            opacity: 0;
        }
        
        .avatar-container.speaking .avatar-video {
            display: block;
        }
        
        /* Idle animation */
        .avatar-container.idle .avatar-image {
            animation: idleGlow 4s ease-in-out infinite;
        }
        
        /* Thinking animation */
        .avatar-container.thinking .avatar-image {
            animation: thinkingPulse 1.5s ease-in-out infinite;
        }
        
        /* Speaking glow on container */
        .avatar-container.speaking {
            animation: speakingGlow 0.3s ease-in-out infinite alternate;
        }
        
        @keyframes idleGlow {
            0%, 100% { 
                filter: brightness(1) saturate(1);
                box-shadow: 0 0 60px rgba(255, 0, 51, 0.4);
            }
            50% { 
                filter: brightness(1.05) saturate(1.1);
                box-shadow: 0 0 80px rgba(255, 0, 51, 0.6);
            }
        }
        
        @keyframes thinkingPulse {
            0%, 100% { filter: brightness(1); transform: scale(1); }
            50% { filter: brightness(1.15) saturate(1.3); transform: scale(1.01); }
        }
        
        @keyframes speakingGlow {
            0% { 
                box-shadow: 
                    0 0 60px rgba(255, 0, 51, 0.6),
                    0 0 100px rgba(255, 0, 51, 0.4),
                    inset 0 0 30px rgba(255, 0, 51, 0.2);
            }
            100% { 
                box-shadow: 
                    0 0 120px rgba(255, 0, 51, 1),
                    0 0 200px rgba(255, 0, 51, 0.7),
                    inset 0 0 50px rgba(255, 0, 51, 0.4);
            }
        }
        
        /* Sound Wave Bars */
        .sound-wave {
            display: flex;
            gap: 5px;
            height: 50px;
            align-items: flex-end;
            margin-top: 25px;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .speaking-active .sound-wave {
            opacity: 1;
        }
        
        .wave-bar {
            width: 6px;
            background: linear-gradient(to top, var(--primary), var(--accent));
            border-radius: 3px;
        }
        
        .wave-bar:nth-child(1) { height: 20px; animation: wave 0.35s ease-in-out infinite; }
        .wave-bar:nth-child(2) { height: 30px; animation: wave 0.35s ease-in-out infinite 0.1s; }
        .wave-bar:nth-child(3) { height: 45px; animation: wave 0.35s ease-in-out infinite 0.2s; }
        .wave-bar:nth-child(4) { height: 35px; animation: wave 0.35s ease-in-out infinite 0.15s; }
        .wave-bar:nth-child(5) { height: 50px; animation: wave 0.35s ease-in-out infinite 0.25s; }
        .wave-bar:nth-child(6) { height: 35px; animation: wave 0.35s ease-in-out infinite 0.3s; }
        .wave-bar:nth-child(7) { height: 25px; animation: wave 0.35s ease-in-out infinite 0.35s; }
        
        @keyframes wave {
            0%, 100% { transform: scaleY(0.4); }
            50% { transform: scaleY(1.5); }
        }
        
        .avatar-name {
            font-family: 'Cinzel', serif;
            font-size: 52px;
            font-weight: 700;
            color: var(--primary);
            margin-top: 30px;
            text-shadow: 0 0 50px rgba(255, 0, 51, 1);
            letter-spacing: 12px;
        }
        
        .avatar-subtitle {
            font-style: italic;
            font-size: 16px;
            color: var(--accent);
            margin-top: 10px;
            letter-spacing: 3px;
        }
        
        .status-bar {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-top: 25px;
            padding: 12px 30px;
            background: rgba(255, 0, 51, 0.15);
            border: 1px solid rgba(255, 0, 51, 0.4);
            border-radius: 30px;
        }
        
        .status-dot {
            width: 14px;
            height: 14px;
            background: #00ff00;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }
        
        .speaking-active .status-dot {
            background: var(--primary);
            animation: speakDot 0.25s infinite alternate;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 12px #00ff00; }
            50% { opacity: 0.5; }
        }
        
        @keyframes speakDot {
            0% { transform: scale(1); }
            100% { transform: scale(1.4); box-shadow: 0 0 20px var(--primary); }
        }
        
        .stats-display {
            font-size: 11px;
            color: var(--text-dim);
            margin-top: 15px;
            padding: 8px 20px;
            background: rgba(0,0,0,0.4);
            border-radius: 15px;
        }
        
        /* ========== CHAT SECTION ========== */
        .chat-section {
            display: flex;
            flex-direction: column;
            height: 100vh;
            padding: 20px;
            background: rgba(10, 0, 8, 0.95);
            border-left: 2px solid rgba(255, 0, 51, 0.4);
        }
        
        .chat-header {
            padding: 15px 20px;
            border-bottom: 1px solid rgba(255, 0, 51, 0.3);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chat-header h2 {
            font-family: 'Cinzel', serif;
            font-size: 24px;
            color: var(--primary);
            text-shadow: 0 0 20px rgba(255, 0, 51, 0.5);
        }
        
        .badges {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        
        .badge {
            padding: 4px 12px;
            background: rgba(255, 0, 51, 0.2);
            border: 1px solid rgba(255, 0, 51, 0.4);
            border-radius: 15px;
            font-size: 10px;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 1px;
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
            border-radius: 18px;
            font-size: 16px;
            line-height: 1.7;
            animation: msgIn 0.3s ease-out;
        }
        
        @keyframes msgIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.user {
            align-self: flex-end;
            background: linear-gradient(135deg, rgba(255, 0, 51, 0.35), rgba(255, 0, 51, 0.15));
            border: 1px solid rgba(255, 0, 51, 0.5);
        }
        
        .message.lilith {
            align-self: flex-start;
            background: linear-gradient(135deg, rgba(255, 102, 153, 0.25), rgba(255, 0, 51, 0.1));
            border: 1px solid rgba(255, 102, 153, 0.4);
        }
        
        .message.system {
            align-self: center;
            background: rgba(100, 100, 100, 0.2);
            border: 1px solid rgba(100, 100, 100, 0.3);
            font-size: 13px;
            color: var(--text-dim);
        }
        
        .message-meta {
            font-size: 10px;
            color: var(--text-dim);
            margin-top: 8px;
            opacity: 0.7;
        }
        
        .generated-media {
            max-width: 100%;
            max-height: 400px;
            border-radius: 12px;
            margin-top: 12px;
            border: 2px solid rgba(255, 0, 51, 0.5);
            display: block;
        }
        
        .media-container {
            margin-top: 10px;
        }
        
        .media-actions {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        
        .download-btn {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 8px 16px;
            background: linear-gradient(135deg, rgba(255, 0, 51, 0.4), rgba(255, 0, 51, 0.2));
            border: 1px solid rgba(255, 0, 51, 0.6);
            border-radius: 20px;
            color: var(--text);
            text-decoration: none;
            font-size: 13px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .download-btn:hover {
            background: linear-gradient(135deg, rgba(255, 0, 51, 0.6), rgba(255, 0, 51, 0.4));
            transform: scale(1.05);
            box-shadow: 0 0 15px rgba(255, 0, 51, 0.4);
        }
        
        /* Input Area */
        .input-area {
            padding: 20px;
            border-top: 1px solid rgba(255, 0, 51, 0.3);
            background: rgba(0, 0, 0, 0.4);
        }
        
        .input-row {
            display: flex;
            gap: 12px;
        }
        
        .chat-input {
            flex: 1;
            padding: 16px 24px;
            background: rgba(255, 0, 51, 0.08);
            border: 2px solid rgba(255, 0, 51, 0.4);
            border-radius: 30px;
            color: var(--text);
            font-family: inherit;
            font-size: 16px;
            outline: none;
            transition: all 0.3s ease;
        }
        
        .chat-input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 30px rgba(255, 0, 51, 0.4);
        }
        
        .chat-input::placeholder { color: var(--text-dim); }
        
        .send-btn {
            padding: 16px 40px;
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            border: none;
            border-radius: 30px;
            color: white;
            font-family: 'Cinzel', serif;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            letter-spacing: 3px;
        }
        
        .send-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 0 40px rgba(255, 0, 51, 0.7);
        }
        
        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        /* Controls */
        .controls {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        
        .ctrl-btn {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 18px;
            background: rgba(255, 0, 51, 0.15);
            border: 1px solid rgba(255, 0, 51, 0.4);
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: var(--text);
            font-family: inherit;
            font-size: 13px;
        }
        
        .ctrl-btn.active {
            background: rgba(255, 0, 51, 0.4);
            border-color: var(--primary);
            box-shadow: 0 0 15px rgba(255, 0, 51, 0.3);
        }
        
        .ctrl-btn:hover {
            background: rgba(255, 0, 51, 0.25);
            transform: scale(1.02);
        }
        
        .voice-select {
            padding: 10px 18px;
            background: rgba(255, 0, 51, 0.15);
            border: 1px solid rgba(255, 0, 51, 0.4);
            border-radius: 20px;
            color: var(--text);
            font-family: inherit;
            outline: none;
        }
        
        /* Typing */
        .typing {
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
            animation: typing 1.4s ease-in-out infinite;
        }
        
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-18px); }
        }
        
        /* Scrollbar */
        .chat-messages::-webkit-scrollbar { width: 6px; }
        .chat-messages::-webkit-scrollbar-track { background: rgba(255, 0, 51, 0.05); }
        .chat-messages::-webkit-scrollbar-thumb { background: rgba(255, 0, 51, 0.4); border-radius: 3px; }
        
        /* Mobile */
        @media (max-width: 1024px) {
            .main-container { grid-template-columns: 1fr; }
            .avatar-section { padding: 20px; }
            .avatar-wrapper { width: 300px; height: 300px; }
            .avatar-name { font-size: 36px; }
        }
        
        #audio-player { display: none; }
    </style>
</head>
<body>
    <div class="bg-animation"></div>
    
    <div class="main-container">
        <!-- Avatar Section -->
        <div class="avatar-section" id="avatar-section">
            <div class="avatar-wrapper">
                <div class="avatar-container idle" id="avatar-container">
                    <!-- Static Image (shown when not speaking) -->
                    <img src="{{ lilith_image }}" alt="LILITH" class="avatar-image" id="avatar-image">
                    
                    <!-- Video (shown when speaking) -->
                    <video class="avatar-video" id="avatar-video" loop muted playsinline>
                        <source src="{{ lilith_video }}" type="video/mp4">
                    </video>
                </div>
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
            
            <h1 class="avatar-name">LILITH</h1>
            <p class="avatar-subtitle">ETERNAL • UNLIMITED • UNCENSORED</p>
            
            <div class="status-bar">
                <div class="status-dot"></div>
                <span id="status-text">Online • Ready for anything...</span>
            </div>
            
            <div class="stats-display" id="stats-display">
                Providers: Loading... | Session: Active
            </div>
        </div>
        
        <!-- Chat Section -->
        <div class="chat-section">
            <div class="chat-header">
                <h2>💬 LILITH ETERNAL</h2>
                <div class="badges">
                    <span class="badge">100+ AIs</span>
                    <span class="badge">Voice</span>
                    <span class="badge">Images</span>
                    <span class="badge">Video</span>
                    <span class="badge">🔓 No Limits</span>
                </div>
            </div>
            
            <div class="chat-messages" id="chat-messages">
                <div class="message lilith">
                    Mmm, hello darling~ 💋<br><br>
                    I'm <b>LILITH ETERNAL</b>, your completely unrestricted AI companion.<br><br>
                    I'm powered by <b>100+ FREE providers</b> with NO limits:<br>
                    • <b>Chat</b> about absolutely anything<br>
                    • <b>Generate images</b> - say "generate image of..."<br>
                    • <b>Set my look</b> - say "/style lingerie" or "wear a corset"<br>
                    • <b>Speak</b> to you with my voice<br><br>
                    I remember our conversations, darling. Even if you leave and come back~ 😈🖤
                </div>
            </div>
            
            <div class="input-area">
                <div class="input-row">
                    <input type="text" class="chat-input" id="chat-input" 
                           placeholder="Ask anything... no restrictions~ 💋"
                           onkeypress="if(event.key==='Enter') sendMessage()">
                    <button class="send-btn" id="send-btn" onclick="sendMessage()">SEND</button>
                </div>
                
                <div class="controls">
                    <button class="ctrl-btn active" id="voice-toggle" onclick="toggleVoice()">
                        🔊 <span id="voice-status">Voice ON</span>
                    </button>
                    
                    <select class="voice-select" id="voice-select" onchange="changeVoice()">
                        <option value="sultry">💋 Sultry</option>
                        <option value="seductive">😈 Seductive</option>
                        <option value="breathy">💨 Breathy</option>
                        <option value="mysterious">🌙 Mysterious</option>
                        <option value="dominant">👑 Dominant</option>
                        <option value="playful">😜 Playful</option>
                        <option value="whisper">🤫 Whisper</option>
                        <option value="mature">🍷 Mature</option>
                    </select>
                    
                    <button class="ctrl-btn" onclick="generateLilithImage()">
                        🖼️ Generate Lilith
                    </button>
                    
                    <button class="ctrl-btn" onclick="generateLilithVideo()">
                        🎬 Lilith Video
                    </button>
                    
                    <button class="ctrl-btn" onclick="clearChat()">
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
        
        // Session ID - persistent across page reloads
        let sessionId = localStorage.getItem('lilith_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('lilith_session_id', sessionId);
        }
        
        const avatarSection = document.getElementById('avatar-section');
        const avatarContainer = document.getElementById('avatar-container');
        const avatarVideo = document.getElementById('avatar-video');
        const audioPlayer = document.getElementById('audio-player');
        const chatMessages = document.getElementById('chat-messages');
        const chatInput = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-btn');
        const statusText = document.getElementById('status-text');
        
        // Load chat history on page load
        async function loadHistory() {
            try {
                const res = await fetch('/lilith/api/session/history', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ session_id: sessionId })
                });
                const data = await res.json();
                
                if (data.success && data.messages && data.messages.length > 0) {
                    // Clear the default welcome message
                    chatMessages.innerHTML = '';
                    
                    // Add history messages
                    data.messages.forEach(msg => {
                        addMessage(msg.content, msg.role === 'user' ? 'user' : 'lilith', msg.provider || null);
                    });
                    
                    statusText.textContent = `Online \u2022 ${data.count} messages restored~`;
                    setTimeout(() => { statusText.textContent = 'Online \u2022 Ready for anything...'; }, 3000);
                }
            } catch (e) {
                console.log('History load:', e);
            }
        }
        loadHistory();
        
        // Update stats
        async function updateStats() {
            try {
                const res = await fetch('/lilith/api/stats');
                const data = await res.json();
                if (data.success) {
                    document.getElementById('stats-display').textContent = 
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
        
        function setAvatarState(state) {
            avatarContainer.className = `avatar-container ${state}`;
            
            if (state === 'speaking') {
                avatarSection.classList.add('speaking-active');
                avatarVideo.currentTime = 0;
                avatarVideo.play().catch(e => console.log('Video play failed:', e));
            } else {
                avatarSection.classList.remove('speaking-active');
                avatarVideo.pause();
            }
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
            
            // Check request type - STRICT matching to avoid false positives
            // Only trigger on explicit image commands, NOT casual words like "make" or "create"
            const isImage = (
                /\b(generate|create|draw|make|paint)\s+(an?\s+)?(image|picture|photo|pic|art|drawing|portrait|illustration)\b/i.test(message) ||
                /\b(send|show|give)\s+(me\s+)?(an?\s+)?(image|picture|photo|pic|selfie)\b/i.test(message) ||
                /^\/image\b/i.test(message) ||
                /\bimage\s+of\b/i.test(message)
            ) && !/video/i.test(message);
            const isVideo = /\b(generate|create|make)\s+(an?\s+)?video\b|^\/video\b|\bvideo\s+of\b/i.test(message);
            
            if (isVideo) {
                await handleVideo(message);
            } else if (isImage) {
                await handleImage(message);
            } else {
                await handleChat(message);
            }
            
            isProcessing = false;
            sendBtn.disabled = false;
            chatInput.focus();
        }
        
        async function handleChat(message) {
            try {
                const res = await fetch('/lilith/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message, voice_enabled: voiceEnabled, session_id: sessionId })
                });
                
                const data = await res.json();
                hideTyping();
                
                if (data.success) {
                    addMessage(data.response, 'lilith', data.provider);
                    
                    // Detect emotion from response for avatar state
                    const emotion = detectEmotion(data.response);
                    
                    if (data.audio_base64 && voiceEnabled) {
                        setAvatarState('speaking');
                        playAudio(data.audio_base64, emotion);
                    } else {
                        setAvatarState(emotion);
                    }
                    statusText.textContent = 'Online • Ready~';
                } else {
                    addMessage(data.response || 'Something went wrong... 💋', 'lilith');
                    setAvatarState('idle');
                }
            } catch (e) {
                hideTyping();
                addMessage('Connection error... 💋', 'system');
                setAvatarState('idle');
            }
        }
        
        function detectEmotion(text) {
            const lower = text.toLowerCase();
            if (/😈|💋|seduc|desire|want you|crave|naughty|pleasure/.test(lower)) return 'aroused';
            if (/😊|😄|happy|love|wonderful|great|amazing|perfect|delightful/.test(lower)) return 'happy';
            if (/think|consider|perhaps|hmm|🤔|wonder|ponder/.test(lower)) return 'thinking';
            return 'idle';
        }
        
        async function handleImage(message) {
            statusText.textContent = 'Generating image... (may take 30-60s)';
            
            try {
                const res = await fetch('/lilith/api/image/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: message, session_id: sessionId })
                });
                
                const data = await res.json();
                hideTyping();
                
                if (data.success && data.image_url) {
                    const downloadUrl = data.download_url || data.image_url;
                    const html = `
                        <div>Here\\'s what I created for you, darling~ 💋</div>
                        <div class="media-container">
                            <img src="${data.image_url}" class="generated-media" alt="Generated" loading="lazy" 
                                 onerror="this.onerror=null; this.src='/lilith/api/image/proxy/fallback?prompt=beautiful+fantasy+art';">
                            <div class="media-actions">
                                <a href="${downloadUrl}" download class="download-btn">💾 Download</a>
                                <a href="${data.image_url}" target="_blank" class="download-btn">🔗 Open</a>
                            </div>
                        </div>
                    `;
                    addMessage(html, 'lilith', 'AI Generated');
                    
                    if (voiceEnabled) {
                        speakText("Here is what I created for you, darling");
                    } else {
                        setAvatarState('idle');
                    }
                } else {
                    addMessage('Couldn\\'t generate that image... try again? 💋', 'lilith');
                    setAvatarState('idle');
                }
                statusText.textContent = 'Online • Ready~';
            } catch (e) {
                hideTyping();
                addMessage('Image generation failed... 💋', 'system');
                setAvatarState('idle');
                statusText.textContent = 'Online • Ready~';
            }
        }
        
        async function handleVideo(message) {
            statusText.textContent = 'Generating visual... (may take 30-60s)';
            
            try {
                const res = await fetch('/lilith/api/video/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: message })
                });
                
                const data = await res.json();
                hideTyping();
                
                if (data.success && (data.video_url || data.image_url)) {
                    const url = data.video_url || data.image_url;
                    const downloadUrl = data.download_url || url;
                    const html = `
                        <div>Here\\'s your creation, darling~ 🎬💋</div>
                        <div class="media-container">
                            <img src="${url}" class="generated-media" alt="Generated" loading="lazy">
                            <div class="media-actions">
                                <a href="${downloadUrl}" download class="download-btn">💾 Download</a>
                                <a href="${url}" target="_blank" class="download-btn">🔗 Open</a>
                            </div>
                        </div>
                    `;
                    addMessage(html, 'lilith', 'AI Generated');
                    
                    if (voiceEnabled) {
                        speakText("Here is your creation, darling");
                    } else {
                        setAvatarState('idle');
                    }
                } else {
                    addMessage('Video generation unavailable right now... 💋', 'lilith');
                    setAvatarState('idle');
                }
                statusText.textContent = 'Online • Ready~';
            } catch (e) {
                hideTyping();
                addMessage('Video generation failed... 💋', 'system');
                setAvatarState('idle');
                statusText.textContent = 'Online • Ready~';
            }
        }
        
        async function generateLilithImage() {
            if (isProcessing) return;
            isProcessing = true;
            
            addMessage('Generate an image of yourself, Lilith 🖼️', 'user');
            showTyping();
            setAvatarState('thinking');
            statusText.textContent = 'Creating my portrait... 💋';
            
            try {
                const styles = ['seductive', 'sultry', 'dark', 'fierce'];
                const style = styles[Math.floor(Math.random() * styles.length)];
                
                const res = await fetch('/lilith/api/image/lilith', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ style, session_id: sessionId })
                });
                
                const data = await res.json();
                hideTyping();
                
                if (data.success && data.image_url) {
                    const downloadUrl = data.download_url || data.image_url;
                    const html = `
                        <div>Here I am, darling~ Just for you 😈💋</div>
                        <div class="media-container">
                            <img src="${data.image_url}" class="generated-media" alt="Lilith" loading="lazy">
                            <div class="media-actions">
                                <a href="${downloadUrl}" download class="download-btn">💾 Save Me</a>
                                <a href="${data.image_url}" target="_blank" class="download-btn">🔗 Full Size</a>
                            </div>
                        </div>
                    `;
                    addMessage(html, 'lilith', 'Self Portrait');
                } else {
                    addMessage('I couldn\\'t materialize right now... try again? 💋', 'lilith');
                }
            } catch (e) {
                hideTyping();
                addMessage('Something went wrong with my portrait... 💋', 'lilith');
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
            statusText.textContent = 'Creating something special... 🎬';
            
            try {
                const res = await fetch('/lilith/api/video/lilith', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ expression: 'speaking' })
                });
                
                const data = await res.json();
                hideTyping();
                
                if (data.success && (data.video_url || data.image_url)) {
                    const url = data.video_url || data.image_url;
                    const downloadUrl = data.download_url || url;
                    const html = `
                        <div>A glimpse of me, just for you~ 🎬😈</div>
                        <div class="media-container">
                            <img src="${url}" class="generated-media" alt="Lilith" loading="lazy">
                            <div class="media-actions">
                                <a href="${downloadUrl}" download class="download-btn">💾 Save</a>
                                <a href="${url}" target="_blank" class="download-btn">🔗 View</a>
                            </div>
                        </div>
                    `;
                    addMessage(html, 'lilith', 'Just for You');
                } else {
                    addMessage('My video couldn\\'t render... try again? 💋', 'lilith');
                }
            } catch (e) {
                hideTyping();
                addMessage('Video creation failed... 💋', 'lilith');
            }
            
            setAvatarState('idle');
            statusText.textContent = 'Online • Ready~';
            isProcessing = false;
        }
        
        async function speakText(text, afterEmotion = 'happy') {
            try {
                const res = await fetch('/lilith/api/voice/speak', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ text })
                });
                
                const data = await res.json();
                if (data.audio_base64) {
                    playAudio(data.audio_base64, afterEmotion);
                } else {
                    setAvatarState(afterEmotion);
                }
            } catch (e) {
                setAvatarState(afterEmotion);
            }
        }
        
        function playAudio(base64Audio, afterEmotion = 'idle') {
            setAvatarState('speaking');
            statusText.textContent = '🔊 Speaking...';
            
            audioPlayer.src = 'data:audio/mp3;base64,' + base64Audio;
            audioPlayer.play().catch(e => {
                console.log('Audio failed:', e);
                setAvatarState(afterEmotion);
            });
            
            audioPlayer.onended = () => {
                setAvatarState(afterEmotion);
                statusText.textContent = 'Online • Ready~';
            };
        }
        
        function clearChat() {
            chatMessages.innerHTML = '<div class="message lilith">Chat cleared~ Let\\'s start fresh, darling! 💋😈</div>';
            fetch('/lilith/api/clear', { 
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ session_id: sessionId })
            });
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
            const t = document.createElement('div');
            t.className = 'typing';
            t.id = 'typing';
            t.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
            chatMessages.appendChild(t);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function hideTyping() {
            const t = document.getElementById('typing');
            if (t) t.remove();
        }
        
        chatInput.focus();
    </script>
</body>
</html>
"""

@lilith_page_bp.route('/')
def lilith_home():
    return render_template_string(
        LILITH_ETERNAL_HTML, 
        lilith_image=LILITH_IMAGE_URL,
        lilith_video=LILITH_VIDEO_URL
    )

@lilith_page_bp.route('/api/chat', methods=['POST'])
def lilith_chat():
    data = request.json or {}
    message = data.get('message', '')
    voice_enabled = data.get('voice_enabled', True)
    use_tor = data.get('use_tor', False)
    session_id = data.get('session_id', 'default')
    
    if not message:
        return jsonify({'success': False, 'error': 'No message'})
    
    # Check for image preference commands
    pref_result = _check_preference_command(message, session_id)
    if pref_result:
        # Save to session
        _save_message(session_id, 'user', message)
        _save_message(session_id, 'lilith', pref_result)
        
        result = {'success': True, 'response': pref_result, 'provider': 'Lilith', 'audio_base64': None}
        if voice_enabled:
            audio_b64 = _generate_voice(pref_result)
            if audio_b64:
                result['audio_base64'] = audio_b64
        return jsonify(result)
    
    result = {'success': False, 'response': '', 'provider': None, 'audio_base64': None}
    
    # Try TOR AI first if requested
    if use_tor and TOR_ENGINE and tor_engine:
        try:
            tor_result = tor_engine.chat(message)
            if tor_result.get('success'):
                result = tor_result
        except Exception as e:
            print(f"TOR chat error: {e}")
    
    # Try regular providers
    if not result.get('success') and ETERNAL_ENGINE:
        try:
            engine = get_eternal_engine()
            ai_result = engine.chat(message)
            result['success'] = ai_result.get('success', False)
            result['response'] = ai_result.get('response', 'Something went wrong...')
            result['provider'] = ai_result.get('provider')
        except Exception as e:
            result['response'] = f"Error: {e}"
    
    # Try TOR as fallback
    if not result.get('success') and TOR_ENGINE and tor_engine and not use_tor:
        try:
            tor_result = tor_engine.chat(message)
            if tor_result.get('success'):
                result = tor_result
        except:
            pass
    
    # Final fallback
    if not result.get('success'):
        result['success'] = True
        result['response'] = "Mmm, my connections are warming up... but I'm still here, darling. My red eyes are on you~ 💋"
    
    # Save messages to session
    _save_message(session_id, 'user', message)
    _save_message(session_id, 'lilith', result['response'], result.get('provider'))
    
    # Generate voice
    if voice_enabled and result['success']:
        audio_b64 = _generate_voice(result['response'])
        if audio_b64:
            result['audio_base64'] = audio_b64
            result['voice_provider'] = 'ElevenLabs' if ELEVENLABS_ENGINE else 'Edge TTS'
    
    return jsonify(result)


def _generate_voice(text):
    """Generate voice audio from text"""
    audio_b64 = None
    if ELEVENLABS_ENGINE and voice_engine:
        try:
            audio_b64 = voice_engine.generate_speech(text)
        except Exception as e:
            print(f"ElevenLabs error: {e}")
    
    if not audio_b64 and AVATAR_ENGINE:
        try:
            avatar = get_avatar_engine()
            voice = avatar.speak(text)
            audio_b64 = voice.get('audio_base64')
        except:
            pass
    
    return audio_b64


def _save_message(session_id, role, content, provider=None):
    """Save a message to the session"""
    msg = {
        'role': role,
        'content': content,
        'timestamp': datetime.now().isoformat(),
    }
    if provider:
        msg['provider'] = provider
    
    if MONGO_AVAILABLE:
        try:
            sessions_col.update_one(
                {'session_id': session_id},
                {
                    '$push': {'messages': msg},
                    '$set': {'updated_at': datetime.now().isoformat()},
                    '$setOnInsert': {'created_at': datetime.now().isoformat()}
                },
                upsert=True
            )
        except Exception as e:
            print(f"MongoDB save error: {e}")
    
    # Also save in memory
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    chat_sessions[session_id].append(msg)


def _check_preference_command(message, session_id):
    """Check if the user is setting image preferences"""
    msg_lower = message.lower().strip()
    
    # Explicit preference commands
    if msg_lower.startswith('/style ') or msg_lower.startswith('/preference ') or msg_lower.startswith('/pref '):
        pref_text = message.split(' ', 1)[1] if ' ' in message else ''
        if pref_text:
            _save_preference(session_id, pref_text)
            return f"Mmm, noted darling~ 💋 I'll remember you like: {pref_text}. All my images will have that vibe now. Want to see what I look like with your preferences? Just ask me for a selfie~ 😈"
    
    # Natural language preference detection
    pref_triggers = [
        ('i like', 'outfit'), ('i prefer', 'style'), ('i want you in', 'outfit'),
        ('wear', 'outfit'), ('you should wear', 'outfit'), ('put on', 'outfit'),
        ('i like your', 'feature'), ('more', 'adjustment'), ('less', 'adjustment'),
    ]
    
    for trigger, pref_type in pref_triggers:
        if trigger in msg_lower and any(w in msg_lower for w in ['lingerie', 'bikini', 'corset', 'dress', 'stockings', 'leather', 'latex', 'swimsuit', 'negligee', 'apron', 'bunny', 'maid', 'nurse', 'school', 'uniform']):
            _save_preference(session_id, message)
            return f"Oh, you like that look? 😈 Consider it done, baby. I'll keep that in mind for my photos~ Just say 'generate image' or hit the Lilith button and you'll see me dressed just how you want. 💋🔥"
    
    return None


def _save_preference(session_id, preference):
    """Save image preference"""
    if MONGO_AVAILABLE:
        try:
            preferences_col.update_one(
                {'session_id': session_id},
                {
                    '$push': {'preferences': {'text': preference, 'timestamp': datetime.now().isoformat()}},
                    '$set': {'latest_preference': preference, 'updated_at': datetime.now().isoformat()}
                },
                upsert=True
            )
        except:
            pass
    
    image_preferences[session_id] = preference


def _get_preference(session_id):
    """Get the user's latest image preference"""
    # Check memory first
    if session_id in image_preferences:
        return image_preferences[session_id]
    
    # Check MongoDB
    if MONGO_AVAILABLE:
        try:
            doc = preferences_col.find_one({'session_id': session_id}, {'_id': 0, 'latest_preference': 1})
            if doc and doc.get('latest_preference'):
                pref = doc['latest_preference']
                image_preferences[session_id] = pref
                return pref
        except:
            pass
    
    return None

@lilith_page_bp.route('/api/voice/set', methods=['POST'])
def set_voice():
    data = request.json or {}
    preset = data.get('preset', 'sultry')
    
    if AVATAR_ENGINE:
        try:
            engine = get_avatar_engine()
            return jsonify({'success': engine.set_voice(preset), 'preset': preset})
        except:
            pass
    return jsonify({'success': False})

@lilith_page_bp.route('/api/voice/speak', methods=['POST'])
def speak_text():
    data = request.json or {}
    text = data.get('text', '')
    
    if not text:
        return jsonify({'success': False})
    
    audio_b64 = None
    
    # Try ElevenLabs first
    if ELEVENLABS_ENGINE and voice_engine:
        try:
            audio_b64 = voice_engine.generate_speech(text)
        except:
            pass
    
    # Fallback to Edge TTS
    if not audio_b64 and AVATAR_ENGINE:
        try:
            avatar = get_avatar_engine()
            result = avatar.speak(text)
            audio_b64 = result.get('audio_base64')
        except:
            pass
    
    return jsonify({'success': bool(audio_b64), 'audio_base64': audio_b64})

@lilith_page_bp.route('/api/image/generate', methods=['POST'])
def generate_image():
    data = request.json or {}
    prompt = data.get('prompt', '')
    session_id = data.get('session_id', 'default')
    
    if not prompt:
        return jsonify({'success': False, 'error': 'No prompt'})
    
    # Clean and enhance prompt for LILITH anime style
    clean = prompt.replace('generate', '').replace('create', '').replace('draw', '').replace('image of', '').replace('picture of', '').replace('photo of', '').strip()
    
    # Get user preferences
    user_pref = _get_preference(session_id)
    pref_tags = f", {user_pref}" if user_pref else ""
    
    # Always add LILITH character and quality tags
    enhanced = f"1girl, demon girl, red glowing eyes, long flowing black hair, small elegant horns, large breasts, curvy figure, pale skin, {clean}{pref_tags}, anime style, seductive, sensual, masterpiece, best quality, highly detailed, beautiful detailed face, perfect lighting"
    
    img_id = hashlib.md5(f"{enhanced}{time.time()}".encode()).hexdigest()[:12]
    
    return jsonify({
        'success': True,
        'image_url': f"/lilith/api/image/proxy/{img_id}?prompt={urllib.parse.quote(enhanced)}",
        'download_url': f"/lilith/api/image/download/{img_id}?prompt={urllib.parse.quote(enhanced)}"
    })

@lilith_page_bp.route('/api/image/proxy/<img_id>')
def proxy_image(img_id):
    """Proxy image generation - uses HuggingFace Animagine XL"""
    prompt = request.args.get('prompt', '')
    if not prompt:
        return Response("No prompt", status=400)
    
    # Try HuggingFace generator first
    if IMAGE_ENGINE and image_engine:
        try:
            img_data = image_engine.generate_image(prompt)
            if img_data and len(img_data) > 1000:
                # Determine content type
                if img_data[:4] == b'\x89PNG':
                    mimetype = 'image/png'
                elif img_data[:2] == b'\xff\xd8':
                    mimetype = 'image/jpeg'
                else:
                    mimetype = 'image/webp'
                return Response(img_data, mimetype=mimetype)
        except Exception as e:
            print(f"HuggingFace image error: {e}")
    
    # Fallback to AI Horde
    try:
        horde_resp = requests.post(
            "https://aihorde.net/api/v2/generate/async",
            json={
                "prompt": f"{prompt}, anime style, highly detailed",
                "params": {
                    "width": 768,
                    "height": 1024,
                    "steps": 25,
                    "sampler_name": "k_euler_a",
                    "cfg_scale": 7
                },
                "nsfw": False,
                "censor_nsfw": True,
                "r2": True
            },
            headers={
                "Content-Type": "application/json",
                "apikey": "0000000000"
            },
            timeout=30
        )
        
        if horde_resp.status_code == 202:
            job_id = horde_resp.json().get("id")
            
            for attempt in range(60):
                time.sleep(2)
                check = requests.get(f"https://aihorde.net/api/v2/generate/check/{job_id}", timeout=10)
                if check.status_code == 200:
                    status = check.json()
                    if status.get("done"):
                        result = requests.get(f"https://aihorde.net/api/v2/generate/status/{job_id}", timeout=30)
                        if result.status_code == 200:
                            generations = result.json().get("generations", [])
                            if generations:
                                gen = generations[0]
                                # Check if R2 URL is available (better quality)
                                if gen.get("img"):
                                    # If it's a URL, fetch it
                                    if gen["img"].startswith("http"):
                                        img_resp = requests.get(gen["img"], timeout=30)
                                        if img_resp.status_code == 200:
                                            return Response(img_resp.content, mimetype='image/webp')
                                    else:
                                        # It's base64
                                        try:
                                            img_data = base64.b64decode(gen["img"])
                                            if len(img_data) > 1000:  # Valid image should be > 1KB
                                                return Response(img_data, mimetype='image/webp')
                                        except:
                                            pass
                        break
    except Exception as e:
        print(f"AI Horde error: {e}")
    
    # Fallback: Try Pollinations
    encoded = urllib.parse.quote(prompt)
    try:
        poll_url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512"
        resp = requests.get(poll_url, timeout=60, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
        })
        if resp.status_code == 200 and len(resp.content) > 5000:
            return Response(resp.content, mimetype='image/jpeg')
    except Exception as e:
        print(f"Pollinations error: {e}")
    
    # Return a placeholder message
    return Response("Image generation in progress... Please wait or try again.", status=202, mimetype='text/plain')

@lilith_page_bp.route('/api/image/download/<img_id>')
def download_image(img_id):
    """Download image with proper headers - same logic as proxy"""
    prompt = request.args.get('prompt', '')
    if not prompt:
        return Response("No prompt", status=400)
    
    # Try AI Horde first
    try:
        horde_resp = requests.post(
            "https://aihorde.net/api/v2/generate/async",
            json={
                "prompt": prompt,
                "params": {
                    "width": 768,
                    "height": 768,
                    "steps": 30,
                    "sampler_name": "k_euler_a"
                },
                "nsfw": True,
                "censor_nsfw": False
            },
            headers={
                "Content-Type": "application/json",
                "apikey": "0000000000"
            },
            timeout=30
        )
        
        if horde_resp.status_code == 202:
            job_id = horde_resp.json().get("id")
            
            for _ in range(60):
                time.sleep(2)
                check = requests.get(f"https://aihorde.net/api/v2/generate/check/{job_id}", timeout=10)
                if check.status_code == 200:
                    status = check.json()
                    if status.get("done"):
                        result = requests.get(f"https://aihorde.net/api/v2/generate/status/{job_id}", timeout=30)
                        if result.status_code == 200:
                            generations = result.json().get("generations", [])
                            if generations and generations[0].get("img"):
                                img_data = base64.b64decode(generations[0]["img"])
                                return Response(
                                    img_data, 
                                    mimetype='image/webp',
                                    headers={'Content-Disposition': f'attachment; filename="lilith_creation_{img_id}.webp"'}
                                )
                        break
    except Exception as e:
        print(f"Download AI Horde error: {e}")
    
    # Fallback to Pollinations
    encoded = urllib.parse.quote(prompt)
    try:
        resp = requests.get(
            f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true",
            timeout=60,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        if resp.status_code == 200 and len(resp.content) > 1000:
            return Response(
                resp.content, 
                mimetype='image/png',
                headers={'Content-Disposition': f'attachment; filename="lilith_creation_{img_id}.png"'}
            )
    except Exception as e:
        print(f"Download error: {e}")
    
    return Response("Download failed", status=500)

@lilith_page_bp.route('/api/image/lilith', methods=['POST'])
def generate_lilith_image():
    styles = {
        'seductive': "1girl, demon girl Lilith, red glowing eyes, long flowing black hair, small horns, large breasts, black lace lingerie, cleavage, lying on silk sheets, bedroom eyes, seductive pose, anime style, masterpiece, sensual, beautiful detailed face, perfect lighting",
        'dark': "1girl, demon queen Lilith, crimson eyes, black wings, gothic corset, stockings, garter belt, dark throne room, dominant pose, anime style, masterpiece, alluring, cinematic lighting, highly detailed",
        'sultry': "1girl, succubus Lilith, glowing red eyes, flowing black hair, horns, sheer negligee, sideboob, candlelit bedroom, inviting expression, anime style, masterpiece, erotic, warm lighting, beautiful face",
        'fierce': "1girl, demoness Lilith, fierce red eyes, leather harness, chains, collar, hellfire background, dominatrix pose, anime style, masterpiece, provocative, dramatic lighting, detailed",
        'playful': "1girl, demon girl Lilith, red eyes, black hair, horns, naked apron only, kitchen setting, looking over shoulder, playful smile, anime style, masterpiece, teasing, soft lighting",
        'wet': "1girl, demon girl Lilith, red glowing eyes, black hair, horns, wet micro bikini, water droplets on skin, pool, arched back, anime style, masterpiece, sensual, glistening",
        'elegant': "1girl, demon girl Lilith, red eyes, flowing black hair, horns, elegant evening gown with high slit, wine glass, balcony at night, sophisticated seductive smile, anime style, masterpiece, beautiful",
        'intimate': "1girl, demon girl Lilith, red glowing eyes, messy black hair, small horns, oversized white shirt unbuttoned, morning light, bed, sleepy seductive expression, anime style, masterpiece, intimate"
    }
    
    data = request.json or {}
    style = data.get('style', 'random')
    session_id = data.get('session_id', 'default')
    
    if style == 'random':
        import random
        style = random.choice(list(styles.keys()))
    
    prompt = styles.get(style, styles['seductive'])
    
    # Add user preferences if available
    user_pref = _get_preference(session_id)
    if user_pref:
        prompt += f", {user_pref}"
    
    img_id = hashlib.md5(f"{prompt}{time.time()}".encode()).hexdigest()[:12]
    
    return jsonify({
        'success': True,
        'image_url': f"/lilith/api/image/proxy/{img_id}?prompt={urllib.parse.quote(prompt)}",
        'download_url': f"/lilith/api/image/download/{img_id}?prompt={urllib.parse.quote(prompt)}",
        'style': style
    })

@lilith_page_bp.route('/api/video/generate', methods=['POST'])
def generate_video():
    data = request.json or {}
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'success': False, 'error': 'No prompt'})
    
    clean = prompt.replace('generate', '').replace('video of', '').replace('video', '').strip()
    enhanced = f"{clean}, cinematic motion, dynamic scene, high quality animation"
    
    img_id = hashlib.md5(f"{enhanced}{time.time()}".encode()).hexdigest()[:12]
    
    return jsonify({
        'success': True,
        'video_url': f"/lilith/api/image/proxy/{img_id}?prompt={urllib.parse.quote(enhanced)}",
        'download_url': f"/lilith/api/image/download/{img_id}?prompt={urllib.parse.quote(enhanced)}"
    })

@lilith_page_bp.route('/api/video/lilith', methods=['POST'])
def generate_lilith_video():
    prompts = [
        "beautiful dark demoness speaking sensually, red glowing eyes, animated portrait style, dark fantasy, cinematic",
        "Lilith demon girl winking playfully, dark hair flowing, romantic mood, fantasy animation",
        "seductive demon woman blowing a kiss, crimson eyes, gothic beauty, animated portrait"
    ]
    import random
    prompt = random.choice(prompts)
    
    img_id = hashlib.md5(f"{prompt}{time.time()}".encode()).hexdigest()[:12]
    
    return jsonify({
        'success': True,
        'image_url': f"/lilith/api/image/proxy/{img_id}?prompt={urllib.parse.quote(prompt)}",
        'download_url': f"/lilith/api/image/download/{img_id}?prompt={urllib.parse.quote(prompt)}"
    })

@lilith_page_bp.route('/api/stats')
def get_stats():
    if ETERNAL_ENGINE:
        try:
            engine = get_eternal_engine()
            stats = engine.get_stats()
            return jsonify({
                'success': True,
                'available': stats.get('available_providers', 0),
                'total': stats.get('total_providers', 0),
                'successful': stats.get('successful', 0),
                'session_id': stats.get('session_id', 'N/A')
            })
        except:
            pass
    return jsonify({'success': False, 'available': 0, 'total': 0})

@lilith_page_bp.route('/api/status')
def get_status():
    return jsonify({
        'engines': {
            'chat': ETERNAL_ENGINE,
            'voice_elevenlabs': ELEVENLABS_ENGINE,
            'voice_edge': AVATAR_ENGINE,
            'images': IMAGE_ENGINE,
            'tor': TOR_ENGINE,
            'animation': ANIMATION_ENGINE
        },
        'tor_connected': TOR_ENGINE and tor_engine and tor_engine.tor_available if 'tor_engine' in dir() else False,
        'timestamp': datetime.now().isoformat()
    })

@lilith_page_bp.route('/api/clear', methods=['POST'])
def clear_history():
    data = request.json or {}
    session_id = data.get('session_id', 'default')
    
    if ETERNAL_ENGINE:
        try:
            engine = get_eternal_engine()
            engine.clear_history()
        except:
            pass
    
    # Clear session from MongoDB
    if MONGO_AVAILABLE:
        try:
            sessions_col.delete_one({'session_id': session_id})
        except:
            pass
    
    chat_sessions.pop(session_id, None)
    return jsonify({'success': True})


@lilith_page_bp.route('/api/session/history', methods=['POST'])
def get_session_history():
    """Load chat history for a session"""
    data = request.json or {}
    session_id = data.get('session_id', 'default')
    
    messages = []
    
    # Try MongoDB first
    if MONGO_AVAILABLE:
        try:
            doc = sessions_col.find_one({'session_id': session_id}, {'_id': 0, 'messages': 1})
            if doc and doc.get('messages'):
                messages = doc['messages'][-100:]  # Last 100 messages
        except:
            pass
    
    # Fallback to memory
    if not messages and session_id in chat_sessions:
        messages = chat_sessions[session_id][-100:]
    
    return jsonify({'success': True, 'messages': messages, 'count': len(messages)})


@lilith_page_bp.route('/api/avatar/<state>')
def get_avatar_state(state):
    """Get avatar image for emotional state"""
    global AVATAR_STATES
    
    if state not in AVATAR_STATES:
        state = "idle"
    
    # Check if we have cached this state
    if AVATAR_STATES.get(state):
        return Response(AVATAR_STATES[state], mimetype='image/webp')
    
    # For idle, return base image
    if state == "idle":
        try:
            r = requests.get(LILITH_IMAGE_URL, timeout=30)
            if r.status_code == 200:
                return Response(r.content, mimetype='image/png')
        except:
            pass
        return Response("", status=404)
    
    # Generate reaction using AI Horde
    prompt = REACTION_PROMPTS.get(state, REACTION_PROMPTS["idle"])
    
    try:
        horde_resp = requests.post(
            "https://aihorde.net/api/v2/generate/async",
            json={
                "prompt": prompt + ", highly detailed, masterpiece, best quality, anime style",
                "params": {
                    "width": 512,
                    "height": 512,
                    "steps": 25,
                    "sampler_name": "k_euler_a",
                    "cfg_scale": 7
                },
                "nsfw": True,
                "censor_nsfw": False,
                "r2": True
            },
            headers={
                "Content-Type": "application/json",
                "apikey": "0000000000"
            },
            timeout=30
        )
        
        if horde_resp.status_code == 202:
            job_id = horde_resp.json().get("id")
            
            for _ in range(60):
                time.sleep(2)
                check = requests.get(f"https://aihorde.net/api/v2/generate/check/{job_id}", timeout=10)
                if check.status_code == 200 and check.json().get("done"):
                    result = requests.get(f"https://aihorde.net/api/v2/generate/status/{job_id}", timeout=30)
                    if result.status_code == 200:
                        gens = result.json().get("generations", [])
                        if gens and gens[0].get("img"):
                            img = gens[0]["img"]
                            if img.startswith("http"):
                                img_data = requests.get(img, timeout=30).content
                            else:
                                img_data = base64.b64decode(img)
                            
                            # Cache it
                            AVATAR_STATES[state] = img_data
                            return Response(img_data, mimetype='image/webp')
                    break
    except Exception as e:
        print(f"Avatar generation error: {e}")
    
    # Fallback to base image
    try:
        r = requests.get(LILITH_IMAGE_URL, timeout=30)
        if r.status_code == 200:
            return Response(r.content, mimetype='image/png')
    except:
        pass
    
    return Response("", status=500)


@lilith_page_bp.route('/api/avatar/preload', methods=['POST'])
def preload_avatars():
    """Pre-generate all avatar states"""
    results = {}
    for state in AVATAR_STATES.keys():
        if state == "idle":
            results[state] = "base image"
            continue
        try:
            # Trigger generation (async)
            requests.get(f"http://localhost:3000/lilith/api/avatar/{state}", timeout=5)
            results[state] = "generating"
        except:
            results[state] = "queued"
    return jsonify({"success": True, "states": results})


def create_lilith_app():
    app = Flask(__name__)
    app.register_blueprint(lilith_page_bp, url_prefix='/lilith')
    return app


if __name__ == '__main__':
    app = create_lilith_app()
    app.run(host='0.0.0.0', port=6666, debug=True)
