"""
Database models and connection management
"""
from sqlalchemy import create_engine, Column, String, DateTime, Integer, JSON, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Database Models
class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    organization = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, default=dict)


class OAuthToken(Base):
    """OAuth token storage with encryption"""
    __tablename__ = "oauth_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    provider = Column(String, index=True, nullable=False)  # microsoft, slack, jira, etc.
    access_token = Column(Text, nullable=False)  # Encrypted
    refresh_token = Column(Text, nullable=True)  # Encrypted
    token_type = Column(String, default="Bearer")
    expires_at = Column(DateTime, nullable=True)
    scopes = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default=dict)


class DataFetch(Base):
    """Track data fetch operations"""
    __tablename__ = "data_fetches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    provider = Column(String, index=True, nullable=False)
    data_type = Column(String, nullable=False)  # calendar, email, messages, etc.
    fetch_start = Column(DateTime, nullable=False)
    fetch_end = Column(DateTime, nullable=False)
    status = Column(String, default="pending")  # pending, success, failed
    records_fetched = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Feature(Base):
    """Extracted features for ML"""
    __tablename__ = "features"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    date = Column(DateTime, index=True, nullable=False)
    provider = Column(String, index=True, nullable=False)
    feature_name = Column(String, index=True, nullable=False)
    feature_value = Column(JSON, nullable=False)  # Can be float, int, dict, etc.
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class WellbeingScore(Base):
    """Computed wellbeing scores"""
    __tablename__ = "wellbeing_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    date = Column(DateTime, index=True, nullable=False)
    stress_score = Column(Integer, nullable=True)  # 0-100
    burnout_risk = Column(String, nullable=True)  # low, medium, high
    focus_time_score = Column(Integer, nullable=True)
    collaboration_balance = Column(Integer, nullable=True)
    workload_balance = Column(Integer, nullable=True)
    recommendations = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


# Dependency to get database session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
