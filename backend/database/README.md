# Database Migrations with Alembic

This directory contains database models and Alembic migrations for the Travel Agent application.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create PostgreSQL database:
```bash
createdb travelagent_db
```

3. Configure `.env` file with database URL:
```
DATABASE_URL=postgresql://username:password@localhost:5432/travelagent_db
```

## Running Migrations

### Apply migrations (upgrade to latest)
```bash
cd backend/database
alembic upgrade head
```

### Create a new migration (after model changes)
```bash
alembic revision --autogenerate -m "description of changes"
```

### Rollback one migration
```bash
alembic downgrade -1
```

### View migration history
```bash
alembic history
```

### View current version
```bash
alembic current
```

## Database Models

- **User**: User accounts with authentication and travel preferences
- **Conversation**: Chat conversation history
- **Message**: Individual chat messages within conversations
- **SearchHistory**: Record of flight/hotel searches
- **Booking**: Flight and hotel bookings
- **Location**: Cached location/city data

## Important Notes

- Always create a migration after changing models in `models.py`
- Test migrations in development before applying to production
- Never modify existing migrations, create new ones instead
- Backup database before running migrations in production
