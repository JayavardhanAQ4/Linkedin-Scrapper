from fastapi import APIRouter, HTTPException
from linkedin_scraper.search_profiles import fetch_linkedin_urls

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/{first_name}/{last_name}")
def search_profiles(first_name: str, last_name: str, company: str = None):
    query = f"{first_name} {last_name} LinkedIn {company if company else ''}"
    urls = fetch_linkedin_urls(query)

    if not urls:
        raise HTTPException(status_code=404, detail="No LinkedIn profiles found")
    
    return {"profiles": urls}
