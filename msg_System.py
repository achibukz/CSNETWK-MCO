# Member 2

import time
import random
from vars import *

class msgSystem:
    def __init__(self, netSystem, fileGameSystem):
        self.netSystem = netSystem
        self.fileGameSystem = fileGameSystem
        self.known_peers = {}  # Store peer information {user_id: {display_name, status, avatar}}
        self.stored_posts = []  # Store valid posts
        self.stored_dms = []    # Store DMs
        self.following = set()  # Users we're following
        self.followers = set()  # Users following us
        self.processed_messages = set()  # Track processed message IDs to prevent duplicates
        self.last_profile_received = {}  # Track last PROFILE message time per user to prevent spam
        self.pending_acks = {}  # Track messages waiting for ACK {message_id: {timestamp, retries, message}}
        self.ack_timeout = 5  # seconds to wait for ACK before retry
        self.acks_sent = 0  # Counter for ACKs sent
        self.acks_received = 0  # Counter for ACKs received
        
        # Like tracking system
        self.post_likes = {}  # Track likes per post {(user_id, timestamp): {likers: set(), count: int}}
        
        # Group Management
        self.groups = {}  # Store groups {group_id: {name, members, creator, created_time}}
        self.group_messages = {}  # Store group messages {group_id: [messages]}
        
        # Enhanced token validation
        self.revoked_tokens = set()  # Store revoked tokens
        self.valid_messages = []  # Store all messages with valid token structure
        self.token_validation_log = []  # Log token validation attempts

    def get_timestamp_str(self):
        """Get formatted timestamp string for logging."""
        # Only show timestamps in verbose mode
        if hasattr(self.netSystem, 'verbose') and self.netSystem.verbose:
            import datetime
            return datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ')
        return ""

    def log_message(self, category, message, show_full=True):
        """Log message in the new clean format."""
        if hasattr(self.netSystem, 'verbose') and self.netSystem.verbose and show_full:
            # Build the entire message as one string for atomic printing
            output_lines = []
            output_lines.append(f"\n{self.get_timestamp_str()}{category}: {{")
            for key, value in message.items():
                if isinstance(value, str):
                    output_lines.append(f"\t'{key}': '{value}',")
                else:
                    output_lines.append(f"\t'{key}': {value},")
            output_lines.append("}\n")
            # Print as one atomic operation
            print("\n".join(output_lines))
        elif hasattr(self.netSystem, 'verbose') and self.netSystem.verbose:
            print(f"{self.get_timestamp_str()}{category}: {message}")

    def create_profile(self, user_id, display_name, status, avatar_path=None):
        self.user_id = user_id
        self.display_name = display_name
        self.status = status
        
        # Use default avatar if none provided
        if avatar_path is None:
            import os
            default_avatar = os.path.join("uploads", "default.jpg")
            if os.path.exists(default_avatar):
                avatar_path = default_avatar
                print(f"[INFO] Using default avatar: {default_avatar}")
        
        # Store our own profile in known_peers
        self.known_peers[user_id] = {
            'display_name': display_name,
            'status': status,
            'avatar_path': avatar_path
        }
        
        # Broadcast PROFILE message
        message = {
            "TYPE": MSG_PROFILE,
            "USER_ID": user_id,
            "DISPLAY_NAME": display_name,
            "STATUS": status,
            "LISTEN_PORT": self.netSystem.port,  # Include our listening port
            "BROADCAST": True
        }
        
        # Add avatar data (will use default if avatar_path was set above)
        if avatar_path:
            try:
                avatar_data = self.encode_avatar(avatar_path)
                if avatar_data:
                    message.update(avatar_data)
                    print(f"[INFO] Added avatar to profile: {avatar_path}")
            except Exception as e:
                print(f"[WARN] Could not encode avatar: {e}")
        
        self.netSystem.send_message(message)

    def send_post(self, content, ttl=3600):
        """Send a POST message to all followers (unicast) or broadcast if no followers."""
        user_id = self.user_id
        timestamp = int(time.time())
        message_id = f"{random.getrandbits(64):016x}"
        token = f"{user_id}|{timestamp + ttl}|{SCOPE_BROADCAST}"

        message = {
            "TYPE": MSG_POST,
            "USER_ID": user_id,
            "CONTENT": content,
            "TTL": ttl,
            "MESSAGE_ID": message_id,
            "TOKEN": token,
            "TIMESTAMP": timestamp,
            "BROADCAST": False  # Will be set to True if broadcasting
        }

        # Get followers list
        followers_list = self.get_followers_list()
        
        if not followers_list:
            # No followers - use broadcast so the post still reaches the network
            print(f"{self.get_timestamp_str()} [POST] No followers - broadcasting to network: '{content}'")
            message["BROADCAST"] = True
            self.netSystem.send_message(message)
            # Store our own post locally
            self.stored_posts.append(message)
            return

        # Send to all followers individually (unicast)
        sent_count = 0
        failed_count = 0
        
        for follower_user_id in followers_list:
            try:
                # Extract IP from user_id for unicast
                ip_address = follower_user_id.rsplit('@', 1)[1] if '@' in follower_user_id else "127.0.0.1"
                target_port = LSNP_PORT
                
                # Find the port for this user from known_clients
                for known_ip, known_port in self.netSystem.known_clients:
                    if known_ip == ip_address:
                        target_port = known_port
                        break
                
                self.netSystem.send_message(message, target_ip=ip_address, target_port=target_port)
                sent_count += 1
                
                if self.netSystem.verbose:
                    display_name = self.get_display_name(follower_user_id)
                    print(f"{self.get_timestamp_str()} [DEBUG] Sent POST to follower: {display_name} ({follower_user_id})")
                    
            except Exception as e:
                failed_count += 1
                if self.netSystem.verbose:
                    display_name = self.get_display_name(follower_user_id)
                    print(f"{self.get_timestamp_str()} [ERROR] Failed to send POST to {display_name}: {e}")
        
        # Store our own post locally
        self.stored_posts.append(message)
        
        # Show summary
        print(f"{self.get_timestamp_str()} [POST] Sent to {sent_count}/{len(followers_list)} followers: '{content}'")
        if failed_count > 0:
            print(f"{self.get_timestamp_str()} [WARN] Failed to send to {failed_count} followers")

    def send_dm(self, to_user, content):
        """Send a direct message to a specific user."""
        timestamp = int(time.time())
        message_id = f"{random.getrandbits(64):016x}"
        token = f"{self.user_id}|{timestamp + 3600}|{SCOPE_CHAT}"
        
        message = {
            "TYPE": MSG_DM,
            "FROM": self.user_id,
            "TO": to_user,
            "CONTENT": content,
            "TIMESTAMP": timestamp,
            "MESSAGE_ID": message_id,
            "TOKEN": token
        }
        
        # Send with ACK tracking
        self.send_message_with_ack(message, to_user)
        print(f"{self.get_timestamp_str()} [SENT DM] To {self.get_display_name(to_user)}: {content}")

    def send_follow(self, target_user):
        """Send a FOLLOW message to a user."""
        timestamp = int(time.time())
        message_id = f"{random.getrandbits(64):016x}"
        token = f"{self.user_id}|{timestamp + 3600}|{SCOPE_FOLLOW}"
        
        message = {
            "TYPE": MSG_FOLLOW,
            "MESSAGE_ID": message_id,
            "FROM": self.user_id,
            "TO": target_user,
            "TIMESTAMP": timestamp,
            "TOKEN": token
        }
        
        # Send with ACK tracking
        self.send_message_with_ack(message, target_user)
        
        # Add to our following list
        self.following.add(target_user)
        print(f"{self.get_timestamp_str()} [FOLLOW] Now following {self.get_display_name(target_user)}")

    def send_unfollow(self, target_user):
        """Send an UNFOLLOW message to a user."""
        timestamp = int(time.time())
        message_id = f"{random.getrandbits(64):016x}"
        token = f"{self.user_id}|{timestamp + 3600}|{SCOPE_FOLLOW}"
        
        message = {
            "TYPE": MSG_UNFOLLOW,
            "MESSAGE_ID": message_id,
            "FROM": self.user_id,
            "TO": target_user,
            "TIMESTAMP": timestamp,
            "TOKEN": token
        }
        
        # Send with ACK tracking
        self.send_message_with_ack(message, target_user)
        
        # Remove from our following list
        self.following.discard(target_user)
        print(f"{self.get_timestamp_str()} [UNFOLLOW] No longer following {self.get_display_name(target_user)}")

    def send_like(self, to_user, post_timestamp, action="LIKE"):
        """Send a LIKE message to a user for their post."""
        timestamp = int(time.time())
        message_id = f"{random.getrandbits(64):016x}"
        token = f"{self.user_id}|{timestamp + 3600}|{SCOPE_BROADCAST}"
        
        message = {
            "TYPE": MSG_LIKE,
            "MESSAGE_ID": message_id,
            "FROM": self.user_id,
            "TO": to_user,
            "ACTION": action,  # LIKE or UNLIKE
            "POST_TIMESTAMP": post_timestamp,
            "TIMESTAMP": timestamp,
            "TOKEN": token
        }
        
        # Send with ACK tracking
        self.send_message_with_ack(message, to_user)
        
        # Also update local like tracking for immediate feedback
        # This helps show like counts locally before the recipient processes the message
        post_key = (to_user, post_timestamp)
        
        # Initialize post like tracking if not exists
        if post_key not in self.post_likes:
            self.post_likes[post_key] = {'likers': set(), 'count': 0}
        
        # Handle LIKE/UNLIKE actions locally
        if action == "LIKE":
            if self.user_id not in self.post_likes[post_key]['likers']:
                self.post_likes[post_key]['likers'].add(self.user_id)
                self.post_likes[post_key]['count'] += 1
        elif action == "UNLIKE":
            if self.user_id in self.post_likes[post_key]['likers']:
                self.post_likes[post_key]['likers'].remove(self.user_id)
                self.post_likes[post_key]['count'] -= 1
                # Ensure count doesn't go negative
                if self.post_likes[post_key]['count'] < 0:
                    self.post_likes[post_key]['count'] = 0
        
        display_name = self.get_display_name(to_user)
        print(f"{self.get_timestamp_str()} [LIKE] Sent {action.lower()} to {display_name}'s post")

    def follow_user(self, user_id):
        pass

    def unfollow_user(self, user_id):
        pass

    def process_incoming_message(self, message):
        """Process incoming messages and store valid ones."""
        msg_type = message.get("TYPE")
        print(f"[DEBUG] Processing message type: '{msg_type}'")
        
        if msg_type == MSG_PROFILE:
            self.handle_profile_message(message)
        elif msg_type == MSG_POST:
            self.handle_post_message(message)
        elif msg_type == MSG_DM:
            self.handle_dm_message(message)
        elif msg_type == MSG_PING:
            self.handle_ping_message(message)
        elif msg_type == MSG_LIKE:
            self.handle_like_message(message)
        elif msg_type == MSG_FOLLOW:
            self.handle_follow_message(message)
        elif msg_type == MSG_UNFOLLOW:
            self.handle_unfollow_message(message)
        elif msg_type == MSG_ACK:
            self.handle_ack_message(message)
        elif msg_type == MSG_REVOKE:
            self.handle_revoke_message(message)
        elif msg_type == MSG_GROUP_CREATE:
            print(f"[DEBUG] Calling handle_group_create_message for: {msg_type}")
            self.handle_group_create_message(message)
        elif msg_type == MSG_GROUP_UPDATE:
            self.handle_group_update_message(message)
        elif msg_type == MSG_GROUP_MESSAGE:
            self.handle_group_message(message)
        else:
            print(f"[DEBUG] Unknown message type: '{msg_type}'")
        
        # Send ACK for messages that require acknowledgment
        if msg_type in [MSG_DM, MSG_FOLLOW, MSG_UNFOLLOW, MSG_LIKE, MSG_GROUP_CREATE, MSG_GROUP_UPDATE, MSG_GROUP_MESSAGE] and message.get("MESSAGE_ID"):
            self.send_ack(message)

    def handle_profile_message(self, message):
        """Handle incoming PROFILE messages."""
        user_id = message.get("USER_ID")
        display_name = message.get("DISPLAY_NAME")
        status = message.get("STATUS")
        message_id = message.get("MESSAGE_ID")
        current_time = int(time.time())
        
        # Check for duplicate messages by MESSAGE_ID
        if message_id and message_id in self.processed_messages:
            if self.netSystem.verbose:
                print(f"[DEBUG] Ignoring duplicate PROFILE: {message_id}")
            return
        
        # Check for recent PROFILE messages from same user (within 3 seconds)
        if user_id in self.last_profile_received:
            time_diff = current_time - self.last_profile_received[user_id]
            if time_diff < 3:  # Ignore if received within last 3 seconds
                if self.netSystem.verbose:
                    print(f"[DEBUG] Ignoring recent PROFILE from {user_id} (received {time_diff}s ago)")
                return
        
        if user_id and display_name:
            self.known_peers[user_id] = {
                'display_name': display_name,
                'status': status or "No status",
                'avatar_type': message.get("AVATAR_TYPE"),
                'avatar_data': message.get("AVATAR_DATA")
            }
            
            # Mark message as processed
            if message_id:
                self.processed_messages.add(message_id)
            
            # Update last received time for this user
            self.last_profile_received[user_id] = current_time
            
            if not self.netSystem.verbose:
                print(f"{self.get_timestamp_str()} [PROFILE] {display_name}: {status}")
            else:
                print(f"{self.get_timestamp_str()} [PROFILE] Updated profile for {user_id}: {display_name} - {status}")

    def handle_post_message(self, message):
        """Handle incoming POST messages."""
        user_id = message.get("USER_ID")
        content = message.get("CONTENT")
        token = message.get("TOKEN")
        message_id = message.get("MESSAGE_ID")
        
        # Check for duplicate messages
        if message_id and message_id in self.processed_messages:
            if self.netSystem.verbose:
                print(f"[DEBUG] Ignoring duplicate POST: {message_id}")
            return
        
        # Only accept posts from users we're following (or our own posts)
        if user_id != self.user_id and user_id not in self.following:
            if self.netSystem.verbose:
                print(f"[DEBUG] Ignoring POST from non-followed user: {user_id}")
            return
        
        # Enhanced token validation
        if token and self.validate_enhanced_token(token, SCOPE_BROADCAST, message_type="POST"):
            self.stored_posts.append(message)
            
            # Store as valid message
            self.store_valid_message(message, {'token_valid': True, 'scope': SCOPE_BROADCAST})
            
            # Mark message as processed
            if message_id:
                self.processed_messages.add(message_id)
            
            # Get display name if known
            display_name = self.get_display_name(user_id)
            
            if not self.netSystem.verbose:
                print(f"\n[POST] {display_name}: {content}\n")
            else:
                print(f"\n{self.get_timestamp_str()}[POST] From {user_id} ({display_name}): {content}\n")
        elif self.netSystem.verbose:
            print(f"{self.get_timestamp_str()} [DEBUG] POST rejected due to invalid token")

    def handle_dm_message(self, message):
        """Handle incoming DM messages."""
        from_user = message.get("FROM")
        to_user = message.get("TO")
        content = message.get("CONTENT")
        message_id = message.get("MESSAGE_ID")
        token = message.get("TOKEN")
        
        # Check for duplicate messages
        if message_id and message_id in self.processed_messages:
            if self.netSystem.verbose:
                print(f"[DEBUG] Ignoring duplicate DM: {message_id}")
            return
        
        # Only process if DM is for us and has valid token
        if to_user == self.user_id:
            if token and self.validate_enhanced_token(token, SCOPE_CHAT, message_type="DM"):
                self.stored_dms.append(message)
                
                # Store as valid message
                self.store_valid_message(message, {'token_valid': True, 'scope': SCOPE_CHAT})
                
                # Mark message as processed
                if message_id:
                    self.processed_messages.add(message_id)
                
                display_name = self.get_display_name(from_user)
                
                if not self.netSystem.verbose:
                    print(f"\n[DM] {display_name}: {content}\n")
                else:
                    print(f"\n{self.get_timestamp_str()}[DM] From {from_user} ({display_name}): {content}\n")
            elif self.netSystem.verbose:
                print(f"{self.get_timestamp_str()} [DEBUG] DM rejected due to invalid token")

    def handle_follow_message(self, message):
        """Handle incoming FOLLOW messages."""
        from_user = message.get("FROM")
        to_user = message.get("TO")
        token = message.get("TOKEN")
        
        # Only process if FOLLOW is for us and has valid token
        if to_user == self.user_id and token and self.validate_enhanced_token(token, SCOPE_FOLLOW, message_type="FOLLOW"):
            # Add to our followers list
            self.followers.add(from_user)
            
            # Store as valid message
            self.store_valid_message(message, {'token_valid': True, 'scope': SCOPE_FOLLOW})
            
            display_name = self.get_display_name(from_user)
            print(f"\n[FOLLOW] {display_name} started following you\n")
        elif to_user == self.user_id and self.netSystem.verbose:
            print(f"{self.get_timestamp_str()} [DEBUG] FOLLOW rejected due to invalid token")

    def handle_unfollow_message(self, message):
        """Handle incoming UNFOLLOW messages."""
        from_user = message.get("FROM")
        to_user = message.get("TO")
        token = message.get("TOKEN")
        
        # Only process if UNFOLLOW is for us and has valid token
        if to_user == self.user_id and token and self.validate_enhanced_token(token, SCOPE_FOLLOW, message_type="UNFOLLOW"):
            # Remove from our followers list
            self.followers.discard(from_user)
            
            # Store as valid message
            self.store_valid_message(message, {'token_valid': True, 'scope': SCOPE_FOLLOW})
            
            display_name = self.get_display_name(from_user)
            print(f"\n[UNFOLLOW] {display_name} unfollowed you\n")
        elif to_user == self.user_id and self.netSystem.verbose:
            print(f"{self.get_timestamp_str()} [DEBUG] UNFOLLOW rejected due to invalid token")

    def handle_ping_message(self, message):
        """Handle incoming PING messages."""
        user_id = message.get("USER_ID")
        if user_id and user_id != self.user_id:
            # Update last seen time
            if user_id in self.known_peers:
                self.known_peers[user_id]['last_ping'] = int(time.time())
            
            # Respond with our PROFILE if we haven't sent one recently
            if self.netSystem.verbose:
                print(f"{self.get_timestamp_str()} [PING] Received from {user_id}")
            
            # Send PROFILE response (optional - helps with discovery)
            if hasattr(self, 'user_id'):
                self.send_profile_response(user_id)

    def send_profile_response(self, requesting_user):
        """Send a PROFILE message in response to a PING."""
        try:
            # Extract IP from user_id for unicast response
            ip_address = requesting_user.rsplit('@', 1)[1] if '@' in requesting_user else "127.0.0.1"
            target_port = LSNP_PORT
            
            # Find the port for this user from known_clients
            for known_ip, known_port in self.netSystem.known_clients:
                if known_ip == ip_address:
                    target_port = known_port
                    break
            
            message = {
                "TYPE": MSG_PROFILE,
                "USER_ID": self.user_id,
                "DISPLAY_NAME": self.display_name,
                "STATUS": self.status,
                "LISTEN_PORT": self.netSystem.port,
                "BROADCAST": False  # Unicast response
            }
            
            self.netSystem.send_message(message, target_ip=ip_address, target_port=target_port)
            if self.netSystem.verbose:
                print(f"{self.get_timestamp_str()} [PROFILE] Sent response to {requesting_user}")
                
        except Exception as e:
            if self.netSystem.verbose:
                print(f"{self.get_timestamp_str()} [ERROR] Failed to send PROFILE response: {e}")

    def handle_like_message(self, message):
        """Handle incoming LIKE messages."""
        from_user = message.get("FROM")
        action = message.get("ACTION", "LIKE")
        message_id = message.get("MESSAGE_ID")
        post_timestamp = message.get("POST_TIMESTAMP")
        to_user = message.get("TO")
        
        # Check for duplicate messages
        if message_id and message_id in self.processed_messages:
            if self.netSystem.verbose:
                print(f"[DEBUG] Ignoring duplicate LIKE: {message_id}")
            return
        
        # Mark message as processed
        if message_id:
            self.processed_messages.add(message_id)
        
        # Track likes for the post (using post owner and timestamp as key)
        if post_timestamp and to_user:
            post_key = (to_user, post_timestamp)
            
            # Initialize post like tracking if not exists
            if post_key not in self.post_likes:
                self.post_likes[post_key] = {'likers': set(), 'count': 0}
            
            # Handle LIKE/UNLIKE actions
            if action == "LIKE":
                if from_user not in self.post_likes[post_key]['likers']:
                    self.post_likes[post_key]['likers'].add(from_user)
                    self.post_likes[post_key]['count'] += 1
            elif action == "UNLIKE":
                if from_user in self.post_likes[post_key]['likers']:
                    self.post_likes[post_key]['likers'].remove(from_user)
                    self.post_likes[post_key]['count'] -= 1
                    # Ensure count doesn't go negative
                    if self.post_likes[post_key]['count'] < 0:
                        self.post_likes[post_key]['count'] = 0
        
        display_name = self.get_display_name(from_user)
        print(f"{self.get_timestamp_str()} [LIKE] {display_name} {action.lower()}d your post")

    def handle_revoke_message(self, message):
        """Handle incoming REVOKE messages."""
        from_user = message.get("FROM")
        revoked_token = message.get("REVOKED_TOKEN")
        reason = message.get("REASON", "Token revoked by sender")
        
        if revoked_token and from_user:
            # Verify the token belongs to the sender
            try:
                token_parts = revoked_token.split('|')
                if len(token_parts) == 3:
                    token_user = token_parts[0]
                    if token_user == from_user:
                        self.revoke_token(revoked_token, f"Revoked by {from_user}: {reason}")
                        display_name = self.get_display_name(from_user)
                        print(f"{self.get_timestamp_str()} [REVOKE] {display_name} revoked a token")
                    elif self.netSystem.verbose:
                        print(f"{self.get_timestamp_str()} [DEBUG] REVOKE rejected: token user mismatch")
                elif self.netSystem.verbose:
                    print(f"{self.get_timestamp_str()} [DEBUG] REVOKE rejected: invalid token format")
            except Exception as e:
                if self.netSystem.verbose:
                    print(f"{self.get_timestamp_str()} [DEBUG] REVOKE processing error: {e}")

    def send_revoke_message(self, token_to_revoke, reason="User requested revocation"):
        """Send a REVOKE message to announce token revocation."""
        timestamp = int(time.time())
        message_id = f"{random.getrandbits(64):016x}"
        
        message = {
            "TYPE": MSG_REVOKE,
            "MESSAGE_ID": message_id,
            "FROM": self.user_id,
            "REVOKED_TOKEN": token_to_revoke,
            "REASON": reason,
            "TIMESTAMP": timestamp,
            "BROADCAST": True
        }
        
        # Revoke locally first
        self.revoke_token(token_to_revoke, reason)
        
        # Broadcast revocation
        self.netSystem.send_message(message)
        print(f"{self.get_timestamp_str()} [REVOKE] Broadcasted token revocation")

    def send_ack(self, original_message):
        """Send an ACK message in response to a received message."""
        message_id = original_message.get("MESSAGE_ID")
        from_user = original_message.get("FROM") or original_message.get("USER_ID")
        
        if not message_id or not from_user:
            return
        
        ack_message = {
            "TYPE": MSG_ACK,
            "MESSAGE_ID": f"{random.getrandbits(64):016x}",
            "ACK_MESSAGE_ID": message_id,
            "FROM": self.user_id,
            "TO": from_user,
            "TIMESTAMP": int(time.time())
        }
        
        try:
            # Extract IP from user_id for unicast
            ip_address = from_user.rsplit('@', 1)[1] if '@' in from_user else "127.0.0.1"
            target_port = LSNP_PORT
            
            # Find the port for this user from known_clients
            for known_ip, known_port in self.netSystem.known_clients:
                if known_ip == ip_address:
                    target_port = known_port
                    break
            
            self.netSystem.send_message(ack_message, target_ip=ip_address, target_port=target_port)
            
            self.acks_sent += 1  # Increment counter
            
            if self.netSystem.verbose:
                self.log_message(f"[ACK] Sent ACK for message {message_id} to {from_user}", ack_message)
                
        except Exception as e:
            if self.netSystem.verbose:
                print(f"{self.get_timestamp_str()} [ERROR] Failed to send ACK: {e}")

    def handle_ack_message(self, message):
        """Handle incoming ACK messages."""
        ack_message_id = message.get("ACK_MESSAGE_ID")
        from_user = message.get("FROM")
        
        if ack_message_id and ack_message_id in self.pending_acks:
            # Remove from pending ACKs
            del self.pending_acks[ack_message_id]
            
            self.acks_received += 1  # Increment counter
            
            if self.netSystem.verbose:
                display_name = self.get_display_name(from_user)
                print(f"{self.get_timestamp_str()} [ACK] Received ACK from {display_name} for message {ack_message_id}")

    def send_message_with_ack(self, message, target_user_id):
        """Send a message and track it for ACK."""
        message_id = message.get("MESSAGE_ID")
        
        # Store in pending ACKs
        if message_id:
            self.pending_acks[message_id] = {
                'timestamp': int(time.time()),
                'retries': 0,
                'message': message.copy(),
                'target_user': target_user_id
            }
        
        # Send the message normally
        try:
            ip_address = target_user_id.rsplit('@', 1)[1] if '@' in target_user_id else "127.0.0.1"
            target_port = LSNP_PORT
            
            # Find the port for this user from known_clients
            for known_ip, known_port in self.netSystem.known_clients:
                if known_ip == ip_address:
                    target_port = known_port
                    break
            
            self.netSystem.send_message(message, target_ip=ip_address, target_port=target_port)
            
            if self.netSystem.verbose:
                print(f"{self.get_timestamp_str()} [SEND] Sent message {message_id} to {target_user_id} (waiting for ACK)")
                
        except Exception as e:
            if self.netSystem.verbose:
                print(f"{self.get_timestamp_str()} [ERROR] Failed to send message with ACK: {e}")
            # Remove from pending if send failed
            if message_id in self.pending_acks:
                del self.pending_acks[message_id]

    def check_pending_acks(self):
        """Check for pending ACKs that need retry or timeout."""
        current_time = int(time.time())
        to_retry = []
        to_remove = []
        
        for message_id, ack_info in self.pending_acks.items():
            time_elapsed = current_time - ack_info['timestamp']
            
            if time_elapsed > self.ack_timeout:
                if ack_info['retries'] < MAX_RETRIES:
                    # Retry the message
                    to_retry.append((message_id, ack_info))
                else:
                    # Give up after max retries
                    to_remove.append(message_id)
                    if self.netSystem.verbose:
                        print(f"{self.get_timestamp_str()} [ACK] Message {message_id} failed after {MAX_RETRIES} retries")
        
        # Retry messages
        for message_id, ack_info in to_retry:
            ack_info['retries'] += 1
            ack_info['timestamp'] = current_time
            
            # Resend the exact same message (don't call send_message_with_ack again)
            try:
                # Resolve target IP from user ID
                target_user_id = ack_info['target_user']
                ip_address = self.resolve_user_to_ip(target_user_id)
                target_port = 50999  # Default LSNP port
                
                # Check if we have a known port for this IP
                for known_ip, known_port in self.netSystem.known_clients:
                    if known_ip == ip_address:
                        target_port = known_port
                        break
                
                self.netSystem.send_message(ack_info['message'], target_ip=ip_address, target_port=target_port)
                
                if self.netSystem.verbose:
                    print(f"{self.get_timestamp_str()} [RETRY] Resent message {message_id} to {target_user_id} (attempt {ack_info['retries']})")
                    
            except Exception as e:
                if self.netSystem.verbose:
                    print(f"{self.get_timestamp_str()} [ERROR] Failed to retry message {message_id}: {e}")
                # Add to removal list if retry fails
                to_remove.append(message_id)
            
        # Remove failed messages
        for message_id in to_remove:
            del self.pending_acks[message_id]

    def validate_basic_token(self, token):
        """Basic token validation - checks format and expiration."""
        try:
            parts = token.split('|')
            if len(parts) != 3:
                return False
            
            user_id, expiry_str, scope = parts
            expiry = int(expiry_str)
            current_time = int(time.time())
            
            return expiry > current_time
        except:
            return False

    def validate_enhanced_token(self, token, required_scope, sender_ip=None, message_type=None):
        """Enhanced token validation - checks format, expiration, scope, and revocation."""
        timestamp = int(time.time())
        validation_result = {
            'valid': False,
            'reason': '',
            'timestamp': timestamp,
            'token': token,
            'required_scope': required_scope,
            'sender_ip': sender_ip,
            'message_type': message_type
        }
        
        try:
            # Check token format
            parts = token.split('|')
            if len(parts) != 3:
                validation_result['reason'] = 'Invalid token format'
                self.log_token_validation(validation_result)
                return False
            
            user_id, expiry_str, token_scope = parts
            
            # Check expiration
            try:
                expiry = int(expiry_str)
                current_time = int(time.time())
                if expiry <= current_time:
                    validation_result['reason'] = 'Token expired'
                    self.log_token_validation(validation_result)
                    return False
            except ValueError:
                validation_result['reason'] = 'Invalid expiry timestamp'
                self.log_token_validation(validation_result)
                return False
            
            # Check scope match
            if token_scope != required_scope:
                validation_result['reason'] = f'Scope mismatch: got {token_scope}, required {required_scope}'
                self.log_token_validation(validation_result)
                return False
            
            # Check revocation status
            if token in self.revoked_tokens:
                validation_result['reason'] = 'Token is revoked'
                self.log_token_validation(validation_result)
                return False
            
            # Verify sender IP matches token user_id (if provided)
            if sender_ip and '@' in user_id:
                token_ip = user_id.split('@')[1]
                if token_ip != sender_ip:
                    validation_result['reason'] = f'IP mismatch: token IP {token_ip}, sender IP {sender_ip}'
                    self.log_token_validation(validation_result)
                    return False
            
            # Token is valid
            validation_result['valid'] = True
            validation_result['reason'] = 'Valid token'
            self.log_token_validation(validation_result)
            return True
            
        except Exception as e:
            validation_result['reason'] = f'Validation error: {str(e)}'
            self.log_token_validation(validation_result)
            return False

    def log_token_validation(self, validation_result):
        """Log token validation attempts for debugging and security auditing."""
        self.token_validation_log.append(validation_result)
        
        # Keep only last 100 validation attempts to prevent memory bloat
        if len(self.token_validation_log) > 100:
            self.token_validation_log = self.token_validation_log[-100:]
        
        if self.netSystem.verbose:
            status = "✓ VALID" if validation_result['valid'] else "✗ INVALID"
            print(f"{self.get_timestamp_str()} [TOKEN] {status}: {validation_result['reason']} (scope: {validation_result['required_scope']})")

    def revoke_token(self, token, reason="Manual revocation"):
        """Revoke a token to prevent future use."""
        self.revoked_tokens.add(token)
        if self.netSystem.verbose:
            print(f"{self.get_timestamp_str()} [TOKEN] Revoked token: {token[:20]}... (reason: {reason})")

    def get_token_validation_stats(self):
        """Get statistics about token validation."""
        if not self.token_validation_log:
            return {"total": 0, "valid": 0, "invalid": 0, "success_rate": 0}
        
        total = len(self.token_validation_log)
        valid = sum(1 for v in self.token_validation_log if v['valid'])
        invalid = total - valid
        success_rate = (valid / total) * 100 if total > 0 else 0
        
        return {
            "total": total,
            "valid": valid,
            "invalid": invalid,
            "success_rate": round(success_rate, 2)
        }

    def store_valid_message(self, message, validation_info=None):
        """Store messages with valid token structure for analysis."""
        stored_entry = {
            'message': message.copy(),
            'timestamp': int(time.time()),
            'validation_info': validation_info
        }
        self.valid_messages.append(stored_entry)
        
        # Keep only last 200 valid messages to prevent memory bloat
        if len(self.valid_messages) > 200:
            self.valid_messages = self.valid_messages[-200:]

    def get_valid_messages(self):
        """Get all stored messages with valid tokens."""
        return self.valid_messages

    def display_message(self, message, verbose=False):
        pass

    def start_ping_broadcast(self):  # Every 5 minutes
        """Start periodic PROFILE broadcasting for presence."""
        import threading
        
        def broadcast_profile():
            while True:
                time.sleep(BROADCAST_INTERVAL)  # 30 seconds from vars.py
                if hasattr(self, 'user_id'):
                    # Alternate between PING and PROFILE broadcasts
                    import random
                    if random.choice([True, False]):
                        # Send PING message
                        ping_message = {
                            "TYPE": MSG_PING,
                            "USER_ID": self.user_id,
                            "BROADCAST": True
                        }
                        self.netSystem.send_message(ping_message)
                        if self.netSystem.verbose:
                            print(f"[BROADCAST] Sent PING")
                    else:
                        # Re-broadcast PROFILE for presence
                        message = {
                            "TYPE": MSG_PROFILE,
                            "USER_ID": self.user_id,
                            "DISPLAY_NAME": self.display_name,
                            "STATUS": self.status,
                            "LISTEN_PORT": self.netSystem.port,  # Include our listening port
                            "BROADCAST": True
                        }
                        self.netSystem.send_message(message)
                        if self.netSystem.verbose:
                            print(f"[BROADCAST] Sent periodic PROFILE update")
        
        def ack_monitor():
            """Monitor pending ACKs and retry failed messages."""
            while True:
                time.sleep(1)  # Check every second
                self.check_pending_acks()
        
        # Start background thread for periodic broadcasting
        thread = threading.Thread(target=broadcast_profile, daemon=True)
        thread.start()
        
        # Start ACK monitoring thread
        ack_thread = threading.Thread(target=ack_monitor, daemon=True)
        ack_thread.start()

    def get_known_peers(self):
        pass

    def get_user_posts(self, user_id):
        pass

    def is_following(self, user_id):
        pass

    def is_following(self, user_id):
        """Check if we're following a specific user."""
        return user_id in self.following

    def get_following_list(self):
        """Get list of users we're following."""
        return list(self.following)

    def get_followers_list(self):
        """Get list of users following us."""
        return list(self.followers)

    def get_display_name(self, user_id):  # For pretty printing
        """Get display name for a user_id, fallback to user_id if not known."""
        if user_id in self.known_peers:
            return self.known_peers[user_id].get('display_name', user_id)
        return user_id

    def get_known_peers(self):
        """Get all known peers."""
        return self.known_peers

    def get_all_posts(self):  # Show all valid posts
        """Get all stored valid posts."""
        return self.stored_posts
    
    def clear_duplicate_posts(self):
        """Remove duplicate posts based on MESSAGE_ID."""
        seen_ids = set()
        unique_posts = []
        
        for post in self.stored_posts:
            msg_id = post.get("MESSAGE_ID")
            if msg_id and msg_id not in seen_ids:
                seen_ids.add(msg_id)
                unique_posts.append(post)
            elif not msg_id:  # Keep posts without MESSAGE_ID (shouldn't happen but just in case)
                unique_posts.append(post)
                
        self.stored_posts = unique_posts
        return len(self.stored_posts)

    def get_like_count(self, user_id, timestamp):
        """Get the number of likes for a specific post."""
        post_key = (user_id, timestamp)
        if post_key in self.post_likes:
            return self.post_likes[post_key]['count']
        return 0
    
    def get_post_likers(self, user_id, timestamp):
        """Get the list of users who liked a specific post."""
        post_key = (user_id, timestamp)
        if post_key in self.post_likes:
            return list(self.post_likes[post_key]['likers'])
        return []

    def get_all_dms(self):  # Show all DMs
        """Get all stored DMs."""
        return self.stored_dms

    def handle_profile_response(self, message):
        pass

    def encode_avatar(self, image_path):
        """Encode image file to base64 for AVATAR fields."""
        try:
            import base64
            import mimetypes
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type or not mime_type.startswith('image/'):
                return None
            
            # Read and encode file
            with open(image_path, 'rb') as f:
                image_data = f.read()
                
            # Check size limit (~20KB as per specs)
            if len(image_data) > 20480:
                print(f"[WARN] Avatar file too large: {len(image_data)} bytes (limit: 20KB)")
                return None
                
            encoded_data = base64.b64encode(image_data).decode('utf-8')
            
            return {
                "AVATAR_TYPE": mime_type,
                "AVATAR_ENCODING": "base64", 
                "AVATAR_DATA": encoded_data
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to encode avatar: {e}")
            return None

    def decode_avatar(self, avatar_data, mime_type):
        pass

    def filter_posts_by_following(self):  # Only show posts from followed users
        pass

    def get_peer_status(self, user_id):
        pass

    # ============ GROUP MANAGEMENT METHODS ============
    
    def create_group(self, group_id, group_name, members):
        """Create a new group and send GROUP_CREATE message to all members."""
        # Validate group_id is unique locally
        if group_id in self.groups:
            print(f"❌ Group '{group_id}' already exists.")
            return False
        
        # Ensure creator is in members list
        if self.user_id not in members:
            members.append(self.user_id)
        
        # Store group locally
        timestamp = int(time.time())
        self.groups[group_id] = {
            'name': group_name,
            'members': members,
            'creator': self.user_id,
            'created_time': timestamp
        }
        
        # Initialize message storage for this group
        self.group_messages[group_id] = []
        
        # Create GROUP_CREATE message
        message_id = f"{random.getrandbits(64):016x}"
        message = {
            "TYPE": MSG_GROUP_CREATE,
            "MESSAGE_ID": message_id,
            "FROM": self.user_id,
            "GROUP_ID": group_id,
            "GROUP_NAME": group_name,
            "MEMBERS": ",".join(members),
            "TIMESTAMP": timestamp,
            "TOKEN": f"{self.user_id}|{timestamp + 3600}|{SCOPE_GROUP}"
        }
        
        # Send to all members
        for member in members:
            if member != self.user_id:  # Don't send to self
                self.send_message_to_user(message, member)
        
        print(f"✅ Group '{group_name}' created with {len(members)} members.")
        return True
    
    def update_group(self, group_id, add_members=None, remove_members=None):
        """Update group membership and send GROUP_UPDATE message."""
        if group_id not in self.groups:
            print(f"❌ Group '{group_id}' not found.")
            return False
        
        group = self.groups[group_id]
        
        # Check if user is the group creator (only creators can update groups)
        if self.user_id != group['creator']:
            print(f"❌ Only the group creator can update group '{group_id}'.")
            return False
        
        # Store original member list before changes for notification
        original_members = group['members'].copy()
        
        # Process additions
        if add_members:
            for member in add_members:
                if member not in group['members']:
                    group['members'].append(member)
        
        # Process removals
        if remove_members:
            for member in remove_members:
                if member in group['members'] and member != group['creator']:
                    group['members'].remove(member)
        
        # Create GROUP_UPDATE message
        timestamp = int(time.time())
        message_id = f"{random.getrandbits(64):016x}"
        message = {
            "TYPE": MSG_GROUP_UPDATE,
            "MESSAGE_ID": message_id,
            "FROM": self.user_id,
            "GROUP_ID": group_id,
            "TIMESTAMP": timestamp,
            "TOKEN": f"{self.user_id}|{timestamp + 3600}|{SCOPE_GROUP}"
        }
        
        if add_members:
            message["ADD"] = ",".join(add_members)
        if remove_members:
            message["REMOVE"] = ",".join(remove_members)
        
        # Send to all original members (including those being removed)
        all_affected_members = set(original_members)
        if add_members:
            all_affected_members.update(add_members)
        
        # For newly added members, send GROUP_CREATE first (in case they don't know about the group)
        if add_members:
            group_create_message = {
                "TYPE": MSG_GROUP_CREATE,
                "MESSAGE_ID": f"{random.getrandbits(64):016x}",
                "FROM": self.user_id,
                "GROUP_ID": group_id,
                "GROUP_NAME": group['name'],
                "MEMBERS": ",".join(group['members']),  # Current member list after updates
                "TIMESTAMP": timestamp,
                "TOKEN": f"{self.user_id}|{timestamp + 3600}|{SCOPE_GROUP}"
            }
            
            for new_member in add_members:
                if new_member != self.user_id:
                    self.send_message_to_user(group_create_message, new_member)
        
        # Then send GROUP_UPDATE to all affected members
        for member in all_affected_members:
            if member != self.user_id:  # Don't send to self
                self.send_message_to_user(message, member)
        
        print(f"✅ Group '{group['name']}' updated.")
        return True
    
    def send_group_message(self, group_id, content):
        """Send a message to all members of a group."""
        if group_id not in self.groups:
            print(f"❌ Group '{group_id}' not found.")
            return False
        
        group = self.groups[group_id]
        
        # Check if user is a member
        if self.user_id not in group['members']:
            print(f"❌ You are not a member of group '{group_id}'.")
            return False
        
        # Create GROUP_MESSAGE
        timestamp = int(time.time())
        message_id = f"{random.getrandbits(64):016x}"
        message = {
            "TYPE": MSG_GROUP_MESSAGE,
            "MESSAGE_ID": message_id,
            "FROM": self.user_id,
            "GROUP_ID": group_id,
            "CONTENT": content,
            "TIMESTAMP": timestamp,
            "TOKEN": f"{self.user_id}|{timestamp + 3600}|{SCOPE_GROUP}"
        }
        
        # Send to all members except self
        for member in group['members']:
            if member != self.user_id:
                self.send_message_to_user(message, member)
        
        # Store message locally for our own record
        self.group_messages[group_id].append({
            'from': self.user_id,
            'content': content,
            'timestamp': timestamp,
            'message_id': message_id
        })
        
        display_name = self.get_display_name(self.user_id)
        print(f"📤 [GROUP {group['name']}] {display_name}: {content}")
        return True
    
    def handle_group_create_message(self, message):
        """Handle incoming GROUP_CREATE messages."""
        group_id = message.get("GROUP_ID")
        group_name = message.get("GROUP_NAME")
        members_str = message.get("MEMBERS", "")
        from_user = message.get("FROM")
        token = message.get("TOKEN")
        message_id = message.get("MESSAGE_ID")
        
        print(f"[DEBUG] Processing GROUP_CREATE: {group_id} from {from_user}")
        
        # Check for duplicate messages
        if message_id and message_id in self.processed_messages:
            if self.netSystem.verbose:
                print(f"[DEBUG] Ignoring duplicate GROUP_CREATE: {message_id}")
            return
        
        # Validate token
        if not token or not self.validate_enhanced_token(token, SCOPE_GROUP, message_type="GROUP_CREATE"):
            print(f"[DEBUG] Invalid token for GROUP_CREATE from {from_user}")
            return
        
        # Check if we're in the members list
        members = [m.strip() for m in members_str.split(",") if m.strip()]
        print(f"[DEBUG] Group members: {members}")
        print(f"[DEBUG] My user_id: '{self.user_id}'")
        print(f"[DEBUG] Checking membership...")
        for i, member in enumerate(members):
            print(f"[DEBUG]   Member {i}: '{member}' == '{self.user_id}' ? {member == self.user_id}")
        
        if self.user_id not in members:
            print(f"[DEBUG] ❌ Not a member of group {group_id} - user_id mismatch!")
            return
        
        print(f"[DEBUG] ✅ Confirmed as member of group {group_id}")
        
        # Mark message as processed
        if message_id:
            self.processed_messages.add(message_id)
        
        # Store group
        timestamp = message.get("TIMESTAMP", int(time.time()))
        self.groups[group_id] = {
            'name': group_name,
            'members': members,
            'creator': from_user,
            'created_time': timestamp
        }
        
        print(f"[DEBUG] Stored group: {group_id} with {len(members)} members")
        
        # Initialize message storage
        self.group_messages[group_id] = []
        
        # Store valid message
        self.store_valid_message(message, {'token_valid': True, 'scope': SCOPE_GROUP})
        
        # Non-verbose printing (as per spec)
        print(f"📢 You've been added to {group_name}")
    
    def handle_group_update_message(self, message):
        """Handle incoming GROUP_UPDATE messages."""
        group_id = message.get("GROUP_ID")
        from_user = message.get("FROM")
        token = message.get("TOKEN")
        add_members_str = message.get("ADD", "")
        remove_members_str = message.get("REMOVE", "")
        
        # Validate token
        if not token or not self.validate_enhanced_token(token, SCOPE_GROUP, message_type="GROUP_UPDATE"):
            if self.netSystem.verbose:
                print(f"[DEBUG] Invalid token for GROUP_UPDATE from {from_user}")
            return
        
        # Check if group exists  
        if group_id not in self.groups:
            if self.netSystem.verbose:
                print(f"[DEBUG] Unknown group {group_id}")
            return

        group = self.groups[group_id]
        
        # Check if we're affected by this update (either current member or being added/removed)
        is_current_member = self.user_id in group['members']
        is_being_added = add_members_str and self.user_id in [m.strip() for m in add_members_str.split(",")]
        is_being_removed = remove_members_str and self.user_id in [m.strip() for m in remove_members_str.split(",")]
        
        if not (is_current_member or is_being_added or is_being_removed):
            if self.netSystem.verbose:
                print(f"[DEBUG] Not affected by group {group_id} update")
            return
        
        # Process updates
        if add_members_str:
            add_members = [m.strip() for m in add_members_str.split(",") if m.strip()]
            for member in add_members:
                if member not in group['members']:
                    group['members'].append(member)
        
        if remove_members_str:
            remove_members = [m.strip() for m in remove_members_str.split(",") if m.strip()]
            for member in remove_members:
                if member in group['members'] and member != group['creator']:
                    group['members'].remove(member)
                    # If we were removed, clean up our local group data
                    if member == self.user_id:
                        print(f"❌ You have been removed from group \"{group['name']}\"")
                        # Remove group from our local storage
                        del self.groups[group_id]
                        if group_id in self.group_messages:
                            del self.group_messages[group_id]
                        return  # Don't process further since we're no longer in the group
        
        # Store valid message
        self.store_valid_message(message, {'token_valid': True, 'scope': SCOPE_GROUP})
        
        # Non-verbose printing (as per spec) - only if we're still in the group
        if self.user_id in group['members']:
            print(f"📢 The group \"{group['name']}\" member list was updated.")
    
    def handle_group_message(self, message):
        """Handle incoming GROUP_MESSAGE messages."""
        group_id = message.get("GROUP_ID")
        content = message.get("CONTENT")
        from_user = message.get("FROM")
        token = message.get("TOKEN")
        timestamp = message.get("TIMESTAMP", int(time.time()))
        message_id = message.get("MESSAGE_ID")
        
        # Validate token
        if not token or not self.validate_enhanced_token(token, SCOPE_GROUP, message_type="GROUP_MESSAGE"):
            if self.netSystem.verbose:
                print(f"[DEBUG] Invalid token for GROUP_MESSAGE from {from_user}")
            return
        
        # Check if group exists and we're a member
        if group_id not in self.groups:
            if self.netSystem.verbose:
                print(f"[DEBUG] Unknown group {group_id}")
            return
        
        group = self.groups[group_id]
        if self.user_id not in group['members']:
            if self.netSystem.verbose:
                print(f"[DEBUG] Not a member of group {group_id}")
            return
        
        # Store message
        self.group_messages[group_id].append({
            'from': from_user,
            'content': content,
            'timestamp': timestamp,
            'message_id': message_id
        })
        
        # Store valid message
        self.store_valid_message(message, {'token_valid': True, 'scope': SCOPE_GROUP})
        
        # Non-verbose printing (as per spec)
        display_name = self.get_display_name(from_user)
        print(f"📩 [GROUP {group['name']}] {display_name}: {content}")
    
    def get_user_groups(self):
        """Get all groups the user belongs to."""
        user_groups = []
        for group_id, group_data in self.groups.items():
            if self.user_id in group_data['members']:
                user_groups.append({
                    'group_id': group_id,
                    'name': group_data['name'],
                    'members': group_data['members'],
                    'creator': group_data['creator'],
                    'member_count': len(group_data['members'])
                })
        return user_groups
    
    def get_group_members(self, group_id):
        """Get members of a specific group."""
        if group_id not in self.groups:
            return None
        return self.groups[group_id]['members']
    
    def get_group_messages(self, group_id):
        """Get messages for a specific group."""
        if group_id not in self.group_messages:
            return []
        return self.group_messages[group_id]
    
    def send_message_to_user(self, message, target_user):
        """Send a message to a specific user via unicast."""
        try:
            # Extract IP from user_id
            target_ip = target_user.split('@')[-1] if '@' in target_user else "127.0.0.1"
            
            if self.netSystem.verbose:
                print(f"[DEBUG] Sending {message.get('TYPE')} message to {target_user} at {target_ip}")
            
            self.netSystem.send_message(message, target_ip=target_ip, target_port=LSNP_PORT)
        except Exception as e:
            if self.netSystem.verbose:
                print(f"[ERROR] Failed to send message to {target_user}: {e}")
    
    # ============ END GROUP MANAGEMENT ============

"""
Message Types:
1. Profile
    - Show only display_name and status. Optional: PFP
2. POST
    - Show only display name and content
3. DM
    - Show only display_name and content
4. PING
    - Don't display anything
5. ACK
    - Don't display anything
6. Follow
    - Show that x person has followed you
7. Unfollow
    - X person has unfollowed you
"""