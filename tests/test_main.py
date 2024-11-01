import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from aggregator.main import app

client = TestClient(app)

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

#Tests the movie endpoint, which makes a mock call to the Letterboxd API and OMDB API
@patch('aggregator.main.scrape_film')
@patch('requests.get')
def test_movie(mock_requests, mock_scrape):
    # Mock the letterboxd scraping
    mock_scrape.return_value = {"Average_rating": 4.31}
    
    # Mock the OMDB API response
    mock_response = mock_requests.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "Title": "The Departed",
        "Year": "2006",
        "imdbRating": "8.5",
        "Poster": "https://m.media-amazon.com/images/M/MV5BMTI1MTY2OTIxNV5BMl5BanBnXkFtZTYwNjQ4NjY3._V1_SX300.jpg"
    }

    response = client.get("/movie/The Departed")
    assert response.status_code == 200
    data = response.json()
    
    sample_data = {
        "title": "The Departed",
        "imdb_score": 85.0,
        "letterboxd_score": 4.31,
        "aggregate_score": 85.0,
        "year": "2006",
        "poster": "https://m.media-amazon.com/images/M/MV5BMTI1MTY2OTIxNV5BMl5BanBnXkFtZTYwNjQ4NjY3._V1_SX300.jpg"
    }
    
    assert data.keys() == sample_data.keys()

#Tests a fake movie to make sure that the 404 is returned correctly
def test_movie_not_found():
    response = client.get("/movie/ThisMovieDoesNotExistAtAll123456789")
    assert response.status_code == 404

#Tests the caching mechanism, which should return the same data for the same movie, uses a fake movie to test
def test_movie_cache():
    with patch('aggregator.main.scrape_film') as mock_scrape, \
         patch('requests.get') as mock_requests:
        
        mock_scrape.return_value = {"Average_rating": 4.31}
        mock_response = mock_requests.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Title": "Test Movie",
            "Year": "2023",
            "imdbRating": "8.0",
            "Poster": "poster_url"
        }
        
        # First request
        response1 = client.get("/movie/test movie")
        
        # Second request should use cache
        response2 = client.get("/movie/test movie")
        
        assert response1.json() == response2.json()
        mock_scrape.assert_called_once()  # Should only be called once due to caching