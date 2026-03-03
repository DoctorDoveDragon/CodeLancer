# Use an official Python runtime as a small base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install minimal build deps (if needed for some wheels or building)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip/setuptools/wheel
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements file first to leverage Docker cache (if present)
COPY requirements_basic.txt requirements_basic.txt
RUN if [ -f requirements_basic.txt ]; then pip install --no-cache-dir -r requirements_basic.txt; fi

# Copy project into image and make start script executable
COPY . /app
RUN chmod +x /app/start.sh

# Install the package (handles src/ layout via setup.py)
RUN pip install --no-cache-dir .

# Verify the package and ASGI app are importable during build (fail fast if not)
RUN python - <<'PY'
import importlib.util, sys

spec = importlib.util.find_spec('codelancer')
if not spec:
    print('ERROR: codelancer package not found after installation')
    sys.exit(1)
print('codelancer package found:', spec)

try:
    from codelancer.api.main import app
    assert hasattr(app, 'routes'), 'app object has no routes attribute'
    print('codelancer.api.main imported OK; routes:', len(app.routes))
except Exception as exc:
    print(f'ERROR: codelancer.api.main failed to import: {exc}')
    sys.exit(1)
PY

# Expose the port the app will run on (Railway overrides with $PORT at runtime)
EXPOSE 8000

# Docker-native healthcheck (uses Python's built-in urllib; no curl needed in slim image)
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
    CMD python /app/healthcheck.py

# Default command: uses start.sh so PORT expansion works regardless of how the
# container runtime invokes it (shell or exec form)
CMD ["/app/start.sh"]
