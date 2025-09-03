import streamlit as st
from config import DISABLE_SPAM_FEATURES

# Production Safety Check
if DISABLE_SPAM_FEATURES:
    st.title("Email Spammer")
    st.error("**This feature has been disabled.**")
    st.warning("**Notice:** This functionality is not available in production.")
    # st.info("💡 **Alternative:** Please use the main AI Email Generator for legitimate email outreach.")
    
    # Display disabled interface (non-functional)
    st.markdown("---")
    st.subheader("📧 Feature Preview (Disabled)")
    
    # All inputs are disabled
    st.text_input("Target Email:", placeholder="Feature disabled", disabled=True)
    st.text_input("Subject:", placeholder="Feature disabled", disabled=True)
    st.text_area("Message Body:", placeholder="Feature disabled", height=100, disabled=True)
    st.number_input("Number of emails:", min_value=1, max_value=1, value=1, disabled=True)
    st.slider("Delay between emails:", min_value=0, max_value=1, value=0, disabled=True)
    st.checkbox("Use AI variation", value=False, disabled=True)
    
    if st.button("🚫 Start Campaign (DISABLED)", disabled=True):
        pass
    
    st.markdown("---")
    st.error("🔒 **Security Notice:** All spam-related features are temporarily disabled in production.")
    st.stop()

# Original code below (never reached in production)
from components.agentmail_utils import create_inbox, send_email
from components.ai_utils import generate_personalized_email
import time

st.title("Email Spammer")
st.write("Send an email multiple times to a single recipient without getting blocked.")

# Create or use existing inbox
st.subheader("Inbox Settings")
create_new_inbox_option = st.radio(
    "Inbox Option:",
    ["Create New Inbox", "Use Specific Inbox"]
)

inbox_id = None
if create_new_inbox_option == "Create New Inbox":
    if st.button("Create Inbox for Spamming"):
        with st.spinner("Creating inbox..."):
            inbox = create_inbox()
            inbox_id = inbox.inbox_id
            st.session_state['spam_inbox_id'] = inbox_id
            st.success(f"Inbox created: {inbox_id}")
    
    if 'spam_inbox_id' in st.session_state:
        inbox_id = st.session_state['spam_inbox_id']
        st.info(f"Using inbox: {inbox_id}")
else:
    inbox_id = st.text_input("Enter Inbox ID:", placeholder="example@agentmail.to")

# Email Settings
st.subheader("Email Content")
recipient_email = st.text_input("Target Email:", placeholder="victim@example.com")
subject = st.text_input("Subject:")
body = st.text_area("Message Body:", height=150)

# Spam Settings
st.subheader("Spam Settings")
num_emails = st.number_input("Number of emails to send:", min_value=1, max_value=100, value=5)
delay_between_emails = st.slider("Delay between emails (seconds):", min_value=0, max_value=60, value=1)

# AI Enhancement (optional)
use_ai_variation = st.checkbox("Use AI to vary each email slightly", value=False)
if use_ai_variation:
    ai_prompt = st.text_area("AI Variation Prompt (optional):", 
                            placeholder="Make each email slightly different while keeping the same message")

# Send Spam Emails
if st.button("Start Spam Campaign"):
    if not inbox_id:
        st.error("Please create or specify an inbox first.")
    elif not recipient_email or not subject or not body:
        st.error("Please fill in all email content fields.")
    else:
        st.warning(f"About to send {num_emails} emails to {recipient_email} using inbox {inbox_id}")
        st.session_state['ready_to_spam'] = True

# Confirmation and execution
if st.session_state.get('ready_to_spam', False):
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Confirm and Start Spamming"):
            success_count = 0
            failed_count = 0
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(num_emails):
                try:
                    current_subject = subject
                    current_body = body
                    
                    # AI variation if enabled
                    if use_ai_variation and ai_prompt:
                        with st.spinner(f"Generating variation for email {i+1}..."):
                            ai_result = generate_personalized_email(
                                recipient_email=recipient_email,
                                prompt=f"{ai_prompt}. Email #{i+1}: {body}",
                                subject=subject
                            )
                            current_subject = ai_result['subject']
                            current_body = ai_result['body']
                    
                    # Send email
                    status_text.text(f"Sending email {i+1}/{num_emails} to {recipient_email}...")
                    response = send_email(inbox_id, recipient_email, current_subject, current_body)
                    success_count += 1
                    
                    # Update progress
                    progress = (i + 1) / num_emails
                    progress_bar.progress(progress)
                    
                    # Show individual success (for first few emails)
                    if i < 5:
                        st.success(f"Email {i+1} sent! Message ID: {response.message_id}")
                    
                    # Delay between emails
                    if delay_between_emails > 0 and i < num_emails - 1:
                        time.sleep(delay_between_emails)
                        
                except Exception as e:
                    failed_count += 1
                    if i < 5:  # Only show first few errors
                        st.error(f"❌ Failed to send email {i+1}: {e}")
            
            # Final summary
            st.success(f"🎉 Spam campaign complete! {success_count} successful, ❌ {failed_count} failed out of {num_emails} total emails.")
            
            if failed_count > 0:
                st.warning(f"{failed_count} emails failed. This might be due to rate limiting or other API issues.")
            
            # Reset the state
            st.session_state['ready_to_spam'] = False
    
    with col2:
        if st.button("❌ Cancel"):
            st.session_state['ready_to_spam'] = False
            st.success("Spam campaign cancelled.")

# Warning message
st.markdown("---")
st.markdown("**Disclaimer:** Use this feature responsibly. Spamming emails may violate terms of service and anti-spam laws.")
