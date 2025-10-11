"""
Tests for main application endpoints
"""
from app.main import app
from fastapi.testclient import TestClient
import os

# Configure database to use localhost for tests (must be set before importing app)
os.environ["POSTGRES_HOST"] = "localhost"


client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_available_codes():
    """Test getting available legal codes from the database"""
    response = client.get("/legal-texts/gesetze-im-internet/codes")
    assert response.status_code == 200
    data = response.json()
    assert "codes" in data
    assert isinstance(data["codes"], list)
