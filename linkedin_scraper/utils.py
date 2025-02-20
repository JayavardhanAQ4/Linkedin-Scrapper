from fuzzywuzzy import fuzz

def generate_search_query(first_name, last_name, company_name):
    """Generate a LinkedIn search query."""
    return f"{first_name} {last_name} {company_name} site:linkedin.com" if company_name else f"{first_name} {last_name} site:linkedin.com"

def extract_profile_name(url):
    """Extract the profile name from a LinkedIn URL."""
    parts = url.rstrip("/").split("/")
    return parts[4].replace("-", " ") if len(parts) > 4 else "Unknown"

def fuzzy_match(name1, name2):
    """Calculate similarity between two names using fuzzy matching."""
    return fuzz.token_sort_ratio(name1.lower(), name2.lower())
