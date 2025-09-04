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
    
    # Create properly formatted HTML email
    if body:
        # Convert plain text to proper HTML with better formatting
        html_lines = body_with_footer.split('\n')
        html_content = []
        
        for line in html_lines:
            line = line.strip()
            if line == "---":
                html_content.append('<hr style="border: none; border-top: 1px solid #ccc; margin: 20px 0;">')
            elif line == "":
                html_content.append('<br>')
            else:
                html_content.append(f'<p style="margin: 10px 0; line-height: 1.6;">{line}</p>')
        
        # Create complete HTML email structure
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
    <div style="background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        {''.join(html_content)}
    </div>
    <div style="text-align: center; margin-top: 20px; color: #666; font-size: 12px;">
        <p>Sent by <a href="https://automailer.streamlit.app/" style="color: #007bff; text-decoration: none;">https://automailer.streamlit.app/</a></p>
    </div>
</body>
</html>"""
    else:
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
    <div style="background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <p style="margin: 10px 0; line-height: 1.6;">{footer_text}</p>
    </div>
</body>
</html>"""
    
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
