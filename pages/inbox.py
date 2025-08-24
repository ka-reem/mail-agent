import streamlit as st
from components.agentmail_utils import create_inbox, list_messages, get_message

st.title("Inbox Management")

# Create Inbox
st.header("Create Inbox")
if st.button("Create Inbox"):
    inbox = create_inbox()
    st.success(f"Inbox created successfully! ID: {inbox.inbox_id}")

# List Messages
st.header("List Messages")
inbox_id = st.text_input("Inbox ID for listing messages")
if st.button("List Messages"):
    messages = list_messages(inbox_id)
    st.write(f"Found {len(messages)} messages:")
    for message in messages:
        st.write(f"- Subject: {message['subject']}")

# Get Message
st.header("Get Message")
message_id = st.text_input("Message ID")
if st.button("Get Message"):
    message = get_message(inbox_id, message_id)
    st.write(f"Subject: {message['subject']}")
    st.write(f"Body: {message['body']}")
