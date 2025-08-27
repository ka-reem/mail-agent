from agentmail import AgentMail
from dotenv import load_dotenv
import os
import re

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv('AGENTMAIL_API_KEY')

client = AgentMail(api_key=api_key)

all_inboxes = client.inboxes.list()
# print(f"Total Inboxes: {len(all_inboxes)}")
print(f"Total Inboxes: {len(all_inboxes.inboxes)}")
all_inboxes = client.inboxes.list()

# List all inboxes with their email addresses and display names
# print(f"Total Inboxes: {len(all_inboxes.inboxes)}\n")
# for inbox in all_inboxes.inboxes:
#     print(f"Email: {inbox.inbox_id}, Name: {inbox.display_name}")
    
# If you only want the email addresses:
print("\n--- Just Email Addresses ---")
for inbox in all_inboxes.inboxes:
    print(inbox.inbox_id)
    
# # If you only want the display names:
# print("\n--- Just Display Names ---")
# for inbox in all_inboxes.inboxes:
#     print(inbox.display_name)
    