#!/bin/bash
# Quick Start Script - Workforce Analytics

echo "🚀 Starting Workforce Wellbeing Analytics..."
echo ""

# Colors
GREEN='\033[0.32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Firebase service account exists
if [ ! -f "api/firebase-service-account.json" ]; then
    echo -e "${YELLOW}⚠️  Firebase service account key NOT found${NC}"
    echo "   Download from: https://console.firebase.google.com/"
    echo "   Save as: api/firebase-service-account.json"
    echo ""
fi

# Start backend
echo -e "${GREEN}Starting Backend API...${NC}"
cd api
source ../.venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo -e "${GREEN}Starting Frontend...${NC}"
cd app/frontend
npm run dev &
FRONTEND_PID=$!
cd ../..

echo ""
echo -e "${GREEN}✅ Services started!${NC}"
echo ""
echo "📍 Access points:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🛑 To stop, press Ctrl+C"
echo ""

# Wait for user interrupt
wait
