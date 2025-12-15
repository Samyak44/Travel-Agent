FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY api-gateway/requirements.txt /app/requirements-gateway.txt
COPY services/chat-service/requirements.txt /app/requirements-chat.txt
COPY services/flight-service/requirements.txt /app/requirements-flight.txt
COPY services/hotel-service/requirements.txt /app/requirements-hotel.txt
COPY services/user-service/requirements.txt /app/requirements-user.txt
COPY services/weather-service/requirements.txt /app/requirements-weather.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-gateway.txt && \
    pip install --no-cache-dir -r requirements-chat.txt && \
    pip install --no-cache-dir -r requirements-flight.txt && \
    pip install --no-cache-dir -r requirements-hotel.txt && \
    pip install --no-cache-dir -r requirements-user.txt && \
    pip install --no-cache-dir -r requirements-weather.txt

# Copy the entire backend directory
COPY . /app/backend

# Set Python path
ENV PYTHONPATH=/app

WORKDIR /app/backend

# Default command (will be overridden in docker-compose)
CMD ["python", "-m", "uvicorn", "api-gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
