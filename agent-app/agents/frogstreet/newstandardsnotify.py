import hashlib
from phi.agent import Agent
from phi.tools.website import WebsiteTools
from bs4 import BeautifulSoup
from phi.tools.email import send_email

agent = Agent(
    name="website-scanner",
    description="Scans websites for updates and sends email notifications."
)

# Initialize WebsiteTools
website_tools = WebsiteTools()

def get_text_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()

def extract_text_from_html(html_content: str) -> str:
    soup = BeautifulSoup(html_content, 'html.parser')
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    # Get text
    text = soup.get_text()
    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = ' '.join(chunk for chunk in chunks if chunk)
    return text

@agent.run
async def run_agent(
        websites: list = [
            "https://www.fldoe.org/schools/early-learning/providers/dev-standards.stml",
            "https://www.fibonacciskills.com"  # Added your website
        ],
        email_recipient: str = "bdorman@frogstreet.com", 
        check_interval: int = 24 * 60 * 60,  # Check every 24 hours
        hash_file: str = "website_hashes.txt" 
    ) -> str:
    """
    This agent scans a list of websites for updates and sends 
    email notifications if changes are detected.
    """
    try:
        # Load existing hashes
        try:
            with open(hash_file, "r") as f:
                hash_data = f.read().splitlines()
                old_hashes = {line.split(" ")[0]: line.split(" ")[1] for line in hash_data}
        except FileNotFoundError:
            old_hashes = {}

        updated_websites = []
        new_hashes = {}

        for website in websites:
            # 1. Fetch the webpage content using WebsiteTools
            page_content = await website_tools.browse(website)

            # 2. Extract text from the webpage
            extracted_text = extract_text_from_html(page_content)

            # 3. Calculate hash of the extracted text
            new_hash = get_text_hash(extracted_text)
            new_hashes[website] = new_hash  # Store for later saving

            # 4. Compare with the stored hash
            old_hash = old_hashes.get(website)
            if new_hash != old_hash:
                updated_websites.append(website)

        # 5. Send email notification if any websites have changed
        if updated_websites:
            body = "Changes detected in the following websites:\n\n" + "\n".join(updated_websites)
            send_email(
                to=email_recipient,
                subject="Website Updates!",
                body=body
            )

        # 6. Update the stored hashes
        with open(hash_file, "w") as f:
            for website, new_hash in new_hashes.items():
                f.write(f"{website} {new_hash}\n")

        if updated_websites:
            return "Websites updated and email sent."
        else:
            return "No changes detected in the websites."

    except Exception as e:
        return f"An error occurred: {e}"