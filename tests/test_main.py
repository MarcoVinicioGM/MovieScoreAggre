import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from aggregator.main import app
import os
import logging

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create test client
client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_env_variables():
    """Fixture to set up environment variables for all tests"""
    with patch.dict(os.environ, {
        'OMDB_API_KEY': 'fake_key',
        'PORT': '8000'
    }):
        yield

#Obviously reads the root
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

#Obviously reads the health, however I had to make sure it mocks the API check otherwise it would not be
#a real unit test as the network call could fail or the API could be down
@patch('aggregator.main.check_imdb_api')
def test_health(mock_check_imdb):
    mock_check_imdb.return_value = True  # Mock the API check to return True
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["dependencies"]["imdb_api"] == True

#Tests a fake movie to make sure that the 404 is returned correctly
@patch('aggregator.main.scrape_film')
@patch('requests.get')
def test_movie_not_found(mock_requests, mock_scrape):
    # Mock OMDB API response for non-existent movie
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "Response": "False",
        "Error": "Movie not found!"
    }
    mock_requests.return_value = mock_response
    
    response = client.get("/movie/ThisMovieDoesNotExistAtAll123456789")
    assert response.status_code == 404

@patch('aggregator.main.check_imdb_api')
def test_health_check_api_down(mock_check_imdb):
    mock_check_imdb.return_value = False
    response = client.get("/health")
    assert response.status_code == 503
    data = response.json()
    assert data["detail"]["status"] == "unhealthy"
    assert data["detail"]["dependencies"]["imdb_api"] == False

def test_invalid_api_key():
    with patch.dict(os.environ, {'OMDB_API_KEY': ''}):
        response = client.get("/movie/The%20Godfather")
        assert response.status_code == 500

        assert response.json()["detail"] == "OMDB API key not configured"

#Was continually running into issues where Live API calls were failing in build but passing locally and thus should have passed on build
#External apis are not supposed to be called and instead mocked but since this isn't a real service I wanted to do live calls
#Also truthfully I couldn't get the mocking to work so had to do live calls.
def test_postman_equivalent():
    """Test to mimic successful Postman request"""
    with patch.dict(os.environ, {'OMDB_API_KEY': '59dcd1b8'}):  # Use your actual test API key
        try:
            response = client.get("/movie/The%20Godfather", 
                                headers={"Content-Type": "application/json"})
            logger.debug(f"Postman test response status: {response.status_code}")
            logger.debug(f"Postman test response body: {response.json() if response.status_code == 200 else response.text}")
            
            assert response.status_code == 200
            data = response.json()
            assert "title" in data
            assert "year" in data
            assert "imdb_score" in data
            assert "letterboxd_score" in data
        except Exception as e:
            logger.error(f"Postman test failed with error: {str(e)}")
            raise
#Verifies that all the current routes are registered
def test_verify_routes():
    """Verify that all expected routes are registered"""
    routes = [route.path for route in app.routes]
    logger.debug(f"Registered routes: {routes}")
    
    assert "/" in routes
    assert "/movie/{title}" in routes
    assert "/health" in routes

