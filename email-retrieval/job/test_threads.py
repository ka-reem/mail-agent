#!/usr/bin/env python3
"""
Test script to check unreplied threads in AgentMail
"""

import os
import sys

# Add the parent directory to the path to import our utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv
from agentmail import AgentMail

# Load environment variables
load_dotenv()

# Configuration
INBOX_ID = "givemeajob@agentmail.to"
HIRING_EMAIL = "hiring@agentmail.to"

# Initialize AgentMail client
agentmail_api_key = os.getenv("AGENTMAIL_API_KEY")
if not agentmail_api_key:
    raise Exception("AGENTMAIL_API_KEY not found in environment variables")

client = AgentMail(api_key=agentmail_api_key)

def test_unreplied_threads():
    """Test function to check unread threads specifically from givemeajob@agentmail.to"""
    print("🔍 Testing unread threads...")
    print(f"Inbox: {INBOX_ID}")
    print("-" * 50)
    
    try:
        # Get unread threads (they're already from our inbox context)
        threads = client.threads.list(labels=["unread"])
        
        print(f"Raw response type: {type(threads)}")
        
        # Access the threads from the response object
        actual_threads = threads.threads
        print(f"Found {len(actual_threads)} unread threads in {INBOX_ID}")
        
        if not actual_threads:
            print(f"❌ No unread threads found in {INBOX_ID}.")
        else:
            print(f"✅ Found {len(actual_threads)} unread threads in {INBOX_ID}!")
            
            # Let's work on the first unread thread
            thread_to_reply_to = actual_threads[0]
            print(f"First unread thread ID: {getattr(thread_to_reply_to, 'thread_id', 'N/A')}")
            print(f"Thread labels: {getattr(thread_to_reply_to, 'labels', 'N/A')}")
            
            # Get thread details
            thread_details = client.threads.get(actual_threads[0].thread_id)
            print(f"Thread details retrieved: {thread_details}")
            print(f"Thread has {len(thread_details.messages) if thread_details.messages else 0} messages")
            
            if thread_details.messages:
                print("Messages in thread:")
                for i, msg in enumerate(thread_details.messages):
                    print(f"  Message {i}: {type(msg)} - {msg}")
                    if hasattr(msg, 'id'):
                        print(f"    ID: {msg.id}")
                    if hasattr(msg, 'sender'):
                        print(f"    Sender: {msg.sender}")
                    if hasattr(msg, 'subject'):
                        print(f"    Subject: {msg.subject}")
                        
                last_message = thread_details.messages[-1]
                print(f"Last message: {last_message}")
                print(f"Last message ID: {getattr(last_message, 'id', 'N/A')}")
                print(f"Last message sender: {getattr(last_message, 'sender', 'N/A')}")
                print(f"Last message subject: {getattr(last_message, 'subject', 'N/A')}")
                
                text = getattr(last_message, 'text', '')
                if text:
                    print(f"Last message preview: {text[:100]}...")
                else:
                    print("Last message has no text")
            else:
                print("Thread has no messages")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_unreplied_threads()
