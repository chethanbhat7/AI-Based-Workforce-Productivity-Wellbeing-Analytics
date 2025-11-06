"""
OAuth2 Authentication Router
Handles OAuth flows for all providers
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import secrets

from database import get_db, User, OAuthToken
from config import settings
from integrations.microsoft_graph import MicrosoftGraphOAuth
from utils.encryption import encrypt_token, decrypt_token

logger = logging.getLogger(__name__)

router = APIRouter()

# OAuth state store (in production, use Redis)
oauth_states = {}


# Microsoft Graph OAuth2
@router.get("/microsoft/login")
async def microsoft_login(user_id: str, db: Session = Depends(get_db)):
    """
    Initiate Microsoft OAuth2 flow
    """
    try:
        # Generate state for CSRF protection
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
        # Validate state
        if state not in oauth_states:
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
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
        
        # Redirect to frontend success page
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
