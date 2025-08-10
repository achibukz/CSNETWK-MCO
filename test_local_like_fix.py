#!/usr/bin/env python3
"""
Test local like tracking fix
"""

import os
import sys
import time

# Add the project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from msg_System import msgSystem
from network_System import networkSystem
from vars import *

def test_local_like_tracking():
    """Test that sending likes updates local like counts immediately"""
    print("=== Testing Local Like Tracking Fix ===")
    
    # Create Alice's system (the one sending likes)
    alice_net = networkSystem(8400, verbose=False)
    alice_msg = msgSystem(alice_net, None)
    alice_msg.user_id = "alice@192.168.50.230"
    
    # Create a post from Bob that Alice has in her feed
    bob_post = {
        "TYPE": "POST",
        "USER_ID": "bob@192.168.50.28", 
        "CONTENT": "This is Bob's test post",
        "TIMESTAMP": 1754861730,
        "MESSAGE_ID": "bob_post_123"
    }
    
    # Add Bob's post to Alice's stored posts (as if she received it)
    alice_msg.stored_posts.append(bob_post)
    
    # Add Bob to known peers
    alice_msg.known_peers["bob@192.168.50.28"] = {
        "display_name": "Bob",
        "status": "Online"
    }
    
    print("✓ Set up Alice's system with Bob's post")
    print(f"  Post: {bob_post['CONTENT']}")
    
    # Check initial like count (should be 0)
    initial_count = alice_msg.get_like_count("bob@192.168.50.28", 1754861730)
    print(f"✓ Initial like count: {initial_count}")
    
    # Simulate Alice sending a LIKE (without actually sending over network)
    print("\n--- Alice sends LIKE to Bob's post ---")
    
    # Mock the network send to avoid actual network calls
    original_send = alice_msg.send_message_with_ack
    def mock_send(message, target_user):
        print(f"  [MOCK] Would send LIKE message to {target_user}")
        # Don't actually send, just simulate the local tracking
    
    alice_msg.send_message_with_ack = mock_send
    
    # Alice likes Bob's post
    alice_msg.send_like("bob@192.168.50.28", 1754861730, "LIKE")
    
    # Check like count after sending LIKE
    like_count_after = alice_msg.get_like_count("bob@192.168.50.28", 1754861730)
    likers = alice_msg.get_post_likers("bob@192.168.50.28", 1754861730)
    
    print(f"✓ Like count after sending LIKE: {like_count_after}")
    print(f"✓ Users who liked: {likers}")
    
    # Test UNLIKE
    print("\n--- Alice unlikes Bob's post ---")
    alice_msg.send_like("bob@192.168.50.28", 1754861730, "UNLIKE")
    
    unlike_count = alice_msg.get_like_count("bob@192.168.50.28", 1754861730)
    unlike_likers = alice_msg.get_post_likers("bob@192.168.50.28", 1754861730)
    
    print(f"✓ Like count after UNLIKE: {unlike_count}")
    print(f"✓ Users who liked: {unlike_likers}")
    
    # Verify results
    success = True
    
    if like_count_after == 1 and "alice@192.168.50.230" in likers:
        print("✅ Local LIKE tracking works correctly")
    else:
        print(f"❌ Local LIKE tracking failed. Expected count 1 with Alice as liker")
        success = False
    
    if unlike_count == 0 and "alice@192.168.50.230" not in unlike_likers:
        print("✅ Local UNLIKE tracking works correctly")
    else:
        print(f"❌ Local UNLIKE tracking failed. Expected count 0 with Alice removed")
        success = False
    
    # Restore original method
    alice_msg.send_message_with_ack = original_send
    
    return success

def main():
    """Run the local like tracking test"""
    print("Testing local like tracking fix...\n")
    
    success = test_local_like_tracking()
    
    print(f"\n=== Test Result ===")
    if success:
        print("🎉 Local like tracking fix works perfectly!")
        print("   ✅ Like counts update immediately when you like posts")
        print("   ✅ No need to wait for network round-trip")
        print("   ✅ 'Show all posts' will reflect your likes instantly")
        print("\nNow when you like a post, the count will update immediately!")
    else:
        print("⚠️  Local like tracking needs more work.")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
