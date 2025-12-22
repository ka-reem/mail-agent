"""
Reusable UI components for Mail Agent
"""
import streamlit as st
from typing import List, Dict, Optional, Tuple
from utils.validators import extract_emails_from_text, create_inbox_mapping
from components.agentmail_utils import list_inboxes
from config import DISABLE_CREATE_NEW_INBOX

def display_fixed_recipients(contacts: List[Dict], complaint_type: str = "PG&E") -> List[str]:
    """Display recipients with checkboxes and return selected emails"""
    st.subheader("📧 Select Recipients")

    # Filter contacts by complaint type
    if complaint_type == "PG&E":
        filtered_contacts = [c for c in contacts if c.get('org') == 'PG&E']
    else:
        filtered_contacts = contacts

    # Initialize selected recipients in session state if not present
    if 'selected_recipients' not in st.session_state:
        # For City Ordinance, only pre-select PG&E contacts
        # For PG&E, select all filtered contacts (which is all PG&E)
        selected = []
        if complaint_type == "City Ordinance":
            pge_contacts = [c for c in filtered_contacts if c.get('org') == 'PG&E']
            for contact in pge_contacts:
                selected.append(contact.get('email', ''))
        else:
            for contact in filtered_contacts:
                selected.append(contact.get('email', ''))
        st.session_state.selected_recipients = selected

    # If complaint type changed, update selections
    if 'last_complaint_type' not in st.session_state or st.session_state.last_complaint_type != complaint_type:
        selected = []
        if complaint_type == "City Ordinance":
            pge_contacts = [c for c in filtered_contacts if c.get('org') == 'PG&E']
            for contact in pge_contacts:
                selected.append(contact.get('email', ''))
        else:
            for contact in filtered_contacts:
                selected.append(contact.get('email', ''))
        st.session_state.selected_recipients = selected
        st.session_state.last_complaint_type = complaint_type

    with st.expander(f"Choose Recipients ({len(filtered_contacts)} available)", expanded=False):
        # Group by organization
        orgs = {}
        for contact in filtered_contacts:
            org = contact.get('org', 'Other')
            if org not in orgs:
                orgs[org] = []
            orgs[org].append(contact)

        # Sort organizations: PG&E first, then alphabetically
        org_names = sorted(orgs.keys())
        if 'PG&E' in org_names:
            org_names.remove('PG&E')
            org_names = ['PG&E'] + org_names

        # Display each organization's contacts in collapsible sections
        for org_name in org_names:
            org_contacts = orgs[org_name]
            with st.expander(f"{org_name} ({len(org_contacts)} contacts)", expanded=False):
                # Subtle "all" button on the right to select/deselect all contacts
                col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
                org_emails = [c.get('email', '') for c in org_contacts]
                org_all_selected = all(email in st.session_state.selected_recipients for email in org_emails)

                with col3:
                    if st.button(
                        "all" if not org_all_selected else "none",
                        key=f"org_toggle_{org_name}",
                        use_container_width=True
                    ):
                        if org_all_selected:
                            for email in org_emails:
                                if email in st.session_state.selected_recipients:
                                    st.session_state.selected_recipients.remove(email)
                        else:
                            for email in org_emails:
                                if email not in st.session_state.selected_recipients:
                                    st.session_state.selected_recipients.append(email)
                        st.rerun()

                for contact in org_contacts:
                    email = contact.get('email', '')
                    contact_type = contact.get('type', '')

                    is_checked = email in st.session_state.selected_recipients
                    new_state = st.checkbox(
                        f"{contact_type or email}",
                        value=is_checked,
                        key=f"recipient_{email}"
                    )

                    # Update selected recipients based on checkbox state
                    if new_state and email not in st.session_state.selected_recipients:
                        st.session_state.selected_recipients.append(email)
                    elif not new_state and email in st.session_state.selected_recipients:
                        st.session_state.selected_recipients.remove(email)

    selected_count = len(st.session_state.selected_recipients)
    if selected_count > 0:
        st.success(f"📧 {selected_count} recipient(s) selected")
    else:
        st.warning("⚠️ Please select at least one recipient")

    return st.session_state.selected_recipients

