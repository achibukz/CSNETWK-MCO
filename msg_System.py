# Member 2

import time
import random
from vars import *

class msgSystem:
    def __init__(self, netSystem):
        self.netSystem = netSystem
        self.known_peers = {}  # Store peer information {user_id: {display_name, status, avatar}}
        self.stored_posts = []  # Store valid posts
        self.stored_dms = []    # Store DMs
        self.following = set()  # Users we're following

    def create_profile(self, user_id, display_name, status, avatar_path=None):
        self.user_id = user_id
        self.display_name = display_name
        self.status = status
        
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
            "LISTEN_PORT": self.network_system.port,  # Include our listening port
            "BROADCAST": True
        }
        
        # Add avatar data if provided
        if avatar_path:
            try:
                avatar_data = self.encode_avatar(avatar_path)
                if avatar_data:
                    message.update(avatar_data)
            except Exception as e:
                print(f"[WARN] Could not encode avatar: {e}")
        
        self.netSystem.send_message(message)

    def send_post(self, content, ttl=3600):
        user_id = self.user_id  # Assuming self.user_id = "dave@192.168.1.10"
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
            "BROADCAST": True
        }

        # Send as broadcast to all known clients
        self.netSystem.send_message(message)

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
        
        # Send to specific user (unicast)
        try:
            # Extract IP from user_id
            ip_address = to_user.rsplit('@', 1)[1] if '@' in to_user else "127.0.0.1"
            # We need to find the port for this user from known_clients
            target_port = LSNP_PORT  # Use constant instead of hardcoded 6969
            for known_ip, known_port in self.netSystem.known_clients:
                if known_ip == ip_address:
                    target_port = known_port
                    break
            
            self.netSystem.send_message(message, target_ip=ip_address, target_port=target_port)
            print(f"[SENT DM] To {self.get_display_name(to_user)}: {content}")
        except Exception as e:
            print(f"[ERROR] Failed to send DM: {e}")

    def send_like(self, to_user, post_timestamp, action="LIKE"):
        pass

    def follow_user(self, user_id):
        pass

    def unfollow_user(self, user_id):
        pass

    def process_incoming_message(self, message):
        """Process incoming messages and store valid ones."""
        msg_type = message.get("TYPE")
        
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

    def handle_profile_message(self, message):
        """Handle incoming PROFILE messages."""
        user_id = message.get("USER_ID")
        display_name = message.get("DISPLAY_NAME")
        status = message.get("STATUS")
        
        if user_id and display_name:
            self.known_peers[user_id] = {
                'display_name': display_name,
                'status': status or "No status",
                'avatar_type': message.get("AVATAR_TYPE"),
                'avatar_data': message.get("AVATAR_DATA")
            }
            
            if not self.netSystem.verbose:
                print(f"[PROFILE] {display_name}: {status}")
            else:
                print(f"[PROFILE] Updated profile for {user_id}: {display_name} - {status}")

    def handle_post_message(self, message):
        """Handle incoming POST messages."""
        user_id = message.get("USER_ID")
        content = message.get("CONTENT")
        token = message.get("TOKEN")
        
        # Basic token validation (should be enhanced)
        if token and self.validate_basic_token(token):
            self.stored_posts.append(message)
            
            # Get display name if known
            display_name = self.get_display_name(user_id)
            
            if not self.netSystem.verbose:
                print(f"[POST] {display_name}: {content}")
            else:
                print(f"[POST] From {user_id} ({display_name}): {content}")

    def handle_dm_message(self, message):
        """Handle incoming DM messages."""
        from_user = message.get("FROM")
        to_user = message.get("TO")
        content = message.get("CONTENT")
        
        # Only process if DM is for us
        if to_user == self.user_id:
            self.stored_dms.append(message)
            
            display_name = self.get_display_name(from_user)
            
            if not self.netSystem.verbose:
                print(f"[DM] {display_name}: {content}")
            else:
                print(f"[DM] From {from_user} ({display_name}): {content}")

    def handle_ping_message(self, message):
        """Handle incoming PING messages."""
        user_id = message.get("USER_ID")
        if user_id and user_id != self.user_id:
            # Update last seen time
            if user_id in self.known_peers:
                self.known_peers[user_id]['last_ping'] = int(time.time())

    def handle_like_message(self, message):
        """Handle incoming LIKE messages."""
        from_user = message.get("FROM")
        action = message.get("ACTION", "LIKE")
        
        display_name = self.get_display_name(from_user)
        print(f"[LIKE] {display_name} {action.lower()}d your post")

    def handle_follow_message(self, message):
        """Handle incoming FOLLOW messages."""
        from_user = message.get("FROM")
        display_name = self.get_display_name(from_user)
        print(f"[FOLLOW] {display_name} started following you")

    def handle_unfollow_message(self, message):
        """Handle incoming UNFOLLOW messages."""
        from_user = message.get("FROM")
        display_name = self.get_display_name(from_user)
        print(f"[UNFOLLOW] {display_name} unfollowed you")

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

    def display_message(self, message, verbose=False):
        pass

    def start_ping_broadcast(self):  # Every 5 minutes
        """Start periodic PROFILE broadcasting for presence."""
        import threading
        
        def broadcast_profile():
            while True:
                time.sleep(BROADCAST_INTERVAL)  # 5 minutes from vars.py
                if hasattr(self, 'user_id'):
                    # Re-broadcast PROFILE for presence
                    message = {
                        "TYPE": MSG_PROFILE,
                        "USER_ID": self.user_id,
                        "DISPLAY_NAME": self.display_name,
                        "STATUS": self.status,
                        "BROADCAST": True
                    }
                    self.netSystem.send_message(message)
                    if self.netSystem.verbose:
                        print(f"[BROADCAST] Sent periodic PROFILE update")
        
        # Start background thread for periodic broadcasting
        thread = threading.Thread(target=broadcast_profile, daemon=True)
        thread.start()

    def get_known_peers(self):
        pass

    def get_user_posts(self, user_id):
        pass

    def is_following(self, user_id):
        pass

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