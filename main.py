import threading
import time
from network_System import networkSystem
from msg_System import msgSystem
from file_game import fileGameSystem
from grp_ui import groupUISystem
from vars import *

class LSNPClient:
    def __init__(self, user_id, display_name, port, verbose=False):
        self.networkSystem = networkSystem(args.port, verbose=verbose)
        self.msgSystem = msgSystem(self.networkSystem)
        self.fileGameSystem = fileGameSystem(self.networkSystem)
        self.groupUISystem = groupUISystem(
            self.networkSystem, 
            self.msgSystem, 
            self.fileGameSystem
        )
        self.user_id = args.user_id
        self.display_name = args.display_name
        self.verbose = args.verbose
        self.listen_port = args.port
        
    def start(self):
        # Start network listener
        self.networkSystem.start_listener()
        time.sleep(0.5)
        self.msgSystem.create_profile(self.user_id, self.display_name, status=True)

        # Send HELLO to user1 if not user1
        if self.user_id != 'user1@127.0.0.1':
            self.send_hello("127.0.0.1", 6969)

        # Start ping broadcaster
        # Start UI
        while True:
            print("\n== Chat Menu ==")
            print("1. Send POST")
            print("2. Send HELLO")
            print("3. Toggle verbose mode")
            print("4. Show known clients")
            print("5. Quit")

            choice = input("Enter choice: ").strip()

            if choice == "1":
                content = input("Enter post content: ")
                self.msgSystem.send_post(content)

            elif choice == "2":
                self.send_hello("127.0.0.1", 6969)

            elif choice == "3":
                self.networkSystem.toggle_verbose_mode()
                print("Verbose mode is now", "ON" if self.networkSystem.verbose else "OFF")

            elif choice == "4":
                print("Known clients:")
                for ip, port in self.networkSystem.known_clients:
                    print(f"  - {ip}:{port}")

            elif choice == "5":
                print("Exiting...")
                break

            else:
                print("Invalid choice. Try again.")

            time.sleep(0.5)

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
    parser.add_argument('--port', type=int, default=6969, help='Port to listen on')
    
    args = parser.parse_args()
    
    client = LSNPClient(args.user_id, args.display_name, args.port, args.verbose)
    client.start()