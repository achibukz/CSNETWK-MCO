#!/usr/bin/env python3
"""
Simple test script for LSNP file transfer functionality.
Tests the new file transfer implementation against LSNP specifications.
"""

import os
import time
import tempfile
from main import LSNPClient

def create_test_file(content="Hello, this is a test file for LSNP file transfer!"):
    """Create a temporary test file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        return f.name

def test_file_transfer():
    """Test basic file transfer functionality."""
    print("=== LSNP File Transfer Test ===")
    
    # Create test file
    test_file = create_test_file("This is a test file for LSNP file transfer testing.\nLine 2 of the test file.\nEnd of file.")
    print(f"Created test file: {test_file}")
    
    try:
        # Create two clients
        sender = LSNPClient("sender@127.0.0.1", "Sender", 50999, verbose=True)
        receiver = LSNPClient("receiver@127.0.0.1", "Receiver", 51000, verbose=True)
        
        # Start both clients
        sender.start()
        receiver.start()
        
        # Give them time to start
        time.sleep(2)
        
        # Test file offer
        print("\n--- Testing file offer ---")
        file_id = sender.fileGameSystem.send_file("receiver@127.0.0.1", test_file, "Test file description")
        print(f"File offer sent with ID: {file_id}")
        
        # Give time for offer to be received
        time.sleep(1)
        
        # Check pending offers on receiver
        print("\n--- Checking pending offers on receiver ---")
        pending_offers = receiver.fileGameSystem.get_pending_file_offers()
        print(f"Receiver has {len(pending_offers)} pending offers")
        
        if pending_offers:
            # Accept the first offer
            first_offer_id = list(pending_offers.keys())[0]
            print(f"Accepting offer: {first_offer_id}")
            receiver.fileGameSystem.accept_file_offer(first_offer_id)
            
            # Give time for file transfer to complete
            time.sleep(5)
            
            # Check if file was received
            downloads_dir = "downloads"
            if os.path.exists(downloads_dir):
                files = os.listdir(downloads_dir)
                print(f"Files in downloads directory: {files}")
                
                if files:
                    # Check content of received file
                    received_file = os.path.join(downloads_dir, files[0])
                    with open(received_file, 'r') as f:
                        received_content = f.read()
                    print(f"Received file content: {received_content}")
                    
                    # Compare with original
                    with open(test_file, 'r') as f:
                        original_content = f.read()
                    
                    if received_content == original_content:
                        print("✅ File transfer successful! Content matches.")
                    else:
                        print("❌ File transfer failed! Content mismatch.")
                else:
                    print("❌ No files received in downloads directory.")
            else:
                print("❌ Downloads directory not created.")
        else:
            print("❌ No pending file offers received.")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        try:
            sender.stop()
            receiver.stop()
        except:
            pass
        
        # Remove test file
        if os.path.exists(test_file):
            os.unlink(test_file)
            print(f"Cleaned up test file: {test_file}")

if __name__ == "__main__":
    test_file_transfer()
