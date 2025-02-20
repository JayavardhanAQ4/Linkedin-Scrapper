import os
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY", "384e79ee72a4270c97e3639131924917b7c9263f0321d62ed5130bbf66edbda9")

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL", "mkjayavardhan@gmail.com")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "Rebalprabha1")

# Input and Output File Paths
INPUT_EXCEL = "/Users/jay/Desktop/AQ4/BeautifulSoup/linkedin_scraper/Sample data - Customer tag (2).xlsx"
OUTPUT_JSON = "linkedin_profiles.json"
OUTPUT_EXCEL = "linkedin_output.xlsx"
