import time
import json
import pandas as pd
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from config import LINKEDIN_EMAIL, LINKEDIN_PASSWORD, INPUT_EXCEL
from utils import extract_profile_name

# Selenium Chrome Driver Setup
chrome_options = Options()
chrome_options.add_argument("--headless") 
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

print("Initializing Selenium WebDriver...")
driver = uc.Chrome(options=chrome_options, use_subprocess=True)

def linkedin_login():
    """Login to LinkedIn."""
    print("Logging into LinkedIn...")
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)

    driver.find_element(By.ID, "username").send_keys(LINKEDIN_EMAIL)
    driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(5)

    if "feed" not in driver.current_url:
        print("LinkedIn login failed. Exiting script.")
        driver.quit()
        exit()
    print("Successfully logged into LinkedIn.")

def scrape_profile(url):
    """Scrape LinkedIn profile details."""
    print(f"Accessing profile: {url}")
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    profile_data = {
        "profile_url": url,
        "name": extract_profile_name(url),
        "headline": soup.find("div", class_="text-body-medium").text.strip() if soup.find("div", class_="text-body-medium") else "N/A",
        "location": soup.find("span", class_="text-body-small").text.strip() if soup.find("span", class_="text-body-small") else "N/A",
    }

    print(f"Scraped profile: {profile_data['name']}, Headline: {profile_data['headline']}, Location: {profile_data['location']}")
    return profile_data

if __name__ == "__main__":
    linkedin_login()

    print("Loading LinkedIn URLs from 'best_search_results.xlsx'...")
    df = pd.read_excel("best_search_results.xlsx")
    df = df.dropna(subset=["LinkedIn_URL"])  # Remove rows without LinkedIn URLs

    print(f"Found {len(df)} profiles to scrape.")

    results = []
    for index, row in df.iterrows():
        profile_url = row["LinkedIn_URL"]
        if profile_url and isinstance(profile_url, str):
            print(f"Scraping profile {index + 1}/{len(df)}")
            profile_data = scrape_profile(profile_url)
            results.append(profile_data)

    # Saved the scraped results to json
    with open("scraped_profiles.json", "w") as f:
        json.dump(results, f, indent=4)

    print("Profile scraping completed! Results saved to 'scraped_profiles.json'.")
    driver.quit()
    print("WebDriver closed. Script execution finished.")
