#!/usr/bin/env python3

"""
Quick test to verify ACK method compatibility
"""

from file_game import fileGameSystem
from network_System import networkSystem
from msg_System import msgSystem
from vars import *

def test_ack_compatibility():
    print("🔧 Testing ACK Method Compatibility")
    print("=" * 35)
    
    # Create systems
    net_system = networkSystem(12345, verbose=False)
    msg_system = msgSystem(net_system)
    file_game_system = fileGameSystem(net_system)
    
    # Set up connections
    net_system.set_msg_system(msg_system)
    net_system.set_file_game_system(file_game_system)
    
    # Set user info
    msg_system.user_id = "alice@127.0.0.1"
    msg_system.display_name = "Alice"
    
    # Create a test message
    test_message = {
        'TYPE': 'TICTACTOE_INVITE',
        'FROM': 'bob@127.0.0.1',
        'TO': 'alice@127.0.0.1',
        'GAMEID': 'g123',
        'MESSAGE_ID': 'test123',
        'SYMBOL': 'X',
        'TIMESTAMP': '1628943600',
        'TOKEN': 'bob@127.0.0.1|1628947200|game'
    }
    
    print("1. Testing send_ack method signature compatibility")
    
    try:
        # Test the file_game send_ack method
        file_game_system.send_ack(test_message)
        print("✅ file_game send_ack works correctly")
    except Exception as e:
        print(f"❌ file_game send_ack failed: {e}")
    
    try:
        # Test the msg_system send_ack method directly
        msg_system.send_ack(test_message)
        print("✅ msg_system send_ack works correctly")
    except Exception as e:
        print(f"❌ msg_system send_ack failed: {e}")
    
    print("\n2. Testing game invitation handling")
    
    try:
        file_game_system.handle_game_invite(test_message)
        print("✅ Game invitation handling works")
    except Exception as e:
        print(f"❌ Game invitation handling failed: {e}")
    
    print("\n✅ ACK compatibility test complete!")

if __name__ == "__main__":
    test_ack_compatibility()
