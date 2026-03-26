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

def test_database_url_config(monkeypatch):
    """DATABASE_URL is read from the environment and defaults to empty string."""
    import importlib
    import codelancer.config as cfg

    # Default: not set
    monkeypatch.delenv("DATABASE_URL", raising=False)
    importlib.reload(cfg)
    assert cfg.DATABASE_URL == ""

    # Set: value is picked up
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host/db")
    importlib.reload(cfg)
    assert cfg.DATABASE_URL == "postgresql://user:pass@host/db"

def test_logs_endpoint_returns_list():
    r = client.get("/logs")
    assert r.status_code == 200
    data = r.json()
    assert "logs" in data
    assert "count" in data
    assert isinstance(data["logs"], list)
    assert data["count"] == len(data["logs"])
    # from_time and to_time must always be present in the response
    assert "from_time" in data
    assert "to_time" in data

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

def test_logs_endpoint_since_filter():
    import logging
    from datetime import datetime, timezone, timedelta

    test_logger = logging.getLogger("test_since")
    before = datetime.now(tz=timezone.utc) - timedelta(seconds=1)
    test_logger.info("since-filter-token")
    since = before.isoformat()
    r = client.get(f"/logs?since={since}&search=since-filter-token")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 1
    for entry in data["logs"]:
        assert entry["timestamp"] >= since

def test_logs_endpoint_since_future_returns_empty():
    from datetime import datetime, timezone, timedelta

    future = (datetime.now(tz=timezone.utc) + timedelta(hours=1)).isoformat()
    r = client.get(f"/logs?since={future}")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 0

def test_logs_endpoint_since_invalid():
    r = client.get("/logs?since=not-a-date")
    assert r.status_code == 422

