#!/usr/bin/env python3
"""
Test script for avatar and LIKE functionality
"""

import os
import sys
import time
import base64

# Add the project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from msg_System import msgSystem
from network_System import networkSystem
from vars import *

def test_avatar_encoding():
    """Test avatar encoding functionality"""
    print("=== Testing Avatar Encoding ===")
    
    # Create a test network and message system
    net_system = networkSystem(8080, verbose=True)
    msg_system = msgSystem(net_system, None)
    
    # Test default avatar
    default_avatar_path = os.path.join("uploads", "default.jpg")
    if os.path.exists(default_avatar_path):
        print(f"✓ Found default avatar: {default_avatar_path}")
        
        # Test encoding
        try:
            avatar_data = msg_system.encode_avatar(default_avatar_path)
            if avatar_data:
                print(f"✓ Successfully encoded avatar")
                print(f"  - AVATAR_TYPE: {avatar_data.get('AVATAR_TYPE')}")
                print(f"  - AVATAR_ENCODING: {avatar_data.get('AVATAR_ENCODING')}")
                print(f"  - AVATAR_DATA length: {len(avatar_data.get('AVATAR_DATA', ''))} characters")
                
                # Verify it's valid base64
                try:
                    base64.b64decode(avatar_data.get('AVATAR_DATA', ''))
                    print(f"✓ Avatar data is valid base64")
                except Exception as e:
                    print(f"✗ Avatar data is not valid base64: {e}")
                    
            else:
                print("✗ Failed to encode avatar")
                
        except Exception as e:
            print(f"✗ Error encoding avatar: {e}")
    else:
        print(f"✗ Default avatar not found: {default_avatar_path}")

def test_profile_with_avatar():
    """Test profile creation with default avatar"""
    print("\n=== Testing Profile Creation with Avatar ===")
    
    # Create a test network and message system
    net_system = networkSystem(8081, verbose=True)
    msg_system = msgSystem(net_system, None)
    
    try:
        # Test creating profile without specifying avatar (should use default)
        msg_system.create_profile("test_user", "Test User", "Testing avatars")
        
        # Check if avatar was set
        user_info = msg_system.known_peers.get("test_user", {})
        avatar_path = user_info.get('avatar_path')
        
        if avatar_path:
            print(f"✓ Profile created with avatar: {avatar_path}")
            if "default.jpg" in avatar_path:
                print(f"✓ Default avatar was automatically used")
            else:
                print(f"? Custom avatar was used: {avatar_path}")
        else:
            print("✗ No avatar was set in profile")
            
    except Exception as e:
        print(f"✗ Error creating profile: {e}")

def test_like_message_format():
    """Test LIKE message format compliance"""
    print("\n=== Testing LIKE Message Format ===")
    
    # Create a test network and message system
    net_system = networkSystem(8082, verbose=True)
    msg_system = msgSystem(net_system, None)
    msg_system.user_id = "test_user"
    
    try:
        # Test creating a LIKE message (we'll capture it before sending)
        original_send = net_system.send_message
        captured_message = None
        
        def capture_message(message):
            nonlocal captured_message
            captured_message = message
            print(f"✓ Captured LIKE message")
            
        net_system.send_message = capture_message
        
        # Create LIKE message
        msg_system.send_like("target_user", 1234567890, "LIKE")
        
        if captured_message:
            print(f"✓ LIKE message created successfully")
            
            # Check required fields according to specs
            required_fields = ["TYPE", "MESSAGE_ID", "FROM", "TO", "ACTION", "POST_TIMESTAMP", "TIMESTAMP", "TOKEN"]
            missing_fields = []
            
            for field in required_fields:
                if field not in captured_message:
                    missing_fields.append(field)
                else:
                    print(f"  ✓ {field}: {captured_message[field]}")
            
            if missing_fields:
                print(f"✗ Missing required fields: {missing_fields}")
            else:
                print(f"✓ All required LIKE fields present")
                
            # Verify ACTION values
            action = captured_message.get("ACTION")
            if action in ["LIKE", "UNLIKE"]:
                print(f"✓ Valid ACTION value: {action}")
            else:
                print(f"✗ Invalid ACTION value: {action}")
                
        else:
            print("✗ Failed to capture LIKE message")
            
        # Restore original send method
        net_system.send_message = original_send
        
    except Exception as e:
        print(f"✗ Error testing LIKE message: {e}")

def main():
    """Run all tests"""
    print("Testing Avatar and LIKE functionality\n")
    
    test_avatar_encoding()
    test_profile_with_avatar() 
    test_like_message_format()
    
    print("\n=== Test Summary ===")
    print("✓ Tests completed!")
    print("If all tests show ✓, then avatar and LIKE features are working correctly.")

if __name__ == "__main__":
    main()
