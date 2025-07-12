from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
import asyncio
import os
import json
import pandas as pd
from datetime import datetime
from core.fetch_matches import fetch_matches
from core.utils import get_logger
from utils.user_agent_pool import get_random_user_agent

app = FastAPI(title="OddsPortal Scraper API")
logger = get_logger("api")

# CORS middleware setup
origins = [
    "https://oddsportalui-1.onrender.com",  # Correct Streamlit app URL without trailing slash
    "http://localhost",  # Local development URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow access from Streamlit app URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Store scraped data temporarily
scraped_data = []


@app.get("/health")
async def health_check():
    """Check if the API is running."""
    return {"status": "API is running"}


@app.post("/scrape")
async def scrape_matches():
    """Trigger the scraping process for all sports."""
    global scraped_data
    try:
        logger.info("[*] Starting API scrape request...")
        user_agent = get_random_user_agent()
        logger.info(f"[*] Using UA: {user_agent}")

        # Run the existing fetch_matches function
        matches = await fetch_matches(user_agent=user_agent)

        # Store results
        scraped_data = matches
        logger.info(f"[+] Scraped {len(matches)} matches")

        # Prepare response
        response = {
            "status": "success",
            "message": f"Scraped {len(matches)} matches",
            "matches": matches,
            "timestamp": datetime.now().isoformat()
        }
        return JSONResponse(content=response)
    except Exception as e:
        logger.error(f"[!] Scrape error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Scraping failed: {str(e)}")


@app.get("/matches")
async def get_matches():
    """Retrieve the most recently scraped matches."""
    global scraped_data
    if not scraped_data:
        raise HTTPException(
            status_code=404, detail="No scraped data available")

    return JSONResponse(content={
        "status": "success",
        "matches": scraped_data,
        "count": len(scraped_data),
        "timestamp": datetime.now().isoformat()
    })


@app.get("/matches/{sport}")
async def get_matches_by_sport(sport: str):
    """Retrieve scraped matches for a specific sport."""
    global scraped_data
    if not scraped_data:
        raise HTTPException(
            status_code=404, detail="No scraped data available")

    # Filter matches by sport (case-insensitive)
    filtered_matches = [match for match in scraped_data if match.get(
        "league", "").lower() == sport.lower()]

    if not filtered_matches:
        raise HTTPException(
            status_code=404, detail=f"No matches found for sport: {sport}")

    return JSONResponse(content={
        "status": "success",
        "sport": sport,
        "matches": filtered_matches,
        "count": len(filtered_matches),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
