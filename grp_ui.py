# Member 4

from vars import *

class groupUISystem:
    def __init__(self, netSystem, msgSystem, fileGameSystem):
        self.netSystem = netSystem
        self.msgSystem = msgSystem
        self.fileGameSystem = fileGameSystem

    def create_group(self, group_id, group_name, members):
        pass

    def update_group(self, group_id, add_members=[], remove_members=[]):
        pass

    def send_group_message(self, group_id, content):
        pass

    def process_group_update(self, message):
        pass

    def display_groups(self):  # Show all groups user belongs to
        pass

    def display_group_members(self, group_id):
        pass

    def display_group_messages(self, group_id):  # Show only incoming group messages
        pass

    def start_cli(self):
        pass

    def process_command(self, command):
        pass

    def display_help(self):
        pass

    def display_status(self):
        pass

    def run_interactive_mode(self):
        pass

    def show_available_commands(self):
        pass

    def validate_group_membership(self, group_id, user_id):
        pass

    def handle_group_creation(self, message):
        pass

    def handle_group_update(self, message):
        pass

    def handle_group_message(self, message):
        pass

    def display_terminal_grid(self):  # For game boards
        pass

    def format_message_display(self, message, verbose=False):
        pass

    def prompt_user_input(self, prompt):
        pass

    def display_peer_list(self):
        pass

    def display_game_status(self):
        pass

    def display_file_transfers(self):
        pass

    def toggle_verbose_from_ui(self):
        pass