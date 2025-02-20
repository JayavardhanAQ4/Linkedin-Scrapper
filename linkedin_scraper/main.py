import pandas as pd
from search_profiles import process_profiles
from scrape_profiles import scrape_profile
from summarize_profiles import generate_summary
from config import INPUT_EXCEL, OUTPUT_EXCEL

df = pd.read_excel(INPUT_EXCEL)
profiles = process_profiles(df)
scraped_data = [scrape_profile(profile["LinkedIn_URLs"][0]) for profile in profiles]
for profile in scraped_data:
    profile["summary"] = generate_summary(profile)

output_df = pd.DataFrame(scraped_data)
output_df.to_excel(OUTPUT_EXCEL, index=False)
print("Process completed! Results saved.")
