"""test_api.py — FastAPI endpoint tests (dev/mock mode, no API key required)."""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from api import app
    return TestClient(app)


VALID_PAYLOAD = {
    "product_name": "Air Max 90",
    "brand_name": "Nike",
    "product_description": "Classic running shoes with Air cushioning technology",
    "industry": "Fitness",
    "platform": "Instagram",
    "tone": "Bold",
    "visual_style": "Modern Minimal",
    "principle": "Simple",
}


def test_health_endpoint(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "api_key_configured" in data
    assert "dev_mode" in data


def test_api_info_endpoint(client):
    r = client.get("/api-info")
    assert r.status_code == 200
    data = r.json()
    assert "industries" in data
    assert len(data["industries"]) > 0
    assert "platforms" in data
    assert "tones" in data


def test_generate_ad_returns_valid_response(client):
    r = client.post("/generate_ad", json=VALID_PAYLOAD, timeout=60)
    assert r.status_code == 200
    data = r.json()
    assert "headline" in data
    assert "subheadline" in data
    assert "cta" in data
    assert "image_url" in data
    assert len(data["headline"]) > 0


def test_generate_ad_validates_required_fields(client):
    r = client.post("/generate_ad", json={**VALID_PAYLOAD, "product_name": ""})
    assert r.status_code == 422


def test_generate_ad_validates_brand_name(client):
    r = client.post("/generate_ad", json={**VALID_PAYLOAD, "brand_name": "   "})
    assert r.status_code == 422


def test_submit_feedback(client):
    r = client.post("/submit_feedback", json={
        "ad_id": "test-001",
        "headline": "Discover Excellence",
        "rating": 4,
        "strengths": "Clear messaging",
        "weaknesses": "Image too dark",
        "corrections": "",
    })
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_submit_feedback_invalid_rating(client):
    r = client.post("/submit_feedback", json={"rating": 6})
    assert r.status_code == 422
