# GitHub Integration for Workforce Wellbeing Analysis

## Overview
This integration connects to GitHub to track developer productivity metrics including commits, pull requests, code reviews, and collaboration patterns.

## OAuth2 Setup

### Required GitHub OAuth App Settings
1. Go to GitHub Settings → Developer settings → OAuth Apps → New OAuth App
2. Configure:
   - **Application name**: Workforce Wellbeing Analytics
   - **Homepage URL**: `http://localhost:8000`
   - **Authorization callback URL**: `http://localhost:8000/auth/github/callback`
   - **Scopes**: `repo`, `read:user`, `user:email`, `read:org`

3. Add to `.env` file:
```env
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:8000/auth/github/callback
```

## Required Scopes

| Scope | Purpose |
|-------|---------|
| `repo` | Access to private and public repositories |
| `read:user` | Read user profile information |
| `user:email` | Access user email addresses |
| `read:org` | Read organization membership and teams |

## Data Collected

### 1. Commits
- **Endpoint**: `GET /search/commits`
- **Data Points**:
  - Total commits in date range
  - Commit messages
  - Commit timestamps
  - Repositories committed to
  - Lines added/deleted (requires additional API call per commit)

### 2. Pull Requests
- **Endpoint**: `GET /search/issues?q=is:pr+author:{username}`
- **Data Points**:
  - PRs created
  - PR state (open/closed/merged)
  - Time to merge
  - Comments on PRs
  - Labels and assignees
  - Repositories

### 3. Code Reviews
- **Endpoint**: `GET /search/issues?q=is:pr+reviewed-by:{username}`
- **Data Points**:
  - PRs reviewed
  - Review timestamps
  - Repositories reviewed in

### 4. Issues
- **Endpoint**: `GET /search/issues?q=is:issue+author:{username}`
- **Data Points**:
  - Issues created
  - Issue state
  - Comments
  - Labels

## Features Extracted

### New Dataset Columns (from GitHub)

```python
{
    "github_commits_per_week": float,          # Avg commits per week
    "github_prs_per_week": float,              # Pull requests created per week
    "github_pr_merge_rate": float,             # % of PRs that get merged
    "github_reviews_per_week": float,          # Code reviews given per week
    "github_repo_context_switching": int,      # Number of unique repos worked on
    "github_activity_consistency": float       # % of days with GitHub activity
}
```

### Metrics Calculation

1. **Commits Per Week**
   - Total commits / weeks in range
   - Indicates coding velocity

2. **PRs Per Week**
   - Total PRs created / weeks in range
   - Indicates feature completion rate

3. **PR Merge Rate**
   - Merged PRs / Total PRs
   - Quality indicator (higher = better code quality)

4. **Reviews Per Week**
   - Total reviews given / weeks in range
   - Collaboration metric

5. **Repository Context Switching**
   - Count of unique repositories
   - Higher values = more multitasking/context switching

6. **Activity Consistency**
   - Days with commits or PRs / Total days
   - Measures work pattern regularity

## Usage Example

```python
from integrations.github import GitHubOAuth, GitHubAPI
from datetime import datetime, timedelta

# OAuth flow
oauth = GitHubOAuth()
auth_url = oauth.get_authorization_url(state="random_state")
# Redirect user to auth_url

# After callback
tokens = await oauth.exchange_code_for_token(code)
access_token = tokens["access_token"]

# Fetch data
github_api = GitHubAPI(access_token)
user = await github_api.get_authenticated_user()

# Get stats for last 30 days
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

stats = await github_api.get_user_stats(
    username=user["login"],
    start_date=start_date,
    end_date=end_date,
    org="your-org-name"  # Optional
)

print(f"Commits per week: {stats['commits_per_week']}")
print(f"PR merge rate: {stats['pr_merge_rate']}")
```

## Integration with Feature Extraction

```python
from utils.feature_extraction import feature_extractor

# Extract all features including GitHub
features = feature_extractor.extract_all_features(
    calendar_events=calendar_data,
    messages=slack_data,
    tasks=jira_data,
    worklogs=jira_worklogs,
    user_id=user_id,
    start_date=start_date,
    end_date=end_date,
    github_stats=github_stats  # ← New parameter
)
```

## Correlation with Wellbeing

### Expected Correlations:

**Burnout Risk Indicators:**
- ⬆️ High `github_commits_per_week` (>40) → Potential overwork
- ⬆️ High `github_repo_context_switching` (>5) → Mental fatigue from context switching
- ⬇️ Low `github_activity_consistency` (<0.5) → Irregular work patterns

**Performance Indicators:**
- ⬆️ High `github_pr_merge_rate` (>0.8) → Good code quality
- ⬆️ High `github_reviews_per_week` (>5) → Good collaboration
- Balanced commits + reviews → Well-rounded contributor

## Rate Limiting

GitHub API has rate limits:
- **Authenticated requests**: 5,000 per hour
- **Search API**: 30 requests per minute

The integration handles this by:
- Using search API efficiently
- Limiting commit detail fetches to 50 per repo
- Caching results

## Privacy Considerations

- Only public repositories are included by default
- Private repo data requires `repo` scope and user consent
- Commit messages are stored but can be excluded
- Code diffs are NOT stored (only line counts)

## Testing

```bash
# Test GitHub OAuth
python -c "from integrations.github import GitHubOAuth; print(GitHubOAuth().get_authorization_url('test'))"

# Test API calls (requires valid token)
# Add your token to .env first
python -c "
from integrations.github import GitHubAPI
import asyncio
api = GitHubAPI('your_token_here')
print(asyncio.run(api.get_authenticated_user()))
"
```

## Next Steps

1. Add GitHub OAuth routes to `routers/auth.py`
2. Store GitHub tokens in database with encryption
3. Schedule periodic data fetches
4. Update ML model to include GitHub features
5. Add GitHub metrics to dashboard
