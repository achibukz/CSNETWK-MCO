#!/usr/bin/env python3
"""
Quick diagnostic to check Bob's message handling
"""

from network_System import networkSystem
from msg_System import msgSystem
from vars import *

def diagnose_bob_program():
    """Diagnose Bob's message handling in the main program"""
    print("=== Bob Program Diagnostic ===")
    
    # Check Bob's network system
    net = networkSystem(LSNP_PORT, verbose=True)
    msg = msgSystem(net)
    net.set_msg_system(msg)
    
    print(f"Bob's port: {net.port}")
    print(f"Bob's verbose mode: {net.verbose}")
    print(f"Bob's known clients: {net.known_clients}")
    
    # Check if Bob can create and parse messages
    test_message = {
        "TYPE": MSG_PROFILE,
        "USER_ID": "alice@192.168.50.230",
        "DISPLAY_NAME": "Alice",
        "STATUS": "Test status",
        "LISTEN_PORT": LSNP_PORT
    }
    
    print("\n--- Testing message conversion ---")
    lsnp_format = net._dict_to_lsnp(test_message)
    print(f"LSNP format:\n{lsnp_format}")
    
    parsed_back = net._lsnp_to_dict(lsnp_format)
    print(f"Parsed back: {parsed_back}")
    
    # Test profile handling
    print("\n--- Testing profile handling ---")
    msg.handle_profile_message(parsed_back)
    
    peers = msg.get_known_peers()
    print(f"Known peers after handling: {peers}")
    
    # Test message storage
    print("\n--- Testing message storage ---")
    test_post = {
        "TYPE": MSG_POST,
        "USER_ID": "alice@192.168.50.230",
        "CONTENT": "Test post from Alice",
        "MESSAGE_ID": "test123",
        "TOKEN": f"alice@192.168.50.230|{int(time.time()) + 3600}|broadcast",
        "TIMESTAMP": int(time.time())
    }
    
    msg.handle_post_message(test_post)
    posts = msg.get_all_posts()
    print(f"Stored posts: {len(posts)} posts")
    for post in posts:
        print(f"  - {post.get('USER_ID')}: {post.get('CONTENT')}")

if __name__ == "__main__":
    import time
    diagnose_bob_program()
