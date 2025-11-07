"""
Feature Extraction Router
Extracts ML features from raw API data
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
import logging

from database import get_db, Feature, DataFetch
from utils.feature_extraction import feature_extractor
from utils.preprocessing import data_preprocessor, data_anonymizer
from integrations.microsoft_graph import MicrosoftGraphAPI
from integrations.slack import SlackAPI
from integrations.jira import JiraAPI
from routers.data import get_valid_token

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def list_features():
    """List available features matching employee_data.csv schema"""
    return {
        "status": "Feature extraction service active",
        "feature_schema": {
            "communication": [
                "meeting_hours_per_week",
                "meeting_counts_per_week",
                "messages_sent_per_day",
                "messages_received_per_day",
                "avg_response_latency_min",
                "communication_burstiness",
                "after_hours_message_ratio",
                "communication_balance",
                "conversation_length_avg"
            ],
            "task_management": [
                "avg_tasks_assigned_per_week",
                "avg_tasks_completed_per_week",
                "task_completion_rate",
                "avg_task_age_days",
                "overdue_task_ratio",
                "task_comment_sentiment_mean"
            ],
            "work_hours": [
                "logged_hours_per_week",
                "variance_in_work_hours",
                "late_start_count_per_month",
                "early_exit_count_per_month",
                "absenteeism_rate",
                "avg_break_length_minutes"
            ],
            "performance": [
                "performance_score",
                "burnout_risk_score"
            ]
        }
    }


@router.post("/extract/{user_id}")
async def extract_features_for_user(
    user_id: str,
    days_back: int = 14,
    providers: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """
    Extract all ML features for a user from all connected providers
    
    This endpoint:
    1. Fetches data from all connected providers
    2. Preprocesses and anonymizes the data
    3. Extracts ML features
    4. Stores features in database
    5. Returns feature vector
    """
    try:
        # Default to all providers if none specified
        if not providers:
            providers = ["microsoft", "slack", "jira"]
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        # Initialize data containers
        calendar_events = []
        teams_messages = []
        slack_messages = []
        emails = []
        jira_issues = []
        jira_worklogs = []
        
        # Fetch from Microsoft Graph
        if "microsoft" in providers:
            try:
                access_token = await get_valid_token(user_id, "microsoft", db)
                graph_api = MicrosoftGraphAPI(access_token)
                
                # Fetch calendar events
                calendar_events = await graph_api.get_calendar_events(start_date, end_date)
                logger.info(f"Fetched {len(calendar_events)} calendar events")
                
                # Fetch emails (metadata only)
                emails = await graph_api.get_emails(start_date, end_date)
                logger.info(f"Fetched {len(emails)} emails")
                
                # Fetch Teams messages (will be anonymized)
                teams_messages = await graph_api.get_teams_messages(start_date, end_date)
                logger.info(f"Fetched {len(teams_messages)} Teams messages")
                
            except Exception as e:
                logger.warning(f"Error fetching Microsoft data: {e}")
        
        # Fetch from Slack
        if "slack" in providers:
            try:
                access_token = await get_valid_token(user_id, "slack", db)
                slack_api = SlackAPI(access_token)
                
                slack_messages = await slack_api.get_user_messages(start_date, end_date)
                logger.info(f"Fetched {len(slack_messages)} Slack messages")
                
            except Exception as e:
                logger.warning(f"Error fetching Slack data: {e}")
        
        # Fetch from Jira
        if "jira" in providers:
            try:
                access_token = await get_valid_token(user_id, "jira", db)
                
                # Get cloud_id from token metadata
                from database import OAuthToken
                token_record = db.query(OAuthToken).filter(
                    OAuthToken.user_id == user_id,
                    OAuthToken.provider == "jira"
                ).first()
                
                if token_record and token_record.metadata.get("cloud_id"):
                    cloud_id = token_record.metadata["cloud_id"]
                    jira_api = JiraAPI(access_token, cloud_id)
                    
                    # Get user info
                    user_info = await jira_api.get_current_user()
                    account_id = user_info["account_id"]
                    
                    # Fetch issues and worklogs
                    jira_issues = await jira_api.get_user_issues(
                        account_id, start_date, end_date, max_results=500
                    )
                    jira_worklogs = await jira_api.get_user_worklogs(
                        account_id, start_date, end_date
                    )
                    logger.info(f"Fetched {len(jira_issues)} Jira issues and {len(jira_worklogs)} worklogs")
                
            except Exception as e:
                logger.warning(f"Error fetching Jira data: {e}")
        
        # === PREPROCESSING PIPELINE ===
        logger.info("Starting data preprocessing with anonymization...")
        
        preprocessed_data = data_preprocessor.preprocess_all_data(
            calendar_events=calendar_events,
            teams_messages=teams_messages,
            slack_messages=slack_messages,
            emails=emails,
            jira_issues=jira_issues
        )
        
        logger.info("✓ Data preprocessing complete. Teams messages are fully anonymized.")
        
        # === FEATURE EXTRACTION ===
        logger.info("Extracting ML features...")
        
        # Combine all messages for communication features
        all_messages = (
            preprocessed_data["teams_messages"] + 
            preprocessed_data["slack_messages"]
        )
        
        # Extract features
        features = feature_extractor.extract_all_features(
            calendar_events=preprocessed_data["calendar_events"],
            messages=all_messages,
            tasks=preprocessed_data["jira_issues"],
            worklogs=jira_worklogs,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        logger.info("✓ Feature extraction complete")
        
        # === STORE FEATURES IN DATABASE ===
        feature_date = datetime.utcnow()
        
        for feature_name, feature_value in features.items():
            feature_record = Feature(
                user_id=user_id,
                date=feature_date,
                provider="aggregated",
                feature_name=feature_name,
                feature_value=feature_value,
                metadata={
                    "days_back": days_back,
                    "providers": providers,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            )
            db.add(feature_record)
        
        db.commit()
        
        logger.info(f"✓ Stored {len(features)} features in database")
        
        return {
            "status": "success",
            "user_id": user_id,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days_back
            },
            "providers_used": providers,
            "data_counts": {
                "calendar_events": len(calendar_events),
                "teams_messages": len(teams_messages),
                "slack_messages": len(slack_messages),
                "emails": len(emails),
                "jira_issues": len(jira_issues),
                "jira_worklogs": len(jira_worklogs)
            },
            "features": features,
            "privacy_notice": "Teams messages have been fully anonymized. Content is only accessible to ML model."
        }
    
    except Exception as e:
        logger.error(f"Error extracting features: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/latest")
async def get_latest_features(
    user_id: str,
    limit: int = 1,
    db: Session = Depends(get_db)
):
    """
    Get the latest extracted features for a user
    """
    try:
        # Get latest feature set
        latest_features = db.query(Feature).filter(
            Feature.user_id == user_id
        ).order_by(Feature.created_at.desc()).limit(limit * 30).all()
        
        if not latest_features:
            raise HTTPException(
                status_code=404,
                detail="No features found. Please extract features first."
            )
        
        # Group by date
        features_by_date = {}
        for feature in latest_features:
            date_key = feature.date.isoformat()
            if date_key not in features_by_date:
                features_by_date[date_key] = {}
            features_by_date[date_key][feature.feature_name] = feature.feature_value
        
        # Get most recent
        recent_date = max(features_by_date.keys())
        
        return {
            "user_id": user_id,
            "date": recent_date,
            "features": features_by_date[recent_date],
            "feature_count": len(features_by_date[recent_date])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting features: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/history")
async def get_feature_history(
    user_id: str,
    days_back: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get feature history over time for trend analysis
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        features = db.query(Feature).filter(
            Feature.user_id == user_id,
            Feature.date >= cutoff_date
        ).order_by(Feature.date.desc()).all()
        
        if not features:
            raise HTTPException(status_code=404, detail="No feature history found")
        
        # Group by date
        history = {}
        for feature in features:
            date_key = feature.date.isoformat()
            if date_key not in history:
                history[date_key] = {}
            history[date_key][feature.feature_name] = feature.feature_value
        
        return {
            "user_id": user_id,
            "days_back": days_back,
            "data_points": len(history),
            "history": history
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feature history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
