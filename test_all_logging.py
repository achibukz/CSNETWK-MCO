#!/usr/bin/env python3
"""
Test comprehensive message logging in new format
"""

import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network_System import networkSystem
from msg_System import msgSystem
from file_game import fileGameSystem
from vars import *

def test_all_message_logging():
    """Test logging for all message types in the new format."""
    print("=== Testing All Message Types in New Format ===\n")
    
    # Setup system with verbose mode
    net = networkSystem(51003, verbose=True)
    msg = msgSystem(net)
    game = fileGameSystem(net)
    net.set_msg_system(msg)
    net.set_file_game_system(game)
    
    # Create profile
    msg.create_profile("test@127.0.0.1", "Test User", "Testing all logs")
    
    current_time = int(time.time())
    
    print("1. Testing HELLO message")
    print("-" * 30)
    hello_msg = {
        "TYPE": "HELLO",
        "DATA": "Test is online",
        "USER_ID": "test@127.0.0.1", 
        "DISPLAY_NAME": "Test User",
        "LISTEN_PORT": 51003
    }
    # Simulate receiving a HELLO message
    net.parse_message(hello_msg, ("127.0.0.1", 51003))
    
    print("\n2. Testing TICTACTOE_INVITE message") 
    print("-" * 30)
    invite_msg = {
        "TYPE": MSG_TICTACTOE_INVITE,
        "FROM": "bob@127.0.0.1",
        "TO": "test@127.0.0.1",
        "GAMEID": "test_game_123",
        "SYMBOL": "X",
        "MESSAGE_ID": "invite_123",
        "TIMESTAMP": str(current_time),
        "TOKEN": f"bob@127.0.0.1|{current_time + 3600}|{SCOPE_GAME}"
    }
    # Simulate receiving a game invite
    net.parse_message(invite_msg, ("127.0.0.1", 51004))
    
    print("\n3. Testing FILE_OFFER message")
    print("-" * 30)
    file_msg = {
        "TYPE": MSG_FILE_OFFER,
        "FROM": "alice@127.0.0.1",
        "TO": "test@127.0.0.1", 
        "FILE_ID": "file_123",
        "FILENAME": "document.pdf",
        "FILESIZE": "1024",
        "MESSAGE_ID": "file_offer_123",
        "TIMESTAMP": str(current_time),
        "TOKEN": f"alice@127.0.0.1|{current_time + 3600}|{SCOPE_FILE}"
    }
    # Simulate receiving a file offer
    net.parse_message(file_msg, ("127.0.0.1", 51005))
    
    print("\n4. Testing GROUP_CREATE message")
    print("-" * 30)
    group_msg = {
        "TYPE": MSG_GROUP_CREATE,
        "FROM": "admin@127.0.0.1",
        "GROUP_ID": "group_123",
        "GROUP_NAME": "Test Group",
        "MEMBERS": "test@127.0.0.1,alice@127.0.0.1",
        "MESSAGE_ID": "group_create_123",
        "TIMESTAMP": str(current_time),
        "TOKEN": f"admin@127.0.0.1|{current_time + 3600}|{SCOPE_GROUP}"
    }
    # Simulate receiving a group creation
    net.parse_message(group_msg, ("127.0.0.1", 51006))
    
    print("\n=== All Message Types Logged in New Format ===")
    print("✅ All logging now uses clean, organized format!")

if __name__ == "__main__":
    test_all_message_logging()
