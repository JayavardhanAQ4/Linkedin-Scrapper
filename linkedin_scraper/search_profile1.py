import time
import logging
import pandas as pd
import requests  # Use requests to interact with Ollama API
from serpapi import GoogleSearch
from fuzzywuzzy import fuzz
from config import SERPAPI_KEY, INPUT_EXCEL
from utils import generate_search_query, extract_profile_name

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ollama Local API Endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"

def query_llama(prompt):
    """Send a prompt to Llama 3.2 running on Ollama and return the response."""
    try:
        response = requests.post(OLLAMA_URL, json={"model": "llama3.2", "prompt": prompt})
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        logging.error(f"❌ Llama API Error: {e}")
        return None

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
                logging.info(f"✅ Found {len(urls)} LinkedIn profiles for query: '{query}'")
            else:
                logging.warning(f"⚠️ No LinkedIn profiles found for query: '{query}'")

            return urls[:max_results]

        except Exception as e:
            logging.error(f"❌ Error fetching results (Attempt {attempt + 1}): {e}")
            time.sleep(5)
    return urls

def fuzzy_match(name1, name2):
    """Calculate similarity between two names using fuzzy matching."""
    return fuzz.token_sort_ratio(name1.lower(), name2.lower())

def infer_company_name(first_name, last_name):
    """Use Llama 3.2 (via Ollama) to predict the company name of a person."""
    prompt = f"""
    I am searching for the company where {first_name} {last_name} currently works. 
    Please provide the best possible company name based on industry trends and public knowledge.
    """
    return query_llama(prompt)

def select_best_profile(profiles, first_name, last_name, company_name=None):
    """Use Llama 3.2 + fuzzy matching to select the best LinkedIn profile."""
    if not profiles:
        return None

    full_name = f"{first_name} {last_name}"

    # Construct Llama prompt
    prompt = f"""
    I found these LinkedIn profiles for {first_name} {last_name}:
    {profiles}

    Given that they work at {company_name if company_name else 'an unknown company'}, 
    which LinkedIn profile is the most relevant? Provide the exact URL.
    """
    
    llm_choice = query_llama(prompt)

    # Verify the LLM selection with fuzzy matching
    best_match = None
    best_score = 0

    for profile_url in profiles:
        profile_name = extract_profile_name(profile_url)
        score = fuzzy_match(full_name, profile_name)

        if profile_url == llm_choice or score > best_score:
            best_score = score
            best_match = profile_url

    logging.info(f"🏆 Best Match: {best_match} (Confidence: {best_score}%)")
    return best_match if best_score > 75 else None

def process_profiles(df):
    """Generate the best LinkedIn profile URL for each person in the input file."""
    results = []
    for _, row in df.iterrows():
        first_name, last_name = row["First_Name"], row["Last_Name"]
        company_name = row["Company_name"] if pd.notna(row["Company_name"]) else None

        # If company name is missing, infer it using Llama
        if not company_name:
            company_name = infer_company_name(first_name, last_name)

        query = generate_search_query(first_name, last_name, company_name)
        urls = fetch_linkedin_urls(query)
        best_profile = select_best_profile(urls, first_name, last_name, company_name) if urls else None

        results.append({
            "First_Name": first_name,
            "Last_Name": last_name,
            "Company_name": company_name if company_name else "N/A",
            "LinkedIn_URL": best_profile
        })

    return results

if __name__ == "__main__":
    df = pd.read_excel(INPUT_EXCEL)
    profiles = process_profiles(df)
    pd.DataFrame(profiles).to_excel("best_search_results.xlsx", index=False)

    logging.info("✅ Process completed. Best LinkedIn profiles saved to 'best_search_results.xlsx'.")
