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

# Copy project into image
COPY . /app

# Install the package (handles src/ layout via setup.py or pyproject)
RUN pip install --no-cache-dir .

# Verify the package is importable during build (fail fast if not)
RUN python - <<'PY'
import importlib, sys
spec = importlib.util.find_spec('codelancer')
if not spec:
    print('ERROR: codelancer package not found after installation')
    sys.exit(1)
print('codelancer package installed:', spec)
PY

# Expose the port the app will run on
EXPOSE 8000

# Default command to run the application via the installed package
CMD [ "uvicorn", "codelancer.api.main:app", "--host", "0.0.0.0", "--port", "8000" ]
