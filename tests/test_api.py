import pytest
from fastapi.testclient import TestClient
from codelancer.api import main as api_main

client = TestClient(api_main.app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "status" in r.json()

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "healthy"

def test_analyze_basic():
    payload = {"code": "def hello():\\n    pass", "language": "python"}
    r = client.post("/analyze", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "analysis" in data
    assert data["analysis"]["lines"] >= 1

def test_generate_basic():
    payload = {"description": "Create a function that calculates sum", "language": "python"}
    r = client.post("/generate", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "generated_code" in data

def test_correct_basic():
    payload = {"code": "def add(a, b)\\n    retrun a + b", "language": "python"}
    r = client.post("/correct", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "corrected" in data or "corrected" in data.keys()
