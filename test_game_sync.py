#!/usr/bin/env python3
"""
Test the game acceptance synchronization fix
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

def test_game_acceptance_sync():
    """Test that game acceptance properly synchronizes between players."""
    print("=== Testing Game Acceptance Synchronization ===\n")
    
    # Setup Bob's system (inviter)
    bob_net = networkSystem(51001, verbose=True)
    bob_msg = msgSystem(bob_net)
    bob_game = fileGameSystem(bob_net)
    bob_net.set_msg_system(bob_msg)
    bob_net.set_file_game_system(bob_game)
    bob_msg.create_profile("bob@127.0.0.1", "Bob", "Testing sync")
    
    # Setup Alice's system (accepter)
    alice_net = networkSystem(51002, verbose=True)
    alice_msg = msgSystem(alice_net)
    alice_game = fileGameSystem(alice_net)
    alice_net.set_msg_system(alice_msg)
    alice_net.set_file_game_system(alice_game)
    alice_msg.create_profile("alice@127.0.0.1", "Alice", "Testing sync")
    
    current_time = int(time.time())
    
    print("1. Bob sends game invitation to Alice")
    print("-" * 40)
    
    # Bob invites Alice to a game
    bob_game.invite_to_game("alice@127.0.0.1", "X")
    
    # Get the game ID from Bob's pending invites
    bob_invites = getattr(bob_game, 'game_invites', {})
    if bob_invites:
        game_id = list(bob_invites.keys())[0]
        print(f"✓ Bob created invitation for game {game_id}")
    else:
        print("✗ Bob failed to create invitation")
        return False
    
    print(f"Bob's active games: {len(bob_game.get_active_games())}")
    print(f"Bob's pending invites: {len(bob_invites)}")
    
    print("\n2. Simulate Alice receiving the invitation")
    print("-" * 40)
    
    # Simulate Alice receiving the invitation
    invite_message = {
        "TYPE": MSG_TICTACTOE_INVITE,
        "FROM": "bob@127.0.0.1",
        "TO": "alice@127.0.0.1",
        "GAMEID": game_id,
        "SYMBOL": "X",
        "MESSAGE_ID": "test_invite_001",
        "TIMESTAMP": str(current_time),
        "TOKEN": f"bob@127.0.0.1|{current_time + 3600}|{SCOPE_GAME}"
    }
    
    alice_game.handle_game_invite(invite_message)
    
    alice_invites = getattr(alice_game, 'game_invites', {})
    print(f"Alice received invitations: {len(alice_invites)}")
    
    if game_id in alice_invites:
        print(f"✓ Alice has invitation for game {game_id}")
    else:
        print("✗ Alice didn't receive the invitation")
        return False
    
    print("\n3. Alice accepts the game invitation")
    print("-" * 40)
    
    # Alice accepts the game
    result = alice_game.accept_game_invite(game_id, "bob@127.0.0.1")
    
    if result:
        print("✓ Alice successfully accepted the game")
    else:
        print("✗ Alice failed to accept the game")
        return False
    
    # Check Alice's game state
    alice_games = alice_game.get_active_games()
    print(f"Alice's active games after acceptance: {len(alice_games)}")
    
    if alice_games:
        alice_game_info = alice_games[0]
        print(f"Alice's game players: {alice_game_info['players']}")
        print(f"Alice's symbol: {alice_game_info['players']['alice@127.0.0.1']}")
    
    print("\n4. Simulate Bob receiving the acceptance")
    print("-" * 40)
    
    # Simulate Bob receiving the acceptance message
    accept_message = {
        "TYPE": MSG_TICTACTOE_ACCEPT,
        "FROM": "alice@127.0.0.1",
        "TO": "bob@127.0.0.1",
        "GAME_ID": game_id,
        "MESSAGE_ID": "test_accept_001",
        "TIMESTAMP": str(current_time),
        "TOKEN": f"alice@127.0.0.1|{current_time + 3600}|{SCOPE_GAME}"
    }
    
    bob_game.handle_game_accept(accept_message)
    
    # Check Bob's game state
    bob_games = bob_game.get_active_games()
    print(f"Bob's active games after receiving acceptance: {len(bob_games)}")
    
    if bob_games:
        bob_game_info = bob_games[0]
        print(f"Bob's game players: {bob_game_info['players']}")
        print(f"Bob's symbol: {bob_game_info['players']['bob@127.0.0.1']}")
    
    print("\n5. Verify synchronization")
    print("-" * 40)
    
    # Check that both players have the same game
    alice_has_game = len(alice_games) > 0 and game_id in [g['game_id'] if 'game_id' in g else game_id for g in alice_games]
    bob_has_game = len(bob_games) > 0 and game_id in [g['game_id'] if 'game_id' in g else game_id for g in bob_games]
    
    print(f"Alice has game {game_id}: {'✓' if alice_has_game else '✗'}")
    print(f"Bob has game {game_id}: {'✓' if bob_has_game else '✗'}")
    
    # Check that invitations are cleaned up
    alice_invites_after = getattr(alice_game, 'game_invites', {})
    bob_invites_after = getattr(bob_game, 'game_invites', {})
    
    print(f"Alice's pending invites after acceptance: {len(alice_invites_after)}")
    print(f"Bob's pending invites after acceptance: {len(bob_invites_after)}")
    
    success = (alice_has_game and bob_has_game and 
               len(alice_invites_after) == 0 and len(bob_invites_after) == 0)
    
    if success:
        print("\n✅ Game acceptance synchronization working correctly!")
    else:
        print("\n❌ Game acceptance synchronization failed!")
    
    print("\n=== Test Complete ===")
    return success

if __name__ == "__main__":
    test_game_acceptance_sync()
