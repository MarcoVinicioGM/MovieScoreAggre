from fastapi import FastAPI, HTTPException
from requests import get
import os
from datetime import datetime, timedelta

app = FastAPI()

# Simple in-memory cache
cache = {}
CACHE_DURATION = timedelta(hours=24)

@app.get("/movie/{title}")
async def get_movie_scores(title: str):
    # Check cache first
    if title in cache:
        if datetime.now() - cache[title]["timestamp"] < CACHE_DURATION:
            return cache[title]["data"]
    
    try:
        # Get OMDB data (includes IMDb rating)
        omdb_key = os.getenv("OMDB_API_KEY")
        omdb_response = get(f"http://www.omdbapi.com/?t={title}&apikey={omdb_key}")
        omdb_data = omdb_response.json()
        
        imdb_rating = float(omdb_data.get("imdbRating", 0))
        # Convert IMDb rating to percentage
        imdb_score = (imdb_rating / 10) * 100
        
        # You could add more sources here
        
        # Calculate aggregate score
        aggregate_score = {
            "title": omdb_data.get("Title"),
            "imdb_score": imdb_score,
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