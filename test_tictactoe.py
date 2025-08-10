#!/usr/bin/env python3

"""
Test script for Tic-Tac-Toe functionality
Demonstrates the game features without needing multiple users
"""

from file_game import fileGameSystem
from network_System import networkSystem
from msg_System import msgSystem
from vars import *

def test_tic_tac_toe():
    print("🎮 Testing Tic-Tac-Toe Implementation")
    print("=" * 40)
    
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
    
    print("\n1. Testing Game Creation")
    print("-" * 25)
    
    # Test invite creation
    game_id = file_game_system.invite_to_game("bob@127.0.0.1", "X")
    print(f"Created game invitation: {game_id}")
    
    # Show active games
    games = file_game_system.get_active_games()
    invites = file_game_system.get_game_invites()
    print(f"Active games: {len(games)}")
    print(f"Pending invites: {len(invites)}")
    
    print("\n2. Testing Game Acceptance")
    print("-" * 27)
    
    # Accept the invitation (simulate)
    if invites:
        game_id, invite = invites[0]
        if file_game_system.accept_game_invite(game_id, invite['from']):
            print(f"✅ Successfully accepted game {game_id}")
        else:
            print(f"❌ Failed to accept game {game_id}")
    
    print("\n3. Testing Game Board Display")
    print("-" * 31)
    
    # Display initial board
    games = file_game_system.get_active_games()
    if games:
        game_id = games[0]['game_id']
        file_game_system.display_game_board(game_id)
    
    print("\n4. Testing Move Validation")
    print("-" * 27)
    
    if games:
        game_id = games[0]['game_id']
        
        # Test valid moves
        valid_moves = [0, 1, 4, 8]
        for position in valid_moves:
            if file_game_system.validate_move(game_id, position, "X", 1):
                print(f"✅ Position {position} is valid")
            else:
                print(f"❌ Position {position} is invalid")
        
        # Test invalid moves
        invalid_moves = [-1, 9, 10]
        for position in invalid_moves:
            if not file_game_system.validate_move(game_id, position, "X", 1):
                print(f"✅ Position {position} correctly rejected")
            else:
                print(f"❌ Position {position} incorrectly accepted")
    
    print("\n5. Testing Win Detection")
    print("-" * 25)
    
    # Test win conditions
    test_boards = [
        # Horizontal wins
        ["X", "X", "X", " ", " ", " ", " ", " ", " "],  # Top row
        [" ", " ", " ", "O", "O", "O", " ", " ", " "],  # Middle row
        [" ", " ", " ", " ", " ", " ", "X", "X", "X"],  # Bottom row
        
        # Vertical wins
        ["X", " ", " ", "X", " ", " ", "X", " ", " "],  # Left column
        [" ", "O", " ", " ", "O", " ", " ", "O", " "],  # Middle column
        [" ", " ", "X", " ", " ", "X", " ", " ", "X"],  # Right column
        
        # Diagonal wins
        ["X", " ", " ", " ", "X", " ", " ", " ", "X"],  # TL to BR
        [" ", " ", "O", " ", "O", " ", "O", " ", " "],  # TR to BL
        
        # No win
        ["X", "O", "X", "O", "X", "O", "O", "X", "O"],  # Draw
        ["X", " ", "O", " ", "X", " ", "O", " ", " "],   # Incomplete
    ]
    
    for i, board in enumerate(test_boards):
        result = file_game_system.detect_game_winner(board)
        if result:
            symbol, winning_line = result
            print(f"Test {i+1}: Winner {symbol}, Line: {winning_line}")
        else:
            print(f"Test {i+1}: No winner")
    
    print("\n6. Testing Game State Management")
    print("-" * 33)
    
    if games:
        game_id = games[0]['game_id']
        state = file_game_system.get_game_state(game_id)
        if state:
            print(f"Game {game_id} state:")
            print(f"  Status: {state['status']}")
            print(f"  Current turn: {state['current_turn']}")
            print(f"  Turn number: {state['turn_number']}")
            print(f"  Players: {state['players']}")
    
    print("\n✅ Tic-Tac-Toe Test Complete!")
    print("Implementation includes:")
    print("- Game invitation system")
    print("- Move validation and processing")
    print("- Win/draw detection")
    print("- Board display")
    print("- Game state management")
    print("- LSNP message integration")

if __name__ == "__main__":
    test_tic_tac_toe()
