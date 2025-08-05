#!/usr/bin/env python3
"""
Test script specifically for follow/unfollow relationship tracking
"""

import sys
import os
import time

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network_System import networkSystem
from msg_System import msgSystem
from vars import *

def test_followers_tracking():
    """Test that followers are properly tracked when receiving FOLLOW messages"""
    print("=== Testing Followers Tracking ===")
    
    # Create Alice's system
    alice_net = networkSystem(LSNP_PORT, verbose=True)
    alice_msg = msgSystem(alice_net)
    alice_net.set_msg_system(alice_msg)
    alice_msg.user_id = "alice@192.168.1.10"
    alice_msg.display_name = "Alice"
    alice_msg.status = "Testing followers"
    
    print("Initial state:")
    print(f"Alice following: {alice_msg.get_following_list()}")
    print(f"Alice followers: {alice_msg.get_followers_list()}")
    
    # Simulate receiving a FOLLOW message from Bob
    follow_message = {
        "TYPE": MSG_FOLLOW,
        "MESSAGE_ID": "test123",
        "FROM": "bob@192.168.1.11",
        "TO": "alice@192.168.1.10",
        "TIMESTAMP": int(time.time()),
        "TOKEN": f"bob@192.168.1.11|{int(time.time()) + 3600}|{SCOPE_FOLLOW}"
    }
    
    print("\nProcessing FOLLOW message from Bob...")
    alice_msg.handle_follow_message(follow_message)
    
    print("After receiving FOLLOW:")
    print(f"Alice following: {alice_msg.get_following_list()}")
    print(f"Alice followers: {alice_msg.get_followers_list()}")
    
    # Check if Bob is in followers list
    if "bob@192.168.1.11" in alice_msg.followers:
        print("✅ Bob correctly added to followers list")
        success = True
    else:
        print("❌ Bob NOT found in followers list")
        success = False
    
    # Test unfollow
    unfollow_message = {
        "TYPE": MSG_UNFOLLOW,
        "MESSAGE_ID": "test124",
        "FROM": "bob@192.168.1.11",
        "TO": "alice@192.168.1.10",
        "TIMESTAMP": int(time.time()),
        "TOKEN": f"bob@192.168.1.11|{int(time.time()) + 3600}|{SCOPE_FOLLOW}"
    }
    
    print("\nProcessing UNFOLLOW message from Bob...")
    alice_msg.handle_unfollow_message(unfollow_message)
    
    print("After receiving UNFOLLOW:")
    print(f"Alice following: {alice_msg.get_following_list()}")
    print(f"Alice followers: {alice_msg.get_followers_list()}")
    
    # Check if Bob is removed from followers list
    if "bob@192.168.1.11" not in alice_msg.followers:
        print("✅ Bob correctly removed from followers list")
        success = success and True
    else:
        print("❌ Bob still in followers list after unfollow")
        success = False
    
    return success

if __name__ == "__main__":
    if test_followers_tracking():
        print("\n🎉 Followers tracking test PASSED!")
    else:
        print("\n❌ Followers tracking test FAILED!")
