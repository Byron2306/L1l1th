#!/usr/bin/env python3
"""Quick test of the LILITH-OpenClaw bridge flow"""
import requests
import re

LILITH_URL = "http://127.0.0.1:5000"

def test_flow():
    print("="*60)
    print("LILITH-OpenClaw Bridge Test")
    print("="*60)
    
    # 1. Check status
    print("\n[1] Checking LILITH status...")
    r = requests.get(f"{LILITH_URL}/status", timeout=5)
    print(f"    Status: {r.json()['status']}")
    print(f"    Model: {r.json()['model']}")
    
    # 2. Send a reconnaissance request
    print("\n[2] Sending recon request...")
    prompt = "I need to scan 192.168.1.100 for open ports and services. What command should I run?"
    
    r = requests.post(f"{LILITH_URL}/chat", json={"message": prompt}, timeout=120)
    response = r.json()['response']
    print(f"    Response received ({len(response)} chars)")
    
    # 3. Parse commands
    print("\n[3] Parsing for [EXECUTE:] commands...")
    pattern = r'\[EXECUTE:\s*(.+?)\]'
    commands = re.findall(pattern, response)
    
    if commands:
        print(f"    Found {len(commands)} command(s):")
        for i, cmd in enumerate(commands, 1):
            print(f"    {i}. {cmd}")
    else:
        print("    No [EXECUTE:] commands found in response")
        print(f"\n    Full response:\n    {response[:500]}...")
    
    print("\n[TEST COMPLETE]")
    return bool(commands)

if __name__ == "__main__":
    success = test_flow()
    exit(0 if success else 1)
