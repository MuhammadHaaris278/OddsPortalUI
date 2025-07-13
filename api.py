from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
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

# Store scraped data temporarily
scraped_data = []
scraping_status = {"is_running": False, "progress": "", "start_time": None}


@app.get("/health")
async def health_check():
    """Check if the API is running."""
    return {"status": "API is running"}


@app.get("/status")
async def get_status():
    """Get current scraping status."""
    return {
        "is_running": scraping_status["is_running"],
        "progress": scraping_status["progress"],
        "start_time": scraping_status["start_time"],
        "matches_found": len(scraped_data)
    }


async def run_scraping_process():
    """Background function to run the scraping process."""
    global scraped_data, scraping_status
    
    try:
        scraping_status["is_running"] = True
        scraping_status["start_time"] = datetime.now().isoformat()
        scraping_status["progress"] = "Starting scraping process..."
        
        logger.info("[*] Starting API scrape request...")
        user_agent = get_random_user_agent()
        logger.info(f"[*] Using UA: {user_agent}")
        
        scraping_status["progress"] = "Fetching matches from all sources..."
        
        # Run the existing fetch_matches function
        matches = await fetch_matches(user_agent=user_agent)
        
        # Store results
        scraped_data = matches
        logger.info(f"[+] Scraped {len(matches)} matches")
        
        scraping_status["progress"] = f"Completed! Found {len(matches)} matches"
        scraping_status["is_running"] = False
        
    except Exception as e:
        logger.error(f"[!] Scrape error: {str(e)}")
        scraping_status["progress"] = f"Error: {str(e)}"
        scraping_status["is_running"] = False
        scraped_data = []


@app.post("/scrape")
async def scrape_matches(background_tasks: BackgroundTasks):
    """Trigger the scraping process for all sports."""
    global scraping_status
    
    if scraping_status["is_running"]:
        return JSONResponse(content={
            "status": "already_running",
            "message": "Scraping is already in progress",
            "progress": scraping_status["progress"],
            "start_time": scraping_status["start_time"]
        })
    
    # Start scraping in background
    background_tasks.add_task(run_scraping_process)
    
    return JSONResponse(content={
        "status": "started",
        "message": "Scraping started in background. Use /status to check progress.",
        "timestamp": datetime.now().isoformat()
    })


@app.post("/scrape-sync")
async def scrape_matches_sync():
    """Trigger the scraping process synchronously (will wait for completion)."""
    global scraped_data, scraping_status
    
    if scraping_status["is_running"]:
        raise HTTPException(
            status_code=409, 
            detail="Scraping is already in progress"
        )
    
    try:
        scraping_status["is_running"] = True
        scraping_status["start_time"] = datetime.now().isoformat()
        scraping_status["progress"] = "Starting synchronous scraping..."
        
        logger.info("[*] Starting synchronous API scrape request...")
        user_agent = get_random_user_agent()
        logger.info(f"[*] Using UA: {user_agent}")

        # Run the existing fetch_matches function
        matches = await fetch_matches(user_agent=user_agent)

        # Store results
        scraped_data = matches
        logger.info(f"[+] Scraped {len(matches)} matches")

        scraping_status["progress"] = f"Completed! Found {len(matches)} matches"
        scraping_status["is_running"] = False

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
        scraping_status["progress"] = f"Error: {str(e)}"
        scraping_status["is_running"] = False
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
