"""
Tests for main application endpoints
"""
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "0.2.0"}
