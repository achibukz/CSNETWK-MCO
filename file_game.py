# Member 3

import mimetypes
import time
import random
import base64
import os
import uuid
from vars import *
class fileGameSystem:
    def __init__(self, netSystem):
        self.netSystem = netSystem
        self.user_id = getattr(self.netSystem.msg_system, 'user_id', 'unknown@127.0.0.1')
        
        # Game state management
        self.active_games = {}  # {game_id: game_data}
        self.game_invites = {}  # {game_id: invite_data}
        self.pending_moves = {}  # {message_id: move_data} for retries
        
        # File transfer management
        self.pending_file_offers = {}   # {file_id: offer_data}
        self.incoming_files = {}        # {file_id: {chunks, metadata}}
        self.outgoing_files = {}        # {file_id: file_info}

    def get_timestamp_str(self):
        """Get formatted timestamp string for logging."""
        # Only show timestamps in verbose mode
        if hasattr(self.netSystem, 'verbose') and self.netSystem.verbose:
            import datetime
            return datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ')
        return ''

    def log_message(self, category, message, show_full=True):
        """Log message in the new clean format."""
        if hasattr(self.netSystem, 'verbose') and self.netSystem.verbose and show_full:
            from datetime import datetime
            timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ')
            print(f"\n{timestamp}{category}: {{")
            # Format the message dictionary nicely
            for key, value in message.items():
                if isinstance(value, str):
                    print(f"\t'{key}': '{value}',")
                else:
                    print(f"\t'{key}': {value},")
            print("}\n")
        elif hasattr(self.netSystem, 'verbose') and self.netSystem.verbose:
            from datetime import datetime
            timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ')
            print(f"{timestamp}{category}: {message}")

    # ===============================
    # FILE TRANSFER METHODS (LSNP COMPLIANT)
    # ===============================
    
    def send_file(self, to_user, file_path, description=""):
        """Send a file offer to another user according to LSNP specs."""
        # Check if file exists in uploads folder or use absolute path
        if not os.path.isabs(file_path):
            # If relative path, check in uploads folder first
            uploads_path = os.path.join("uploads", file_path)
            if os.path.exists(uploads_path):
                file_path = uploads_path
            elif not os.path.exists(file_path):
                # Create uploads folder if it doesn't exist
                os.makedirs("uploads", exist_ok=True)
                raise FileNotFoundError(f"File not found: {file_path}. Please place files in 'uploads' folder.")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Generate file metadata
        file_id = str(uuid.uuid4())[:8]  # 8-character file ID
        filename = os.path.basename(file_path)
        filesize = os.path.getsize(file_path)
        filetype, _ = mimetypes.guess_type(file_path)
        if not filetype:
            filetype = "application/octet-stream"
        
        timestamp = int(time.time())
        ttl = 3600  # 1 hour TTL
        token = f"{self.user_id}|{timestamp + ttl}|{SCOPE_FILE}"
        
        # Create FILE_OFFER message according to LSNP specs
        file_offer_message = {
            "TYPE": MSG_FILE_OFFER,
            "FROM": self.user_id,
            "TO": to_user,
            "FILENAME": filename,
            "FILESIZE": str(filesize),  # String as per specs
            "FILETYPE": filetype,
            "FILEID": file_id,
            "DESCRIPTION": description,
            "TIMESTAMP": str(timestamp),  # String as per specs
            "TOKEN": token
        }
        
        # Store outgoing file info
        self.outgoing_files[file_id] = {
            "file_path": file_path,
            "to_user": to_user,
            "filename": filename,
            "filesize": filesize,
            "filetype": filetype,
            "description": description,
            "status": "OFFERED",
            "timestamp": timestamp,
            "chunks_sent": 0,
            "total_chunks": 0
        }
        
        # Send the offer - resolve target IP from user_id
        target_ip = to_user.split("@")[1] if "@" in to_user else "127.0.0.1"
        target_port = LSNP_PORT
        
        # Try to get more specific peer info if available
        if hasattr(self.netSystem, 'msg_system') and self.netSystem.msg_system:
            peer_info = self.netSystem.msg_system.known_peers.get(to_user)
            if peer_info:
                target_ip = peer_info.get('ip', target_ip)
                target_port = peer_info.get('port', target_port)
        
        self.netSystem.send_message(file_offer_message, target_ip=target_ip, target_port=target_port)
        
        if hasattr(self.netSystem, 'verbose') and self.netSystem.verbose:
            print(f"[FILE] Sent file offer for {filename} to {to_user} (ID: {file_id})")
            print(f"[FILE] File source: {file_path}")
            print(f"[FILE] Target: {target_ip}:{target_port}")
            print(f"[FILE] Use file management menu to start transmission when ready")
        
        return file_id
    
    def handle_file_offer(self, message):
        """Handle incoming FILE_OFFER message according to LSNP specs."""
        file_id = message.get("FILEID")
        from_user = message.get("FROM")
        filename = message.get("FILENAME")
        filesize = message.get("FILESIZE")
        filetype = message.get("FILETYPE")
        description = message.get("DESCRIPTION", "")
        
        # Store the pending offer
        self.pending_file_offers[file_id] = {
            "from_user": from_user,
            "filename": filename,
            "filesize": int(filesize) if filesize else 0,
            "filetype": filetype,
            "description": description,
            "timestamp": message.get("TIMESTAMP"),
            "token": message.get("TOKEN"),
            "status": "PENDING"
        }
        
        # Get display name
        display_name = from_user
        if hasattr(self.netSystem, 'msg_system') and self.netSystem.msg_system:
            display_name = self.netSystem.msg_system.get_display_name(from_user)
        
        # Non-verbose printing as per specs: "User alice is sending you a file do you accept?"
        print(f"User {display_name} is sending you a file do you accept?")
        print(f"📁 File: {filename} ({filesize} bytes)")
        if description:
            print(f"📝 Description: {description}")
        print(f"🆔 File ID: {file_id}")
        
        # Verbose mode additional info
        if hasattr(self.netSystem, 'verbose') and self.netSystem.verbose:
            print(f"[FILE] Received file offer:")
            print(f"  - From: {display_name} ({from_user})")
            print(f"  - File: {filename}")
            print(f"  - Size: {filesize} bytes")
            print(f"  - Type: {filetype}")
            print(f"  - Description: {description}")
            print(f"  - File ID: {file_id}")
            print(f"  - Will be saved to: downloads/{filename}")
    
    def accept_file_offer(self, file_id):
        """Accept a file offer and prepare to receive chunks."""
        if file_id not in self.pending_file_offers:
            print(f"No pending file offer with ID: {file_id}")
            return False
        
        offer = self.pending_file_offers[file_id]
        offer["status"] = "ACCEPTED"
        
        # Initialize incoming file tracking
        self.incoming_files[file_id] = {
            "filename": offer["filename"],
            "filesize": offer["filesize"],
            "filetype": offer["filetype"],
            "from_user": offer["from_user"],
            "chunks": {},
            "total_chunks": 0,
            "received_chunks": 0
        }
        
        # Ensure downloads directory exists
        os.makedirs("downloads", exist_ok=True)
        
        if hasattr(self.netSystem, 'verbose') and self.netSystem.verbose:
            print(f"[FILE] Accepted file offer {file_id} ({offer['filename']}) from {offer['from_user']}")
            print(f"[FILE] File will be saved to: downloads/{offer['filename']}")
        
        # According to LSNP specs, there's no FILE_ACCEPT message
        # The receiver just starts accepting chunks when they arrive
        return True
    
    def reject_file_offer(self, file_id):
        """Reject a file offer."""
        if file_id not in self.pending_file_offers:
            print(f"No pending file offer with ID: {file_id}")
            return False
        
        offer = self.pending_file_offers[file_id]
        del self.pending_file_offers[file_id]
        
        if hasattr(self.netSystem, 'verbose') and self.netSystem.verbose:
            print(f"[FILE] Rejected file offer {file_id} ({offer['filename']}) from {offer['from_user']}")
        
        return True
    
    def send_file_chunks(self, file_id):
        """Send file in chunks after offer is accepted."""
        if file_id not in self.outgoing_files:
            print(f"No outgoing file with ID: {file_id}")
            return False
        
        file_info = self.outgoing_files[file_id]
        file_path = file_info["file_path"]
        to_user = file_info["to_user"]
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
        
        # Read file and split into chunks
        chunk_size = 1024  # 1KB chunks (can be adjusted)
        filesize = file_info["filesize"]
        total_chunks = (filesize + chunk_size - 1) // chunk_size
        
        file_info["total_chunks"] = total_chunks
        
        timestamp = int(time.time())
        ttl = 3600
        token = f"{self.user_id}|{timestamp + ttl}|{SCOPE_FILE}"
        
        with open(file_path, "rb") as f:
            for chunk_index in range(total_chunks):
                chunk_data = f.read(chunk_size)
                if not chunk_data:
                    break
                
                # Encode chunk data in base64
                encoded_data = base64.b64encode(chunk_data).decode('ascii')
                
                # Create FILE_CHUNK message according to LSNP specs
                chunk_message = {
                    "TYPE": MSG_FILE_CHUNK,
                    "FROM": self.user_id,
                    "TO": to_user,
                    "FILEID": file_id,
                    "CHUNK_INDEX": str(chunk_index),  # String as per specs
                    "TOTAL_CHUNKS": str(total_chunks),  # String as per specs
                    "CHUNK_SIZE": str(len(chunk_data)),  # String as per specs
                    "TOKEN": token,
                    "DATA": encoded_data
                }
                
                # Send the chunk - resolve target IP from user_id
                target_ip = to_user.split("@")[1] if "@" in to_user else "127.0.0.1"
                target_port = LSNP_PORT
                
                # Try to get more specific peer info if available
                if hasattr(self.netSystem, 'msg_system') and self.netSystem.msg_system:
                    peer_info = self.netSystem.msg_system.known_peers.get(to_user)
                    if peer_info:
                        target_ip = peer_info.get('ip', target_ip)
                        target_port = peer_info.get('port', target_port)
                
                self.netSystem.send_message(chunk_message, target_ip=target_ip, target_port=target_port)
                file_info["chunks_sent"] += 1
                
                # Small delay to prevent overwhelming the network
                time.sleep(0.01)
        
        file_info["status"] = "SENT"
        
        if hasattr(self.netSystem, 'verbose') and self.netSystem.verbose:
            print(f"[FILE] Sent {total_chunks} chunks for file {file_id} to {to_user}")
        
        return True
    
    def handle_file_chunk(self, message):
        """Handle incoming FILE_CHUNK message according to LSNP specs."""
        file_id = message.get("FILEID")
        chunk_index = int(message.get("CHUNK_INDEX", 0))
        total_chunks = int(message.get("TOTAL_CHUNKS", 0))
        chunk_size = int(message.get("CHUNK_SIZE", 0))
        encoded_data = message.get("DATA", "")
        
        # Check if we have accepted this file
        if file_id not in self.incoming_files:
            # File not accepted, ignore chunks as per specs
            if hasattr(self.netSystem, 'verbose') and self.netSystem.verbose:
                print(f"[FILE] Ignoring chunk for unaccepted file {file_id}")
            return
        
        file_info = self.incoming_files[file_id]
        
        # Decode chunk data
        try:
            chunk_data = base64.b64decode(encoded_data)
        except Exception as e:
            if hasattr(self.netSystem, 'verbose') and self.netSystem.verbose:
                print(f"[FILE] Failed to decode chunk {chunk_index} for file {file_id}: {e}")
            return
        
        # Store chunk
        file_info["chunks"][chunk_index] = chunk_data
        file_info["total_chunks"] = total_chunks
        file_info["received_chunks"] = len(file_info["chunks"])
        
        if hasattr(self.netSystem, 'verbose') and self.netSystem.verbose:
            print(f"[FILE] Received chunk {chunk_index}/{total_chunks-1} for {file_info['filename']}")
        
        # Check if all chunks are received
        if file_info["received_chunks"] == total_chunks:
            self.reconstruct_file(file_id)
    
    def reconstruct_file(self, file_id):
        """Reconstruct file from received chunks."""
        if file_id not in self.incoming_files:
            return False
        
        file_info = self.incoming_files[file_id]
        filename = file_info["filename"]
        total_chunks = file_info["total_chunks"]
        chunks = file_info["chunks"]
        from_user = file_info["from_user"]
        
        # Check if all chunks are present
        missing_chunks = [i for i in range(total_chunks) if i not in chunks]
        if missing_chunks:
            if hasattr(self.netSystem, 'verbose') and self.netSystem.verbose:
                print(f"[FILE] Missing chunks for {filename}: {missing_chunks}")
            return False
        
        # Create downloads directory if it doesn't exist
        downloads_dir = "downloads"
        os.makedirs(downloads_dir, exist_ok=True)
        
        # Reconstruct file
        output_path = os.path.join(downloads_dir, filename)
        try:
            with open(output_path, "wb") as f:
                for i in range(total_chunks):
                    f.write(chunks[i])
            
            # Non-verbose printing as per specs: "File transfer of filename is complete"
            print(f"File transfer of {filename} is complete")
            
            # Verbose mode additional info
            if hasattr(self.netSystem, 'verbose') and self.netSystem.verbose:
                print(f"[FILE] File saved to: {output_path}")
            
            # Send FILE_RECEIVED confirmation
            self.send_file_received(file_id, from_user, "COMPLETE")
            
            # Clean up
            del self.incoming_files[file_id]
            if file_id in self.pending_file_offers:
                del self.pending_file_offers[file_id]
            
            return True
            
        except Exception as e:
            if hasattr(self.netSystem, 'verbose') and self.netSystem.verbose:
                print(f"[FILE] Failed to reconstruct file {filename}: {e}")
            return False
    
    def send_file_received(self, file_id, to_user, status):
        """Send FILE_RECEIVED confirmation according to LSNP specs."""
        timestamp = int(time.time())
        
        # Create FILE_RECEIVED message according to LSNP specs
        received_message = {
            "TYPE": MSG_FILE_RECEIVED,
            "FROM": self.user_id,
            "TO": to_user,
            "FILEID": file_id,
            "STATUS": status,
            "TIMESTAMP": str(timestamp)  # String as per specs
        }
        
        # Send the confirmation - resolve target IP from user_id
        target_ip = to_user.split("@")[1] if "@" in to_user else "127.0.0.1"
        target_port = LSNP_PORT
        
        # Try to get more specific peer info if available
        if hasattr(self.netSystem, 'msg_system') and self.netSystem.msg_system:
            peer_info = self.netSystem.msg_system.known_peers.get(to_user)
            if peer_info:
                target_ip = peer_info.get('ip', target_ip)
                target_port = peer_info.get('port', target_port)
        
        self.netSystem.send_message(received_message, target_ip=target_ip, target_port=target_port)
        
        # No printing for FILE_RECEIVED as per specs
        if hasattr(self.netSystem, 'verbose') and self.netSystem.verbose:
            print(f"[FILE] Sent FILE_RECEIVED confirmation for {file_id} to {to_user}")
            print(f"[FILE] Target: {target_ip}:{target_port}")
    
    def handle_file_received(self, message):
        """Handle incoming FILE_RECEIVED confirmation."""
        file_id = message.get("FILEID")
        status = message.get("STATUS")
        from_user = message.get("FROM")
        
        if file_id in self.outgoing_files:
            self.outgoing_files[file_id]["status"] = f"RECEIVED_{status}"
            
            # No printing for FILE_RECEIVED as per specs
            if hasattr(self.netSystem, 'verbose') and self.netSystem.verbose:
                filename = self.outgoing_files[file_id]["filename"]
                print(f"[FILE] {from_user} confirmed receipt of {filename} with status: {status}")
    
    def get_pending_file_offers(self):
        """Get list of pending file offers."""
        return self.pending_file_offers.copy()
    
    def get_outgoing_files(self):
        """Get list of outgoing files awaiting transmission."""
        return {file_id: info for file_id, info in self.outgoing_files.items() 
                if info.get("status") in ["OFFERED", "READY"]}
    
    def get_file_transfers(self):
        """Get status of ongoing file transfers."""
        transfers = []
        
        # Outgoing files
        for file_id, info in self.outgoing_files.items():
            transfers.append({
                "file_id": file_id,
                "direction": "outgoing",
                "filename": info["filename"],
                "to_user": info["to_user"],
                "status": info["status"],
                "progress": f"{info['chunks_sent']}/{info['total_chunks']}" if info['total_chunks'] > 0 else "0/0"
            })
        
        # Incoming files
        for file_id, info in self.incoming_files.items():
            transfers.append({
                "file_id": file_id,
                "direction": "incoming", 
                "filename": info["filename"],
                "from_user": info["from_user"],
                "status": "receiving",
                "progress": f"{info['received_chunks']}/{info['total_chunks']}" if info['total_chunks'] > 0 else "0/0"
            })
        
        return transfers

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
        
        # Send acceptance message to the inviter
        timestamp = int(time.time())
        message_id = f"{random.getrandbits(64):016x}"
        
        accept_message = {
            "TYPE": MSG_TICTACTOE_ACCEPT,
            "FROM": user_id,
            "TO": invite['from'],
            "GAME_ID": game_id,
            "MESSAGE_ID": message_id,
            "TIMESTAMP": str(timestamp),
            "TOKEN": f"{user_id}|{timestamp + 3600}|{SCOPE_GAME}"
        }
        
        # Send the acceptance message
        self.netSystem.send_message(accept_message)
        print(f"📤 Sent game acceptance to {invite['from']}")
        
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

    def handle_game_accept(self, message):
        """Handle incoming game acceptance."""
        game_id = message.get('GAME_ID')
        from_user = message.get('FROM')
        
        if not all([game_id, from_user]):
            print("❌ Invalid game acceptance message")
            return
        
        # Check if we have this invitation pending (we should be the original inviter)
        user_id = getattr(self.netSystem.msg_system, 'user_id', 'unknown@127.0.0.1')
        
        # Create the game on the inviter's side
        if game_id in self.game_invites:
            invite = self.game_invites[game_id]
            our_symbol = invite['symbol']
            their_symbol = "O" if our_symbol == "X" else "X"
            
            # Initialize game state
            self.active_games[game_id] = {
                'board': [" " for _ in range(9)],
                'players': {
                    user_id: our_symbol,
                    from_user: their_symbol
                },
                'current_turn': "X",  # X always goes first
                'turn_number': 1,
                'status': 'active',
                'created': time.time(),
                'last_move': time.time()
            }
            
            # Remove the invitation
            del self.game_invites[game_id]
            
            # Get display name
            display_name = from_user
            if hasattr(self.netSystem, 'msg_system') and self.netSystem.msg_system:
                display_name = self.netSystem.msg_system.get_display_name(from_user)
            
            print(f"\n🎉 {display_name} accepted your game invitation!")
            print(f"🎮 Game {game_id} started! You are {our_symbol}.")
            
            if our_symbol == "X":
                print("It's your turn! Choose your move (position 0-8):")
                self.display_game_board(game_id)
                print("0 | 1 | 2")
                print("3 | 4 | 5")
                print("6 | 7 | 8")
            else:
                print(f"Waiting for {display_name} to move...")
                self.display_game_board(game_id)
        
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