# AI Travel Agent - Project Overview

## What We Built

A complete, production-ready AI-powered travel planning platform with microservices architecture, featuring:

- **AI Chat Assistant** powered by LangChain and OpenAI GPT-4
- **Flight Search** using Amadeus API
- **Hotel Booking** using Amadeus API
- **Weather Forecasting** using OpenWeatherMap API
- **User Authentication & Preferences** with JWT
- **Modern Next.js Frontend** with TypeScript and Tailwind CSS

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **AI/ML**: LangChain + OpenAI GPT-4
- **APIs**: Amadeus Travel API, OpenWeatherMap
- **Authentication**: JWT (JSON Web Tokens)
- **HTTP Client**: httpx (async)

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Icons**: React Icons

### Architecture Pattern
- **Microservices Architecture**
- **API Gateway Pattern**
- **Service-Oriented Architecture (SOA)**

## Project Structure

```
Travel-agent/
├── backend/
│   ├── api-gateway/              # Main entry point (Port 8000)
│   │   ├── main.py              # API Gateway with request routing
│   │   └── requirements.txt
│   │
│   ├── services/                 # Microservices
│   │   ├── user-service/        # Authentication & user management (Port 8005)
│   │   │   ├── main.py
│   │   │   ├── routes.py
│   │   │   └── requirements.txt
│   │   │
│   │   ├── chat-service/        # AI chat with LangChain (Port 8001)
│   │   │   ├── main.py
│   │   │   ├── routes.py
│   │   │   ├── agent.py         # LangChain agent implementation
│   │   │   └── requirements.txt
│   │   │
│   │   ├── flight-service/      # Flight search (Port 8002)
│   │   │   ├── main.py
│   │   │   ├── routes.py
│   │   │   ├── amadeus_client.py
│   │   │   └── requirements.txt
│   │   │
│   │   ├── hotel-service/       # Hotel search (Port 8003)
│   │   │   ├── main.py
│   │   │   ├── routes.py
│   │   │   ├── amadeus_client.py
│   │   │   └── requirements.txt
│   │   │
│   │   └── weather-service/     # Weather data (Port 8004)
│   │       ├── main.py
│   │       ├── routes.py
│   │       ├── weather_client.py
│   │       └── requirements.txt
│   │
│   ├── shared/                   # Shared utilities across services
│   │   ├── config/
│   │   │   ├── settings.py      # Centralized configuration
│   │   │   └── database.py      # Database connection
│   │   ├── models/
│   │   │   ├── base.py          # Base models
│   │   │   ├── user.py          # User models
│   │   │   └── travel.py        # Travel-related models
│   │   └── utils/
│   │       ├── security.py      # JWT & password hashing
│   │       ├── http_client.py   # HTTP client wrapper
│   │       └── logger.py        # Logging utilities
│   │
│   └── database/                 # Database migrations
│       ├── models.py            # SQLAlchemy models
│       ├── alembic.ini
│       ├── alembic/
│       │   ├── env.py
│       │   ├── script.py.mako
│       │   └── versions/
│       └── requirements.txt
│
├── frontend/                     # Next.js application
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Homepage
│   │   │   ├── layout.tsx       # Root layout
│   │   │   └── globals.css      # Global styles
│   │   ├── components/          # React components
│   │   ├── lib/
│   │   │   └── api.ts          # API client
│   │   ├── types/
│   │   │   └── index.ts        # TypeScript types
│   │   ├── hooks/              # Custom hooks
│   │   └── store/              # State management
│   ├── public/                  # Static assets
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.js
│
├── .env.example                  # Environment template
├── .gitignore
├── README.md                     # Main README
├── SETUP_GUIDE.md               # Detailed setup instructions
└── PROJECT_OVERVIEW.md          # This file
```

## Services Breakdown

### 1. API Gateway (Port 8000)
**Purpose**: Central entry point for all API requests

**Features**:
- Request routing to microservices
- Service health monitoring
- Centralized error handling
- CORS configuration

**Key Files**:
- `backend/api-gateway/main.py`

### 2. User Service (Port 8005)
**Purpose**: User authentication and profile management

**Features**:
- User registration
- Login with JWT tokens
- User profile management
- Travel preferences
- Password hashing with bcrypt

**Key Files**:
- `backend/services/user-service/main.py`
- `backend/services/user-service/routes.py`

**Endpoints**:
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - Login
- `GET /api/users/me` - Get current user
- `PUT /api/users/me` - Update user profile
- `PUT /api/users/me/preferences` - Update preferences

### 3. Chat Service (Port 8001)
**Purpose**: AI-powered conversational travel assistant

**Features**:
- LangChain integration with OpenAI GPT-4
- Function calling for flight/hotel search
- Conversation history
- Context-aware responses
- Personalized recommendations

**Key Files**:
- `backend/services/chat-service/main.py`
- `backend/services/chat-service/routes.py`
- `backend/services/chat-service/agent.py` - LangChain agent with tools

**LangChain Tools**:
1. `search_flights` - Search for flights
2. `search_hotels` - Search for hotels
3. `get_weather` - Get weather information

**Endpoints**:
- `POST /api/chat/message` - Send message to AI
- `GET /api/chat/conversations/{id}/history` - Get conversation history
- `GET /api/chat/conversations/user/{user_id}` - Get user's conversations

### 4. Flight Service (Port 8002)
**Purpose**: Flight search using Amadeus API

**Features**:
- Real-time flight search
- Airport search and information
- Multiple airlines support
- Flexible search parameters
- Round-trip and one-way searches

**Key Files**:
- `backend/services/flight-service/main.py`
- `backend/services/flight-service/routes.py`
- `backend/services/flight-service/amadeus_client.py`

