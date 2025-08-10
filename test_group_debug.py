#!/usr/bin/env python3
"""Test GROUP_CREATE message debugging."""

import time
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import LSNPClient

def test_group_create_debug():
    """Test GROUP_CREATE message with debug output."""
    print("=== GROUP_CREATE Debug Test ===")
    
    # Create Alice instance
    alice = LSNPClient("Alice@127.0.0.1:8001", "Alice", 8001, verbose=True)
    
    # Create Bob instance  
    bob = LSNPClient("Bob@127.0.0.1:8002", "Bob", 8002, verbose=True)
    
    # Start networking
    alice.start()
    bob.start()
    time.sleep(1)
    
    print("\n--- Alice creates group with Bob ---")
    group_name = "TestGroup"
    members = ["Alice@127.0.0.1:8001", "Bob@127.0.0.1:8002"]
    
    # Alice creates group
    alice.msgSystem.create_group(group_name, members)
    
    # Wait for message processing
    time.sleep(2)
    
    print(f"\n--- Alice's groups: {alice.msgSystem.groups}")
    print(f"--- Bob's groups: {bob.msgSystem.groups}")
    
    # Check if Bob received the group
    if group_name in bob.msgSystem.groups:
        print("✓ SUCCESS: Bob received the group")
    else:
        print("✗ FAILURE: Bob did not receive the group")
    
    # Cleanup
    alice.stop()
    bob.stop()
    time.sleep(1)

if __name__ == "__main__":
    test_group_create_debug()
