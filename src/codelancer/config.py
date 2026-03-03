"""
codelancer.config
Environment-based configuration for dev and production modes.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv(override=False)  # load .env if present; don't override existing env vars
except ImportError:
    pass  # python-dotenv optional; env vars still work without it

# APP_ENV: "dev" or "production" (default: production)
APP_ENV = os.environ.get("APP_ENV", "production").lower()

DEV = APP_ENV == "dev"

# Host / port used by the CLI server/dev commands
HOST = os.environ.get("HOST", "127.0.0.1" if DEV else "0.0.0.0")
_port_str = os.environ.get("PORT", "").strip()
try:
    PORT = int(_port_str) if _port_str else 8000
except ValueError:
    PORT = 8000

# CORS: always configurable via CORS_ORIGINS env var (comma-separated list, or "*")
# Default to "*" to allow all origins in both dev and production unless restricted
CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",") if o.strip()]
if not CORS_ORIGINS:
    CORS_ORIGINS = ["*"]
