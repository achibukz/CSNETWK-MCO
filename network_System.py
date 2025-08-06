# Member 1
import threading
import time
import platform

from vars import *
from socket import *

class networkSystem: # NOTE: Should probs pass the ui class here to acomplish printing as well
    def __init__(self, port, verbose=False):
        self.port = port
        self.verbose = verbose
        self.known_clients = set()
        self.msg_system = None  # Will be set by main.py

    def setup_socket(self):
        self.serverSocket = socket(AF_INET, SOCK_DGRAM) # SOCK_DGRAM -> UDP
        self.serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # allows socket to reuse address

        if platform.system() == "Darwin":
            try:
                self.serverSocket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)  # macOS fix
            except AttributeError:
                print("[WARN] SO_REUSEPORT not supported on this platform")

        #Prepare a sever socket - bind to all interfaces to receive from other devices
        self.serverSocket.bind(('0.0.0.0', self.port))
        print(f"Ready to receive on port {self.port}...")

        while True:
            self.receive_message()
        pass

    def start_listener(self):
        # Run it in the background
        thread = threading.Thread(target=self.setup_socket, daemon=True)
        thread.start()

    def send_message(self, message, target_ip=LSNP_PORT, target_port=LSNP_PORT):  # None for broadcast
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

                    # Send to known clients
                    for ip, port in self.known_clients:
                        if self.verbose:
                            print("Known client:")
                            print(f"{ip} {port}")
                        
                        # Get our local IP for better self-detection
                        try:
                            temp_socket = socket(AF_INET, SOCK_DGRAM)
                            temp_socket.connect(("8.8.8.8", 80))
                            local_ip = temp_socket.getsockname()[0]
                            temp_socket.close()
                        except:
                            local_ip = "127.0.0.1"
                        
                        # Don't send to self
                        is_self = (ip == local_ip and port == self.port) or \
                                 (ip == "127.0.0.1" and port == self.port)
                        
                        if not is_self:
                            clientSocket.sendto(lsnp_message.encode(), (ip, port))
                            if self.verbose:
                                local_send_ip, local_send_port = clientSocket.getsockname()
                                print(f"[SEND] From {local_send_ip}:{local_send_port} To {ip}:{port}")
                        elif self.verbose:
                            print(f"Skipping self: {ip}:{port}")
                    
                    # Also send to broadcast address for device discovery
                    try:
                        broadcast_addr = "255.255.255.255"  # Limited broadcast
                        clientSocket.sendto(lsnp_message.encode(), (broadcast_addr, LSNP_PORT))
                        if self.verbose:
                            print(f"[BROADCAST] Sent to {broadcast_addr}:{LSNP_PORT}")
                    except Exception as e:
                        if self.verbose:
                            print(f"[WARN] Broadcast failed: {e}")
                else:
                    # Get our local IP for better self-detection
                    try:
                        temp_socket = socket(AF_INET, SOCK_DGRAM)
                        temp_socket.connect(("8.8.8.8", 80))
                        local_ip = temp_socket.getsockname()[0]
                        temp_socket.close()
                    except:
                        local_ip = "127.0.0.1"
                    
                    # Don't send to self when sending unicast
                    is_self = (target_ip == local_ip and target_port == self.port) or \
                             (target_ip == "127.0.0.1" and target_port == self.port)
                    
                    if not is_self:
                        clientSocket.sendto(lsnp_message.encode(), (target_ip, target_port))
                        local_send_ip, local_send_port = clientSocket.getsockname()
                        print(f"[SEND] From {local_send_ip}:{local_send_port} To {target_ip}:{target_port}")

                        if self.verbose:
                            print(f"[SEND] To {target_ip}:{target_port} -> {lsnp_message}")
                    elif self.verbose:
                        print(f"Skipping unicast to self: {target_ip}:{target_port}")

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
                key = key.strip()
                value = value.strip()
                
                # Try to convert numeric values back to int
                if value.isdigit():
                    value = int(value)
                
                message_dict[key] = value
        return message_dict

    def receive_message(self):
        if self.verbose:
            print("RECEIVED!!!")
        try:
            data, addr = self.serverSocket.recvfrom(4096) # addr = ip, port
            raw_message = data.decode()
            message = self._lsnp_to_dict(raw_message)

            if self.verbose:
                print(f"[RECEIVED] From {addr} -> {message}")

            # Get the correct listening port from the message
            listening_port = message.get("LISTEN_PORT", LSNP_PORT)  # Use standard port as fallback
            
            # Get our local IP to avoid adding ourselves as a client
            try:
                # Get our actual IP address
                temp_socket = socket(AF_INET, SOCK_DGRAM)
                temp_socket.connect(("8.8.8.8", 80))
                local_ip = temp_socket.getsockname()[0]
                temp_socket.close()
            except:
                local_ip = "127.0.0.1"  # fallback
            
            # Improved self-detection: use USER_ID if available, otherwise fall back to IP/port
            user_id = message.get("USER_ID")
            our_user_id = getattr(self.msg_system, 'user_id', None) if self.msg_system else None
            
            is_self = False
            if user_id and our_user_id:
                # Use USER_ID for self-detection (most reliable)
                is_self = (user_id == our_user_id)
                if self.verbose and is_self:
                    print(f"Ignoring self message: USER_ID {user_id}")
            else:
                # Fall back to IP/port detection for messages without USER_ID
                is_self = (addr[0] == local_ip and int(listening_port) == self.port) or \
                         (addr[0] == "127.0.0.1" and int(listening_port) == self.port)
                if self.verbose and is_self:
                    print(f"Ignoring self message: IP/port {addr[0]}:{listening_port}")
            
            if not is_self:
                # Add to known clients (set automatically prevents duplicates)
                client_tuple = (addr[0], int(listening_port))
                if client_tuple not in self.known_clients:
                    self.known_clients.add(client_tuple)
                    if self.verbose:
                        print(f"Adding NEW client: {addr[0]}:{listening_port}")
                elif self.verbose:
                    print(f"Already known client: {addr[0]}:{listening_port}")

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
            if msg_type in [MSG_PROFILE, MSG_POST, MSG_DM, MSG_PING, MSG_LIKE, MSG_FOLLOW, MSG_UNFOLLOW, MSG_ACK]:
                if self.msg_system:
                    self.msg_system.process_incoming_message(message)
                else:
                    # Fallback if msg_system not set
                    print(f"[{msg_type}] {message}")
            elif msg_type in [MSG_TICTACTOE_INVITE, MSG_TICTACTOE_MOVE, MSG_TICTACTOE_RESULT]:
                print(f"[GAME] {message}")
            elif msg_type in [MSG_GROUP_CREATE, MSG_GROUP_UPDATE, MSG_GROUP_MESSAGE]:
                print(f"[GROUP] {message}")
            elif msg_type in [MSG_FILE_OFFER, MSG_FILE_CHUNK, MSG_FILE_RECEIVED]:
                print(f"[FILE] {message}")
            elif msg_type == "HELLO":  # HELLO is not in specs, so keep as string
                hello_data = message.get('DATA', 'Hello message')
                listen_port = message.get('LISTEN_PORT', LSNP_PORT)
                sender_ip = sender_addr[0]
                sender_user_id = message.get('USER_ID')
                sender_display_name = message.get('DISPLAY_NAME', 'Unknown User')
                
                # Add sender to known clients for peer discovery
                client_tuple = (sender_ip, listen_port)
                if client_tuple not in self.known_clients:
                    self.known_clients.add(client_tuple)
                    if self.verbose:
                        print(f"[HELLO] Added {sender_ip}:{listen_port} to known clients")
                
                print(f"[HELLO] {hello_data}")
                
                # If we have user info, create a peer entry and send PROFILE response
                if self.msg_system and sender_user_id and sender_display_name:
                    # Create peer entry from HELLO info
                    self.msg_system.known_peers[sender_user_id] = {
                        'display_name': sender_display_name,
                        'status': 'Online',
                        'avatar_type': None,
                        'avatar_data': None
                    }
                    if self.verbose:
                        print(f"[HELLO] Added peer: {sender_display_name} ({sender_user_id})")
                    
                    # Send PROFILE response if we have our own profile
                    if hasattr(self.msg_system, 'user_id'):
                        try:
                            response_message = {
                                "TYPE": MSG_PROFILE,
                                "USER_ID": self.msg_system.user_id,
                                "DISPLAY_NAME": self.msg_system.display_name,
                                "STATUS": getattr(self.msg_system, 'status', 'Online'),
                                "LISTEN_PORT": self.port,
                                "BROADCAST": False  # Unicast response
                            }
                            self.send_message(response_message, target_ip=sender_ip, target_port=listen_port)
                            if self.verbose:
                                print(f"[HELLO] Sent PROFILE response to {sender_ip}:{listen_port}")
                        except Exception as e:
                            if self.verbose:
                                print(f"[HELLO] Failed to send PROFILE response: {e}")
            else:
                print(f"[WARN] Unknown message type: {msg_type}")

        except Exception as e:
            print(f"[ERROR] Failed to parse message: {e}")

    def set_msg_system(self, msg_system):
        """Set the message system for proper routing."""
        self.msg_system = msg_system

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

    def get_unique_clients(self):
        """Get unique clients by IP, keeping only the standard port entries."""
        unique_clients = {}
        for ip, port in self.known_clients:
            if ip not in unique_clients:
                unique_clients[ip] = port
            elif port == LSNP_PORT:  # Prefer standard port if available
                unique_clients[ip] = port
        return [(ip, port) for ip, port in unique_clients.items()]

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