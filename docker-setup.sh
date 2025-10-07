#!/bin/bash
# Ajenti 3 Docker Quick Setup Script
# This script automates the Docker setup for Ajenti 3 development

set -e

echo "================================"
echo "Ajenti 3 Docker Setup"
echo "================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker is installed"
echo "✅ Docker Compose is installed"
echo ""

# Stop any existing containers
echo "📦 Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Build and start the container
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting Ajenti container..."
docker-compose up -d

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 3

# Check if container is running
if docker ps | grep -q "ajenti-3-development-backend"; then
    echo ""
    echo "================================"
    echo "✅ SUCCESS!"
    echo "================================"
    echo ""
    echo "Backend is running at: http://localhost:8001"
    echo ""
    echo "📋 Next Steps:"
    echo "1. View logs: docker logs ajenti-ajenti-3-development-backend-1 -f"
    echo "2. Build frontend (see DOCKER_SETUP.md for details)"
    echo "3. Access Ajenti at http://localhost:8001"
    echo ""
    echo "📚 For full setup instructions, see DOCKER_SETUP.md"
    echo ""
else
    echo ""
    echo "❌ Container failed to start"
    echo "View logs with: docker logs ajenti-ajenti-3-development-backend-1"
    exit 1
fi
