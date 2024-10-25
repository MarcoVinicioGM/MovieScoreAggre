import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from aggregator.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

def test_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_movie():
    """Test with specific sample data"""
    response = client.get("/movie/The Departed")
    data = response.json()

    sample_data = {
        "title": "The Departed",
        "imdb_score": 85.0,
        "letterboxd_score": 4.31,
        "aggregate_score": 85.0,
        "year": "2006",
        "poster": "https://m.media-amazon.com/images/M/MV5BMTI1MTY2OTIxNV5BMl5BanBnXkFtZTYwNjQ4NjY3._V1_SX300.jpg"
    }
    
    # Compare with sample data structure
    assert data.keys() == sample_data.keys()
    

def test_movie_not_found():
    response = client.get("/movie/ThisMovieDoesNotExistAtAll123456789")
    assert response.status_code == 404