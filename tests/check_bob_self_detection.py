#!/usr/bin/env python3
"""
Quick fix for Bob's device - run this to see what's happening
"""

import socket
from vars import *

def get_bob_ip():
    """Get Bob's actual IP address"""
    try:
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.connect(("8.8.8.8", 80))
        bob_ip = temp_socket.getsockname()[0]
        temp_socket.close()
        return bob_ip
    except:
        return "Unknown"

def check_self_detection():
    """Check if Bob's self-detection is working correctly"""
    bob_ip = get_bob_ip()
    alice_ip = "192.168.50.230"
    
    print(f"Bob's IP: {bob_ip}")
    print(f"Alice's IP: {alice_ip}")
    print(f"LSNP Port: {LSNP_PORT}")
    
    # Simulate what happens when Bob receives Alice's message
    print("\n--- Simulating Alice's message to Bob ---")
    
    # This is what Bob sees when Alice sends a message
    sender_addr = (alice_ip, 54321)  # Alice's ephemeral port
    alice_listen_port = LSNP_PORT    # Alice's actual listening port
    
    print(f"Message from: {sender_addr}")
    print(f"Alice's LISTEN_PORT: {alice_listen_port}")
    
    # Check Bob's self-detection logic
    is_self_old = (sender_addr[0] == "127.0.0.1" and alice_listen_port == LSNP_PORT)
    is_self_new = (sender_addr[0] == bob_ip and alice_listen_port == LSNP_PORT) or \
                  (sender_addr[0] == "127.0.0.1" and alice_listen_port == LSNP_PORT)
    
    print(f"\nOld self-detection (127.0.0.1 only): {is_self_old}")
    print(f"New self-detection (with local IP): {is_self_new}")
    
    if is_self_new:
        print("❌ PROBLEM: Bob thinks Alice's message is from himself!")
        print("   This means Bob is rejecting Alice's messages")
    else:
        print("✅ Self-detection looks OK")
    
    print(f"\nBob should accept messages from {alice_ip}:{alice_listen_port}")

if __name__ == "__main__":
    check_self_detection()
