"""
codelancer.api.main
FastAPI app and endpoints. Safe to import (no auto-start).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from codelancer.api.gui import GUI_HTML
from pydantic import BaseModel
from datetime import datetime
import ast
import asyncio
import logging
from typing import Optional

from codelancer.core import AutoCorrector, CodeGenerator
from codelancer.config import CORS_ORIGINS, DEV
from codelancer.log_handler import InMemoryLogHandler

# Pydantic models for API requests
class CodeRequest(BaseModel):
    code: str
    language: str = "python"

class GenerationRequest(BaseModel):
    description: str
    language: str = "python"
    context: Optional[str] = None

class CorrectionRequest(BaseModel):
    code: str
    language: str = "python"
    fix_style: bool = True
    fix_syntax: bool = True

# Logging: attach in-memory handler to root logger so all app logs are captured
_log_handler = InMemoryLogHandler(maxlen=1000)
_log_handler.setFormatter(logging.Formatter("%(message)s"))
logging.getLogger().addHandler(_log_handler)
logging.getLogger().setLevel(logging.DEBUG if DEV else logging.INFO)

logger = logging.getLogger(__name__)

# Engines
corrector = AutoCorrector()
generator = CodeGenerator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Attach in-memory handler to uvicorn loggers so HTTP access logs and
    # uvicorn error/startup messages are captured and searchable via /logs.
    # Uvicorn sets propagate=False on its own loggers (via dictConfig), so
    # records don't reach the root logger; we must add the handler explicitly.
    try:
        for _name in ("uvicorn", "uvicorn.access"):
            logging.getLogger(_name).addHandler(_log_handler)
        logger.info("CODELANCER AI startup complete")
    except (AttributeError, ValueError, TypeError):
        logger.exception("Failed to attach log handlers during startup; continuing anyway")
    yield
    logger.info("CODELANCER AI shutdown")

# Initialize FastAPI
app = FastAPI(
    title="CODELANCER AI",
    description="AI-powered code analysis, generation, and correction",
    version="0.1.0",
    docs_url="/docs" if DEV else None,
    redoc_url="/redoc" if DEV else None,
    lifespan=lifespan,
)

# CORS: permissive in dev, configurable in production.
# allow_credentials must not be True when allow_origins contains '*' (CORS spec).
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials="*" not in CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=500)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# Endpoints
@app.get("/")
async def root():
    return {
        "message": "CODELANCER AI",
        "status": "running",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat(),
        "dev": DEV,
        "ui": "/ui",
    }

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@app.get("/ui", include_in_schema=False)
async def gui():
    """Serve the built-in web GUI."""
    return HTMLResponse(content=GUI_HTML)

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/logs")
async def get_logs(
    level: Optional[str] = Query(default=None, description="Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    search: Optional[str] = Query(default=None, description="Search substring in log messages"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of log entries to return"),
    since: Optional[str] = Query(default=None, description="Return only logs at or after this ISO 8601 timestamp (e.g. 2026-03-02T16:00:00+00:00)"),
    until: Optional[str] = Query(default=None, description="Return only logs at or before this ISO 8601 timestamp (e.g. 2026-03-02T17:00:00+00:00)"),
):
    if since is not None:
        try:
            # '+' in query strings is decoded as space; restore it for timezone offsets
            datetime.fromisoformat(since.replace(" ", "+"))
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid 'since' timestamp: {since!r}. Use ISO 8601 format.")
        since = since.replace(" ", "+")
    if until is not None:
        try:
            datetime.fromisoformat(until.replace(" ", "+"))
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid 'until' timestamp: {until!r}. Use ISO 8601 format.")
        until = until.replace(" ", "+")
    records = _log_handler.get_records(level=level, search=search, limit=limit, since=since, until=until)
    from_time = records[0]["timestamp"] if records else None
    to_time = records[-1]["timestamp"] if records else None
    return {"logs": records, "count": len(records), "from_time": from_time, "to_time": to_time}

@app.post("/analyze")
async def analyze_code(request: CodeRequest):
    try:
        lines = request.code.count("\n") + 1
        chars = len(request.code)
        words = len(request.code.split())
        syntax_valid = True
        syntax_error = None

        try:
            if request.language == "python":
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, ast.parse, request.code)
        except SyntaxError as e:
            syntax_valid = False
            syntax_error = str(e)

        return {
            "analysis": {
                "lines": lines,
                "characters": chars,
                "words": words,
                "language": request.language,
                "syntax_valid": syntax_valid,
                "syntax_error": syntax_error,
                "estimated_complexity": min(10, lines // 3),
                "density": round(words / max(1, lines), 2),
            },
            "suggestions": ["Consider adding docstrings", "Add error handling"] if lines > 10 else ["Code looks good!"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
def generate_code(request: GenerationRequest):
    try:
        return generator.generate(request.description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/correct")
def correct_code(request: CorrectionRequest):
    try:
        return corrector.correct(request.code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/features")
async def list_features():
    return {
        "features": [
            {"name": "Code Analysis", "endpoint": "POST /analyze"},
            {"name": "Code Generation", "endpoint": "POST /generate"},
            {"name": "Auto-Correction", "endpoint": "POST /correct"},
        ]
    }
