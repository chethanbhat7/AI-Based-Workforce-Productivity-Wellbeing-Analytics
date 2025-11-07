#!/bin/bash

# Script to switch between local and production environments

case "$1" in
  local)
    echo "🔧 Switching to LOCAL environment..."
    cp api/.env.local api/.env
    cp app/frontend/.env.local app/frontend/.env
    echo "✅ Local environment activated!"
    echo "   - Backend: http://localhost:8000"
    echo "   - Frontend: http://localhost:5173"
    echo ""
    echo "To start:"
    echo "   1. Terminal 1: cd api && source ../.venv/bin/activate && uvicorn main:app --reload"
    echo "   2. Terminal 2: cd app/frontend && npm run dev"
    ;;
    
  production)
    echo "🚀 Switching to PRODUCTION environment..."
    cp api/.env.production api/.env
    rm -f app/frontend/.env
    echo "✅ Production environment activated!"
    echo "   - Vercel URL: https://ai-based-workforce-productivity-wel-livid.vercel.app"
    echo ""
    echo "To deploy:"
    echo "   1. git add ."
    echo "   2. git commit -m 'Update'"
    echo "   3. git push"
    ;;
    
  *)
    echo "Usage: ./switch-env.sh {local|production}"
    echo ""
    echo "  local       - Configure for local testing (localhost:8000 + localhost:5173)"
    echo "  production  - Configure for Vercel deployment"
    exit 1
    ;;
esac
