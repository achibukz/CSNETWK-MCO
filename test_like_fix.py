#!/usr/bin/env python3
"""
Test LIKE duplicate detection fix
"""

import os
import sys
import time

# Add the project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from msg_System import msgSystem
from network_System import networkSystem
from vars import *

def test_like_duplicate_detection():
    """Test that duplicate LIKE messages are properly filtered"""
    print("=== Testing LIKE Duplicate Detection ===")
    
    # Create test systems
    net_system = networkSystem(8090, verbose=False)
    msg_system = msgSystem(net_system, None)
    msg_system.user_id = "test_receiver"
    
    # Create a mock LIKE message
    like_message = {
        "TYPE": MSG_LIKE,
        "MESSAGE_ID": "test_like_123",
        "FROM": "alice@192.168.1.100",
        "TO": "test_receiver",
        "ACTION": "LIKE",
        "POST_TIMESTAMP": 1234567890,
        "TIMESTAMP": int(time.time()),
        "TOKEN": "alice@192.168.1.100|9999999999|broadcast"
    }
    
    print("Sending first LIKE message...")
    output_buffer = []
    
    # Capture print output
    original_print = print
    def capture_print(*args, **kwargs):
        output_buffer.append(' '.join(str(arg) for arg in args))
        original_print(*args, **kwargs)
    
    import builtins
    builtins.print = capture_print
    
    try:
        # Handle the message first time
        msg_system.handle_like_message(like_message)
        
        # Handle the same message again (should be ignored)
        print("Sending duplicate LIKE message...")
        msg_system.handle_like_message(like_message)
        
        # Handle the same message a third time (should be ignored)
        print("Sending another duplicate LIKE message...")
        msg_system.handle_like_message(like_message)
        
    finally:
        # Restore original print
        builtins.print = original_print
    
    # Check results
    like_notifications = [line for line in output_buffer if "[LIKE]" in line and "liked your post" in line]
    duplicate_detections = [line for line in output_buffer if "Ignoring duplicate LIKE" in line]
    
    print(f"\nResults:")
    print(f"  LIKE notifications: {len(like_notifications)}")
    print(f"  Duplicate detections: {len(duplicate_detections)}")
    
    if len(like_notifications) == 1:
        print("✅ LIKE notification shown only once")
    else:
        print(f"❌ LIKE notification shown {len(like_notifications)} times (should be 1)")
        
    if len(duplicate_detections) >= 2:
        print("✅ Duplicate LIKE messages detected and ignored")
    else:
        print(f"❌ Duplicate detection not working properly")
    
    return len(like_notifications) == 1 and len(duplicate_detections) >= 2

def main():
    """Run the test"""
    print("Testing LIKE duplicate detection fix...\n")
    
    success = test_like_duplicate_detection()
    
    print(f"\n=== Test Result ===")
    if success:
        print("✅ LIKE duplicate detection is working correctly!")
        print("   Users will now only see one notification per LIKE, even if the message is retried.")
    else:
        print("❌ LIKE duplicate detection needs more work.")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
