"""
Microsoft Graph API Integration
Handles OAuth2 and data fetching from Microsoft 365
"""
import httpx
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from urllib.parse import urlencode

from config import settings

logger = logging.getLogger(__name__)


class MicrosoftGraphOAuth:
    """Microsoft Graph OAuth2 handler"""
    
    def __init__(self):
        self.client_id = settings.MICROSOFT_CLIENT_ID
        self.client_secret = settings.MICROSOFT_CLIENT_SECRET
        self.tenant_id = settings.MICROSOFT_TENANT_ID
        self.redirect_uri = settings.MICROSOFT_REDIRECT_URI
        self.scopes = settings.MICROSOFT_SCOPES
        self.authority = f"{settings.MICROSOFT_AUTHORITY}/{self.tenant_id}"
        self.token_endpoint = f"{self.authority}/oauth2/v2.0/token"
        self.authorize_endpoint = f"{self.authority}/oauth2/v2.0/authorize"
    
    def get_authorization_url(self, state: str) -> str:
        """
        Generate OAuth2 authorization URL
        """
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "state": state,
            "response_mode": "query"
        }
        
        auth_url = f"{self.authorize_endpoint}?{urlencode(params)}"
        return auth_url
    
    async def exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange authorization code for access token
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_endpoint,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "redirect_uri": self.redirect_uri,
                        "grant_type": "authorization_code",
                        "scope": " ".join(self.scopes)
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                return response.json()
        
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            raise
    
    async def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Refresh an expired access token
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_endpoint,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": refresh_token,
                        "grant_type": "refresh_token",
                        "scope": " ".join(self.scopes)
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                return response.json()
        
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise


class MicrosoftGraphAPI:
    """Microsoft Graph API data fetcher"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = settings.MICROSOFT_GRAPH_ENDPOINT
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    async def get_user_profile(self) -> Dict:
        """Get user profile information"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/me",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching user profile: {e}")
            raise
    
    async def get_calendar_events(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Fetch calendar events for analysis
        """
        try:
            # Format dates for Graph API
            start_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
            end_str = end_date.strftime("%Y-%m-%dT%H:%M:%S")
            
            params = {
                "$filter": f"start/dateTime ge '{start_str}' and end/dateTime le '{end_str}'",
                "$select": "subject,start,end,attendees,isAllDay,organizer,location,showAs",
                "$orderby": "start/dateTime",
                "$top": 1000
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/me/calendar/events",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                return data.get("value", [])
        
        except Exception as e:
            logger.error(f"Error fetching calendar events: {e}")
            raise
    
    async def get_emails(
        self,
        start_date: datetime,
        end_date: datetime,
        folder: str = "inbox"
    ) -> List[Dict]:
        """
        Fetch email metadata (no content for privacy)
        """
        try:
            start_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            params = {
                "$filter": f"receivedDateTime ge {start_str} and receivedDateTime le {end_str}",
                "$select": "receivedDateTime,sentDateTime,from,toRecipients,ccRecipients,hasAttachments,importance,isRead",
                "$orderby": "receivedDateTime desc",
                "$top": 1000
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/me/mailFolders/{folder}/messages",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                return data.get("value", [])
        
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            raise
    
    async def get_teams_messages(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Fetch Teams chat activity
        """
        try:
            # Get user's chats
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/me/chats",
                    headers=self.headers,
                    params={"$expand": "members"}
                )
                response.raise_for_status()
                chats = response.json().get("value", [])
                
                all_messages = []
                
                # Get messages from each chat
                for chat in chats[:50]:  # Limit to recent chats
                    chat_id = chat["id"]
                    messages_response = await client.get(
                        f"{self.base_url}/chats/{chat_id}/messages",
                        headers=self.headers,
                        params={
                            "$top": 100,
                            "$orderby": "createdDateTime desc"
                        }
                    )
                    
                    if messages_response.status_code == 200:
                        messages = messages_response.json().get("value", [])
                        all_messages.extend(messages)
                
                return all_messages
        
        except Exception as e:
            logger.error(f"Error fetching Teams messages: {e}")
            raise
    
    async def get_presence(self) -> Dict:
        """Get user presence/availability status"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/me/presence",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching presence: {e}")
            raise
