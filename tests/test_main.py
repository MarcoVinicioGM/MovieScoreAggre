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

def test_movie_not_found():
    response = client.get("/movie/ThisMovieDoesNotExistAtAll123456789")
    assert response.status_code == 404