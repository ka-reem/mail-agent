"""
Email Inbox Viewer
View all sent and received emails from all AgentMail inboxes unified with pagination
"""
import streamlit as st
from components.agentmail_utils import list_inboxes, list_messages, get_message

st.set_page_config(page_title="Email Inbox", page_icon="📧", layout="wide", initial_sidebar_state="collapsed")

st.title("📧 Email Inbox")
st.write("View all your sent and received emails")

# Batch size for pagination
BATCH_SIZE = 15

# Initialize session state
if 'all_emails_loaded' not in st.session_state:
    st.session_state.all_emails_loaded = False
    st.session_state.all_messages = []
    st.session_state.sent_emails = []
    st.session_state.received_emails = []
    st.session_state.current_batch = 1

try:
    # Load all inboxes
    all_inboxes = list_inboxes()

    # Handle both dict and object responses
    if hasattr(all_inboxes, 'inboxes'):
        inboxes_list = all_inboxes.inboxes
    elif isinstance(all_inboxes, dict) and 'inboxes' in all_inboxes:
        inboxes_list = all_inboxes['inboxes']
    else:
        inboxes_list = []

    if not inboxes_list:
        st.error("❌ No inboxes available. Please create an inbox first.")
        st.stop()

    # Load emails only once
    if not st.session_state.all_emails_loaded:
        st.info(f"📬 Loading emails from {len(inboxes_list)} inbox(es)...")

        # Collect all messages from all inboxes
        all_messages = []

        with st.spinner("Loading email list..."):
            for inbox in inboxes_list:
                # Handle both object and dict inbox formats
                inbox_id = inbox.inbox_id if hasattr(inbox, 'inbox_id') else inbox.get('inbox_id')

                try:
                    messages_response = list_messages(inbox_id)

                    # Handle both dict and object responses
                    if hasattr(messages_response, 'messages'):
                        messages_list = messages_response.messages
                    elif isinstance(messages_response, dict) and 'messages' in messages_response:
                        messages_list = messages_response['messages']
                    else:
                        messages_list = []

                    all_messages.extend(messages_list)
                except Exception as e:
                    st.warning(f"Could not load messages from inbox {inbox_id}: {str(e)}")
                    continue

        if not all_messages:
            st.info("📭 No emails found in any inbox.")
            st.stop()

        # Separate sent and received emails (without fetching full content yet)
        sent_emails = []
        received_emails = []

        for email in all_messages:
            try:
                # Extract fields from object attributes (don't fetch full content yet)
                inbox_id = getattr(email, 'inbox_id', None)
                message_id = getattr(email, 'message_id', None)
                sender = getattr(email, 'from', None) or 'Unknown'
                recipients = getattr(email, 'to', None) or []
                subject = getattr(email, 'subject', None) or '(No Subject)'
                date = getattr(email, 'created_at', None) or getattr(email, 'timestamp', None) or 'Unknown Date'
                preview = getattr(email, 'preview', None) or 'No preview'
                labels = getattr(email, 'labels', []) or []

                # Convert recipients list to string
                if isinstance(recipients, list):
                    recipient_str = ', '.join(recipients) if recipients else 'Unknown'
                else:
                    recipient_str = str(recipients) if recipients else 'Unknown'

                # Determine if sent or received based on labels
                is_sent = 'sent' in labels if labels else False

                email_data = {
                    'inbox_id': inbox_id,
                    'message_id': message_id,
                    'subject': subject,
                    'date': date,
                    'preview': preview,
                    'labels': labels,
                    'body': None  # Will be fetched on-demand
                }

                if is_sent:
                    email_data['to'] = recipient_str
                    email_data['from'] = sender
                    sent_emails.append(email_data)
                else:
                    email_data['from'] = sender
                    email_data['to'] = recipient_str
                    received_emails.append(email_data)

            except Exception as e:
                st.warning(f"Could not process email: {str(e)}")
                continue

        # Store in session state
        st.session_state.sent_emails = sent_emails
        st.session_state.received_emails = received_emails
        st.session_state.all_emails_loaded = True
        st.session_state.current_batch = 1

    # Get current batch of emails
    sent_emails = st.session_state.sent_emails
    received_emails = st.session_state.received_emails
    current_batch = st.session_state.current_batch

    # Calculate pagination - show only current page
    start_idx = (current_batch - 1) * BATCH_SIZE
    end_idx = start_idx + BATCH_SIZE

    sent_batch = sent_emails[start_idx:end_idx]
    received_batch = received_emails[start_idx:end_idx]

    total_emails = len(sent_emails) + len(received_emails)
    showing_until = min(end_idx, total_emails)
    total_sent = len(sent_emails)
    total_received = len(received_emails)

    # Display pagination info
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write(f"Page {current_batch} — Showing {start_idx + 1}-{showing_until} of {total_emails} emails")

    # Create tabs for sent and received
    tab1, tab2 = st.tabs([f"📤 Sent ({len(sent_emails)})", f"📥 Received ({len(received_emails)})"])

    # Sent emails tab
    with tab1:
        if sent_batch:
            for email in sent_batch:
                with st.expander(f"📤 {email['to']} | {email['subject']}", expanded=False):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**To:** {email['to']}")
                        st.write(f"**Subject:** {email['subject']}")

                    with col2:
                        st.write(f"**Date:** {email['date']}")
                        st.write(f"**Status:** ✅ Sent")

                    st.write("**Message:**")

                    # Fetch full content on demand if not already loaded
                    if email['body'] is None:
                        try:
                            full_message = get_message(email['inbox_id'], email['message_id'])
                            if full_message:
                                body_text = getattr(full_message, 'body', None) or getattr(full_message, 'text', None) or 'No content available'
                                st.text(body_text)
                            else:
                                st.text("Could not load message content")
                        except Exception as e:
                            st.text(f"Error loading message: {str(e)}")
                    else:
                        st.text(email['body'] or "No content")
        else:
            st.info("📭 No sent emails in this batch.")

    # Received emails tab
    with tab2:
        if received_batch:
            for email in received_batch:
                with st.expander(f"📥 {email['from']} | {email['subject']}", expanded=False):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**From:** {email['from']}")
                        st.write(f"**Subject:** {email['subject']}")

                    with col2:
                        st.write(f"**Date:** {email['date']}")
                        st.write(f"**Status:** ✅ Received")

                    st.write("**Message:**")

                    # Fetch full content on demand if not already loaded
                    if email['body'] is None:
                        try:
                            full_message = get_message(email['inbox_id'], email['message_id'])
                            if full_message:
                                body_text = getattr(full_message, 'body', None) or getattr(full_message, 'text', None) or 'No content available'
                                st.text(body_text)
                            else:
                                st.text("Could not load message content")
                        except Exception as e:
                            st.text(f"Error loading message: {str(e)}")
                    else:
                        st.text(email['body'] or "No content")
        else:
            st.info("📭 No received emails in this batch.")

    # Pagination controls
    total_pages = (total_emails + BATCH_SIZE - 1) // BATCH_SIZE
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if current_batch > 1:
                if st.button("⬅️ Previous", use_container_width=True):
                    st.session_state.current_batch -= 1
                    st.rerun()
            else:
                st.write("")

        with col2:
            st.write(f"Page {current_batch} of {total_pages}", )

        with col3:
            if current_batch < total_pages:
                if st.button("Next ➡️", use_container_width=True):
                    st.session_state.current_batch += 1
                    st.rerun()

except Exception as e:
    st.error(f"❌ Error loading inbox: {str(e)}")
    st.info("Make sure you have an AgentMail API key configured and try again.")
    import traceback
    with st.expander("Debug Info"):
        st.write(traceback.format_exc())
