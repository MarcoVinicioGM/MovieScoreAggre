# tests/test_integration.py (with real API calls)
import pytest
import os
import warnings
from fastapi.testclient import TestClient
from aggregator.main import app



client = TestClient(app)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="bs4.builder._lxml")



def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Marco's movie score aggregator!"}


@pytest.mark.skipif(not os.getenv("OMDB_API_KEY"), reason="OMDB API key not found")
def test_health_check_integration():
    response = client.get("/health")
    assert response.status_code == 200
    health_data = response.json()
    assert health_data["status"] == "healthy"
    assert health_data["dependencies"]["imdb_api"] == True  # Verify API is actually working


@pytest.mark.skipif(not os.getenv("OMDB_API_KEY"), reason="OMDB API key not found")
def test_get_movie_scores_integration():
    # Test successful movie lookup
    response = client.get("/movie/The%20Godfather")
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    data = response.json()
    print(f"Response data: {data}")  # Debug print
    assert "title" in data, "Title not found in response"
    assert "imdb_score" in data, "IMDB score not found in response"
    assert "letterboxd_score" in data, "Letterboxd score not found in response"
    assert "aggregate_score" in data, "Aggregate score not found in response"
    assert "year" in data, "Year not found in response"
    assert "poster" in data, "Poster not found in response"
    
    # Test movie not found
    response = client.get("/movie/ThisMovieDefinitelyDoesNotExist12345")
    assert response.status_code == 404, f"Expected status code 404, but got {response.status_code}"
    
    # Test rate limiting and caching
    movie_title = "Inception"
    for i in range(3):
        response = client.get(f"/movie/{movie_title}")
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code} on iteration {i+1}"
        print(f"Response {i+1} for {movie_title}: {response.json()}")  # Debug print
    
@pytest.mark.skipif(not os.getenv("OMDB_API_KEY"), reason="OMDB API key not found")
def test_get_movie_scores_integration():
    response = client.get("/movie/The%20Godfather")
    assert response.status_code == 200
    data = response.json()
    assert data["imdb_score"] > 0
    assert data["letterboxd_score"] > 0
    
    # Test rate limits and API key validity
    for _ in range(3):  # Make a few requests to check rate limits
        response = client.get("/movie/Inception")
        assert response.status_code == 200