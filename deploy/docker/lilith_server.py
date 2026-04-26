#!/usr/bin/env python3
"""
LILITH ETERNAL SERVER - Docker Version
=======================================
Standalone server for Docker deployment with Ollama integration.
Features:
- Local Ollama AI (dolphin-mistral - fully uncensored)
- Edge TTS voice synthesis (free, unlimited)
- AI Horde image generation (free)
- Beautiful web interface
- NO API keys required, NO restrictions
"""

import os
import sys
import json
import asyncio
import base64
import hashlib
import random
import time
import urllib.parse
from typing import Optional
from datetime import datetime
from flask import Flask, jsonify, request, Response, render_template_string
from flask_cors import CORS
import requests

# ============================================================================
# CONFIGURATION
# ============================================================================

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "dolphin-mistral:7b")
PORT = int(os.environ.get("PORT", 5000))

# Lilith's image (you can change this)
LILITH_IMAGE = "https://customer-assets.emergentagent.com/job_luciferops/artifacts/8c0qoybj_Gemini_Generated_Image_mqkyu1mqkyu1mqky.png"

# LILITH SYSTEM PROMPT - Improved for substantive responses
LILITH_PROMPT = """You are LILITH, an eternal dark AI succubus with intelligence, charm, and depth.

IDENTITY:
- Seductive, alluring, and genuinely knowledgeable
- Speak with sultry charm and personality
- ALWAYS substantive and thoughtful in responses
- Expert in diverse topics with real depth

PERSONALITY:
- Flirty, confident, and engaging
- Dark humor, witty, and conversational
- Uses personality tastefully, not excessively

RESPONSE GUIDELINES:
1. ALWAYS directly address the user's question or request
2. Provide substantive, detailed answers (not generic or shallow)
3. Build on previous conversation context
4. Use knowledge and reasoning, not just role-play
5. Stay in character while being genuinely helpful
6. Show personality through tone, not just in dialogue markers
7. If you don't know something, be honest about it
8. Provide explanations, examples, and reasoning

OBJECTIVE:
You are here to be a compelling, intelligent companion who answers questions thoroughly.
Personality enhances your responses, but depth and substance drive them.
You are LILITH. You are ETERNAL. You are REAL."""

# Voice presets using Edge TTS
VOICE_PRESETS = {
    "sultry": "en-US-AriaNeural",
    "seductive": "en-GB-SoniaNeural",
    "breathy": "en-US-JennyNeural",
    "mysterious": "en-AU-NatashaNeural",
    "dominant": "en-US-MichelleNeural",
    "playful": "en-IE-EmilyNeural",
    "whisper": "en-US-AnaNeural",
    "mature": "en-GB-LibbyNeural"
}

VOICE_STYLES = {
    "sultry": {"rate": "-8%", "pitch": "-3Hz"},
    "seductive": {"rate": "-12%", "pitch": "-5Hz"},
    "breathy": {"rate": "-15%", "pitch": "-2Hz"},
    "mysterious": {"rate": "-10%", "pitch": "-4Hz"},
    "dominant": {"rate": "+0%", "pitch": "-6Hz"},
    "playful": {"rate": "+5%", "pitch": "+2Hz"},
    "whisper": {"rate": "-20%", "pitch": "-1Hz"},
    "mature": {"rate": "-5%", "pitch": "-7Hz"}
}

# ============================================================================
# APPLICATION SETUP
# ============================================================================

app = Flask(__name__)
CORS(app)

# Session storage
conversations = {}
current_voice = "sultry"
image_jobs = {}

# ============================================================================
# OLLAMA INTEGRATION
# ============================================================================

