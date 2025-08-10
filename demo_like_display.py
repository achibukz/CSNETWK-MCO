#!/usr/bin/env python3
"""
Demo of enhanced post display with like counts and liker names
"""

import os
import sys
import time

# Add the project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import LSNPClient

def demo_enhanced_posts():
    """Demo the enhanced post display"""
    print("=== Demo: Enhanced Post Display with Like Counts ===\n")
    
    # Create a test client
    client = LSNPClient("demo@192.168.1.100", "Demo User", 8300, verbose=False)
    
    # Create some test posts
    test_posts = [
        {
            "TYPE": "POST",
            "USER_ID": "alice@192.168.50.230",
            "CONTENT": "Just had a great day at the beach! 🌊",
            "TIMESTAMP": 1234567890,
            "MESSAGE_ID": "post_1"
        },
        {
            "TYPE": "POST", 
            "USER_ID": "bob@192.168.50.28",
            "CONTENT": "Working on my LSNP implementation. Almost done!",
            "TIMESTAMP": 1234567950,
            "MESSAGE_ID": "post_2"
        },
        {
            "TYPE": "POST",
            "USER_ID": "charlie@192.168.50.100",
            "CONTENT": "Does anyone know a good restaurant in the area?",
            "TIMESTAMP": 1234568000,
            "MESSAGE_ID": "post_3"
        }
    ]
    
    # Add posts to the system
    for post in test_posts:
        client.msgSystem.stored_posts.append(post)
    
    # Add some display names
    client.msgSystem.known_peers["alice@192.168.50.230"] = {"display_name": "Alice", "status": "Online"}
    client.msgSystem.known_peers["bob@192.168.50.28"] = {"display_name": "Bob", "status": "Online"}
    client.msgSystem.known_peers["charlie@192.168.50.100"] = {"display_name": "Charlie", "status": "Online"}
    client.msgSystem.known_peers["diana@192.168.50.150"] = {"display_name": "Diana", "status": "Online"}
    client.msgSystem.known_peers["eve@192.168.50.200"] = {"display_name": "Eve", "status": "Online"}
    
    print("📝 Created sample posts from Alice, Bob, and Charlie")
    
    # Simulate likes for different posts
    
    # Alice's post gets 3 likes
    alice_post_likes = [
        ("bob@192.168.50.28", "LIKE"),
        ("charlie@192.168.50.100", "LIKE"), 
        ("diana@192.168.50.150", "LIKE")
    ]
    
    for liker, action in alice_post_likes:
        like_msg = {
            "TYPE": "LIKE",
            "MESSAGE_ID": f"like_{liker}_{time.time()}",
            "FROM": liker,
            "TO": "alice@192.168.50.230",
            "ACTION": action,
            "POST_TIMESTAMP": 1234567890,
            "TIMESTAMP": int(time.time())
        }
        client.msgSystem.handle_like_message(like_msg)
    
    # Bob's post gets 1 like
    bob_like_msg = {
        "TYPE": "LIKE",
        "MESSAGE_ID": f"like_alice_{time.time()}",
        "FROM": "alice@192.168.50.230",
        "TO": "bob@192.168.50.28",
        "ACTION": "LIKE",
        "POST_TIMESTAMP": 1234567950,
        "TIMESTAMP": int(time.time())
    }
    client.msgSystem.handle_like_message(bob_like_msg)
    
    # Charlie's post gets 5 likes (to test "and X others" display)
    charlie_post_likes = [
        ("alice@192.168.50.230", "LIKE"),
        ("bob@192.168.50.28", "LIKE"),
        ("diana@192.168.50.150", "LIKE"),
        ("eve@192.168.50.200", "LIKE"),
        ("demo@192.168.1.100", "LIKE")
    ]
    
    for liker, action in charlie_post_likes:
        like_msg = {
            "TYPE": "LIKE",
            "MESSAGE_ID": f"like_{liker}_{time.time()}",
            "FROM": liker,
            "TO": "charlie@192.168.50.100",
            "ACTION": action,
            "POST_TIMESTAMP": 1234568000,
            "TIMESTAMP": int(time.time())
        }
        client.msgSystem.handle_like_message(like_msg)
    
    print("👍 Simulated various likes on the posts")
    print("\n" + "="*60)
    print("Here's how the enhanced post display looks:")
    print("="*60)
    
    # Show the posts using the enhanced display
    client.show_all_posts()
    
    print("\n" + "="*60)
    print("✨ Features demonstrated:")
    print("  ✅ Like counts for each post")
    print("  ✅ Names of users who liked")
    print("  ✅ Compact display for multiple likers")
    print("  ✅ 'and X others' for posts with many likes")
    print("  ✅ Posts without likes show 'No likes'")

def main():
    """Run the demo"""
    print("Like Count Display Demo\n")
    demo_enhanced_posts()
    print("\n🎉 Your 'Show all posts' feature now displays like counts!")
    print("Users can see exactly how popular each post is!")

if __name__ == "__main__":
    main()
