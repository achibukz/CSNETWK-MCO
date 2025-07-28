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
        
    def start(self):
        # Start network listener
        self.networkSystem.start_listener()
        self.msgSystem.send_dm("here", "CONTENT!!!")

        # Start ping broadcaster
        # Start UI
        while True:
            pass

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