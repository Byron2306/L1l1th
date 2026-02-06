#!/usr/bin/env python3
"""Quick test for AI providers"""
import sys
sys.path.insert(0, '.')

from ai_providers import get_ai_manager

print("Testing AI Provider Fallback System...")
print("=" * 50)

m = get_ai_manager()

print("\nProvider Status:")
status = m.get_status()
for p in status['providers']:
    avail = "✓ Available" if p['is_available'] else "✗ Unavailable"
    print(f"  {p['name']}: {avail}")

print(f"\nActive: {status['active_count']}/{status['total_count']}")

print("\nSending test message...")
r = m.chat("Say 'LILITH ONLINE' in exactly 3 words")

if r['success']:
    print(f"\n✓ SUCCESS via {r['provider']} ({r['model']})")
    print(f"Response: {r['response'][:200]}")
else:
    print(f"\n✗ FAILED")
    print(r['response'])
