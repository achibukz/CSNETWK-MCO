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
        self.known_clients = set()

    def setup_socket(self):
        self.serverSocket = socket(AF_INET, SOCK_DGRAM) # SOCK_DGRAM -> UDP
        self.serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # allows socket to reuse address

        #Prepare a sever socket
        self.serverSocket.bind(('127.0.0.1', self.port))
        print(f"Ready to receive on port {self.port}...")

        while True:
            self.receive_message()
        pass

    def start_listener(self):
        # Run it in the background
        thread = threading.Thread(target=self.setup_socket, daemon=True)
        thread.start()

    def send_message(self, message, target_ip=50999, target_port=6969):  # None for broadcast
        """Send a JSON message via UDP to a target IP and port or everybody (if broadcast)."""
        print("SENDING THE FF:")
        print(message)
        print("-----")
        try:
            json_message = json.dumps(message)

            with socket(AF_INET, SOCK_DGRAM) as clientSocket:
                if message["BROADCAST"]:
                    print("BROADCASTING!!!")
                    clientSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
                    
                    for ip, port in self.known_clients:
                        local_ip, local_port = clientSocket.getsockname()

                        clientSocket.sendto(json_message.encode(), (ip, port))

                        if self.verbose:
                            # Log sender and receiver
                            print(f"[SEND] From {local_ip}:{local_port} To {ip}:{port}")
                else:
                    with socket(AF_INET, SOCK_DGRAM) as clientSocket:
                        clientSocket.sendto(json_message.encode(), (target_ip, target_port))
                        local_ip, local_port = clientSocket.getsockname()
                        print(f"[SEND] From {local_ip}:{local_port} To {target_ip}:{target_port}")

                    if self.verbose:
                        print(f"[SEND] To {target_ip}:{target_port} → {json_message}")

        except Exception as e:
            if self.verbose:
                print(f"[ERROR] Failed to send message: {e}")
        pass

    def receive_message(self):
        print("RECEOVED!!!")
        try:
            data, addr = self.serverSocket.recvfrom(4096) # addr = ip, port
            raw_message = data.decode()

            # if self.verbose:
            print(f"[RECEIVED] From {addr} → {raw_message}")

            listening_port = raw_message.get("LISTEN_PORT", addr[1]) # addr 1 is sending port, and it's just a fallback in case listen port doesnt exist
            self.known_clients.add(raw_message.get("LISTEN_PORT", addr[1]))

            self.parse_message(raw_message, addr)

        except Exception as e:
            print(f"[ERROR] Failed to receive message: {e}")

        pass

    def parse_message(self, raw_message, sender_addr):
        print("PARSING!!!")
        try:
            message = json.loads(raw_message)
            msg_type = message.get("TYPE")
            print(raw_message)
            print(msg_type)

            """ if msg_type == "POST":
                # self.handle_post(message, sender_addr)
                pass
             elif msg_type == "DM":
                # self.handle_dm(message, sender_addr)
                pass 
            else:
                print(f"[WARN] Unknown message type: {msg_type}") """

        except Exception as e:
            print(f"[ERROR] Failed to parse message: {e}")

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