"""
Email preview and approval workflow management
"""
import streamlit as st
from typing import List, Dict
from components.email_manager import EmailManager
from utils.session_manager import get_email_data, mark_email_sent

class EmailApprovalManager:
    """Manages email preview and approval workflows"""
    
    def __init__(self, email_manager: EmailManager):
        self.email_manager = email_manager
    
    def display_email_previews(self, email_data: List[Dict], preview_emails: bool, 
                              human_approval: bool) -> None:
        """Display email previews with approval interface"""
        if not (preview_emails or human_approval):
            return
            
        st.subheader("AI Generated Email Previews")
        
        # Add bulk select controls if human approval is required
        if human_approval:
            self._display_bulk_approval_controls(email_data)
        
        for i, email_info in enumerate(email_data):
            with st.expander(f"Email for {email_info['recipient']}", expanded=human_approval):
                if human_approval and not email_info.get('sent', False):
                    # Editable email content
                    st.write("✏️ **Edit Email Content:**")
                    
                    # Editable subject
                    edited_subject = st.text_input(
                        "Subject:",
                        value=email_info['subject'],
                        key=f"subject_{i}_{email_info['recipient']}"
                    )
                    
                    # Editable body
                    edited_body = st.text_area(
                        "Email Body:",
                        value=email_info['body'],
                        height=200,
                        key=f"body_{i}_{email_info['recipient']}"
                    )
                    
                    # Update the email data if content was edited
                    if edited_subject != email_info['subject'] or edited_body != email_info['body']:
                        st.session_state.email_data[i]['subject'] = edited_subject
                        st.session_state.email_data[i]['body'] = edited_body
                    
                    st.markdown("---")
                    self._display_approval_controls(i, email_info)
                else:
                    # Read-only preview
                    st.write(f"**Subject:** {email_info['subject']}")
                    st.write(f"**Body:**")
                    st.write(email_info['body'])
                    
                if email_info.get('sent', False):
                    st.success(f"✅ Email already sent to {email_info['recipient']}")
    
    def _display_bulk_approval_controls(self, email_data: List[Dict]) -> None:
        """Display bulk approval controls"""
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            select_all = st.checkbox("📧 Select All", key="select_all_emails")
        
        with col2:
            if st.button("Clear All", key="clear_all_emails"):
                # Clear all approvals
                for i, email_info in enumerate(email_data):
                    if not email_info.get('sent', False):
                        st.session_state.email_data[i]['approved'] = False
                        # Clear individual checkboxes
                        approval_key = f"approve_{i}_{email_info['recipient']}"
                        if approval_key in st.session_state:
                            st.session_state[approval_key] = False
                st.session_state.select_all_emails = False
                st.rerun()
        
        # Handle select all functionality
        if select_all:
            for i, email_info in enumerate(email_data):
                if not email_info.get('sent', False):
                    st.session_state.email_data[i]['approved'] = True
                    # Update individual checkboxes
                    approval_key = f"approve_{i}_{email_info['recipient']}"
                    st.session_state[approval_key] = True
        
        st.markdown("---")
    
    def _display_approval_controls(self, index: int, email_info: Dict) -> None:
        """Display approval controls for individual email"""
        # Individual approval checkbox
        approval_key = f"approve_{index}_{email_info['recipient']}"
        approved = st.checkbox(
            f"✅ Approve this email for {email_info['recipient']}", 
            key=approval_key,
            value=email_info.get('approved', False)
        )
        
        # Update the approval status in session state
        st.session_state.email_data[index]['approved'] = approved
        
        # Individual send button
        if approved and st.button(f"Send to {email_info['recipient']}", key=f"send_{index}"):
            self._send_individual_email(index, email_info)
    
    def _send_individual_email(self, index: int, email_info: Dict) -> None:
        """Send individual email and update status"""
        with st.spinner(f"Sending to {email_info['recipient']}..."):
            if self.email_manager.send_single_email(email_info):
                st.success(f"✅ Email sent successfully to {email_info['recipient']}!")
                mark_email_sent(index)
                st.rerun()
    
    def display_bulk_send_controls(self, email_data: List[Dict]) -> None:
        """Display bulk send controls for approved emails"""
        st.markdown("---")
        approved_emails = self.email_manager.get_approved_emails(email_data)
        
        if approved_emails:
            if st.button(f"📧 Send All Approved Emails ({len(approved_emails)} emails)", 
                        use_container_width=True):
                self._send_bulk_emails(approved_emails, email_data)
        else:
            st.info("No emails approved for sending. Please approve emails above to enable bulk sending.")
    
    def _send_bulk_emails(self, approved_emails: List[Dict], all_email_data: List[Dict]) -> None:
        """Send all approved emails in bulk"""
        results = self.email_manager.send_multiple_emails(approved_emails)
        
        # Update sent status for successfully sent emails
        for email_info in approved_emails:
            # Find the index in the original list and mark as sent
            for i, original_email in enumerate(all_email_data):
                if original_email['recipient'] == email_info['recipient']:
                    mark_email_sent(i)
                    break
        
        self.email_manager.display_results(results)
        st.rerun()

def display_auto_send_workflow(email_manager: EmailManager, email_data: List[Dict]) -> None:
    """Handle auto-send workflow (no approval required)"""
    results = email_manager.send_multiple_emails(email_data)
    email_manager.display_results(results)
    
    # Mark all emails as sent in session state
    for i, _ in enumerate(email_data):
        mark_email_sent(i)
