import pandas as pd
from fastapi import UploadFile, HTTPException
from io import BytesIO
from search_profiles import fetch_linkedin_urls
from scrape_profiles import scrape_profile
from summarize_profiles import generate_summary  # Llama 3.2
from utils import extract_profile_name, fuzzy_match
import logging

async def process_file(file: UploadFile):
    # Step 1: Read File
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents), sheet_name="Customer Data")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid File Format: {e}")

    # Step 2: Validate Mandatory Fields
    mandatory_fields = ["First Name", "Last Name", "Company Name"]
    missing_rows = df[df[mandatory_fields].isnull().any(axis=1)]
    df = df.dropna(subset=mandatory_fields)

    # Step 3: Generate LinkedIn URLs
    df["Find LinkedIN URL"] = df.apply(lambda row: fetch_linkedin_urls(f"{row['First Name']} {row['Last Name']} {row['Company Name']}"), axis=1)

    # Step 4: Subset DF A (with URL) & DF B (without URL)
    df_a = df.dropna(subset=["Find LinkedIN URL"])
    df_b = df[df["Find LinkedIN URL"].isna()]

    # Step 5: Scrape Existing LinkedIn Profiles
    df_a["Profile Data"] = df_a["Find LinkedIN URL"].apply(lambda url: scrape_profile(url) if pd.notna(url) else None)

    # Step 6: Identify Missing Fields → DF C
    df_c = df_a[df_a.isnull().any(axis=1)]

    # Step 7: Use Llama 3.2 to Fill Missing Data → DF D
    df_d = generate_summary(df_b, df_c)

    # Step 8: Merge Processed Data → Final DF
    final_df = pd.concat([df_a, df_d])

    # Step 9: Extract Tokens
    final_df["Extracted Tokens"] = final_df.apply(lambda row: extract_profile_name(row["Find LinkedIN URL"]), axis=1)

    # Step 10: Predict Column Tags → DF RESULT
    final_df["Predicted Tags"] = final_df.apply(lambda row: fuzzy_match(row["Extracted Tokens"], row["Company Name"]), axis=1)

    # Step 11: Return Results
    output_file = BytesIO()
    final_df.to_excel(output_file, index=False)
    output_file.seek(0)
    
    return {
        "message": "Processing Completed",
        "missing_rows": missing_rows.to_dict(orient="records"),
        "download_url": "/download/output.xlsx"
    }
