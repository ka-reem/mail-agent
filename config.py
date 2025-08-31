"""
Configuration settings for Mail Agent
"""

# App Configuration
APP_TITLE = "Mail Agent"
APP_ICON = "📬"
APP_DESCRIPTION = "Send personalized emails with ease - choose between manual or AI-powered emails"

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

# Messages
FOOTER_TEXT = "Mail Agent - Powered by AgentMail & Gemini AI"
