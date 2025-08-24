import os
from dotenv import load_dotenv
from agentmail import AgentMail

# Load environment variables
load_dotenv()
api_key = os.getenv("AGENTMAIL_API_KEY")

# Initialize AgentMail client
client = AgentMail(api_key=api_key)

def create_inbox():
    """Create a new inbox using the AgentMail API."""
    print("Creating inbox...")
    inbox = client.inboxes.create()  # domain is optional
    print("Inbox created successfully!")
    print(inbox)
    return inbox

def list_inboxes():
    """List all available inboxes."""
    return client.inboxes.list()

def send_email(inbox_id, recipient, subject, body):
    """Send an email using the AgentMail API."""
    return client.inboxes.messages.send(
        inbox_id=inbox_id,
        to=recipient,
        subject=subject,
        text=body
    )

def list_messages(inbox_id):
    """List all messages in an inbox."""
    return client.inboxes.messages.list(inbox_id=inbox_id)

def get_message(inbox_id, message_id):
    """Retrieve a specific message."""
    return client.inboxes.messages.get(inbox_id=inbox_id, message_id=message_id)
