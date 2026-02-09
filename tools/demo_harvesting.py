#!/usr/bin/env python3
"""
Step-by-step API Key Harvesting Demo
Shows the process with detailed logging
"""

import time
import random
from datetime import datetime

def demo_step(step_num, title, description, duration=2):
    """Display a demo step"""
    print(f"\n{'='*70}")
    print(f"STEP {step_num}: {title}")
    print(f"{'='*70}")
    print(f"📋 {description}")
    print(f"⏳ Processing...", end='', flush=True)
    
    for i in range(duration):
        time.sleep(1)
        print(".", end='', flush=True)
    
    print(" ✓ Complete!")
    return True

def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║   LILITH Autonomous API Key Harvesting - Step-by-Step Demo    ║
╚════════════════════════════════════════════════════════════════╝

This demo simulates the autonomous harvesting process.
Watch as LILITH creates accounts and harvests API keys!
""")
    
    time.sleep(2)
    
    # Step 1: Initialize Browser
    demo_step(
        1,
        "Initialize Browser Automation",
        "Starting Playwright browser with stealth settings",
        duration=2
    )
    
    print("""
✓ Browser Configuration:
  - User Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0
  - Viewport: 1920x1080
  - Automation Detection: Disabled
    """)
    
    # Step 2: Create Temporary Email
    demo_step(
        2,
        "Create Temporary Email Account",
        "Navigating to GuerrillaMail.com to generate disposable email",
        duration=3
    )
    
    # Generate fake email
    random_id = random.randint(10000, 99999)
    temp_email = f"lilith{random_id}@guerrillamail.com"
    
    print(f"""
✓ Temporary Email Created:
  📧 Email: {temp_email}
  ⏰ Valid for: 60 minutes
  📬 Inbox: Active and monitoring
    """)
    
    # Step 3: Navigate to AI Provider
    demo_step(
        3,
        "Navigate to Groq Console",
        "Opening https://console.groq.com for signup",
        duration=2
    )
    
    print("""
✓ Page Loaded:
  🌐 URL: https://console.groq.com
  📄 Page Title: Groq Cloud - Fast AI Inference
  🔍 Looking for signup button...
    """)
    
    # Step 4: Fill Signup Form
    demo_step(
        4,
        "Automate Signup Process",
        "Filling registration form with generated credentials",
        duration=3
    )
    
    print(f"""
✓ Form Filled:
  📧 Email: {temp_email}
  👤 Username: user{random_id}
  🔐 Password: ************ (auto-generated)
  ✅ Terms: Accepted
  
  Submitting form...
    """)
    
    # Step 5: Monitor Email
    demo_step(
        5,
        "Monitor Email Inbox",
        "Checking for verification email from Groq",
        duration=4
    )
    
    print("""
✓ Email Received:
  📨 From: noreply@groq.com
  📝 Subject: Verify your Groq account
  🔗 Verification Link Found:
     https://console.groq.com/verify?token=abc123xyz789...
    """)
    
    # Step 6: Click Verification Link
    demo_step(
        6,
        "Complete Email Verification",
        "Clicking verification link to activate account",
        duration=3
    )
    
    print("""
✓ Account Verified:
  ✅ Email verification successful
  🎉 Account activated
  🏠 Redirected to dashboard
    """)
    
    # Step 7: Navigate to API Keys
    demo_step(
        7,
        "Navigate to API Keys Section",
        "Finding and clicking API Keys menu",
        duration=2
    )
    
    print("""
✓ API Keys Page Loaded:
  📍 URL: https://console.groq.com/keys
  🔑 Current Keys: 0
  ➕ "Create API Key" button found
    """)
    
    # Step 8: Generate API Key
    demo_step(
        8,
        "Generate New API Key",
        "Creating and extracting API key",
        duration=3
    )
    
    # Generate fake API key
    fake_key = f"gsk_{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=48))}"
    
    print(f"""
✓ API Key Generated:
  🔑 Key: {fake_key[:20]}...{fake_key[-10:]}
  📋 Full Key Copied
  ⚡ Rate Limit: 30 requests/minute
  💰 Free Tier: Active
    """)
    
    # Step 9: Save to Configuration
    demo_step(
        9,
        "Save Key to Configuration",
        "Updating system configuration with new API key",
        duration=2
    )
    
    print(f"""
✓ Configuration Updated:
  📁 Config File: /app/config/lucifera.conf
  🔧 Parameter: groq_api_key
  💾 Backup Created: lucifera.conf.backup
  
  Old Value: gsk_abc123... (expired)
  New Value: {fake_key[:20]}... (active)
    """)
    
    # Step 10: Validate and Integrate
    demo_step(
        10,
        "Validate and Integrate Key",
        "Testing new API key and reloading providers",
        duration=3
    )
    
    print("""
✓ Key Validation:
  🧪 Test Request: Success
  📊 Response Time: 245ms
  ✅ Model Access: llama-3.3-70b-versatile
  🔄 Provider Reloaded
    """)
    
    # Summary
    print(f"""

{'='*70}
🎉 API KEY HARVESTING COMPLETE!
{'='*70}

📊 HARVEST SUMMARY:
  Provider: Groq
  Email Used: {temp_email}
  API Key: {fake_key[:20]}...{fake_key[-10:]}
  Status: ✅ ACTIVE
  Timestamp: {datetime.now().isoformat()}

💾 FILES UPDATED:
  ✓ /app/config/lucifera.conf - Main configuration
  ✓ /app/config/harvested_keys.json - Key database

🚀 LILITH is now operational with fresh API credentials!
  
  Test the new key:
  curl -X POST http://127.0.0.1:5000/chat \\
    -H "Content-Type: application/json" \\
    -d '{{"message": "Hello LILITH, test new key"}}'

{'='*70}
""")
    
    print("\n✨ This demonstrates LILITH's autonomous self-sustaining capabilities!")
    print("   In production, this runs automatically when API keys fail.\n")

if __name__ == '__main__':
    main()
