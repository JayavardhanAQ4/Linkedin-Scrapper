from fastapi import APIRouter, HTTPException
from summarize_profiles import generate_summary

router = APIRouter(prefix="/summarize", tags=["Summarization"])

@router.post("/")
def summarize_profile(profile: dict):
    summary = generate_summary(profile)

    if not summary:
        raise HTTPException(status_code=500, detail="Failed to generate summary")
    
    return {"summary": summary}
