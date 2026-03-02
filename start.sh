#!/bin/sh
# Entrypoint: reads PORT from environment (Railway injects it), falls back to 8000
PORT="${PORT:-8000}"
exec python -m uvicorn codelancer.api.main:app --host 0.0.0.0 --port "$PORT" --proxy-headers --forwarded-allow-ips='*'