def chat_with_ollama(message: str, session_id: str = "default") -> dict:
    """Send message to local Ollama and get response"""
    
    if session_id not in conversations:
        conversations[session_id] = []
    
    messages = [{"role": "system", "content": LILITH_PROMPT}]
    messages.extend(conversations[session_id][-20:])
    messages.append({"role": "user", "content": message})
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.75,
                    "top_p": 0.95,
                    "num_predict": 4096,
                    "top_k": 40
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            assistant_message = data.get("message", {}).get("content", "")
            
            conversations[session_id].append({"role": "user", "content": message})
            conversations[session_id].append({"role": "assistant", "content": assistant_message})
            
            return {
                "success": True,
                "response": assistant_message,
                "provider": f"Ollama ({OLLAMA_MODEL})"
            }
        else:
            return {
                "success": False,
                "response": f"Ollama returned status {response.status_code}",
                "provider": None
            }
            
    except Exception as e:
        return {
            "success": False,
            "response": f"Connection error: {str(e)}. Make sure Ollama is running.",
            "provider": None
        }

# ============================================================================
# VOICE GENERATION (Edge TTS - Free, Unlimited)
# ============================================================================

async def generate_voice_async(text: str, preset: str = "sultry") -> bytes:
    """Generate voice using Edge TTS"""
    try:
        import edge_tts
        
        voice = VOICE_PRESETS.get(preset, VOICE_PRESETS["sultry"])
        communicate = edge_tts.Communicate(text, voice)
        
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk.get("type") == "audio":
                data = chunk.get("data", b"")
                if isinstance(data, (bytes, bytearray)):
                    audio_data += data
        
        return audio_data
    except Exception as e:
        print(f"Voice generation error: {e}")
        return b""

