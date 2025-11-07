"""
OAuth2 Authentication Router - PRODUCTION READY
Handles OAuth flows for all providers with real OAuth support
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import secrets

from database import get_db, OAuthToken
from config import settings
from integrations.google_sheets import GoogleSheetsOAuth
from integrations.github import GitHubOAuth
from utils.encryption import encrypt_token

logger = logging.getLogger(__name__)

router = APIRouter()

# TEST MODE - Set to False for real OAuth, True for testing
TEST_MODE = False

# OAuth state storage (use Redis in production)
oauth_states = {}


def get_success_html(provider: str):
    """HTML response to close popup and notify parent"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Authorization Successful</title></head>
    <body>
        <h2>✅ {provider.capitalize()} Connected!</h2>
        <p>This window will close automatically...</p>
        <script>
            if (window.opener) {{
                window.opener.postMessage({{
                    type: 'oauth_success',
                    service: '{provider}'
                }}, '*');
                setTimeout(() => window.close(), 1000);
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
        <script>
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


def create_mock_token(db: Session, user_id: str, provider: str):
    """Create mock OAuth token for testing"""
    existing = db.query(OAuthToken).filter(
        OAuthToken.user_id == user_id,
        OAuthToken.provider == provider
    ).first()
    
    if existing:
        existing.updated_at = datetime.utcnow()
    else:
        new_token = OAuthToken(
            user_id=user_id,
            provider=provider,
            access_token=f"TEST_{provider.upper()}_ACCESS_TOKEN",
            refresh_token=f"TEST_{provider.upper()}_REFRESH_TOKEN",
            expires_at=datetime.utcnow() + timedelta(days=30),
            scopes=["test_scope"]
        )
        db.add(new_token)
    
    db.commit()


# Microsoft Graph OAuth
@router.get("/microsoft/login")
async def microsoft_login(user_id: str, state: str = None, db: Session = Depends(get_db)):
    """Initiate Microsoft OAuth2 flow"""
    if TEST_MODE:
        logger.info(f"TEST MODE: Microsoft OAuth for user {user_id}")
        return RedirectResponse(url=f"/api/auth/microsoft/callback?code=TEST&state={state or user_id}")
    
    try:
        # Generate state for CSRF protection
        csrf_state = secrets.token_urlsafe(32)
        oauth_states[csrf_state] = {
            "user_id": user_id,
            "original_state": state,
            "provider": "microsoft",
            "created_at": datetime.utcnow()
        }
        
        from integrations.microsoft_graph import MicrosoftGraphOAuth
        ms_oauth = MicrosoftGraphOAuth()
        auth_url = ms_oauth.get_authorization_url(csrf_state)
        
        logger.info(f"Redirecting user {user_id} to Microsoft OAuth")
        return RedirectResponse(url=auth_url)
    
    except Exception as e:
        logger.error(f"Microsoft OAuth initiation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/microsoft/callback")
async def microsoft_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle Microsoft OAuth callback"""
    try:
        if TEST_MODE:
            create_mock_token(db, state, "microsoft")
            logger.info(f"TEST: Microsoft token created for user {state}")
            return HTMLResponse(content=get_success_html("microsoft"))
        
        # Validate state
        if state not in oauth_states:
            return HTMLResponse(content=get_error_html("microsoft", "Invalid state - session expired"))
        
        state_data = oauth_states.pop(state)
        user_id = state_data["user_id"]
        
        # Exchange code for tokens
        from integrations.microsoft_graph import MicrosoftGraphOAuth
        ms_oauth = MicrosoftGraphOAuth()
        token_response = await ms_oauth.exchange_code_for_token(code)
        
        # Encrypt and store tokens
        encrypted_access = encrypt_token(token_response["access_token"])
        encrypted_refresh = encrypt_token(token_response.get("refresh_token", ""))
        
        expires_at = datetime.utcnow() + timedelta(seconds=token_response.get("expires_in", 3600))
        
        # Store in database
        existing = db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == "microsoft"
        ).first()
        
        if existing:
            existing.access_token = encrypted_access
            existing.refresh_token = encrypted_refresh
            existing.expires_at = expires_at
            existing.updated_at = datetime.utcnow()
        else:
            new_token = OAuthToken(
                user_id=user_id,
                provider="microsoft",
                access_token=encrypted_access,
                refresh_token=encrypted_refresh,
                expires_at=expires_at,
                scopes=settings.MICROSOFT_SCOPES
            )
            db.add(new_token)
        
        db.commit()
        logger.info(f"Microsoft token stored for user {user_id}")
        return HTMLResponse(content=get_success_html("microsoft"))
    
    except Exception as e:
        logger.error(f"Microsoft callback error: {e}")
        return HTMLResponse(content=get_error_html("microsoft", str(e)))


# Slack OAuth
@router.get("/slack/login")
async def slack_login(user_id: str, state: str = None, db: Session = Depends(get_db)):
    """Initiate Slack OAuth2 flow"""
    if TEST_MODE:
        logger.info(f"TEST MODE: Slack OAuth for user {user_id}")
        return RedirectResponse(url=f"/api/auth/slack/callback?code=TEST&state={state or user_id}")
    
    try:
        # Generate state for CSRF protection
        csrf_state = secrets.token_urlsafe(32)
        oauth_states[csrf_state] = {
            "user_id": user_id,
            "original_state": state,
            "provider": "slack",
            "created_at": datetime.utcnow()
        }
        
        from integrations.slack import SlackOAuth
        slack_oauth = SlackOAuth()
        auth_url = slack_oauth.get_authorization_url(csrf_state)
        
        logger.info(f"Redirecting user {user_id} to Slack OAuth")
        return RedirectResponse(url=auth_url)
    
    except Exception as e:
        logger.error(f"Slack OAuth initiation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/slack/callback")
async def slack_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle Slack OAuth callback"""
    try:
        if TEST_MODE:
            create_mock_token(db, state, "slack")
            logger.info(f"TEST: Slack token created for user {state}")
            return HTMLResponse(content=get_success_html("slack"))
        
        # Validate state
        if state not in oauth_states:
            return HTMLResponse(content=get_error_html("slack", "Invalid state - session expired"))
        
        state_data = oauth_states.pop(state)
        user_id = state_data["user_id"]
        
        # Exchange code for tokens
        from integrations.slack import SlackOAuth
        slack_oauth = SlackOAuth()
        token_response = await slack_oauth.exchange_code_for_token(code)
        
        # Encrypt and store tokens
        encrypted_access = encrypt_token(token_response["access_token"])
        
        # Slack tokens don't expire
        expires_at = datetime.utcnow() + timedelta(days=365)
        
        # Store in database
        existing = db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == "slack"
        ).first()
        
        if existing:
            existing.access_token = encrypted_access
            existing.updated_at = datetime.utcnow()
        else:
            new_token = OAuthToken(
                user_id=user_id,
                provider="slack",
                access_token=encrypted_access,
                refresh_token="",
                expires_at=expires_at,
                scopes=settings.SLACK_SCOPES
            )
            db.add(new_token)
        
        db.commit()
        logger.info(f"Slack token stored for user {user_id}")
        return HTMLResponse(content=get_success_html("slack"))
    
    except Exception as e:
        logger.error(f"Slack callback error: {e}")
        return HTMLResponse(content=get_error_html("slack", str(e)))


# Google Sheets OAuth
@router.get("/google/login")
async def google_login(user_id: str, state: str = None, db: Session = Depends(get_db)):
    """Initiate Google OAuth2 flow"""
    if TEST_MODE:
        logger.info(f"TEST MODE: Google OAuth for user {user_id}")
        return RedirectResponse(url=f"/api/auth/google/callback?code=TEST&state={state or user_id}")
    
    try:
        # Generate state for CSRF protection
        csrf_state = secrets.token_urlsafe(32)
        oauth_states[csrf_state] = {
            "user_id": user_id,
            "original_state": state,
            "provider": "google",
            "created_at": datetime.utcnow()
        }
        
        # Initialize Google OAuth
        google_oauth = GoogleSheetsOAuth()
        auth_url = google_oauth.get_authorization_url(csrf_state)
        
        logger.info(f"Redirecting user {user_id} to Google OAuth URL: {auth_url}")
        return RedirectResponse(url=auth_url)
    
    except Exception as e:
        logger.error(f"Google OAuth initiation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/google/callback")
async def google_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        if TEST_MODE:
            create_mock_token(db, state, "google-sheets")
            logger.info(f"TEST: Google token created for user {state}")
            return HTMLResponse(content=get_success_html("google"))
        
        # Validate state
        if state not in oauth_states:
            return HTMLResponse(content=get_error_html("google", "Invalid state - session expired"))
        
        state_data = oauth_states.pop(state)
        user_id = state_data["user_id"]
        
        # Exchange code for tokens
        google_oauth = GoogleSheetsOAuth()
        token_response = await google_oauth.exchange_code_for_token(code)
        
        # Encrypt and store tokens
        encrypted_access = encrypt_token(token_response["access_token"])
        encrypted_refresh = encrypt_token(token_response.get("refresh_token", ""))
        
        expires_at = datetime.utcnow() + timedelta(seconds=token_response.get("expires_in", 3600))
        
        # Store in database
        existing = db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == "google-sheets"
        ).first()
        
        if existing:
            existing.access_token = encrypted_access
            existing.refresh_token = encrypted_refresh
            existing.expires_at = expires_at
            existing.updated_at = datetime.utcnow()
        else:
            new_token = OAuthToken(
                user_id=user_id,
                provider="google-sheets",
                access_token=encrypted_access,
                refresh_token=encrypted_refresh,
                expires_at=expires_at,
                scopes=["spreadsheets", "drive.file"]
            )
            db.add(new_token)
        
        db.commit()
        logger.info(f"Google Sheets token stored for user {user_id}")
        return HTMLResponse(content=get_success_html("google"))
    
    except Exception as e:
        logger.error(f"Google callback error: {e}")
        return HTMLResponse(content=get_error_html("google", str(e)))


