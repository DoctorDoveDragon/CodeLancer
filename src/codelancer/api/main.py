"""
codelancer.api.main
FastAPI app and endpoints. Safe to import (no auto-start).
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import ast
from typing import Optional

from codelancer.core import AutoCorrector, CodeGenerator

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

# Initialize FastAPI
app = FastAPI(
    title="CODELANCER AI",
    description="AI-powered code analysis, generation, and correction (dev)",
    version="0.1.0",
)

# CORS - permissive for local/dev; tighten in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Engines
corrector = AutoCorrector()
generator = CodeGenerator()

# Endpoints
@app.get("/")
async def root():
    return {
        "message": "CODELANCER AI",
        "status": "running",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

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
                ast.parse(request.code)
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
async def generate_code(request: GenerationRequest):
    try:
        return generator.generate(request.description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/correct")
async def correct_code(request: CorrectionRequest):
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
