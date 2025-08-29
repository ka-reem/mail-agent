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

def generate_personalized_email(recipient_email, template=None, prompt=None, subject=None, customize_per_recipient=False, contact_context=None):
    """Generate personalized email using Gemini AI"""
    
    if not GEMINI_API_KEY:
        # Fallback if no Gemini API key
        if contact_context:
            name = contact_context.get('name', 'there')
            company = contact_context.get('company', 'your company')
        else:
            name, company = extract_name_and_company(recipient_email)
        
        return {
            'subject': subject or f"Exciting Opportunity at {company}",
            'body': f"Hi {name},\n\nI hope this email finds you well. I wanted to reach out regarding an exciting opportunity that might interest you."
        }
    
    # Use contact context if provided, otherwise extract from email
    if contact_context:
        name = contact_context.get('name', 'there')
        company = contact_context.get('company', 'your company')
        title = contact_context.get('title', 'Professional')
    else:
        name, company = extract_name_and_company(recipient_email)
        title = "Professional"
    
    try:
        if template:
            # Use template with AI enhancement
            customization_note = "\n\nIMPORTANT: Generate VERY similar content for consistency across recipients. Only personalize the name and company." if not customize_per_recipient else "\n\nGenerate highly customized content based on the recipient's company and background."
            
            ai_prompt = f"""
            You are writing a professional email. Use this template but make it more engaging and personalized:
            
            Template: {template}
            
            Recipient Details:
            - Name: {name}
            - Company: {company}
            - Title: {title}
            - Email: {recipient_email}
            {f"- Additional Context: {contact_context}" if contact_context and contact_context.get('original_data') else ""}
            
            CRITICAL INSTRUCTIONS:
            - Generate a compelling subject line and enhance the email body
            - Replace ALL placeholders like {{name}}, {{company}}, {{title}}, etc. with actual content
            - NEVER leave anything blank or as placeholder text like [Your Name], [Company], etc.
            - If you don't have specific information, make reasonable professional assumptions
            - Ensure the email is complete and ready to send without any editing needed
            - DO NOT include any closing signatures, sign-offs, or closing statements like "Best regards," "Sincerely," "Thank you," "[Your Name]," etc.
            - The email should end with the main content, not a formal closing
            - The user will add their own signature separately, so do not include any signature-like content
            {customization_note}
            
            Format your response as:
            SUBJECT: [subject line here]
            BODY: [email body here]
            """
        elif prompt:
            # Use custom prompt
            customization_note = "\n\nIMPORTANT: Keep the core message consistent across all recipients. Only personalize names and companies." if not customize_per_recipient else "\n\nCreate unique, highly personalized content based on the recipient's specific company and industry."
            
            ai_prompt = f"""
            {prompt}
            
            Recipient Details:
            - Name: {name}
            - Company: {company}
            - Title: {title}
            - Email: {recipient_email}
            {f"- Additional Context: {contact_context}" if contact_context and contact_context.get('original_data') else ""}
            
            CRITICAL INSTRUCTIONS:
            - Generate both a compelling subject line and email body
            - NEVER leave anything blank or as placeholder text like [Your Name], [Company], {{name}}, etc.
            - Fill in ALL information with actual content - if you don't have specific details, make reasonable professional assumptions
            - The email must be complete and ready to send without any editing needed
            - Do not include any brackets, curly braces, or placeholder formatting
            - DO NOT include any closing signatures, sign-offs, or closing statements like "Best regards," "Sincerely," "Thank you," "[Your Name]," etc.
            - The email should end with the main content, not a formal closing
            - The user will add their own signature separately, so do not include any signature-like content
            {customization_note}
            
            Format your response as:
            SUBJECT: [subject line here]
            BODY: [email body here]
            """
        else:
            # Default AI generation
            customization_note = "Keep the message professional and consistent. Only personalize with their name and company." if not customize_per_recipient else "Research typical companies in their domain and create highly specific, customized content."
            
            ai_prompt = f"""
            Write a professional, personalized email to {name} who works at {company} as a {title} ({recipient_email}).
            {f"Additional context: {contact_context}" if contact_context and contact_context.get('original_data') else ""}
            
            CRITICAL INSTRUCTIONS:
            - Make it engaging and professional
            - Generate both subject and body
            - NEVER leave anything blank or as placeholder text like [Your Name], [Company], {{name}}, etc.
            - Fill in ALL information with actual content - if you don't have specific details, make reasonable professional assumptions
            - The email must be complete and ready to send without any editing needed
            - Do not include any brackets, curly braces, or placeholder formatting
            - DO NOT include any closing signatures, sign-offs, or closing statements like "Best regards," "Sincerely," "Thank you," "[Your Name]," etc.
            - The email should end with the main content, not a formal closing
            - The user will add their own signature separately, so do not include any signature-like content
            {customization_note}
            
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
        if contact_context:
            name = contact_context.get('name', 'there')
            company = contact_context.get('company', 'your company')
        else:
            name, company = extract_name_and_company(recipient_email)
            
        return {
            'subject': subject or f"Exciting Opportunity at {company}",
            'body': f"Hi {name},\n\nI hope this email finds you well. I wanted to reach out regarding an exciting opportunity."
        }
