import time
import logging
import pandas as pd
from serpapi import GoogleSearch
from fuzzywuzzy import fuzz
from config import SERPAPI_KEY, INPUT_EXCEL
from utils import generate_search_query, extract_profile_name

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s") #this line of code sets up a "diary" for program, where it records important events with the date, time, and a description. This helps understand what program is doing and find any problems that might occur.

def fetch_linkedin_urls(query, max_results=3, retries=3):
    """Fetch potential LinkedIn profile URLs using Google Search via SerpAPI."""
    urls = []
    for attempt in range(retries):
        try:
            params = {"engine": "google", "q": query, "num": 10, "api_key": SERPAPI_KEY}
            search = GoogleSearch(params)
            results = search.get_dict()

            for result in results.get("organic_results", []):
                link = result.get("link", "")
                if "linkedin.com/in/" in link or "linkedin.com/pub/" in link:
                    urls.append(link)

            if urls:
                logging.info(f"Found {len(urls)} LinkedIn profiles for query: '{query}'")
            else:
                logging.warning(f" No LinkedIn profiles found for query: '{query}'")
                
            return urls[:max_results]

        except Exception as e:
            logging.error(f"Error fetching results (Attempt {attempt + 1}): {e}")
            time.sleep(5)
    return urls

def fuzzy_match(name1, name2):
    """Calculate similarity between two names using fuzzy matching."""
    return fuzz.token_sort_ratio(name1.lower(), name2.lower())

def select_best_profile(profiles, first_name, last_name):
    """Choose the best LinkedIn profile URL based on fuzzy matching."""
    best_match = None
    best_score = 0

    full_name = f"{first_name} {last_name}"

    for profile_url in profiles:
        profile_name = extract_profile_name(profile_url)
        score = fuzzy_match(full_name, profile_name)

        if score > best_score:
            best_score = score
            best_match = profile_url

    logging.info(f"Best Match: {best_match} (Confidence: {best_score}%)")
    return best_match if best_score > 75 else None  # Only return if confidence > 75%

def process_profiles(df):
    """Generate the best LinkedIn profile URL for each person in the input file."""
    results = []
    for _, row in df.iterrows():
        first_name, last_name = row["First_Name"], row["Last_Name"]
        company_name = row["Company_name"] if pd.notna(row["Company_name"]) else None

        # If company name is missing, search only with First Name & Last Name
        query = generate_search_query(first_name, last_name, company_name if company_name else None) 

        urls = fetch_linkedin_urls(query)
        best_profile = select_best_profile(urls, first_name, last_name) if urls else None
        
        results.append({
            "First_Name": first_name,
            "Last_Name": last_name,
            "Company_name": company_name if company_name else "N/A",  # Store "N/A" if missing
            "LinkedIn_URL": best_profile
        })
    
    return results

if __name__ == "__main__":
    df = pd.read_excel(INPUT_EXCEL)
    profiles = process_profiles(df)
    pd.DataFrame(profiles).to_excel("best_search_results.xlsx", index=False)

    logging.info("Process completed. Best LinkedIn profiles saved to 'best_search_results.xlsx'.")
