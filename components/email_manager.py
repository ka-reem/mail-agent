"""
Email workflow management
Handles email generation, approval, and sending workflows
"""
import streamlit as st
import time
from typing import List, Dict, Optional
from components.agentmail_utils import create_inbox, send_email
from components.ai_utils import generate_personalized_email
from utils.session_manager import get_email_data, set_email_data, mark_email_sent

class EmailManager:
    """Manages email generation, approval, and sending workflows"""
    
    def __init__(self, create_inbox_toggle: bool, selected_inbox: Optional[str] = None):
        self.create_inbox_toggle = create_inbox_toggle
        self.selected_inbox = selected_inbox
    
    def generate_email_data(self, recipients: List[str], email_config: Dict, json_contacts: List[Dict] = None) -> List[Dict]:
        """Generate email data for all recipients"""
        email_data = []
        
        # Get signature from session state if available
        signature = st.session_state.get('email_signature', '')
        
        # Create a mapping from email to contact info if JSON contacts provided
        contact_mapping = {}
        if json_contacts:
            for contact in json_contacts:
                contact_mapping[contact['email']] = contact
        
        for i, recipient in enumerate(recipients):
            try:
                if email_config['email_type'] == "regular":
                    current_subject = email_config['subject']
                    current_body = email_config['body']
                else:
                    # AI Email generation
                    with st.spinner(f"Generating personalized email for {recipient}..."):
                        # Get contact context if available
                        contact_context = contact_mapping.get(recipient, None)
                        
                        ai_result = generate_personalized_email(
                            recipient_email=recipient,
                            template=email_config.get('template'),
                            prompt=email_config.get('prompt'),
                            subject=email_config.get('subject'),
                            customize_per_recipient=email_config.get('customize_per_recipient', False),
                            contact_context=contact_context
                        )
                        current_subject = ai_result['subject']
                        current_body = ai_result['body']
                        
                        # Add signature to AI-generated email if signature exists
                        if signature:
                            current_body = f"{current_body}\n\n{signature}"
                
                email_data.append({
                    'recipient': recipient,
                    'subject': current_subject,
                    'body': current_body,
                    'approved': False,
                    'sent': False
                })
                
            except Exception as e:
                st.error(f"Failed to generate email for {recipient}: {e}")
        
        return email_data
    
    def send_single_email(self, email_info: Dict) -> bool:
        """Send a single email"""
        try:
            # Create or use existing inbox
            if self.create_inbox_toggle:
                inbox = create_inbox()
                current_inbox_id = inbox.inbox_id
                time.sleep(1)
            else:
                current_inbox_id = self.selected_inbox
                if not current_inbox_id:
                    st.error("No inbox selected.")
                    return False
            
            # Send email
            response = send_email(
                current_inbox_id, 
                email_info['recipient'], 
                email_info['subject'], 
                email_info['body']
            )
            return True
            
        except Exception as e:
            st.error(f"Failed to send to {email_info['recipient']}: {e}")
            return False
    
    def send_multiple_emails(self, emails_to_send: List[Dict]) -> Dict[str, int]:
        """Send multiple emails with progress tracking"""
        success_count = 0
        failed_count = 0
        
        # Progress tracking
        if len(emails_to_send) > 1:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        for i, email_info in enumerate(emails_to_send):
            with st.spinner(f"Sending to {email_info['recipient']}..."):
                if self.send_single_email(email_info):
                    success_count += 1
                else:
                    failed_count += 1
            
            # Update progress
            if len(emails_to_send) > 1:
                progress = (i + 1) / len(emails_to_send)
                progress_bar.progress(progress)
                status_text.text(f"Processing {i + 1}/{len(emails_to_send)} emails...")
        
        return {'success': success_count, 'failed': failed_count}
    
    def get_approved_emails(self, email_data: List[Dict]) -> List[Dict]:
        """Get list of approved but not sent emails"""
        return [email for email in email_data 
                if email.get('approved', False) and not email.get('sent', False)]
    
    def display_results(self, results: Dict[str, int]):
        """Display sending results"""
        if results['success'] > 0:
            st.success(f"Successfully sent {results['success']} emails!")
        if results['failed'] > 0:
            st.error(f"{results['failed']} emails failed to send")

def create_email_config(email_type: str, **kwargs) -> Dict:
    """Create email configuration dictionary"""
    config = {'email_type': email_type}
    config.update(kwargs)
    return config
