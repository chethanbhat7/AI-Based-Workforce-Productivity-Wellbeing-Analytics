"""
Feature Extraction Router
Placeholder for ML feature extraction endpoints
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_features():
    """List available features"""
    return {
        "status": "Feature extraction endpoints coming soon",
        "available_features": [
            "calendar_metrics",
            "email_metrics",
            "teams_metrics"
        ]
    }
