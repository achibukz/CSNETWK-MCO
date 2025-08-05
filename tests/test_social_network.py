#!/usr/bin/env python3
"""
Interactive social networking test for Milestone #2
Simulates a complete follow/unfollow social scenario
"""

import sys
import os
import time
import threading

# Add the parent directory to the path to import our modules  
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network_System import networkSystem
from msg_System import msgSystem
from vars import *

class SocialTestUser:
    """Simulates a social network user for testing"""
    
    def __init__(self, user_id, display_name, port_offset=0):
        self.user_id = user_id
        self.display_name = display_name
        self.port = LSNP_PORT + port_offset
        
        self.net = networkSystem(self.port, verbose=True)
        self.msg = msgSystem(self.net)
        self.net.set_msg_system(self.msg)
        
        # Set user details
        self.msg.user_id = user_id
        self.msg.display_name = display_name
        self.msg.status = "Active in social test"
        
        print(f"Created test user: {display_name} ({user_id}) on port {self.port}")
    
    def start_networking(self):
        """Start the networking system"""
        self.net.start_listener()
        time.sleep(0.5)  # Brief delay for startup
        
    def stop_networking(self):
        """Stop the networking system"""
        # Network system runs in daemon threads, will stop when main exits
        pass
        
    def follow_user(self, target_user_id):
        """Follow another user"""
        print(f"\n{self.display_name} follows {target_user_id}")
        self.msg.send_follow(target_user_id)
        time.sleep(0.2)
        
    def unfollow_user(self, target_user_id):
        """Unfollow another user"""
        print(f"\n{self.display_name} unfollows {target_user_id}")
        self.msg.send_unfollow(target_user_id)
        time.sleep(0.2)
        
    def post_message(self, content):
        """Post a message"""
        print(f"\n{self.display_name} posts: '{content}'")
        self.msg.send_post(content)
        time.sleep(0.2)
        
    def show_social_info(self):
        """Display social networking information"""
        print(f"\n=== {self.display_name}'s Social Info ===")
        print(f"Following: {self.msg.get_following_list()}")
        print(f"Followers: {self.msg.get_followers_list()}")
        print(f"Posts received: {len(self.msg.stored_posts)}")
        
        if self.msg.stored_posts:
            print("Recent posts:")
            for post in list(self.msg.stored_posts)[-3:]:  # Show last 3 posts
                print(f"  - {post}")

def run_social_network_test():
    """Run a comprehensive social networking test"""
    print("LSNP Social Network Test")
    print("========================")
    
    # Create test users
    alice = SocialTestUser("alice@192.168.1.10", "Alice", 0)
    bob = SocialTestUser("bob@192.168.1.11", "Bob", 1)
    charlie = SocialTestUser("charlie@192.168.1.12", "Charlie", 2)
    
    users = [alice, bob, charlie]
    
    try:
        # Start all networking
        print("\n--- Starting networking for all users ---")
        for user in users:
            user.start_networking()
        
        time.sleep(2)  # Allow systems to initialize
        
        # Test 1: User Discovery via PING
        print("\n--- Test 1: User Discovery ---")
        
        # Send PING messages manually for immediate testing
        for user in users:
            ping_message = {
                "TYPE": MSG_PING,
                "USER_ID": user.user_id,
                "BROADCAST": True
            }
            user.net.send_message(ping_message)
            
        time.sleep(3)  # Allow discovery to complete
        
        # Test 2: Following relationships
        print("\n--- Test 2: Following Relationships ---")
        alice.follow_user("bob@192.168.1.11")
        alice.follow_user("charlie@192.168.1.12")
        bob.follow_user("alice@192.168.1.10")
        
        time.sleep(2)  # Allow follow messages to process
        
        # Show initial social state
        for user in users:
            user.show_social_info()
        
        # Test 3: Post broadcasting and filtering
        print("\n--- Test 3: Post Broadcasting and Filtering ---")
        bob.post_message("Hello from Bob! This should reach Alice.")
        charlie.post_message("Hello from Charlie! This should reach Alice.")
        alice.post_message("Hello from Alice! This should reach Bob.")
        
        time.sleep(3)  # Allow posts to propagate
        
        # Show posts received by each user
        print("\n--- Posts Received by Each User ---")
        for user in users:
            user.show_social_info()
        
        # Test 4: Unfollow functionality
        print("\n--- Test 4: Unfollow Functionality ---")
        alice.unfollow_user("charlie@192.168.1.12")
        
        time.sleep(2)
        
        # Post again to test filtering after unfollow
        charlie.post_message("Second message from Charlie - Alice shouldn't see this")
        bob.post_message("Second message from Bob - Alice should see this")
        
        time.sleep(3)
        
        # Final social state
        print("\n--- Final Social State ---")
        for user in users:
            user.show_social_info()
        
        # Validate test results
        print("\n--- Test Results Validation ---")
        
        # Check if Alice follows Bob but not Charlie
        alice_following = alice.msg.get_following_list()
        if "bob@192.168.1.11" in alice_following and "charlie@192.168.1.12" not in alice_following:
            print("✅ Follow/Unfollow working correctly")
        else:
            print("❌ Follow/Unfollow not working correctly")
        
        # Check if Alice received Bob's posts but not Charlie's second post
        alice_posts = [post for post in alice.msg.stored_posts]
        bob_posts_count = sum(1 for post in alice_posts if "bob@192.168.1.11" in str(post))
        charlie_posts_count = sum(1 for post in alice_posts if "charlie@192.168.1.12" in str(post))
        
        print(f"Alice received {bob_posts_count} posts from Bob, {charlie_posts_count} posts from Charlie")
        print(f"Expected: Bob >= 1, Charlie <= 1 (only first post before unfollow)")
        
        # Charlie should have only 1 post (the first one) since Alice unfollowed before the second
        if bob_posts_count >= 1 and charlie_posts_count <= 1:
            print("✅ Post filtering by following relationship working correctly")
        else:
            print("❌ Post filtering not working correctly")
        
        print("\n🎉 Social network test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up
        print("\n--- Stopping all networking ---")
        for user in users:
            try:
                user.stop_networking()
            except:
                pass

if __name__ == "__main__":
    run_social_network_test()
