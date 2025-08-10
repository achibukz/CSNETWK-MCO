#!/usr/bin/env python3
"""Simple GROUP_CREATE test."""

import time
import threading
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from msg_System import msgSystem
from network_System import networkSystem
from file_game import fileGameSystem

def test_simple_group():
    """Test GROUP_CREATE with direct method calls."""
    print("=== Simple GROUP_CREATE Test ===")
    
    # Create Alice 
    alice_net = networkSystem(8001, verbose=True)
    alice_fg = fileGameSystem(alice_net)
    alice_msg = msgSystem(alice_net, alice_fg)
    alice_net.set_msg_system(alice_msg)
    alice_net.set_file_game_system(alice_fg)
    alice_msg.user_id = "Alice@127.0.0.1:8001"
    alice_msg.display_name = "Alice"
    
    # Create Bob
    bob_net = networkSystem(8002, verbose=True)
    bob_fg = fileGameSystem(bob_net)
    bob_msg = msgSystem(bob_net, bob_fg)
    bob_net.set_msg_system(bob_msg)
    bob_net.set_file_game_system(bob_fg)
    bob_msg.user_id = "Bob@127.0.0.1:8002"
    bob_msg.display_name = "Bob"
    
    # Start network threads
    def start_alice():
        alice_net.network_thread()
    
    def start_bob():
        bob_net.network_thread()
    
    alice_thread = threading.Thread(target=start_alice)
    bob_thread = threading.Thread(target=start_bob)
    
    alice_thread.daemon = True
    bob_thread.daemon = True
    
    alice_thread.start()
    bob_thread.start()
    
    time.sleep(1)
    print("Networks started...")
    
    # Alice creates group
    group_name = "TestGroup"
    members = ["Alice@127.0.0.1:8001", "Bob@127.0.0.1:8002"]
    
    print(f"Alice creating group '{group_name}' with members: {members}")
    alice_msg.create_group(group_name, members)
    
    # Wait for processing
    time.sleep(3)
    
    print(f"\n--- Results ---")
    print(f"Alice groups: {alice_msg.groups}")
    print(f"Bob groups: {bob_msg.groups}")
    
    if group_name in bob_msg.groups:
        print("✓ SUCCESS: Bob received the group")
    else:
        print("✗ FAILURE: Bob did not receive the group")
    
    print("Test complete.")

if __name__ == "__main__":
    test_simple_group()
