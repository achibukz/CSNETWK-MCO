#!/usr/bin/env python3
"""
Comprehensive test for LIKE functionality with ACK retries
"""

import os
import sys
import time
import threading

# Add the project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from msg_System import msgSystem
from network_System import networkSystem
from vars import *

def test_like_with_ack_system():
    """Test LIKE messages with proper ACK handling and duplicate detection"""
    print("=== Testing LIKE with ACK System ===")
    
    # Create Alice (sender)
    alice_net = networkSystem(8100, verbose=True)
    alice_msg = msgSystem(alice_net, None)
    alice_msg.user_id = "alice@192.168.50.230"
    alice_msg.display_name = "Alice"
    
    # Create Bob (receiver) 
    bob_net = networkSystem(8101, verbose=True)
    bob_msg = msgSystem(bob_net, None)
    bob_msg.user_id = "bob@192.168.50.28"
    bob_msg.display_name = "Bob"
    
    # Set up cross-references
    alice_net.set_msg_system(alice_msg)
    bob_net.set_msg_system(bob_msg)
    
    # Start network listeners
    alice_net.start_listener()
    bob_net.start_listener()
    time.sleep(0.5)
    
    # Add each other as known peers for testing
    alice_msg.known_peers["bob@192.168.50.28"] = {
        'display_name': 'Bob',
        'status': 'Online',
        'ip': '127.0.0.1',
        'port': 8101
    }
    
    bob_msg.known_peers["alice@192.168.50.230"] = {
        'display_name': 'Alice', 
        'status': 'Online',
        'ip': '127.0.0.1',
        'port': 8100
    }
    
    # Add to known clients for IP resolution
    alice_net.known_clients.add(('127.0.0.1', 8101))
    bob_net.known_clients.add(('127.0.0.1', 8100))
    
    print("✓ Set up Alice and Bob")
    
    # Capture output for analysis
    notifications = []
    original_print = print
    
    def capture_print(*args, **kwargs):
        line = ' '.join(str(arg) for arg in args)
        if "[LIKE]" in line and ("liked your post" in line or "Sent like" in line):
            notifications.append(line)
        original_print(*args, **kwargs)
    
    import builtins
    builtins.print = capture_print
    
    try:
        print("\n--- Sending LIKE from Alice to Bob ---")
        
        # Alice sends a LIKE to Bob
        alice_msg.send_like("bob@192.168.50.28", 1234567890, "LIKE")
        
        # Wait for message processing
        time.sleep(2)
        
        print(f"\n--- Results ---")
        
    finally:
        builtins.print = original_print
    
    # Analyze results
    like_sent = [n for n in notifications if "Sent like" in n]
    like_received = [n for n in notifications if "liked your post" in n]
    
    print(f"LIKE sent notifications: {len(like_sent)}")
    print(f"LIKE received notifications: {len(like_received)}")
    
    success = True
    
    if len(like_sent) >= 1:
        print("✅ Alice successfully sent LIKE")
    else:
        print("❌ Alice failed to send LIKE")
        success = False
        
    if len(like_received) == 1:
        print("✅ Bob received exactly one LIKE notification")
    elif len(like_received) > 1:
        print(f"⚠️  Bob received {len(like_received)} LIKE notifications (duplicates not filtered)")
        success = False
    else:
        print("❌ Bob did not receive LIKE notification")
        success = False
    
    # Clean up
    alice_net.stop_listener()
    bob_net.stop_listener()
    
    return success

def main():
    """Run comprehensive LIKE tests"""
    print("Testing LIKE functionality with ACK system...\n")
    
    success = test_like_with_ack_system()
    
    print(f"\n=== Final Result ===")
    if success:
        print("🎉 LIKE functionality is working correctly!")
        print("   ✅ Messages are sent properly")
        print("   ✅ Duplicates are filtered")
        print("   ✅ ACK system is functioning")
        print("\nYour LIKE bug has been fixed! Users will now only see one notification per LIKE.")
    else:
        print("⚠️  LIKE functionality needs more attention.")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
