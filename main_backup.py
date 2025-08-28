import streamlit as st
from components.agentmail_utils import create_inbox, send_email, list_inboxes
from components.ai_utils import generate_personalized_email
import time
import re

st.set_page_config(page_title="Mail Agent", page_icon="📬", layout="wide")

# Main header
st.title("Mail Agent")
st.write("Send personalized emails with ease - choose between manual or AI-powered emails")

# Email Type Selection
st.subheader("Choose Your Email Type")

col1, col2 = st.columns(2)

with col1:
    regular_selected = st.button("Regular Email", key="regular_btn", use_container_width=True)
    if regular_selected:
        st.session_state.email_type = "regular"

with col2:
    ai_selected = st.button("AI-Generated Email", key="ai_btn", use_container_width=True)
    if ai_selected:
        st.session_state.email_type = "ai"

# Initialize email type if not set
if 'email_type' not in st.session_state:
    st.session_state.email_type = "regular"

# Show current selection
if st.session_state.email_type == "regular":
    st.info("Regular Email Selected - Manually write your email subject and body")
else:
    st.info("AI-Generated Email Selected - Let AI create personalized emails for each recipient")

st.markdown("---")

# Recipients Section
st.subheader("Recipients")
email_text = st.text_area(
    "Enter recipient emails (one per line or comma-separated):",
    placeholder="john@company1.com\nmary@company2.com\nbob@startup.io\n\nOr: john@company1.com, mary@company2.com",
    height=120
)

recipients = []
if email_text:
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    recipients = re.findall(email_pattern, email_text)
    
    if recipients:
        st.success(f"Found {len(recipients)} recipients: " + ", ".join(recipients))
    else:
        st.warning("No valid email addresses found")

st.markdown("---")

# Inbox Settings Section
st.subheader("Inbox Settings")
create_inbox_toggle = st.checkbox("Create new inbox per email", value=True, help="If disabled, you'll use one existing inbox for all emails")

# Inbox selection when not creating new ones
selected_inbox = None
if not create_inbox_toggle:
    with st.spinner("Loading existing inboxes..."):
        try:
            all_inboxes = list_inboxes()
            if all_inboxes.inboxes:
                # Create options for dropdown (display name - inbox_id)
                inbox_options = []
                inbox_mapping = {}
                
                for inbox in all_inboxes.inboxes:
                    display_text = f"{inbox.display_name} ({inbox.inbox_id})"
                    inbox_options.append(display_text)
                    inbox_mapping[display_text] = inbox.inbox_id
                
                selected_option = st.selectbox(
                    "Select an existing inbox:",
                    options=inbox_options,
                    help="Choose from your existing inboxes"
                )
                
                if selected_option:
                    selected_inbox = inbox_mapping[selected_option]
                    st.success(f"Selected inbox: {selected_inbox}")
            else:
                st.warning("No existing inboxes found. Please create a new inbox.")
                create_inbox_toggle = True
        except Exception as e:
            st.error(f"Failed to load inboxes: {e}")
            create_inbox_toggle = True

st.markdown("---")

# Email Content Section
if st.session_state.email_type == "regular":
    # Regular Email UI
    st.subheader("Email Content")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        subject = st.text_input("Subject Line", placeholder="Enter your email subject")
    with col2:
        st.write("")  # Spacer for alignment
    
    body = st.text_area(
        "Email Body",
        placeholder="Write your email message here...",
        height=200
    )
    
    # Preview section
    if subject and body and recipients:
        with st.expander("Email Preview", expanded=False):
            st.write(f"**Subject:** {subject}")
            st.write(f"**Body:**")
            st.write(body)
            st.write(f"**Will be sent to:** {len(recipients)} recipients")

else:
    # AI Email UI
    st.subheader("AI Email Settings")
    
    # AI Options in tabs
    tab1, tab2, tab3 = st.tabs(["Template Mode", "Custom Prompt", "Auto Generate"])
    
    template = None
    prompt = None
    subject = None
    
    with tab1:
        st.write("Provide a template and AI will enhance it with personalized content")
        template = st.text_area(
            "Email Template:",
            placeholder="Hi {name},\n\nI noticed your work at {company} and wanted to reach out about...\n\nBest regards,\nYour Name",
            height=150
        )
        if template:
            st.info("AI will replace {name} and {company} with personalized information")
    
    with tab2:
        st.write("Tell AI what kind of email you want to send")
        prompt = st.text_area(
            "Custom Prompt:",
            placeholder="Write a professional email inviting them to a networking event in San Francisco next month",
            height=100
        )
    
    with tab3:
        st.write("Let AI generate a completely personalized email")
        subject = st.text_input("Optional Subject Hint:", placeholder="Partnership opportunity")
        st.info("AI will create unique emails for each recipient based on their email domain")
    
    # AI Settings
    col1, col2 = st.columns(2)
    with col1:
        preview_emails = st.checkbox("Preview generated emails", value=True)
    with col2:
        human_approval = st.checkbox("Require manual approval for each email", value=False, help="Review and approve each email individually before sending")
    
    # Advanced AI Settings
    with st.expander("Experimental AI Settings", expanded=False):
        customize_per_recipient = st.checkbox(
            "🔧 Customize message per recipient (Not Recommended)", 
            value=False,
            help="This will generate completely different messages for each recipient based on their email domain. May result in inconsistent messaging."
        )
        if customize_per_recipient:
            st.warning("⚠️ This option may create inconsistent messaging across recipients. Use with caution for professional communications.")
        else:
            st.info("💡 Recommended: Keep this disabled for consistent, professional messaging across all recipients.")

