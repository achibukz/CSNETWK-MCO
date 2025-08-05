#!/usr/bin/env python3
"""
Check what user IDs Alice and Bob are using
"""

def check_user_ids():
    """Check the user IDs being used"""
    print("=== User ID Check ===")
    print("Based on your setup:")
    print("Alice should be: alice@192.168.50.230")
    print("Bob should be: bob@192.168.50.28")
    print()
    print("But the diagnostic shows both devices have IP: 192.168.50.230")
    print()
    print("This means:")
    print("1. Both devices are on the same machine (different ports), OR")
    print("2. Both devices are behind the same NAT/router")
    print()
    print("Solutions:")
    print("1. Use different ports for each device")
    print("2. Use USER_ID for self-detection instead of IP")
    print("3. Add process ID or session ID to differentiate")

def suggest_fix():
    """Suggest the best fix approach"""
    print("\n=== Recommended Fix ===")
    print("Since both devices have the same IP, we should:")
    print("1. Use USER_ID for self-detection")
    print("2. Or use different ports for Alice and Bob")
    print()
    print("Option 1: Different Ports")
    print("- Alice: python main.py --user-id alice@192.168.50.230 --display-name Alice --port 50999")
    print("- Bob: python main.py --user-id bob@192.168.50.230 --display-name Bob --port 51000")
    print()
    print("Option 2: USER_ID Self-Detection (modify code)")
    print("- Check USER_ID in messages instead of IP/port")

if __name__ == "__main__":
    check_user_ids()
    suggest_fix()
