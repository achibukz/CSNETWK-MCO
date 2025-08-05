#!/usr/bin/env python3
"""
Multi-device test script for LSNP
Tests communication between two instances
"""

import subprocess
import sys
import time
import threading

def start_client(user_id, display_name, port):
    """Start an LSNP client instance"""
    cmd = [
        sys.executable, "main.py",
        "--user-id", user_id,
        "--display-name", display_name, 
        "--port", str(port),
        "--verbose"
    ]
    
    print(f"Starting {display_name} on port {port}...")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                           text=True, bufsize=1)
    return proc

def test_two_instances():
    """Test with two instances on same machine"""
    print("=== Testing Two LSNP Instances ===")
    
    # Start Alice on port 50999
    alice_proc = start_client("alice@127.0.0.1", "Alice", 50999)
    time.sleep(2)
    
    # Start Bob on port 50998
    bob_proc = start_client("bob@127.0.0.1", "Bob", 50998)
    time.sleep(3)
    
    print("Both instances started. Let them run for 10 seconds...")
    time.sleep(10)
    
    # Check if both are still running
    alice_running = alice_proc.poll() is None
    bob_running = bob_proc.poll() is None
    
    print(f"Alice status: {'RUNNING' if alice_running else 'STOPPED'}")
    print(f"Bob status: {'RUNNING' if bob_running else 'STOPPED'}")
    
    # Get outputs
    if alice_running:
        alice_proc.terminate()
        alice_out, alice_err = alice_proc.communicate(timeout=5)
        print(f"Alice output (last 500 chars):\n{alice_out[-500:]}")
    
    if bob_running:
        bob_proc.terminate()
        bob_out, bob_err = bob_proc.communicate(timeout=5)
        print(f"Bob output (last 500 chars):\n{bob_out[-500:]}")
    
    return alice_running and bob_running

def test_manual_hello():
    """Test manual HELLO message exchange"""
    print("\n=== Manual HELLO Test Instructions ===")
    print("1. Start two terminals:")
    print("   Terminal 1: python main.py --user-id 'alice@127.0.0.1' --display-name 'Alice' --port 50999")
    print("   Terminal 2: python main.py --user-id 'bob@127.0.0.1' --display-name 'Bob' --port 50998")
    print("2. In Alice's terminal, choose option 2 (Send HELLO)")
    print("3. Enter target IP: 127.0.0.1")
    print("4. Enter target port: 50998")
    print("5. Check if Bob receives the HELLO message")
    print("6. Repeat from Bob to Alice (port 50999)")

def main():
    print("LSNP Multi-Device Test Suite")
    print("=" * 40)
    
    print("Testing scenarios:")
    print("1. Two instances on same machine")
    print("2. Manual testing instructions")
    
    # Test 1: Automated two instances
    success = test_two_instances()
    
    if success:
        print("\n✅ Two instances can start and run simultaneously")
    else:
        print("\n❌ Issues with running two instances")
    
    # Test 2: Manual instructions
    test_manual_hello()
    
    print("\n=== Network Testing Recommendations ===")
    print("For real device testing:")
    print("1. Connect both devices to same Wi-Fi network")
    print("2. Find IP addresses: ipconfig (Windows) or ifconfig (Linux/Mac)")
    print("3. Ensure firewall allows UDP traffic on port 50999")
    print("4. Test with: python main.py --user-id 'user@<YOUR_IP>' --display-name 'YourName' --port 50999")

if __name__ == "__main__":
    main()
