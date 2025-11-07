"""
GitHub API Integration
Handles OAuth2 and data fetching from GitHub for developer productivity analysis
"""
import httpx
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from urllib.parse import urlencode

from config import settings

logger = logging.getLogger(__name__)


class GitHubOAuth:
    """GitHub OAuth2 handler"""
    
    def __init__(self):
        self.client_id = settings.GITHUB_CLIENT_ID
        self.client_secret = settings.GITHUB_CLIENT_SECRET
        self.redirect_uri = settings.get_redirect_uri("github")
        self.scopes = settings.GITHUB_SCOPES
        self.authorize_endpoint = "https://github.com/login/oauth/authorize"
        self.token_endpoint = "https://github.com/login/oauth/access_token"
    
    def get_authorization_url(self, state: str) -> str:
        """
        Generate OAuth2 authorization URL for GitHub
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "state": state,
            "allow_signup": "false"
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
                    },
                    headers={"Accept": "application/json"}
                )
                response.raise_for_status()
                return response.json()
        
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            raise


class GitHubAPI:
    """GitHub API data fetcher for developer productivity metrics"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    async def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict] = None,
        method: str = "GET"
    ) -> Dict:
        """Helper method to make authenticated API requests"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/{endpoint}"
                
                if method == "GET":
                    response = await client.get(url, headers=self.headers, params=params or {})
                else:
                    response = await client.request(method, url, headers=self.headers, params=params or {})
                
                response.raise_for_status()
                return response.json()
        
        except Exception as e:
            logger.error(f"Error making GitHub API request to {endpoint}: {e}")
            raise
    
    async def get_authenticated_user(self) -> Dict:
        """Get authenticated user information"""
        try:
            data = await self._make_request("user")
            return {
                "login": data.get("login"),
                "id": data.get("id"),
                "name": data.get("name"),
                "email": data.get("email"),
                "company": data.get("company"),
                "created_at": data.get("created_at"),
                "public_repos": data.get("public_repos"),
                "followers": data.get("followers"),
                "following": data.get("following")
            }
        except Exception as e:
            logger.error(f"Error getting authenticated user: {e}")
            raise
    
    async def get_user_commits(
        self,
        username: str,
        start_date: datetime,
        end_date: datetime,
        org: Optional[str] = None
    ) -> List[Dict]:
        """
        Get commits made by user across repositories
        
        Args:
            username: GitHub username
            start_date: Start date for commit search
            end_date: End date for commit search
            org: Optional organization name to limit search
        
        Returns:
            List of commits with metadata
        """
        try:
            # Build search query
            query_parts = [
                f"author:{username}",
                f"committer-date:{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"
            ]
            
            if org:
                query_parts.append(f"org:{org}")
            
            query = " ".join(query_parts)
            
            params = {
                "q": query,
                "sort": "committer-date",
                "order": "desc",
                "per_page": 100
            }
            
            data = await self._make_request("search/commits", params)
            
            commits = []
            for item in data.get("items", []):
                commit = item.get("commit", {})
                commits.append({
                    "sha": item.get("sha"),
                    "message": commit.get("message"),
                    "author": commit.get("author", {}).get("name"),
                    "author_email": commit.get("author", {}).get("email"),
                    "date": commit.get("author", {}).get("date"),
                    "committer_date": commit.get("committer", {}).get("date"),
                    "repository": item.get("repository", {}).get("full_name"),
                    "html_url": item.get("html_url"),
                    "additions": 0,  # Will need separate API call for stats
                    "deletions": 0,
                    "total_changes": 0
                })
            
            return commits
        
        except Exception as e:
            logger.error(f"Error getting user commits: {e}")
            raise
    
    async def get_user_pull_requests(
        self,
        username: str,
        start_date: datetime,
        end_date: datetime,
        org: Optional[str] = None
    ) -> List[Dict]:
        """
        Get pull requests created by user
        
        Args:
            username: GitHub username
            start_date: Start date for PR search
            end_date: End date for PR search
            org: Optional organization name
        
        Returns:
            List of pull requests with metadata
        """
        try:
            # Build search query
            query_parts = [
                f"author:{username}",
                "is:pr",
                f"created:{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"
            ]
            
            if org:
                query_parts.append(f"org:{org}")
            
            query = " ".join(query_parts)
            
            params = {
                "q": query,
                "sort": "created",
                "order": "desc",
                "per_page": 100
            }
            
            data = await self._make_request("search/issues", params)
            
            pull_requests = []
            for item in data.get("items", []):
                pr = {
                    "id": item.get("id"),
                    "number": item.get("number"),
                    "title": item.get("title"),
                    "state": item.get("state"),
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at"),
                    "closed_at": item.get("closed_at"),
                    "merged_at": item.get("pull_request", {}).get("merged_at"),
                    "html_url": item.get("html_url"),
                    "repository": item.get("repository_url").split("/repos/")[-1] if item.get("repository_url") else None,
                    "comments": item.get("comments", 0),
                    "labels": [label.get("name") for label in item.get("labels", [])],
                    "assignees": [assignee.get("login") for assignee in item.get("assignees", [])]
                }
                pull_requests.append(pr)
            
            return pull_requests
        
        except Exception as e:
            logger.error(f"Error getting user pull requests: {e}")
            raise
    
    async def get_user_reviews(
        self,
        username: str,
        start_date: datetime,
        end_date: datetime,
        org: Optional[str] = None
    ) -> List[Dict]:
        """
        Get pull request reviews made by user
        
        Args:
            username: GitHub username
            start_date: Start date for review search
            end_date: End date for review search
            org: Optional organization name
        
        Returns:
            List of PR reviews
        """
        try:
            # Search for PRs reviewed by user
            query_parts = [
                f"reviewed-by:{username}",
                "is:pr",
                f"created:{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"
            ]
            
            if org:
                query_parts.append(f"org:{org}")
            
            query = " ".join(query_parts)
            
            params = {
                "q": query,
                "sort": "created",
                "order": "desc",
                "per_page": 100
            }
            
            data = await self._make_request("search/issues", params)
            
            reviews = []
            for item in data.get("items", []):
                reviews.append({
                    "pr_number": item.get("number"),
                    "pr_title": item.get("title"),
                    "pr_state": item.get("state"),
                    "pr_created_at": item.get("created_at"),
                    "pr_url": item.get("html_url"),
                    "repository": item.get("repository_url").split("/repos/")[-1] if item.get("repository_url") else None
                })
            
            return reviews
        
        except Exception as e:
            logger.error(f"Error getting user reviews: {e}")
            raise
    
    async def get_user_issues(
        self,
        username: str,
        start_date: datetime,
        end_date: datetime,
        org: Optional[str] = None
    ) -> List[Dict]:
        """
        Get issues created or assigned to user
        
        Args:
            username: GitHub username
            start_date: Start date
            end_date: End date
            org: Optional organization name
        
        Returns:
            List of issues
        """
        try:
            # Search for issues created by user
            query_parts = [
                f"author:{username}",
                "is:issue",
                f"created:{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"
            ]
            
            if org:
                query_parts.append(f"org:{org}")
            
            query = " ".join(query_parts)
            
            params = {
                "q": query,
                "sort": "created",
                "order": "desc",
                "per_page": 100
            }
            
            data = await self._make_request("search/issues", params)
            
            issues = []
            for item in data.get("items", []):
                issues.append({
                    "id": item.get("id"),
                    "number": item.get("number"),
                    "title": item.get("title"),
                    "state": item.get("state"),
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at"),
                    "closed_at": item.get("closed_at"),
                    "html_url": item.get("html_url"),
                    "repository": item.get("repository_url").split("/repos/")[-1] if item.get("repository_url") else None,
                    "comments": item.get("comments", 0),
                    "labels": [label.get("name") for label in item.get("labels", [])]
                })
            
            return issues
        
        except Exception as e:
            logger.error(f"Error getting user issues: {e}")
            raise
    
    async def get_repository_stats(
        self,
        owner: str,
        repo: str,
        username: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Get detailed statistics for a user in a specific repository
        
        Args:
            owner: Repository owner
            repo: Repository name
            username: GitHub username
            start_date: Start date
            end_date: End date
        
        Returns:
            Repository-specific statistics
        """
        try:
            # Get commits in this repo
            params = {
                "author": username,
                "since": start_date.isoformat(),
                "until": end_date.isoformat(),
                "per_page": 100
            }
            
            commits = await self._make_request(f"repos/{owner}/{repo}/commits", params)
            
            total_commits = len(commits)
            total_additions = 0
            total_deletions = 0
            
            # Get detailed stats for each commit
            for commit in commits[:50]:  # Limit to avoid rate limits
                sha = commit.get("sha")
                try:
                    commit_detail = await self._make_request(f"repos/{owner}/{repo}/commits/{sha}")
                    stats = commit_detail.get("stats", {})
                    total_additions += stats.get("additions", 0)
                    total_deletions += stats.get("deletions", 0)
                except Exception as e:
                    logger.warning(f"Error fetching commit stats for {sha}: {e}")
                    continue
            
            return {
                "repository": f"{owner}/{repo}",
                "total_commits": total_commits,
                "total_additions": total_additions,
                "total_deletions": total_deletions,
                "total_changes": total_additions + total_deletions
            }
        
        except Exception as e:
            logger.error(f"Error getting repository stats: {e}")
            raise
    
    async def get_user_stats(
        self,
        username: str,
        start_date: datetime,
        end_date: datetime,
        org: Optional[str] = None
    ) -> Dict:
        """
        Calculate comprehensive GitHub activity statistics for a user
        
        Args:
            username: GitHub username
            start_date: Start date for analysis
            end_date: End date for analysis
            org: Optional organization to limit scope
        
        Returns:
            Comprehensive statistics dictionary
        """
        try:
            # Fetch all data in parallel would be ideal, but for now sequential
            commits = await self.get_user_commits(username, start_date, end_date, org)
            pull_requests = await self.get_user_pull_requests(username, start_date, end_date, org)
            reviews = await self.get_user_reviews(username, start_date, end_date, org)
            issues = await self.get_user_issues(username, start_date, end_date, org)
            
            # Calculate statistics
            days_in_range = (end_date - start_date).days + 1
            
            # Commit stats
            total_commits = len(commits)
            unique_repos_commits = len(set(c["repository"] for c in commits if c.get("repository")))
            
            # PR stats
            total_prs_created = len(pull_requests)
            merged_prs = [pr for pr in pull_requests if pr.get("merged_at")]
            closed_prs = [pr for pr in pull_requests if pr.get("state") == "closed"]
            open_prs = [pr for pr in pull_requests if pr.get("state") == "open"]
            
            pr_merge_rate = len(merged_prs) / total_prs_created if total_prs_created > 0 else 0
            
            # Calculate average time to merge
            merge_times = []
            for pr in merged_prs:
                if pr.get("created_at") and pr.get("merged_at"):
                    created = datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00"))
                    merged = datetime.fromisoformat(pr["merged_at"].replace("Z", "+00:00"))
                    merge_times.append((merged - created).total_seconds() / 3600)  # hours
            
            avg_pr_merge_time_hours = sum(merge_times) / len(merge_times) if merge_times else 0
            
            # Review stats
            total_reviews_given = len(reviews)
            
            # Issue stats
            total_issues_created = len(issues)
            closed_issues = [issue for issue in issues if issue.get("state") == "closed"]
            
            # Repository diversity (context switching)
            all_repos = set()
            for item in commits + pull_requests + issues:
                if item.get("repository"):
                    all_repos.add(item["repository"])
            
            unique_repos = len(all_repos)
            
            # Activity distribution by day of week
            commit_by_weekday = {i: 0 for i in range(7)}
            pr_by_weekday = {i: 0 for i in range(7)}
            
            for commit in commits:
                if commit.get("date"):
                    date = datetime.fromisoformat(commit["date"].replace("Z", "+00:00"))
                    commit_by_weekday[date.weekday()] += 1
            
            for pr in pull_requests:
                if pr.get("created_at"):
                    date = datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00"))
                    pr_by_weekday[date.weekday()] += 1
            
            # Calculate consistency (days with activity)
            activity_dates = set()
            for commit in commits:
                if commit.get("date"):
                    date = datetime.fromisoformat(commit["date"].replace("Z", "+00:00")).date()
                    activity_dates.add(date)
            
            for pr in pull_requests:
                if pr.get("created_at"):
                    date = datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00")).date()
                    activity_dates.add(date)
            
            active_days = len(activity_dates)
            activity_consistency = active_days / days_in_range if days_in_range > 0 else 0
            
            return {
                "total_commits": total_commits,
                "commits_per_day": total_commits / days_in_range if days_in_range > 0 else 0,
                "commits_per_week": (total_commits / days_in_range) * 7 if days_in_range > 0 else 0,
                "total_prs_created": total_prs_created,
                "prs_per_week": (total_prs_created / days_in_range) * 7 if days_in_range > 0 else 0,
                "merged_prs": len(merged_prs),
                "open_prs": len(open_prs),
                "pr_merge_rate": pr_merge_rate,
                "avg_pr_merge_time_hours": avg_pr_merge_time_hours,
                "total_reviews_given": total_reviews_given,
                "reviews_per_week": (total_reviews_given / days_in_range) * 7 if days_in_range > 0 else 0,
                "total_issues_created": total_issues_created,
                "issues_closed": len(closed_issues),
                "issue_close_rate": len(closed_issues) / total_issues_created if total_issues_created > 0 else 0,
                "unique_repositories": unique_repos,
                "repo_context_switching": unique_repos,  # Higher = more context switching
                "active_days": active_days,
                "activity_consistency": activity_consistency,
                "commit_by_weekday": {
                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][day]: count
                    for day, count in commit_by_weekday.items()
                },
                "pr_by_weekday": {
                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][day]: count
                    for day, count in pr_by_weekday.items()
                }
            }
        
        except Exception as e:
            logger.error(f"Error calculating user stats: {e}")
            raise
