# Member 1
import threading
import time

from vars import *
from socket import *

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
        """Send an LSNP message via UDP to a target IP and port or everybody (if broadcast)."""
        if self.verbose:
            print("SENDING THE FF:")
            print(message)
            print("-----")
        try:
            # Convert to LSNP format (key-value pairs with \n\n terminator)
            lsnp_message = self._dict_to_lsnp(message)
            
            with socket(AF_INET, SOCK_DGRAM) as clientSocket:
                if message.get("BROADCAST", False):
                    if self.verbose:
                        print("Broadcasting!!!")
                    clientSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

                    for ip, port in self.known_clients:
                        if self.verbose:
                            print("Known client:")
                            print(f"{ip} {port}")
                        local_ip, local_port = clientSocket.getsockname()
                        # Don't send to self
                        if not (ip == "127.0.0.1" and port == self.port):
                            clientSocket.sendto(lsnp_message.encode(), (ip, port))

                        if self.verbose:
                            # Log sender and receiver
                            print(f"[SEND] From {local_ip}:{local_port} To {ip}:{port}")
                else:
                    # Don't send to self when sending unicast
                    if not (target_ip == "127.0.0.1" and target_port == self.port):
                        clientSocket.sendto(lsnp_message.encode(), (target_ip, target_port))
                        local_ip, local_port = clientSocket.getsockname()
                        print(f"[SEND] From {local_ip}:{local_port} To {target_ip}:{target_port}")

                        if self.verbose:
                            print(f"[SEND] To {target_ip}:{target_port} → {lsnp_message}")

        except Exception as e:
            if self.verbose:
                print(f"[ERROR] Failed to send message: {e}")

    def _dict_to_lsnp(self, message_dict):
        """Convert a dictionary to LSNP key-value format."""
        lines = []
        for key, value in message_dict.items():
            if key != "BROADCAST":  # Don't include internal flags in LSNP message
                lines.append(f"{key}: {value}")
        return "\n".join(lines) + "\n\n"

    def _lsnp_to_dict(self, lsnp_message):
        """Convert LSNP key-value format to dictionary."""
        lines = lsnp_message.strip().split('\n')
        message_dict = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                message_dict[key.strip()] = value.strip()
        return message_dict

    def receive_message(self):
        if self.verbose:
            print("RECEIVED!!!")
        try:
            data, addr = self.serverSocket.recvfrom(4096) # addr = ip, port
            raw_message = data.decode()
            message = self._lsnp_to_dict(raw_message)

            if self.verbose:
                print(f"[RECEIVED] From {addr} → {message}")

            listening_port = message.get("LISTEN_PORT", addr[1]) # addr 1 is sending port, and it's just a fallback in case listen port doesnt exist
            # Only add to known clients if it's not ourselves
            if not (addr[0] == "127.0.0.1" and int(listening_port) == self.port):
                self.known_clients.add((addr[0], int(listening_port)))
                if self.verbose:
                    print(f"Adding client: {addr[0]}:{listening_port}")

            self.parse_message(message, addr)

        except Exception as e:
            print(f"[ERROR] Failed to receive message: {e}")

    def parse_message(self, message, sender_addr):
        if self.verbose:
            print("PARSING!!!")
        try:
            msg_type = message.get("TYPE")
            if self.verbose:
                print(f"Message type: {msg_type}")
                print(f"Full message: {message}")

            # Route messages to appropriate systems
            if msg_type in ["PROFILE", "POST", "DM", "PING", "LIKE", "FOLLOW", "UNFOLLOW"]:
                # Import here to avoid circular imports
                from msg_System import msgSystem
                # We need to find the msgSystem instance - this should be handled differently
                # For now, just print the message
                print(f"[{msg_type}] {message}")
            elif msg_type in ["TICTACTOE_INVITE", "TICTACTOE_MOVE", "TICTACTOE_RESULT"]:
                print(f"[GAME] {message}")
            elif msg_type in ["GROUP_CREATE", "GROUP_UPDATE", "GROUP_MESSAGE"]:
                print(f"[GROUP] {message}")
            elif msg_type in ["FILE_OFFER", "FILE_CHUNK", "FILE_RECEIVED"]:
                print(f"[FILE] {message}")
            elif msg_type == "HELLO":
                print(f"[HELLO] {message.get('DATA', 'Hello message')}")
            else:
                print(f"[WARN] Unknown message type: {msg_type}")

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