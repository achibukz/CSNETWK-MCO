#!/usr/bin/env python3
"""
Test like counting functionality
"""

import os
import sys
import time

# Add the project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from msg_System import msgSystem
from network_System import networkSystem
from vars import *

def test_like_counting():
    """Test that like counts are tracked correctly"""
    print("=== Testing Like Counting ===")
    
    # Create test system
    net_system = networkSystem(8200, verbose=False)
    msg_system = msgSystem(net_system, None)
    msg_system.user_id = "bob@192.168.50.28"
    
    # Create a mock post
    test_post = {
        "TYPE": MSG_POST,
        "USER_ID": "bob@192.168.50.28",
        "CONTENT": "This is a test post",
        "TIMESTAMP": 1234567890,
        "MESSAGE_ID": "test_post_123"
    }
    
    # Add the post to storage
    msg_system.stored_posts.append(test_post)
    
    print("✓ Created test post")
    print(f"  Post: {test_post['CONTENT']}")
    print(f"  Timestamp: {test_post['TIMESTAMP']}")
    
    # Test initial like count (should be 0)
    initial_count = msg_system.get_like_count("bob@192.168.50.28", 1234567890)
    print(f"✓ Initial like count: {initial_count}")
    
    # Simulate LIKE messages from different users
    users = [
        "alice@192.168.50.230",
        "charlie@192.168.50.100", 
        "diana@192.168.50.150"
    ]
    
    print("\n--- Simulating LIKE messages ---")
    for i, user in enumerate(users, 1):
        like_message = {
            "TYPE": MSG_LIKE,
            "MESSAGE_ID": f"like_msg_{i}",
            "FROM": user,
            "TO": "bob@192.168.50.28",
            "ACTION": "LIKE",
            "POST_TIMESTAMP": 1234567890,
            "TIMESTAMP": int(time.time()) + i
        }
        
        print(f"  Sending LIKE from {user}")
        msg_system.handle_like_message(like_message)
        
        # Check like count after each like
        count = msg_system.get_like_count("bob@192.168.50.28", 1234567890)
        print(f"    Like count now: {count}")
    
    # Test UNLIKE functionality
    print("\n--- Testing UNLIKE ---")
    unlike_message = {
        "TYPE": MSG_LIKE,
        "MESSAGE_ID": "unlike_msg_1",
        "FROM": "alice@192.168.50.230",
        "TO": "bob@192.168.50.28", 
        "ACTION": "UNLIKE",
        "POST_TIMESTAMP": 1234567890,
        "TIMESTAMP": int(time.time()) + 10
    }
    
    print("  Alice unlikes the post")
    msg_system.handle_like_message(unlike_message)
    
    final_count = msg_system.get_like_count("bob@192.168.50.28", 1234567890)
    likers = msg_system.get_post_likers("bob@192.168.50.28", 1234567890)
    
    print(f"✓ Final like count: {final_count}")
    print(f"✓ Users who liked: {likers}")
    
    # Verify results
    success = True
    
    if final_count == 2:  # 3 likes - 1 unlike = 2
        print("✅ Like counting works correctly")
    else:
        print(f"❌ Like counting failed. Expected 2, got {final_count}")
        success = False
    
    if len(likers) == 2 and "alice@192.168.50.230" not in likers:
        print("✅ UNLIKE functionality works correctly")
    else:
        print(f"❌ UNLIKE functionality failed. Expected Alice to be removed from likers")
        success = False
    
    if "charlie@192.168.50.100" in likers and "diana@192.168.50.150" in likers:
        print("✅ Like tracking maintains correct user list")
    else:
        print(f"❌ Like tracking failed to maintain correct user list")
        success = False
    
    return success

def main():
    """Run like counting tests"""
    print("Testing like counting functionality...\n")
    
    success = test_like_counting()
    
    print(f"\n=== Test Result ===")
    if success:
        print("🎉 Like counting functionality works perfectly!")
        print("   ✅ Posts show accurate like counts")
        print("   ✅ LIKE and UNLIKE actions tracked correctly")
        print("   ✅ Individual likers are tracked")
        print("\nNow when you 'Show all posts', you'll see like counts for each post!")
    else:
        print("⚠️  Like counting needs more work.")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
