from fastapi import FastAPI, UploadFile, File
from routes import search, scrape, summarize
from routes.process import process_file
app = FastAPI(
    title="LinkedIn Scraper API",
    description="An API for Searching, Scraping & Summarizing LinkedIn Profiles",
    version="1.0"
)

# Include Routes
app.include_router(search.router)
app.include_router(scrape.router)
app.include_router(summarize.router)

@app.get("/")
def home():
    return {"message": "Linkedin Profile Scrapper API"}

@app.post("/process")
async def process_endpoint(file: UploadFile = File(...)):
    return await process_file(file)

