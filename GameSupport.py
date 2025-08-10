import socket
import time
import random
import sys
import threading

from vars import *
from network_System import *

LSNP_PORT = 50999

def time_stamp():
    return int(time.time())

def make_message():
    return f"{int(time.time()*1000):x}"

def token(user_ip):
    return f"{user_ip}|{int(time.time())+3600}|game"

def lsnp(fields: dict):
    lines = []
    for k,v in fields.items():
        lines.append(f"{k}: {v}")
    return "\n".join(lines) + "\n"

def parse_lsnp(raw: str):
    out = {}
    for line in raw.splitlines():
        if": " in line:
            k,v = line.split(": ", 1)
            out[k.strip()] = v.strip()
    return out

def print_board(board):
    print()
    print(f" {board[0]} | {board[1]} {board[2]}")
    print("-----------")
    print(f" {board[3]} | {board[4]} {board[5]}")
    print("-----------")
    print(f" {board[6]} | {board[7]} {board[8]}")
    print("-----------")

class TicTacToe:
    def __init__(self, username, listen_port = LSNP_PORT, verbose = False):
        self.user = username
        self.listen_port = listen_port
        self.verbose = verbose

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", self.listen_port))

        self.board = [" "] * GAME_BOARD_SIZE
        self.gameID = None
        self.my_play = None
        self.opponent_play = None
        self.opponent_ip = None
        self.turn = 0
        self.is_turn = False

        t = threading.Thread(target = self.listen_loop, daemon = True)
        t.start()

    def local_address(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def invite(self, target_ip, gameID = None, play = "X"):
        if gameID is None:
            gameID = f"g{random.randint(0,255)}"
        self.gameID = gameID
        self.opponent_ip = target_ip
        self.my_play = play
        self.opponent_play = "O" if play == "X" else "X"
        self.is_turn = (self.my_play == "X")
        self.board = [" "] * GAME_BOARD_SIZE
        self.turn = 0

        fields = {
            "TYPE": MSG_TICTACTOE_INVITE,
            "FROM": f"{self.user}@{self.local_address()}",
            "TO": f"player@{target_ip}",
            "GAMEID": self.gameID,
            "MESSAGE_ID": make_message(),
            "SYMBOL": self.my_play,
            "TIMESTAMP": time_stamp(),
            "TOKEN": token()
        }
        lsnp = lsnp(fields)
        self.send_raw(lsnp, target_ip)

        if self.verbose:
            print("INVITE SENT")
            print(lsnp)
        
    def move(self, position):
        if self.opponent_ip is None or self.gameID is None:
            print("No active game / opponent. Invite someone or wait for invite.")
            return
        if not self.is_turn:
            print("It's not your turn.")
            return
        if position < 0 or position >= GAME_BOARD_SIZE:
            print("Position out of range (0-8).")
            return
        if self.board[position] != " ":
            print("Position already taken.")
            return
        
        self.board[position] = self.my_play
        self.turn += 1

        fields = {
            "TYPE": MSG_TICTACTOE_MOVE,
            "FROM": f"{self.user}@{self.local_address()}",
            "TO": f"player@{self.opponent_ip}",
            "GAMEID": self.gameID,
            "MESSAGE_ID": make_message(),
            "POSITION": position,
            "SYMBOL": self.my_play,
            "TURN": self.turn,
            "TOKEN": token(),
            "TIMESTAMP": time_stamp()
        }
        lsnp = lsnp(fields)
        self.send_raw(lsnp, self.opponent_ip)

        print_board(self.board)

        winner = self.check_result()
        if winner: 
            self.result(winner)
        else:
            self.is_turn = False
    
    def result(self, winner):
        if winner == "DRAW":
            result_field = "DRAW"
            winning_line = ""
        else:
            result_field = "WIN" if winner == self.my_play else "LOSS"
            line = self.winning_line(winner)
            winning_line = ",".join(map(str, line)) if line else ""

        fields = {
            "TYPE": MSG_TICTACTOE_RESULT,
            "FROM": f"{self.user}@{self.local_address()}",
            "TO": f"player@{self.opponent_ip}",
            "GAMEID": self.gameID,
            "MESSAGE_ID": make_message(),
            "RESULT": result_field,
            "SYMBOL": winner if winner != "DRAW" else "",
            "WINNING_LINE": winning_line,
            "TIMESTAMP": time_stamp()
        }
        lsnp = lsnp(fields)
        self.send_raw(lsnp, self.opponent_ip)

        print_board(self.board)
        print(f"Game result sent: {result_field}")

        self.reset()
    
    def listen_loop(self):
        while True:
            try:
                data, address = self.sock.recvfrom(4096)
                raw = data.decode(errors="ignore")
                parsed = parse_lsnp(raw)

                if self.verbose:
                    print(f"\n RECEIVED RAW from {address[0]}\n {raw}")
                
                self.process(parsed, address)
            except Exception as e:
                if self.verbose:
                    print("LISTENER ERROR", e)
    
    def process(self, message_dict, address):
        messagetype = message_dict.get("TYPE")
        sender_full = message_dict.get("FROM", "")
        sender_ip = address[0]

        if messagetype == MSG_TICTACTOE_INVITE:
            incoming_gameID = message_dict.get("GAMEID")
            symbol = message_dict.get("SYMBOL", "X")
            self.gameID = incoming_gameID
            self.opponent_ip = sender_ip
            self.opp_port = LSNP_PORT
            
            self.opponent_play = symbol
            self.my_play = "O" if symbol == "X" else "X"

            self.is_turn = (self.my_play == "X")
            self.turn = 0
            self.board = [" "] * GAME_BOARD_SIZE

            username = sender_full.split("@")[0] if "@" in sender_full else sender_full
            print(f"\n{username} is inviting you to play tic-tac-toe.")
        
        elif messagetype == MSG_TICTACTOE_MOVE:
            try: 
                position = int(message_dict.get("POSITION"))
            except:
                if self.verbose:
                    print("ERROR: Move missing, invalid POSITION")
                return
            
            symbol = message_dict.get("SYMBOL")
            if message_dict.get("GAMEID") != self.gameID:
                if self.verbose: 
                    print("ERROR: received move for a different GAMEID")
                return
            
            if 0 <= position < GAME_BOARD_SIZE and self.board[position] == " ":
                self.board[position] = symbol
                self.turn = int(message_dict.get("TURN", self.turn + 1))
                print_board(self.board)
                winner = self.check_result()
                if winner:
                    self.is_turn = False
                else:
                    self.is_turn = True
            else: 
                if self.verbose:
                    print("ERROR: Invalid move")
        
        elif messagetype == MSG_TICTACTOE_RESULT:
            result = message_dict.get("RESULT", "")
            win_line = message_dict.get("WINNING_LINE", "")
            print_board(self.board)
            print(f"Game result: {result} (winning line: {win_line})")
            self.reset()
        else:
            if self.verbose:
                print("INFO Unknown message type", messagetype)
    
    def send_raw(self, lsnp, target_ip):
        try:
            self.socket.sendto(lsnp.encode(), (target_ip, LSNP_PORT))
            if self.verbose:
                print(f"SENT TO {target_ip}:{LSNP_PORT}\n{lsnp}")
        except Exception as e:
            print("Failed to send message", e)
    
    def check_result(self):
        for a,b,c in WINNING_LINES:
            if self.board[a] != " " and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        if " " not in self.board:
            return "DRAW"
        return None
    
    def winning_line(self, symbol):
        for a,b,c in WINNING_LINES:
            if self.board[a] == symbol and self.board[b] == symbol and self.board[c] == symbol:
                return (a,b,c)
        return ()
    
    def reset(self):
        self.board = [" "] * GAME_BOARD_SIZE
        self.gameID = None
        self.my_play = None
        self.opponent_play = None
        self.opponent_ip = None 
        self.turn = 0
        self.is_turn = False

        if self.verbose:
            print("Game reset")