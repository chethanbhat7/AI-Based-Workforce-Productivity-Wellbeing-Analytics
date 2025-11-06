"""
Configuration management for the API
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Workforce Wellbeing Analytics"
    DEBUG: bool = False
    API_VERSION: str = "v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/wellbeing_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENCRYPTION_KEY: str = ""  # Fernet key for token encryption
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000"
    ]
    
    # Microsoft Graph OAuth2
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_TENANT_ID: str = "common"  # or specific tenant ID
    MICROSOFT_REDIRECT_URI: str = "http://localhost:8000/auth/microsoft/callback"
    MICROSOFT_SCOPES: List[str] = [
        "User.Read",
        "Calendars.Read",
        "Mail.Read",
        "Chat.Read",
        "ChannelMessage.Read.All",
        "Presence.Read"
    ]
    MICROSOFT_AUTHORITY: str = "https://login.microsoftonline.com"
    MICROSOFT_GRAPH_ENDPOINT: str = "https://graph.microsoft.com/v1.0"
    
    # Slack OAuth2
    SLACK_CLIENT_ID: str = ""
    SLACK_CLIENT_SECRET: str = ""
    SLACK_REDIRECT_URI: str = "http://localhost:8000/auth/slack/callback"
    SLACK_SCOPES: List[str] = [
        "channels:history",
        "channels:read",
        "users:read",
        "users:read.email",
        "im:history",
        "reactions:read"
    ]
    
    # Jira OAuth2
    JIRA_CLIENT_ID: str = ""
    JIRA_CLIENT_SECRET: str = ""
    JIRA_REDIRECT_URI: str = "http://localhost:8000/auth/jira/callback"
    JIRA_CLOUD_ID: str = ""
    
    # Background Jobs
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Feature Extraction
    ANALYSIS_DAYS_BACK: int = 14
    WORKING_HOURS_START: int = 9
    WORKING_HOURS_END: int = 18
    
    # Privacy
    ANONYMIZE_DATA: bool = True
    HASH_ALGORITHM: str = "sha256"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Initialize settings
settings = Settings()


def get_encryption_key() -> bytes:
    """Get or generate Fernet encryption key"""
    if settings.ENCRYPTION_KEY:
        return settings.ENCRYPTION_KEY.encode()
    
    # Generate a new key if not provided
    from cryptography.fernet import Fernet
    return Fernet.generate_key()
