# AI Travel Agent - Complete Setup Guide

This guide will walk you through setting up and running the entire AI Travel Agent platform.

## Prerequisites

Before starting, ensure you have:

- **Python 3.11+** installed
- **Node.js 18+** and npm installed
- **PostgreSQL 15+** installed and running
- **Redis** (optional, for caching)

## API Keys Required

You'll need to obtain the following API keys:

1. **OpenAI API Key**
   - Sign up at https://platform.openai.com/
   - Create an API key in your account settings

2. **Amadeus API Key & Secret**
   - Sign up at https://developers.amadeus.com/
   - Create a new app to get API key and secret
   - Use the Test environment for development

3. **OpenWeatherMap API Key**
   - Sign up at https://openweathermap.org/api
   - Get a free API key (sufficient for development)

## Step-by-Step Setup

### 1. Clone and Setup Environment

```bash
cd "Travel-agent"

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment Variables

Edit the `.env` file with your API keys and database credentials:

```bash
# Database Configuration
POSTGRES_USER=travelagent
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=travelagent_db
DATABASE_URL=postgresql://travelagent:your_secure_password@localhost:5432/travelagent_db

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4

# Amadeus API Configuration
AMADEUS_API_KEY=your-amadeus-api-key
AMADEUS_API_SECRET=your-amadeus-api-secret

# Weather API Configuration
WEATHER_API_KEY=your-weather-api-key

# JWT Secret (generate a random string)
JWT_SECRET=your-very-secure-jwt-secret-key
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb travelagent_db

# Or using psql:
psql -U postgres
CREATE DATABASE travelagent_db;
\q

# Run migrations
cd backend/database
pip install -r requirements.txt
alembic upgrade head
cd ../..
```

### 4. Install Backend Dependencies

Each microservice has its own dependencies. Install them:

```bash
# User Service
cd backend/services/user-service
pip install -r requirements.txt
cd ../../..

# Chat Service
cd backend/services/chat-service
pip install -r requirements.txt
cd ../../..

# Flight Service
cd backend/services/flight-service
pip install -r requirements.txt
cd ../../..

# Hotel Service
cd backend/services/hotel-service
pip install -r requirements.txt
cd ../../..

# Weather Service
cd backend/services/weather-service
pip install -r requirements.txt
cd ../../..

# API Gateway
cd backend/api-gateway
pip install -r requirements.txt
cd ../..
```

**Pro Tip**: Create a virtual environment for each service to avoid conflicts:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

## Running the Application

You need to run each microservice in a separate terminal window/tab.

### Terminal 1: API Gateway (Port 8000)

```bash
cd backend/api-gateway
python main.py
```

### Terminal 2: User Service (Port 8005)

```bash
cd backend/services/user-service
python main.py
```

### Terminal 3: Chat Service (Port 8001)

```bash
cd backend/services/chat-service
python main.py
```

### Terminal 4: Flight Service (Port 8002)

```bash
cd backend/services/flight-service
python main.py
```

### Terminal 5: Hotel Service (Port 8003)

```bash
cd backend/services/hotel-service
python main.py
```

### Terminal 6: Weather Service (Port 8004)

```bash
cd backend/services/weather-service
python main.py
```

### Terminal 7: Frontend (Port 3000)

```bash
cd frontend
npm run dev
```

## Accessing the Application

Once all services are running:

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs

Individual service docs:
- User Service: http://localhost:8005/docs
- Chat Service: http://localhost:8001/docs
- Flight Service: http://localhost:8002/docs
- Hotel Service: http://localhost:8003/docs
- Weather Service: http://localhost:8004/docs

## Quick Start Script

To make starting easier, you can create a startup script.

### For Unix/Mac (`start.sh`):

```bash
#!/bin/bash

# Start API Gateway
cd backend/api-gateway && python main.py &

# Start User Service
cd backend/services/user-service && python main.py &

# Start Chat Service
cd backend/services/chat-service && python main.py &

# Start Flight Service
cd backend/services/flight-service && python main.py &

# Start Hotel Service
cd backend/services/hotel-service && python main.py &

# Start Weather Service
cd backend/services/weather-service && python main.py &

# Start Frontend
cd frontend && npm run dev &

echo "All services started!"
echo "Frontend: http://localhost:3000"
echo "API Gateway: http://localhost:8000/docs"
```

Make it executable:
```bash
chmod +x start.sh
./start.sh
```

## Testing the Setup

### 1. Check Service Health

```bash
curl http://localhost:8000/health/services
```

You should see all services as "healthy".

### 2. Test User Registration

```bash
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User",
    "role": "user"
  }'
```

### 3. Test Flight Search

```bash
curl -X POST http://localhost:8000/api/flights/search \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "JFK",
    "destination": "LAX",
    "departure_date": "2024-06-01",
    "passengers": 1,
    "flight_class": "economy"
  }'
```

### 4. Test Weather

```bash
curl http://localhost:8000/api/weather/city/London
```

## Common Issues & Troubleshooting

### Issue: Database connection fails

**Solution**: Ensure PostgreSQL is running and credentials in `.env` are correct.

```bash
# Check if PostgreSQL is running
pg_isready

# Test connection
psql -U travelagent -d travelagent_db
```

### Issue: Port already in use

**Solution**: Change the port in `.env` or kill the process using the port:

```bash
# Find process on port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Issue: Module not found errors

**Solution**: Ensure all dependencies are installed and you're in the correct directory:

```bash
cd backend/services/chat-service
pip install -r requirements.txt
```

### Issue: CORS errors in frontend

**Solution**: Ensure `NEXT_PUBLIC_API_URL` in frontend `.env.local` matches your API Gateway URL.

### Issue: OpenAI API errors

**Solution**:
- Verify your API key is correct
- Check you have credits in your OpenAI account
- Ensure you're using a supported model (gpt-4 or gpt-3.5-turbo)

### Issue: Amadeus API errors

**Solution**:
- Verify you're using the Test environment credentials
- Check API rate limits
- Ensure date formats are correct (YYYY-MM-DD)

## Development Tips

1. **Use virtual environments** for Python services to avoid dependency conflicts
2. **Check logs** - each service outputs logs that help debug issues
3. **Use the Swagger docs** at `/docs` endpoints to test APIs
4. **Monitor the database** - use a tool like pgAdmin or DBeaver
5. **Hot reload** - Both FastAPI and Next.js support hot reload during development

## Production Deployment

For production deployment:

1. Use environment-specific `.env` files
2. Set up proper PostgreSQL with backups
3. Use Redis for caching
4. Deploy services separately (consider containerization)
5. Set up proper logging and monitoring
6. Use a process manager like PM2 or systemd
7. Set up NGINX as a reverse proxy
8. Enable HTTPS with SSL certificates

## Next Steps

1. Create a user account at http://localhost:3000/register
2. Try the AI chat at http://localhost:3000/chat
3. Search for flights and hotels
4. Customize user preferences
5. Explore the API documentation

## Support

For issues or questions:
- Check the individual service README files
- Review API documentation at `/docs` endpoints
- Check logs for error messages

## Architecture Overview

```
Frontend (Next.js) → API Gateway (Port 8000)
                         ↓
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
   User Service    Chat Service    Flight Service
   (Port 8005)     (Port 8001)     (Port 8002)
        ↓                ↓                ↓
   Hotel Service   Weather Service   Database
   (Port 8003)     (Port 8004)      (PostgreSQL)
```

All backend services share:
- Common models and utilities (`backend/shared/`)
- Database connection (PostgreSQL)
- Configuration management

Happy Travel Planning!
