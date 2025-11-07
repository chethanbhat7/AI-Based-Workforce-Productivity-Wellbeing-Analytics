#!/bin/bash
# Start script for production deployment with Gunicorn

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Workforce Wellbeing Analytics API with Gunicorn${NC}"

# Navigate to api directory
cd "$(dirname "$0")"

# Check if .env.local exists
if [ ! -f .env.local ]; then
    echo -e "${YELLOW}⚠️  Warning: .env.local not found. Using .env.example defaults${NC}"
    cp .env.example .env.local
fi

# Set default port if not specified
PORT=${PORT:-8000}

# Number of worker processes (2 x CPU cores + 1)
WORKERS=${WORKERS:-4}

echo -e "${GREEN}📊 Configuration:${NC}"
echo "   Port: $PORT"
echo "   Workers: $WORKERS"
echo "   Worker Class: uvicorn.workers.UvicornWorker"
echo ""

# Start Gunicorn with Uvicorn workers
gunicorn main:app \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --reload
