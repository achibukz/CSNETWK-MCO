# Member 1
import threading
import time

from vars import *
from socket import *
import json

class networkSystem: # NOTE: Should probs pass the ui class here to acomplish printing as well
    def __init__(self, port, verbose=False):
        self.port = port
        self.verbose = verbose

    def setup_socket(self):
        serverSocket = socket(AF_INET, SOCK_DGRAM) # SOCK_DGRAM -> UDP
        serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # allows socket to reuse address

        #Prepare a sever socket
        serverSocket.bind(('', self.port))
        print(f"Ready to receive on port {self.port}...")

        while True:
            message, clientAddress = serverSocket.recvfrom(2048)
            print(f"Received message: {message.decode()} from {clientAddress}")
            # Echo or respond back if needed
            serverSocket.sendto(b"Got your message", clientAddress)
        pass

    def start_listener(self):
        # Run it in the background
        thread = threading.Thread(target=self.setup_socket, daemon=True)
        thread.start()

    def send_message(self, message, target_ip=50999, target_port=6969):  # None for broadcast
        """Send a JSON message via UDP to a target IP and port."""
        try:
            json_message = json.dumps(message)
            with socket(AF_INET, SOCK_DGRAM) as clientSocket:
                clientSocket.sendto(json_message.encode(), (target_ip, target_port))

            if self.verbose:
                print(f"[SEND] To {target_ip}:{target_port} → {json_message}")

        except Exception as e:
            if self.verbose:
                print(f"[ERROR] Failed to send message: {e}")
        pass

    def receive_message(self):
        pass

    def parse_message(self, raw_message):
        pass

    def validate_token(self, token, scope, sender_ip):
        pass

    def is_token_revoked(self, token):
        pass

    def revoke_token(self, token):
        pass

    def send_ack(self, message_id, status="RECEIVED"):
        pass

    def retry_message(self, message, max_retries=3):
        pass

    def log_verbose(self, message, msg_type="INFO"):
        pass

    def toggle_verbose_mode(self):
        self.verbose = not self.verbose

    def get_broadcast_address(self):
        pass

    def simulate_packet_loss(self, loss_rate=0.1):  # For testing
        pass

    def validate_ip_match(self, message, sender_ip):
        pass

    def craft_test_message(self, msg_type, **kwargs):  # For test suite
        pass