#!/usr/bin/env bash
set -euo pipefail

# Change these if needed
REPO_SSH="git@github.com:DoctorDoveDragon/CodeLancer.git"
REPO_HTTP="https://github.com/DoctorDoveDragon/CodeLancer.git"
BRANCH="refactor/package-layout"
BASE_BRANCH="main"
PR_TITLE="Refactor: package layout (core, api, cli) + tests, CI, Docker"
PR_BODY="Refactor the single-file implementation into a proper Python package layout (src/codelancer).

Files added:
- src/codelancer/core.py
- src/codelancer/api/main.py
- src/codelancer/cli.py
- src/codelancer/__init__.py
- setup.py
- requirements_basic.txt
- README.md
- .gitignore
- tests/test_api.py
- Dockerfile
- .github/workflows/ci.yml

This preserves existing behavior but improves structure for packaging, testing, and CI."

# If not in a repo, clone
if [ ! -d ".git" ]; then
  echo "No git repo detected in this directory. Cloning repository..."
  git clone "$REPO_SSH" repo-temp || git clone "$REPO_HTTP" repo-temp
  cd repo-temp
else
  echo "Using existing repository at $(pwd)"
fi

# Ensure base branch is up to date
git fetch origin || true
if git rev-parse --verify "$BASE_BRANCH" >/dev/null 2>&1; then
  git checkout "$BASE_BRANCH"
  git pull origin "$BASE_BRANCH" || true
else
  echo "No existing commits on $BASE_BRANCH, initializing..."
fi

# Create feature branch
if git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
  git checkout "$BRANCH"
else
  git checkout -b "$BRANCH"
fi

# Create directories
mkdir -p src/codelancer/api
mkdir -p tests
mkdir -p .github/workflows

# Write files
cat > src/codelancer/__init__.py <<'EOF'
__version__ = "0.1.0"
EOF

cat > src/codelancer/core.py <<'EOF'
"""
codelancer.core
Core engines: AutoCorrector and CodeGenerator
"""

from datetime import datetime
import re
from typing import Optional

class AutoCorrector:
    """Simple auto-correction engine"""

    def __init__(self):
        self.common_fixes = {
            "retrun": "return",
            "prinnt": "print",
            "flase": "False",
            "ture": "True",
            "improt": "import",
            "frmo": "from",
            "whiel": "while",
        }

    def correct(self, code: str) -> dict:
        """Correct common code issues"""
        corrections = []
        fixed_code = code

        # Fix common typos
        for wrong, right in self.common_fixes.items():
            if wrong in fixed_code:
                count = fixed_code.count(wrong)
                fixed_code = fixed_code.replace(wrong, right)
                corrections.append(f"Fixed '{wrong}' -> '{right}' ({count} times)")

        # Fix missing colons for common statements
        lines = fixed_code.split("\n")
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (
                (stripped.startswith("def ") or stripped.startswith("class ") or stripped.startswith("if ")
                 or stripped.startswith("for ") or stripped.startswith("while ") or stripped.startswith("elif "))
                and not stripped.endswith(":")
            ):
                lines[i] = line + ":"
                corrections.append(f"Added missing colon on line {i+1}")

        fixed_code = "\n".join(lines)

        # Add parentheses to print calls without them (simple heuristic)
        lines = fixed_code.split("\n")
        for i, line in enumerate(lines):
            if "print " in line and "(" not in line and ")" not in line:
                match = re.search(r'print\s+(.+)', line)
                if match:
                    content = match.group(1)
                    lines[i] = line.replace(f"print {content}", f"print({content})")
                    corrections.append(f"Added parentheses to print on line {i+1}")

        fixed_code = "\n".join(lines)

        return {
            "original": code,
            "corrected": fixed_code,
            "corrections": corrections,
            "total_fixes": len(corrections),
        }