# Jira OAuth
@router.get("/jira/login")
async def jira_login(user_id: str, state: str = None, db: Session = Depends(get_db)):
    """Initiate Jira OAuth2 flow"""
    if TEST_MODE:
        logger.info(f"TEST MODE: Jira OAuth for user {user_id}")
        return RedirectResponse(url=f"/api/auth/jira/callback?code=TEST&state={state or user_id}")
    
    try:
        # Generate state for CSRF protection
        csrf_state = secrets.token_urlsafe(32)
        oauth_states[csrf_state] = {
            "user_id": user_id,
            "original_state": state,
            "provider": "jira",
            "created_at": datetime.utcnow()
        }
        
        from integrations.jira import JiraOAuth
        jira_oauth = JiraOAuth(
            client_id=settings.JIRA_CLIENT_ID,
            client_secret=settings.JIRA_CLIENT_SECRET,
            redirect_uri=settings.JIRA_REDIRECT_URI,
            scopes=["read:jira-work", "read:jira-user"]
        )
        auth_url = jira_oauth.get_authorization_url(csrf_state)
        
        logger.info(f"Redirecting user {user_id} to Jira OAuth")
        return RedirectResponse(url=auth_url)
    
    except Exception as e:
        logger.error(f"Jira OAuth initiation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jira/callback")
