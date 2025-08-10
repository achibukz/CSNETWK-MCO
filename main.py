import threading
import time
import random
from network_System import networkSystem
from msg_System import msgSystem
from file_game import fileGameSystem
from grp_ui import groupUISystem
from vars import *

class LSNPClient:
    def __init__(self, user_id, display_name, port, verbose=False):
        self.user_id = user_id
        self.display_name = display_name
        self.verbose = verbose
        self.listen_port = port
        
        self.networkSystem = networkSystem(port, verbose=verbose)
        self.fileGameSystem = fileGameSystem(self.networkSystem)
        self.msgSystem = msgSystem(self.networkSystem, self.fileGameSystem)
        self.groupUISystem = groupUISystem(
            self.networkSystem, 
            self.msgSystem, 
            self.fileGameSystem
        )
        
        # Set up cross-references for proper message routing
        self.networkSystem.set_msg_system(self.msgSystem)
        self.networkSystem.set_file_game_system(self.fileGameSystem)
        
    def start(self):
        # Start network listener
        self.networkSystem.start_listener()
        time.sleep(0.5)
        self.msgSystem.create_profile(self.user_id, self.display_name, "Online and ready!")

        # Start periodic PROFILE broadcasting
        self.msgSystem.start_ping_broadcast()

        # Wait a moment for initial messages to settle
        time.sleep(1)

        # Start UI
        while True:
            print("\n=== LSNP Client Menu ===")
            print("1. Send POST")
            print("2. Send HELLO")
            print("3. Send DM")
            print("4. Toggle verbose mode")
            print("5. Show known clients")
            print("6. Show known peers and their display names")
            print("7. Show all valid posts")
            print("8. Show all DMs")
            print("9. Test message crafting")
            print("10. Follow user")
            print("11. Unfollow user")
            print("12. Show following/followers")
            print("13. Edit profile")
            print("14. Like/Unlike a post")
            print("15. Show token validation stats")
            print("16. Show valid messages log")
            print("17. Revoke a token")
            print("18. 🎮 Tic-Tac-Toe Game")
            print("19. Send File Offer")
            print("20. Show Pending File Offers")
            print("21. 👥 Create Group")
            print("22. 👥 Update Group")
            print("23. 👥 Send Group Message")
            print("24. 👥 Show My Groups")
            print("25. 👥 Show Group Members")
            print("26. 👥 Show Group Messages")
            print("27. Quit")

            choice = input("Enter choice: ").strip()

            if choice == "1":
                content = input("Enter post content: ")
                self.msgSystem.send_post(content)

            elif choice == "2":
                self.send_hello("", 0)  # Parameters not used anymore since it's a broadcast

            elif choice == "3":
                to_user = input("Enter recipient user_id (e.g., user@127.0.0.1): ").strip()
                content = input("Enter DM content: ")
                if to_user and content:
                    self.msgSystem.send_dm(to_user, content)

            elif choice == "4":
                self.networkSystem.toggle_verbose_mode()
                print("Verbose mode is now", "ON" if self.networkSystem.verbose else "OFF")

            elif choice == "5":
                print("Known clients:")
                unique_clients = self.networkSystem.get_unique_clients()
                if unique_clients:
                    for ip, port in unique_clients:
                        print(f"  - {ip}:{port}")
                else:
                    print("  No known clients yet")
                    
                if self.networkSystem.verbose:
                    print("\nAll client entries (including duplicates):")
                    for ip, port in self.networkSystem.known_clients:
                        print(f"    - {ip}:{port}")

            elif choice == "6":
                self.show_known_peers()

            elif choice == "7":
                self.show_all_posts()

            elif choice == "8":
                self.show_all_dms()

            elif choice == "9":
                self.test_message_crafting()

            elif choice == "10":
                self.follow_user()

            elif choice == "11":
                self.unfollow_user()

            elif choice == "12":
                self.show_following_info()

            elif choice == "13":
                self.edit_profile()

            elif choice == "14":
                self.like_post()

            elif choice == "15":
                self.show_token_validation_stats()

            elif choice == "16":
                self.show_valid_messages_log()

            elif choice == "17":
                self.revoke_token_manually()

            elif choice == "18":
                self.tic_tac_toe_menu()

            elif choice == "19":
                self.fileGameSystem.offer_file()

            elif choice == "20":
                print("\n=== Pending File Offers ===")
                pending_offers = self.show_pending_file_offers()
                if pending_offers:
                    for offer in pending_offers:
                        print(f"  - {offer['FILENAME']} from {offer['FROM']} (ID: {offer['FILEID']})")
                else:
                    print("No pending file offers.")

            elif choice == "21":
                self.create_group()

            elif choice == "22":
                self.update_group()

            elif choice == "23":
                self.send_group_message()

            elif choice == "24":
                self.show_my_groups()

            elif choice == "25":
                self.show_group_members()

            elif choice == "26":
                self.show_group_messages()

            elif choice == "27":
                print("Exiting...")
                break

            else:
                print("Invalid choice. Try again.")

            time.sleep(0.5)

    def show_known_peers(self):
        """Show list of known peers and their display names."""
        print("\n=== Known Peers ===")
        peers = self.msgSystem.get_known_peers()
        if peers:
            for user_id, info in peers.items():
                display_name = info.get('display_name', user_id)
                status = info.get('status', 'Unknown')
                print(f"  - {display_name} ({user_id}) - {status}")
        else:
            print("  No known peers yet")

    def show_all_posts(self):
        """Show all valid posts."""
        print("\n=== All Valid Posts ===")
        # Clean up any duplicates first
        post_count = self.msgSystem.clear_duplicate_posts()
        posts = self.msgSystem.get_all_posts()
        
        if posts:
            for post in posts:
                user_id = post.get('USER_ID', 'Unknown')
                content = post.get('CONTENT', 'No content')
                timestamp = post.get('TIMESTAMP', 'No timestamp')
                display_name = self.msgSystem.get_display_name(user_id)
                print(f"  [{display_name}] {content} (at {timestamp})")
        else:
            print("  No posts available")

    def show_all_dms(self):
        """Show all DMs."""
        print("\n=== All Direct Messages ===")
        dms = self.msgSystem.get_all_dms()
        if dms:
            for dm in dms:
                from_user = dm.get('FROM', 'Unknown')
                content = dm.get('CONTENT', 'No content')
                timestamp = dm.get('TIMESTAMP', 'No timestamp')
                display_name = self.msgSystem.get_display_name(from_user)
                print(f"  From {display_name}: {content} (at {timestamp})")
        else:
            print("  No DMs available")

    def test_message_crafting(self):
        """Test suite for crafting and parsing LSNP messages."""
        print("\n=== Message Crafting Test Suite ===")
        print("1. Test PROFILE message")
        print("2. Test POST message") 
        print("3. Test DM message")
        print("4. Test HELLO message")
        print("5. Back to main menu")
        
        choice = input("Enter test choice: ").strip()
        
        if choice == "1":
            self.test_profile_message()
        elif choice == "2":
            self.test_post_message()
        elif choice == "3":
            self.test_dm_message()
        elif choice == "4":
            self.test_hello_message()

    def test_profile_message(self):
        """Test PROFILE message crafting."""
        message = {
            "TYPE": MSG_PROFILE,
            "USER_ID": self.user_id,
            "DISPLAY_NAME": self.display_name,
            "STATUS": "Testing LSNP!",
            "BROADCAST": True
        }
        lsnp_format = self.networkSystem._dict_to_lsnp(message)
        print("LSNP PROFILE Message:")
        print(lsnp_format)
        
        # Test parsing back
        parsed = self.networkSystem._lsnp_to_dict(lsnp_format)
        print("Parsed back to dict:")
        print(parsed)

    def test_post_message(self):
        """Test POST message crafting."""
        content = "This is a test post!"
        timestamp = int(time.time())
        message_id = f"{random.getrandbits(64):016x}"
        
        message = {
            "TYPE": MSG_POST,
            "USER_ID": self.user_id,
            "CONTENT": content,
            "TTL": 3600,
            "MESSAGE_ID": message_id,
            "TOKEN": f"{self.user_id}|{timestamp + 3600}|{SCOPE_BROADCAST}",
            "TIMESTAMP": timestamp,
            "BROADCAST": True
        }
        lsnp_format = self.networkSystem._dict_to_lsnp(message)
        print("LSNP POST Message:")
        print(lsnp_format)

    def test_dm_message(self):
        """Test DM message crafting."""
        to_user = input("Enter recipient user_id: ").strip()
        content = input("Enter DM content: ").strip()
        timestamp = int(time.time())
        message_id = f"{random.getrandbits(64):016x}"
        
        message = {
            "TYPE": MSG_DM,
            "FROM": self.user_id,
            "TO": to_user,
            "CONTENT": content,
            "TIMESTAMP": timestamp,
            "MESSAGE_ID": message_id,
            "TOKEN": f"{self.user_id}|{timestamp + 3600}|{SCOPE_CHAT}"
        }
        lsnp_format = self.networkSystem._dict_to_lsnp(message)
        print("LSNP DM Message:")
        print(lsnp_format)

    def test_hello_message(self):
        """Test HELLO message crafting."""
        message = {
            "TYPE": "HELLO",
            "DATA": f"{self.display_name} is online",
            "USER_ID": self.user_id,
            "DISPLAY_NAME": self.display_name,
            "LISTEN_PORT": self.listen_port,
            "BROADCAST": True
        }
        lsnp_format = self.networkSystem._dict_to_lsnp(message)
        print("LSNP HELLO Message:")
        print(lsnp_format)

    def follow_user(self):
        """Follow a user."""
        print("\n=== Follow User ===")
        peers = self.msgSystem.get_known_peers()
        if not peers:
            print("No known peers to follow.")
            return
        
        print("Available peers:")
        for i, (user_id, info) in enumerate(peers.items(), 1):
            display_name = info.get('display_name', user_id)
            following_status = "✓ Following" if self.msgSystem.is_following(user_id) else ""
            print(f"  {i}. {display_name} ({user_id}) {following_status}")
        
        try:
            choice = input("\nEnter number to follow (or user_id): ").strip()
            if choice.isdigit():
                choice_num = int(choice) - 1
                user_ids = list(peers.keys())
                if 0 <= choice_num < len(user_ids):
                    target_user = user_ids[choice_num]
                else:
                    print("Invalid selection.")
                    return
            else:
                target_user = choice
            
            if target_user == self.user_id:
                print("You cannot follow yourself.")
                return
                
            if self.msgSystem.is_following(target_user):
                print(f"You are already following {self.msgSystem.get_display_name(target_user)}.")
                return
            
            self.msgSystem.send_follow(target_user)
            
        except ValueError:
            print("Invalid input.")

    def unfollow_user(self):
        """Unfollow a user."""
        print("\n=== Unfollow User ===")
        following_list = self.msgSystem.get_following_list()
        if not following_list:
            print("You are not following anyone.")
            return
        
        print("Users you are following:")
        for i, user_id in enumerate(following_list, 1):
            display_name = self.msgSystem.get_display_name(user_id)
            print(f"  {i}. {display_name} ({user_id})")
        
        try:
            choice = input("\nEnter number to unfollow (or user_id): ").strip()
            if choice.isdigit():
                choice_num = int(choice) - 1
                if 0 <= choice_num < len(following_list):
                    target_user = following_list[choice_num]
                else:
                    print("Invalid selection.")
                    return
            else:
                target_user = choice
            
            if not self.msgSystem.is_following(target_user):
                print(f"You are not following {target_user}.")
                return
            
            self.msgSystem.send_unfollow(target_user)
            
        except ValueError:
            print("Invalid input.")

    def show_following_info(self):
        """Show following and followers information."""
        print("\n=== Following & Followers ===")
        
        # Show who we're following
        following_list = self.msgSystem.get_following_list()
        print(f"\n📤 Following ({len(following_list)} users):")
        if following_list:
            for user_id in following_list:
                display_name = self.msgSystem.get_display_name(user_id)
                print(f"  - {display_name} ({user_id})")
        else:
            print("  Not following anyone yet.")
        
        # Show who's following us
        followers_list = self.msgSystem.get_followers_list()
        print(f"\n📥 Followers ({len(followers_list)} users):")
        if followers_list:
            for user_id in followers_list:
                display_name = self.msgSystem.get_display_name(user_id)
                print(f"  - {display_name} ({user_id})")
        else:
            print("  No followers yet.")

    def edit_profile(self):
        """Edit user profile (display name, status, avatar)."""
        print("\n=== Edit Profile ===")
        print(f"Current profile:")
        print(f"  User ID: {self.user_id}")
        print(f"  Display Name: {self.display_name}")
        print(f"  Status: {getattr(self.msgSystem, 'status', 'Online and ready!')}")
        
        print("\nWhat would you like to edit?")
        print("1. Display Name")
        print("2. Status")
        print("3. Avatar (profile picture)")
        print("4. Update all")
        print("5. Cancel")
        
        choice = input("Enter choice: ").strip()
        
        new_display_name = self.display_name
        new_status = getattr(self.msgSystem, 'status', 'Online and ready!')
        avatar_path = None
        
        if choice == "1":
            new_display_name = input(f"Enter new display name (current: {self.display_name}): ").strip()
            if not new_display_name:
                new_display_name = self.display_name
                
        elif choice == "2":
            new_status = input(f"Enter new status (current: {new_status}): ").strip()
            if not new_status:
                new_status = getattr(self.msgSystem, 'status', 'Online and ready!')
                
        elif choice == "3":
            avatar_path = input("Enter path to avatar image (leave empty to remove avatar): ").strip()
            if avatar_path and not avatar_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                print("Warning: File doesn't have a common image extension")
                
        elif choice == "4":
            new_display_name = input(f"Enter new display name (current: {self.display_name}): ").strip()
            if not new_display_name:
                new_display_name = self.display_name
                
            new_status = input(f"Enter new status (current: {new_status}): ").strip()
            if not new_status:
                new_status = getattr(self.msgSystem, 'status', 'Online and ready!')
                
            avatar_path = input("Enter path to avatar image (leave empty for no change): ").strip()
            if avatar_path and not avatar_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                print("Warning: File doesn't have a common image extension")
                
        elif choice == "5":
            print("Profile edit cancelled.")
            return
        else:
            print("Invalid choice.")
            return
        
        # Update profile
        try:
            # Update local attributes
            self.display_name = new_display_name
            
            # Create and broadcast updated profile
            self.msgSystem.create_profile(self.user_id, new_display_name, new_status, avatar_path)
            
            print("✅ Profile updated successfully!")
            print(f"  Display Name: {new_display_name}")
            print(f"  Status: {new_status}")
            if avatar_path:
                print(f"  Avatar: {avatar_path}")
                
        except Exception as e:
            print(f"❌ Failed to update profile: {e}")

    def like_post(self):
        """Like or unlike a post."""
        print("\n=== Like/Unlike Post ===")
        
        # Show available posts
        posts = self.msgSystem.get_all_posts()
        if not posts:
            print("No posts available to like.")
            return
        
        print("Available posts:")
        for i, post in enumerate(posts, 1):
            user_id = post.get('USER_ID', 'Unknown')
            content = post.get('CONTENT', 'No content')
            timestamp = post.get('TIMESTAMP', 'No timestamp')
            display_name = self.msgSystem.get_display_name(user_id)
            print(f"  {i}. [{display_name}] {content[:50]}{'...' if len(content) > 50 else ''}")
        
        try:
            choice = input("\nEnter post number to like/unlike: ").strip()
            if not choice.isdigit():
                print("Invalid input.")
                return
                
            post_index = int(choice) - 1
            if post_index < 0 or post_index >= len(posts):
                print("Invalid post number.")
                return
            
            selected_post = posts[post_index]
            post_user = selected_post.get('USER_ID')
            post_timestamp = selected_post.get('TIMESTAMP')
            
            if post_user == self.user_id:
                print("You cannot like your own post.")
                return
            
            action = input("Enter action (LIKE/UNLIKE) [default: LIKE]: ").strip().upper()
            if action not in ['LIKE', 'UNLIKE']:
                action = 'LIKE'
            
            self.msgSystem.send_like(post_user, post_timestamp, action)
            
        except ValueError:
            print("Invalid input.")
        except Exception as e:
            print(f"Error: {e}")

    def send_hello(self, target_ip, target_port):
        message = {
            "TYPE": "HELLO",
            "BROADCAST": True,
            "DATA": f"{self.display_name} is online",
            "USER_ID": self.user_id,
            "DISPLAY_NAME": self.display_name,
            "LISTEN_PORT": self.listen_port
        }
        self.networkSystem.send_message(message)
        print(f"[HELLO] Broadcasted presence to network")

    def show_token_validation_stats(self):
        """Show token validation statistics."""
        print("\n=== Token Validation Statistics ===")
        stats = self.msgSystem.get_token_validation_stats()
        
        print(f"Total validations: {stats['total']}")
        print(f"Valid tokens: {stats['valid']}")
        print(f"Invalid tokens: {stats['invalid']}")
        print(f"Success rate: {stats['success_rate']}%")
        
        if stats['total'] > 0:
            print(f"\nRevoked tokens: {len(self.msgSystem.revoked_tokens)}")
            print(f"Valid messages stored: {len(self.msgSystem.valid_messages)}")

    def show_valid_messages_log(self):
        """Show log of all messages with valid tokens."""
        print("\n=== Valid Messages Log ===")
        valid_messages = self.msgSystem.get_valid_messages()
        
        if not valid_messages:
            print("No valid messages recorded yet.")
            return
        
        print(f"Showing last {min(10, len(valid_messages))} valid messages:")
        for entry in valid_messages[-10:]:
            message = entry['message']
            timestamp = entry['timestamp']
            validation_info = entry.get('validation_info', {})
            
            msg_type = message.get('TYPE', 'Unknown')
            user_id = message.get('USER_ID') or message.get('FROM', 'Unknown')
            scope = validation_info.get('scope', 'Unknown')
            
            # Format timestamp
            import datetime
            time_str = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
            
            print(f"  [{time_str}] {msg_type} from {user_id} (scope: {scope})")

    def revoke_token_manually(self):
        """Manually revoke a token."""
        print("\n=== Revoke Token ===")
        print("1. Revoke token locally only")
        print("2. Revoke token and broadcast revocation")
        
        revoke_choice = input("Enter choice: ").strip()
        
        print("\nEnter a token to revoke (format: user@ip|timestamp|scope):")
        token = input("Token: ").strip()
        
        if not token:
            print("No token provided.")
            return
        
        # Validate token format
        try:
            parts = token.split('|')
            if len(parts) != 3:
                print("Invalid token format. Expected: user@ip|timestamp|scope")
                return
        except:
            print("Invalid token format.")
            return
        
        reason = input("Reason for revocation (optional): ").strip() or "Manual revocation"
        
        if revoke_choice == "1":
            self.msgSystem.revoke_token(token, reason)
            print(f"✅ Token revoked locally!")
        elif revoke_choice == "2":
            self.msgSystem.send_revoke_message(token, reason)
            print(f"✅ Token revoked and revocation broadcasted!")
        else:
            print("Invalid choice.")
            return
            
        print(f"Reason: {reason}")

    def tic_tac_toe_menu(self):
        """Tic-Tac-Toe game management menu."""
        while True:
            print("\n🎮 === Tic-Tac-Toe Game Menu ===")
            print("1. Invite someone to play")
            print("2. Show game invitations")
            print("3. Accept game invitation")
            print("4. Show active games")
            print("5. Make a move")
            print("6. Display game board")
            print("7. Forfeit game")
            print("8. Back to main menu")
            
            choice = input("Enter choice: ").strip()
            
            if choice == "1":
                self.invite_to_game()
            elif choice == "2":
                self.show_game_invites()
            elif choice == "3":
                self.accept_game_invitation()
            elif choice == "4":
                self.show_active_games()
            elif choice == "5":
                self.make_game_move()
            elif choice == "6":
                self.display_game_board()
            elif choice == "7":
                self.forfeit_game()
            elif choice == "8":
                break
            else:
                print("Invalid choice. Try again.")
            
            time.sleep(0.5)

    def invite_to_game(self):
        """Invite a user to play Tic-Tac-Toe."""
        print("\n🎮 === Invite to Tic-Tac-Toe ===")
        peers = self.msgSystem.get_known_peers()
        if not peers:
            print("No known peers to invite.")
            return
        
        print("Available peers:")
        for i, (user_id, info) in enumerate(peers.items(), 1):
            display_name = info.get('display_name', user_id)
            print(f"  {i}. {display_name} ({user_id})")
        
        try:
            choice = input("\nEnter number to invite (or user_id): ").strip()
            if choice.isdigit():
                choice_num = int(choice) - 1
                user_ids = list(peers.keys())
                if 0 <= choice_num < len(user_ids):
                    target_user = user_ids[choice_num]
                else:
                    print("Invalid selection.")
                    return
            else:
                target_user = choice
            
            if target_user == self.user_id:
                print("You cannot play against yourself.")
                return
            
            # Choose symbol
            symbol = input("Choose your symbol (X/O) [default: X]: ").strip().upper()
            if symbol not in ['X', 'O']:
                symbol = 'X'
            
            game_id = self.fileGameSystem.invite_to_game(target_user, symbol)
            print(f"✅ Game invitation sent! Game ID: {game_id}")
            
        except ValueError:
            print("Invalid input.")
        except Exception as e:
            print(f"Error: {e}")

    def show_game_invites(self):
        """Show pending game invitations."""
        print("\n🎮 === Game Invitations ===")
        invites = self.fileGameSystem.get_game_invites()
        
        if not invites:
            print("No pending game invitations.")
            return
        
        for game_id, invite in invites:
            from_user = invite['from']
            symbol = invite['symbol']
            our_symbol = "O" if symbol == "X" else "X"
            display_name = self.msgSystem.get_display_name(from_user)
            
            print(f"Game {game_id}:")
            print(f"  From: {display_name} ({from_user})")
            print(f"  Their symbol: {symbol}")
            print(f"  Your symbol: {our_symbol}")
            print()

    def accept_game_invitation(self):
        """Accept a game invitation."""
        print("\n🎮 === Accept Game Invitation ===")
        invites = self.fileGameSystem.get_game_invites()
        
        if not invites:
            print("No pending game invitations.")
            return
        
        print("Pending invitations:")
        for i, (game_id, invite) in enumerate(invites, 1):
            from_user = invite['from']
            display_name = self.msgSystem.get_display_name(from_user)
            symbol = invite['symbol']
            our_symbol = "O" if symbol == "X" else "X"
            print(f"  {i}. Game {game_id} from {display_name} (You: {our_symbol})")
        
        try:
            choice = input("\nEnter number to accept (or game_id): ").strip()
            if choice.isdigit():
                choice_num = int(choice) - 1
                if 0 <= choice_num < len(invites):
                    game_id, invite = invites[choice_num]
                else:
                    print("Invalid selection.")
                    return
            else:
                game_id = choice
                # Find invite
                invite = None
                for gid, inv in invites:
                    if gid == game_id:
                        invite = inv
                        break
                if not invite:
                    print(f"Game {game_id} not found in invitations.")
                    return
            
            if self.fileGameSystem.accept_game_invite(game_id, invite['from']):
                print(f"✅ Game {game_id} accepted!")
            else:
                print(f"❌ Failed to accept game {game_id}")
                
        except ValueError:
            print("Invalid input.")
        except Exception as e:
            print(f"Error: {e}")

    def show_active_games(self):
        """Show active games."""
        print("\n🎮 === Active Games ===")
        games = self.fileGameSystem.get_active_games()
        
        if not games:
            print("No active games.")
            return
        
        for game in games:
            game_id = game['game_id']
            players = game['players']
            current_turn = game['current_turn']
            turn_number = game['turn_number']
            
            print(f"Game {game_id}:")
            print(f"  Players: {players}")
            print(f"  Current turn: {current_turn}")
            print(f"  Turn number: {turn_number}")
            
            user_id = self.user_id
            if user_id in players:
                our_symbol = players[user_id]
                if current_turn == our_symbol:
                    print(f"  👈 Your turn! ({our_symbol})")
                else:
                    print(f"  ⏳ Waiting for opponent ({current_turn})")
            print()

    def make_game_move(self):
        """Make a move in an active game."""
        print("\n🎮 === Make Game Move ===")
        games = self.fileGameSystem.get_active_games()
        
        if not games:
            print("No active games.")
            return
        
        # Show games where it's our turn
        our_turn_games = []
        user_id = self.user_id
        
        for game in games:
            game_id = game['game_id']
            players = game['players']
            current_turn = game['current_turn']
            
            if user_id in players and players[user_id] == current_turn:
                our_turn_games.append(game)
        
        if not our_turn_games:
            print("No games where it's your turn.")
            print("\nAll active games:")
            for game in games:
                print(f"  Game {game['game_id']}: Waiting for {game['current_turn']}")
            return
        
        print("Games where it's your turn:")
        for i, game in enumerate(our_turn_games, 1):
            print(f"  {i}. Game {game['game_id']}")
        
        try:
            choice = input("\nEnter game number (or game_id): ").strip()
            if choice.isdigit():
                choice_num = int(choice) - 1
                if 0 <= choice_num < len(our_turn_games):
                    game = our_turn_games[choice_num]
                    game_id = game['game_id']
                else:
                    print("Invalid selection.")
                    return
            else:
                game_id = choice
            
            # Show current board
            self.fileGameSystem.display_game_board(game_id)
            
            # Get move
            print("Choose your move (position 0-8):")
            print("0 | 1 | 2")
            print("3 | 4 | 5")
            print("6 | 7 | 8")
            
            position = input("Enter position: ").strip()
            if not position.isdigit():
                print("Invalid position. Must be a number 0-8.")
                return
            
            position = int(position)
            if position < 0 or position > 8:
                print("Invalid position. Must be 0-8.")
                return
            
            if self.fileGameSystem.make_move(game_id, position):
                print(f"✅ Move made at position {position}!")
            else:
                print(f"❌ Failed to make move")
                
        except ValueError:
            print("Invalid input.")
        except Exception as e:
            print(f"Error: {e}")

    def display_game_board(self):
        """Display a game board."""
        print("\n🎮 === Display Game Board ===")
        games = self.fileGameSystem.get_active_games()
        
        if not games:
            print("No active games.")
            return
        
        print("Active games:")
        for i, game in enumerate(games, 1):
            print(f"  {i}. Game {game['game_id']}")
        
        try:
            choice = input("\nEnter game number (or game_id): ").strip()
            if choice.isdigit():
                choice_num = int(choice) - 1
                if 0 <= choice_num < len(games):
                    game_id = games[choice_num]['game_id']
                else:
                    print("Invalid selection.")
                    return
            else:
                game_id = choice
            
            self.fileGameSystem.display_game_board(game_id)
            
        except ValueError:
            print("Invalid input.")
        except Exception as e:
            print(f"Error: {e}")

    def forfeit_game(self):
        """Forfeit an active game."""
        print("\n🎮 === Forfeit Game ===")
        games = self.fileGameSystem.get_active_games()
        
        if not games:
            print("No active games.")
            return
        
        print("Active games:")
        for i, game in enumerate(games, 1):
            print(f"  {i}. Game {game['game_id']}")
        
        try:
            choice = input("\nEnter game number to forfeit (or game_id): ").strip()
            if choice.isdigit():
                choice_num = int(choice) - 1
                if 0 <= choice_num < len(games):
                    game_id = games[choice_num]['game_id']
                else:
                    print("Invalid selection.")
                    return
            else:
                game_id = choice
            
            confirm = input(f"Are you sure you want to forfeit game {game_id}? (y/N): ").strip().lower()
            if confirm == 'y':
                if self.fileGameSystem.forfeit_game(game_id):
                    print(f"✅ Game {game_id} forfeited")
                else:
                    print(f"❌ Failed to forfeit game {game_id}")
            else:
                print("Forfeit cancelled.")
                
        except ValueError:
            print("Invalid input.")
        except Exception as e:
            print(f"Error: {e}")

    def show_pending_file_offers(self):
        """Show and handle pending file offers."""
        offers = getattr(self.fileGameSystem, "pending_file_offers", {})
        if not offers:
            print("No pending file offers.")
            return

        print("\n=== Pending File Offers ===")
        for i, (file_id, offer) in enumerate(offers.items(), 1):
            from_user = offer.get("from_user", "Unknown")
            filename = offer.get("filename", offer.get("file_path", "Unknown"))
            filesize = offer.get("filesize", "Unknown")
            description = offer.get("description", "")
            status = offer.get("status", "PENDING")
            print(f"{i}. From: {from_user}, File: {filename} ({filesize} bytes), Desc: {description}, Status: {status}, ID: {file_id}")

        choice = input("Enter number to accept (or blank to cancel): ").strip()
        if not choice.isdigit():
            print("Cancelled.")
            return

        idx = int(choice) - 1
        if idx < 0 or idx >= len(offers):
            print("Invalid selection.")
            return

        file_id = list(offers.keys())[idx]
        offer = offers[file_id]
        from_user = offer.get("from_user")
        # Call your accept logic here, e.g.:
        self.msgSystem.accept_file_offer(file_id, from_user)
        print(f"Accepted file offer {file_id} from {from_user}.")

    # ============ GROUP MANAGEMENT METHODS ============

    def create_group(self):
        """Create a new group."""
        print("\n=== Create Group ===")
        
        group_id = input("Enter group ID (alphanumeric): ").strip()
        if not group_id:
            print("Group ID cannot be empty.")
            return
        
        group_name = input("Enter group name: ").strip()
        if not group_name:
            print("Group name cannot be empty.")
            return
        
        print("\nAdd members to the group:")
        print("Available users:")
        peers = self.msgSystem.get_known_peers()
        if not peers:
            print("No known peers available.")
            return
        
        for i, (user_id, info) in enumerate(peers.items(), 1):
            display_name = info.get('display_name', user_id)
            print(f"  {i}. {display_name} ({user_id})")
        
        members = [self.user_id]  # Creator is always a member
        
        while True:
            choice = input("\nEnter user number to add (or 'done' to finish): ").strip().lower()
            if choice == 'done':
                break
            
            try:
                idx = int(choice) - 1
                user_list = list(peers.keys())
                if 0 <= idx < len(user_list):
                    selected_user = user_list[idx]
                    if selected_user not in members:
                        members.append(selected_user)
                        display_name = peers[selected_user].get('display_name', selected_user)
                        print(f"✅ Added {display_name}")
                    else:
                        print("User already in group.")
                else:
                    print("Invalid user number.")
            except ValueError:
                print("Invalid input.")
        
        if len(members) < 2:
            print("A group must have at least 2 members.")
            return
        
        success = self.msgSystem.create_group(group_id, group_name, members)
        if success:
            print(f"📢 Group '{group_name}' created successfully!")

    def update_group(self):
        """Update group membership."""
        print("\n=== Update Group ===")
        
        groups = self.msgSystem.get_user_groups()
        if not groups:
            print("You are not a member of any groups.")
            return
        
        print("Your groups:")
        for i, group in enumerate(groups, 1):
            print(f"  {i}. {group['name']} ({group['group_id']}) - {group['member_count']} members")
        
        try:
            choice = input("\nSelect group number: ").strip()
            idx = int(choice) - 1
            if idx < 0 or idx >= len(groups):
                print("Invalid group number.")
                return
            
            selected_group = groups[idx]
            group_id = selected_group['group_id']
            
            # Check if user is the creator or has permission to update
            if self.user_id != selected_group['creator']:
                print(f"❌ Only the group creator ({selected_group['creator']}) can update this group.")
                return
            
            print(f"\nUpdating group: {selected_group['name']}")
            print("1. Add members")
            print("2. Remove members")
            print("3. Both")
            
            action = input("Choose action: ").strip()
            
            add_members = []
            remove_members = []
            
            if action in ['1', '3']:
                # Add members
                peers = self.msgSystem.get_known_peers()
                current_members = selected_group['members']
                available_users = {uid: info for uid, info in peers.items() if uid not in current_members}
                
                if available_users:
                    print("\nAvailable users to add:")
                    for i, (user_id, info) in enumerate(available_users.items(), 1):
                        display_name = info.get('display_name', user_id)
                        print(f"  {i}. {display_name} ({user_id})")
                    
                    while True:
                        choice = input("Enter user number to add (or 'done'): ").strip().lower()
                        if choice == 'done':
                            break
                        try:
                            idx = int(choice) - 1
                            user_list = list(available_users.keys())
                            if 0 <= idx < len(user_list):
                                add_members.append(user_list[idx])
                                print(f"✅ Will add {available_users[user_list[idx]].get('display_name', user_list[idx])}")
                            else:
                                print("Invalid user number.")
                        except ValueError:
                            print("Invalid input.")
                else:
                    print("No available users to add.")
            
            if action in ['2', '3']:
                # Remove members (only creator can remove, and can't remove themselves)
                current_members = [m for m in selected_group['members'] if m != self.user_id]
                if current_members:
                    print("\nCurrent members (you can remove):")
                    for i, member in enumerate(current_members, 1):
                        display_name = self.msgSystem.get_display_name(member)
                        print(f"  {i}. {display_name} ({member})")
                    
                    while True:
                        choice = input("Enter member number to remove (or 'done'): ").strip().lower()
                        if choice == 'done':
                            break
                        try:
                            idx = int(choice) - 1
                            if 0 <= idx < len(current_members):
                                remove_members.append(current_members[idx])
                                display_name = self.msgSystem.get_display_name(current_members[idx])
                                print(f"✅ Will remove {display_name}")
                            else:
                                print("Invalid member number.")
                        except ValueError:
                            print("Invalid input.")
                else:
                    print("No members available to remove (group only has creator).")
            
            if add_members or remove_members:
                success = self.msgSystem.update_group(group_id, add_members, remove_members)
                if success:
                    print("✅ Group updated successfully!")
            else:
                print("No changes made.")
                
        except ValueError:
            print("Invalid input.")

    def send_group_message(self):
        """Send a message to a group."""
        print("\n=== Send Group Message ===")
        
        groups = self.msgSystem.get_user_groups()
        if not groups:
            print("You are not a member of any groups.")
            return
        
        print("Your groups:")
        for i, group in enumerate(groups, 1):
            print(f"  {i}. {group['name']} ({group['group_id']}) - {group['member_count']} members")
        
        try:
            choice = input("\nSelect group number: ").strip()
            idx = int(choice) - 1
            if idx < 0 or idx >= len(groups):
                print("Invalid group number.")
                return
            
            selected_group = groups[idx]
            group_id = selected_group['group_id']
            
            content = input(f"\nEnter message for '{selected_group['name']}': ").strip()
            if not content:
                print("Message cannot be empty.")
                return
            
            success = self.msgSystem.send_group_message(group_id, content)
            if success:
                print("📤 Message sent to group!")
                
        except ValueError:
            print("Invalid input.")

    def show_my_groups(self):
        """Show all groups the user belongs to."""
        print("\n=== My Groups ===")
        
        groups = self.msgSystem.get_user_groups()
        if not groups:
            print("You are not a member of any groups.")
            return
        
        for group in groups:
            creator_name = self.msgSystem.get_display_name(group['creator'])
            print(f"\n📁 {group['name']} (ID: {group['group_id']})")
            print(f"   Creator: {creator_name}")
            print(f"   Members: {group['member_count']}")
            
            # Show member names
            member_names = []
            for member in group['members']:
                display_name = self.msgSystem.get_display_name(member)
                if member == group['creator']:
                    member_names.append(f"{display_name} (creator)")
                elif member == self.user_id:
                    member_names.append(f"{display_name} (you)")
                else:
                    member_names.append(display_name)
            
            print(f"   {', '.join(member_names)}")

    def show_group_members(self):
        """Show members of a specific group."""
        print("\n=== Group Members ===")
        
        groups = self.msgSystem.get_user_groups()
        if not groups:
            print("You are not a member of any groups.")
            return
        
        print("Your groups:")
        for i, group in enumerate(groups, 1):
            print(f"  {i}. {group['name']} ({group['group_id']})")
        
        try:
            choice = input("\nSelect group number: ").strip()
            idx = int(choice) - 1
            if idx < 0 or idx >= len(groups):
                print("Invalid group number.")
                return
            
            selected_group = groups[idx]
            print(f"\n👥 Members of '{selected_group['name']}':")
            
            for member in selected_group['members']:
                display_name = self.msgSystem.get_display_name(member)
                role = ""
                if member == selected_group['creator']:
                    role = " (creator)"
                elif member == self.user_id:
                    role = " (you)"
                
                print(f"   • {display_name} ({member}){role}")
                
        except ValueError:
            print("Invalid input.")

    def show_group_messages(self):
        """Show messages for a specific group."""
        print("\n=== Group Messages ===")
        
        groups = self.msgSystem.get_user_groups()
        if not groups:
            print("You are not a member of any groups.")
            return
        
        print("Your groups:")
        for i, group in enumerate(groups, 1):
            print(f"  {i}. {group['name']} ({group['group_id']})")
        
        try:
            choice = input("\nSelect group number: ").strip()
            idx = int(choice) - 1
            if idx < 0 or idx >= len(groups):
                print("Invalid group number.")
                return
            
            selected_group = groups[idx]
            group_id = selected_group['group_id']
            
            messages = self.msgSystem.get_group_messages(group_id)
            print(f"\n💬 Messages in '{selected_group['name']}':")
            
            if not messages:
                print("   No messages yet.")
                return
            
            for msg in messages[-10:]:  # Show last 10 messages
                from_user = msg['from']
                display_name = self.msgSystem.get_display_name(from_user)
                content = msg['content']
                
                # Format timestamp
                timestamp = msg['timestamp']
                import datetime
                dt = datetime.datetime.fromtimestamp(timestamp)
                time_str = dt.strftime('%H:%M:%S')
                
                print(f"   [{time_str}] {display_name}: {content}")
                
        except ValueError:
            print("Invalid input.")

    # ============ END GROUP MANAGEMENT ============

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='LSNP Client')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')
    parser.add_argument('--user-id', required=True, help='User ID (username@ip)')
    parser.add_argument('--display-name', required=True, help='Display name')
    parser.add_argument('--port', type=int, default=LSNP_PORT, help='Port to listen on')
    
    args = parser.parse_args()
    
    client = LSNPClient(args.user_id, args.display_name, args.port, args.verbose)
    client.start()