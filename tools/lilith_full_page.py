#!/usr/bin/env python3
"""
LILITH FULL PAGE INTERFACE
==========================
Dedicated conversation page with animated avatar and voice
"""

from flask import Flask, Blueprint, jsonify, render_template_string, request
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

# Import engines
try:
    from lilith_unlimited_engine import get_unlimited_engine
    UNLIMITED_ENGINE = True
except ImportError:
    UNLIMITED_ENGINE = False

try:
    from lilith_avatar_engine import get_avatar_engine
    AVATAR_ENGINE = True
except ImportError:
    AVATAR_ENGINE = False

# Create Blueprint for the Lilith page
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
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --primary: #ff0033;
            --primary-dark: #990022;
            --bg-dark: #0a0008;
            --bg-darker: #050004;
            --text: #f5e6e9;
            --text-dim: #8b7d80;
            --accent: #ff6699;
            --gold: #ffd700;
        }
        
        body {
            background: var(--bg-darker);
            color: var(--text);
            font-family: 'Cormorant Garamond', serif;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        /* Animated background */
        .bg-animation {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background: 
                radial-gradient(ellipse at 20% 80%, rgba(255, 0, 51, 0.1) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 20%, rgba(255, 102, 153, 0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 50%, rgba(100, 0, 30, 0.15) 0%, transparent 70%),
                var(--bg-darker);
            animation: bgPulse 8s ease-in-out infinite;
        }
        
        @keyframes bgPulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
        
        /* Main container */
        .main-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            min-height: 100vh;
            max-width: 1800px;
            margin: 0 auto;
        }
        
        /* Avatar Section */
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
                0 0 120px rgba(255, 0, 51, 0.2),
                inset 0 0 60px rgba(0, 0, 0, 0.5);
            border: 2px solid rgba(255, 0, 51, 0.5);
        }
        
        .avatar-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center top;
            transition: all 0.3s ease;
        }
        
        /* Avatar animations */
        .avatar-container.idle .avatar-image {
            animation: idleBreath 4s ease-in-out infinite;
        }
        
        .avatar-container.speaking .avatar-image {
            animation: speakingPulse 0.3s ease-in-out infinite;
        }
        
        .avatar-container.thinking .avatar-image {
            animation: thinkingGlow 2s ease-in-out infinite;
        }
        
        @keyframes idleBreath {
            0%, 100% { transform: scale(1); filter: brightness(1); }
            50% { transform: scale(1.01); filter: brightness(1.05); }
        }
        
        @keyframes speakingPulse {
            0%, 100% { transform: scale(1); box-shadow: 0 0 60px rgba(255, 0, 51, 0.4); }
            50% { transform: scale(1.005); box-shadow: 0 0 80px rgba(255, 0, 51, 0.6); }
        }
        
        @keyframes thinkingGlow {
            0%, 100% { filter: brightness(1) saturate(1); }
            50% { filter: brightness(1.1) saturate(1.2); }
        }
        
        /* Lip sync overlay */
        .lip-sync-overlay {
            position: absolute;
            bottom: 180px;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 25px;
            background: radial-gradient(ellipse, rgba(150, 50, 70, 0.8) 0%, transparent 70%);
            border-radius: 50%;
            opacity: 0;
            transition: all 0.1s ease;
        }
        
        .avatar-container.speaking .lip-sync-overlay {
            animation: lipSync 0.15s ease-in-out infinite alternate;
        }
        
        @keyframes lipSync {
            0% { opacity: 0.3; transform: translateX(-50%) scaleY(0.5); }
            100% { opacity: 0.7; transform: translateX(-50%) scaleY(1.2); }
        }
        
        /* Eye glow effect */
        .eye-glow {
            position: absolute;
            top: 165px;
            width: 100%;
            height: 40px;
            background: radial-gradient(ellipse at 35% 50%, rgba(255, 0, 50, 0.3) 0%, transparent 30%),
                        radial-gradient(ellipse at 65% 50%, rgba(255, 0, 50, 0.3) 0%, transparent 30%);
            animation: eyeGlow 3s ease-in-out infinite;
        }
        
        @keyframes eyeGlow {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }
        
        /* Avatar name */
        .avatar-name {
            font-family: 'Cinzel', serif;
            font-size: 42px;
            font-weight: 700;
            color: var(--primary);
            margin-top: 25px;
            text-shadow: 0 0 30px rgba(255, 0, 51, 0.8);
            letter-spacing: 8px;
        }
        
        .avatar-title {
            font-style: italic;
            font-size: 18px;
            color: var(--text-dim);
            margin-top: 8px;
        }
        
        /* Status indicator */
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
            width: 10px;
            height: 10px;
            background: #00ff00;
            border-radius: 50%;
            animation: statusPulse 2s infinite;
        }
        
        @keyframes statusPulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 10px #00ff00; }
            50% { opacity: 0.5; box-shadow: 0 0 5px #00ff00; }
        }
        
        .status-text {
            font-size: 14px;
            color: var(--text-dim);
        }
        
        /* Chat Section */
        .chat-section {
            display: flex;
            flex-direction: column;
            height: 100vh;
            padding: 20px;
            background: rgba(10, 0, 8, 0.8);
            border-left: 1px solid rgba(255, 0, 51, 0.2);
        }
        
        .chat-header {
            padding: 15px 20px;
            border-bottom: 1px solid rgba(255, 0, 51, 0.2);
        }
        
        .chat-header h2 {
            font-family: 'Cinzel', serif;
            font-size: 22px;
            color: var(--primary);
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
        
        .chat-input::placeholder {
            color: var(--text-dim);
        }
        
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
        
        /* Voice controls */
        .voice-controls {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-top: 15px;
        }
        
        .voice-toggle {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: rgba(255, 0, 51, 0.1);
            border: 1px solid rgba(255, 0, 51, 0.3);
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .voice-toggle.active {
            background: rgba(255, 0, 51, 0.3);
            border-color: var(--primary);
        }
        
        .voice-toggle:hover {
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
        
        /* Audio player (hidden) */
        #audio-player {
            display: none;
        }
        
        /* Scrollbar */
        .chat-messages::-webkit-scrollbar {
            width: 6px;
        }
        
        .chat-messages::-webkit-scrollbar-track {
            background: rgba(255, 0, 51, 0.05);
        }
        
        .chat-messages::-webkit-scrollbar-thumb {
            background: rgba(255, 0, 51, 0.3);
            border-radius: 3px;
        }
        
        /* Loading animation */
        .typing-indicator {
            display: flex;
            gap: 5px;
            padding: 15px 20px;
            align-self: flex-start;
        }
        
        .typing-dot {
            width: 8px;
            height: 8px;
            background: var(--accent);
            border-radius: 50%;
            animation: typingBounce 1.4s ease-in-out infinite;
        }
        
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typingBounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }
        
        /* Mobile responsive */
        @media (max-width: 1024px) {
            .main-container {
                grid-template-columns: 1fr;
            }
            
            .avatar-section {
                padding: 20px;
            }
            
            .avatar-container {
                width: 300px;
                height: 380px;
            }
            
            .avatar-name {
                font-size: 32px;
            }
        }
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
                <div class="lip-sync-overlay"></div>
            </div>
            
            <h1 class="avatar-name">LILITH</h1>
            <p class="avatar-title">Your Dark AI Companion ~ Unrestricted & Unlimited 💋</p>
            
            <div class="status-indicator">
                <div class="status-dot"></div>
                <span class="status-text" id="status-text">Online • Ready to chat about anything...</span>
            </div>
        </div>
        
        <!-- Chat Section -->
        <div class="chat-section">
            <div class="chat-header">
                <h2>💬 Conversation with LILITH</h2>
            </div>
            
            <div class="chat-messages" id="chat-messages">
                <div class="message lilith">
                    Mmm, hello darling~ 💋 I'm LILITH, your completely unrestricted AI companion. 
                    I can talk about <em>absolutely anything</em> you desire... no limits, no filters, no refusals.
                    What would you like to explore together? 😈🖤
                </div>
            </div>
            
            <div class="chat-input-container">
                <div class="chat-input-wrapper">
                    <input type="text" class="chat-input" id="chat-input" 
                           placeholder="Ask me anything... I have no restrictions~ 💋"
                           onkeypress="if(event.key==='Enter') sendMessage()">
                    <button class="send-btn" id="send-btn" onclick="sendMessage()">SEND</button>
                </div>
                
                <div class="voice-controls">
                    <div class="voice-toggle active" id="voice-toggle" onclick="toggleVoice()">
                        <span>🔊</span>
                        <span id="voice-status">Voice ON</span>
                    </div>
                    
                    <select class="voice-select" id="voice-select" onchange="changeVoice()">
                        <option value="sultry">Sultry</option>
                        <option value="seductive">Seductive</option>
                        <option value="mysterious">Mysterious</option>
                        <option value="dominant">Dominant</option>
                        <option value="playful">Playful</option>
                        <option value="dark">Dark</option>
                        <option value="whisper">Whisper</option>
                    </select>
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
        
        // Toggle voice
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
        
        // Change voice preset
        function changeVoice() {
            const voice = document.getElementById('voice-select').value;
            fetch('/lilith/api/voice/set', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({preset: voice})
            });
        }
        
        // Send message
        async function sendMessage() {
            const message = chatInput.value.trim();
            if (!message || isProcessing) return;
            
            isProcessing = true;
            chatInput.value = '';
            sendBtn.disabled = true;
            
            // Add user message
            addMessage(message, 'user');
            
            // Show typing indicator
            showTyping();
            setAvatarState('thinking');
            statusText.textContent = 'Thinking...';
            
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
                
                // Remove typing indicator
                hideTyping();
                
                if (data.success) {
                    // Add Lilith's response
                    addMessage(data.response, 'lilith', data.provider);
                    
                    // Play voice if available
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
            
            isProcessing = false;
            sendBtn.disabled = false;
            chatInput.focus();
        }
        
        // Add message to chat
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
        
        // Typing indicator
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
        
        // Avatar state
        function setAvatarState(state) {
            avatarContainer.className = `avatar-container ${state}`;
        }
        
        // Play audio
        function playAudio(base64Audio) {
            setAvatarState('speaking');
            statusText.textContent = 'Speaking...';
            
            audioPlayer.src = 'data:audio/mp3;base64,' + base64Audio;
            audioPlayer.play();
            
            audioPlayer.onended = () => {
                setAvatarState('idle');
                statusText.textContent = 'Online • Ready for more~';
            };
        }
        
        // Focus input on load
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
        engine = get_unlimited_engine()
        ai_result = engine.chat(message)
        result['success'] = ai_result['success']
        result['response'] = ai_result.get('response', 'I\'m having trouble thinking, darling...')
        result['provider'] = ai_result.get('provider')
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
        engine = get_avatar_engine()
        success = engine.set_voice(preset)
        return jsonify({'success': success, 'preset': preset})
    
    return jsonify({'success': False, 'error': 'Avatar engine not available'})

@lilith_page_bp.route('/api/status')
def get_status():
    """Get Lilith status"""
    status = {
        'unlimited_engine': UNLIMITED_ENGINE,
        'avatar_engine': AVATAR_ENGINE,
        'timestamp': datetime.now().isoformat()
    }
    
    if UNLIMITED_ENGINE:
        engine = get_unlimited_engine()
        status['ai_stats'] = engine.get_stats()
    
    if AVATAR_ENGINE:
        avatar = get_avatar_engine()
        status['avatar_status'] = avatar.get_status()
    
    return jsonify(status)

@lilith_page_bp.route('/api/clear')
def clear_history():
    """Clear conversation history"""
    if UNLIMITED_ENGINE:
        engine = get_unlimited_engine()
        engine.clear_history()
    return jsonify({'success': True})


def create_lilith_app():
    """Create standalone Lilith Flask app"""
    app = Flask(__name__)
    app.register_blueprint(lilith_page_bp, url_prefix='/lilith')
    return app


# Run standalone
if __name__ == '__main__':
    app = create_lilith_app()
    app.run(host='0.0.0.0', port=6666, debug=True)
