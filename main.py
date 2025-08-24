import streamlit as st
from components.agentmail_utils import create_inbox, send_email, list_inboxes
import time

st.set_page_config(page_title="Mail Agent", page_icon="📬", layout="wide")
st.title("📬 Mail Agent")
st.write("Welcome to the Mail Agent app! Manage your emails easily.")

# Send Email
st.header("Send Email")

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

recipient = st.text_input("Recipient Email")
subject = st.text_input("Subject")
body = st.text_area("Message Body")

if st.button("Send Email"):
    if create_new_inbox:
        with st.spinner("Creating new inbox..."):
            inbox = create_inbox()  # Automatically create a new inbox
            inbox_id = inbox.inbox_id
            st.info(f"Created new inbox: {inbox_id}")
            # Add a small delay to ensure inbox is ready
            time.sleep(1)
    
    if inbox_id and recipient and subject:
        try:
            with st.spinner("Sending email..."):
                response = send_email(inbox_id, recipient, subject, body)
                st.success(f"Email sent successfully! Inbox ID: {inbox_id}, Message ID: {response.message_id}")
        except Exception as e:
            st.error(f"Error sending email: {e}")
    else:
        st.error("Please fill in all required fields.")