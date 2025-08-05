#!/usr/bin/env python3
"""
Debug script for Bob's device to diagnose message reception issues
"""

import socket
import threading
import time
from vars import *

def debug_bob_reception():
    """Debug Bob's message reception capabilities"""
    print("=== Bob's Reception Debug ===")
    
    # Get Bob's IP
    try:
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.connect(("8.8.8.8", 80))
        bob_ip = temp_socket.getsockname()[0]
        temp_socket.close()
        print(f"Bob's IP: {bob_ip}")
    except Exception as e:
        print(f"Could not get Bob's IP: {e}")
        return
    
    # Test socket binding
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        test_socket.bind(('0.0.0.0', LSNP_PORT))
        print(f"✓ Successfully bound to 0.0.0.0:{LSNP_PORT}")
        
        # Listen for messages for 30 seconds
        print("Listening for messages for 30 seconds...")
        test_socket.settimeout(1.0)  # 1 second timeout
        
        start_time = time.time()
        received_count = 0
        
        while time.time() - start_time < 30:
            try:
                data, addr = test_socket.recvfrom(4096)
                received_count += 1
                message = data.decode()
                print(f"[{received_count}] RECEIVED from {addr}:")
                print(f"    Raw: {repr(message)}")
                print(f"    Decoded: {message}")
                print("    ---")
            except socket.timeout:
                print(".", end="", flush=True)
            except Exception as e:
                print(f"\nError receiving: {e}")
        
        print(f"\nTotal messages received: {received_count}")
        test_socket.close()
        
    except Exception as e:
        print(f"✗ Failed to bind to port {LSNP_PORT}: {e}")
        print("This could mean:")
        print("- Port is already in use (Bob's main program running?)")
        print("- Permission denied")
        print("- Firewall blocking")

def test_send_to_alice():
    """Test sending a message to Alice"""
    print("\n=== Testing Send to Alice ===")
    alice_ip = "192.168.50.230"
    
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_message = f"TYPE: HELLO\nDATA: Debug test from Bob\nLISTEN_PORT: {LSNP_PORT}\n\n"
        
        test_socket.sendto(test_message.encode(), (alice_ip, LSNP_PORT))
        print(f"✓ Sent test message to {alice_ip}:{LSNP_PORT}")
        test_socket.close()
        
    except Exception as e:
        print(f"✗ Failed to send to Alice: {e}")

def check_firewall():
    """Check basic network connectivity"""
    print("\n=== Network Connectivity Check ===")
    alice_ip = "192.168.50.230"
    
    # Test ping-like connectivity using UDP
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_socket.settimeout(2.0)
        
        # Try to connect (won't actually connect with UDP, but tests routing)
        test_socket.connect((alice_ip, LSNP_PORT))
        print(f"✓ Network routing to {alice_ip} appears OK")
        test_socket.close()
        
    except Exception as e:
        print(f"✗ Network connectivity issue: {e}")
        print("Suggestions:")
        print("- Check if both devices are on same network")
        print("- Check firewall settings")
        print("- Ensure Alice's device is running")

if __name__ == "__main__":
    print("Bob's LSNP Debug Tool")
    print("====================")
    print("This tool will help diagnose why Bob isn't receiving Alice's messages.")
    print()
    
    # Make sure Bob's main program isn't running
    print("⚠️  IMPORTANT: Stop Bob's main LSNP program before running this!")
    print("   This debug tool needs to bind to the same port.")
    print()
    
    input("Press Enter when Bob's main program is stopped...")
    
    debug_bob_reception()
    test_send_to_alice()
    check_firewall()
    
    print("\n=== Recommendations ===")
    print("1. If no messages received: Check Alice is broadcasting")
    print("2. If send failed: Check network connectivity")
    print("3. If bind failed: Stop Bob's main program first")
    print("4. Check Windows Firewall on Bob's device")
