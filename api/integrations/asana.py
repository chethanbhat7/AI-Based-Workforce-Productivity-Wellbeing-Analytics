"""
Asana OAuth2 and API integration for workforce wellbeing analysis
Supports Asana workspace and task management data
"""

import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urlencode
import logging

logger = logging.getLogger(__name__)


class AsanaOAuth:
    """Handle Asana OAuth 2.0 authentication"""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://app.asana.com/-/oauth_authorize"
        self.token_url = "https://app.asana.com/-/oauth_token"
    
    def get_authorization_url(self, state: str) -> str:
        """Generate OAuth2 authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": self.redirect_uri
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.text}")
                raise Exception(f"Failed to exchange code for token: {response.text}")
            
            return response.json()
    
    async def refresh_access_token(self, refresh_token: str) -> Dict:
        """Refresh the access token using refresh token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": refresh_token
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                logger.error(f"Token refresh failed: {response.text}")
                raise Exception(f"Failed to refresh token: {response.text}")
            
            return response.json()


class AsanaAPI:
    """Handle Asana API calls for data extraction"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://app.asana.com/api/1.0"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Asana API"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.base_url}/{endpoint}"
            response = await client.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                logger.error(f"Asana API request failed: {response.status_code} - {response.text}")
                raise Exception(f"Asana API error: {response.status_code}")
            
            data = response.json()
            return data.get("data", {})
    
    async def get_current_user(self) -> Dict:
        """Get current authenticated user information"""
        try:
            data = await self._make_request("users/me")
            return {
                "gid": data.get("gid"),
                "name": data.get("name"),
                "email": data.get("email"),
                "workspaces": data.get("workspaces", [])
            }
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            raise
    
    async def get_workspaces(self) -> List[Dict]:
        """Get all workspaces the user has access to"""
        try:
            data = await self._make_request("workspaces")
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Error getting workspaces: {e}")
            raise
    
    async def get_user_tasks(
        self,
        user_gid: str,
        workspace_gid: str,
        completed_since: Optional[datetime] = None,
        modified_since: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get tasks assigned to a user in a workspace
        Returns tasks with key fields for workload analysis
        """
        try:
            params = {
                "assignee": user_gid,
                "workspace": workspace_gid,
                "opt_fields": "gid,name,completed,completed_at,created_at,modified_at,due_on,due_at,assignee,assignee_status,num_subtasks,parent,projects,tags,memberships,notes"
            }
            
            if completed_since:
                params["completed_since"] = completed_since.isoformat()
            if modified_since:
                params["modified_since"] = modified_since.isoformat()
            
            data = await self._make_request("tasks", params)
            tasks = data if isinstance(data, list) else []
            
            # Enrich each task with additional details
            enriched_tasks = []
            for task in tasks[:100]:  # Limit to avoid rate limits
                try:
                    task_detail = await self._make_request(f"tasks/{task['gid']}")
                    enriched_tasks.append({
                        "gid": task_detail.get("gid"),
                        "name": task_detail.get("name"),
                        "completed": task_detail.get("completed", False),
                        "completed_at": task_detail.get("completed_at"),
                        "created_at": task_detail.get("created_at"),
                        "modified_at": task_detail.get("modified_at"),
                        "due_on": task_detail.get("due_on"),
                        "due_at": task_detail.get("due_at"),
                        "assignee_status": task_detail.get("assignee_status"),
                        "num_subtasks": task_detail.get("num_subtasks", 0),
                        "projects": [p.get("gid") for p in task_detail.get("projects", [])],
                        "tags": [t.get("gid") for t in task_detail.get("tags", [])],
                        "notes": task_detail.get("notes", ""),
                        "parent": task_detail.get("parent", {}).get("gid") if task_detail.get("parent") else None
                    })
                except Exception as e:
                    logger.warning(f"Error fetching task details for {task['gid']}: {e}")
                    continue
            
            return enriched_tasks
        
        except Exception as e:
            logger.error(f"Error getting user tasks: {e}")
            raise
    
    async def get_projects(self, workspace_gid: str) -> List[Dict]:
        """Get all projects in a workspace"""
        try:
            params = {
                "workspace": workspace_gid,
                "opt_fields": "gid,name,created_at,modified_at,owner,team,public,archived"
            }
            
            data = await self._make_request("projects", params)
            return data if isinstance(data, list) else []
        
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            raise
    
    async def get_task_stories(self, task_gid: str) -> List[Dict]:
        """
        Get stories (comments, status changes) for a task
        Useful for collaboration analysis
        """
        try:
            data = await self._make_request(f"tasks/{task_gid}/stories")
            return data if isinstance(data, list) else []
        
        except Exception as e:
            logger.error(f"Error getting task stories: {e}")
            raise
    
    async def get_user_stats(
        self,
        user_gid: str,
        workspace_gid: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Calculate comprehensive workload statistics for a user
        """
        try:
            # Get tasks modified in the date range
            tasks = await self.get_user_tasks(
                user_gid,
                workspace_gid,
                modified_since=start_date
            )
            
            # Filter tasks by date range
            filtered_tasks = []
            for task in tasks:
                modified_at = datetime.fromisoformat(task["modified_at"].replace("Z", "+00:00"))
                if start_date <= modified_at <= end_date:
                    filtered_tasks.append(task)
            
            # Calculate statistics
            total_tasks = len(filtered_tasks)
            completed_tasks = [t for t in filtered_tasks if t["completed"]]
            incomplete_tasks = [t for t in filtered_tasks if not t["completed"]]
            overdue_tasks = []
            
            # Check for overdue tasks
            now = datetime.utcnow()
            for task in incomplete_tasks:
                if task["due_on"] or task["due_at"]:
                    due_date_str = task["due_at"] if task["due_at"] else task["due_on"]
                    try:
                        due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
                        if due_date < now:
                            overdue_tasks.append(task)
                    except:
                        continue
            
            # Calculate unique projects
            all_projects = set()
            for task in filtered_tasks:
                all_projects.update(task["projects"])
            
            # Calculate task completion rate
            completion_rate = len(completed_tasks) / total_tasks if total_tasks > 0 else 0
            
            # Calculate subtasks statistics
            total_subtasks = sum(t["num_subtasks"] for t in filtered_tasks)
            avg_subtasks = total_subtasks / total_tasks if total_tasks > 0 else 0
            
            # Calculate task status distribution
            status_distribution = {}
            for task in filtered_tasks:
                status = task["assignee_status"] or "no_status"
                status_distribution[status] = status_distribution.get(status, 0) + 1
            
            # Calculate daily task activity
            days_range = (end_date - start_date).days + 1
            avg_tasks_per_day = total_tasks / days_range if days_range > 0 else 0
            
            # Calculate tasks by day of week
            tasks_by_weekday = {i: 0 for i in range(7)}  # 0=Monday, 6=Sunday
            for task in filtered_tasks:
                modified_at = datetime.fromisoformat(task["modified_at"].replace("Z", "+00:00"))
                tasks_by_weekday[modified_at.weekday()] += 1
            
            return {
                "total_tasks": total_tasks,
                "completed_tasks": len(completed_tasks),
                "incomplete_tasks": len(incomplete_tasks),
                "overdue_tasks": len(overdue_tasks),
                "completion_rate": completion_rate,
                "unique_projects": len(all_projects),
                "context_switching_score": len(all_projects),  # Higher = more context switching
                "total_subtasks": total_subtasks,
                "avg_subtasks_per_task": avg_subtasks,
                "avg_tasks_per_day": avg_tasks_per_day,
                "status_distribution": status_distribution,
                "tasks_by_weekday": {
                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][day]: count
                    for day, count in tasks_by_weekday.items()
                },
                "overdue_ratio": len(overdue_tasks) / len(incomplete_tasks) if incomplete_tasks else 0
            }
        
        except Exception as e:
            logger.error(f"Error calculating user stats: {e}")
            raise
