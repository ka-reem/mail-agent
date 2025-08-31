"""
Mail Agent - Main Application
A Streamlit app for sending personalized emails with AI assistance
"""
import streamlit as st
from config import *
from utils.session_manager import init_session_state, reset_email_data, is_email_data_generated, set_email_data, get_email_data
from components.ui_components import (
    display_email_type_selector, display_email_type_info, display_recipients_input,
    display_inbox_settings, display_regular_email_form, display_regular_email_preview,
    display_ai_email_settings, display_send_button, display_reset_button
)
from components.email_manager import EmailManager, create_email_config
from components.email_approval import EmailApprovalManager, display_auto_send_workflow
from components.json_email_processor import display_json_email_input, create_recipients_from_json

# Page configuration
st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

# Initialize session state
init_session_state()

# Main header
st.title(APP_TITLE)
st.write(APP_DESCRIPTION)

# Email Type Selection
display_email_type_selector()

# Show current selection
display_email_type_info(st.session_state.email_type)

st.markdown("---")

# Recipients Section
recipients = display_recipients_input()

# JSON Recipients Section
json_contacts = display_json_email_input()
if json_contacts:
    json_recipients = create_recipients_from_json(json_contacts)
    if json_recipients:
        # Merge or replace recipients based on user choice
        if recipients:
            merge_option = st.radio(
                "Recipients detected from both sources:",
                ["Use JSON recipients only", "Combine JSON + manual recipients"],
                key="recipient_merge_option"
            )
            if merge_option == "Use JSON recipients only":
                recipients = json_recipients
            else:
                recipients = list(set(recipients + json_recipients))  # Remove duplicates
        else:
            recipients = json_recipients
        
        st.success(f"Using {len(recipients)} recipients total")
else:
    json_contacts = None

st.markdown("---")

# Inbox Settings Section
create_inbox_toggle, selected_inbox = display_inbox_settings()

st.markdown("---")

# Email Content Section
if st.session_state.email_type == "regular":
    # Regular Email UI
    subject, body = display_regular_email_form()
    display_regular_email_preview(subject, body, recipients)
    
    # Initialize AI settings for regular emails
    preview_emails = False
    human_approval = False
    customize_per_recipient = False
    template, prompt = None, None
else:
    # AI Email UI
    template, prompt, subject, preview_emails, human_approval, customize_per_recipient = display_ai_email_settings()
    body = ""  # AI will generate the body

st.markdown("---")

# Send Button and Email Processing
if display_send_button(st.session_state.email_type, recipients, subject, body, human_approval, preview_emails):
    if not recipients:
        st.error("Please add at least one recipient")
    elif st.session_state.email_type == "regular" and (not subject or not body):
        st.error("Please fill in subject and body for regular emails")
    else:
        # Generate emails if not already generated
        if not is_email_data_generated():
            # Create email manager
            email_manager = EmailManager(create_inbox_toggle, selected_inbox)
            
            # Create email configuration
            email_config = create_email_config(
                email_type=st.session_state.email_type,
                subject=subject,
                body=body,
                template=template,
                prompt=prompt,
                customize_per_recipient=customize_per_recipient
            )
            
            # Generate email data
            email_data = email_manager.generate_email_data(recipients, email_config, json_contacts)
            set_email_data(email_data)
            st.rerun()

# Display Email Approval Interface
if is_email_data_generated():
    email_data = get_email_data()
    email_manager = EmailManager(create_inbox_toggle, selected_inbox)
    
    # Handle AI emails with preview/approval
    if st.session_state.email_type == "ai" and (preview_emails or human_approval):
        approval_manager = EmailApprovalManager(email_manager)
        approval_manager.display_email_previews(email_data, preview_emails, human_approval)
        
        if human_approval:
            approval_manager.display_bulk_send_controls(email_data)
    
    # Handle auto-send mode (no approval required)
    if not human_approval:
        display_auto_send_workflow(email_manager, email_data)
        # Clear session state after sending
        reset_email_data()
    
    # Reset button
    if display_reset_button():
        reset_email_data()
        st.rerun()

# Footer
st.markdown("---")
st.write(FOOTER_TEXT)
