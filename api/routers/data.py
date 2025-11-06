"""
Data Fetching Router
Handles data retrieval from connected providers
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import logging

from database import get_db, OAuthToken, DataFetch
from config import settings
from integrations.microsoft_graph import MicrosoftGraphAPI
from utils.encryption import decrypt_token

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_valid_token(user_id: str, provider: str, db: Session) -> str:
    """
    Get a valid access token, refreshing if necessary
    """
    token_record = db.query(OAuthToken).filter(
        OAuthToken.user_id == user_id,
        OAuthToken.provider == provider
    ).first()
    
    if not token_record:
        raise HTTPException(status_code=404, detail=f"No {provider} connection found")
    
    # Check if token is expired
    if token_record.expires_at and token_record.expires_at < datetime.utcnow():
        # Token is expired - need to refresh
        # This would trigger the refresh flow
        raise HTTPException(status_code=401, detail="Token expired, please refresh")
    
    # Decrypt and return token
    return decrypt_token(token_record.access_token)


@router.post("/microsoft/fetch")
async def fetch_microsoft_data(
    user_id: str,
    data_types: list[str],  # ["calendar", "email", "teams"]
    days_back: int = 14,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Fetch data from Microsoft Graph API
    """
    try:
        # Get valid access token
        access_token = await get_valid_token(user_id, "microsoft", db)
        
        # Initialize Graph API client
        graph_api = MicrosoftGraphAPI(access_token)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        results = {}
        
        # Fetch calendar events
        if "calendar" in data_types:
            logger.info(f"Fetching calendar events for user {user_id}")
            
            # Create fetch record
            fetch_record = DataFetch(
                user_id=user_id,
                provider="microsoft",
                data_type="calendar",
                fetch_start=start_date,
                fetch_end=end_date,
                status="in_progress"
            )
            db.add(fetch_record)
            db.commit()
            
            try:
                events = await graph_api.get_calendar_events(start_date, end_date)
                results["calendar"] = {
                    "count": len(events),
                    "events": events
                }
                
                # Update fetch record
                fetch_record.status = "success"
                fetch_record.records_fetched = len(events)
                db.commit()
                
            except Exception as e:
                fetch_record.status = "failed"
                fetch_record.error_message = str(e)
                db.commit()
                raise
        
        # Fetch emails
        if "email" in data_types:
            logger.info(f"Fetching emails for user {user_id}")
            
            fetch_record = DataFetch(
                user_id=user_id,
                provider="microsoft",
                data_type="email",
                fetch_start=start_date,
                fetch_end=end_date,
                status="in_progress"
            )
            db.add(fetch_record)
            db.commit()
            
            try:
                emails = await graph_api.get_emails(start_date, end_date)
                results["email"] = {
                    "count": len(emails),
                    "emails": emails
                }
                
                fetch_record.status = "success"
                fetch_record.records_fetched = len(emails)
                db.commit()
                
            except Exception as e:
                fetch_record.status = "failed"
                fetch_record.error_message = str(e)
                db.commit()
                raise
        
        # Fetch Teams messages
        if "teams" in data_types:
            logger.info(f"Fetching Teams messages for user {user_id}")
            
            fetch_record = DataFetch(
                user_id=user_id,
                provider="microsoft",
                data_type="teams",
                fetch_start=start_date,
                fetch_end=end_date,
                status="in_progress"
            )
            db.add(fetch_record)
            db.commit()
            
            try:
                messages = await graph_api.get_teams_messages(start_date, end_date)
                results["teams"] = {
                    "count": len(messages),
                    "messages": messages
                }
                
                fetch_record.status = "success"
                fetch_record.records_fetched = len(messages)
                db.commit()
                
            except Exception as e:
                fetch_record.status = "failed"
                fetch_record.error_message = str(e)
                db.commit()
                raise
        
        return {
            "status": "success",
            "user_id": user_id,
            "provider": "microsoft",
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "results": results
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Microsoft data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fetch-history/{user_id}")
async def get_fetch_history(
    user_id: str,
    provider: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get data fetch history for a user
    """
    try:
        query = db.query(DataFetch).filter(DataFetch.user_id == user_id)
        
        if provider:
            query = query.filter(DataFetch.provider == provider)
        
        fetches = query.order_by(DataFetch.created_at.desc()).limit(limit).all()
        
        return {
            "user_id": user_id,
            "total": len(fetches),
            "fetches": [
                {
                    "id": f.id,
                    "provider": f.provider,
                    "data_type": f.data_type,
                    "status": f.status,
                    "records_fetched": f.records_fetched,
                    "fetch_start": f.fetch_start.isoformat(),
                    "fetch_end": f.fetch_end.isoformat(),
                    "created_at": f.created_at.isoformat(),
                    "error": f.error_message
                }
                for f in fetches
            ]
        }
    
    except Exception as e:
        logger.error(f"Error getting fetch history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
