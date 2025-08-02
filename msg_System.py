# Member 2

import time
import random
from vars import *

class msgSystem:
    def __init__(self, netSystem):
        self.netSystem = netSystem

    def create_profile(self, user_id, display_name, status, avatar_path=None):
        self.user_id = user_id
        self.display_name = display_name
        self.status = status
        pass

    def send_post(self, content, ttl=3600):
        user_id = self.user_id  # Assuming self.user_id = "dave@192.168.1.10"
        timestamp = int(time.time())
        message_id = f"{random.getrandbits(64):016x}"
        token = f"{user_id}|{timestamp + ttl}|broadcast"

        message = {
            "TYPE": "POST",
            "USER_ID": user_id,
            "CONTENT": content,
            "TTL": ttl,
            "MESSAGE_ID": message_id,
            "TOKEN": token,
            "BROADCAST": True
        }

        ip_address = user_id.rsplit('@', 1)[1]
        print(ip_address)

        self.netSystem.send_message(message, target_ip=ip_address, target_port=6969)

    def send_dm(self, to_user, content):
        message = {"type": "DM", "content": content}
        self.netSystem.send_message(message, target_ip="127.0.0.1", target_port=6969)
        pass

    def send_like(self, to_user, post_timestamp, action="LIKE"):
        pass

    def follow_user(self, user_id):
        pass

    def unfollow_user(self, user_id):
        pass

    def process_incoming_message(self, message):
        pass

    def display_message(self, message, verbose=False):
        pass

    def start_ping_broadcast(self):  # Every 5 minutes
        pass

    def get_known_peers(self):
        pass

    def get_user_posts(self, user_id):
        pass

    def is_following(self, user_id):
        pass

    def get_display_name(self, user_id):  # For pretty printing
        pass

    def store_valid_message(self, message):  # Store messages with valid tokens
        pass

    def get_all_posts(self):  # Show all valid posts
        pass

    def get_all_dms(self):  # Show all DMs
        pass

    def handle_profile_response(self, message):
        pass

    def encode_avatar(self, image_path):
        pass

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