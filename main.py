"""
Mail Agent - Main Application
A Streamlit app for sending personalized emails with AI assistance
"""
import streamlit as st
from config import *
from utils.session_manager import init_session_state, reset_email_data, is_email_data_generated, set_email_data, get_email_data
from components.ui_components import (
    display_complaint_type_selector,
    display_email_type_selector,
    display_inbox_settings,
    display_ai_email_settings, display_send_button, display_reset_button,
    display_fixed_recipients
)
from components.email_manager import EmailManager, create_email_config
from components.email_approval import EmailApprovalManager, display_auto_send_workflow
from utils.recipient_loader import load_city_ordinance_recipients, get_recipient_emails

# Page configuration
st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide", initial_sidebar_state="collapsed")

# Initialize session state
init_session_state()

# Main header
col1, col2 = st.columns([1, 0.15])
with col1:
    st.title(APP_TITLE)
    st.write(APP_DESCRIPTION)
with col2:
    st.write("")  # Spacer
    if st.button("📧 Inbox", help="View emails sent using this tool", use_container_width=True):
        st.switch_page("pages/inbox.py")

# Complaint type selector
complaint_type = display_complaint_type_selector()

# Ensure AI mode is always selected
display_email_type_selector()

# Load Fixed Recipients
try:
    json_contacts = load_city_ordinance_recipients()

    # Display recipients with checkboxes and get selected ones (filtered by complaint type)
    recipients = display_fixed_recipients(json_contacts, complaint_type)

except FileNotFoundError:
    st.error("❌ Recipient list not found. Please ensure 'data/city_ordinance_recipients.json' exists.")
    st.info("Create the file with city official contacts to continue.")
    st.stop()
except Exception as e:
    st.error(f"❌ Error loading recipients: {e}")
    st.stop()

# Inbox Settings Section
create_inbox_toggle, selected_inbox = display_inbox_settings()

if not selected_inbox:
    st.error("❌ No inbox available. Please configure an inbox in AgentMail first.")
    st.stop()

# Email Content Section - AI Mode Only
template, prompt, subject, preview_emails, human_approval, customize_per_recipient = display_ai_email_settings(complaint_type)
body = ""  # AI will generate the body

# Send Button and Email Processing
if display_send_button(st.session_state.email_type, recipients, subject, body, human_approval, preview_emails):

    if not recipients:
        st.error("Please add at least one recipient")
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

    # Handle email preview/approval (AI mode only)
    if preview_emails or human_approval:
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
st.write(FOOTER_TEXT)