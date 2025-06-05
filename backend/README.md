# Question Generator Backend

FastAPI backend for the Question Generation Platform with Clerk Authentication.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment variables:
```bash
cp env.example .env
```

4. Update `.env` with your actual Clerk values:
   - `CLERK_PUBLISHABLE_KEY`: Your Clerk publishable key
   - `CLERK_SECRET_KEY`: Your Clerk secret key
   - `CLERK_JWT_KEY`: Your Clerk JWT signing key

5. Run the development server:
```bash
python main.py
```

The API will be available at http://localhost:8000

## Testing Authentication

1. Start the server: `python main.py`
2. Run authentication tests: `python test_auth.py`

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