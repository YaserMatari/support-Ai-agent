# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Unbuffered output + no .pyc files keeps container logs clean and images small.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies first so this layer is cached until requirements change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code.
COPY . .

# The API listens on port 8000.
EXPOSE 8000

# Serve the FastAPI app with uvicorn, bound to 0.0.0.0 so it is reachable from
# outside the container. (The Streamlit UI is started via docker-compose.)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