async def jira_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle Jira OAuth callback"""
    try:
        if TEST_MODE:
            create_mock_token(db, state, "jira")
            logger.info(f"TEST: Jira token created for user {state}")
            return HTMLResponse(content=get_success_html("jira"))
        
        # Validate state
        if state not in oauth_states:
            return HTMLResponse(content=get_error_html("jira", "Invalid state - session expired"))
        
        state_data = oauth_states.pop(state)
        user_id = state_data["user_id"]
        
        # Exchange code for tokens
        from integrations.jira import JiraOAuth
        jira_oauth = JiraOAuth(
            client_id=settings.JIRA_CLIENT_ID,
            client_secret=settings.JIRA_CLIENT_SECRET,
            redirect_uri=settings.JIRA_REDIRECT_URI,
            scopes=["read:jira-work", "read:jira-user"]
        )
        token_response = await jira_oauth.exchange_code_for_token(code)
        
        # Encrypt and store tokens
        encrypted_access = encrypt_token(token_response["access_token"])
        encrypted_refresh = encrypt_token(token_response.get("refresh_token", ""))
        
        expires_at = datetime.utcnow() + timedelta(seconds=token_response.get("expires_in", 3600))
        
        # Store in database
        existing = db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == "jira"
        ).first()
        
        if existing:
            existing.access_token = encrypted_access
            existing.refresh_token = encrypted_refresh
            existing.expires_at = expires_at
            existing.updated_at = datetime.utcnow()
        else:
            new_token = OAuthToken(
                user_id=user_id,
                provider="jira",
                access_token=encrypted_access,
                refresh_token=encrypted_refresh,
                expires_at=expires_at,
                scopes=["read:jira-work", "read:jira-user"]
            )
            db.add(new_token)
        
        db.commit()
        logger.info(f"Jira token stored for user {user_id}")
        return HTMLResponse(content=get_success_html("jira"))
    
    except Exception as e:
        logger.error(f"Jira callback error: {e}")
        return HTMLResponse(content=get_error_html("jira", str(e)))


# Asana OAuth
@router.get("/asana/login")
async def asana_login(user_id: str, state: str = None, db: Session = Depends(get_db)):
    """Initiate Asana OAuth2 flow"""
    if TEST_MODE:
        logger.info(f"TEST MODE: Asana OAuth for user {user_id}")
        return RedirectResponse(url=f"/api/auth/asana/callback?code=TEST&state={state or user_id}")
    
    try:
        # Generate state for CSRF protection
        csrf_state = secrets.token_urlsafe(32)
        oauth_states[csrf_state] = {
            "user_id": user_id,
            "original_state": state,
            "provider": "asana",
            "created_at": datetime.utcnow()
        }
        
        from integrations.asana import AsanaOAuth
        asana_oauth = AsanaOAuth(
            client_id=settings.ASANA_CLIENT_ID,
            client_secret=settings.ASANA_CLIENT_SECRET,
            redirect_uri=settings.ASANA_REDIRECT_URI
        )
        auth_url = asana_oauth.get_authorization_url(csrf_state)
        
        logger.info(f"Redirecting user {user_id} to Asana OAuth")
        return RedirectResponse(url=auth_url)
    
    except Exception as e:
        logger.error(f"Asana OAuth initiation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/asana/callback")
async def asana_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle Asana OAuth callback"""
    try:
        if TEST_MODE:
            create_mock_token(db, state, "asana")
            logger.info(f"TEST: Asana token created for user {state}")
            return HTMLResponse(content=get_success_html("asana"))
        
        # Validate state
        if state not in oauth_states:
            return HTMLResponse(content=get_error_html("asana", "Invalid state - session expired"))
        
        state_data = oauth_states.pop(state)
        user_id = state_data["user_id"]
        
        # Exchange code for tokens
        from integrations.asana import AsanaOAuth
        asana_oauth = AsanaOAuth(
            client_id=settings.ASANA_CLIENT_ID,
            client_secret=settings.ASANA_CLIENT_SECRET,
            redirect_uri=settings.ASANA_REDIRECT_URI
        )
        token_response = await asana_oauth.exchange_code_for_token(code)
        
        # Encrypt and store tokens
        encrypted_access = encrypt_token(token_response["access_token"])
        encrypted_refresh = encrypt_token(token_response.get("refresh_token", ""))
        
        expires_at = datetime.utcnow() + timedelta(seconds=token_response.get("expires_in", 3600))
        
        # Store in database
        existing = db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == "asana"
        ).first()
        
        if existing:
            existing.access_token = encrypted_access
            existing.refresh_token = encrypted_refresh
            existing.expires_at = expires_at
            existing.updated_at = datetime.utcnow()
        else:
            new_token = OAuthToken(
                user_id=user_id,
                provider="asana",
                access_token=encrypted_access,
                refresh_token=encrypted_refresh,
                expires_at=expires_at,
                scopes=["default"]
            )
            db.add(new_token)
        
        db.commit()
        logger.info(f"Asana token stored for user {user_id}")
        return HTMLResponse(content=get_success_html("asana"))
    
    except Exception as e:
        logger.error(f"Asana callback error: {e}")
        return HTMLResponse(content=get_error_html("asana", str(e)))


