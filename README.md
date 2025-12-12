# AI Travel Agent - Microservices Architecture

A comprehensive travel planning platform powered by AI, built with FastAPI microservices and Next.js frontend.

## Features

- **AI-Powered Chat**: Intelligent travel assistant using LangChain and OpenAI GPT-4
- **Flight Search**: Real-time flight search and booking via Amadeus API
- **Hotel Booking**: Hotel search and recommendations with location-based services
- **Weather Information**: Real-time weather data for travel destinations
- **User Personalization**: User preferences, saved searches, and travel history
- **Authentication**: Secure JWT-based authentication system

## Architecture

### Backend Microservices
- **API Gateway** (Port 8000): Main entry point, request routing
- **Chat Service** (Port 8001): LangChain + OpenAI integration
- **Flight Service** (Port 8002): Amadeus flight search API
- **Hotel Service** (Port 8003): Amadeus hotel search API
- **Weather Service** (Port 8004): Weather data integration
- **User Service** (Port 8005): Authentication & user management

### Tech Stack
- **Backend**: FastAPI, Python 3.11+
- **LLM**: LangChain + OpenAI GPT-4
- **Database**: PostgreSQL with Alembic migrations
- **Cache**: Redis
- **Frontend**: Next.js 14, React, TypeScript
- **APIs**: Amadeus Travel API, OpenWeatherMap

## Project Structure

```
Travel-agent/
├── backend/
│   ├── api-gateway/          # API Gateway service
│   ├── services/
│   │   ├── chat-service/     # LLM & LangChain service
│   │   ├── flight-service/   # Flight search service
│   │   ├── hotel-service/    # Hotel search service
│   │   ├── weather-service/  # Weather data service
│   │   └── user-service/     # User & auth service
│   ├── shared/               # Shared code across services
│   │   ├── models/           # Pydantic models & schemas
│   │   ├── utils/            # Helper functions
│   │   └── config/           # Configuration management
│   └── database/             # Database migrations (Alembic)
├── frontend/                 # Next.js application
├── docs/                     # Documentation
└── scripts/                  # Utility scripts

```

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys:
# - OPENAI_API_KEY
# - AMADEUS_API_KEY & AMADEUS_API_SECRET
# - WEATHER_API_KEY
# - Database credentials
```

### 2. Database Setup

```bash
# Create PostgreSQL database
createdb travelagent_db

# Run migrations
cd backend/database
alembic upgrade head
```

### 3. Backend Services

Each service runs independently:

```bash
# Install dependencies
cd backend/api-gateway
pip install -r requirements.txt

# Run service
uvicorn main:app --port 8000 --reload
```

Repeat for each service in `backend/services/`

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Access the application at `http://localhost:3000`

## API Documentation

Once services are running, access Swagger docs:
- API Gateway: http://localhost:8000/docs
- Chat Service: http://localhost:8001/docs
- Flight Service: http://localhost:8002/docs
- Hotel Service: http://localhost:8003/docs
- Weather Service: http://localhost:8004/docs
- User Service: http://localhost:8005/docs

## Development

### Adding a New Service

1. Create service directory in `backend/services/`
2. Add `main.py`, `models.py`, `routes.py`, `requirements.txt`
3. Register routes in API Gateway
4. Add service configuration to `.env`

### Database Migrations

```bash
cd backend/database

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## License

MIT
