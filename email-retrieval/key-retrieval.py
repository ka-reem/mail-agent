from agentmail import AgentMail
from dotenv import load_dotenv
import os
import re

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv('AGENTMAIL_API_KEY')

client = AgentMail(api_key=api_key)

# Retrieve all messages
all_messages = client.inboxes.messages.list(inbox_id='hello@agentmail.to')

print(f"Found {all_messages.count} messages in the inbox.")

# Extract and print email content
api_keys = []
for message in all_messages:
    # Debugging: Print the structure of the message
    # print(f"Debug: Message structure: {message}")

    # Prioritize printing the content
    content = str(message[1]) if isinstance(message, tuple) and len(message) > 1 else ''

    # Find all occurrences of 'API key:' in the content
    matches = re.findall(r"API key: [a-f0-9]{64}", content)
    for match in matches:
        print(f"Filtered Content: {match}")
        api_keys.append(match)

# Save to a text file
# with open('extracted_api_keys.txt', 'w') as file:
#     for key in api_keys:
#         file.write(f"{key}\n")