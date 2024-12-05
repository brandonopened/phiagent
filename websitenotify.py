from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.googlesearch import GoogleSearch
from phi.tools.email import EmailTools
import hashlib
import os
import json

# Configuration
receiver_email = "brandon.dorman@gmail.com"
sender_email = "<sender_email>"
sender_name = "<sender_name>"
sender_passkey = "<sender_passkey>"
tracking_file = "website_tracking.json"

# Utility functions
def hash_content(content):
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def load_tracking_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return {}

def save_tracking_data(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file)

# Define the agent
website_monitor_agent = Agent(
    name="Website Monitor Agent",
    role="Monitor websites for changes and notify the user via email",
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        GoogleSearch(),
        EmailTools(
            receiver_email=receiver_email,
            sender_email=sender_email,
            sender_name=sender_name,
            sender_passkey=sender_passkey,
        ),
    ],
    instructions=[
        "Scan a list of websites provided by the user.",
        "Detect changes since the last scan by comparing website content hashes.",
        "Log changes and notify the user via email."
    ],
    show_tool_calls=True,
    markdown=True,
    debug_mode=True,
)

# Function to monitor websites
def monitor_websites(websites):
    changes_detected = []
    tracking_data = load_tracking_data(tracking_file)

    for site in websites:
        try:
            response = website_monitor_agent.tools[0].search(query=f"site:{site}")
            if response:
                content_hash = hash_content(response[0]["snippet"])
                if site in tracking_data:
                    if tracking_data[site] != content_hash:
                        changes_detected.append(site)
                tracking_data[site] = content_hash
        except Exception as e:
            print(f"Error monitoring {site}: {e}")

    save_tracking_data(tracking_file, tracking_data)
    return changes_detected

# Function to send email notification
def notify_user(changes):
    if not changes:
        print("No changes detected.")
        return

    changes_list = "\n".join(changes)
    email_subject = "Website Changes Detected"
    email_body = f"The following websites have changed since the last scan:\n\n{changes_list}"
    
    email_tool = website_monitor_agent.tools[1]
    email_tool.send_email(
        subject=email_subject,
        body=email_body
    )

# List of websites to monitor
websites_to_monitor = [
    "example.com",
    "news.example.com",
    "blog.example.com",
]

# Monitor websites and notify user
changes = monitor_websites(websites_to_monitor)
notify_user(changes)
