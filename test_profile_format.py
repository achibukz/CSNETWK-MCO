#!/usr/bin/env python3
"""
Test PROFILE message format compliance
"""

from msg_System import msgSystem
from network_System import networkSystem
from vars import *

def test_profile_format():
    """Test if PROFILE message follows LSNP specification"""
    print("=== Testing PROFILE Message Format ===")
    
    # Create systems
    net = networkSystem(50999, verbose=True)
    msg = msgSystem(net)
    net.set_msg_system(msg)
    
    # Test basic PROFILE message
    print("\n1. Basic PROFILE message:")
    message = {
        "TYPE": MSG_PROFILE,
        "USER_ID": "dave@192.168.1.10",
        "DISPLAY_NAME": "Dave",
        "STATUS": "Exploring LSNP!",
        "BROADCAST": True
    }
    
    lsnp_format = net._dict_to_lsnp(message)
    print("Generated LSNP format:")
    print(lsnp_format)
    
    # Test PROFILE with avatar
    print("\n2. PROFILE message with avatar fields:")
    message_with_avatar = {
        "TYPE": MSG_PROFILE,
        "USER_ID": "dave@192.168.1.10",
        "DISPLAY_NAME": "Dave",
        "STATUS": "Exploring LSNP!",
        "AVATAR_TYPE": "image/png",
        "AVATAR_ENCODING": "base64",
        "AVATAR_DATA": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
        "BROADCAST": True
    }
    
    lsnp_format_avatar = net._dict_to_lsnp(message_with_avatar)
    print("Generated LSNP format with avatar:")
    print(lsnp_format_avatar)
    
    # Test parsing back
    print("\n3. Parse back test:")
    parsed = net._lsnp_to_dict(lsnp_format)
    print("Parsed message:")
    for key, value in parsed.items():
        print(f"  {key}: {value}")
    
    # Test profile handling
    print("\n4. Test profile message handling:")
    msg.handle_profile_message(parsed)
    
    # Check if it stores correctly
    print("\n5. Stored peer info:")
    peers = msg.get_known_peers()
    for user_id, info in peers.items():
        print(f"  {user_id}: {info}")

if __name__ == "__main__":
    test_profile_format()
