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
from integrations.slack import SlackAPI
from integrations.jira import JiraAPI
from integrations.asana import AsanaAPI
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


@router.post("/slack/fetch")
async def fetch_slack_data(
    user_id: str,
    data_types: list[str],  # ["messages", "reactions", "stats"]
    days_back: int = 14,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Fetch data from Slack API
    """
    try:
        # Get valid access token
        access_token = await get_valid_token(user_id, "slack", db)
        
        # Initialize Slack API client
        slack_api = SlackAPI(access_token)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        results = {}
        
        # Fetch user messages
        if "messages" in data_types:
            logger.info(f"Fetching Slack messages for user {user_id}")
            
            fetch_record = DataFetch(
                user_id=user_id,
                provider="slack",
                data_type="messages",
                fetch_start=start_date,
                fetch_end=end_date,
                status="in_progress"
            )
            db.add(fetch_record)
            db.commit()
            
            try:
                messages = await slack_api.get_user_messages(start_date, end_date)
                results["messages"] = {
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
        
        # Fetch reactions
        if "reactions" in data_types:
            logger.info(f"Fetching Slack reactions for user {user_id}")
            
            fetch_record = DataFetch(
                user_id=user_id,
                provider="slack",
                data_type="reactions",
                fetch_start=start_date,
                fetch_end=end_date,
                status="in_progress"
            )
            db.add(fetch_record)
            db.commit()
            
            try:
                reactions = await slack_api.get_reactions(start_date, end_date)
                results["reactions"] = {
                    "count": len(reactions),
                    "reactions": reactions
                }
                
                fetch_record.status = "success"
                fetch_record.records_fetched = len(reactions)
                db.commit()
                
            except Exception as e:
                fetch_record.status = "failed"
                fetch_record.error_message = str(e)
                db.commit()
                raise
        
        # Fetch statistics
        if "stats" in data_types:
            logger.info(f"Fetching Slack stats for user {user_id}")
            
            fetch_record = DataFetch(
                user_id=user_id,
                provider="slack",
                data_type="stats",
                fetch_start=start_date,
                fetch_end=end_date,
                status="in_progress"
            )
            db.add(fetch_record)
            db.commit()
            
            try:
                stats = await slack_api.get_user_stats(start_date, end_date)
                results["stats"] = stats
                
                fetch_record.status = "success"
                fetch_record.records_fetched = 1
                db.commit()
                
            except Exception as e:
                fetch_record.status = "failed"
                fetch_record.error_message = str(e)
                db.commit()
                raise
        
        return {
            "status": "success",
            "user_id": user_id,
            "provider": "slack",
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "results": results
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Slack data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jira/fetch")
async def fetch_jira_data(
    user_id: str,
    data_types: list[str],  # ["issues", "worklogs", "stats"]
    days_back: int = 14,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Fetch Jira data for a user
    Data types: issues, worklogs, stats
    """
    try:
        # Get valid token
        access_token = await get_valid_token(user_id, "jira", db)
        
        # Get cloud_id from token metadata
        token_record = db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == "jira"
        ).first()
        
        cloud_id = token_record.metadata.get("cloud_id")
        if not cloud_id:
            raise HTTPException(status_code=400, detail="No Jira cloud_id found in token metadata")
        
        # Initialize Jira API
        jira_api = JiraAPI(access_token, cloud_id)
        
        # Get current user account_id
        user_info = await jira_api.get_current_user()
        account_id = user_info["account_id"]
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        results = {}
        
        # Fetch issues
        if "issues" in data_types:
            logger.info(f"Fetching Jira issues for user {user_id}")
            
            fetch_record = DataFetch(
                user_id=user_id,
                provider="jira",
                data_type="issues",
                fetch_start=start_date,
                fetch_end=end_date,
                status="in_progress"
            )
            db.add(fetch_record)
            db.commit()
            
            try:
                issues = await jira_api.get_user_issues(
                    account_id,
                    start_date,
                    end_date,
                    max_results=500
                )
                results["issues"] = {
                    "count": len(issues),
                    "issues": issues
                }
                
                fetch_record.status = "success"
                fetch_record.records_fetched = len(issues)
                db.commit()
                
            except Exception as e:
                fetch_record.status = "failed"
                fetch_record.error_message = str(e)
                db.commit()
                raise
        
        # Fetch worklogs
        if "worklogs" in data_types:
            logger.info(f"Fetching Jira worklogs for user {user_id}")
            
            fetch_record = DataFetch(
                user_id=user_id,
                provider="jira",
                data_type="worklogs",
                fetch_start=start_date,
                fetch_end=end_date,
                status="in_progress"
            )
            db.add(fetch_record)
            db.commit()
            
            try:
                worklogs = await jira_api.get_user_worklogs(
                    account_id,
                    start_date,
                    end_date
                )
                results["worklogs"] = {
                    "count": len(worklogs),
                    "worklogs": worklogs
                }
                
                fetch_record.status = "success"
                fetch_record.records_fetched = len(worklogs)
                db.commit()
                
            except Exception as e:
                fetch_record.status = "failed"
                fetch_record.error_message = str(e)
                db.commit()
                raise
        
        # Fetch statistics
        if "stats" in data_types:
            logger.info(f"Fetching Jira stats for user {user_id}")
            
            fetch_record = DataFetch(
                user_id=user_id,
                provider="jira",
                data_type="stats",
                fetch_start=start_date,
                fetch_end=end_date,
                status="in_progress"
            )
            db.add(fetch_record)
            db.commit()
            
            try:
                stats = await jira_api.get_user_stats(
                    account_id,
                    start_date,
                    end_date
                )
                results["stats"] = stats
                
                fetch_record.status = "success"
                fetch_record.records_fetched = 1
                db.commit()
                
            except Exception as e:
                fetch_record.status = "failed"
                fetch_record.error_message = str(e)
                db.commit()
                raise
        
        return {
            "status": "success",
            "user_id": user_id,
            "provider": "jira",
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "results": results
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Jira data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/asana/fetch")
async def fetch_asana_data(
    user_id: str,
    workspace_gid: str,
    data_types: list[str],  # ["tasks", "projects", "stats"]
    days_back: int = 14,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Fetch Asana data for a user
    Data types: tasks, projects, stats
    """
    try:
        # Get valid token
        access_token = await get_valid_token(user_id, "asana", db)
        
        # Initialize Asana API
        asana_api = AsanaAPI(access_token)
        
        # Get current user
        user_info = await asana_api.get_current_user()
        user_gid = user_info["gid"]
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        results = {}
        
        # Fetch tasks
        if "tasks" in data_types:
            logger.info(f"Fetching Asana tasks for user {user_id}")
            
            fetch_record = DataFetch(
                user_id=user_id,
                provider="asana",
                data_type="tasks",
                fetch_start=start_date,
                fetch_end=end_date,
                status="in_progress"
            )
            db.add(fetch_record)
            db.commit()
            
            try:
                tasks = await asana_api.get_user_tasks(
                    user_gid,
                    workspace_gid,
                    modified_since=start_date
                )
                results["tasks"] = {
                    "count": len(tasks),
                    "tasks": tasks
                }
                
                fetch_record.status = "success"
                fetch_record.records_fetched = len(tasks)
                db.commit()
                
            except Exception as e:
                fetch_record.status = "failed"
                fetch_record.error_message = str(e)
                db.commit()
                raise
        
        # Fetch projects
        if "projects" in data_types:
            logger.info(f"Fetching Asana projects for workspace {workspace_gid}")
            
            fetch_record = DataFetch(
                user_id=user_id,
                provider="asana",
                data_type="projects",
                fetch_start=start_date,
                fetch_end=end_date,
                status="in_progress"
            )
            db.add(fetch_record)
            db.commit()
            
            try:
                projects = await asana_api.get_projects(workspace_gid)
                results["projects"] = {
                    "count": len(projects),
                    "projects": projects
                }
                
                fetch_record.status = "success"
                fetch_record.records_fetched = len(projects)
                db.commit()
                
            except Exception as e:
                fetch_record.status = "failed"
                fetch_record.error_message = str(e)
                db.commit()
                raise
        
        # Fetch statistics
        if "stats" in data_types:
            logger.info(f"Fetching Asana stats for user {user_id}")
            
            fetch_record = DataFetch(
                user_id=user_id,
                provider="asana",
                data_type="stats",
                fetch_start=start_date,
                fetch_end=end_date,
                status="in_progress"
            )
            db.add(fetch_record)
            db.commit()
            
            try:
                stats = await asana_api.get_user_stats(
                    user_gid,
                    workspace_gid,
                    start_date,
                    end_date
                )
                results["stats"] = stats
                
                fetch_record.status = "success"
                fetch_record.records_fetched = 1
                db.commit()
                
            except Exception as e:
                fetch_record.status = "failed"
                fetch_record.error_message = str(e)
                db.commit()
                raise
        
        return {
            "status": "success",
            "user_id": user_id,
            "provider": "asana",
            "workspace_gid": workspace_gid,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "results": results
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Asana data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