# Initialize variables for regular email mode
if st.session_state.email_type == "regular":
    preview_emails = False
    human_approval = False
    customize_per_recipient = False

st.markdown("---")

# Send Button
send_button_disabled = not recipients or (st.session_state.email_type == "regular" and (not subject or not body))

# Determine button text based on mode
if st.session_state.email_type == "ai":
    if human_approval:
        button_text = "🔍 Generate & Preview Emails for Approval"
    elif preview_emails:
        button_text = "📧 Generate & Send Emails (with Preview)"
    else:
        button_text = "📧 Generate & Send Emails"
else:
    button_text = "📧 Send Emails"

if st.button(button_text, disabled=send_button_disabled, use_container_width=True):
    if not recipients:
        st.error("Please add at least one recipient")
    elif st.session_state.email_type == "regular" and (not subject or not body):
        st.error("Please fill in subject and body for regular emails")
    else:
        # Initialize session state for email data if not exists
        if 'email_data_generated' not in st.session_state:
            st.session_state.email_data_generated = False
        
        # Only generate email data if not already generated
        if not st.session_state.email_data_generated:
            # Email sending logic here
            success_count = 0
            failed_count = 0
            
            # Progress tracking
            if len(recipients) > 1:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            # Container for email previews (AI mode)
            if st.session_state.email_type == "ai" and (preview_emails or human_approval):
                st.subheader("AI Generated Email Previews")
            
            # Prepare all email content first
            email_data = []
            
            for i, recipient in enumerate(recipients):
                try:
                    # Prepare email content
                    if st.session_state.email_type == "regular":
                        current_subject = subject
                        current_body = body
                    else:
                        # AI Email generation
                        with st.spinner(f"Generating personalized email for {recipient}..."):
                            ai_result = generate_personalized_email(
                                recipient_email=recipient,
                                template=template if template else None,
                                prompt=prompt if prompt else None,
                                subject=subject if subject else None,
                                customize_per_recipient=customize_per_recipient
                            )
                            current_subject = ai_result['subject']
                            current_body = ai_result['body']
                    
                    email_data.append({
                        'recipient': recipient,
                        'subject': current_subject,
                        'body': current_body,
                        'approved': False,
                        'sent': False
                    })
                    
                except Exception as e:
                    st.error(f"Failed to generate email for {recipient}: {e}")
            
            # Store email data in session state for persistence
            st.session_state.email_data = email_data
            st.session_state.email_data_generated = True
            st.rerun()  # Rerun to show the approval interface

