"""
Email validation and utility functions
"""
import re

def extract_emails_from_text(email_text):
    """Extract valid email addresses from text"""
    if not email_text:
        return []
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, email_text)

def validate_email(email):
    """Validate a single email address"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return bool(re.match(email_pattern, email))

def format_inbox_display(inbox):
    """Format inbox for display in dropdown"""
    return f"{inbox.display_name} ({inbox.inbox_id})"

def create_inbox_mapping(inboxes):
    """Create mapping between display text and inbox IDs"""
    inbox_options = []
    inbox_mapping = {}
    
    for inbox in inboxes:
        display_text = format_inbox_display(inbox)
        inbox_options.append(display_text)
        inbox_mapping[display_text] = inbox.inbox_id
    
    return inbox_options, inbox_mapping
