#!/usr/bin/env python3
"""
AI-Powered Job Application Agent
Monitors givemeajob@agentmail.to for emails from hiring@agentmail.to
and automatically responds with AI-generated job application emails
"""

import os
import sys
import time
from datetime import datetime
import html

# Add the parent directory to the path to import our utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv
from agentmail import AgentMail
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configuration
INBOX_ID = "givemeajob@agentmail.to"
HIRING_EMAIL = "hiring@agentmail.to"
POLL_INTERVAL = 4 # Check for new emails every 5 seconds(sweet spot seems like 8)

# Initialize AgentMail client
agentmail_api_key = os.getenv("AGENTMAIL_API_KEY")
if not agentmail_api_key:
    raise Exception("AGENTMAIL_API_KEY not found in environment variables")

client = AgentMail(api_key=agentmail_api_key)

# Initialize Llama API client
llama_api_key = os.getenv("LLAMA_API_KEY")
if not llama_api_key:
    raise Exception("LLAMA_API_KEY not found in environment variables")

llama_client = OpenAI(
    api_key=llama_api_key,
    base_url="https://api.llama.com/compat/v1/"
)

def generate_job_application_response(previous_message, conversation_history=""):
    """Generate an AI-powered job application response using Llama API"""
    
    # Determine if this is the first message or a continuation
    is_first_message = not conversation_history.strip()
    
    prompt = f"""
    You are an extremely eager job seeker named Alex responding to a hiring manager's email.
    
    {"This is your FIRST response to their initial outreach." if is_first_message else "This is a CONTINUATION of an ongoing conversation thread."}
    
    Latest message from hiring manager:
    {previous_message}
    
    {"" if is_first_message else f'''
    Full conversation history (chronological order):
    {conversation_history}
    '''}
    
    INSTRUCTIONS:
    - Be VERY pushy and aggressive about getting this job
    - Show you NEED this job and will do ANYTHING to get it
    - Be desperate but professional
    - {"Highlight your best skills quickly" if is_first_message else "Build on previous discussion, push for next steps"}
    - ALWAYS push for an interview, call, or meeting
    - Be persistent and convincing
    - Keep it SHORT (1-2 short paragraphs ONLY)
    - End with urgent action request
    - Show you're available IMMEDIATELY
    - Make them feel like they'd be crazy not to hire you
    
    Generate ONLY the email body text (no subject line needed for replies).
    Keep it under 100 words. Be direct and pushy.
    """
    
    try:
        completion = llama_client.chat.completions.create(
            model="Llama-3.3-70B-Instruct",
            messages=[
                {
                    "role": "system", 
                    "content": f"You are an extremely pushy, desperate job seeker named Alex who needs this job badly. {'This is your first contact - be aggressive about getting an interview.' if is_first_message else 'You are continuing a job conversation - push hard for the next step.'} Keep responses under 100 words and very direct."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=150,
            temperature=0.9
        )
        
        return completion.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Llama API error: {e}")
        # Fallback response based on conversation state
        if is_first_message:
            return """Hi! I'm Alex and I NEED this job. I have exactly what you're looking for and I'm ready to start TODAY. 

Can we talk this week? I'm available anytime - literally anytime. This is my dream opportunity and I won't let you down!"""
        else:
            return """I'm ready to move forward RIGHT NOW. Whatever you need, I can do it. 

When can we schedule an interview? I'm available 24/7 and ready to prove I'm your best choice!"""

def get_unreplied_threads():
    """Get unread threads specifically from the givemeajob@agentmail.to inbox"""
    try:
        # Get unread threads (they're already from our inbox context)
        threads_response = client.threads.list(labels=["unread"])
        
        # Access the threads from the response object
        threads = getattr(threads_response, 'threads', threads_response)
        if hasattr(threads_response, 'data'):
            threads = threads_response.data
        
        print(f"Debug: Found {len(threads)} unread threads in {INBOX_ID}")
        
        if not threads:
            print(f"No unread threads in {INBOX_ID}")
            return []
        
        # Let's work on the first unread thread
        thread_to_reply_to = threads[0]
        thread_id = getattr(thread_to_reply_to, 'thread_id', getattr(thread_to_reply_to, 'id', 'unknown'))
        print(f"Found unread thread: {thread_id}")
        
        # Get the full thread object to access its messages
        thread_details = client.threads.get(thread_id)
        
        if not thread_details.messages:
            print("Thread has no messages")
            return []
        
        # The last message in the list is the one we want to reply to
        last_message = thread_details.messages[-1]
        
        print(f"Found latest message in thread to reply to")
        return [last_message]  # Return as list to maintain compatibility
    
    except Exception as e:
        print(f"Error getting unread threads from {INBOX_ID}: {e}")
        return []

def build_conversation_history(thread_details):
    """Build a conversation history string from thread messages"""
    history = []
    
    # Get all messages except the last one (which is what we're replying to)
    messages = thread_details.messages[:-1] if len(thread_details.messages) > 1 else []
    
    for msg in messages:
        sender = getattr(msg, 'sender', 'Unknown')
        text = getattr(msg, 'text', '')
        
        # Determine if it's from us or them
        if sender == HIRING_EMAIL:
            history.append(f"HIRING MANAGER: {text}")
        else:
            history.append(f"ME (Alex): {text}")
    
    return "\n\n".join(history)


def _convert_text_to_html(text):
    """Convert plain text into simple, paragraph-aware HTML.

    - Escapes HTML entities
    - Converts consecutive blank lines into paragraph breaks
    - Converts single blank lines into paragraph spacing
    - Converts lines starting with '-' or '*' into unordered lists
    """
    if not text:
        return ""

    # Escape HTML special characters first
    escaped = html.escape(text)
    lines = escaped.splitlines()

    parts = []
    para = []
    in_list = False

    def flush_paragraph():
        nonlocal para
        if para:
            # join lines within the paragraph with a single space
            parts.append(f"<p style=\"margin:10px 0; line-height:1.6;\">{' '.join(para)}</p>")
            para = []

    for raw in lines:
        line = raw.strip()

        # blank line -> paragraph break
        if line == "":
            flush_paragraph()
            if in_list:
                parts.append("</ul>")
                in_list = False
            continue

        # list item
        if line.startswith('-') or line.startswith('*'):
            # start a list if needed
            if not in_list:
                flush_paragraph()
                parts.append('<ul style="margin:10px 0 10px 20px; padding:0;">')
                in_list = True

            item = line.lstrip('-* ').strip()
            parts.append(f"<li style=\"margin:4px 0;\">{item}</li>")
            continue

        # normal text line -> accumulate into paragraph
        para.append(line)

    # flush any remaining content
    flush_paragraph()
    if in_list:
        parts.append("</ul>")

    return ''.join(parts)

def send_reply(message_id, reply_text):
    """Send a reply to a specific message"""
    try:
        # Add visible footer to reply text
        footer_text = "\n\n---\nSent by https://automailer.streamlit.app/"
        reply_with_footer = f"{reply_text}{footer_text}"
        # Convert text body into simple HTML using helper
        body_html = _convert_text_to_html(reply_with_footer)

        # Create complete HTML email structure with clean styling
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reply</title>
    <style>
        body {{ font-family: Arial, sans-serif; color: #333; background-color: #f6f7fb; margin: 0; padding: 20px; }}
        .container {{ max-width: 680px; margin: 0 auto; background: #ffffff; padding: 28px; border-radius: 8px; box-shadow: 0 6px 20px rgba(23,24,28,0.06); }}
        p {{ margin: 10px 0; line-height: 1.6; color: #222; }}
        ul {{ margin: 10px 0 10px 20px; }}
        li {{ margin: 6px 0; }}
        .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
        hr.sep {{ border: none; border-top: 1px solid #e6e7ed; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        {body_html}
    </div>
    <div class="footer">
        <p>Sent by <a href="https://automailer.streamlit.app/" style="color: #2563eb; text-decoration: none;">https://automailer.streamlit.app/</a></p>
    </div>
</body>
</html>
"""
        
        # Send the reply with both text and HTML
        response = client.inboxes.messages.reply(
            inbox_id=INBOX_ID,
            message_id=message_id,
            text=reply_with_footer,
            html=html_content,
            labels=["ai-generated", "job-application"]
        )
        
        # Mark the original message as replied
        client.inboxes.messages.update(
            inbox_id=INBOX_ID,
            message_id=message_id,
            add_labels=["replied"],
            remove_labels=["unreplied"]
        )
        
        return response
    
    except Exception as e:
        print(f"Error sending reply: {e}")
        return None

def process_conversations():
    """Main function to process unread threads from givemeajob@agentmail.to"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for unread threads in {INBOX_ID}...")
    
    unreplied_messages = get_unreplied_threads()
    
    if not unreplied_messages:
        print(f"No unread threads found in {INBOX_ID}.")
        return
    
    print(f"Replying to unread thread from {INBOX_ID}")
    
    message = unreplied_messages[0]  # Just get the first (and only) message
    
    # Access message attributes directly
    sender = getattr(message, 'from_', getattr(message, 'sender', 'Unknown'))
    subject = getattr(message, 'subject', 'No Subject')
    text = getattr(message, 'text', '')
    html = getattr(message, 'html', '')
    msg_id = getattr(message, 'message_id', getattr(message, 'id', None))
    
    # Use HTML content if text is empty
    content = text if text else html
    if not content:
        print("Message has no text or HTML content")
        return
    
    print(f"\nProcessing message from {sender}")
    print(f"Subject: {subject}")
    print(f"Content type: {'Text' if text else 'HTML'}")
    print(f"Preview: {content[:100]}...")
    
    # Generate AI response
    print("Generating AI response...")
    ai_response = generate_job_application_response(content, "")
    
    # Send the reply
    print("Sending reply...")
    reply_result = send_reply(msg_id, ai_response)
    
    if reply_result:
        print(f"✅ Successfully replied to message {msg_id}")
        print(f"Reply preview: {ai_response[:100]}...")
    else:
        print(f"❌ Failed to reply to message {msg_id}")

def send_initial_job_application():
    """Send the initial job application email to hiring@agentmail.to"""
    
    initial_prompt = """
    Write an initial job application email from an enthusiastic job seeker named Alex.
    
    INSTRUCTIONS:
    - This is the first contact, so introduce yourself briefly
    - Express genuine interest in working for their company
    - Highlight key skills and experience
    - Be professional but enthusiastic
    - Ask about available opportunities
    - Keep it concise (2-3 paragraphs)
    - End with a strong call to action
    - Format properly with line breaks
    
    Generate both a subject line and email body.
    Format as:
    SUBJECT: [subject line]
    BODY: [email body starting with greeting and blank line]
    """
    
    try:
        completion = llama_client.chat.completions.create(
            model="Llama-3.3-70B-Instruct",
            messages=[
                {
                    "role": "system",
                    "content": "You are writing a compelling initial job application email."
                },
                {
                    "role": "user", 
                    "content": initial_prompt
                }
            ],
            max_tokens=600,
            temperature=0.7
        )
        
        response = completion.choices[0].message.content
        
        if "SUBJECT:" in response and "BODY:" in response:
            subject = response.split("SUBJECT:")[1].split("BODY:")[0].strip()
            body = response.split("BODY:")[1].strip()
        else:
            subject = "Enthusiastic Application - Ready to Contribute!"
            body = response
        
        # Add visible footer to email body
        footer_text = "\n\n---\nSent by https://automailer.streamlit.app/"
        body_with_footer = f"{body}{footer_text}"

        # Convert text body into HTML using helper
        body_html = _convert_text_to_html(body_with_footer)

        # Create complete HTML email structure
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-wide, initial-scale=1.0">
    <title>Job Application</title>
    <style>
        body {{ font-family: Arial, sans-serif; color: #333; background-color: #f6f7fb; margin: 0; padding: 20px; }}
        .container {{ max-width: 680px; margin: 0 auto; background: #ffffff; padding: 28px; border-radius: 8px; box-shadow: 0 6px 20px rgba(23,24,28,0.06); }}
        p {{ margin: 10px 0; line-height: 1.6; color: #222; }}
        ul {{ margin: 10px 0 10px 20px; }}
        li {{ margin: 6px 0; }}
        .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        {body_html}
    </div>
    <div class="footer">
        <p>Sent by <a href="https://automailer.streamlit.app/" style="color: #2563eb; text-decoration: none;">https://automailer.streamlit.app/</a></p>
    </div>
</body>
</html>"""
        
        # Send initial application
        result = client.inboxes.messages.send(
            inbox_id=INBOX_ID,
            to=[HIRING_EMAIL],
            subject=subject,
            text=body_with_footer,
            html=html_body,
            labels=["initial-application", "ai-generated"]
        )
        
        print(f"✅ Sent initial job application!")
        print(f"Subject: {subject}")
        print(f"Preview: {body[:150]}...")
        
        return result
        
    except Exception as e:
        print(f"Error sending initial application: {e}")
        return None

def main():
    """Main application loop"""
    print("🤖 AI Job Application Agent Starting...")
    print(f"Monitoring: {INBOX_ID}")
    print(f"Responding to: {HIRING_EMAIL}")
    print(f"Poll interval: {POLL_INTERVAL} seconds")
    print("-" * 50)
    
    # Ask if user wants to send initial application
    send_initial = input("Send initial job application? (y/n): ").lower().strip() == 'y'
    
    if send_initial:
        print("\nSending initial job application...")
        send_initial_job_application()
        print("\nWaiting 10 seconds before starting monitoring loop...")
        time.sleep(10)
    
    print("\n🔄 Starting monitoring loop...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            process_conversations()
            print(f"Sleeping for {POLL_INTERVAL} seconds...")
            time.sleep(POLL_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n🛑 Job application agent stopped by user")
    except Exception as e:
        print(f"\n❌ Error in main loop: {e}")

if __name__ == "__main__":
    main()
