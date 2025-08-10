import time

class GameSuppport:
    def __init__(self, game, play):
        self.game = game
        self.play = play
        self.board = [" " for _ in range(9)]
        self.opponent_play = "O" if play == "X" else "X"
        self.turn = 1
        self.current_play = "X"

    def print_board(self):
        for i in range(0, 9, 3):
            print(f"{self.board[i]} | {self.board[i+1]} | {self.board[i+2]}")
            if i < 6:
                print("---------")
        print()
    
    def invite(self, from_address, to_address):
        message = f"""TYPE: TICTACTOE_INVITE
        FROM: {from_address}
        TO: {to_address}
        GAMEID: {self.game}
        SYMBOL: {self.play}
        TIMESTAMP: {int(time.time())}
        TOKEN: {from_address}|{int(time.time())+3600}|game
        """
        
    def move(self, from_address, to_address, position):
        if(self.board[position]!=" "):
            raise ValueError("Invalid move: Position already taken.")
        self.board[position] = self.current_play
        self.turn += 1
        message = f"""TYPE: TICTACTOE_MOVE
        FROM: {from_address}
        TO: {to_address}
        GAMEID: {self.game}
        MESSAGE_ID: f{int (time.time()*1000):x}
        POSITION: {position}
        SYMBOL: {self.current_play}
        TURN: {self.turn}
        TOKEN: {from_address}|{int(time.time())+3600}|game
        """
        self.print_board()
        self.current_play = self.opponent_play if self.current_play == self.play else self.play
        return message
    
    def result_message(self, from_address, to_address, result, win_condition=None):
        ts = int(time.time())
        wc = f"WIN_CONDITION: {','.join(map(str, win_condition))}" if win_condition else ""
        message = f"""TYPE: TICTACTOE_RESULT
        FROM: {from_address}
        TO: {to_address}
        GAMEID: {self.game}
        MESSAGE_ID: f{int (time.time()*1000):x}
        RESULT: {result}
        SYMBOL: {self.play}
        {wc}
        TIMESTAMP: {ts}"""
        self.print_board()
        print(f"Game over: {result}")
        return message