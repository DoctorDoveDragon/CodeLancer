import os
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

def test_analyze_syntax_error():
    payload = {"code": "def bad syntax !!!", "language": "python"}
    r = client.post("/analyze", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["analysis"]["syntax_valid"] is False
    assert data["analysis"]["syntax_error"] is not None

def test_analyze_large_code_does_not_block_health():
    """Large code submissions run ast.parse in a thread executor; /health remains reachable."""
    import threading
    large_code = "x = 1\n" * 5000
    payload = {"code": large_code, "language": "python"}
    results = {}

    def call_analyze():
        results["analyze"] = client.post("/analyze", json=payload)

    def call_health():
        results["health"] = client.get("/health")

    t_analyze = threading.Thread(target=call_analyze)
    t_health = threading.Thread(target=call_health)
    t_analyze.start()
    t_health.start()
    t_analyze.join()
    t_health.join()

    assert results["analyze"].status_code == 200
    assert results["health"].status_code == 200

def test_generate_does_not_block_health():
    """The /generate endpoint is a sync def; FastAPI runs it in a thread pool so /health stays reachable."""
    import threading
    payload = {"description": "Create a function that calculates sum", "language": "python"}
    results = {}

    def call_generate():
        results["generate"] = client.post("/generate", json=payload)

    def call_health():
        results["health"] = client.get("/health")

    t_generate = threading.Thread(target=call_generate)
    t_health = threading.Thread(target=call_health)
    t_generate.start()
    t_health.start()
    t_generate.join()
    t_health.join()

    assert results["generate"].status_code == 200
    assert results["health"].status_code == 200

def test_correct_does_not_block_health():
    """The /correct endpoint is a sync def; FastAPI runs it in a thread pool so /health stays reachable."""
    import threading
    large_code = "retrun x\n" * 500
    payload = {"code": large_code, "language": "python"}
    results = {}

    def call_correct():
        results["correct"] = client.post("/correct", json=payload)

    def call_health():
        results["health"] = client.get("/health")

    t_correct = threading.Thread(target=call_correct)
    t_health = threading.Thread(target=call_health)
    t_correct.start()
    t_health.start()
    t_correct.join()
    t_health.join()

    assert results["correct"].status_code == 200
    assert results["health"].status_code == 200

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

def test_features_endpoint():
    r = client.get("/features")
    assert r.status_code == 200
    data = r.json()
    assert "features" in data
    assert len(data["features"]) == 3

def test_dev_mode_config(monkeypatch):
    """In dev mode (APP_ENV=dev), config.DEV is True and docs are enabled."""
    import importlib
    import codelancer.config as cfg
    monkeypatch.setenv("APP_ENV", "dev")
    importlib.reload(cfg)
    assert cfg.DEV is True
    assert cfg.CORS_ORIGINS == ["*"]

def test_logs_endpoint_returns_list():
    r = client.get("/logs")
    assert r.status_code == 200
    data = r.json()
    assert "logs" in data
    assert "count" in data
    assert isinstance(data["logs"], list)
    assert data["count"] == len(data["logs"])

def test_logs_endpoint_limit():
    r = client.get("/logs?limit=2")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] <= 2

def test_logs_endpoint_level_filter():
    import logging
    test_logger = logging.getLogger("test_level_filter")
    test_logger.warning("test-warning-message")
    r = client.get("/logs?level=WARNING&search=test-warning-message")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 1
    for entry in data["logs"]:
        assert entry["level"] == "WARNING"

def test_logs_endpoint_search():
    import logging
    test_logger = logging.getLogger("test_search")
    test_logger.info("unique-search-token-xyz")
    r = client.get("/logs?search=unique-search-token-xyz")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 1
    for entry in data["logs"]:
        assert "unique-search-token-xyz" in entry["message"]

def test_logs_endpoint_invalid_limit():
    r = client.get("/logs?limit=0")
    assert r.status_code == 422

