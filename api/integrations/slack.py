"""
Slack API Integration
Handles OAuth2 and data fetching from Slack
"""
import httpx
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from urllib.parse import urlencode

from config import settings

logger = logging.getLogger(__name__)


class SlackOAuth:
    """Slack OAuth2 handler"""
    
    def __init__(self):
        self.client_id = settings.SLACK_CLIENT_ID
        self.client_secret = settings.SLACK_CLIENT_SECRET
        self.redirect_uri = settings.get_redirect_uri("slack")
        self.scopes = settings.SLACK_SCOPES
        self.authorize_endpoint = "https://slack.com/oauth/v2/authorize"
        self.token_endpoint = "https://slack.com/api/oauth.v2.access"
    
    def get_authorization_url(self, state: str) -> str:
        """
        Generate OAuth2 authorization URL for Slack
        """
        params = {
            "client_id": self.client_id,
            "scope": ",".join(self.scopes),
            "redirect_uri": self.redirect_uri,
            "state": state,
            "user_scope": ""  # Add user scopes if needed
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
                        "redirect_uri": self.redirect_uri
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                if not data.get("ok"):
                    raise Exception(f"Slack OAuth error: {data.get('error')}")
                
                return data
        
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            raise


class SlackAPI:
    """Slack API data fetcher"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://slack.com/api"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Helper method to make API requests"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{endpoint}",
                    headers=self.headers,
                    params=params or {}
                )
                response.raise_for_status()
                data = response.json()
                
                if not data.get("ok"):
                    raise Exception(f"Slack API error: {data.get('error')}")
                
                return data
        except Exception as e:
            logger.error(f"Error making Slack API request to {endpoint}: {e}")
            raise
    
    async def get_user_info(self) -> Dict:
        """Get authenticated user information"""
        try:
            # For bot tokens, get auth.test to identify the bot/user
            data = await self._make_request("auth.test")
            return {
                "id": data.get("user_id"),
                "team_id": data.get("team_id"),
                "team": data.get("team"),
                "user": data.get("user")
            }
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            raise
    
    async def get_conversations_list(self, types: str = "public_channel,private_channel") -> List[Dict]:
        """
        Get list of channels/conversations
        types: comma-separated list of conversation types
        """
        all_channels = []
        cursor = None
        
        while True:
            params = {
                "types": types,
                "limit": 200
            }
            if cursor:
                params["cursor"] = cursor
            
            data = await self._make_request("conversations.list", params)
            channels = data.get("channels", [])
            all_channels.extend(channels)
            
            cursor = data.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        
        return all_channels
    
    async def get_conversation_history(
        self,
        channel_id: str,
        oldest: Optional[float] = None,
        latest: Optional[float] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Get message history from a channel
        oldest/latest: Unix timestamps
        """
        all_messages = []
        cursor = None
        
        while True:
            params = {
                "channel": channel_id,
                "limit": min(limit, 1000)
            }
            if oldest:
                params["oldest"] = oldest
            if latest:
                params["latest"] = latest
            if cursor:
                params["cursor"] = cursor
            
            data = await self._make_request("conversations.history", params)
            messages = data.get("messages", [])
            all_messages.extend(messages)
            
            if len(all_messages) >= limit:
                break
            
            cursor = data.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        
        return all_messages[:limit]
    
    async def get_user_messages(
        self,
        start_date: datetime,
        end_date: datetime,
        channel_limit: int = 50
    ) -> List[Dict]:
        """
        Get all messages sent by the authenticated user across channels
        """
        # Convert dates to Unix timestamps
        oldest = start_date.timestamp()
        latest = end_date.timestamp()
        
        # Get all channels user is in
        channels = await self.get_conversations_list()
        
        all_user_messages = []
        
        # Get the bot's user_id from auth.test
        auth_data = await self._make_request("auth.test")
        user_id = auth_data.get("user_id")
        
        # Limit channels to process
        for channel in channels[:channel_limit]:
            try:
                channel_id = channel["id"]
                messages = await self.get_conversation_history(
                    channel_id,
                    oldest=oldest,
                    latest=latest,
                    limit=1000
                )
                
                # Filter messages by user
                user_messages = [
                    {
                        **msg,
                        "channel_id": channel_id,
                        "channel_name": channel.get("name")
                    }
                    for msg in messages
                    if msg.get("user") == user_id
                ]
                all_user_messages.extend(user_messages)
                
            except Exception as e:
                logger.warning(f"Error fetching messages from channel {channel.get('name')}: {e}")
                continue
        
        return all_user_messages
    
    async def get_reactions(
        self,
        start_date: datetime,
        end_date: datetime,
        channel_limit: int = 50
    ) -> List[Dict]:
        """
        Get emoji reactions from messages (sentiment proxy)
        """
        oldest = start_date.timestamp()
        latest = end_date.timestamp()
        
        channels = await self.get_conversations_list()
        all_reactions = []
        
        for channel in channels[:channel_limit]:
            try:
                channel_id = channel["id"]
                messages = await self.get_conversation_history(
                    channel_id,
                    oldest=oldest,
                    latest=latest,
                    limit=500
                )
                
                for msg in messages:
                    if "reactions" in msg:
                        for reaction in msg["reactions"]:
                            all_reactions.append({
                                "channel_id": channel_id,
                                "channel_name": channel.get("name"),
                                "emoji": reaction.get("name"),
                                "count": reaction.get("count"),
                                "timestamp": msg.get("ts"),
                                "message_user": msg.get("user")
                            })
            
            except Exception as e:
                logger.warning(f"Error fetching reactions from channel {channel.get('name')}: {e}")
                continue
        
        return all_reactions
    
    async def get_user_stats(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Get comprehensive user activity statistics
        """
        messages = await self.get_user_messages(start_date, end_date)
        
        # Calculate statistics
        total_messages = len(messages)
        
        # Messages by hour
        messages_by_hour = {}
        after_hours_count = 0
        
        for msg in messages:
            ts = float(msg.get("ts", 0))
            dt = datetime.fromtimestamp(ts)
            hour = dt.hour
            
            messages_by_hour[hour] = messages_by_hour.get(hour, 0) + 1
            
            # After hours: before 8am or after 6pm
            if hour < 8 or hour >= 18:
                after_hours_count += 1
        
        # Channel diversity
        unique_channels = len(set(msg.get("channel_id") for msg in messages))
        
        # Response time analysis (simplified)
        # In a real implementation, you'd need to track thread replies
        
        return {
            "total_messages": total_messages,
            "unique_channels": unique_channels,
            "messages_by_hour": messages_by_hour,
            "after_hours_count": after_hours_count,
            "after_hours_ratio": after_hours_count / total_messages if total_messages > 0 else 0,
            "avg_messages_per_day": total_messages / max((end_date - start_date).days, 1)
        }
    
    async def get_team_info(self) -> Dict:
        """Get information about the Slack workspace"""
        return await self._make_request("team.info")
