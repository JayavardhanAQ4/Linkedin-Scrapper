from fastapi import APIRouter, HTTPException
from scrape_profiles import scrape_profile

router = APIRouter(prefix="/scrape", tags=["Scrape"])

@router.get("/")
def scrape_profile(linkedin_url: str):
    profile_data = scrape_profile(linkedin_url)

    if not profile_data:
        raise HTTPException(status_code=404, detail="Failed to scrape profile")
    
    return profile_data
