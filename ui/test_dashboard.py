#!/usr/bin/env python3
"""Test wrapper to catch crash"""
import sys
import traceback

try:
    from dashboard_streamlined import main
    main()
except Exception as e:
    print(f"\n\n====== CRASH DETECTED ======")
    print(f"ERROR: {e}")
    print("\n====== FULL TRACEBACK ======")
    traceback.print_exc()
    print("============================")
    input("\nPress Enter to exit...")
