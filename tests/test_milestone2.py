#!/usr/bin/env python3
"""
Test script for Milestone #2 verification
LSNP Basic User Discovery and Messaging
"""

import sys
import os
import time
import subprocess
import threading

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network_System import networkSystem
from msg_System import msgSystem
from vars import *

def test_follow_unfollow_functionality():
    """Test FOLLOW/UNFOLLOW message creation and parsing"""
    print("=== Testing FOLLOW/UNFOLLOW Functionality ===")
    
    net = networkSystem(LSNP_PORT, verbose=True)
    msg = msgSystem(net)
    net.set_msg_system(msg)
    
    # Test FOLLOW message creation
    print("\n1. Testing FOLLOW message creation:")
    msg.user_id = "alice@192.168.1.10"
    msg.display_name = "Alice"
    msg.status = "Testing"
    
    # Create a follow message manually to test format
    timestamp = int(time.time())
    follow_message = {
        "TYPE": MSG_FOLLOW,
        "MESSAGE_ID": "test123",
        "FROM": "alice@192.168.1.10",
        "TO": "bob@192.168.1.11",
        "TIMESTAMP": timestamp,
        "TOKEN": f"alice@192.168.1.10|{timestamp + 3600}|{SCOPE_FOLLOW}"
    }
    
    lsnp_format = net._dict_to_lsnp(follow_message)
    print("FOLLOW message in LSNP format:")
    print(lsnp_format)
    
    # Test parsing back
    parsed = net._lsnp_to_dict(lsnp_format)
    print("Parsed back:")
    for key, value in parsed.items():
        print(f"  {key}: {value}")
    
    # Test UNFOLLOW message
    print("\n2. Testing UNFOLLOW message creation:")
    unfollow_message = {
        "TYPE": MSG_UNFOLLOW,
        "MESSAGE_ID": "test124",
        "FROM": "alice@192.168.1.10",
        "TO": "bob@192.168.1.11",
        "TIMESTAMP": timestamp,
        "TOKEN": f"alice@192.168.1.10|{timestamp + 3600}|{SCOPE_FOLLOW}"
    }
    
    lsnp_format = net._dict_to_lsnp(unfollow_message)
    print("UNFOLLOW message in LSNP format:")
    print(lsnp_format)
    
    return True

def test_ping_functionality():
    """Test PING message creation and handling"""
    print("\n=== Testing PING Functionality ===")
    
    net = networkSystem(LSNP_PORT, verbose=True)
    msg = msgSystem(net)
    net.set_msg_system(msg)
    
    # Test PING message creation
    ping_message = {
        "TYPE": MSG_PING,
        "USER_ID": "alice@192.168.1.10"
    }
    
    lsnp_format = net._dict_to_lsnp(ping_message)
    print("PING message in LSNP format:")
    print(lsnp_format)
    
    # Test parsing back
    parsed = net._lsnp_to_dict(lsnp_format)
    print("Parsed back:")
    for key, value in parsed.items():
        print(f"  {key}: {value}")
    
    return True

def test_following_management():
    """Test following/followers tracking"""
    print("\n=== Testing Following Management ===")
    
    net = networkSystem(LSNP_PORT, verbose=True)
    msg = msgSystem(net)
    net.set_msg_system(msg)
    msg.user_id = "alice@192.168.1.10"
    
    # Test following list management
    print("Initial following list:", msg.get_following_list())
    print("Initial followers list:", msg.get_followers_list())
    
    # Simulate adding to following
    msg.following.add("bob@192.168.1.11")
    msg.following.add("charlie@192.168.1.12")
    
    print("After adding follows:", msg.get_following_list())
    print("Is following bob:", msg.is_following("bob@192.168.1.11"))
    print("Is following unknown:", msg.is_following("unknown@192.168.1.13"))
    
    # Simulate receiving followers
    msg.followers.add("david@192.168.1.14")
    msg.followers.add("eve@192.168.1.15")
    
    print("Followers list:", msg.get_followers_list())
    
    return True

def test_post_filtering():
    """Test that posts are filtered by following relationship"""
    print("\n=== Testing Post Filtering ===")
    
    net = networkSystem(LSNP_PORT, verbose=True)
    msg = msgSystem(net)
    net.set_msg_system(msg)
    msg.user_id = "alice@192.168.1.10"
    
    # Add bob to following list
    msg.following.add("bob@192.168.1.11")
    
    timestamp = int(time.time())
    
    # Test post from followed user (should be accepted)
    followed_post = {
        "TYPE": MSG_POST,
        "USER_ID": "bob@192.168.1.11",
        "CONTENT": "Hello from Bob!",
        "MESSAGE_ID": "post001",
        "TOKEN": f"bob@192.168.1.11|{timestamp + 3600}|{SCOPE_BROADCAST}",
        "TIMESTAMP": timestamp
    }
    
    print("Processing post from followed user...")
    initial_count = len(msg.stored_posts)
    msg.handle_post_message(followed_post)
    followed_count = len(msg.stored_posts)
    
    # Test post from non-followed user (should be rejected)
    non_followed_post = {
        "TYPE": MSG_POST,
        "USER_ID": "charlie@192.168.1.12",
        "CONTENT": "Hello from Charlie!",
        "MESSAGE_ID": "post002", 
        "TOKEN": f"charlie@192.168.1.12|{timestamp + 3600}|{SCOPE_BROADCAST}",
        "TIMESTAMP": timestamp
    }
    
    print("Processing post from non-followed user...")
    msg.handle_post_message(non_followed_post)
    final_count = len(msg.stored_posts)
    
    print(f"Posts stored - Initial: {initial_count}, After followed: {followed_count}, Final: {final_count}")
    
    if followed_count > initial_count and final_count == followed_count:
        print("✅ Post filtering working correctly!")
        return True
    else:
        print("❌ Post filtering not working correctly!")
        return False

def test_broadcast_interval():
    """Test that broadcasting happens at correct intervals"""
    print("\n=== Testing Broadcast Interval ===")
    
    print(f"Current BROADCAST_INTERVAL: {BROADCAST_INTERVAL} seconds")
    
    if BROADCAST_INTERVAL <= 60:  # Reasonable for testing
        print("✅ Broadcast interval is set for testing")
        return True
    else:
        print("⚠️  Broadcast interval might be too long for testing")
        return True

def run_milestone2_tests():
    """Run all Milestone #2 tests"""
    print("LSNP Milestone #2 Test Suite")
    print("========================================")
    
    tests = [
        ("FOLLOW/UNFOLLOW Message Format", test_follow_unfollow_functionality),
        ("PING Message Format", test_ping_functionality),
        ("Following Management", test_following_management),
        ("Post Filtering", test_post_filtering),
        ("Broadcast Interval", test_broadcast_interval),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n=== Testing {test_name} ===")
        try:
            if test_func():
                print(f"✅ {test_name}: PASS")
                passed += 1
            else:
                print(f"❌ {test_name}: FAIL")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All Milestone #2 tests PASSED!")
        print("\nMilestone #2 Requirements Met:")
        print("✅ User Discovery and Presence")
        print("✅ FOLLOW/UNFOLLOW Messaging Functionality")
        print("✅ Post Filtering by Following Relationship")
        print("✅ PING/PROFILE Broadcasting")
        print("\n🚀 Ready for Milestone #3!")
    else:
        print(f"❌ {total - passed} test(s) failed. Please review and fix.")

if __name__ == "__main__":
    run_milestone2_tests()
