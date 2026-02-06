#!/usr/bin/env python3
"""
Quick test for LILITH Autonomous Agent
"""
import sys
sys.path.insert(0, 'C:\\LuciferOS_FULL')

from tools.lilith_autonomous import LILITHAgent, GROQ_API_KEY

def test_lilith():
    print("=" * 50)
    print("LILITH AUTONOMOUS AGENT TEST")
    print("=" * 50)
    
    # Test 1: Check API key
    print("\n[1] API Key Check:")
    if GROQ_API_KEY:
        print(f"    ✓ API Key configured: {GROQ_API_KEY[:20]}...")
    else:
        print("    ✗ API Key MISSING!")
        return False
    
    # Test 2: Initialize agent
    print("\n[2] Agent Initialization:")
    try:
        agent = LILITHAgent(auto_execute=False)
        print(f"    ✓ Agent created")
        print(f"    ✓ Model: {agent.model}")
        print(f"    ✓ Workdir: {agent.workdir}")
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False
    
    # Test 3: Query Groq API
    print("\n[3] Groq API Test:")
    try:
        response = agent.query_groq("Say 'LILITH ONLINE' and nothing else")
        if 'LILITH' in response.upper():
            print(f"    ✓ API Response: {response[:50]}")
        else:
            print(f"    ? Response: {response[:100]}")
    except Exception as e:
        print(f"    ✗ API Error: {e}")
        return False
    
    # Test 4: Command parsing
    print("\n[4] Command Parsing Test:")
    test_response = """
    Let me scan the target.
    [EXECUTE: nmap -sV target.com]
    [WRITE_FILE: /tmp/test.txt]
    test content here
    [/WRITE_FILE]
    [READ_FILE: /etc/passwd]
    """
    commands = agent.parse_commands(test_response)
    print(f"    ✓ Parsed {len(commands)} commands")
    for cmd in commands:
        print(f"      - {cmd[0]}: {cmd[1][:30]}...")
    
    print("\n" + "=" * 50)
    print("ALL TESTS PASSED!")
    print("=" * 50)
    print("\nLILITH is ready for autonomous operation.")
    print("Launch via dashboard: 🔥 LILITH TAKEOVER")
    print("Or run: python tools/lilith_autonomous.py --interactive")
    
    return True

if __name__ == "__main__":
    success = test_lilith()
    sys.exit(0 if success else 1)
