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
        
        # Check for spam-like patterns (basic validation)
        if len(body) < 10:
            st.warning("⚠️ Very short email body detected - please ensure legitimate use.")
    
    # Convert plain text body into a professional-looking HTML email
    def _convert_text_to_html(text: str) -> str:
        import html as _html
        if not text:
            return ''

        escaped = _html.escape(text)
        lines = escaped.splitlines()

        content_parts = []
        para = []
        in_list = False

        def flush_para():
            nonlocal para
            if not para:
                return
            content_parts.append(f"<p style=\"margin:0 0 12px 0;line-height:1.6;color:#222;font-size:15px;\">{'<br/>'.join(para)}</p>")
            para = []

        for raw in lines:
            line = raw.strip()
            if not line:
                flush_para()
                continue

            if line.startswith(('- ', '* ')):
                if not in_list:
                    flush_para()
                    content_parts.append('<ul style="margin:0 0 12px 18px;padding:0;color:#222;font-size:15px;">')
                    in_list = True
                content_parts.append(f"<li style=\"margin-bottom:8px;\">{_html.escape(line[2:].strip())}</li>")
                continue

            if in_list:
                content_parts.append('</ul>')
                in_list = False

            para.append(line)

        flush_para()
        if in_list:
            content_parts.append('</ul>')

        # Professional card-style wrapper
        html_body = (
            '<!doctype html>'
            '<html><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width,initial-scale=1"/>'
            '</head>'
            '<body style="margin:0;padding:20px;background-color:#f4f6f8;font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, Helvetica, Arial, sans-serif;">'
            '<div style="max-width:600px;margin:0 auto;background:#ffffff;border-radius:8px;box-shadow:0 1px 3px rgba(16,24,40,0.08);overflow:hidden;">'
            '  <div style="padding:20px 24px;border-bottom:1px solid #eef1f4;background:linear-gradient(90deg,#fbfdff,#ffffff);">'
            f'    <h2 style="margin:0;font-size:18px;color:#0f172a;font-weight:600">{_html.escape(subject or "Message")}</h2>'
            '  </div>'
            '  <div style="padding:20px 24px;">'
            + ''.join(content_parts) +
            '  </div>'
            '  <div style="padding:14px 24px;border-top:1px solid #eef1f4;background:#fafbfc;color:#6b7280;font-size:13px;">'
            '    <div>ACM SFSU</div>'
            '  </div>'
            '</div>'
            '</body></html>'
        )

        return html_body

    html_body = _convert_text_to_html(body)

    return client.inboxes.messages.send(
        inbox_id=inbox_id,
        to=recipient,
        subject=subject,
        text=body,
        html=html_body
    )

def list_messages(inbox_id):
    """List all messages in an inbox."""
    return client.inboxes.messages.list(inbox_id=inbox_id)

def get_message(inbox_id, message_id):
    """Retrieve a specific message."""
    return client.inboxes.messages.get(inbox_id=inbox_id, message_id=message_id)
