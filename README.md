# LSNP Prototype

## Overview

This project is a prototype implementation of the **Local Social Networking Protocol (LSNP)**, a decentralized, UDP-based protocol for peer-to-peer messaging, file transfer, and basic social networking features on a local network.  
This prototype focuses on core messaging, file transfer, and peer discovery as described in the specs.txt.

This was accomplished as the final project for CSNETWK under section S15.

### Members

- Aki Bukuhan
- Stephen Co
- Hannah Lee
- Nathaniel Tolentino

---

## Menu Guide

- **1. Send POST**  
  Create and broadcast a public post to all peers in the network.

- **2. Send HELLO**  
  Broadcast a `HELLO` message to announce your presence to other peers.

- **3. Send DM**  
  Send a **direct message** to a specific user by entering their `user_id` and message content.

- **4. Toggle verbose mode**  
  Enable or disable **verbose mode** for the network listener.  
  Verbose mode shows more detailed logs for debugging and monitoring.

- **5. Show known clients**  
  Display the list of **unique known clients** (IP and port).  
  If verbose mode is ON, also shows all client entries, including duplicates.

- **6. Show known peers and their display names**  
  List all known peers along with their associated display names.

- **7. Show all valid posts**  
  Display all valid posts received from the network.

- **8. Show all DMs**  
  Display all valid direct messages received.

- **9. Test message crafting**  
  Run internal tests for crafting different types of LSNP messages.

- **10. Follow user**  
  Follow a specific user to receive updates from them.

- **11. Unfollow user**  
  Stop following a user.

- **12. Show following/followers**  
  Display the list of users you follow and users who follow you.

- **13. Edit profile**  
  Update your display name and profile status message.

- **14. Like/Unlike a post**  
  Like or unlike a specific post in the network.

- **15. Show token validation stats**  
  View statistics about token validation for messages.

- **16. Show valid messages log**  
  Display a log of all valid messages received and processed.

- **17. Revoke a token**  
  Manually revoke a token to invalidate its associated message.

- **18. 🎮 Tic-Tac-Toe Game**  
  Play a game of Tic-Tac-Toe with another user in the network.

- **19. 📁 Send File**  
  Send a file to another user over the LSNP network.

- **20. 📁 File Management**  
  Manage your received and sent files (view, delete, organize).

- **21. 👥 Create Group**  
  Create a new group for group messaging.

- **22. 👥 Update Group**  
  Update group details such as name, members, or settings.

- **23. 👥 Send Group Message**  
  Send a message to a specific group.

- **24. 👥 Show My Groups**  
  Display the list of groups you are a member of.

- **25. 👥 Show Group Members**  
  Show all members of a selected group.

- **26. 👥 Show Group Messages**  
  View all messages sent within a specific group.

- **27. Quit**  
  Exit the LSNP Client application.

---

## File Structure

- **main.py**  
  The main entry point and user interface for the LSNP client. Handles user input, menu navigation, and calls into the protocol logic for messaging, file transfer, and games.

- **network_System.py**  
  Handles all UDP networking, including sending and receiving LSNP messages, parsing messages, maintaining a list of known clients, and routing messages to the appropriate subsystem (messaging, file transfer, games).

- **msg_System.py**  
  Implements the core LSNP messaging logic:  
  - Profile management and broadcasting  
  - Posts, DMs, follow/unfollow, likes  
  - Token validation and revocation  
  - ACK handling and retry logic  
  - Known peers and message logs

- **file_game.py**  
  Implements file transfer and game logic:  
  - File offer, accept, chunking, and reconstruction  
  - Handles incoming file offers and manages file transfer state  
  - (Stub) Game logic for Tic-Tac-Toe and group features

- **grp_ui.py**  
  Provides the **Group Management User Interface** for LSNP.  
  - Interfaces with `msg_System` to create, update, and manage groups  
  - Displays group lists, group members, and recent group messages  
  - Processes group-related incoming messages  
  - Includes a command-line interface (`start_cli`) for group operations  
  - Integrates optional status displays for games, file transfers, and peers  
  - Supports toggling verbose mode and validating group membership

- **vars.py**  
  Defines all **global constants** and **protocol-wide configuration values** for LSNP:  
  - **Network settings**: Port numbers, broadcast intervals, retry timeouts, and limits  
  - **Token scopes**: Access categories for chat, file transfer, broadcasts, follows, games, and groups  
  - **Message types**: Identifiers for all LSNP message operations (posts, DMs, likes, file chunks, group updates, etc.)  
  - **Game constants**: Tic-Tac-Toe board size and winning combinations  
  - **File transfer limits**: Maximum chunk size and total file size

- **specs.txt**  
  The RFC-style protocol specification for LSNP, including message formats, field descriptions, and protocol rules.

- **milestone.txt**  
  The grading rubric and milestone breakdown for the project.

---