def test_logs_endpoint_since_naive_timestamp():
    """A naive (no-timezone) since timestamp must not crash with a TypeError."""
    import logging
    from datetime import datetime, timezone, timedelta

    # Capture the 'since' time before writing the log entry to avoid a race
    naive = (datetime.now(tz=timezone.utc) - timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%S")
    test_logger = logging.getLogger("test_naive_since")
    test_logger.info("naive-since-token")
    r = client.get(f"/logs?since={naive}&search=naive-since-token")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 1

def test_uvicorn_loggers_attached_after_lifespan():
    """Lifespan startup must attach _log_handler to uvicorn and uvicorn.access loggers."""
    import logging
    from fastapi.testclient import TestClient as _TC
    from codelancer.api import main as _main

    # Use context manager so the lifespan actually runs (module-level client skips lifespan)
    with _TC(_main.app) as tc:
        tc.get("/health")  # ensure app is live
        uv_logger = logging.getLogger("uvicorn")
        uv_access_logger = logging.getLogger("uvicorn.access")
        assert _main._log_handler in uv_logger.handlers, "uvicorn logger missing _log_handler"
        assert _main._log_handler in uv_access_logger.handlers, "uvicorn.access logger missing _log_handler"

def test_favicon():
    r = client.get("/favicon.ico")
    assert r.status_code == 204

def test_ui_endpoint_returns_html():
    r = client.get("/ui")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")
    body = r.text
    assert "CODELANCER" in body
    assert "<html" in body.lower()
    # Verify key GUI sections are present
    assert "ana-code" in body   # Analyze tab
    assert "gen-desc" in body   # Generate tab
    assert "cor-code" in body   # Correct tab
    assert "log-lvl" in body    # Logs tab
    assert "log-range" in body  # Logs time-range filter

def test_root_endpoint_includes_dev_and_ui_fields():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "dev" in data
    assert "ui" in data
    assert data["ui"] == "/ui"

def test_cors_no_credentials_with_wildcard():
    """When CORS_ORIGINS contains '*', the CORS response must not allow credentials."""
    r = client.options(
        "/",
        headers={"Origin": "https://example.com", "Access-Control-Request-Method": "GET"},
    )
    # 'Access-Control-Allow-Credentials: true' must be absent when origin is wildcard
    assert r.headers.get("access-control-allow-credentials", "false").lower() != "true"

def test_unhandled_exception_returns_500():
    """Global exception handler must return 500 for unhandled exceptions (no process crash)."""
    from fastapi import FastAPI as _FastAPI
    from fastapi.testclient import TestClient as _TestClient
    from codelancer.api.main import unhandled_exception_handler

    # Build an isolated app that shares only the exception handler, to avoid
    # mutating the shared global app used by the rest of the test suite.
    test_app = _FastAPI()
    test_app.add_exception_handler(Exception, unhandled_exception_handler)

    @test_app.get("/_crash")
    async def _crash():
        raise RuntimeError("deliberate test crash")

    tc = _TestClient(test_app, raise_server_exceptions=False)
    r = tc.get("/_crash")
    assert r.status_code == 500
    data = r.json()
    assert "detail" in data

def test_health_includes_monitoring_fields():
    """
    After the lifespan runs, /health must include started_at and uptime_seconds
    so that container startup and uptime are observable via the health endpoint.
    """
    from fastapi.testclient import TestClient as _TC
    from codelancer.api import main as _main

    with _TC(_main.app) as tc:
        r = tc.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert "started_at" in data, "health endpoint must include started_at"
    assert "uptime_seconds" in data, "health endpoint must include uptime_seconds"
    assert data["started_at"] is not None, "started_at must be set after lifespan startup"
    assert isinstance(data["uptime_seconds"], (int, float)), "uptime_seconds must be numeric"
    assert data["uptime_seconds"] >= 0, "uptime_seconds must be non-negative"

def test_startup_log_includes_port_and_env():
    """
    The startup log message must record port and APP_ENV so that container
    configuration is visible in the Railway log stream.
    """
    from fastapi.testclient import TestClient as _TC
    from codelancer.api import main as _main

    with _TC(_main.app) as tc:
        r = tc.get("/logs?search=startup+complete")
    assert r.status_code == 200
    data = r.json()
    assert len(data["logs"]) >= 1, "At least one 'startup complete' log entry expected"
    # The message must contain port, env and db info
    msg = data["logs"][0]["message"]
    assert "port=" in msg, f"startup log should include port=, got: {msg!r}"
    assert "env=" in msg, f"startup log should include env=, got: {msg!r}"
    assert "db=" in msg, f"startup log should include db=, got: {msg!r}"

def test_health_returns_503_when_shutting_down(monkeypatch):
    """
    /health must return 503 when _shutting_down is True so that Railway's health
    checker detects the degraded state and stops routing traffic to the container
    before uvicorn closes its listening socket — eliminating the 502 window.
    """
    import codelancer.api.main as _main
    monkeypatch.setattr(_main, "_shutting_down", True)
    r = client.get("/health")
    assert r.status_code == 503
    data = r.json()
    assert data["status"] == "shutting_down"
    assert "started_at" in data
    assert "uptime_seconds" in data


def test_shutdown_log_includes_uptime():
    """
    After the lifespan shuts down, the in-memory logs must contain a shutdown
    message with uptime so Railway logs show how long the container ran.
    """
    from fastapi.testclient import TestClient as _TC
    from codelancer.api import main as _main

    with _TC(_main.app) as tc:
        pass  # lifespan runs startup then shutdown
    # Query logs via a fresh client (module-level client, no lifespan restart needed)
    r = client.get("/logs?search=shutdown")
    assert r.status_code == 200
    data = r.json()
    assert len(data["logs"]) >= 1, "At least one 'shutdown' log entry expected"
    msg = data["logs"][0]["message"]
    assert "uptime=" in msg, f"shutdown log should include uptime=, got: {msg!r}"


def test_drain_delay_constant_positive():
    """_DRAIN_DELAY_S must be a positive integer so the drain window is non-zero."""
    from codelancer.api import main as _main

    assert isinstance(_main._DRAIN_DELAY_S, int), "_DRAIN_DELAY_S must be an int"
    assert _main._DRAIN_DELAY_S > 0, "_DRAIN_DELAY_S must be positive"


