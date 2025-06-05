# Question Generator Platform

A comprehensive platform for generating educational questions from uploaded documents using AI agents, built with Next.js frontend and FastAPI backend.

## 🏗️ Architecture

- **Frontend**: Next.js with Clerk authentication
- **Backend**: FastAPI with Clerk JWT verification
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Vector Store**: ChromaDB for semantic search
- **AI**: CrewAI agents for question generation

## 🚀 Quick Start with Docker (Recommended)

### Prerequisites
- [Docker Desktop](https://docs.docker.com/get-docker/) installed and running
- [Git](https://git-scm.com/) installed

### Setup Database with Docker

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd question-generator
   ```

2. **Start PostgreSQL with Docker**:
   
   **On Linux/Mac**:
   ```bash
   chmod +x docker-setup.sh
   ./docker-setup.sh
   ```
   
   **On Windows**:
   ```cmd
   docker-setup.bat
   ```
   
   **Or manually**:
   ```bash
   docker-compose up -d
   ```

3. **Services will be available at**:
   - **PostgreSQL**: `localhost:5432`
     - Database: `question_generator`
     - Username: `postgres` 
     - Password: `password123`
   - **pgAdmin**: http://localhost:8080
     - Email: `admin@questiongenerator.com`
     - Password: `admin123`

### Setup Backend

1. **Navigate to backend**:
   ```bash
   cd backend
   ```

2. **Create Python environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp env.example .env
   # Update .env with your Clerk keys
   ```

5. **Initialize database**:
   ```bash
   python init_db.py
   ```

6. **Start the API server**:
   ```bash
   python main.py
   ```

### Setup Frontend

1. **Navigate to frontend**:
   ```bash
   cd client
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env.local
   # Update with your Clerk keys
   ```

4. **Start the development server**:
   ```bash
   npm run dev
   ```

## 🔧 Development Commands

### Docker Commands
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs

# Restart services
docker-compose restart

# Remove everything (including data)
docker-compose down -v
```

### Database Management
```bash
# Check setup
python setup_check.py

# Initialize tables
python init_db.py

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

### Testing
```bash
# Test authentication
python test_auth.py

# API documentation
# Visit: http://localhost:8000/docs
```

## 📊 Service URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:8080
- **PostgreSQL**: localhost:5432

## 🛠️ Manual PostgreSQL Setup

If you prefer not to use Docker:

1. Install PostgreSQL locally
2. Create database: `question_generator`
3. Update `DATABASE_URL` in `backend/.env`
4. Run `python init_db.py`

## 📝 Environment Variables

### Backend (`backend/.env`)
```env
# Clerk Authentication
CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
CLERK_JWT_KEY=your_jwt_key

# Database
DATABASE_URL=postgresql://postgres:password123@localhost:5432/question_generator

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### Frontend (`client/.env.local`)
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

## 🔍 Troubleshooting

### Docker Issues
- Ensure Docker Desktop is running
- Check port 5432 is not already in use
- Run `docker-compose logs postgres` for database logs

### Database Connection
- Verify PostgreSQL is running: `docker-compose ps`
- Test connection: `python setup_check.py`
- Reset database: `docker-compose down -v && docker-compose up -d`

### Authentication Issues
- Verify Clerk keys are set correctly
- Check JWT token format in API requests
- Test with: `python test_auth.py`

## 📚 Project Structure

```
question-generator/
├── client/                 # Next.js frontend
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── models/       # Database models
│   │   ├── routes/       # API routes
│   │   └── services/     # Business logic
│   ├── auth/             # Authentication
│   ├── config/           # Configuration
│   └── alembic/          # Database migrations
├── docker-compose.yml    # Docker services
└── init-scripts/         # Database initialization
```

## 🚦 Development Workflow

1. Start Docker services: `./docker-setup.sh`
2. Initialize backend database: `cd backend && python init_db.py`
3. Start backend API: `python main.py`
4. Start frontend: `cd client && npm run dev`
5. Begin development!

For detailed backend setup, see [backend/README.md](backend/README.md). 