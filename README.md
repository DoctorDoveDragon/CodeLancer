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
