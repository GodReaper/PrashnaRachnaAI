#!/bin/bash

# Question Generator - Docker Setup Script
# This script sets up PostgreSQL using Docker Compose

echo "🐳 Setting up Question Generator with Docker"
echo "================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker is available"

# Create .env file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating .env file from template..."
    cp backend/env.example backend/.env
    echo "✅ .env file created. Please update it with your Clerk keys."
else
    echo "✅ .env file already exists"
fi

# Start Docker services
echo "🚀 Starting PostgreSQL, ChromaDB and pgAdmin..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
timeout=60
counter=0

while [ $counter -lt $timeout ]; do
    if docker-compose exec -T postgres pg_isready -U postgres -d question_generator &> /dev/null; then
        echo "✅ PostgreSQL is ready!"
        break
    fi
    sleep 2
    counter=$((counter + 2))
    echo "   Waiting... ($counter/${timeout}s)"
done

if [ $counter -ge $timeout ]; then
    echo "❌ PostgreSQL failed to start within ${timeout} seconds"
    echo "   Check logs with: docker-compose logs postgres"
    exit 1
fi

# Wait for ChromaDB to be ready
echo "⏳ Waiting for ChromaDB to be ready..."
counter=0

while [ $counter -lt $timeout ]; do
    if curl -f http://localhost:8001/api/v2/heartbeat &> /dev/null; then
        echo "✅ ChromaDB is ready!"
        break
    fi
    sleep 2
    counter=$((counter + 2))
    echo "   Waiting... ($counter/${timeout}s)"
done

if [ $counter -ge $timeout ]; then
    echo "❌ ChromaDB failed to start within ${timeout} seconds"
    echo "   Check logs with: docker-compose logs chromadb"
    exit 1
fi

# Display service information
echo ""
echo "🎉 Docker setup completed successfully!"
echo "================================================"
echo "📊 Services started:"
echo "   PostgreSQL: localhost:5432"
echo "   - Database: question_generator"
echo "   - Username: postgres"
echo "   - Password: password123"
echo ""
echo "   ChromaDB: http://localhost:8001"
echo "   - Vector database for document chunks"
echo "   - API endpoint: http://localhost:8001/api/v1"
echo ""
echo "   pgAdmin: http://localhost:8080"
echo "   - Email: admin@questiongenerator.com"
echo "   - Password: admin123"
echo ""
echo "📝 Next steps:"
echo "1. Update backend/.env with your Clerk keys"
echo "2. cd backend"
echo "3. Initialize database: python init_db.py"
echo "4. Start the API server: python main.py"
echo ""
echo "🛠️  Useful commands:"
echo "   Stop services: docker-compose down"
echo "   View logs: docker-compose logs"
echo "   Restart: docker-compose restart" 