def display_complaint_type_selector() -> str:
    """Display complaint type selector"""
    complaint_type = st.radio(
        "Complaint Type:",
        options=["PG&E", "City Ordinance"],
        index=0,
        horizontal=True,
        key="complaint_type"
    )

    return complaint_type


def display_email_type_selector() -> None:
    """Ensure AI mode is always selected"""
    st.session_state.email_type = "ai"


def display_inbox_settings() -> Tuple[bool, Optional[str]]:
    """Display simplified inbox settings - always use existing inbox"""
    st.subheader("Sending From")

    # Always False - using existing inbox only
    create_inbox_toggle = False

    selected_inbox = None
    with st.spinner("Loading your inboxes..."):
        try:
            all_inboxes = list_inboxes()
            if all_inboxes.inboxes:
                inbox_options, inbox_mapping = create_inbox_mapping(all_inboxes.inboxes)

                selected_option = st.selectbox(
                    "Select inbox:",
                    options=inbox_options,
                    help="Choose which inbox to send complaints from"
                )

                if selected_option:
                    selected_inbox = inbox_mapping[selected_option]
            else:
                st.error("❌ No inboxes available. Please configure an inbox in AgentMail first.")
        except Exception as e:
            st.error(f"❌ Failed to load inboxes: {e}")

    return create_inbox_toggle, selected_inbox

def display_ai_email_settings(complaint_type: str = "PG&E") -> Tuple[Optional[str], Optional[str], Optional[str], bool, bool, bool]:
    st.subheader("Complaint Details")

    if complaint_type == "PG&E":
        placeholder = "Write a detailed complaint about [specific PG&E service issue]. Include what happened, when it occurred, how it affects you, and what resolution you're requesting."
        help_text = "Describe the PG&E service issue you want to complain about. Be specific about what's happening, when it occurs, and the impact. The AI will generate personalized complaint emails for each recipient."
    else:
        placeholder = "Write a formal complaint about [specific ordinance violation]. Include details about what, when, where, and how it violates the city ordinance. Request specific action or enforcement."
        help_text = "Describe the ordinance violation you want to complain about. Be specific about what's happening, when it occurs, and which ordinance is being violated. The AI will generate personalized complaint emails for each official."

    prompt = st.text_area(
        "Describe Your Complaint:",
        placeholder=placeholder,
        height=120,
        help=help_text
    )

    # Additional Settings Tab
    with st.expander("⚙️ Additional Settings", expanded=False):
        # Email Signature Section
        st.subheader("Email Signature")

        col1, col2 = st.columns([1, 3])
        with col1:
            include_signature = st.checkbox("Include signature", value=True, help="Add a signature to the end of your emails")

        signature = ""
        if include_signature:
            with col2:
                st.write("")  # Spacer for alignment

            # Only custom signature option
            signature = st.text_area(
                "Custom Signature:",
                placeholder="",
                height=100,
                help="Write your custom email signature. This will be automatically added to the end of each email."
            )

            st.info("**Tip:** Include your contact information in your signature so officials can reach you with responses.")

        # Store signature in session state for use in email generation
        if include_signature and signature:
            st.session_state.email_signature = signature
        else:
            st.session_state.email_signature = ""

        # Email Generation Settings
        st.subheader("Generation Settings")
        col1, col2 = st.columns(2)
        with col1:
            preview_emails = st.checkbox("Preview generated emails", value=True,
                                       help="Show all generated emails for review before sending")
        with col2:
            human_approval = st.checkbox("Require manual approval for each email", value=True,
                                       help="Review and approve each email individually before sending")

    # Initialize other variables as None since we're only using custom prompt
    template = None
    subject = None

    # Always use consistent messaging across all recipients
    customize_per_recipient = False

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
    return st.button("🔄 Generate New Emails", use_container_width=True)