# GitHub OAuth
@router.get("/github/login")
async def github_login(user_id: str, state: str = None, db: Session = Depends(get_db)):
    """Initiate GitHub OAuth2 flow"""
    if TEST_MODE:
        logger.info(f"TEST MODE: GitHub OAuth for user {user_id}")
        return RedirectResponse(url=f"/api/auth/github/callback?code=TEST&state={state or user_id}")
    
    try:
        # Generate state for CSRF protection
        csrf_state = secrets.token_urlsafe(32)
        oauth_states[csrf_state] = {
            "user_id": user_id,
            "original_state": state,
            "provider": "github",
            "created_at": datetime.utcnow()
        }
        
        # Initialize GitHub OAuth
        github_oauth = GitHubOAuth()
        auth_url = github_oauth.get_authorization_url(csrf_state)
        
        logger.info(f"Redirecting user {user_id} to GitHub OAuth")
        return RedirectResponse(url=auth_url)
    
    except Exception as e:
        logger.error(f"GitHub OAuth initiation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/github/callback")
async def github_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle GitHub OAuth callback"""
    try:
        if TEST_MODE:
            create_mock_token(db, state, "github")
            logger.info(f"TEST: GitHub token created for user {state}")
            return HTMLResponse(content=get_success_html("github"))
        
        # Validate state
        if state not in oauth_states:
            return HTMLResponse(content=get_error_html("github", "Invalid state - session expired"))
        
        state_data = oauth_states.pop(state)
        user_id = state_data["user_id"]
        
        # Exchange code for tokens
        github_oauth = GitHubOAuth()
        token_response = await github_oauth.exchange_code_for_token(code)
        
        # Encrypt and store token
        encrypted_access = encrypt_token(token_response["access_token"])
        
        # GitHub tokens don't expire, but set far future date
        expires_at = datetime.utcnow() + timedelta(days=365)
        
        # Store in database
        existing = db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == "github"
        ).first()
        
        if existing:
            existing.access_token = encrypted_access
            existing.updated_at = datetime.utcnow()
        else:
            new_token = OAuthToken(
                user_id=user_id,
                provider="github",
                access_token=encrypted_access,
                refresh_token="",
                expires_at=expires_at,
                scopes=settings.GITHUB_SCOPES
            )
            db.add(new_token)
        
        db.commit()
        logger.info(f"GitHub token stored for user {user_id}")
        return HTMLResponse(content=get_success_html("github"))
    
    except Exception as e:
        logger.error(f"GitHub callback error: {e}")
        return HTMLResponse(content=get_error_html("github", str(e)))


# CloudABIS (non-OAuth, just mock for completeness)
@router.post("/cloudabis/enroll")
async def cloudabis_enroll(user_id: str, db: Session = Depends(get_db)):
    """Enroll biometric"""
    if TEST_MODE:
        create_mock_token(db, user_id, "cloudabis")
        return {"status": "success", "message": "Biometric enrolled (TEST MODE)"}
    
    raise HTTPException(status_code=501, detail="CloudABIS not configured")


@router.post("/cloudabis/verify")
async def cloudabis_verify(user_id: str, db: Session = Depends(get_db)):
    """Verify biometric"""
    if TEST_MODE:
        return {"status": "success", "verified": True, "message": "TEST MODE"}
    
    raise HTTPException(status_code=501, detail="CloudABIS not configured")


# Status endpoint
@router.get("/status/{user_id}")
async def get_integration_status(user_id: str, db: Session = Depends(get_db)):
    """Get user's integration status"""
    tokens = db.query(OAuthToken).filter(OAuthToken.user_id == user_id).all()
    
    return {
        "user_id": user_id,
        "integrations": [
            {
                "provider": token.provider,
                "connected": True,
                "expires_at": token.expires_at.isoformat() if token.expires_at else None
            }
            for token in tokens
        ]
    }
