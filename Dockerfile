# Simple Dockerfile for development/demo
FROM python:3.11-slim

WORKDIR /app

COPY requirements_basic.txt /app/requirements_basic.txt
RUN pip install --no-cache-dir -r /app/requirements_basic.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "codelancer.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
