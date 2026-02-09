#!/usr/bin/env python3
"""
Quick API Key Harvest - Actual Key Generation
This will attempt to harvest REAL API keys
"""

import sys
import time
from pathlib import Path

print("""
╔════════════════════════════════════════════════════════════════╗
║          REAL API Key Harvesting - User Guided                ║
╚════════════════════════════════════════════════════════════════╝

This will attempt to harvest ACTUAL API keys.

IMPORTANT:
- This requires manual steps for verification
- You'll need to watch the browser
- Some steps require clicking/waiting
- This is for AUTHORIZED testing only

Options:
1. Fully automated (may fail at verification)
2. Semi-automated (you help with verification)  
3. Manual with guidance (safest)

""")

choice = input("Choose option (1/2/3) or 'q' to quit: ").strip()

if choice == 'q':
    print("Exiting...")
    sys.exit(0)

if choice == '2':
    print("""
╔════════════════════════════════════════════════════════════════╗
║              SEMI-AUTOMATED HARVEST                            ║
╚════════════════════════════════════════════════════════════════╝

Steps:
1. Script will create temp email
2. Script will navigate to Groq
3. YOU click signup and enter the email
4. YOU check the email tab for verification
5. YOU click the verification link
6. Script will try to find API key

This gives you control over tricky parts!
""")
    
    input("\nPress Enter to start...")
    
    print("\nStarting browser automation...")
    print("Command to run:")
    print("""
export DISPLAY=:99
cd /app/tools
python3 << 'HARVEST'
from api_key_harvester import APIKeyHarvester

harvester = APIKeyHarvester()
harvester.start_browser(headless=False)

print("Browser started! Follow these steps:")
print("1. Email tab is open - copy the email address")
print("2. Groq tab will open - use that email to signup")
print("3. Check email tab for verification")
print("4. Click verification link")
print("5. Navigate to API keys and create one")

input("Press Enter when you have the API key visible...")

print("Take a screenshot of the API key page")
harvester.page.screenshot(path='/tmp/api_key_page.png')
print("Screenshot saved to /tmp/api_key_page.png")

harvester.close_browser()
HARVEST
    """)

elif choice == '3':
    print("""
╔════════════════════════════════════════════════════════════════╗
║              MANUAL HARVEST WITH GUIDANCE                      ║
╚════════════════════════════════════════════════════════════════╝

Follow these steps manually:

STEP 1: CREATE TEMPORARY EMAIL
--------------------------------
Visit: https://www.guerrillamail.com
Copy the email address shown

STEP 2: SIGNUP AT GROQ
-----------------------
Visit: https://console.groq.com
Click "Sign Up" or "Login"
Enter the temporary email
Create password: Password123!Aa
Submit the form

STEP 3: VERIFY EMAIL
--------------------
Go back to GuerrillaMail tab
Wait for email from Groq (usually < 1 minute)
Click the verification link in the email

STEP 4: GENERATE API KEY
-------------------------
Once logged in to Groq:
- Click on your profile/settings
- Navigate to "API Keys"
- Click "Create API Key"
- Copy the key (starts with gsk_)

STEP 5: SAVE THE KEY
--------------------
Run this command with your key:
    """)
    
    print("""
echo 'YOUR_KEY_HERE' > /tmp/harvested_groq_key.txt

Then run:
python3 << 'SAVE'
import re
from pathlib import Path

# Read the key
key = Path('/tmp/harvested_groq_key.txt').read_text().strip()

if key.startswith('gsk_'):
    # Update config
    config = Path('/app/config/lucifera.conf')
    content = config.read_text()
    content = re.sub(r'groq_api_key = .*', f'groq_api_key = {key}', content)
    config.write_text(content)
    print(f"✓ Saved key to config: {key[:20]}...")
    print("✓ Restart backend to use new key")
else:
    print("✗ Invalid key format")
SAVE
    """)

else:
    print("\nInvalid choice. Run the script again.")

print("\n" + "="*70)
print("For questions, see: /app/API_HARVESTING_DOCUMENTATION.md")
print("="*70)
