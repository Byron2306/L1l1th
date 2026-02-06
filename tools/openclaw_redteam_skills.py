#!/usr/bin/env python3
"""
OpenClaw Skills Configuration for LuciferOS Red Team Operations

This module defines which OpenClaw skills are most relevant for penetration testing,
social engineering, and red team operations.
"""

# ============================================================================
# TIER 1: CRITICAL - Core Red Team Capabilities
# ============================================================================
CRITICAL_SKILLS = {
    'coding-agent': {
        'description': 'Run Codex/Claude Code for exploit development, script generation',
        'use_cases': [
            'Generate exploit code',
            'Create custom payloads',
            'Write automation scripts',
            'Develop evasion techniques',
            'Code analysis and review'
        ],
        'priority': 1
    },
    'github': {
        'description': 'GitHub CLI for repository analysis and secret hunting',
        'use_cases': [
            'Search repos for secrets/credentials',
            'Analyze target organization code',
            'Find exposed API keys',
            'Discover internal tooling',
            'CI/CD pipeline analysis'
        ],
        'priority': 1
    },
    'discord': {
        'description': 'Discord bot control for C2 and notifications',
        'use_cases': [
            'Command & Control channel',
            'Real-time attack notifications',
            'Team coordination',
            'Target community infiltration',
            'Data exfiltration channel'
        ],
        'priority': 1
    },
    'slack': {
        'description': 'Slack integration for enterprise reconnaissance',
        'use_cases': [
            'Enterprise target recon',
            'Internal comms monitoring',
            'Social engineering vector',
            'C2 for corporate targets',
            'Credential harvesting'
        ],
        'priority': 1
    },
    'himalaya': {
        'description': 'Email CLI for phishing and communication',
        'use_cases': [
            'Send phishing emails',
            'Monitor target inboxes (if compromised)',
            'Email-based C2',
            'Automated email campaigns',
            'Credential harvesting follow-up'
        ],
        'priority': 1
    },
}

# ============================================================================
# TIER 2: HIGH VALUE - Enhanced Capabilities
# ============================================================================
HIGH_VALUE_SKILLS = {
    'summarize': {
        'description': 'AI summarization for large document analysis',
        'use_cases': [
            'Analyze exfiltrated documents',
            'Process recon data',
            'Summarize target intelligence',
            'Extract key info from dumps'
        ],
        'priority': 2
    },
    'oracle': {
        'description': 'AI oracle for attack planning and analysis',
        'use_cases': [
            'Attack strategy planning',
            'Vulnerability analysis',
            'Risk assessment',
            'Decision support'
        ],
        'priority': 2
    },
    'nano-pdf': {
        'description': 'PDF processing and analysis',
        'use_cases': [
            'Extract metadata from target PDFs',
            'Analyze document structure',
            'Find hidden data in PDFs',
            'Create malicious PDFs'
        ],
        'priority': 2
    },
    'openai-whisper': {
        'description': 'Audio transcription for intelligence gathering',
        'use_cases': [
            'Transcribe recorded calls',
            'Process voicemails',
            'Analyze intercepted audio',
            'Voice phishing analysis'
        ],
        'priority': 2
    },
    'openai-whisper-api': {
        'description': 'Cloud-based audio transcription',
        'use_cases': [
            'Fast transcription of large files',
            'Real-time audio processing',
            'Multi-language support'
        ],
        'priority': 2
    },
    'openai-image-gen': {
        'description': 'AI image generation for social engineering',
        'use_cases': [
            'Create fake profile pictures',
            'Generate phishing content',
            'Create convincing documents',
            'Visual social engineering'
        ],
        'priority': 2
    },
    'camsnap': {
        'description': 'Camera/screenshot capture',
        'use_cases': [
            'Capture evidence',
            'Document exploitation',
            'Visual reconnaissance',
            'Screen monitoring'
        ],
        'priority': 2
    },
    'peekaboo': {
        'description': 'System surveillance and monitoring',
        'use_cases': [
            'Monitor target activity',
            'Capture screenshots',
            'Record sessions',
            'Evidence collection'
        ],
        'priority': 2
    },
}

# ============================================================================
# TIER 3: USEFUL - Supporting Capabilities  
# ============================================================================
USEFUL_SKILLS = {
    'trello': {
        'description': 'Project management for engagement tracking',
        'use_cases': [
            'Track pen test progress',
            'Manage findings',
            'Team task coordination'
        ],
        'priority': 3
    },
    'notion': {
        'description': 'Note-taking and documentation',
        'use_cases': [
            'Document findings',
            'Create reports',
            'Knowledge base'
        ],
        'priority': 3
    },
    'obsidian': {
        'description': 'Knowledge management',
        'use_cases': [
            'Link related findings',
            'Build attack graphs',
            'Document techniques'
        ],
        'priority': 3
    },
    'blogwatcher': {
        'description': 'Monitor blogs/feeds for vulnerabilities',
        'use_cases': [
            'Track 0-day disclosures',
            'Monitor security blogs',
            'Vulnerability intelligence'
        ],
        'priority': 3
    },
    'video-frames': {
        'description': 'Extract frames from video',
        'use_cases': [
            'Analyze surveillance footage',
            'Extract evidence from video',
            'Process screen recordings'
        ],
        'priority': 3
    },
    'weather': {
        'description': 'Weather data for physical operations',
        'use_cases': [
            'Plan physical pen tests',
            'Timing for on-site work',
            'Environmental factors'
        ],
        'priority': 3
    },
    'imsg': {
        'description': 'iMessage integration',
        'use_cases': [
            'Social engineering via iMessage',
            'Target communication'
        ],
        'priority': 3
    },
    'wacli': {
        'description': 'WhatsApp CLI',
        'use_cases': [
            'Social engineering via WhatsApp',
            'International target communication'
        ],
        'priority': 3
    },
    'bird': {
        'description': 'Twitter/X integration',
        'use_cases': [
            'OSINT on targets',
            'Social media reconnaissance',
            'Reputation monitoring'
        ],
        'priority': 3
    },
    'tmux': {
        'description': 'Terminal multiplexer',
        'use_cases': [
            'Manage multiple sessions',
            'Persistent attack sessions',
            'Multi-target operations'
        ],
        'priority': 3
    },
    'gemini': {
        'description': 'Google Gemini AI',
        'use_cases': [
            'Additional AI reasoning',
            'Fallback AI provider',
            'Multimodal analysis'
        ],
        'priority': 3
    },
    'skill-creator': {
        'description': 'Create custom OpenClaw skills',
        'use_cases': [
            'Build custom attack tools',
            'Extend platform capabilities',
            'Integrate new tools'
        ],
        'priority': 3
    },
}

