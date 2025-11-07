"""
Database models and connection management
"""
from sqlalchemy import create_engine, Column, String, DateTime, Integer, JSON, Text, Boolean, Float, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings
import enum

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
    extra_metadata = Column(JSON, default=dict)


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
    extra_metadata = Column(JSON, default=dict)


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
    extra_metadata = Column(JSON, default=dict)
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


# ============================================================================
# ALERT SYSTEM MODELS
# ============================================================================

class AlertType(str, enum.Enum):
    """Alert types"""
    OVERTIME_WARNING = "overtime_warning"
    MANAGER_ESCALATION = "manager_escalation"
    TEAM_ESCALATION = "team_escalation"
    WELLBEING_CHECK = "wellbeing_check"
    BURNOUT_RISK = "burnout_risk"


class AlertStatus(str, enum.Enum):
    """Alert status"""
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class EmployeeAttendance(Base):
    """Track employee login/logout times"""
    __tablename__ = "employee_attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, index=True, nullable=False)
    login_time = Column(DateTime, nullable=False)
    logout_time = Column(DateTime, nullable=True)
    date = Column(DateTime, index=True, nullable=False)
    is_overtime = Column(Boolean, default=False)
    overtime_hours = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OvertimeTracker(Base):
    """Track overtime occurrences for employees"""
    __tablename__ = "overtime_tracker"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, index=True, nullable=False)
    manager_id = Column(String, index=True, nullable=False)
    overtime_count = Column(Integer, default=0)
    last_overtime_date = Column(DateTime, nullable=True)
    threshold_reached = Column(Boolean, default=False)
    escalation_triggered = Column(Boolean, default=False)
    manager_notified = Column(Boolean, default=False)
    team_notified = Column(Boolean, default=False)
    reset_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Alert(Base):
    """Alert notifications"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String, nullable=False)
    employee_id = Column(String, index=True, nullable=False)
    recipient_id = Column(String, index=True, nullable=False)
    recipient_type = Column(String, nullable=False)  # 'manager', 'team', 'employee'
    subject = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String, default=AlertStatus.PENDING.value)
    priority = Column(String, default="medium")  # low, medium, high, critical
    sent_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    action_required = Column(Boolean, default=True)
    action_deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ManagerAction(Base):
    """Track manager actions on overtime alerts"""
    __tablename__ = "manager_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    manager_id = Column(String, index=True, nullable=False)
    employee_id = Column(String, index=True, nullable=False)
    action_taken = Column(String, nullable=True)
    action_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ManagerPenalty(Base):
    """Track penalties for managers who don't take action"""
    __tablename__ = "manager_penalties"
    
    id = Column(Integer, primary_key=True, index=True)
    manager_id = Column(String, index=True, nullable=False)
    employee_id = Column(String, index=True, nullable=False)
    reason = Column(Text, nullable=False)
    penalty_type = Column(String, nullable=False)  # 'fine', 'warning', 'other'
    penalty_amount = Column(Float, nullable=True)
    penalty_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending, applied, appealed
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class WellbeingFeedback(Base):
    """Team feedback on colleague wellbeing"""
    __tablename__ = "wellbeing_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, index=True, nullable=False)
    feedback_provider_id = Column(String, index=True, nullable=False)
    feedback_date = Column(DateTime, default=datetime.utcnow)
    is_doing_well = Column(Boolean, nullable=True)
    concerns = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5 scale
    comments = Column(Text, nullable=True)
    anonymous = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TeamWellbeingCheck(Base):
    """Scheduled team wellbeing check events"""
    __tablename__ = "team_wellbeing_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String, index=True, nullable=False)
    employee_id = Column(String, index=True, nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    completed = Column(Boolean, default=False)
    responses_count = Column(Integer, default=0)
    positive_responses = Column(Integer, default=0)
    negative_responses = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TeamMember(Base):
    """Team membership for tracking team relationships"""
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String, index=True, nullable=False)
    employee_id = Column(String, index=True, nullable=False)
    manager_id = Column(String, index=True, nullable=False)
    role = Column(String, nullable=True)
    joined_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Dependency to get database session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
