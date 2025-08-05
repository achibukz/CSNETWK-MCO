#!/usr/bin/env python3
"""
Test script for profile editing functionality
"""

import sys
import os
import time

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network_System import networkSystem
from msg_System import msgSystem
from vars import *

def test_profile_editing():
    """Test profile creation and editing functionality"""
    print("=== Testing Profile Editing ===")
    
    # Create a message system
    net = networkSystem(LSNP_PORT, verbose=True)
    msg = msgSystem(net)
    net.set_msg_system(msg)
    
    # Test initial profile creation
    print("\n1. Testing initial profile creation:")
    msg.create_profile("alice@192.168.1.10", "Alice", "Online and ready!")
    
    # Check if profile was stored
    if hasattr(msg, 'user_id') and hasattr(msg, 'display_name') and hasattr(msg, 'status'):
        print(f"✅ Profile created - User: {msg.user_id}, Name: {msg.display_name}, Status: {msg.status}")
    else:
        print("❌ Profile creation failed")
        return False
    
    # Test profile update
    print("\n2. Testing profile update:")
    msg.create_profile("alice@192.168.1.10", "Alice Smith", "Busy working on LSNP!")
    
    if msg.display_name == "Alice Smith" and msg.status == "Busy working on LSNP!":
        print(f"✅ Profile updated - Name: {msg.display_name}, Status: {msg.status}")
    else:
        print("❌ Profile update failed")
        return False
    
    # Test known_peers storage
    print("\n3. Testing known_peers storage:")
    if "alice@192.168.1.10" in msg.known_peers:
        peer_info = msg.known_peers["alice@192.168.1.10"]
        print(f"✅ Profile stored in known_peers: {peer_info}")
    else:
        print("❌ Profile not stored in known_peers")
        return False
    
    return True

if __name__ == "__main__":
    if test_profile_editing():
        print("\n🎉 Profile editing test PASSED!")
    else:
        print("\n❌ Profile editing test FAILED!")
