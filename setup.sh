#!/bin/bash

# PromptForge Quick Setup Script
# This script automates the initial setup process

set -e  # Exit on error

echo "🚀 PromptForge Quick Setup"
echo "=========================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install from https://python.org${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install from https://nodejs.org${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found. Please install Node.js from https://nodejs.org${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm found${NC}"

# Check Docker (optional)
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker found${NC}"
    DOCKER_AVAILABLE=true
else
    echo -e "${YELLOW}⚠ Docker not found (optional - needed for sandbox execution)${NC}"
    DOCKER_AVAILABLE=false
fi

echo ""
echo "🔧 Setting up backend..."

# Backend setup
cd backend

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate and install dependencies
echo "Installing Python dependencies..."
source .venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"

cd ..

echo ""
echo "🎨 Setting up frontend..."

# Frontend setup
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
    echo -e "${GREEN}✓ Node.js dependencies installed${NC}"
else
    echo -e "${YELLOW}Node modules already installed${NC}"
fi

cd ..

echo ""
echo "⚙️  Configuring environment..."

# Environment setup
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}⚠ Please edit .env and add your watsonx.ai credentials:${NC}"
    echo "   - WATSONX_API_KEY"
    echo "   - WATSONX_PROJECT_ID"
    echo "   - WATSONX_URL"
else
    echo -e "${YELLOW}.env file already exists${NC}"
fi

# Docker sandbox setup (optional)
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo ""
    echo "🐳 Docker Setup (Optional)"
    read -p "Build Docker sandbox image? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Building sandbox image..."
        cd backend/sandbox
        docker build -t promptforge-sandbox:latest .
        echo -e "${GREEN}✓ Sandbox image built${NC}"
        cd ../..
    fi
fi

# Create data directories
echo ""
echo "📁 Creating data directories..."
mkdir -p data/chroma
mkdir -p data/output
mkdir -p data/temp
mkdir -p data/cache
echo -e "${GREEN}✓ Data directories created${NC}"

echo ""
echo "✅ Setup Complete!"
echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. Configure watsonx.ai credentials in .env file:"
echo "   nano .env"
echo ""
echo "2. Start the backend (Terminal 1):"
echo "   cd backend"
echo "   source .venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "3. Start the frontend (Terminal 2):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "4. Open your browser:"
echo "   http://localhost:3000"
echo ""
echo "📚 For more information, see:"
echo "   - QUICK_START.md - Quick start guide"
echo "   - docs/SETUP.md - Detailed setup instructions"
echo "   - DEMO.md - Demo scenarios and examples"
echo ""
echo "Happy building! 🚀"

# Made with Bob
