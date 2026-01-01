# Use an official Python runtime as parent image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install build deps (if any) and pip tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy only requirements first for caching (if requirements file exists)
COPY requirements_basic.txt requirements_basic.txt
RUN if [ -f requirements_basic.txt ]; then pip install --no-cache-dir -r requirements_basic.txt; fi

# Copy project files
COPY . /app

# Install the package from source (src layout)
RUN pip install --no-cache-dir .

# Optional: verify package is importable
RUN python -c "import codelancer"

# Expose port (match uvicorn command)
EXPOSE 8000

# Default command - run uvicorn pointing at the installed package
CMD ["uvicorn", "codelancer.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