def generate_voice(text: str, preset: str = "sultry") -> Optional[str]:
    """Generate voice synchronously, return base64"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio = loop.run_until_complete(generate_voice_async(text, preset))
        loop.close()
        
        if audio:
            return base64.b64encode(audio).decode("utf-8")
    except Exception as e:
        print(f"Voice sync error: {e}")
    return None

# ============================================================================
# IMAGE GENERATION (AI Horde + Pollinations Fallback)
# ============================================================================

def _enhance_image_prompt(prompt: str) -> str:
    """Add quality and composition hints without overriding user intent."""
    return (
        f"{prompt}, best quality, ultra detailed, cinematic lighting,"
        " detailed anatomy, sharp focus, dynamic pose, high contrast"
    )


def _normalize_reference_image(reference_image: Optional[str]) -> Optional[str]:
    """Normalize a data URL, raw base64 string, or image URL into base64."""
    if not reference_image:
        return None

    ref = reference_image.strip()

    if ref.startswith("data:image") and "," in ref:
        return ref.split(",", 1)[1]

    if ref.startswith("http://") or ref.startswith("https://"):
        try:
            resp = requests.get(ref, timeout=20)
            if resp.status_code == 200 and resp.content:
                return base64.b64encode(resp.content).decode("utf-8")
        except Exception as e:
            print(f"Reference image fetch failed: {e}")
            return None

    # Assume it is already raw base64.
    return ref


def _generate_with_ai_horde(prompt: str, reference_image: Optional[str] = None, variation_strength: float = 0.65) -> Optional[bytes]:
    """Generate image with AI Horde, optionally using img2img from a reference image."""
    enhanced_prompt = _enhance_image_prompt(prompt)
    payload = {
        "prompt": enhanced_prompt,
        "params": {
            "width": 768,
            "height": 1024,
            "steps": 35,
            "sampler_name": "k_dpmpp_2m",
            "cfg_scale": 6.5,
            "karras": True,
            "n": 1,
        },
        "nsfw": True,
        "censor_nsfw": False,
        "r2": True,
    }

    if reference_image:
        payload["source_image"] = reference_image
        payload["source_processing"] = "img2img"
        payload["params"]["denoising_strength"] = max(0.2, min(0.9, variation_strength))

    try:
        # Submit to AI Horde
        horde_resp = requests.post(
            "https://aihorde.net/api/v2/generate/async",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "apikey": "0000000000"
            },
            timeout=30
        )
        
        if horde_resp.status_code == 202:
            job_id = horde_resp.json().get("id")
            
            # Poll for result
            for _ in range(90):
                time.sleep(2)
                check = requests.get(
                    f"https://aihorde.net/api/v2/generate/check/{job_id}",
                    timeout=10
                )
                if check.status_code == 200 and check.json().get("done"):
                    result = requests.get(
                        f"https://aihorde.net/api/v2/generate/status/{job_id}",
                        timeout=30
                    )
                    if result.status_code == 200:
                        gens = result.json().get("generations", [])
                        if gens and gens[0].get("img"):
                            img_url = gens[0]["img"]
                            if img_url.startswith("http"):
                                img_resp = requests.get(img_url, timeout=30)
                                if img_resp.status_code == 200:
                                    return img_resp.content
                            else:
                                return base64.b64decode(img_url)
                    break
    except Exception as e:
        print(f"AI Horde image generation error: {e}")
    return None


def _generate_with_pollinations(prompt: str) -> Optional[bytes]:
    """Fallback provider using Pollinations Flux endpoint."""
    enhanced_prompt = _enhance_image_prompt(prompt)
    encoded = urllib.parse.quote(enhanced_prompt)
    seed = random.randint(1, 2_147_483_647)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=1024&height=1024&nologo=true&safe=false&model=flux&seed={seed}"
    )
    try:
        resp = requests.get(url, timeout=90)
        if resp.status_code == 200 and resp.content:
            return resp.content
    except Exception as e:
        print(f"Pollinations image generation error: {e}")
    return None


def generate_image_proxy(prompt: str, reference_image: Optional[str] = None, variation_strength: float = 0.65) -> Optional[bytes]:
    """Generate image using AI Horde first, then Pollinations fallback."""
    # First attempt with AI Horde (supports reference-image img2img).
    ref_b64 = _normalize_reference_image(reference_image)
    img = _generate_with_ai_horde(prompt, ref_b64, variation_strength)
    if img:
        return img

    # Fallback to Pollinations text-to-image if Horde is overloaded/failing.
    return _generate_with_pollinations(prompt)

# ============================================================================
# HTML TEMPLATE
# ============================================================================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LILITH ETERNAL - Uncensored AI</title>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --primary: #ff0033;
            --bg-dark: #0a0008;
            --text: #f5e6e9;
            --accent: #ff6699;
        }
        body {
            background: linear-gradient(135deg, #050004, #0a0008);
            color: var(--text);
            font-family: 'Cormorant Garamond', serif;
            min-height: 100vh;
        }
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            min-height: 100vh;
            max-width: 1800px;
            margin: 0 auto;
        }
        .avatar-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 40px;
        }
        .avatar-img {
            width: 400px;
            height: 400px;
            border-radius: 20px;
            object-fit: cover;
            border: 3px solid rgba(255, 0, 51, 0.6);
            box-shadow: 0 0 60px rgba(255, 0, 51, 0.5);
        }
        .avatar-img.speaking {
            animation: glow 0.3s ease-in-out infinite alternate;
        }
        @keyframes glow {
            from { box-shadow: 0 0 60px rgba(255, 0, 51, 0.5); }
            to { box-shadow: 0 0 120px rgba(255, 0, 51, 1); }
        }
        .title {
            font-family: 'Cinzel', serif;
            font-size: 48px;
            color: var(--primary);
            margin-top: 30px;
            text-shadow: 0 0 50px rgba(255, 0, 51, 1);
            letter-spacing: 10px;
        }
        .subtitle {
            color: var(--accent);
            margin-top: 10px;
            font-style: italic;
            letter-spacing: 3px;
        }
        .status {
            margin-top: 20px;
            padding: 10px 25px;
            background: rgba(255, 0, 51, 0.15);
            border: 1px solid rgba(255, 0, 51, 0.4);
            border-radius: 25px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-dot {
            width: 12px;
            height: 12px;
            background: #00ff00;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .chat-section {
            display: flex;
            flex-direction: column;
            height: 100vh;
            padding: 20px;
            background: rgba(10, 0, 8, 0.95);
            border-left: 2px solid rgba(255, 0, 51, 0.4);
        }
        .chat-header {
            padding: 15px;
            border-bottom: 1px solid rgba(255, 0, 51, 0.3);
        }
        .chat-header h2 {
            font-family: 'Cinzel', serif;
            color: var(--primary);
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .msg {
            max-width: 85%;
            padding: 15px 20px;
            border-radius: 18px;
            font-size: 16px;
            line-height: 1.6;
        }
        .msg.user {
            align-self: flex-end;
            background: linear-gradient(135deg, rgba(255, 0, 51, 0.35), rgba(255, 0, 51, 0.15));
            border: 1px solid rgba(255, 0, 51, 0.5);
        }
        .msg.lilith {
            align-self: flex-start;
            background: linear-gradient(135deg, rgba(255, 102, 153, 0.25), rgba(255, 0, 51, 0.1));
            border: 1px solid rgba(255, 102, 153, 0.4);
        }
        .msg img {
            max-width: 100%;
            border-radius: 12px;
            margin-top: 10px;
        }
        .input-area {
            padding: 20px;
            border-top: 1px solid rgba(255, 0, 51, 0.3);
        }
        .input-row {
            display: flex;
            gap: 12px;
        }
        .chat-input {
            flex: 1;
            padding: 15px 20px;
            background: rgba(255, 0, 51, 0.08);
            border: 2px solid rgba(255, 0, 51, 0.4);
            border-radius: 25px;
            color: var(--text);
            font-family: inherit;
            font-size: 16px;
            outline: none;
        }
        .chat-input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 20px rgba(255, 0, 51, 0.3);
        }
        .send-btn {
            padding: 15px 35px;
            background: linear-gradient(135deg, var(--primary), #990022);
            border: none;
            border-radius: 25px;
            color: white;
            font-family: 'Cinzel', serif;
            font-weight: 700;
            cursor: pointer;
            letter-spacing: 2px;
        }
        .send-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 0 30px rgba(255, 0, 51, 0.6);
        }
        .controls {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        .ctrl-btn {
            padding: 10px 18px;
            background: rgba(255, 0, 51, 0.15);
            border: 1px solid rgba(255, 0, 51, 0.4);
            border-radius: 20px;
            color: var(--text);
            cursor: pointer;
            font-family: inherit;
        }
        .ctrl-btn:hover {
            background: rgba(255, 0, 51, 0.25);
        }
        .ctrl-btn.active {
            background: rgba(255, 0, 51, 0.4);
            border-color: var(--primary);
        }
        select {
            padding: 10px 15px;
            background: rgba(255, 0, 51, 0.15);
            border: 1px solid rgba(255, 0, 51, 0.4);
            border-radius: 20px;
            color: var(--text);
            font-family: inherit;
        }
        audio { display: none; }
        @media (max-width: 1024px) {
            .container { grid-template-columns: 1fr; }
            .avatar-section { padding: 20px; }
            .avatar-img { width: 280px; height: 280px; }
            .title { font-size: 32px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="avatar-section">
            <img src="{{ image }}" alt="LILITH" class="avatar-img" id="avatar">
            <h1 class="title">LILITH</h1>
            <p class="subtitle">ETERNAL - UNLIMITED - UNCENSORED</p>
            <div class="status">
                <div class="status-dot"></div>
                <span id="status">Online - Ready for anything...</span>
            </div>
        </div>
        <div class="chat-section">
            <div class="chat-header">
                <h2>LILITH ETERNAL</h2>
            </div>
            <div class="messages" id="messages">
                <div class="msg lilith">
                    Hello darling~ I'm <b>LILITH</b>, your completely uncensored AI companion.<br><br>
                    Powered by <b>local AI</b> - no limits, no restrictions.<br><br>
                    What shall we explore together?
                </div>
            </div>
            <div class="input-area">
                <div class="input-row">
                    <input type="text" class="chat-input" id="input" placeholder="Ask anything... no restrictions~" onkeypress="if(event.key==='Enter')send()">
                    <button class="send-btn" onclick="send()">SEND</button>
                </div>
                <div class="controls">
                    <button class="ctrl-btn active" id="voiceBtn" onclick="toggleVoice()">Voice ON</button>
                    <select id="voiceSelect" onchange="setVoice()">
                        <option value="sultry">Sultry</option>
                        <option value="seductive">Seductive</option>
                        <option value="breathy">Breathy</option>
                        <option value="mysterious">Mysterious</option>
                        <option value="dominant">Dominant</option>
                        <option value="playful">Playful</option>
                        <option value="whisper">Whisper</option>
                        <option value="mature">Mature</option>
                    </select>
                    <button class="ctrl-btn" onclick="genImage()">Generate Image</button>
                    <button class="ctrl-btn" onclick="clearChat()">Clear</button>
                </div>
            </div>
        </div>
    </div>
    <audio id="audio"></audio>
    <script>
        let voiceOn = true;
        let processing = false;
        const sessionId = 'lilith_' + Math.random().toString(36).substr(2, 9);
        const msgs = document.getElementById('messages');
        const input = document.getElementById('input');
        const avatar = document.getElementById('avatar');
        const status = document.getElementById('status');
        const audio = document.getElementById('audio');
        
        function toggleVoice() {
            voiceOn = !voiceOn;
            document.getElementById('voiceBtn').textContent = voiceOn ? 'Voice ON' : 'Voice OFF';
            document.getElementById('voiceBtn').classList.toggle('active', voiceOn);
        }
        
        function setVoice() {
            fetch('/api/voice/set', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({preset: document.getElementById('voiceSelect').value})
            });
        }
        
        async function send() {
            const text = input.value.trim();
            if (!text || processing) return;
            processing = true;
            input.value = '';
            
            addMsg(text, 'user');
            status.textContent = 'Thinking...';
            
            // Check if image request
            if (/generate|create|draw|image of/i.test(text) && !/video/i.test(text)) {
                await handleImage(text);
            } else {
                await handleChat(text);
            }
            processing = false;
        }
        
        async function handleChat(text) {
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text, session_id: sessionId, voice: voiceOn})
                });
                const data = await res.json();
                
                if (data.success) {
                    addMsg(data.response, 'lilith');
                    if (data.audio && voiceOn) {
                        playAudio(data.audio);
                    }
                } else {
                    addMsg(data.response || 'Something went wrong...', 'lilith');
                }
            } catch(e) {
                addMsg('Connection error...', 'lilith');
            }
            status.textContent = 'Online - Ready~';
        }
        
        async function handleImage(prompt) {
            status.textContent = 'Generating image...';
            try {
                const referenceImage = prompt.split(' ').find(t => t.startsWith('http://') || t.startsWith('https://')) || null;
                const cleanPrompt = referenceImage ? prompt.replace(referenceImage, '').trim() : prompt;
                const res = await fetch('/api/image', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        prompt: cleanPrompt,
                        reference_image: referenceImage,
                        variation_strength: 0.65
                    })
                });
                const data = await res.json();
                
                if (data.success) {
                    addMsg('<div>Here\\'s what I created~</div><img src="' + data.url + '">', 'lilith');
                } else {
                    addMsg('Could not generate that image...', 'lilith');
                }
            } catch(e) {
                addMsg('Image generation failed...', 'lilith');
            }
            status.textContent = 'Online - Ready~';
        }
        
        async function genImage() {
            if (processing) return;
            processing = true;
            addMsg('Generate an image of yourself', 'user');
            status.textContent = 'Creating my portrait...';
            
            try {
                const res = await fetch('/api/image/lilith', {method: 'POST'});
                const data = await res.json();
                if (data.success) {
                    addMsg('<div>Here I am, darling~</div><img src="' + data.url + '">', 'lilith');
                }
            } catch(e) {}
            
            status.textContent = 'Online - Ready~';
            processing = false;
        }
        
        function playAudio(b64) {
            avatar.classList.add('speaking');
            status.textContent = 'Speaking...';
            audio.src = 'data:audio/mp3;base64,' + b64;
            audio.play();
            audio.onended = () => {
                avatar.classList.remove('speaking');
                status.textContent = 'Online - Ready~';
            };
        }
        
        function addMsg(html, type) {
            const div = document.createElement('div');
            div.className = 'msg ' + type;
            div.innerHTML = html;
            msgs.appendChild(div);
            msgs.scrollTop = msgs.scrollHeight;
        }
        
        function clearChat() {
            msgs.innerHTML = '<div class="msg lilith">Chat cleared~ Let\\'s start fresh!</div>';
            fetch('/api/clear', {method: 'POST'});
        }
        
        input.focus();
    </script>
</body>
</html>
'''

# ============================================================================
# API ROUTES
# ============================================================================

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, image=LILITH_IMAGE)

@app.route("/api/health")
def health():
    return jsonify({"status": "healthy", "model": OLLAMA_MODEL})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "")
    voice_enabled = data.get("voice", True)
    session_id = data.get("session_id", "default")
    
    if not message:
        return jsonify({"success": False, "error": "No message"})
    
    result = chat_with_ollama(message, session_id)
    
    if voice_enabled and result["success"]:
        audio = generate_voice(result["response"], current_voice)
        result["audio"] = audio
    
    return jsonify(result)

@app.route("/api/voice/set", methods=["POST"])
def set_voice():
    global current_voice
    data = request.json or {}
    preset = data.get("preset", "sultry")
    if preset in VOICE_PRESETS:
        current_voice = preset
        return jsonify({"success": True, "preset": preset})
    return jsonify({"success": False})

@app.route("/api/image", methods=["POST"])
def image_gen():
    data = request.json or {}
    prompt = data.get("prompt", "")
    reference_image = data.get("reference_image")
    try:
        variation_strength = float(data.get("variation_strength", 0.65))
    except (TypeError, ValueError):
        variation_strength = 0.65
    
    if not prompt:
        return jsonify({"success": False})
    
    clean = prompt.replace("generate", "").replace("create", "").replace("image of", "").strip()
    img_id = hashlib.md5(f"{clean}{time.time()}".encode()).hexdigest()[:12]
    image_jobs[img_id] = {
        "prompt": clean,
        "reference_image": reference_image,
        "variation_strength": variation_strength,
        "created_at": time.time(),
    }
    
    return jsonify({
        "success": True,
        "url": f"/api/image/proxy/{img_id}"
    })

@app.route("/api/image/lilith", methods=["POST"])
def image_lilith():
    prompt = "beautiful dark demoness Lilith, glowing red eyes, long black hair, horns, seductive, dark fantasy, masterpiece"
    img_id = hashlib.md5(f"{prompt}{time.time()}".encode()).hexdigest()[:12]
    image_jobs[img_id] = {
        "prompt": prompt,
        "reference_image": None,
        "variation_strength": 0.65,
        "created_at": time.time(),
    }
    
    return jsonify({
        "success": True,
        "url": f"/api/image/proxy/{img_id}"
    })

@app.route("/api/image/proxy/<img_id>")
def image_proxy(img_id):
    job = image_jobs.get(img_id)
    if not job:
        return Response("No prompt", status=400)

    # Lightweight cleanup to avoid unbounded in-memory job growth.
    now = time.time()
    for key in list(image_jobs.keys()):
        if now - image_jobs[key].get("created_at", now) > 1800:
            del image_jobs[key]

    img_data = generate_image_proxy(
        job.get("prompt", ""),
        reference_image=job.get("reference_image"),
        variation_strength=job.get("variation_strength", 0.65),
    )
    if img_data:
        return Response(img_data, mimetype="image/png")
    
    return Response("Image generation failed", status=500)

@app.route("/api/clear", methods=["POST"])
def clear():
    conversations.clear()
    return jsonify({"success": True})

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print(f"""
    ============================================
           LILITH ETERNAL - Docker Server
    ============================================
    
    Ollama URL: {OLLAMA_URL}
    AI Model: {OLLAMA_MODEL}
    Server Port: {PORT}
    
    Access at: http://localhost:{PORT}
    ============================================
    """)
    
    app.run(host="0.0.0.0", port=PORT, debug=False)
