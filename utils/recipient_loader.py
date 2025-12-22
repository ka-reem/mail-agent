"""
Utilities for loading and managing city ordinance recipients
"""
import json
import os
import re
from typing import List, Dict

from config import CITY_ORDINANCE_RECIPIENTS_FILE, EMAIL_PATTERN


def load_city_ordinance_recipients() -> List[Dict]:
    """
    Load and validate recipients from city_ordinance_recipients.json

    Returns:
        List of contact dictionaries with name, email, department, etc.

    Raises:
        FileNotFoundError: If recipients file doesn't exist
        json.JSONDecodeError: If JSON is malformed
        ValueError: If no valid emails found in recipient list
    """
    if not os.path.exists(CITY_ORDINANCE_RECIPIENTS_FILE):
        raise FileNotFoundError(
            f"Recipient file not found: {CITY_ORDINANCE_RECIPIENTS_FILE}"
        )

    try:
        with open(CITY_ORDINANCE_RECIPIENTS_FILE, 'r') as f:
            contacts = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in {CITY_ORDINANCE_RECIPIENTS_FILE}: {str(e)}",
            e.doc,
            e.pos
        )

    if not isinstance(contacts, list):
        raise ValueError("Recipients JSON must be an array of contact objects")

    if not contacts:
        raise ValueError("Recipients list is empty")

    # Validate that all contacts have email addresses
    valid_contacts = []
    for contact in contacts:
        if not isinstance(contact, dict):
            continue
        email = contact.get('email', '').strip()
        if email and is_valid_email(email):
            valid_contacts.append(contact)

    if not valid_contacts:
        raise ValueError("No valid email addresses found in recipients list")

    return valid_contacts


def get_recipient_emails(contacts: List[Dict]) -> List[str]:
    """
    Extract list of email addresses from contacts (for backward compatibility)

    Args:
        contacts: List of contact dictionaries

    Returns:
        List of email strings
    """
    emails = []
    for contact in contacts:
        email = contact.get('email', '').strip()
        if email and is_valid_email(email):
            emails.append(email)
    return emails


def get_pge_emails(contacts: List[Dict]) -> List[str]:
    """
    Extract email addresses for all PG&E contacts

    Args:
        contacts: List of contact dictionaries

    Returns:
        List of PG&E email strings
    """
    emails = []
    for contact in contacts:
        if contact.get('org') == 'PG&E':
            email = contact.get('email', '').strip()
            if email and is_valid_email(email):
                emails.append(email)
    return emails


def format_recipient_display(contact: Dict) -> str:
    """
    Format a contact for UI display

    Args:
        contact: Contact dictionary

    Returns:
        Formatted string based on available fields
    """
    email = contact.get('email', '')
    org = contact.get('org', '')
    contact_type = contact.get('type', '')

    # Handle new structure (org + type)
    if org and contact_type:
        return f"{contact_type} - {org} ({email})"
    elif org:
        return f"{org} ({email})"
    else:
        return email


def is_valid_email(email: str) -> bool:
    """
    Validate email address format

    Args:
        email: Email string to validate

    Returns:
        True if valid email format, False otherwise
    """
    pattern = EMAIL_PATTERN
    return bool(re.match(pattern, email))
