from fastapi import FastAPI, HTTPException
from requests import get
import os
import httpx
from datetime import datetime, timedelta
from scrapers.LetterBoxd.Letterboxdscraper.listscraper.scrape_functions import scrape_film


app = FastAPI()

# Simple in-memory cache
cache = {}
CACHE_DURATION = timedelta(hours=24)


async def check_imdb_api() -> bool:
    try:
        # Replace this URL with your actual IMDB API endpoint for a basic check
        async with httpx.AsyncClient() as client:
            omdb_key = os.getenv("OMDB_API_KEY")
            response = await client.get(f"http://www.omdbapi.com/?i=tt3896198&apikey={omdb_key}")
            return response.status_code == 200
    except:
        return False

@app.get("/health")
async def health_check() -> dict:
    # Basic application health metrics
    health_data = {
        "status": "healthy",
        "api_version": "1.0.0",
        "dependencies": {
            "imdb_api": await check_imdb_api(),
            "letterboxd_scraping": True  # Since this is local scraping, we'll assume it's always available
        }
    }
    
    # If any critical dependency is down, return unhealthy status
    if not all(health_data["dependencies"].values()):
        health_data["status"] = "unhealthy"
        raise HTTPException(status_code=503, detail=health_data)
        
    return health_data

@app.get("/movie/{title}")
async def get_movie_scores(title: str):
    # Check cache first
    if title in cache:
        if datetime.now() - cache[title]["timestamp"] < CACHE_DURATION:
            return cache[title]["data"]
    
    try:
        title = title.lower()
        letterboxd_data = scrape_film(title,'.json')
        # Get OMDB data (includes IMDb rating)
        omdb_key = os.getenv("OMDB_API_KEY")
        omdb_response = get(f"http://www.omdbapi.com/?t={title}&apikey={omdb_key}")
        omdb_data = omdb_response.json()
        
        imdb_rating = float(omdb_data.get("imdbRating", 0))
        # Convert IMDb rating to percentage
        imdb_score = (imdb_rating / 10) * 100
        
        letterboxd_score = letterboxd_data.get("Average_rating")
        print(letterboxd_score)

        # Calculate aggregate score
        aggregate_score = {
            "title": omdb_data.get("Title"),
            "imdb_score": imdb_score,
            "letterboxd_score": letterboxd_score,
            "aggregate_score": imdb_score,  # For now just IMDb, but you can add more
            "year": omdb_data.get("Year"),
            "poster": omdb_data.get("Poster")
        }
        
        # Cache the result
        cache[title] = {
            "timestamp": datetime.now(),
            "data": aggregate_score
        }
        
        return aggregate_score
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/")
async def root():
    return {"message": "Welcome to Marco's movie score aggregator!"}