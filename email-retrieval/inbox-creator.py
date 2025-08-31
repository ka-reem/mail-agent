# Create a list of inboxes with custom names
from agentmail import AgentMail
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the client with API key from environment
api_key = os.getenv('AGENTMAIL_API_KEY')
if not api_key:
    print("❌ Error: AGENTMAIL_API_KEY not found in environment variables")
    print("Please add AGENTMAIL_API_KEY=your_key_here to your .env file")
    exit(1)

client = AgentMail(api_key=api_key)

# List of custom inbox names to create (unique variations)
inbox_names = [
    "infobox",
    "supportdesk",
    "salesteam",
    "contactus",
    "helpdesk",
    "adminpanel",
    "noreplies",
    "billpay",
    "promo",
    "orders",
    "returns",
    "newsletter",
    "alerts",
    "updates",
    "careers",
    "press",
    "events",
    "partners",
    "privacy",
    "accounts",
    "customerservice",
    "technicalsupport",
    "webmaster",
]

print("Creating custom inboxes...")

for name in inbox_names:
    try:
        # Try to create inbox with custom username (this creates name@agentmail.to)
        try:
            new_inbox = client.inboxes.create(username=name)
            print(f"Created Inbox: {name}@agentmail.to")
        except Exception as e:
            # If username is taken or invalid, fall back to random email with display name
            error_msg = str(e).lower()
            if "already exists" in error_msg or "taken" in error_msg or "unavailable" in error_msg:
                print(f" Username '{name}' is already taken, creating with random email...")
            else:
                print(f" Couldn't use username '{name}': {e}")
            
            # Fallback: create with random email but set display name
            #no
            # new_inbox = client.inboxes.create(display_name=name)
            # print(f"Created Inbox: {new_inbox.inbox_id} (display name: '{name}')")
            
    except Exception as e:
        print(f"❌ Failed to create inbox '{name}': {e}")

print(f"\nFinished creating {len(inbox_names)} inboxes!")