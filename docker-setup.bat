@echo off
REM Question Generator - Docker Setup Script for Windows
REM This script sets up PostgreSQL using Docker Compose

echo 🐳 Setting up Question Generator with Docker
echo ================================================

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    echo    Visit: https://docs.docker.com/desktop/windows/
    pause
    exit /b 1
)

echo ✅ Docker is available

REM Create .env file if it doesn't exist
if not exist "backend\.env" (
    echo 📝 Creating .env file from template...
    copy backend\env.example backend\.env
    echo ✅ .env file created. Please update it with your Clerk keys.
) else (
    echo ✅ .env file already exists
)

REM Start Docker services
echo 🚀 Starting PostgreSQL and pgAdmin...
docker-compose up -d

REM Wait for PostgreSQL to be ready
echo ⏳ Waiting for PostgreSQL to be ready...
timeout /t 10 /nobreak >nul

REM Check if PostgreSQL is ready
docker-compose exec -T postgres pg_isready -U postgres -d question_generator >nul 2>&1
if errorlevel 1 (
    echo ⏳ Still waiting for PostgreSQL...
    timeout /t 10 /nobreak >nul
    docker-compose exec -T postgres pg_isready -U postgres -d question_generator >nul 2>&1
    if errorlevel 1 (
        echo ❌ PostgreSQL is taking longer than expected to start
        echo    Check logs with: docker-compose logs postgres
        pause
        exit /b 1
    )
)

echo ✅ PostgreSQL is ready!

REM Display service information
echo.
echo 🎉 Docker setup completed successfully!
echo ================================================
echo 📊 Services started:
echo    PostgreSQL: localhost:5432
echo    - Database: question_generator
echo    - Username: postgres
echo    - Password: password123
echo.
echo    pgAdmin: http://localhost:8080
echo    - Email: admin@questiongenerator.com
echo    - Password: admin123
echo.
echo 📝 Next steps:
echo 1. Update backend\.env with your Clerk keys
echo 2. cd backend
echo 3. Initialize database: python init_db.py
echo 4. Start the API server: python main.py
echo.
echo 🛠️  Useful commands:
echo    Stop services: docker-compose down
echo    View logs: docker-compose logs
echo    Restart: docker-compose restart

pause 