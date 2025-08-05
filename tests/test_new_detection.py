#!/usr/bin/env python3
"""
Test the new USER_ID based self-detection
"""

def test_new_self_detection():
    """Test the new USER_ID self-detection logic"""
    print("=== Testing New Self-Detection Logic ===")
    
    # Simulate Bob receiving Alice's message
    alice_message = {
        "TYPE": "PROFILE",
        "USER_ID": "alice@192.168.50.230",
        "DISPLAY_NAME": "Alice",
        "STATUS": "Online and ready!",
        "LISTEN_PORT": 50999
    }
    
    bob_user_id = "bob@192.168.50.28"
    alice_user_id = alice_message.get("USER_ID")
    
    print(f"Alice's USER_ID: {alice_user_id}")
    print(f"Bob's USER_ID: {bob_user_id}")
    
    # New self-detection logic
    is_self_new = (alice_user_id == bob_user_id)
    
    print(f"Is Alice's message from Bob (self)? {is_self_new}")
    
    if is_self_new:
        print("❌ Bob would ignore Alice's message")
    else:
        print("✅ Bob would accept Alice's message")
        print("✅ Bob should now see Alice's posts and profile!")

if __name__ == "__main__":
    test_new_self_detection()
