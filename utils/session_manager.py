"""
Session state management utilities for Mail Agent
Handles all Streamlit session state operations
"""
import streamlit as st

def init_session_state():
    """Initialize all session state variables with default values"""
    if 'email_type' not in st.session_state:
        st.session_state.email_type = "ai"
    
    if 'email_data_generated' not in st.session_state:
        st.session_state.email_data_generated = False
    
    if 'email_signature' not in st.session_state:
        st.session_state.email_signature = ""
    
    if 'sender_info' not in st.session_state:
        st.session_state.sender_info = ""

def reset_email_data():
    """Reset email generation data"""
    st.session_state.email_data_generated = False
    if 'email_data' in st.session_state:
        del st.session_state.email_data

def get_email_data():
    """Get current email data from session state"""
    return st.session_state.get('email_data', [])

def set_email_data(email_data):
    """Store email data in session state"""
    st.session_state.email_data = email_data
    st.session_state.email_data_generated = True

def is_email_data_generated():
    """Check if email data has been generated"""
    return st.session_state.get('email_data_generated', False) and 'email_data' in st.session_state

def update_email_approval(index, approved):
    """Update approval status for specific email"""
    if 'email_data' in st.session_state and index < len(st.session_state.email_data):
        st.session_state.email_data[index]['approved'] = approved

def mark_email_sent(index):
    """Mark email as sent"""
    if 'email_data' in st.session_state and index < len(st.session_state.email_data):
        st.session_state.email_data[index]['sent'] = True
