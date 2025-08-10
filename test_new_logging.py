#!/usr/bin/env python3
"""
Test the new logging format
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network_System import networkSystem
from msg_System import msgSystem
from file_game import fileGameSystem
from vars import *

def test_new_logging_format():
    """Test the new clean logging format."""
    print("=== Testing New Logging Format ===\n")
    
    # Setup system with verbose mode
    net = networkSystem(51001, verbose=True)
    msg = msgSystem(net)
    game = fileGameSystem(net)
    net.set_msg_system(msg)
    net.set_file_game_system(game)
    
    # Create profile
    msg.create_profile("alice@127.0.0.1", "Alice", "Testing new logs")
    
    print("1. Testing ACK message logging")
    print("-" * 40)
    
    # Test ACK logging
    test_message = {
        "TYPE": MSG_TICTACTOE_INVITE,
        "FROM": "bob@127.0.0.1",
        "TO": "alice@127.0.0.1",
        "GAME_ID": "test_game_001",
        "MESSAGE_ID": "test_invite_001",
        "TIMESTAMP": "1754844000",
        "TOKEN": "bob@127.0.0.1|1754847600|game"
    }
    
    # This should trigger the new ACK logging format
    msg.send_ack(test_message)
    
    print("\n2. Testing game message logging")
    print("-" * 40)
    
    # Test game message logging
    game_message = {
        "TYPE": MSG_TICTACTOE_ACCEPT,
        "FROM": "alice@127.0.0.1",
        "TO": "bob@127.0.0.1",
        "GAME_ID": "test_game_001",
        "MESSAGE_ID": "test_accept_001",
        "TIMESTAMP": "1754844100",
        "TOKEN": "alice@127.0.0.1|1754847700|game"
    }
    
    # Test the new logging method
    game.log_message("Game Acceptance", game_message)
    
    print("\n3. Testing network message logging")
    print("-" * 40)
    
    # Test network message logging
    net.log_message("Full message", test_message)
    
    print("\n=== New Logging Format Test Complete ===")

if __name__ == "__main__":
    test_new_logging_format()
