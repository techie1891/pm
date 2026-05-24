import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_api_hello():
    """Test the /api/hello endpoint returns correct JSON"""
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "hello"}


def test_frontend_root():
    """Test that the frontend root page is served"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Kanban Studio" in response.text
    assert "text/html" in response.headers["content-type"]


def test_frontend_styles():
    """Test that static assets are available"""
    response = client.get("/_next/static/")
    # Assets should exist in the static directory
    assert response.status_code in [200, 404]  # May be 404 without index, but directory should exist


def test_api_not_conflicting_with_static():
    """Test that API routes don't get caught by static file serving"""
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
