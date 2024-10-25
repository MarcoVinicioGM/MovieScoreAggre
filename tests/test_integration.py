# tests/test_integration.py (with real API calls)
import pytest
import os
from fastapi.testclient import TestClient
from aggregator.main import app

client = TestClient(app)

@pytest.mark.skipif(not os.getenv("OMDB_API_KEY"), reason="OMDB API key not found")
def test_health_check_integration():
    response = client.get("/health")
    assert response.status_code == 200
    health_data = response.json()
    assert health_data["status"] == "healthy"
    assert health_data["dependencies"]["imdb_api"] == True  # Verify API is actually working

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