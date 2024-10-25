from fastapi import FastAPI, HTTPException
from requests import get
import os
import httpx
from datetime import datetime, timedelta
from scrapers.LetterBoxd.scrape_functions import scrape_film

app = FastAPI()
# Simple in-memory cache
cache = {}
CACHE_DURATION = timedelta(hours=24)

class MovieNotFoundException(Exception):
    """Custom exception for when a movie is not found"""
    pass

async def check_imdb_api() -> bool:
    try:
        async with httpx.AsyncClient() as client:
            omdb_key = os.getenv("OMDB_API_KEY")
            response = await client.get(f"http://www.omdbapi.com/?i=tt3896198&apikey={omdb_key}")
            return response.status_code == 200
    except:
        return False

@app.get("/health")
async def health_check() -> dict:
    health_data = {
        "status": "healthy",
        "api_version": "1.0.0",
        "dependencies": {
            "imdb_api": await check_imdb_api(),
            "letterboxd_scraping": True
        }
    }
    
    if not all(health_data["dependencies"].values()):
        health_data["status"] = "unhealthy"
        raise HTTPException(status_code=503, detail=health_data)
        
    return health_data

@app.get("/movie/{title}")
async def get_movie_scores(title: str):
    try:
        # Check cache first
        if title in cache:
            if datetime.now() - cache[title]["timestamp"] < CACHE_DURATION:
                return cache[title]["data"]
        
        title = title.lower()
        # First try to get Letterboxd data
        letterboxd_data = scrape_film(title,'.json')
        if letterboxd_data is None:
            raise MovieNotFoundException(f"Movie '{title}' not found on Letterboxd")

        # Get OMDB data
        omdb_key = os.getenv("OMDB_API_KEY")
        if not omdb_key:
            raise HTTPException(status_code=500, detail="OMDB API key not configured")

        omdb_response = get(f"http://www.omdbapi.com/?t={title}&apikey={omdb_key}")
        omdb_data = omdb_response.json()
        
        # Check for OMDB errors
        if "Error" in omdb_data or omdb_response.status_code != 200:
            raise MovieNotFoundException(f"Movie '{title}' not found on IMDB")

        # Get IMDb rating
        imdb_rating = omdb_data.get("imdbRating")
        if not imdb_rating or imdb_rating == "N/A":
            imdb_score = 0
        else:
            imdb_score = (float(imdb_rating) / 10) * 100

        letterboxd_score = letterboxd_data.get("Average_rating")
        
        aggregate_score = {
            "title": omdb_data.get("Title"),
            "imdb_score": imdb_score,
            "letterboxd_score": letterboxd_score,
            "aggregate_score": imdb_score,
            "year": omdb_data.get("Year"),
            "poster": omdb_data.get("Poster")
        }
        
        # Cache the result
        cache[title] = {
            "timestamp": datetime.now(),
            "data": aggregate_score
        }
        
        return aggregate_score
        
    except MovieNotFoundException as e:
        # Explicitly handle 404 cases
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException as e:
        # Re-raise existing HTTP exceptions with their original status codes
        raise
    except Exception as e:
        # Log the unexpected error for debugging
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Welcome to Marco's movie score aggregator!"}