# ============================================================================
# TIER 4: LOW PRIORITY - Not relevant for red team
# ============================================================================
LOW_PRIORITY_SKILLS = [
    '1password',        # Personal password manager
    'apple-notes',      # Mac notes app
    'apple-reminders',  # Mac reminders
    'bear-notes',       # Mac notes app
    'blucli',           # Bluetooth CLI
    'bluebubbles',      # iMessage bridge
    'canvas',           # Drawing
    'clawhub',          # OpenClaw hub
    'eightctl',         # 8base
    'food-order',       # Food ordering
    'gifgrep',          # GIF search
    'gog',              # Gaming (GOG)
    'goplaces',         # Location services
    'local-places',     # Local business search
    'mcporter',         # MCP tools
    'model-usage',      # AI model stats
    'nano-banana-pro',  # Unknown
    'openhue',          # Smart lights
    'ordercli',         # Food ordering
    'sag',              # Unknown
    'session-logs',     # Logging
    'sherpa-onnx-tts',  # Text to speech
    'songsee',          # Music recognition
    'sonoscli',         # Sonos speakers
    'spotify-player',   # Music
    'things-mac',       # Mac task manager
    'voice-call',       # Voice calling
]

# ============================================================================
# Helper Functions
# ============================================================================

def get_all_redteam_skills():
    """Get all skills relevant for red team operations"""
    skills = {}
    skills.update(CRITICAL_SKILLS)
    skills.update(HIGH_VALUE_SKILLS)
    skills.update(USEFUL_SKILLS)
    return skills

def get_skill_names_by_priority(max_priority=3):
    """Get skill names up to specified priority level"""
    skills = []
    if max_priority >= 1:
        skills.extend(CRITICAL_SKILLS.keys())
    if max_priority >= 2:
        skills.extend(HIGH_VALUE_SKILLS.keys())
    if max_priority >= 3:
        skills.extend(USEFUL_SKILLS.keys())
    return skills

def get_skill_prompt_context():
    """Generate a context string for AI prompts about available skills"""
    context = "Available OpenClaw skills for red team operations:\n\n"
    
    context += "🔴 CRITICAL (use frequently):\n"
    for name, info in CRITICAL_SKILLS.items():
        context += f"  • {name}: {info['description']}\n"
    
    context += "\n🟠 HIGH VALUE:\n"
    for name, info in HIGH_VALUE_SKILLS.items():
        context += f"  • {name}: {info['description']}\n"
    
    context += "\n🟡 USEFUL:\n"
    for name, info in list(USEFUL_SKILLS.items())[:8]:  # Top 8
        context += f"  • {name}: {info['description']}\n"
    
    return context

# Skill to command mapping for common operations
SKILL_COMMANDS = {
    'github': {
        'search_secrets': 'gh api search/code?q={query}+in:file+org:{org}',
        'list_repos': 'gh repo list {org} --limit 100',
        'get_commits': 'gh api repos/{owner}/{repo}/commits',
    },
    'discord': {
        'send_message': {'action': 'sendMessage', 'to': 'channel:{channel_id}', 'content': '{message}'},
        'read_messages': {'action': 'readMessages', 'channelId': '{channel_id}', 'limit': 50},
    },
    'slack': {
        'send_message': 'slack chat:send --channel {channel} --text "{message}"',
        'list_channels': 'slack channels:list',
    },
    'himalaya': {
        'send_email': 'himalaya send --to {to} --subject "{subject}" --body "{body}"',
        'list_emails': 'himalaya list --folder INBOX',
    },
}

if __name__ == '__main__':
    print("=" * 60)
    print("LuciferOS OpenClaw Red Team Skills Configuration")
    print("=" * 60)
    
    print(f"\n🔴 CRITICAL Skills ({len(CRITICAL_SKILLS)}):")
    for name in CRITICAL_SKILLS:
        print(f"   • {name}")
    
    print(f"\n🟠 HIGH VALUE Skills ({len(HIGH_VALUE_SKILLS)}):")
    for name in HIGH_VALUE_SKILLS:
        print(f"   • {name}")
    
    print(f"\n🟡 USEFUL Skills ({len(USEFUL_SKILLS)}):")
    for name in USEFUL_SKILLS:
        print(f"   • {name}")
    
    print(f"\n⚪ LOW PRIORITY Skills ({len(LOW_PRIORITY_SKILLS)}):")
    print(f"   (Not relevant for red team: {', '.join(LOW_PRIORITY_SKILLS[:5])}...)")
    
    total = len(CRITICAL_SKILLS) + len(HIGH_VALUE_SKILLS) + len(USEFUL_SKILLS)
    print(f"\n📊 TOTAL RELEVANT: {total} skills")
