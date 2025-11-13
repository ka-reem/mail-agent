"""
Reusable UI components for Mail Agent
"""
import streamlit as st
from typing import List, Dict, Optional, Tuple
from utils.validators import extract_emails_from_text, create_inbox_mapping
from components.agentmail_utils import list_inboxes
from config import DISABLE_CREATE_NEW_INBOX

def display_email_type_selector() -> None:
    """Display email type selection buttons"""
    st.subheader("Choose Your Email Type")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ai_selected = st.button("AI-Generated Email", key="ai_btn", use_container_width=True)
        if ai_selected:
            st.session_state.email_type = "ai"
    
    with col2:
        regular_selected = st.button("Regular Email", key="regular_btn", use_container_width=True)
        if regular_selected:
            st.session_state.email_type = "regular"

def display_email_type_info(email_type: str) -> None:
    """Display information about current email type"""
    if email_type == "regular":
        st.info("Regular Email Selected - Manually write your email subject and body")
    else:
        st.info("AI-Generated Email Selected - Let AI create personalized emails for each recipient")

def display_recipients_input() -> List[str]:
    """Display recipients input and return list of valid emails"""
    st.subheader("Recipients")
    email_text = st.text_area(
        "Enter recipient emails (one per line or comma-separated):",
        placeholder="john@company1.com\nmary@company2.com\nbob@startup.io\n\nOr: john@company1.com, mary@company2.com",
        height=120,
        key="manual_recipients_input"
    )
    
    recipients = extract_emails_from_text(email_text)
    
    if email_text:
        if recipients:
            st.success(f"Found {len(recipients)} recipients: " + ", ".join(recipients))
        else:
            st.warning("No valid email addresses found")
    
    return recipients

def display_inbox_settings() -> Tuple[bool, Optional[str]]:
    """Display inbox settings and return configuration"""
    st.subheader("Inbox Settings")
    
    # Production safety check
    if DISABLE_CREATE_NEW_INBOX:
        st.warning("🔒 **Security Notice:** Creating new inboxes per email has been disabled for production safety.")
        create_inbox_toggle = st.checkbox(
            "Create new inbox per email (DISABLED)", 
            value=False, 
            disabled=True,
            help="This feature is disabled in production to prevent abuse and ensure responsible email usage."
        )
        # Force to False regardless of checkbox state
        create_inbox_toggle = False
    else:
        create_inbox_toggle = st.checkbox(
            "Create new inbox per email", 
            value=False, 
            help="Creates a new unique separate inbox for each outgoing email, ensuring messages are always delivered without bounces."
        )
    
    selected_inbox = None
    if not create_inbox_toggle:
        with st.spinner("Loading existing inboxes..."):
            try:
                all_inboxes = list_inboxes()
                if all_inboxes.inboxes:
                    inbox_options, inbox_mapping = create_inbox_mapping(all_inboxes.inboxes)
                    
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
    
    return create_inbox_toggle, selected_inbox

def display_regular_email_form() -> Tuple[str, str]:
    """Display regular email form and return subject and body"""
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
    
    # Email Signature Section for Regular Emails
    st.markdown("---")
    st.subheader("Email Signature")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        include_signature = st.checkbox("Include signature", value=True, help="Add a signature to the end of your emails")
    
    if include_signature:
        with col2:
            st.write("")  # Spacer for alignment
        
        # Only custom signature option
        signature = st.text_area(
            "Custom Signature:",
            placeholder="Best regards,\nJohn Smith\nSenior Developer\nTechCorp Inc.\njohn@techcorp.com\n(555) 123-4567",
            height=100,
            help="Write your custom email signature. This will be automatically added to the end of each email."
        )
        
        st.info("**Tip:** If you're looking for responses, include your contact information in your signature and consider adding a note like 'This email is not actively monitored. Please reach out to yourname@email.com for inquiries.'")
        
        if signature:
            # Append signature to body if it exists
            if body and signature:
                body_with_signature = f"{body}\n\n{signature}"
            elif signature:
                body_with_signature = signature
            else:
                body_with_signature = body
        else:
            body_with_signature = body
        
        # Store signature in session state
        st.session_state.email_signature = signature if signature else ""
    else:
        body_with_signature = body
        st.session_state.email_signature = ""
    
    return subject, body_with_signature

def display_regular_email_preview(subject: str, body: str, recipients: List[str]) -> None:
    """Display email preview for regular emails"""
    if subject and body and recipients:
        with st.expander("Email Preview", expanded=False):
            st.write(f"**Subject:** {subject}")
            st.write(f"**Body:**")
            st.write(body)
            st.write(f"**Will be sent to:** {len(recipients)} recipients")

