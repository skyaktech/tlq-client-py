#!/usr/bin/env python3
"""Example TLQ message producer."""

from tlq_client import TLQClient


def produce_messages():
    """Produce sample messages to the TLQ queue."""
    with TLQClient() as client:
        # Check if server is healthy
        if not client.health_check():
            print("TLQ server is not available!")
            return
        
        print("Producing messages...")
        
        for i in range(10):
            message_id = client.add_message(f"Task {i}: Process important data")
            print(f"Queued task {i}: {message_id}")
        
        print("All messages queued successfully!")


if __name__ == "__main__":
    produce_messages()