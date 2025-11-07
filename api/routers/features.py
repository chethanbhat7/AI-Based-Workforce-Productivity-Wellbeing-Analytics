"""
Feature Extraction and Prediction Router
Handles ML feature extraction and predictions
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
import logging

from database import get_db, OAuthToken
from services.feature_extraction import FeatureExtractor
from services.prediction import get_prediction_service
from routers.data import get_valid_token
from integrations.microsoft_graph import MicrosoftGraphAPI
from integrations.slack import SlackAPI
from integrations.jira import JiraAPI

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def list_features():
    """List available feature extraction and prediction endpoints"""
    return {
        "status": "active",
        "endpoints": {
            "predict": "/features/predict/{user_id}",
            "extract": "/features/extract/{user_id}",
            "feature_importance": "/features/importance/{target}",
            "batch_predict": "/features/predict/batch",
            "supported_integrations": ["microsoft", "slack", "jira", "asana"]
        },
        "model_targets": [
            "performance_score",
            "burnout_risk_score"
        ]
    }


@router.post("/extract/{user_id}")
async def extract_features(
    user_id: str,
    providers: Optional[List[str]] = None,
    days_back: int = 14,
    db: Session = Depends(get_db)
):
    """
    Extract ML features from integrated data sources

    Args:
        user_id: User ID to extract features for
        providers: List of data providers to use (defaults to all available)
        days_back: Number of days of historical data to analyze

    Returns:
        Dictionary of extracted features
    """
    try:
        # Default to all providers if none specified
        if not providers:
            providers = ["microsoft", "slack", "jira"]

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)

        # Initialize data containers
        calendar_events = None
        messages = None
        tasks = None
        worklogs = None
        message_source = "teams"
        task_source = "jira"

        # Fetch from Microsoft Graph (calendar, teams messages)
        if "microsoft" in providers:
            try:
                access_token = await get_valid_token(user_id, "microsoft", db)
                graph_api = MicrosoftGraphAPI(access_token)

                logger.info(f"Fetching Microsoft data for user {user_id}")

                # Fetch calendar events
                calendar_events = await graph_api.get_calendar_events(start_date, end_date)
                logger.info(f"Fetched {len(calendar_events)} calendar events")

                # Fetch Teams messages
                messages = await graph_api.get_teams_messages(start_date, end_date)
                logger.info(f"Fetched {len(messages)} Teams messages")
                message_source = "teams"

            except Exception as e:
                logger.warning(f"Error fetching Microsoft data: {e}")

        # Fetch from Slack
        if "slack" in providers:
            try:
                access_token = await get_valid_token(user_id, "slack", db)
                slack_api = SlackAPI(access_token)

                logger.info(f"Fetching Slack data for user {user_id}")

                # Fetch Slack messages (if not already have messages from Teams)
                if not messages:
                    messages = await slack_api.get_user_messages(start_date, end_date)
                    logger.info(f"Fetched {len(messages)} Slack messages")
                    message_source = "slack"

            except Exception as e:
                logger.warning(f"Error fetching Slack data: {e}")

        # Fetch from Jira
        if "jira" in providers:
            try:
                access_token = await get_valid_token(user_id, "jira", db)

                # Get cloud_id from token metadata
                token_record = db.query(OAuthToken).filter(
                    OAuthToken.user_id == user_id,
                    OAuthToken.provider == "jira"
                ).first()

                cloud_id = token_record.metadata.get("cloud_id") if token_record else None
                if cloud_id:
                    jira_api = JiraAPI(access_token, cloud_id)

                    logger.info(f"Fetching Jira data for user {user_id}")

                    # Get user info
                    user_info = await jira_api.get_current_user()
                    account_id = user_info["account_id"]

                    # Fetch issues and worklogs
                    tasks = await jira_api.get_user_issues(account_id, start_date, end_date, max_results=500)
                    worklogs = await jira_api.get_user_worklogs(account_id, start_date, end_date)

                    logger.info(f"Fetched {len(tasks)} Jira issues and {len(worklogs)} worklogs")
                    task_source = "jira"

            except Exception as e:
                logger.warning(f"Error fetching Jira data: {e}")

        # Extract features using FeatureExtractor
        features = FeatureExtractor.extract_all_features(
            calendar_events=calendar_events,
            messages=messages,
            tasks=tasks,
            worklogs=worklogs,
            message_source=message_source,
            task_source=task_source
        )

        return {
            "status": "success",
            "user_id": user_id,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "providers_used": providers,
            "data_counts": {
                "calendar_events": len(calendar_events) if calendar_events else 0,
                "messages": len(messages) if messages else 0,
                "tasks": len(tasks) if tasks else 0,
                "worklogs": len(worklogs) if worklogs else 0
            },
            "features": features
        }

    except Exception as e:
        logger.error(f"Error extracting features: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/{user_id}")
async def predict_employee_metrics(
    user_id: str,
    providers: Optional[List[str]] = None,
    days_back: int = 14,
    custom_features: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """
    Extract features and predict employee metrics

    Args:
        user_id: User ID to make predictions for
        providers: List of data providers (if None, use custom_features)
        days_back: Number of days of historical data to analyze
        custom_features: Manually provided features (skip data fetching if provided)

    Returns:
        Predictions and interpretations
    """
    try:
        prediction_service = get_prediction_service()

        # Extract features if not provided
        if custom_features is None:
            if not providers:
                # Default to all providers if none specified
                providers = ["microsoft", "slack", "jira"]

            logger.info(f"Extracting features for user {user_id}")

            feature_result = await extract_features(
                user_id=user_id,
                providers=providers,
                days_back=days_back,
                db=db
            )

            features = feature_result["features"]
            data_info = {
                "date_range": feature_result["date_range"],
                "providers_used": feature_result["providers_used"],
                "data_counts": feature_result["data_counts"]
            }
        else:
            features = custom_features
            data_info = {
                "source": "custom_features",
                "note": "Features provided manually"
            }

        # Make predictions
        logger.info(f"Making predictions for user {user_id}")
        prediction_result = prediction_service.predict(features)

        if prediction_result["status"] == "error":
            raise HTTPException(status_code=500, detail=prediction_result["message"])

        return {
            "status": "success",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data_info": data_info,
            "features": features,
            "predictions": prediction_result["predictions"],
            "interpretations": prediction_result["interpretations"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error making predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/importance/{target}")
async def get_feature_importance(target: str):
    """
    Get feature importance for a specific prediction target

    Args:
        target: Target variable (e.g., 'performance_score', 'burnout_risk_score')

    Returns:
        Feature importance scores sorted by importance
    """
    try:
        prediction_service = get_prediction_service()

        importance = prediction_service.get_feature_importance(target)

        if not importance:
            raise HTTPException(
                status_code=404,
                detail=f"Feature importance not available for target: {target}"
            )

        # Convert to list format for easier visualization
        importance_list = [
            {"feature": feature, "importance": score}
            for feature, score in importance.items()
        ]

        return {
            "status": "success",
            "target": target,
            "feature_count": len(importance_list),
            "feature_importance": importance_list
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feature importance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/batch")
async def batch_predict(
    predictions_request: dict,
    db: Session = Depends(get_db)
):
    """
    Make predictions for multiple employees

    Request body:
    {
        "user_ids": ["user1", "user2", ...],
        "providers": ["microsoft", "jira"],
        "days_back": 14
    }

    Returns:
        Dictionary with predictions for each user
    """
    try:
        user_ids = predictions_request.get("user_ids", [])
        providers = predictions_request.get("providers", ["microsoft"])
        days_back = predictions_request.get("days_back", 14)

        if not user_ids:
            raise HTTPException(status_code=400, detail="user_ids list is required")

        results = {}

        for user_id in user_ids:
            try:
                result = await predict_employee_metrics(
                    user_id=user_id,
                    providers=providers,
                    days_back=days_back,
                    db=db
                )
                results[user_id] = result
            except Exception as e:
                logger.error(f"Error predicting for user {user_id}: {e}")
                results[user_id] = {
                    "status": "error",
                    "user_id": user_id,
                    "error": str(e)
                }

        return {
            "status": "success",
            "total_users": len(user_ids),
            "successful": len([r for r in results.values() if r.get("status") == "success"]),
            "failed": len([r for r in results.values() if r.get("status") == "error"]),
            "predictions": results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))
