# Member 3

import time
import random
import base64
import os
from vars import *

class fileGameSystem:
    def __init__(self, netSystem):
        self.netSystem = netSystem
        
        # Game state management
        self.active_games = {}  # {game_id: game_data}
        self.game_invites = {}  # {game_id: invite_data}
        self.pending_moves = {}  # {message_id: move_data} for retries
        
        # File transfer management
        self.file_offers = {}   # {file_id: offer_data}
        self.file_chunks = {}   # {file_id: {chunk_index: data}}
        self.active_transfers = {}  # {file_id: transfer_data}

    def offer_file(self, to_user, file_path, description=""):
        """Offer a file to another user."""
        # TODO: Implement file transfer functionality
        print("📁 File transfer not yet implemented")
        pass

    def accept_file_offer(self, file_id, from_user):
        """Accept a file offer."""
        # TODO: Implement file transfer functionality
        print("📁 File transfer not yet implemented")
        pass

    def send_file_chunk(self, file_id, chunk_index, data):
        """Send a file chunk."""
        # TODO: Implement file transfer functionality
        pass

    def receive_file_chunk(self, message):
        """Receive a file chunk."""
        # TODO: Implement file transfer functionality
        pass

    def reconstruct_file(self, file_id):
        """Reconstruct a file from chunks."""
        # TODO: Implement file transfer functionality
        pass

    def send_file_received(self, file_id, to_user, status="COMPLETE"):
        """Send file received confirmation."""
        # TODO: Implement file transfer functionality
        pass

    def get_file_transfers(self):
        """Get list of active file transfers."""
        # TODO: Implement file transfer functionality
        return []

    def retry_game_move(self, game_id, position, max_retries=3):
        """Retry a game move if it fails."""
        for attempt in range(max_retries):
            try:
                if self.make_move(game_id, position):
                    return True
                time.sleep(1)  # Wait before retry
            except Exception as e:
                print(f"Move attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    print(f"❌ Failed to make move after {max_retries} attempts")
                    return False
        return False

    def simulate_file_packet_loss(self):  # For testing
        """Simulate file packet loss for testing."""
        # TODO: Implement for testing file transfer reliability
        pass

    def invite_to_game(self, to_user, symbol="X"):
        """Send a Tic-Tac-Toe game invitation."""
        # Generate unique game ID
        game_id = f"g{random.randint(0, 255)}"
        
        # Ensure game ID is unique
        while game_id in self.active_games or game_id in self.game_invites:
            game_id = f"g{random.randint(0, 255)}"
        
        # Get user info
        user_id = getattr(self.netSystem.msg_system, 'user_id', 'unknown@127.0.0.1')
        timestamp = int(time.time())
        message_id = f"{random.getrandbits(64):016x}"
        
        # Create game invite
        invite_message = {
            "TYPE": MSG_TICTACTOE_INVITE,
            "FROM": user_id,
            "TO": to_user,
            "GAMEID": game_id,
            "MESSAGE_ID": message_id,
            "SYMBOL": symbol,
            "TIMESTAMP": str(timestamp),  # Convert to string for LSNP
            "TOKEN": f"{user_id}|{timestamp + 3600}|{SCOPE_GAME}"
        }
        
        # Store invite locally
        self.game_invites[game_id] = {
            'from': user_id,
            'to': to_user,
            'symbol': symbol,
            'timestamp': timestamp,
            'message_id': message_id
        }
        
        # Send invitation
        self.netSystem.send_message(invite_message)
        
        # Add to pending ACKs if msg_system exists
        if hasattr(self.netSystem, 'msg_system') and self.netSystem.msg_system:
            self.netSystem.msg_system.pending_acks[message_id] = {
                'timestamp': timestamp,
                'retries': 0,
                'message': invite_message,
                'target_user': to_user
            }
        
        print(f"🎮 Sent Tic-Tac-Toe invitation to {to_user} (Game: {game_id}, Symbol: {symbol})")
        return game_id

    def accept_game_invite(self, game_id, from_user):
        """Accept a game invitation and start the game."""
        if game_id not in self.game_invites:
            print(f"❌ No pending invitation for game {game_id}")
            return False
        
        invite = self.game_invites[game_id]
        user_id = getattr(self.netSystem.msg_system, 'user_id', 'unknown@127.0.0.1')
        
        # Determine our symbol (opposite of inviter)
        their_symbol = invite['symbol']
        our_symbol = "O" if their_symbol == "X" else "X"
        
        # Initialize game state
        self.active_games[game_id] = {
            'board': [" " for _ in range(9)],  # 3x3 board (positions 0-8)
            'players': {
                invite['from']: their_symbol,
                user_id: our_symbol
            },
            'current_turn': "X",  # X always goes first
            'turn_number': 1,
            'status': 'active',
            'created': time.time(),
            'last_move': time.time()
        }
        
        # Remove from invites
        del self.game_invites[game_id]
        
        # Make first move if we're X
        if our_symbol == "X":
            print(f"🎮 Game {game_id} started! You are {our_symbol}. It's your turn!")
            self.display_game_board(game_id)
            print("Choose your move (position 0-8):")
            print("0 | 1 | 2")
            print("3 | 4 | 5") 
            print("6 | 7 | 8")
        else:
            print(f"🎮 Game {game_id} started! You are {our_symbol}. Waiting for {from_user} to move...")
            self.display_game_board(game_id)
        
        return True

    def make_move(self, game_id, position):
        """Make a move in the specified game."""
        if game_id not in self.active_games:
            print(f"❌ Game {game_id} not found")
            return False
        
        game = self.active_games[game_id]
        user_id = getattr(self.netSystem.msg_system, 'user_id', 'unknown@127.0.0.1')
        
        # Validate it's our turn
        if user_id not in game['players']:
            print(f"❌ You are not a player in game {game_id}")
            return False
        
        our_symbol = game['players'][user_id]
        if game['current_turn'] != our_symbol:
            print(f"❌ Not your turn! Waiting for {game['current_turn']}")
            return False
        
        # Validate position
        if not self.validate_move(game_id, position, our_symbol, game['turn_number']):
            return False
        
        # Make the move locally
        game['board'][position] = our_symbol
        game['turn_number'] += 1
        game['last_move'] = time.time()
        
        # Switch turns
        game['current_turn'] = "O" if our_symbol == "X" else "X"
        
        # Find opponent
        opponent = None
        for player, symbol in game['players'].items():
            if player != user_id:
                opponent = player
                break
        
        if not opponent:
            print("❌ No opponent found")
            return False
        
        # Create move message
        timestamp = int(time.time())
        message_id = f"{random.getrandbits(64):016x}"
        
        move_message = {
            "TYPE": MSG_TICTACTOE_MOVE,
            "FROM": user_id,
            "TO": opponent,
            "GAMEID": game_id,
            "MESSAGE_ID": message_id,
            "POSITION": str(position),  # Convert to string for LSNP
            "SYMBOL": our_symbol,
            "TURN": str(game['turn_number'] - 1),  # Convert to string
            "TOKEN": f"{user_id}|{timestamp + 3600}|{SCOPE_GAME}"
        }
        
        # Send move
        self.netSystem.send_message(move_message)
        
        # Add to pending ACKs
        if hasattr(self.netSystem, 'msg_system') and self.netSystem.msg_system:
            self.netSystem.msg_system.pending_acks[message_id] = {
                'timestamp': timestamp,
                'retries': 0,
                'message': move_message,
                'target_user': opponent
            }
        
        # Display updated board
        self.display_game_board(game_id)
        
        # Check for game end
        result = self.check_game_result(game_id)
        if result:
            self.send_game_result(game_id, opponent, result)
        else:
            print(f"Waiting for {opponent}'s move...")
        
        return True

    def validate_move(self, game_id, position, symbol, turn):
        """Validate if a move is legal."""
        if game_id not in self.active_games:
            print(f"❌ Game {game_id} not found")
            return False
        
        game = self.active_games[game_id]
        
        # Check position bounds
        if not isinstance(position, int) or position < 0 or position > 8:
            print(f"❌ Invalid position {position}. Must be 0-8")
            return False
        
        # Check if position is empty
        if game['board'][position] != " ":
            print(f"❌ Position {position} is already occupied by '{game['board'][position]}'")
            return False
        
        # Check game is active
        if game['status'] != 'active':
            print(f"❌ Game {game_id} is not active (status: {game['status']})")
            return False
        
        return True

    def check_game_result(self, game_id):
        """Check if the game has ended and return result."""
        if game_id not in self.active_games:
            return None
        
        game = self.active_games[game_id]
        board = game['board']
        
        # Check for winner
        winner_info = self.detect_game_winner(board)
        if winner_info:
            symbol, winning_line = winner_info
            user_id = getattr(self.netSystem.msg_system, 'user_id', 'unknown@127.0.0.1')
            our_symbol = game['players'].get(user_id, '')
            
            if symbol == our_symbol:
                result = "WIN"
            else:
                result = "LOSS"
            
            game['status'] = 'finished'
            game['result'] = result
            game['winning_line'] = winning_line
            game['winner_symbol'] = symbol
            
            return {
                'result': result,
                'winning_line': winning_line,
                'winner_symbol': symbol
            }
        
        # Check for draw (board full)
        if " " not in board:
            game['status'] = 'finished'
            game['result'] = 'DRAW'
            return {
                'result': 'DRAW',
                'winning_line': None,
                'winner_symbol': None
            }
        
        return None

    def display_game_board(self, game_id):
        """Display the current game board."""
        if game_id not in self.active_games:
            print(f"❌ Game {game_id} not found")
            return
        
        game = self.active_games[game_id]
        board = game['board']
        
        print(f"\n🎮 Game {game_id} - Turn {game['turn_number']}")
        print("Current board:")
        print(f" {board[0]} | {board[1]} | {board[2]} ")
        print("-----------")
        print(f" {board[3]} | {board[4]} | {board[5]} ")
        print("-----------")
        print(f" {board[6]} | {board[7]} | {board[8]} ")
        print()
        
        # Show player info
        user_id = getattr(self.netSystem.msg_system, 'user_id', 'unknown@127.0.0.1')
        if user_id in game['players']:
            our_symbol = game['players'][user_id]
            print(f"You are: {our_symbol}")
            print(f"Current turn: {game['current_turn']}")
            
            if game['current_turn'] == our_symbol:
                print("👈 Your turn!")
            else:
                print("⏳ Waiting for opponent...")
        print()

    def get_active_games(self):
        pass

    def get_file_transfers(self):
        pass

    def handle_game_invite(self, message):
        """Handle incoming game invitation."""
        game_id = message.get('GAMEID')
        from_user = message.get('FROM')
        symbol = message.get('SYMBOL')
        
        if not all([game_id, from_user, symbol]):
            print("❌ Invalid game invitation message")
            return
        
        # Store the invitation
        self.game_invites[game_id] = {
            'from': from_user,
            'to': message.get('TO'),
            'symbol': symbol,
            'timestamp': message.get('TIMESTAMP', int(time.time())),
            'message_id': message.get('MESSAGE_ID')
        }
        
        # Get display name
        display_name = from_user
        if hasattr(self.netSystem, 'msg_system') and self.netSystem.msg_system:
            display_name = self.netSystem.msg_system.get_display_name(from_user)
        
        print(f"\n🎮 Game Invitation Received!")
        print(f"From: {display_name} ({from_user})")
        print(f"Game ID: {game_id}")
        print(f"Your symbol will be: {'O' if symbol == 'X' else 'X'}")
        print(f"To accept, use menu option to accept game {game_id}")
        
        # Send ACK
        if message.get('MESSAGE_ID'):
            self.send_ack(message)

    def handle_game_move(self, message):
        """Handle incoming game move."""
        game_id = message.get('GAMEID')
        position = message.get('POSITION')
        symbol = message.get('SYMBOL')
        turn = message.get('TURN')
        from_user = message.get('FROM')
        
        if not all([game_id, position is not None, symbol, turn is not None, from_user]):
            print("❌ Invalid game move message")
            return
        
        # Convert string values to integers
        try:
            position = int(position)
            turn = int(turn)
        except (ValueError, TypeError):
            print("❌ Invalid position or turn value")
            return
        
        # Check if we have this game
        if game_id not in self.active_games:
            print(f"❌ Received move for unknown game {game_id}")
            return
        
        game = self.active_games[game_id]
        
        # Validate the move
        if not self.validate_move(game_id, position, symbol, turn):
            print(f"❌ Invalid move received: position {position}")
            return
        
        # Check for duplicate moves (idempotency)
        if self.handle_duplicate_move(game_id, turn):
            print(f"⚠️ Duplicate move detected for turn {turn}, ignoring")
            if message.get('MESSAGE_ID'):
                self.send_ack(message)
            return
        
        # Apply the move
        game['board'][position] = symbol
        game['turn_number'] += 1
        game['last_move'] = time.time()
        
        # Switch turns
        game['current_turn'] = "O" if symbol == "X" else "X"
        
        # Display updated board
        print(f"\n🎮 {from_user} played {symbol} at position {position}")
        self.display_game_board(game_id)
        
        # Check for game end
        result = self.check_game_result(game_id)
        if result:
            self.send_game_result(game_id, from_user, result)
            self.display_game_result(game_id, result)
        else:
            user_id = getattr(self.netSystem.msg_system, 'user_id', 'unknown@127.0.0.1')
            our_symbol = game['players'].get(user_id, '')
            if game['current_turn'] == our_symbol:
                print("👈 Your turn! Choose your move (0-8):")
                print("0 | 1 | 2")
                print("3 | 4 | 5")
                print("6 | 7 | 8")
        
        # Send ACK
        if message.get('MESSAGE_ID'):
            self.send_ack(message)

    def handle_game_result(self, message):
        """Handle incoming game result."""
        game_id = message.get('GAMEID')
        result = message.get('RESULT')
        symbol = message.get('SYMBOL')
        winning_line = message.get('WINNING_LINE')
        from_user = message.get('FROM')
        
        if not all([game_id, result, symbol, from_user]):
            print("❌ Invalid game result message")
            return
        
        if game_id not in self.active_games:
            print(f"❌ Received result for unknown game {game_id}")
            return
        
        game = self.active_games[game_id]
        game['status'] = 'finished'
        game['final_result'] = result
        game['winner_symbol'] = symbol if result in ['WIN', 'LOSS'] else None
        
        if winning_line:
            try:
                game['winning_line'] = [int(x) for x in winning_line.split(',')]
            except:
                game['winning_line'] = None
        
        # Display final result
        self.display_game_result(game_id, {
            'result': 'LOSS' if result == 'WIN' else ('WIN' if result == 'LOSS' else result),
            'winning_line': game.get('winning_line'),
            'winner_symbol': symbol
        })
        
        # Send ACK
        if message.get('MESSAGE_ID'):
            self.send_ack(message)

    def detect_game_winner(self, board):
        """Detect if there's a winner and return (symbol, winning_line)."""
        # Define winning combinations (positions)
        winning_combinations = [
            [0, 1, 2],  # Top row
            [3, 4, 5],  # Middle row
            [6, 7, 8],  # Bottom row
            [0, 3, 6],  # Left column
            [1, 4, 7],  # Middle column
            [2, 5, 8],  # Right column
            [0, 4, 8],  # Diagonal top-left to bottom-right
            [2, 4, 6]   # Diagonal top-right to bottom-left
        ]
        
        for combination in winning_combinations:
            symbols = [board[pos] for pos in combination]
            
            # Check if all three positions have the same non-empty symbol
            if symbols[0] != " " and symbols[0] == symbols[1] == symbols[2]:
                return (symbols[0], combination)
        
        return None

    def send_game_result(self, game_id, opponent, result_info):
        """Send game result message."""
        user_id = getattr(self.netSystem.msg_system, 'user_id', 'unknown@127.0.0.1')
        timestamp = int(time.time())
        
        result_message = {
            "TYPE": MSG_TICTACTOE_RESULT,
            "FROM": user_id,
            "TO": opponent,
            "GAMEID": game_id,
            "MESSAGE_ID": f"{random.getrandbits(64):016x}",
            "RESULT": result_info['result'],
            "SYMBOL": result_info['winner_symbol'] or '',
            "TIMESTAMP": str(timestamp)  # Convert to string for LSNP
        }
        
        if result_info['winning_line']:
            result_message["WINNING_LINE"] = ','.join(map(str, result_info['winning_line']))
        
        self.netSystem.send_message(result_message)
    
    def display_game_result(self, game_id, result_info):
        """Display the final game result."""
        if game_id not in self.active_games:
            return
        
        game = self.active_games[game_id]
        self.display_game_board(game_id)
        
        result = result_info['result']
        winning_line = result_info.get('winning_line')
        winner_symbol = result_info.get('winner_symbol')
        
        print("🎯 GAME OVER! 🎯")
        if result == "WIN":
            print("🎉 You WON! 🎉")
        elif result == "LOSS":
            print("😔 You lost.")
        elif result == "DRAW":
            print("🤝 It's a DRAW!")
        elif result == "FORFEIT":
            print("🏃 Game forfeited.")
        
        if winning_line and winner_symbol:
            print(f"Winning line: {winning_line} ({winner_symbol})")
        
        print(f"Game {game_id} completed.\n")
    
    def send_ack(self, original_message):
        """Send ACK message."""
        if hasattr(self.netSystem, 'msg_system') and self.netSystem.msg_system:
            self.netSystem.msg_system.send_ack(original_message)
    
    def handle_duplicate_move(self, game_id, turn):
        """Check for duplicate moves (idempotency)."""
        if game_id not in self.active_games:
            return False
        
        game = self.active_games[game_id]
        return turn < game['turn_number']

    def get_active_games(self):
        """Get list of active games."""
        active = []
        current_time = time.time()
        
        for game_id, game in self.active_games.items():
            if game['status'] == 'active':
                # Check for timeout (15 minutes)
                if current_time - game['last_move'] > 900:  # 15 minutes
                    game['status'] = 'timeout'
                    continue
                
                active.append({
                    'game_id': game_id,
                    'players': game['players'],
                    'current_turn': game['current_turn'],
                    'turn_number': game['turn_number'],
                    'created': game['created'],
                    'last_move': game['last_move']
                })
        
        return active
    
    def get_game_invites(self):
        """Get list of pending game invitations."""
        return list(self.game_invites.items())
    
    def timeout_inactive_games(self):
        """Mark inactive games as timed out."""
        current_time = time.time()
        timeout_threshold = 900  # 15 minutes
        
        for game_id, game in self.active_games.items():
            if game['status'] == 'active' and current_time - game['last_move'] > timeout_threshold:
                game['status'] = 'timeout'
                print(f"⏰ Game {game_id} timed out due to inactivity")
    
    def get_game_state(self, game_id):
        """Get complete game state."""
        if game_id in self.active_games:
            return self.active_games[game_id].copy()
        elif game_id in self.game_invites:
            return {'status': 'invited', 'invite': self.game_invites[game_id]}
        else:
            return None
    
    def forfeit_game(self, game_id):
        """Forfeit an active game."""
        if game_id not in self.active_games:
            print(f"❌ Game {game_id} not found")
            return False
        
        game = self.active_games[game_id]
        if game['status'] != 'active':
            print(f"❌ Game {game_id} is not active")
            return False
        
        user_id = getattr(self.netSystem.msg_system, 'user_id', 'unknown@127.0.0.1')
        
        # Find opponent
        opponent = None
        for player in game['players']:
            if player != user_id:
                opponent = player
                break
        
        if opponent:
            # Send forfeit result
            forfeit_result = {
                'result': 'FORFEIT',
                'winning_line': None,
                'winner_symbol': None
            }
            self.send_game_result(game_id, opponent, forfeit_result)
        
        game['status'] = 'forfeited'
        print(f"🏃 You forfeited game {game_id}")
        return True

    def simulate_file_packet_loss(self):  # For testing
        pass