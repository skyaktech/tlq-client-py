#!/usr/bin/env python3
"""Example TLQ message consumer."""

import time
from tlq_client import TLQClient, TLQError


def consume_messages():
    """Consume messages from the TLQ queue."""
    with TLQClient() as client:
        # Check if server is healthy
        if not client.health_check():
            print("TLQ server is not available!")
            return
        
        print("Starting message consumer (Press Ctrl+C to stop)...")
        
        try:
            while True:
                try:
                    # Get messages from the queue
                    messages = client.get_messages(count=5)
                    
                    if not messages:
                        print("No messages available, sleeping...")
                        time.sleep(1)
                        continue
                    
                    for message in messages:
                        try:
                            # Process the message
                            print(f"Processing: {message.body} (ID: {message.id})")
                            
                            # Simulate work
                            time.sleep(0.5)
                            
                            # Mark as completed
                            client.delete_messages(message.id)
                            print(f"Completed: {message.id}")
                            
                        except Exception as e:
                            print(f"Failed to process {message.id}: {e}")
                            # Return to queue for retry
                            client.retry_messages(message.id)
                            
                except TLQError as e:
                    print(f"TLQ error: {e}")
                    time.sleep(5)  # Back off on errors
                    
        except KeyboardInterrupt:
            print("\nShutting down consumer...")


if __name__ == "__main__":
    consume_messages()