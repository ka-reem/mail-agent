import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Use the latest Gemini model with high rate limits
    model = genai.GenerativeModel('gemini-2.0-flash-lite')  # Fast model with high rate limits
    # all models: https://ai.google.dev/gemini-api/docs/models

def extract_name_and_company(email):
    """Extract name and company from email address using simple logic"""
    try:
        username, domain = email.split('@')
        
        # Extract name from username (handle dots, underscores)
        name_parts = username.replace('.', ' ').replace('_', ' ').split()
        name = ' '.join([part.capitalize() for part in name_parts])
        
        # Extract company from domain
        company = domain.split('.')[0].capitalize()
        
        return name, company
    except:
        return "there", "your company"

def generate_personalized_email(recipient_email, template=None, prompt=None, subject=None):
    """Generate personalized email using Gemini AI"""
    
    if not GEMINI_API_KEY:
        # Fallback if no Gemini API key
        name, company = extract_name_and_company(recipient_email)
        return {
            'subject': subject or f"Exciting Opportunity at {company}",
            'body': f"Hi {name},\n\nI hope this email finds you well. I wanted to reach out regarding an exciting opportunity that might interest you.\n\nBest regards"
        }
    
    name, company = extract_name_and_company(recipient_email)
    
    try:
        if template:
            # Use template with AI enhancement
            ai_prompt = f"""
            You are writing a professional email. Use this template but make it more engaging and personalized:
            
            Template: {template}
            
            Recipient: {name} at {company}
            Email: {recipient_email}
            
            Generate a compelling subject line and enhance the email body. Replace placeholders like {{name}} and {{company}} appropriately.
            
            Format your response as:
            SUBJECT: [subject line here]
            BODY: [email body here]
            """
        elif prompt:
            # Use custom prompt
            ai_prompt = f"""
            {prompt}
            
            Recipient details:
            - Name: {name}
            - Company: {company}
            - Email: {recipient_email}
            
            Generate both a compelling subject line and email body.
            
            Format your response as:
            SUBJECT: [subject line here]
            BODY: [email body here]
            """
        else:
            # Default AI generation
            ai_prompt = f"""
            Write a professional, personalized email to {name} who works at {company} ({recipient_email}).
            
            Make it engaging and professional. Generate both subject and body.
            
            Format your response as:
            SUBJECT: [subject line here]
            BODY: [email body here]
            """
        
        response = model.generate_content(ai_prompt)
        content = response.text
        
        # Parse the response
        if "SUBJECT:" in content and "BODY:" in content:
            subject_part = content.split("SUBJECT:")[1].split("BODY:")[0].strip()
            body_part = content.split("BODY:")[1].strip()
            
            return {
                'subject': subject_part,
                'body': body_part
            }
        else:
            # Fallback parsing
            lines = content.strip().split('\n')
            return {
                'subject': subject or f"Personalized message for {name}",
                'body': content
            }
    
    except Exception as e:
        print(f"Gemini API error: {e}")
        # Fallback content
        return {
            'subject': subject or f"Exciting Opportunity at {company}",
            'body': f"Hi {name},\n\nI hope this email finds you well. I wanted to reach out regarding an exciting opportunity.\n\nBest regards"
        }
