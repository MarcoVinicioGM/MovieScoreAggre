# tests/test_integration.py (with real API calls)
import pytest
import os
import warnings
from fastapi.testclient import TestClient
from aggregator.main import app



client = TestClient(app)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="bs4.builder._lxml")


#Can only use non scored data as the rating is continually being updated
#Seperated from other tests as it makes live calls to the API
@pytest.mark.skipif(not os.getenv("OMDB_API_KEY"), reason="OMDB API key not found")
def test_get_movie_scores_success():
    # Test successful movie lookup with real API
    response = client.get("/movie/The%20Godfather")
    assert response.status_code == 200
    data = response.json()
    
    # Verify all required fields are present and valid
    assert data["title"] == "The Godfather", "Title mismatch"
    assert data["year"] == "1972", "Year mismatch"
    assert data["poster"].startswith("https://"), "Poster URL should start with https://"