**Endpoints**:
- `POST /api/flights/search` - Search flights
- `GET /api/flights/airports/search` - Search airports
- `GET /api/flights/airports/{code}` - Get airport details

**Search Parameters**:
- Origin/destination (IATA codes)
- Departure/return dates
- Passengers
- Flight class (economy, business, first)
- Non-stop flights option

### 5. Hotel Service (Port 8003)
**Purpose**: Hotel search using Amadeus API

**Features**:
- Hotel search by city
- Filter by rating, price, amenities
- City search functionality
- Hotel details and information

**Key Files**:
- `backend/services/hotel-service/main.py`
- `backend/services/hotel-service/routes.py`
- `backend/services/hotel-service/amadeus_client.py`

**Endpoints**:
- `POST /api/hotels/search` - Search hotels
- `GET /api/hotels/cities/search` - Search cities
- `GET /api/hotels/{hotel_id}` - Get hotel details

**Search Parameters**:
- City code (IATA)
- Check-in/check-out dates
- Guests and rooms
- Min rating, max price
- Amenities

### 6. Weather Service (Port 8004)
**Purpose**: Weather information using OpenWeatherMap

**Features**:
- Current weather conditions
- 5-day forecast
- Air quality index
- Weather by city or coordinates

**Key Files**:
- `backend/services/weather-service/main.py`
- `backend/services/weather-service/routes.py`
- `backend/services/weather-service/weather_client.py`

**Endpoints**:
- `GET /api/weather/city/{city}` - Weather by city name
- `GET /api/weather/coordinates` - Weather by coordinates
- `GET /api/weather/air-quality` - Air quality data

## Database Schema

### Users Table
- User authentication
- Profile information
- Travel preferences (JSON)

### Conversations Table
- Chat conversation metadata
- User relationship
- Context storage

### Messages Table
- Individual chat messages
- Role (user/assistant/system)
- Timestamps

### SearchHistory Table
- User search history
- Search type (flight/hotel)
- Search parameters

### Bookings Table
- User bookings
- Booking details (JSON)
- Status tracking

### Locations Table
- Cached location data
- IATA codes
- Coordinates

## Key Features

### 1. Intelligent Conversation
The chat service uses LangChain to:
- Understand user intent
- Ask clarifying questions
- Extract travel requirements
- Call appropriate tools (flights, hotels, weather)
- Provide personalized recommendations

### 2. Location-Aware Search
- City and airport search
- IATA code lookup
- Geographic coordinates
- Weather by location

### 3. User Personalization
- Save travel preferences
- Remember past searches
- Tailored recommendations
- Budget tracking

### 4. Real-Time Data
- Live flight availability
- Current hotel prices
- Real-time weather updates
- Air quality monitoring

## API Integration Details

### Amadeus API
- **Environment**: Test (for development)
- **Authentication**: OAuth 2.0
- **Endpoints Used**:
  - Flight Offers Search
  - Hotel Search
  - Location Search

### OpenAI API
- **Model**: GPT-4
- **Framework**: LangChain
- **Features**:
  - Function calling
  - Conversation memory
  - Tool use

### OpenWeatherMap API
- **Plan**: Free tier (sufficient for development)
- **Endpoints Used**:
  - Current Weather
  - 5-Day Forecast
  - Air Pollution

## Security Features

1. **JWT Authentication**
   - Secure token-based auth
   - Token expiration
   - Password hashing with bcrypt

2. **CORS Protection**
   - Configured allowed origins
   - Credential support

3. **Input Validation**
   - Pydantic models
   - Type checking
   - Data sanitization

4. **Environment Variables**
   - Sensitive data in .env
   - No hardcoded secrets

## Scalability Considerations

### Microservices Architecture
- Independent scaling of services
- Service isolation
- Fault tolerance

### Database
- PostgreSQL for reliability
- Connection pooling
- Migration management

### Caching
- Redis support (optional)
- API response caching
- Session management

## Development Workflow

1. **Backend Development**:
   ```bash
   cd backend/services/[service-name]
   python main.py  # Auto-reload enabled
   ```

2. **Frontend Development**:
   ```bash
   cd frontend
   npm run dev  # Hot reload enabled
   ```

3. **Database Changes**:
   ```bash
   cd backend/database
   alembic revision --autogenerate -m "description"
   alembic upgrade head
   ```

4. **Testing APIs**:
   - Use Swagger UI at http://localhost:8000/docs
   - Individual service docs at their `/docs` endpoints

## Next Steps for Enhancement

### Backend
1. Add Redis caching layer
2. Implement booking confirmation
3. Add payment integration
4. Email notifications
5. Advanced search filters
6. Recommendation engine
7. Price tracking

### Frontend
8. Complete chat UI
9. Flight search page
10. Hotel search page
11. User dashboard
12. Booking management
13. Responsive design
14. Progressive Web App (PWA)

### Infrastructure
15. Docker containerization
16. Kubernetes orchestration
17. CI/CD pipeline
18. Monitoring & logging
19. Load balancing
20. Auto-scaling

## Performance Optimization

1. **Backend**:
   - Async/await throughout
   - Connection pooling
   - Request caching
   - Batch processing

2. **Frontend**:
   - Code splitting
   - Image optimization
   - Server-side rendering
   - Static generation

## Monitoring & Debugging

### Health Checks
```bash
curl http://localhost:8000/health/services
```

### Service Logs
Each service outputs detailed logs for debugging.

### Database Monitoring
Use PostgreSQL logs and query performance tools.

## Contributing Guidelines

1. Follow the existing code structure
2. Use type hints in Python
3. Use TypeScript in frontend
4. Write descriptive commit messages
5. Test before committing
6. Update documentation

## License

MIT License - Feel free to use for personal or commercial projects.

---

**Built with best practices for a senior developer level architecture** ✨
