#!/usr/bin/env python3
"""
Quick network test for multi-device LSNP discovery
"""

import socket
import time
from vars import *

def get_local_ip():
    """Get the actual local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def test_network_setup():
    """Test if devices can discover each other"""
    local_ip = get_local_ip()
    print(f"=== Network Test ===")
    print(f"Local IP: {local_ip}")
    print(f"LSNP Port: {LSNP_PORT}")
    
    # Test socket binding on all interfaces
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        test_socket.bind(('0.0.0.0', LSNP_PORT))
        print("✓ Can bind to 0.0.0.0 (all interfaces)")
        test_socket.close()
    except Exception as e:
        print(f"✗ Cannot bind to all interfaces: {e}")
        return False
    
    # Test broadcast capability
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        test_message = f"TYPE: HELLO\nDATA: Test from {local_ip}\nLISTEN_PORT: {LSNP_PORT}\n\n"
        test_socket.sendto(test_message.encode(), ("255.255.255.255", LSNP_PORT))
        print("✓ Broadcast message sent")
        test_socket.close()
        
        print("\nNow run the main LSNP program on both devices.")
        print("If they don't discover each other:")
        print("1. Check Windows Firewall (allow UDP port 50999)")
        print("2. Ensure both devices are on same network")
        print("3. Try temporarily disabling firewall")
        
        return True
    except Exception as e:
        print(f"✗ Broadcast failed: {e}")
        return False

if __name__ == "__main__":
    test_network_setup()
