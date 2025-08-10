#!/usr/bin/env python3
"""
Test the two fixes:
1. Posts work without followers (broadcast)
2. [SEND] logs only show in verbose mode
"""

import os
import sys
import time
import io
from contextlib import redirect_stdout

# Add the project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import LSNPClient

def test_posts_without_followers():
    """Test that posts work when user has no followers"""
    print("=== Testing Posts Without Followers ===")
    
    # Create a client with no followers
    client = LSNPClient("user@192.168.1.100", "Test User", 8600, verbose=False)
    
    # Start the network system
    client.start()
    time.sleep(0.5)
    
    # Verify no followers
    followers = client.msgSystem.get_followers_list()
    print(f"✓ Followers count: {len(followers)}")
    
    if len(followers) > 0:
        print("❌ Test setup failed - user should have no followers")
        return False
    
    # Capture output to check for broadcast behavior
    captured_output = []
    original_print = print
    
    def capture_print(*args, **kwargs):
        line = ' '.join(str(arg) for arg in args)
        captured_output.append(line)
        original_print(*args, **kwargs)
    
    import builtins
    builtins.print = capture_print
    
    try:
        # Send a post without followers
        print("Sending post without followers...")
        client.msgSystem.send_post("This is a test post without followers")
        
        time.sleep(0.5)
        
    finally:
        builtins.print = original_print
    
    # Check if the post was handled correctly
    broadcast_messages = [line for line in captured_output if "broadcasting to network" in line]
    stored_posts = client.msgSystem.get_all_posts()
    
    print(f"✓ Broadcast messages: {len(broadcast_messages)}")
    print(f"✓ Stored posts: {len(stored_posts)}")
    
    success = len(broadcast_messages) > 0 and len(stored_posts) > 0
    
    if success:
        print("✅ Posts work without followers (using broadcast)")
    else:
        print("❌ Posts don't work without followers")
    
    # Clean up
    client.networkSystem.stop_listener()
    
    return success

def test_send_logs_verbose_only():
    """Test that [SEND] logs only appear in verbose mode"""
    print("\n=== Testing [SEND] Logs in Verbose Mode ===")
    
    # Test with verbose=False
    print("Testing with verbose=False...")
    client_quiet = LSNPClient("user@192.168.1.101", "Quiet User", 8601, verbose=False)
    
    # Mock the network send to avoid actual network calls
    original_send = client_quiet.networkSystem.send_message
    sent_messages = []
    
    def mock_send(message, target_ip="255.255.255.255", target_port=50999):
        sent_messages.append((message, target_ip, target_port))
        # Call the actual send logic but capture output
        captured_output = []
        original_print = print
        
        def capture_print(*args, **kwargs):
            line = ' '.join(str(arg) for arg in args)
            captured_output.append(line)
            # Don't actually print during this test
        
        import builtins
        builtins.print = capture_print
        
        try:
            original_send(message, target_ip, target_port)
        finally:
            builtins.print = original_print
        
        return captured_output
    
    client_quiet.networkSystem.send_message = mock_send
    
    # Start and send a message
    client_quiet.start()
    time.sleep(0.2)
    
    output_quiet = client_quiet.networkSystem.send_message({"TYPE": "TEST", "CONTENT": "test"})
    
    # Test with verbose=True
    print("Testing with verbose=True...")
    client_verbose = LSNPClient("user@192.168.1.102", "Verbose User", 8602, verbose=True)
    client_verbose.networkSystem.send_message = mock_send
    
    client_verbose.start()
    time.sleep(0.2)
    
    output_verbose = client_verbose.networkSystem.send_message({"TYPE": "TEST", "CONTENT": "test"})
    
    # Check results
    quiet_send_logs = [line for line in output_quiet if "[SEND]" in line]
    verbose_send_logs = [line for line in output_verbose if "[SEND]" in line]
    
    print(f"✓ [SEND] logs in quiet mode: {len(quiet_send_logs)}")
    print(f"✓ [SEND] logs in verbose mode: {len(verbose_send_logs)}")
    
    success = len(quiet_send_logs) == 0 and len(verbose_send_logs) > 0
    
    if success:
        print("✅ [SEND] logs only appear in verbose mode")
    else:
        print("❌ [SEND] logs appearing incorrectly")
        if len(quiet_send_logs) > 0:
            print(f"   Problem: {len(quiet_send_logs)} [SEND] logs in quiet mode")
        if len(verbose_send_logs) == 0:
            print(f"   Problem: No [SEND] logs in verbose mode")
    
    # Clean up
    client_quiet.networkSystem.stop_listener()
    client_verbose.networkSystem.stop_listener()
    
    return success

def main():
    """Run both tests"""
    print("Testing both fixes...\n")
    
    test1_success = test_posts_without_followers()
    test2_success = test_send_logs_verbose_only()
    
    print(f"\n=== Test Results ===")
    
    if test1_success:
        print("✅ Fix 1: Posts work without followers")
    else:
        print("❌ Fix 1: Posts still don't work without followers")
    
    if test2_success:
        print("✅ Fix 2: [SEND] logs only show in verbose mode")
    else:
        print("❌ Fix 2: [SEND] logs still showing in non-verbose mode")
    
    if test1_success and test2_success:
        print("\n🎉 Both fixes are working correctly!")
        print("   📤 Posts now broadcast when you have no followers")
        print("   🤫 Network logs are quiet in non-verbose mode")
    else:
        print("\n⚠️  Some fixes need more work.")
    
    return test1_success and test2_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
