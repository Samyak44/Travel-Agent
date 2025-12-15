# Travel Agent Backend - Microservices

AI-powered travel agent backend built with Python microservices architecture.

## Architecture

- **API Gateway** (Port 8000): Central gateway for routing requests
- **Chat Service** (Port 8001): LangChain-powered AI agent
- **Flight Service** (Port 8002): Amadeus flight search integration
- **Hotel Service** (Port 8003): Amadeus hotel search integration
- **Weather Service** (Port 8004): OpenWeather API integration
- **User Service** (Port 8005): Authentication and user management
- **PostgreSQL Database**: User data, conversations, bookings
- **Redis** (optional): Caching layer

## Getting Started with Docker

### Prerequisites

- Docker and Docker Compose installed
- API keys for:
  - [OpenRouter](https://openrouter.ai/keys) - for AI models
  - [Amadeus](https://developers.amadeus.com/) - for flights and hotels
  - [OpenWeather](https://openweathermap.org/api) - for weather data

### Setup

1. **Create `.env` file** from the example:
   ```bash
   cp .env.example .env
   ```

2. **Update your `.env` file** with your API keys:
   ```env
   # OpenRouter API (Get from https://openrouter.ai/keys)
   OPENAI_API_KEY=sk-or-v1-your-key-here
   OPENAI_MODEL=openai/gpt-4  # or anthropic/claude-3-opus, etc.

   # Amadeus API
   AMADEUS_API_KEY=your-amadeus-key
   AMADEUS_API_SECRET=your-amadeus-secret

   # Weather API
   WEATHER_API_KEY=your-openweather-key

   # JWT Secret (generate a random string)
   JWT_SECRET=your-super-secret-key-change-this

   # Database (defaults work for Docker)
   DATABASE_URL=postgresql://travelagent:password@postgres:5432/travelagent_db
   POSTGRES_PASSWORD=password
   ```

3. **Build and start all services**:
   ```bash
   docker-compose up --build
   ```

   Or run in detached mode:
   ```bash
   docker-compose up -d --build
   ```

4. **Check service health**:
   ```bash
   curl http://localhost:8000/health/services
   ```

5. **Access the API documentation**:
   - API Gateway Docs: http://localhost:8000/docs
   - Chat Service: http://localhost:8001/docs
   - Flight Service: http://localhost:8002/docs
   - Hotel Service: http://localhost:8003/docs
   - Weather Service: http://localhost:8004/docs
   - User Service: http://localhost:8005/docs

### Managing Services

**Stop all services**:
```bash
docker-compose down
```

**Stop and remove volumes** (clean database):
```bash
docker-compose down -v
```

**View logs**:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f chat-service
```

**Restart a specific service**:
```bash
docker-compose restart chat-service
```

## Database Migrations

To run database migrations:

```bash
# Access the database container
docker exec -it travel-agent-db psql -U travelagent -d travelagent_db

# Or run migrations from user-service
docker-compose exec user-service alembic upgrade head
```

## OpenRouter Configuration

This project uses **OpenRouter** instead of directly using OpenAI. OpenRouter provides:
- Access to multiple AI models (OpenAI, Anthropic, Meta, etc.)
- Unified API compatible with OpenAI SDK
- Pay-per-use pricing
- No need for multiple API keys

### Available Models

You can use any model from OpenRouter. Popular options:

```env
# OpenAI Models
OPENAI_MODEL=openai/gpt-4
OPENAI_MODEL=openai/gpt-3.5-turbo

# Anthropic Claude
OPENAI_MODEL=anthropic/claude-3-opus
OPENAI_MODEL=anthropic/claude-3-sonnet

# Meta Llama
OPENAI_MODEL=meta-llama/llama-3-70b-instruct

# And many more at https://openrouter.ai/models
```

## Development

### Project Structure

```
backend/
├── api-gateway/          # API Gateway service
├── database/             # Database models and migrations
├── services/
│   ├── chat-service/     # AI agent service
│   ├── flight-service/   # Flight search service
│   ├── hotel-service/    # Hotel search service
│   ├── user-service/     # User management service
│   └── weather-service/  # Weather service
├── shared/               # Shared utilities and models
│   ├── config/          # Configuration and database
│   ├── models/          # Pydantic models
│   └── utils/           # Helper functions
├── Dockerfile           # Docker image
├── docker-compose.yml   # Docker orchestration
└── .env                 # Environment variables
```

### Running Individual Services Locally

If you want to run services outside Docker:

1. Install dependencies:
   ```bash
   pip install -r api-gateway/requirements.txt
   pip install -r services/chat-service/requirements.txt
   # ... etc
   ```

2. Update `.env` to use localhost:
   ```env
   DATABASE_URL=postgresql://travelagent:password@localhost:5432/travelagent_db
   ```

3. Run PostgreSQL separately:
   ```bash
   docker-compose up postgres -d
   ```

4. Run a service:
   ```bash
   cd api-gateway
   python main.py
   ```

## API Usage Examples

### Register a User
```bash
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

### Chat with AI Agent
```bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to plan a trip to Paris",
    "conversation_id": "test-123"
  }'
```

## Troubleshooting

### Database Connection Issues

If services can't connect to PostgreSQL:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Service Won't Start

```bash
# Check logs for the specific service
docker-compose logs chat-service

# Rebuild the image
docker-compose build chat-service
docker-compose up chat-service
```

### Reset Everything

```bash
# Stop all containers
docker-compose down

# Remove all volumes (WARNING: deletes all data)
docker-compose down -v

# Rebuild and start fresh
docker-compose up --build
```

## License

MIT License
