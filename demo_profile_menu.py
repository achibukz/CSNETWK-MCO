#!/usr/bin/env python3
"""
Demo script showing the new Edit Profile menu option
"""

def show_menu_demo():
    """Demonstrate the updated menu with Edit Profile option"""
    print("=== LSNP Client Menu (Updated) ===")
    print("1. Send POST")
    print("2. Send HELLO")
    print("3. Send DM")
    print("4. Toggle verbose mode")
    print("5. Show known clients")
    print("6. Show known peers and their display names")
    print("7. Show all valid posts")
    print("8. Show all DMs")
    print("9. Test message crafting")
    print("10. Follow user")
    print("11. Unfollow user")
    print("12. Show following/followers")
    print("13. Edit profile  ← NEW!")
    print("14. Quit")
    print()
    print("=== Edit Profile Options ===")
    print("1. Display Name - Change your visible name")
    print("2. Status - Update your status message")
    print("3. Avatar - Set a profile picture (Base64 encoded)")
    print("4. Update all - Change name, status, and avatar")
    print("5. Cancel - Return to main menu")
    print()
    print("✅ Profile changes are automatically broadcasted to all peers!")
    print("✅ Supports avatar images (JPEG, PNG, GIF, BMP) up to 20KB")
    print("✅ Real-time profile updates across the network")

if __name__ == "__main__":
    show_menu_demo()
