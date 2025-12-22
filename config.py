"""
Configuration settings for Mail Agent
"""

# App Configuration
APP_TITLE = "PG&E Complaint Tool"
APP_ICON = "⚡"
APP_DESCRIPTION = "Send personalized complaints to PG&E and regulatory bodies about service issues."

# Production Safety Settings
PRODUCTION_MODE = True  # Set to False for development
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
DEFAULT_EMAIL_TYPE = "ai"
DEFAULT_CREATE_INBOX = True
DEFAULT_PREVIEW_EMAILS = True
DEFAULT_HUMAN_APPROVAL = False
DEFAULT_CUSTOMIZE_PER_RECIPIENT = False

# Recipients Configuration
CITY_ORDINANCE_RECIPIENTS_FILE = "data/city_ordinance_recipients.json"

# Placeholders
RECIPIENTS_PLACEHOLDER = ""

EMAIL_TEMPLATE_PLACEHOLDER = ""

CUSTOM_PROMPT_PLACEHOLDER = ""

EMAIL_BODY_PLACEHOLDER = ""

# Messages
FOOTER_TEXT = "PG&E Complaint Tool"
