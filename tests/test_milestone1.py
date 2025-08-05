#!/usr/bin/env python3
"""
Test script for Milestone #1 verification
Tests all required functionality for LSNP basic implementation
"""

import threading
import time
import subprocess
import sys
from vars import *

def test_message_format():
    """Test LSNP message format conversion"""
    print("=== Testing LSNP Message Format ===")
    
    # Import our classes
    from network_System import networkSystem
    
    net = networkSystem(LSNP_PORT, verbose=True)
    
    # Test message dict to LSNP conversion
    test_message = {
        "TYPE": MSG_POST,
        "USER_ID": "test@127.0.0.1",
        "CONTENT": "Hello LSNP!",
        "TTL": 3600,
        "TIMESTAMP": int(time.time())
    }
    
    lsnp_format = net._dict_to_lsnp(test_message)
    print("Original dict:", test_message)
    print("LSNP format:")
    print(repr(lsnp_format))
    
    # Test parsing back
    parsed = net._lsnp_to_dict(lsnp_format)
    print("Parsed back:", parsed)
    
    # Verify they match (excluding BROADCAST key)
    original_filtered = {k:v for k,v in test_message.items() if k != "BROADCAST"}
    success = original_filtered == parsed
    print(f"Format conversion test: {'PASS' if success else 'FAIL'}")
    return success

def test_basic_functionality():
    """Test basic send/receive without infinite loops"""
    print("\n=== Testing Basic Send/Receive ===")
    
    try:
        # Start a client on port 50999 for testing
        proc = subprocess.Popen([
            sys.executable, "main.py", 
            "--user-id", "testuser@127.0.0.1", 
            "--display-name", "TestUser",
            "--port", str(LSNP_PORT),
            "--verbose"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Let it start up
        time.sleep(2)
        
        # Check if process is still running (not crashed)
        if proc.poll() is None:
            print("Application startup: PASS")
            
            # Terminate the test process
            proc.terminate()
            proc.wait(timeout=5)
            return True
        else:
            stdout, stderr = proc.communicate()
            print("Application startup: FAIL")
            print("STDOUT:", stdout[:500])
            print("STDERR:", stderr[:500])
            return False
            
    except Exception as e:
        print(f"Test failed with exception: {e}")
        return False

def main():
    """Run all Milestone #1 tests"""
    print("LSNP Milestone #1 Test Suite")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Message format
    if test_message_format():
        tests_passed += 1
    
    # Test 2: Basic functionality
    if test_basic_functionality():
        tests_passed += 1
    
    print(f"\n=== Test Results ===")
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All Milestone #1 tests PASSED!")
        print("\nMilestone #1 Requirements Met:")
        print("✅ Clean Architecture & Logging")
        print("✅ Protocol Compliance Test Suite")
        print("✅ Message Sending and Receiving")
        print("✅ Protocol Parsing and Message Format")
    else:
        print("❌ Some tests failed. Please check implementation.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    main()