# Display email approval interface if data is generated
if st.session_state.get('email_data_generated', False) and 'email_data' in st.session_state:
    email_data = st.session_state.email_data
    
    # Show previews and handle approvals
    if st.session_state.email_type == "ai" and (preview_emails or human_approval):
        st.subheader("AI Generated Email Previews")
        
        for i, email_info in enumerate(email_data):
            with st.expander(f"Email for {email_info['recipient']}", expanded=human_approval):
                st.write(f"**Subject:** {email_info['subject']}")
                st.write(f"**Body:**")
                st.write(email_info['body'])
                
                if human_approval and not email_info.get('sent', False):
                    # Individual approval checkbox
                    approval_key = f"approve_{i}_{email_info['recipient']}"
                    approved = st.checkbox(
                        f"✅ Approve this email for {email_info['recipient']}", 
                        key=approval_key,
                        value=email_info.get('approved', False)
                    )
                    # Update the approval status in session state
                    st.session_state.email_data[i]['approved'] = approved
                    
                    # Individual send button
                    if approved and st.button(f"Send to {email_info['recipient']}", key=f"send_{i}"):
                        try:
                            # Create inbox
                            if create_inbox_toggle:
                                with st.spinner(f"Creating inbox for {email_info['recipient']}..."):
                                    inbox = create_inbox()
                                    current_inbox_id = inbox.inbox_id
                                    time.sleep(1)
                            else:
                                current_inbox_id = selected_inbox
                                if not current_inbox_id:
                                    st.error("No inbox selected.")
                                    st.stop()
                            
                            with st.spinner(f"Sending to {email_info['recipient']}..."):
                                response = send_email(current_inbox_id, email_info['recipient'], 
                                                    email_info['subject'], email_info['body'])
                                st.success(f"✅ Email sent successfully to {email_info['recipient']}!")
                                st.session_state.email_data[i]['sent'] = True
                                st.rerun()  # Refresh to update the UI
                                
                        except Exception as e:
                            st.error(f"Failed to send to {email_info['recipient']}: {e}")
                
                elif email_info.get('sent', False):
                    st.success(f"✅ Email already sent to {email_info['recipient']}")
        
        # Bulk send button for approved emails
        if human_approval:
            st.markdown("---")
            approved_emails = [email for email in email_data if email.get('approved', False) and not email.get('sent', False)]
            
            if approved_emails:
                if st.button(f"📧 Send All Approved Emails ({len(approved_emails)} emails)", use_container_width=True):
                    success_count = 0
                    failed_count = 0
                    
                    if len(approved_emails) > 1:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                    
                    for i, email_info in enumerate(approved_emails):
                        # Find the index in the original list
                        original_index = next(j for j, email in enumerate(email_data) if email['recipient'] == email_info['recipient'])
                        
                        try:
                            # Create inbox
                            if create_inbox_toggle:
                                with st.spinner(f"Creating inbox for {email_info['recipient']}..."):
                                    inbox = create_inbox()
                                    current_inbox_id = inbox.inbox_id
                                    time.sleep(1)
                            else:
                                current_inbox_id = selected_inbox
                                if not current_inbox_id:
                                    st.error("No inbox selected.")
                                    break
                            
                            with st.spinner(f"Sending to {email_info['recipient']}..."):
                                response = send_email(current_inbox_id, email_info['recipient'], 
                                                    email_info['subject'], email_info['body'])
                                success_count += 1
                                st.session_state.email_data[original_index]['sent'] = True
                                
                        except Exception as e:
                            failed_count += 1
                            st.error(f"Failed to send to {email_info['recipient']}: {e}")
                        
                        # Update progress
                        if len(approved_emails) > 1:
                            progress = (i + 1) / len(approved_emails)
                            progress_bar.progress(progress)
                            status_text.text(f"Processing {i + 1}/{len(approved_emails)} emails...")
                    
                    # Final results
                    if success_count > 0:
                        st.success(f"Successfully sent {success_count} emails!")
                    if failed_count > 0:
                        st.error(f"{failed_count} emails failed to send")
                    
                    st.rerun()  # Refresh to update the UI
            else:
                st.info("No emails approved for sending. Please approve emails above to enable bulk sending.")
    
    # Auto-send mode (no human approval required)
    if not human_approval:
        # For regular emails or AI emails without approval, send immediately
        success_count = 0
        failed_count = 0
        
        # Progress tracking
        if len(email_data) > 1:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        for i, email_info in enumerate(email_data):
            if not email_info.get('sent', False):
                try:
                    # Create inbox
                    if create_inbox_toggle:
                        with st.spinner(f"Creating inbox for {email_info['recipient']}..."):
                            inbox = create_inbox()
                            current_inbox_id = inbox.inbox_id
                            time.sleep(1)
                    else:
                        current_inbox_id = selected_inbox
                        if not current_inbox_id:
                            st.error("No inbox selected.")
                            break
                    
                    # Send email
                    with st.spinner(f"Sending to {email_info['recipient']}..."):
                        response = send_email(current_inbox_id, email_info['recipient'], 
                                            email_info['subject'], email_info['body'])
                        success_count += 1
                        st.session_state.email_data[i]['sent'] = True
                    
                except Exception as e:
                    failed_count += 1
                    st.error(f"Failed to send to {email_info['recipient']}: {e}")
                
                # Update progress
                if len(email_data) > 1:
                    progress = (i + 1) / len(email_data)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing {i + 1}/{len(email_data)} emails...")
        
        # Final results
        if success_count > 0:
            st.success(f"Successfully sent {success_count} emails!")
        if failed_count > 0:
            st.error(f"{failed_count} emails failed to send")
        
        # Clear the session state after sending
        st.session_state.email_data_generated = False
        if 'email_data' in st.session_state:
            del st.session_state.email_data
    
    # Reset button
    st.markdown("---")
    if st.button("🔄 Generate New Emails", use_container_width=True):
        st.session_state.email_data_generated = False
        if 'email_data' in st.session_state:
            del st.session_state.email_data
        st.rerun()

# Footer
st.markdown("---")
st.write("Mail Agent - Powered by AgentMail & Gemini AI")