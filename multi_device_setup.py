#!/usr/bin/env python3
"""
Multi-Device Testing Guide and Helper Script
"""

import socket
import subprocess
import sys

def get_local_ip():
    """Get the local IP address of this device"""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        return "127.0.0.1"

def test_network_connectivity(target_ip, port=50999):
    """Test if we can reach another device"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(2)
            s.sendto(b"TEST", (target_ip, port))
            print(f"✅ Can send to {target_ip}:{port}")
            return True
    except Exception as e:
        print(f"❌ Cannot reach {target_ip}:{port} - {e}")
        return False

def main():
    print("=== LSNP Multi-Device Testing Helper ===")
    print()
    
    # Get local IP
    local_ip = get_local_ip()
    print(f"Your device IP: {local_ip}")
    print()
    
    print("=== Step-by-Step Testing Instructions ===")
    print()
    
    print("STEP 1: Network Setup")
    print("- Ensure both devices are on the same Wi-Fi network")
    print("- Configure firewall to allow UDP port 50999")
    print()
    
    print("STEP 2: Get IP Addresses")
    print("- Device 1 IP:", local_ip)
    target_ip = input("- Enter Device 2 IP address: ").strip()
    
    if target_ip:
        print(f"- Device 2 IP: {target_ip}")
        print()
        
        print("STEP 3: Test Network Connectivity")
        if test_network_connectivity(target_ip):
            print("✅ Network connectivity OK")
        else:
            print("❌ Network connectivity failed - check firewall and IP address")
            return
    
    print()
    print("STEP 4: Start LSNP Clients")
    print()
    print("=== Commands to Run ===")
    print()
    print(f"Device 1 ({local_ip}):")
    print(f"python main.py --user-id alice@{local_ip} --display-name Alice --port 50999 --verbose")
    print()
    
    if target_ip:
        print(f"Device 2 ({target_ip}):")
        print(f"python main.py --user-id bob@{target_ip} --display-name Bob --port 50999 --verbose")
    else:
        print("Device 2 (replace <DEVICE2_IP> with actual IP):")
        print("python main.py --user-id bob@<DEVICE2_IP> --display-name Bob --port 50999 --verbose")
    
    print()
    print("STEP 5: Test Communication")
    print("1. Both devices should show startup messages")
    print("2. Both should broadcast PROFILE messages")
    print("3. In Alice's menu, choose option 2 (Send HELLO)")
    print(f"   - Target IP: {target_ip if target_ip else '<DEVICE2_IP>'}")
    print("   - Target port: 50999")
    print("4. Bob should receive the HELLO message")
    print("5. Test POST messages (option 1) - both should see broadcasts")
    print("6. Test DMs (option 3) between devices")
    print()
    
    print("=== Expected Results ===")
    print("✅ Profile messages appear on both devices")
    print("✅ HELLO messages are received")
    print("✅ POST broadcasts are seen by both")
    print("✅ Direct messages work between devices")
    print("✅ Known peers list shows both users")

if __name__ == "__main__":
    main()
