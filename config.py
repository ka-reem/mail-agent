"""
Configuration settings for Mail Agent
"""

# App Configuration
APP_TITLE = "📬📬📬📬📬📬📬📬📬📬📬📬📬📬📬📬📬📬📬📬📬📬"
APP_ICON = "📬"
APP_DESCRIPTION = "Send mass personalized email with ease, no account needed."

# Production Safety Settings
PRODUCTION_MODE = True  # Set to False for full access
DISABLE_SPAM_FEATURES = PRODUCTION_MODE
DISABLE_CREATE_NEW_INBOX = PRODUCTION_MODE

# UI Configuration
EMAIL_TEXT_AREA_HEIGHT = 120
EMAIL_BODY_HEIGHT = 200
EMAIL_TEMPLATE_HEIGHT = 150
EMAIL_PROMPT_HEIGHT = 100

# Email Validation
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Default Values
DEFAULT_EMAIL_TYPE = "regular"
DEFAULT_CREATE_INBOX = True
DEFAULT_PREVIEW_EMAILS = True
DEFAULT_HUMAN_APPROVAL = False
DEFAULT_CUSTOMIZE_PER_RECIPIENT = False

# Placeholders
RECIPIENTS_PLACEHOLDER = """john@company1.com
mary@company2.com
bob@startup.io

Or: john@company1.com, mary@company2.com"""

EMAIL_TEMPLATE_PLACEHOLDER = """Hi {name},

I noticed your work at {company} and wanted to reach out about...

Best regards,
Your Name"""

CUSTOM_PROMPT_PLACEHOLDER = "Write a professional email inviting them to a networking event in San Francisco next month"

EMAIL_BODY_PLACEHOLDER = "Write your email message here..."

# Message
FOOTER_TEXT = "Created by "" [Kareem](https://github.com/ka-reem)"
