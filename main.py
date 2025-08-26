import streamlit as st
from components.agentmail_utils import create_inbox, send_email, list_inboxes
from components.ai_utils import generate_personalized_email
import time
import re

st.set_page_config(page_title="Mail Agent", page_icon="📬", layout="wide")


# Default bulk email sender
st.title("📬 Mail Agent")
st.write("Welcome to the Mail Agent app! Manage your emails easily.")

# Send Email
st.header("Send Email")

# Simple Settings
st.subheader("Simple Settings")
use_ai_customization = st.checkbox("Enable AI Customization", value=False, help="Uses Gemini AI to generate personalized emails based on recipient's email address")
require_approval = st.checkbox("Require Approval for Each Email", value=True, help="Review and approve each email before sending")

# Advanced Settings
st.subheader("Advanced Settings")
email_template = st.text_area(
    "Email Template (optional)", 
    placeholder="Hi {name},\n\nI noticed your work at {company} and wanted to reach out regarding {topic}.",
    help="AI will enhance this template with personalized content"
)
prompt = st.text_area(
    "Custom Prompt (optional)", 
    placeholder="Write a professional email inviting {name} from {company} to collaborate on a new project.",
    help="AI will generate emails based on this prompt"
)
bulk_approval = st.checkbox("Enable Bulk Approval", value=False, help="Review all generated emails at once instead of one by one")

# Checkbox for creating a new inbox
create_new_inbox = st.checkbox("Create a new inbox for each email", value=True)

# If not creating new inbox, show existing inboxes
inbox_id = None
if not create_new_inbox:
    st.subheader("Select from existing inboxes:")
    try:
        inboxes = list_inboxes()
        if inboxes:
            inbox_options = [f"{inbox.inbox_id} ({inbox.display_name})" for inbox in inboxes]
            selected_inbox = st.selectbox("Choose an inbox:", inbox_options)
            if selected_inbox:
                inbox_id = selected_inbox.split(" ")[0]  # Extract inbox_id
        else:
            st.info("No existing inboxes found. Please create a new inbox.")
            create_new_inbox = True
    except Exception as e:
        st.error(f"Error loading inboxes: {e}")
        create_new_inbox = True

# Email Recipients Input
st.write("**Recipient Emails** (paste multiple emails - any format works):")
email_text = st.text_area(
    "Recipients", 
    placeholder="john@example.com\nmary@example.com\nbob@example.com\n\nOR paste: john@example.com, mary@example.com, bob@example.com",
    height=100
)

recipients = []
if email_text:
    # Extract emails using regex pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    recipients = re.findall(email_pattern, email_text)
    
    if recipients:
        st.success(f"Found {len(recipients)} email(s):")
        for i, email in enumerate(recipients, 1):
            st.write(f"{i}. {email}")
    else:
        st.warning("No valid email addresses found. Please check your input.")

subject = st.text_input("Subject")
body = st.text_area("Message Body")

if st.button("Send Email(s)"):
    if not recipients:
        st.error("Please add at least one recipient email.")
    elif not subject or not body:
        st.error("Please fill in subject and message body.")
    else:
        success_count = 0
        failed_count = 0
        
        # Progress bar for multiple emails
        if len(recipients) > 1:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        for i, recipient in enumerate(recipients):
            try:
                # Create new inbox for each email
                with st.spinner(f"Creating new inbox for {recipient}..."):
                    inbox = create_inbox()
                    current_inbox_id = inbox.inbox_id
                    st.info(f"Created inbox {current_inbox_id} for {recipient}")
                    time.sleep(1)  # Small delay to ensure inbox is ready
                
                # Generate personalized email using Gemini AI
                current_subject = subject
                current_body = body
                
                if use_ai_customization or email_template or prompt:
                    with st.spinner(f"Generating personalized email for {recipient}..."):
                        ai_result = generate_personalized_email(
                            recipient_email=recipient,
                            template=email_template if email_template else None,
                            prompt=prompt if prompt else None,
                            subject=subject if subject else None
                        )
                        current_subject = ai_result['subject']
                        current_body = ai_result['body']
                
                # Send email
                with st.spinner(f"Sending email to {recipient}..."):
                    response = send_email(current_inbox_id, recipient, current_subject, current_body)
                    success_count += 1
                    
                    if require_approval:
                        st.write(f"**Generated email for {recipient}:**")
                        st.write(f"**Subject:** {current_subject}")
                        st.write(f"**Body:**\n{current_body}")
                        if not st.button(f"✅ Approve & Send to {recipient}", key=f"approve_{i}"):
                            st.warning(f"Email to {recipient} not approved.")
                            continue
                    
                    if len(recipients) == 1:
                        st.success(f"✅ Email sent to {recipient}! Inbox: {current_inbox_id}, Message: {response.message_id}")
                
            except Exception as e:
                failed_count += 1
                st.error(f"❌ Failed to send email to {recipient}: {e}")
            
            # Update progress for multiple emails
            if len(recipients) > 1:
                progress = (i + 1) / len(recipients)
                progress_bar.progress(progress)
                status_text.text(f"Processing {i + 1}/{len(recipients)} emails...")
        
        # Final summary for multiple emails
        if len(recipients) > 1:
            st.success(f"🎉 Email sending complete! ✅ {success_count} successful, ❌ {failed_count} failed out of {len(recipients)} total emails.")