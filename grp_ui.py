# Member 4

from vars import *

class groupUISystem:
    def __init__(self, netSystem, msgSystem, fileGameSystem):
        self.netSystem = netSystem
        self.msgSystem = msgSystem
        self.fileGameSystem = fileGameSystem

    def create_group(self, group_id, group_name, members):
        """Create a new group - delegate to msgSystem."""
        return self.msgSystem.create_group(group_id, group_name, members)

    def update_group(self, group_id, add_members=[], remove_members=[]):
        """Update group membership - delegate to msgSystem."""
        return self.msgSystem.update_group(group_id, add_members, remove_members)

    def send_group_message(self, group_id, content):
        """Send message to group - delegate to msgSystem."""
        return self.msgSystem.send_group_message(group_id, content)

    def process_group_update(self, message):
        """Process group update message - delegate to msgSystem."""
        return self.msgSystem.handle_group_update_message(message)

    def display_groups(self):  # Show all groups user belongs to
        """Display all groups user belongs to."""
        groups = self.msgSystem.get_user_groups()
        if not groups:
            print("You are not a member of any groups.")
            return
        
        print("Your Groups:")
        for group in groups:
            print(f"  • {group['name']} ({group['group_id']}) - {group['member_count']} members")

    def display_group_members(self, group_id):
        """Display members of a specific group."""
        members = self.msgSystem.get_group_members(group_id)
        if not members:
            print(f"Group {group_id} not found or you're not a member.")
            return
        
        print(f"Members of group {group_id}:")
        for member in members:
            display_name = self.msgSystem.get_display_name(member)
            print(f"  • {display_name} ({member})")

    def display_group_messages(self, group_id):  # Show only incoming group messages
        """Display messages for a specific group."""
        messages = self.msgSystem.get_group_messages(group_id)
        if not messages:
            print(f"No messages in group {group_id}.")
            return
        
        print(f"Messages in group {group_id}:")
        for msg in messages[-10:]:  # Show last 10 messages
            from_user = msg['from']
            display_name = self.msgSystem.get_display_name(from_user)
            content = msg['content']
            print(f"  {display_name}: {content}")

    def start_cli(self):
        """Start group CLI interface."""
        print("Group Management CLI - Type 'help' for commands")
        
        while True:
            command = input("group> ").strip().lower()
            if command == 'quit' or command == 'exit':
                break
            elif command == 'help':
                self.display_help()
            else:
                self.process_command(command)

    def process_command(self, command):
        """Process CLI commands."""
        if command == 'list':
            self.display_groups()
        elif command.startswith('members '):
            group_id = command.split(' ', 1)[1]
            self.display_group_members(group_id)
        elif command.startswith('messages '):
            group_id = command.split(' ', 1)[1]
            self.display_group_messages(group_id)
        else:
            print("Unknown command. Type 'help' for available commands.")

    def display_help(self):
        """Display available commands."""
        print("Available commands:")
        print("  list                 - Show all your groups")
        print("  members <group_id>   - Show members of a group")
        print("  messages <group_id>  - Show messages in a group")
        print("  help                 - Show this help")
        print("  quit/exit           - Exit group CLI")

    def display_status(self):
        """Display group system status."""
        groups = self.msgSystem.get_user_groups()
        print(f"Groups: {len(groups)}")
        total_messages = sum(len(self.msgSystem.get_group_messages(g['group_id'])) for g in groups)
        print(f"Total group messages: {total_messages}")

    def run_interactive_mode(self):
        """Run interactive group management mode."""
        self.start_cli()

    def show_available_commands(self):
        """Show available group commands."""
        self.display_help()

    def validate_group_membership(self, group_id, user_id):
        """Validate if user is a member of the group."""
        members = self.msgSystem.get_group_members(group_id)
        return members and user_id in members

    def handle_group_creation(self, message):
        """Handle group creation message - delegate to msgSystem."""
        return self.msgSystem.handle_group_create_message(message)

    def handle_group_update(self, message):
        """Handle group update message - delegate to msgSystem."""
        return self.msgSystem.handle_group_update_message(message)

    def handle_group_message(self, message):
        """Handle group message - delegate to msgSystem."""
        return self.msgSystem.handle_group_message(message)

    def display_terminal_grid(self):  # For game boards
        """Display terminal grid for games (placeholder)."""
        print("Terminal grid display not implemented.")

    def format_message_display(self, message, verbose=False):
        """Format message display."""
        msg_type = message.get('TYPE', 'UNKNOWN')
        from_user = message.get('FROM', 'Unknown')
        
        if verbose:
            return f"[{msg_type}] From {from_user}: {message}"
        else:
            content = message.get('CONTENT', str(message))
            return f"{from_user}: {content}"

    def prompt_user_input(self, prompt):
        """Prompt user for input."""
        return input(prompt).strip()

    def display_peer_list(self):
        """Display list of known peers."""
        peers = self.msgSystem.get_known_peers()
        if not peers:
            print("No known peers.")
            return
        
        print("Known peers:")
        for user_id, info in peers.items():
            display_name = info.get('display_name', user_id)
            print(f"  • {display_name} ({user_id})")

    def display_game_status(self):
        """Display game status (placeholder)."""
        if hasattr(self.fileGameSystem, 'get_active_games'):
            games = self.fileGameSystem.get_active_games()
            print(f"Active games: {len(games)}")
        else:
            print("Game status not available.")

    def display_file_transfers(self):
        """Display file transfer status (placeholder)."""
        if hasattr(self.fileGameSystem, 'get_file_transfers'):
            transfers = self.fileGameSystem.get_file_transfers()
            print(f"Active file transfers: {len(transfers)}")
        else:
            print("File transfer status not available.")

    def toggle_verbose_from_ui(self):
        """Toggle verbose mode from UI."""
        if hasattr(self.netSystem, 'verbose'):
            self.netSystem.verbose = not self.netSystem.verbose
            print(f"Verbose mode: {'ON' if self.netSystem.verbose else 'OFF'}")
        else:
            print("Verbose mode control not available.")