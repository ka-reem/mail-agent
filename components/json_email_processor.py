"""
JSON-based email generation processor
Handles JSON input with flexible field mapping for email generation
"""
import streamlit as st
import json
from typing import List, Dict, Optional, Any
import re

def extract_contact_info_from_json(json_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Extract contact information from JSON with flexible field mapping
    Supports various field name patterns and structures
    """
    extracted_contacts = []
    
    # Common field name mappings
    name_fields = ['name', 'full_name', 'fullname', 'person_name', 'first_name', 'fname', 'contact_name']
    email_fields = ['email', 'email_address', 'contact_email', 'mail', 'e_mail']
    company_fields = ['company', 'organization', 'employer', 'corp', 'business', 'firm']
    title_fields = ['title', 'position', 'job_title', 'role', 'designation', 'job_position']
    
    for entry in json_data:
        try:
            if not isinstance(entry, dict):
                continue
                
            # Extract fields using flexible matching
            extracted_info = {
                'name': extract_field_value(entry, name_fields, 'there'),
                'email': extract_field_value(entry, email_fields, None),
                'company': extract_field_value(entry, company_fields, 'your company'),
                'title': extract_field_value(entry, title_fields, 'Professional')
            }
            
            # Only include entries with valid email addresses
            if extracted_info['email'] and is_valid_email(extracted_info['email']):
                # Store original entry for AI context
                extracted_info['original_data'] = entry
                extracted_contacts.append(extracted_info)
                
        except Exception as e:
            st.warning(f"Error processing entry: {entry}. Error: {str(e)}")
            continue
    
    return extracted_contacts

def extract_field_value(entry: Dict[str, Any], possible_fields: List[str], default: Optional[str]) -> str:
    """Extract field value using case-insensitive matching"""
    for field in possible_fields:
        # Direct match
        if field in entry and entry[field]:
            return str(entry[field])
        
        # Case-insensitive match
        for key, value in entry.items():
            if key.lower() == field.lower() and value:
                return str(value)
    
    return default or ""

def is_valid_email(email: str) -> bool:
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def display_json_email_input() -> Optional[List[Dict[str, str]]]:
    """Display JSON input interface and return extracted contact data"""
    with st.expander("Import Recipients from JSON (Recommended)", expanded=False):
        # st.write("Paste your JSON with recipient info. Make sure to include \"email\": \"their@email.com\". Other fields like name, title, or job will be used automatically. Well-labeled data works better than dumping everything into \"info\".")
        st.write("Paste your JSON with recipient data. The only required field is \"email\". Other fields such as name, title, or company are optional but will improve personalization. For best results, use a deep research model to generate enriched JSON based off of emails and names.")

        st.write("[Here's a very simple example using Perplexity Deep Research](https://www.perplexity.ai/search/fill-out-this-json-with-50-rec-EyOlYmqCSt67XDWXadjzzg) to predict emails. This can be improved with better prompting or by finding common email patterns at companies. Otherwise you can use/build your own scraper or buy email lists.")

        json_data = None
        
        json_text = st.text_area(
            "Paste your JSON data here:",
            placeholder='[\n  {\n    "name": "John Doe",\n    "company": "TechCorp",\n    "title": "Senior Engineer",\n    "email": "john@techcorp.com"\n  },\n  {\n    "name": "Sarah Johnson",\n    "company": "StartupXYZ",\n    "title": "Product Manager",\n    "email": "sarah@startupxyz.io"\n  }\n]',
            height=200,
            key="json_paste_input"
        )
        
        if json_text.strip():
            try:
                json_data = json.loads(json_text)
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON format: {str(e)}")
                return None
        
        if json_data:
            # Ensure it's a list
            if not isinstance(json_data, list):
                st.error("JSON data must be an array/list of objects")
                return None
            
            # Extract contact information
            contacts = extract_contact_info_from_json(json_data)
            
            if contacts:
                st.success(f"Successfully extracted {len(contacts)} valid contacts from JSON")
                
                # Show preview without nested expander
                st.write("**Preview of extracted data:**")
                for i, contact in enumerate(contacts[:5]):  # Show first 5
                    st.write(f"• **{contact['name']}** ({contact['email']}) - {contact['company']}, {contact['title']}")
                
                if len(contacts) > 5:
                    st.write(f"... and {len(contacts) - 5} more contacts")
                
                return contacts
            else:
                st.warning("No valid contacts found in the JSON data. Please ensure your JSON contains email addresses.")
                return None
        
        return None

def create_recipients_from_json(contacts: List[Dict[str, str]]) -> List[str]:
    """Extract just the email addresses for the recipients list"""
    return [contact['email'] for contact in contacts if contact.get('email')]

def enhance_ai_prompt_with_json_context(base_prompt: str, contact: Dict[str, str]) -> str:
    """Enhance AI prompt with additional context from JSON data"""
    context_additions = []
    
    # Add LinkedIn if available
    original_data = contact.get('original_data', {})
    if 'linkedin' in original_data:
        context_additions.append(f"LinkedIn: {original_data['linkedin']}")
    
    # Add any other relevant fields
    relevant_fields = ['location', 'experience', 'skills', 'department', 'years_experience']
    for field in relevant_fields:
        if field in original_data and original_data[field]:
            context_additions.append(f"{field.replace('_', ' ').title()}: {original_data[field]}")
    
    if context_additions:
        enhanced_prompt = f"{base_prompt}\n\nAdditional context about {contact['name']}:\n"
        enhanced_prompt += "\n".join(f"- {addition}" for addition in context_additions)
        return enhanced_prompt
    
    return base_prompt
