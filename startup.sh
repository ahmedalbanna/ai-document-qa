#!/bin/bash

# AI Document QA System - Startup Script
# This script automates the setup and startup process

set -e

echo "🤖 AI Document QA System - Startup Script"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

echo -e "${GREEN}✓ Docker found${NC}"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed!${NC}"
    echo "Please install Docker Compose first"
    exit 1
fi

echo -e "${GREEN}✓ Docker Compose found${NC}"

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ Creating .env file from template${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env created${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

echo ""
echo "📦 Starting Docker services..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check if Ollama is running
echo "🔍 Checking Ollama status..."
if docker exec ai-qa-ollama ollama list &> /dev/null; then
    echo -e "${GREEN}✓ Ollama is running${NC}"
    
    # Check if models are installed
    MODELS=$(docker exec ai-qa-ollama ollama list)
    
    if echo "$MODELS" | grep -q "nomic-embed-text"; then
        echo -e "${GREEN}✓ Embedding model found${NC}"
    else
        echo -e "${YELLOW}⚠ Pulling embedding model (nomic-embed-text)...${NC}"
        docker exec ai-qa-ollama ollama pull nomic-embed-text
        echo -e "${GREEN}✓ Embedding model installed${NC}"
    fi
    
    if echo "$MODELS" | grep -q "llama2"; then
        echo -e "${GREEN}✓ LLM model found${NC}"
    else
        echo -e "${YELLOW}⚠ Pulling LLM model (llama2)...${NC}"
        echo "This may take a few minutes (~4GB download)..."
        docker exec ai-qa-ollama ollama pull llama2
        echo -e "${GREEN}✓ LLM model installed${NC}"
    fi
else
    echo -e "${RED}❌ Ollama is not responding${NC}"
    echo "Check logs with: docker-compose logs ollama"
fi

echo ""
echo "🏥 Checking service health..."

# Check backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Backend is starting up...${NC}"
fi

# Check Qdrant
if curl -s http://localhost:6333/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Qdrant is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Qdrant is starting up...${NC}"
fi

echo ""
echo "============================================"
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo ""
echo "Access the application:"
echo -e "  📱 Frontend:  ${GREEN}http://localhost:3000${NC}"
echo -e "  🔧 Backend:   ${GREEN}http://localhost:8000${NC}"
echo -e "  📚 API Docs:  ${GREEN}http://localhost:8000/docs${NC}"
echo -e "  🗄️  Qdrant:   ${GREEN}http://localhost:6333/dashboard${NC}"
echo ""
echo "Useful commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop services:    docker-compose down"
echo "  Restart:          docker-compose restart"
echo ""
echo "Need help? Check README.md or SETUP.md"
echo "============================================"
