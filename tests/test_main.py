import pytest
from fastapi.testclient import TestClient
from aggregator.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["healthy", "unhealthy"]
    assert "dependencies" in response.json()

@pytest.mark.asyncio
async def test_get_movie_scores():
    # Testing with a well known movie 
    movie_name = "The Godfather"
    response = client.get(f"/movie/{movie_name}")
    assert response.status_code == 200
    assert "imdb_score" in response.json()
    assert "letterboxd_score" in response.json()

def test_movie_not_found():
    # Test with a movie that shouldn't exist
    response = client.get("/movie/ThisMovieDoesNotExistAtAll123456789")
    assert response.status_code == 404