class CodeGenerator:
    """Simple code generator"""

    def generate(self, description: str) -> dict:
        """Generate code from description"""
        func_name = self._suggest_name(description)
        desc_lower = description.lower()
        if any(word in desc_lower for word in ["api", "endpoint", "rest"]):
            code = self._generate_api(description, func_name)
        elif any(word in desc_lower for word in ["class", "object"]):
            code = self._generate_class(description, func_name)
        elif any(word in desc_lower for word in ["test", "unit test"]):
            code = self._generate_test(description, func_name)
        else:
            code = self._generate_function(description, func_name)

        return {
            "description": description,
            "generated_code": code,
            "function_name": func_name,
            "timestamp": datetime.now().isoformat(),
        }

    def _suggest_name(self, description: str) -> str:
        desc = description.lower()
        if "calculate" in desc:
            return "calculate"
        if "validate" in desc:
            return "validate"
        if "create" in desc or "make" in desc:
            return "create"
        if "get" in desc:
            return "get"
        return "process_data"

    def _generate_function(self, description: str, name: str) -> str:
        return f'''def {name}():
    """
    {description}

    Returns:
        Any: result of the operation
    """
    try:
        # TODO: Implement this function
        result = "Function implemented successfully"
        return result
    except Exception as e:
        print(f"Error in {name}: {{e}}")
        raise

if __name__ == "__main__":
    print({name}())'''
    
    def _generate_api(self, description: str, name: str) -> str:
        return f'''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="{name.capitalize()} API")

class RequestModel(BaseModel):
    data: str
    options: Optional[dict] = None

class ResponseModel(BaseModel):
    result: str
    success: bool
    message: Optional[str] = None

@app.get("/")
async def root():
    return {{"message": "{name.capitalize()} API is running"}}

@app.post("/{name}")
async def {name}_endpoint(request: RequestModel):
    try:
        result = process_request(request.data, request.options)
        return ResponseModel(result=result, success=True, message="OK")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def process_request(data: str, options: Optional[dict] = None) -> str:
    return f"Processed: {{data}}"
'''

    def _generate_class(self, description: str, name: str) -> str:
        cls = name.capitalize()
        return f'''class {cls}:
    """
    {description}
    """
    def __init__(self, name: str, value: any = None):
        self.name = name
        self.value = value
        self.created_at = "{datetime.now().isoformat()}"

    def process(self):
        return f"Processed {{self.name}} with value {{self.value}}"

    def validate(self):
        if not self.name:
            raise ValueError("Name cannot be empty")
        return True

if __name__ == "__main__":
    obj = {cls}("test", 42)
    print(obj.process())'''
    
    def _generate_test(self, description: str, name: str) -> str:
        cls = name.capitalize()
        return f'''import unittest

class Test{cls}(unittest.TestCase):
    def test_basic(self):
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()'''
EOF

cat > src/codelancer/api/main.py <<'EOF'
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
EOF

cat > src/codelancer/cli.py <<'EOF'
#!/usr/bin/env python3
"""
CLI for CODELANCER package.
Works in two modes:
- server -> starts the FastAPI server with uvicorn
- generate/correct/analyze -> calls the local engine directly (no HTTP)
"""

import argparse
import sys
import uvicorn
from codelancer.core import CodeGenerator, AutoCorrector

generator = CodeGenerator()
corrector = AutoCorrector()

def run_server(args):
    # Run uvicorn programmatically; keep reload off for programmatic runs
    uvicorn.run("codelancer.api.main:app", host=args.host, port=args.port, reload=args.reload)

def cmd_generate(args):
    description = args.description
    result = generator.generate(description)
    code = result["generated_code"]
    if args.output:
        with open(args.output, "w") as f:
            f.write(code)
        print(f"✅ Generated code saved to {args.output}")
    else:
        print(code)

def cmd_correct(args):
    if args.file:
        with open(args.file, "r") as f:
            code = f.read()
    else:
        print("Paste your code (Ctrl-D to end):")
        code = sys.stdin.read()
    result = corrector.correct(code)
    corrected = result["corrected"]
    if args.output:
        with open(args.output, "w") as f:
            f.write(corrected)
        print(f"✅ Corrected code saved to {args.output}")
    else:
        print(corrected)
    if result["corrections"]:
        print("\nCorrections:")
        for c in result["corrections"]:
            print(f"  • {c}")

def cmd_analyze(args):
    if args.file:
        with open(args.file, "r") as f:
            code = f.read()
    else:
        print("Paste your code (Ctrl-D to end):")
        code = sys.stdin.read()
    lines = code.count("\n") + 1
    chars = len(code)
    print("Code analysis:")
    print(f"  Lines: {lines}")
    print(f"  Characters: {chars}")
    avg = chars // max(1, lines)
    print(f"  Avg line length: {avg}")
    issues = []
    if "retrun" in code:
        issues.append("Found 'retrun' (should be 'return')")
    if issues:
        print("\nIssues found:")
        for i in issues:
            print(f"  • {i}")
    else:
        print("\nNo obvious issues found.")

