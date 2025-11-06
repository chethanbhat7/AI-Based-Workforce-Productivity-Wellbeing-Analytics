#!/bin/bash

# Workforce Wellbeing Analysis - Development Setup Script

echo "🚀 Workforce Wellbeing Analysis - Development Setup"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if app folder exists
if [ ! -d "app" ]; then
    echo -e "${RED}❌ Error: app folder not found${NC}"
    exit 1
fi

cd app

# Backend Setup
echo -e "\n${YELLOW}📦 Setting up Backend...${NC}"
if [ ! -d "backend/venv" ]; then
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env file${NC}"
    fi
    cd ..
    echo -e "${GREEN}✓ Backend setup complete${NC}"
else
    echo -e "${GREEN}✓ Backend venv already exists${NC}"
fi

# Frontend Setup
echo -e "\n${YELLOW}📦 Setting up Frontend...${NC}"
if [ ! -d "frontend/node_modules" ]; then
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✓ Frontend setup complete${NC}"
else
    echo -e "${GREEN}✓ Frontend node_modules already exists${NC}"
fi

# Display next steps
echo -e "\n${GREEN}✅ Setup Complete!${NC}"
echo -e "\n${YELLOW}📖 Next Steps:${NC}"
echo ""
echo -e "${YELLOW}Terminal 1 - Start Backend:${NC}"
echo "  cd app/backend"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo -e "${YELLOW}Terminal 2 - Start Frontend:${NC}"
echo "  cd app/frontend"
echo "  npm run dev"
echo ""
echo -e "${YELLOW}Or use Docker:${NC}"
echo "  cd app"
echo "  docker-compose up"
echo ""
echo -e "${GREEN}🌐 URLs:${NC}"
echo "  Frontend:  http://localhost:5173"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
