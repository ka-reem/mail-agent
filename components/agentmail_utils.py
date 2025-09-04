import os
from dotenv import load_dotenv
from agentmail import AgentMail
from config import DISABLE_CREATE_NEW_INBOX, DISABLE_SPAM_FEATURES
import streamlit as st

# Load environment variables
load_dotenv()
api_key = os.getenv("AGENTMAIL_API_KEY")

# Initialize AgentMail client
client = AgentMail(api_key=api_key)

def create_inbox():
    """Create a new inbox using the AgentMail API."""
    # Production safety check
    if DISABLE_CREATE_NEW_INBOX:
        st.error("🚫 **Security Alert:** Inbox creation blocked for production safety.")
        raise Exception("Inbox creation disabled in production mode")
    
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
    # Production safety check - prevent spam-like behavior
    if DISABLE_SPAM_FEATURES:
        # Add basic rate limiting and validation
        if not recipient or not subject or not body:
            raise Exception("Invalid email parameters")
        
        # # Check for spam-like patterns (basic validation)
        # if len(body) < 10:
        #     st.warning("⚠️ Very short email body detected - please ensure legitimate use.")
    
    # Add visible footer to email body
    footer_text = "\n\n---\nSent by https://automailer.streamlit.app/"
    
    # Add footer to both text and HTML versions
    body_with_footer = f"{body}{footer_text}"
    
    # Convert body to HTML and add footer
    if body:
        # Convert plain text to HTML
        html_body = body_with_footer.replace('\n\n', '</p><p>').replace('\n', '<br>')
        html_body = f"<p>{html_body}</p>"
    else:
        html_body = f"<p>{footer_text}</p>"
    
    return client.inboxes.messages.send(
        inbox_id=inbox_id,
        to=recipient,
        subject=subject,
        text=body_with_footer,
        html=html_body
    )

def list_messages(inbox_id):
    """List all messages in an inbox."""
    return client.inboxes.messages.list(inbox_id=inbox_id)

def get_message(inbox_id, message_id):
    """Retrieve a specific message."""
    return client.inboxes.messages.get(inbox_id=inbox_id, message_id=message_id)
