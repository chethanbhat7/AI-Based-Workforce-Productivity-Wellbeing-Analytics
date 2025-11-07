"""
OAuth2 Authentication Router
Handles OAuth flows for all providers
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import secrets

from database import get_db, User, OAuthToken
from config import settings
from integrations.microsoft_graph import MicrosoftGraphOAuth
from integrations.slack import SlackOAuth
from integrations.jira import JiraOAuth
from integrations.asana import AsanaOAuth
from integrations.google_sheets import GoogleSheetsOAuth
from integrations.github import GitHubOAuth
from utils.encryption import encrypt_token, decrypt_token

logger = logging.getLogger(__name__)

router = APIRouter()

# OAuth state store (in production, use Redis)
oauth_states = {}

# TEST MODE - Set to True for testing without real OAuth
TEST_MODE = True


def get_success_html(provider: str):
    """HTML response to close popup and notify parent"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Authorization Successful</title></head>
    <body>
        <h2>✅ {provider.capitalize()} Authorization Successful!</h2>
        <p>You can close this window.</p>
        <script>
            // Notify parent window
            if (window.opener) {{
                window.opener.postMessage({{
                    type: 'oauth_success',
                    service: '{provider}'
                }}, '*');
                window.close();
            }}
        </script>
    </body>
    </html>
    """


def get_error_html(provider: str, error: str):
    """HTML response for OAuth errors"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Authorization Failed</title></head>
    <body>
        <h2>❌ {provider.capitalize()} Authorization Failed</h2>
        <p>Error: {error}</p>
        <p>You can close this window and try again.</p>
        <script>
            // Notify parent window
            if (window.opener) {{
                window.opener.postMessage({{
                    type: 'oauth_error',
                    service: '{provider}',
                    error: '{error}'
                }}, '*');
            }}
        </script>
    </body>
    </html>
    """


# Microsoft Graph OAuth2
@router.get("/microsoft/login")
async def microsoft_login(user_id: str, state: str = None, db: Session = Depends(get_db)):
    """
    Initiate Microsoft OAuth2 flow
    """
    try:
        # In TEST MODE, skip OAuth and go directly to success
        if TEST_MODE:
            logger.info(f"TEST MODE: Simulating Microsoft OAuth for user {user_id}")
            return RedirectResponse(url=f"/auth/microsoft/callback?code=TEST_CODE&state={state or user_id}")
        
        # Generate state for CSRF protection if not provided
        if not state:
            state = secrets.token_urlsafe(32)
        
        oauth_states[state] = {
            "user_id": user_id,
            "provider": "microsoft",
            "created_at": datetime.utcnow()
        }
        
        # Initialize Microsoft OAuth
        ms_oauth = MicrosoftGraphOAuth()
        auth_url = ms_oauth.get_authorization_url(state)
        
        logger.info(f"Redirecting user {user_id} to Microsoft login")
        return RedirectResponse(url=auth_url)
    
    except Exception as e:
        logger.error(f"Error initiating Microsoft OAuth: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/microsoft/callback")
async def microsoft_callback(
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Microsoft OAuth2 callback
    Exchange code for tokens and store securely
    """
    try:
        # In TEST MODE, create mock token
        if TEST_MODE:
            logger.info(f"TEST MODE: Creating mock Microsoft token for state {state}")
            user_id = state  # In test mode, state is the user_id
            
            # Create mock token in database
            existing_token = db.query(OAuthToken).filter(
                OAuthToken.user_id == user_id,
                OAuthToken.provider == "microsoft"
            ).first()
            
            if existing_token:
                existing_token.access_token = "TEST_ACCESS_TOKEN_ENCRYPTED"
                existing_token.updated_at = datetime.utcnow()
            else:
                new_token = OAuthToken(
                    user_id=user_id,
                    provider="microsoft",
                    access_token="TEST_ACCESS_TOKEN_ENCRYPTED",
                    refresh_token="TEST_REFRESH_TOKEN_ENCRYPTED",
                    expires_at=datetime.utcnow() + timedelta(days=1),
                    scopes=["User.Read"]
                )
                db.add(new_token)
            
            db.commit()
            logger.info(f"TEST MODE: Mock token stored for user {user_id}")
            return HTMLResponse(content=get_success_html("microsoft"))
        
        # Production OAuth flow
        if state not in oauth_states:
            return HTMLResponse(content=get_error_html("microsoft", "Invalid state parameter"))
        
        state_data = oauth_states.pop(state)
        user_id = state_data["user_id"]
        
        # Exchange code for tokens
        ms_oauth = MicrosoftGraphOAuth()
        token_response = await ms_oauth.exchange_code_for_token(code)
        
        # Encrypt tokens before storage
        encrypted_access_token = encrypt_token(token_response["access_token"])
        encrypted_refresh_token = encrypt_token(token_response.get("refresh_token", ""))
        
        # Calculate expiration
        expires_in = token_response.get("expires_in", 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Check if token already exists
        existing_token = db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == "microsoft"
        ).first()
        
        if existing_token:
            # Update existing token
            existing_token.access_token = encrypted_access_token
            existing_token.refresh_token = encrypted_refresh_token
            existing_token.expires_at = expires_at
            existing_token.scopes = token_response.get("scope", "").split()
            existing_token.updated_at = datetime.utcnow()
        else:
            # Create new token entry
            new_token = OAuthToken(
                user_id=user_id,
                provider="microsoft",
                access_token=encrypted_access_token,
                refresh_token=encrypted_refresh_token,
                expires_at=expires_at,
                scopes=token_response.get("scope", "").split()
            )
            db.add(new_token)
        
        db.commit()
        
        logger.info(f"Successfully stored Microsoft tokens for user {user_id}")
        
        # Return success HTML
        return HTMLResponse(content=get_success_html("microsoft"))
    
    except Exception as e:
        logger.error(f"Error in Microsoft OAuth callback: {e}")
        return HTMLResponse(content=get_error_html("microsoft", str(e)))
        frontend_url = settings.CORS_ORIGINS[0]
        return RedirectResponse(url=f"{frontend_url}/integrations/success?provider=microsoft")
    
    except Exception as e:
        logger.error(f"Error in Microsoft OAuth callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh_token(
    user_id: str,
    provider: str,
    db: Session = Depends(get_db)
):
    """
    Refresh an expired OAuth token
    """
    try:
        # Get stored token
        token_record = db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == provider
        ).first()
        
        if not token_record:
            raise HTTPException(status_code=404, detail="Token not found")
        
        # Decrypt refresh token
        refresh_token = decrypt_token(token_record.refresh_token)
        
        if not refresh_token:
            raise HTTPException(status_code=400, detail="No refresh token available")
        
        # Refresh based on provider
        if provider == "microsoft":
            ms_oauth = MicrosoftGraphOAuth()
            new_token = await ms_oauth.refresh_access_token(refresh_token)
            
            # Update token in database
            token_record.access_token = encrypt_token(new_token["access_token"])
            if "refresh_token" in new_token:
                token_record.refresh_token = encrypt_token(new_token["refresh_token"])
            
            expires_in = new_token.get("expires_in", 3600)
            token_record.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            token_record.updated_at = datetime.utcnow()
            
            db.commit()
            
            return {
                "status": "success",
                "provider": provider,
                "expires_at": token_record.expires_at.isoformat()
            }
        
        elif provider == "slack":
            # Slack tokens don't expire and don't have refresh tokens
            # If token is invalid, user needs to re-authenticate
            raise HTTPException(
                status_code=400,
                detail="Slack tokens do not expire. If invalid, please reconnect."
            )
        
        elif provider == "jira":
            # Refresh Jira token
            jira_oauth = JiraOAuth(
                client_id=settings.JIRA_CLIENT_ID,
                client_secret=settings.JIRA_CLIENT_SECRET,
                redirect_uri=settings.JIRA_REDIRECT_URI,
                scopes=["read:jira-user", "read:jira-work", "offline_access"]
            )
            
            refresh_token = decrypt_token(token_record.refresh_token)
            new_token = await jira_oauth.refresh_access_token(refresh_token)
            
            # Update token in database
            token_record.access_token = encrypt_token(new_token["access_token"])
            if "refresh_token" in new_token:
                token_record.refresh_token = encrypt_token(new_token["refresh_token"])
            
            expires_in = new_token.get("expires_in", 3600)
            token_record.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            token_record.updated_at = datetime.utcnow()
            
            db.commit()
            
            return {
                "status": "success",
                "provider": provider,
                "expires_at": token_record.expires_at.isoformat()
            }
        
        elif provider == "asana":
            # Refresh Asana token (if refresh token available)
            if not token_record.refresh_token:
                raise HTTPException(
                    status_code=400,
                    detail="Asana token has no refresh token. Please reconnect."
                )
            
            asana_oauth = AsanaOAuth(
                client_id=settings.ASANA_CLIENT_ID,
                client_secret=settings.ASANA_CLIENT_SECRET,
                redirect_uri=settings.ASANA_REDIRECT_URI
            )
            
            refresh_token = decrypt_token(token_record.refresh_token)
            new_token = await asana_oauth.refresh_access_token(refresh_token)
            
            # Update token in database
            token_record.access_token = encrypt_token(new_token["access_token"])
            if "refresh_token" in new_token:
                token_record.refresh_token = encrypt_token(new_token["refresh_token"])
            
            expires_in = new_token.get("expires_in")
            if expires_in:
                token_record.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            token_record.updated_at = datetime.utcnow()
            
            db.commit()
            
            return {
                "status": "success",
                "provider": provider,
                "expires_at": token_record.expires_at.isoformat() if token_record.expires_at else None
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
    
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{user_id}")
async def get_auth_status(user_id: str, db: Session = Depends(get_db)):
    """
    Get authentication status for all providers
    """
    try:
        tokens = db.query(OAuthToken).filter(OAuthToken.user_id == user_id).all()
        
        status = {}
        for token in tokens:
            is_expired = token.expires_at and token.expires_at < datetime.utcnow()
            status[token.provider] = {
                "connected": True,
                "expired": is_expired,
                "expires_at": token.expires_at.isoformat() if token.expires_at else None,
                "scopes": token.scopes
            }
        
        return {
            "user_id": user_id,
            "providers": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting auth status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/disconnect/{provider}")
async def disconnect_provider(
    user_id: str,
    provider: str,
    db: Session = Depends(get_db)
):
    """
    Disconnect a provider (delete tokens)
    """
    try:
        token = db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == provider
        ).first()
        
        if not token:
            raise HTTPException(status_code=404, detail="Provider not connected")
        
        db.delete(token)
        db.commit()
        
        logger.info(f"Disconnected {provider} for user {user_id}")
        
        return {
            "status": "success",
            "message": f"{provider} disconnected successfully"
        }
    
    except Exception as e:
        logger.error(f"Error disconnecting provider: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Slack OAuth2
@router.get("/slack/login")
async def slack_login(user_id: str, db: Session = Depends(get_db)):
    """
    Initiate Slack OAuth2 flow
    """
    try:
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        oauth_states[state] = {
            "user_id": user_id,
            "provider": "slack",
            "created_at": datetime.utcnow()
        }
        
        # Initialize Slack OAuth
        slack_oauth = SlackOAuth()
        auth_url = slack_oauth.get_authorization_url(state)
        
        logger.info(f"Redirecting user {user_id} to Slack login")
        return RedirectResponse(url=auth_url)
    
    except Exception as e:
        logger.error(f"Error initiating Slack OAuth: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/slack/callback")
async def slack_callback(
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Slack OAuth2 callback
    Exchange code for tokens and store securely
    """
    try:
        # Validate state
        if state not in oauth_states:
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        state_data = oauth_states.pop(state)
        user_id = state_data["user_id"]
        
        # Exchange code for tokens
        slack_oauth = SlackOAuth()
        token_response = await slack_oauth.exchange_code_for_token(code)
        
        # Extract token from Slack response
        # Slack returns: {"ok": true, "access_token": "...", "team": {...}, "authed_user": {...}}
        access_token = token_response.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token in Slack response")
        
        # Encrypt token before storage
        encrypted_access_token = encrypt_token(access_token)
        
        # Slack tokens don't expire by default, but can be revoked
        # Store team and user info in metadata
        metadata = {
            "team_id": token_response.get("team", {}).get("id"),
            "team_name": token_response.get("team", {}).get("name"),
            "authed_user_id": token_response.get("authed_user", {}).get("id"),
            "scope": token_response.get("scope"),
            "token_type": token_response.get("token_type")
        }
        
        # Check if token already exists
        existing_token = db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == "slack"
        ).first()
        
        if existing_token:
            # Update existing token
            existing_token.access_token = encrypted_access_token
            existing_token.scopes = token_response.get("scope", "").split(",")
            existing_token.metadata = metadata
            existing_token.updated_at = datetime.utcnow()
        else:
            # Create new token entry
            new_token = OAuthToken(
                user_id=user_id,
                provider="slack",
                access_token=encrypted_access_token,
                refresh_token="",  # Slack doesn't use refresh tokens
                expires_at=None,  # Slack tokens don't expire
                scopes=token_response.get("scope", "").split(","),
                metadata=metadata
            )
            db.add(new_token)
        
        db.commit()
        
        logger.info(f"Successfully stored Slack tokens for user {user_id}")
        
        # Redirect to frontend success page
        frontend_url = settings.CORS_ORIGINS[0]
        return RedirectResponse(url=f"{frontend_url}/integrations/success?provider=slack")
    
    except Exception as e:
        logger.error(f"Error in Slack OAuth callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Jira OAuth2
@router.get("/jira/login")
async def jira_login(user_id: str, db: Session = Depends(get_db)):
    """
    Initiate Jira OAuth2 flow
    """
    try:
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        oauth_states[state] = {
            "user_id": user_id,
            "provider": "jira",
            "created_at": datetime.utcnow()
        }
        
        # Initialize Jira OAuth
        jira_oauth = JiraOAuth(
            client_id=settings.JIRA_CLIENT_ID,
            client_secret=settings.JIRA_CLIENT_SECRET,
            redirect_uri=settings.JIRA_REDIRECT_URI,
            scopes=["read:jira-user", "read:jira-work", "offline_access"]
        )
        auth_url = jira_oauth.get_authorization_url(state)
        
        logger.info(f"Redirecting user {user_id} to Jira login")
        return RedirectResponse(url=auth_url)
    
    except Exception as e:
        logger.error(f"Error initiating Jira OAuth: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jira/callback")
async def jira_callback(
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Jira OAuth2 callback
    Exchange code for tokens and store securely
    """
    try:
        # Validate state
        if state not in oauth_states:
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        state_data = oauth_states.pop(state)
        user_id = state_data["user_id"]
        
        # Exchange code for tokens
        jira_oauth = JiraOAuth(
            client_id=settings.JIRA_CLIENT_ID,
            client_secret=settings.JIRA_CLIENT_SECRET,
            redirect_uri=settings.JIRA_REDIRECT_URI,
            scopes=["read:jira-user", "read:jira-work", "offline_access"]
        )
        token_response = await jira_oauth.exchange_code_for_token(code)
        
        # Get accessible resources (Jira sites)
        access_token = token_response["access_token"]
        resources = await jira_oauth.get_accessible_resources(access_token)
        
        if not resources:
            raise HTTPException(status_code=400, detail="No Jira sites accessible")
        
        # Use the first accessible resource (or let user choose in production)
        cloud_id = resources[0]["id"]
        cloud_url = resources[0]["url"]
        
        # Encrypt tokens before storage
        encrypted_access_token = encrypt_token(token_response["access_token"])
        encrypted_refresh_token = encrypt_token(token_response.get("refresh_token", ""))
        
        # Calculate expiration
        expires_in = token_response.get("expires_in", 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Store cloud_id and site info in metadata
        metadata = {
            "cloud_id": cloud_id,
            "cloud_url": cloud_url,
            "site_name": resources[0].get("name"),
            "scopes": token_response.get("scope", "").split()
        }
        
        # Check if token already exists
        existing_token = db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == "jira"
        ).first()
        
        if existing_token:
            # Update existing token
            existing_token.access_token = encrypted_access_token
            existing_token.refresh_token = encrypted_refresh_token
            existing_token.expires_at = expires_at
            existing_token.scopes = token_response.get("scope", "").split()
            existing_token.metadata = metadata
            existing_token.updated_at = datetime.utcnow()
        else:
            # Create new token entry
            new_token = OAuthToken(
                user_id=user_id,
                provider="jira",
                access_token=encrypted_access_token,
                refresh_token=encrypted_refresh_token,
                expires_at=expires_at,
                scopes=token_response.get("scope", "").split(),
                metadata=metadata
            )
            db.add(new_token)
        
        db.commit()
        
        logger.info(f"Successfully stored Jira tokens for user {user_id}")
        
        # Redirect to frontend success page
        frontend_url = settings.CORS_ORIGINS[0]
        return RedirectResponse(url=f"{frontend_url}/integrations/success?provider=jira")
    
    except Exception as e:
        logger.error(f"Error in Jira OAuth callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Asana OAuth2
@router.get("/asana/login")
async def asana_login(user_id: str, db: Session = Depends(get_db)):
    """
    Initiate Asana OAuth2 flow
    """
    try:
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        oauth_states[state] = {
            "user_id": user_id,
            "provider": "asana",
            "created_at": datetime.utcnow()
        }
        
        # Initialize Asana OAuth
        asana_oauth = AsanaOAuth(
            client_id=settings.ASANA_CLIENT_ID,
            client_secret=settings.ASANA_CLIENT_SECRET,
            redirect_uri=settings.ASANA_REDIRECT_URI
        )
        auth_url = asana_oauth.get_authorization_url(state)
        
        logger.info(f"Redirecting user {user_id} to Asana login")
        return RedirectResponse(url=auth_url)
    
    except Exception as e:
        logger.error(f"Error initiating Asana OAuth: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/asana/callback")
async def asana_callback(
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Asana OAuth2 callback
    Exchange code for tokens and store securely
    """
    try:
        # Validate state
        if state not in oauth_states:
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        state_data = oauth_states.pop(state)
        user_id = state_data["user_id"]
        
        # Exchange code for tokens
        asana_oauth = AsanaOAuth(
            client_id=settings.ASANA_CLIENT_ID,
            client_secret=settings.ASANA_CLIENT_SECRET,
            redirect_uri=settings.ASANA_REDIRECT_URI
        )
        token_response = await asana_oauth.exchange_code_for_token(code)
        
        # Encrypt tokens before storage
        encrypted_access_token = encrypt_token(token_response["access_token"])
        encrypted_refresh_token = encrypt_token(token_response.get("refresh_token", ""))
        
        # Calculate expiration (Asana tokens typically don't expire, but handle if provided)
        expires_in = token_response.get("expires_in")
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in) if expires_in else None
        
        # Check if token already exists
        existing_token = db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == "asana"
        ).first()
        
        if existing_token:
            # Update existing token
            existing_token.access_token = encrypted_access_token
            existing_token.refresh_token = encrypted_refresh_token
            existing_token.expires_at = expires_at
            existing_token.updated_at = datetime.utcnow()
        else:
            # Create new token entry
            new_token = OAuthToken(
                user_id=user_id,
                provider="asana",
                access_token=encrypted_access_token,
                refresh_token=encrypted_refresh_token,
                expires_at=expires_at,
                scopes=[],
                metadata={"token_type": token_response.get("token_type")}
            )
            db.add(new_token)
        
        db.commit()
        
        logger.info(f"Successfully stored Asana tokens for user {user_id}")
        
        # Redirect to frontend success page
        frontend_url = settings.CORS_ORIGINS[0]
        return RedirectResponse(url=f"{frontend_url}/integrations/success?provider=asana")
    
    except Exception as e:
        logger.error(f"Error in Asana OAuth callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Google Sheets OAuth2 (for Attendance Tracking)
@router.get("/google/login")
async def google_login(user_id: str, db: Session = Depends(get_db)):
    """
    Initiate Google OAuth2 flow for Google Sheets access
    Required for storing attendance records
    """
    try:
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        oauth_states[state] = {
            "user_id": user_id,
            "provider": "google",
            "created_at": datetime.utcnow()
        }
        
        # Initialize Google OAuth
        google_oauth = GoogleSheetsOAuth()
        auth_url = google_oauth.get_authorization_url(state)
        
        logger.info(f"Redirecting user {user_id} to Google login")
        return RedirectResponse(url=auth_url)
    
    except Exception as e:
        logger.error(f"Error initiating Google OAuth: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth2 callback
    Stores access and refresh tokens for Google Sheets API
    """
    try:
        # Verify state
        if state not in oauth_states:
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        state_data = oauth_states.pop(state)
        user_id = state_data["user_id"]
        
        # Exchange code for tokens
        google_oauth = GoogleSheetsOAuth()
        token_response = await google_oauth.exchange_code_for_token(code)
        
        # Encrypt tokens before storage
        encrypted_access_token = encrypt_token(token_response["access_token"])
        encrypted_refresh_token = encrypt_token(token_response.get("refresh_token", ""))
        
        # Calculate expiration
        expires_in = token_response.get("expires_in", 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Check if token already exists
        existing_token = db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == "google"
        ).first()
        
        if existing_token:
            # Update existing token
            existing_token.access_token = encrypted_access_token
            existing_token.refresh_token = encrypted_refresh_token
            existing_token.expires_at = expires_at
            existing_token.scopes = token_response.get("scope", "").split()
            existing_token.updated_at = datetime.utcnow()
        else:
            # Create new token entry
            new_token = OAuthToken(
                user_id=user_id,
                provider="google",
                access_token=encrypted_access_token,
                refresh_token=encrypted_refresh_token,
                expires_at=expires_at,
                scopes=token_response.get("scope", "").split(),
                metadata={"token_type": token_response.get("token_type")}
            )
            db.add(new_token)
        
        db.commit()
        
        logger.info(f"Successfully stored Google tokens for user {user_id}")
        
        # Redirect to frontend success page
        frontend_url = settings.CORS_ORIGINS[0]
        return RedirectResponse(url=f"{frontend_url}/integrations/success?provider=google")
    
    except Exception as e:
        logger.error(f"Error in Google OAuth callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# GitHub OAuth2
@router.get("/github/login")
async def github_login(user_id: str, db: Session = Depends(get_db)):
    """
    Initiate GitHub OAuth2 flow
    """
    try:
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        oauth_states[state] = {
            "user_id": user_id,
            "provider": "github",
            "created_at": datetime.utcnow()
        }
        
        # Initialize GitHub OAuth
        github_oauth = GitHubOAuth(
            client_id=settings.GITHUB_CLIENT_ID,
            client_secret=settings.GITHUB_CLIENT_SECRET,
            redirect_uri=settings.GITHUB_REDIRECT_URI,
            scopes=settings.GITHUB_SCOPES
        )
        auth_url = github_oauth.get_authorization_url(state)
        
        logger.info(f"Redirecting user {user_id} to GitHub login")
        return RedirectResponse(url=auth_url)
    
    except Exception as e:
        logger.error(f"Error initiating GitHub OAuth: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/github/callback")
async def github_callback(
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle GitHub OAuth2 callback
    Exchange code for tokens and store securely
    """
    try:
        # Validate state
        if state not in oauth_states:
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        state_data = oauth_states.pop(state)
        user_id = state_data["user_id"]
        
        # Exchange code for tokens
        github_oauth = GitHubOAuth(
            client_id=settings.GITHUB_CLIENT_ID,
            client_secret=settings.GITHUB_CLIENT_SECRET,
            redirect_uri=settings.GITHUB_REDIRECT_URI,
            scopes=settings.GITHUB_SCOPES
        )
        token_response = await github_oauth.exchange_code_for_token(code)
        
        # Encrypt token before storage
        access_token = token_response.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token in GitHub response")
        
        encrypted_access_token = encrypt_token(access_token)
        
        # GitHub tokens don't expire by default
        # Store token type and scope in metadata
        metadata = {
            "token_type": token_response.get("token_type", "bearer"),
            "scope": token_response.get("scope", "")
        }
        
        # Check if token already exists
        existing_token = db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == "github"
        ).first()
        
        if existing_token:
            # Update existing token
            existing_token.access_token = encrypted_access_token
            existing_token.scopes = token_response.get("scope", "").split(",") if token_response.get("scope") else settings.GITHUB_SCOPES
            existing_token.metadata = metadata
            existing_token.updated_at = datetime.utcnow()
        else:
            # Create new token entry
            new_token = OAuthToken(
                user_id=user_id,
                provider="github",
                access_token=encrypted_access_token,
                refresh_token="",  # GitHub doesn't use refresh tokens for standard OAuth
                expires_at=None,  # GitHub tokens don't expire
                scopes=token_response.get("scope", "").split(",") if token_response.get("scope") else settings.GITHUB_SCOPES,
                metadata=metadata
            )
            db.add(new_token)
        
        db.commit()
        
        logger.info(f"Successfully stored GitHub tokens for user {user_id}")
        
        # Redirect to frontend success page
        frontend_url = settings.CORS_ORIGINS[0]
        return RedirectResponse(url=f"{frontend_url}/integrations/success?provider=github")
    
    except Exception as e:
        logger.error(f"Error in GitHub OAuth callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# CloudABIS Biometric Authentication (One-time setup, no OAuth)
@router.post("/cloudabis/enroll")
async def cloudabis_enroll(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Enroll user in CloudABIS biometric system
    This is a one-time setup, not OAuth-based
    """
    try:
        from integrations.cloudabis import CloudABISClient
        
        # Get biometric data from request
        data = await request.json()
        biometric_data = data.get("biometric_data")
        biometric_type = data.get("biometric_type", "FACE")  # FACE, FINGERPRINT, IRIS
        
        if not biometric_data:
            raise HTTPException(status_code=400, detail="Biometric data required")
        
        # Initialize CloudABIS client
        cloudabis = CloudABISClient(
            app_key=settings.CLOUDABIS_APP_KEY,
            secret_key=settings.CLOUDABIS_SECRET_KEY,
            customer_key=settings.CLOUDABIS_CUSTOMER_KEY,
            base_url=settings.CLOUDABIS_BASE_URL,
            engine_name=biometric_type
        )
        
        # Enroll user
        result = await cloudabis.enroll(
            member_id=user_id,
            biometric_data=biometric_data
        )
        
        # Store enrollment status in database
        # (You might want to create a separate table for CloudABIS enrollment)
        metadata = {
            "enrolled": True,
            "biometric_type": biometric_type,
            "enrollment_id": result.get("enrollment_id"),
            "enrolled_at": datetime.utcnow().isoformat()
        }
        
        # Check if enrollment record exists
        existing_token = db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == "cloudabis"
        ).first()
        
        if existing_token:
            # Update existing record
            existing_token.metadata = metadata
            existing_token.updated_at = datetime.utcnow()
        else:
            # Create new record (using OAuthToken table for consistency, though not OAuth)
            new_record = OAuthToken(
                user_id=user_id,
                provider="cloudabis",
                access_token="",  # Not applicable for CloudABIS
                refresh_token="",
                expires_at=None,
                scopes=[],
                metadata=metadata
            )
            db.add(new_record)
        
        db.commit()
        
        logger.info(f"Successfully enrolled user {user_id} in CloudABIS")
        
        return {
            "status": "success",
            "message": "Biometric enrollment successful",
            "enrollment_id": result.get("enrollment_id")
        }
    
    except Exception as e:
        logger.error(f"Error enrolling user in CloudABIS: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cloudabis/verify")
async def cloudabis_verify(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Verify user identity using CloudABIS biometric authentication
    """
    try:
        from integrations.cloudabis import CloudABISClient
        
        # Get biometric data from request
        data = await request.json()
        biometric_data = data.get("biometric_data")
        biometric_type = data.get("biometric_type", "FACE")
        
        if not biometric_data:
            raise HTTPException(status_code=400, detail="Biometric data required")
        
        # Initialize CloudABIS client
        cloudabis = CloudABISClient(
            app_key=settings.CLOUDABIS_APP_KEY,
            secret_key=settings.CLOUDABIS_SECRET_KEY,
            customer_key=settings.CLOUDABIS_CUSTOMER_KEY,
            base_url=settings.CLOUDABIS_BASE_URL,
            engine_name=biometric_type
        )
        
        # Verify user
        result = await cloudabis.verify(
            member_id=user_id,
            biometric_data=biometric_data
        )
        
        logger.info(f"Biometric verification for user {user_id}: {result.get('is_match')}")
        
        return {
            "status": "success",
            "is_match": result.get("is_match", False),
            "confidence_score": result.get("confidence_score", 0),
            "message": "Identity verified" if result.get("is_match") else "Identity verification failed"
        }
    
    except Exception as e:
        logger.error(f"Error verifying user with CloudABIS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

