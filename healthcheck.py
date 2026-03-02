"""Docker HEALTHCHECK script: verifies the /health endpoint is reachable."""
import os
import sys
import urllib.request

port = os.environ.get("PORT", "8000")
url = f"http://localhost:{port}/health"
try:
    urllib.request.urlopen(url, timeout=4)
except Exception as exc:
    print(f"Healthcheck failed: {exc}", file=sys.stderr)
    sys.exit(1)