def display_ai_email_settings() -> Tuple[Optional[str], Optional[str], Optional[str], bool, bool, bool]:
    # """Display AI email settings and return configuration"""
    # st.subheader("AI Email Settings")
    
    # Sender Information Section
    # st.markdown("---")
    st.subheader("About You (Sender Information)")
    sender_info = st.text_area(
        "Add information about yourself here:",
        placeholder="I'm a Computer Science student at SFSU graduating in May 2030. I have internship experience at tech companies including Google and Microsoft, where I worked on backend systems and machine learning projects.",
        height=100,
        key="sender_info_input",
        help="This information will be used by AI to personalize emails from your perspective. Include your background, experience, education, and any relevant details."
    )
    
    # Store sender info in session state
    st.session_state.sender_info = sender_info if sender_info else ""
    
    st.markdown("---")
    
    # Custom Prompt Section (no tabs, direct input)
    st.write("Tell AI what kind of email you want to send")
    prompt = st.text_area(
        "Custom Prompt:",
        placeholder="Write a professional email inviting them to a networking event in San Francisco next month. Include specific details about the event date, location, and what attendees will gain from participating.",
        height=120,
        help="Describe the type of email you want AI to generate. Be specific about the tone, purpose, and any key information to include. The AI will generate complete emails without any placeholder text."
    )
    
    # Email Signature Section
    st.markdown("---")
    st.subheader("Email Signature")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        include_signature = st.checkbox("Include signature", value=True, help="Add a signature to the end of your emails—one will not be added by default.")
    
    signature = ""
    if include_signature:
        with col2:
            st.write("")  # Spacer for alignment
        
        # Only custom signature option
        signature = st.text_area(
            "Custom Signature:",
            placeholder="Best regards,\nJohn Smith\nSenior Developer\nTechCorp Inc.\njohn@techcorp.com\n(555) 123-4567",
            height=120,
            help="Write your custom email signature. This will be automatically added to the end of each email."
        )
        
        st.info("**Tip:** If you're looking for responses, include your contact information in your signature and consider adding a note like 'This email is not actively monitored. Please reach out to yourname@email.com for inquiries.'")
    
    # Store signature in session state for use in email generation
    if include_signature and signature:
        st.session_state.email_signature = signature
    else:
        st.session_state.email_signature = ""
    
    # Initialize other variables as None since we're only using custom prompt
    template = None
    subject = None
    
    st.markdown("---")
    
    # AI Settings
    col1, col2 = st.columns(2)
    with col1:
        preview_emails = st.checkbox("Preview generated emails", value=True, 
                                   help="Show all generated emails and lets you customize their content (should not be unchecked)")
    with col2:
        human_approval = st.checkbox("Require manual approval for each email", value=True, 
                                   help="Review and approve each email individually before sending")
    
    # Advanced AI Settings
    with st.expander("⚙️ Advanced AI Settings", expanded=False):
        customize_per_recipient = st.checkbox(
            "🔧 Customize message per recipient (Not Recommended)", 
            value=False,
            help="This will generate completely different messages for each recipient based on their email domain. May result in inconsistent messaging and longer generation time."
        )
        if customize_per_recipient:
            st.warning("This option may create inconsistent messaging across recipients and take longer to generate. Use with caution for professional communications.")
        else:
            st.info("💡 Recommended: Keep this disabled for consistent, professional messaging across all recipients.")
    
    return template, prompt, subject, preview_emails, human_approval, customize_per_recipient

def display_send_button(email_type: str, recipients: List[str], subject: str = "", body: str = "", 
                       human_approval: bool = False, preview_emails: bool = False) -> bool:
    """Display send button with appropriate text and return if clicked"""
    send_button_disabled = not recipients or (email_type == "regular" and (not subject or not body))
    
    # Determine button text based on mode
    if email_type == "ai":
        if human_approval:
            button_text = "🔍 Generate & Preview Emails for Approval"
        elif preview_emails:
            button_text = "📧 Generate & Send Emails (with Preview)"
        else:
            button_text = "📧 Generate & Send Emails"
    else:
        button_text = "📧 Send Emails"
    
    return st.button(button_text, disabled=send_button_disabled, use_container_width=True)

def display_reset_button() -> bool:
    """Display reset button and return if clicked"""
    st.markdown("---")
    return st.button("🔄 Generate New Emails", use_container_width=True)
