"""
Workforce Wellbeing Analytics - API Backend
OAuth2-based integration with workplace tools
"""
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
import logging

from routers import auth, data, users, features
from database import engine, Base
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Workforce Wellbeing Analytics API")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables initialized")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down API")


# Initialize FastAPI app
app = FastAPI(
    title="Workforce Wellbeing Analytics API",
    description="OAuth2-based integration platform for workplace productivity and wellbeing analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(data.router, prefix="/data", tags=["Data Fetching"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(features.router, prefix="/features", tags=["Feature Extraction"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Workforce Wellbeing Analytics API",
        "version": "1.0.0",
        "status": "running",
        "integrations": [
            "Microsoft Graph",
            "Slack",
            "Jira",
            "HRIS",
            "Surveys"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "oauth_providers": {
            "microsoft": settings.MICROSOFT_CLIENT_ID is not None,
            "slack": settings.SLACK_CLIENT_ID is not None,
            "jira": settings.JIRA_CLIENT_ID is not None
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
