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
        self.msgSystem = msgSystem(self.networkSystem)
        self.fileGameSystem = fileGameSystem(self.networkSystem)
        self.groupUISystem = groupUISystem(
            self.networkSystem, 
            self.msgSystem, 
            self.fileGameSystem
        )
        
        # Set up cross-references for proper message routing
        self.networkSystem.set_msg_system(self.msgSystem)
        
    def start(self):
        # Start network listener
        self.networkSystem.start_listener()
        time.sleep(0.5)
        self.msgSystem.create_profile(self.user_id, self.display_name, "Online and ready!")

        # Start periodic PROFILE broadcasting
        self.msgSystem.start_ping_broadcast()

        # Send HELLO to user1 if not user1
        if self.user_id != 'user1@127.0.0.1':
            self.send_hello("127.0.0.1", LSNP_PORT)

        # Start ping broadcaster
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
            print("10. Quit")

            choice = input("Enter choice: ").strip()

            if choice == "1":
                content = input("Enter post content: ")
                self.msgSystem.send_post(content)

            elif choice == "2":
                target_ip = input("Enter target IP (default: 127.0.0.1): ").strip() or "127.0.0.1"
                target_port = input(f"Enter target port (default: {LSNP_PORT}): ").strip()
                target_port = int(target_port) if target_port else LSNP_PORT
                self.send_hello(target_ip, target_port)

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
                for ip, port in self.networkSystem.known_clients:
                    print(f"  - {ip}:{port}")

            elif choice == "6":
                self.show_known_peers()

            elif choice == "7":
                self.show_all_posts()

            elif choice == "8":
                self.show_all_dms()

            elif choice == "9":
                self.test_message_crafting()

            elif choice == "10":
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
            "LISTEN_PORT": self.listen_port
        }
        lsnp_format = self.networkSystem._dict_to_lsnp(message)
        print("LSNP HELLO Message:")
        print(lsnp_format)

    def send_hello(self, target_ip, target_port):
        message = {
            "TYPE": "HELLO",
            "BROADCAST": False,
            "DATA": f"{self.display_name} is online",
            "LISTEN_PORT": self.listen_port
        }
        self.networkSystem.send_message(message, target_ip=target_ip, target_port=target_port)

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