def main():
    parser = argparse.ArgumentParser(prog="codelancer", description="CODELANCER CLI")
    sub = parser.add_subparsers(dest="cmd")

    srv = sub.add_parser("server", help="Start API server")
    srv.add_argument("--host", default="0.0.0.0")
    srv.add_argument("--port", type=int, default=8000)
    srv.add_argument("--reload", action="store_true", help="Enable reload (dev only)")

    gen = sub.add_parser("generate", help="Generate code from description")
    gen.add_argument("description")
    gen.add_argument("--output", "-o", help="Write output to file")

    corr = sub.add_parser("correct", help="Auto-correct code")
    corr.add_argument("--file", "-f", help="Input file")
    corr.add_argument("--output", "-o", help="Write corrected code to file")

    ana = sub.add_parser("analyze", help="Analyze code")
    ana.add_argument("--file", "-f", help="Input file")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return

    if args.cmd == "server":
        run_server(args)
    elif args.cmd == "generate":
        cmd_generate(args)
    elif args.cmd == "correct":
        cmd_correct(args)
    elif args.cmd == "analyze":
        cmd_analyze(args)

if __name__ == "__main__":
    main()
EOF

cat > setup.py <<'EOF'
from setuptools import setup, find_packages

setup(
    name="codelancer",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
    ],
    entry_points={
        "console_scripts": [
            "codelancer=codelancer.cli:main",
        ],
    },
)
EOF

cat > requirements_basic.txt <<'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
requests==2.31.0
pytest==7.4.0
EOF

cat > README.md <<'EOF'
# CODELANCER (refactored package)

This repo contains a small demo package for CODELANCER: a development/demo-quality tool with:
- REST API (FastAPI): `/`, `/health`, `/analyze`, `/generate`, `/correct`
- CLI: `codelancer` (via the package CLI)
- Core engines split into `codelancer.core` (AutoCorrector, CodeGenerator)

Quick start (local dev)
1. Create venv:
   python3 -m venv .venv
   source .venv/bin/activate

2. Install (editable) and deps:
   pip install -r requirements_basic.txt
   pip install -e .

3. Start server:
   python -m codelancer.cli server --port 8000
   or
   uvicorn codelancer.api.main:app --reload

4. Use CLI:
   python -m codelancer.cli generate "Create a function that calculates factorial"
   python -m codelancer.cli correct --file some_buggy.py

Notes
- This is a development/demo implementation. Before production:
  - Restrict CORS origins
  - Remove `reload=True` in production runs
  - Add proper sanitization/sandbox for generated code execution
  - Add additional tests, logging, monitoring
EOF

cat > .gitignore <<'EOF'
# Byte-compiled / cache
__pycache__/
*.py[cod]
*.pyo
*.pyd

# Virtualenv
.venv/
venv/

# IDEs
.vscode/
.idea/

# OS
.DS_Store

# Python packaging
dist/
build/
*.egg-info/

# Logs
*.log

# Test output
test_output.py
test_code.py
EOF

cat > tests/test_api.py <<'EOF'
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
EOF

cat > Dockerfile <<'EOF'
# Simple Dockerfile for development/demo
FROM python:3.11-slim

WORKDIR /app

COPY requirements_basic.txt /app/requirements_basic.txt
RUN pip install --no-cache-dir -r /app/requirements_basic.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "codelancer.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > .github/workflows/ci.yml <<'EOF'
name: CI

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11"]

    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements_basic.txt
          pip install -e .
      - name: Run tests
        run: |
          pytest -q
EOF

# Stage and commit
git add -A
git commit -m "Refactor: package layout (core, api, cli) + tests, CI, Docker"

# Push branch
git push -u origin "$BRANCH"

echo "Branch '$BRANCH' pushed to origin."

# Create PR using gh if available
if command -v gh >/dev/null 2>&1; then
  echo "Creating Pull Request with gh..."
  gh pr create --base "$BASE_BRANCH" --head "$BRANCH" --title "$PR_TITLE" --body "$PR_BODY"
  echo "PR created via gh."
else
  echo "gh CLI not found. To create the PR, either install gh and run:"
  echo "  gh auth login"
  echo "  gh pr create --base $BASE_BRANCH --head $BRANCH --title \"$PR_TITLE\" --body \"$PR_BODY\""
  echo ""
  echo "Or open a PR from $BRANCH to $BASE_BRANCH via the GitHub web UI at:"
  echo "  https://github.com/DoctorDoveDragon/CodeLancer/compare"
fi

echo "Done."
