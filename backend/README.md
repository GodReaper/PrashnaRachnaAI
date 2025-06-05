# Question Generator Backend

FastAPI backend for the Question Generation Platform with Clerk Authentication.

## Setup

### 1. Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Copy environment variables
cp env.example .env
```

Update `.env` with your values:
- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql://username:password@localhost:5432/question_generator`)
- `CLERK_PUBLISHABLE_KEY`: Your Clerk publishable key
- `CLERK_SECRET_KEY`: Your Clerk secret key
- `CLERK_JWT_KEY`: Your Clerk JWT signing key

```bash
# Initialize database (creates tables)
python init_db.py

# OR use Alembic migrations (recommended for production)
alembic upgrade head
```

### 3. Run the Server
```bash
python main.py
```

The API will be available at http://localhost:8000

## Database Management

### Using SQLAlchemy Models
```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head

# Create new migration after model changes
alembic revision --autogenerate -m "Description of changes"
```

### Direct Table Creation
```bash
# Quick setup for development
python init_db.py
```

## Testing Authentication

1. Ensure PostgreSQL is running and DATABASE_URL is set
2. Initialize database: `python init_db.py`
3. Start the server: `python main.py`
4. Run authentication tests: `python test_auth.py`

## API Endpoints

### Public Endpoints
- `GET /` - Basic health check
- `GET /health` - Detailed health status
- `GET /auth/public` - Public test endpoint

### Protected Endpoints (Require Authentication)
- `GET /auth/profile` - Get user profile (requires valid JWT)
- `GET /auth/verify` - Verify authentication status

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Clerk Integration

This backend uses Clerk for authentication. Protected routes require a valid JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
``` 