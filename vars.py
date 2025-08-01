# Network Configuration
LSNP_PORT = 50999
BROADCAST_INTERVAL = 300  # 5 minutes
RETRY_TIMEOUT = 2  # seconds
MAX_RETRIES = 3

# Token Scopes
SCOPE_CHAT = "chat"
SCOPE_FILE = "file"
SCOPE_BROADCAST = "broadcast"
SCOPE_FOLLOW = "follow"
SCOPE_GAME = "game"
SCOPE_GROUP = "group"

# Message Types
MSG_PROFILE = "PROFILE"
MSG_POST = "POST"
MSG_DM = "DM"
MSG_PING = "PING"
MSG_ACK = "ACK"
MSG_FOLLOW = "FOLLOW"
MSG_UNFOLLOW = "UNFOLLOW"
MSG_FILE_OFFER = "FILE_OFFER"
MSG_FILE_CHUNK = "FILE_CHUNK"
MSG_FILE_RECEIVED = "FILE_RECEIVED"
MSG_REVOKE = "REVOKE"
MSG_TICTACTOE_INVITE = "TICTACTOE_INVITE"
MSG_TICTACTOE_MOVE = "TICTACTOE_MOVE"
MSG_TICTACTOE_RESULT = "TICTACTOE_RESULT"
MSG_LIKE = "LIKE"
MSG_GROUP_CREATE = "GROUP_CREATE"
MSG_GROUP_UPDATE = "GROUP_UPDATE"
MSG_GROUP_MESSAGE = "GROUP_MESSAGE"

# Game Constants
GAME_BOARD_SIZE = 9
WINNING_LINES = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
    [0, 4, 8], [2, 4, 6]              # diagonals
]

# File Transfer
MAX_CHUNK_SIZE = 1024  # bytes
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB