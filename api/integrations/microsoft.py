"""
Microsoft Graph OAuth Integration
"""
import msal
import httpx
from config import settings
import logging

logger = logging.getLogger(__name__)


class MicrosoftGraphOAuth:
    """Microsoft Graph OAuth handler"""
    
    def __init__(self):
        self.client_id = settings.MICROSOFT_CLIENT_ID
        self.client_secret = settings.MICROSOFT_CLIENT_SECRET
        self.tenant_id = settings.MICROSOFT_TENANT_ID
        self.redirect_uri = settings.get_redirect_uri("microsoft")
        self.scopes = settings.MICROSOFT_SCOPES
        
        self.authority = f"{settings.MICROSOFT_AUTHORITY}/{self.tenant_id}"
        
    def get_authorization_url(self, state: str) -> str:
        """Get Microsoft OAuth authorization URL"""
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret
        )
        
        auth_url = app.get_authorization_request_url(
            scopes=self.scopes,
            state=state,
            redirect_uri=self.redirect_uri
        )
        
        return auth_url
    
    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token"""
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret
        )
        
        result = app.acquire_token_by_authorization_code(
            code,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        if "access_token" in result:
            return {
                "access_token": result["access_token"],
                "refresh_token": result.get("refresh_token"),
                "expires_in": result.get("expires_in", 3600),
                "token_type": result.get("token_type", "Bearer")
            }
        else:
            raise Exception(f"Failed to get token: {result.get('error_description', 'Unknown error')}")
    
    async def get_user_info(self, access_token: str) -> dict:
        """Get user information from Microsoft Graph"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.MICROSOFT_GRAPH_ENDPOINT}/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_user_calendar(self, access_token: str, days: int = 7) -> dict:
        """Get user's calendar events"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.MICROSOFT_GRAPH_ENDPOINT}/me/calendar/events",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"$top": 100}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_user_emails(self, access_token: str, count: int = 50) -> dict:
        """Get user's emails"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.MICROSOFT_GRAPH_ENDPOINT}/me/messages",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"$top": count}
            )
            response.raise_for_status()
            return response.json()
