# import google.generativeai as genai
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configure Llama API
LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")
llama_client = None
if LLAMA_API_KEY:
    llama_client = OpenAI(
        api_key=LLAMA_API_KEY,
        base_url="https://api.llama.com/compat/v1/"
    )

# Gemini Configuration (DISABLED)
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# if GEMINI_API_KEY:
#     genai.configure(api_key=GEMINI_API_KEY)
#     # Use the latest Gemini model with high rate limits
#     model = genai.GenerativeModel('gemini-2.0-flash-lite')  # Fast model with high rate limits
#     # all models: https://ai.google.dev/gemini-api/docs/models

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

def clean_placeholder_content(content):
    """Remove or replace placeholder content with generic professional content"""
    import re
    
    # Common placeholder patterns to replace
    placeholder_patterns = [
        (r'\[Your [^\]]+\]', ''),
        (r'\[your [^\]]+\]', ''),
        (r'\{[^}]+\}', ''),
        (r'your major here', 'Computer Science'),
        (r'put information about yourself here', 'I am a motivated professional with relevant experience'),
        (r'insert details here', 'relevant details'),
        (r'mention your experience', 'my experience'),
        (r'add your qualifications', 'my qualifications'),
        (r'insert your background', 'my background'),
        (r'describe your skills', 'my skills'),
        (r'your experience here', 'relevant professional experience'),
        (r'your background here', 'a strong background in technology'),
        (r'your qualifications here', 'relevant qualifications'),
        (r'your skills here', 'strong technical skills'),
    ]
    
    # Apply replacements (case insensitive)
    for pattern, replacement in placeholder_patterns:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    # Clean up any remaining brackets or braces that might contain placeholders
    content = re.sub(r'\[[^\]]*\]', '', content)
    content = re.sub(r'\{[^}]*\}', '', content)
    
    # Clean up extra spaces and line breaks
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'\n\s*\n', '\n\n', content)
    
    return content.strip()

def generate_personalized_email(recipient_email, template=None, prompt=None, subject=None, customize_per_recipient=False, contact_context=None, sender_info=None):
    """Generate personalized email using Llama API"""
    
    if not LLAMA_API_KEY or not llama_client:
        # Fallback if no Llama API key
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
            
            Sender Information (USE THIS FOR ANY PERSONAL DETAILS):
            {sender_info if sender_info else "Professional with relevant experience seeking opportunities"}
            
            CRITICAL INSTRUCTIONS - READ CAREFULLY:
            - Generate a compelling subject line and enhance the email body
            - Replace ALL placeholders like {{name}}, {{company}}, {{title}}, etc. with actual content
            - When you need information about the sender (like name, background, experience, education), ONLY use the "Sender Information" provided above
            - NEVER make up names, majors, companies, or personal details about the sender
            - If sender information is not provided for something specific, write in a general professional manner without specific personal details
            - NEVER leave anything blank or as placeholder text like [Your Name], [Company], "your major here", etc.
            - The email must be 100% complete and ready to send without any editing needed
            - DO NOT include any closing signatures, sign-offs, or closing statements like "Best regards," "Sincerely," etc.
            - The user will add their own signature separately
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
            
            Sender Information (USE THIS FOR ANY PERSONAL DETAILS):
            {sender_info if sender_info else "Professional with relevant experience seeking opportunities"}
            
            CRITICAL INSTRUCTIONS - READ CAREFULLY:
            - Generate both a compelling subject line and email body
            - When you need information about the sender (like name, background, experience, education), ONLY use the "Sender Information" provided above
            - NEVER make up names, majors, companies, or personal details about the sender
            - If sender information is not provided for something specific, write in a general professional manner without specific personal details
            - NEVER leave anything blank or as placeholder text like [Your Name], [Company], "your major here", etc.
            - The email must be 100% complete and ready to send without any editing needed
            - DO NOT include any closing signatures, sign-offs, or closing statements like "Best regards," "Sincerely," etc.
            - The user will add their own signature separately
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
            
            Sender Information (USE THIS FOR ANY PERSONAL DETAILS):
            {sender_info if sender_info else "Professional with relevant experience seeking opportunities"}
            
            CRITICAL INSTRUCTIONS - READ CAREFULLY:
            - Make it engaging and professional
            - Generate both subject and body
            - When you need information about the sender (like name, background, experience, education), ONLY use the "Sender Information" provided above
            - NEVER make up names, majors, companies, or personal details about the sender
            - If sender information is not provided for something specific, write in a general professional manner without specific personal details
            - NEVER leave anything blank or as placeholder text like [Your Name], [Company], "your major here", etc.
            - The email must be 100% complete and ready to send without any editing needed
            - DO NOT include any closing signatures, sign-offs, or closing statements like "Best regards," "Sincerely," etc.
            - The user will add their own signature separately
            {customization_note}
            
            Format your response as:
            SUBJECT: [subject line here]
            BODY: [email body here]
            """
        
        # Use Llama API
        completion = llama_client.chat.completions.create(
            model="Llama-3.3-70B-Instruct",  # Using a good balance model
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional email writing assistant. Generate complete, ready-to-send emails based on the user's requirements."
                },
                {
                    "role": "user",
                    "content": ai_prompt
                }
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        content = completion.choices[0].message.content
        
        # Post-process to remove any remaining placeholders
        content = clean_placeholder_content(content)
        
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
        print(f"Llama API error: {e}")
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
