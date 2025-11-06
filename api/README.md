# Workforce Wellbeing Analytics - API Backend

OAuth2-based integration platform for workplace productivity and wellbeing analysis.

## Features

### Implemented
- **Microsoft Graph OAuth2 Flow**
  - Authorization URL generation
  - Code exchange for tokens
  - Token refresh mechanism
  - Secure encrypted storage
  
- **Microsoft Graph Data Fetching**
  - Calendar events
  - Email metadata
  - Teams messages
  - User presence

- **Slack OAuth2 Flow**
  - Authorization URL generation
  - Code exchange for tokens
  - Secure encrypted storage
  - Workspace information
  
- **Slack Data Fetching**
  - User messages across channels
  - Emoji reactions (sentiment proxy)
  - Activity statistics
  - Channel participation
  - After-hours messaging patterns

- **Jira OAuth2 Flow**
  - Authorization URL generation
  - Code exchange for tokens
  - Token refresh mechanism
  - Accessible resources detection
  - Secure encrypted storage
  
- **Jira Data Fetching**
  - User issues (assigned/created)
  - Worklog time tracking
  - Issue statistics
  - Context switching metrics
  - Priority/status distribution

- **Asana OAuth2 Flow**
  - Authorization URL generation
  - Code exchange for tokens
  - Token refresh mechanism
  - Secure encrypted storage
  
- **Asana Data Fetching**
  - User tasks (assigned/modified)
  - Task completion tracking
  - Project participation
  - Workload statistics
  - Context switching metrics
  
- **Database Models**
  - Users
  - OAuth tokens (encrypted)
  - Data fetch tracking
  - Features storage
  - Wellbeing scores

### Coming Soon
- HRIS integration
- Survey platforms (Typeform/Qualtrics)
- Feature extraction pipeline
- ML model integration
- Background job scheduler

## Project Structure

```
api/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration management
├── database.py            # Database models and connection
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
│
├── routers/
│   ├── auth.py           # OAuth2 authentication endpoints
│   ├── data.py           # Data fetching endpoints
│   ├── users.py          # User management
│   └── features.py       # Feature extraction (placeholder)
│
├── integrations/
│   ├── microsoft_graph.py # Microsoft 365 integration
│   ├── slack.py          # Slack integration
│   ├── jira.py           # Jira integration
│   └── asana.py          # Asana integration
│
└── utils/
    └── encryption.py      # Token encryption utilities
```

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL
- Microsoft Azure App Registration (for Microsoft Graph)
- Slack App (for Slack API)
- Jira Cloud App (for Jira API)
- Asana App (for Asana API)

### 1. Install Dependencies

```bash
cd api
python -m venv venv
source venv/bin/activate  # On Mac/Linux
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Install PostgreSQL (Mac)
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb wellbeing_db
```

### 3. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your credentials
```

**Generate encryption key:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 4. Microsoft Azure App Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Set redirect URI: `http://localhost:8000/auth/microsoft/callback`
5. Add API permissions:
   - `User.Read`
   - `Calendars.Read`
   - `Mail.Read`
   - `Chat.Read`
   - `ChannelMessage.Read.All`
6. Copy **Client ID** and **Client Secret** to `.env`

### 5. Slack App Setup

1. Go to [Slack API](https://api.slack.com/apps)
2. Click **Create New App** → **From scratch**
3. Name your app and select workspace
4. Navigate to **OAuth & Permissions**
5. Add redirect URL: `http://localhost:8000/auth/slack/callback`
6. Add **Bot Token Scopes**:
   - `channels:history`
   - `channels:read`
   - `groups:history`
   - `groups:read`
   - `im:history`
   - `mpim:history`
   - `users:read`
   - `users:read.email`
   - `reactions:read`
   - `team:read`
7. Copy **Client ID** and **Client Secret** to `.env`
8. Install app to your workspace

### 6. Run the API

```bash
uvicorn main:app --reload --port 8000
```

Visit: `http://localhost:8000/docs` for API documentation

## API Endpoints

### Microsoft Graph Authentication

#### Initiate Microsoft OAuth
```http
GET /auth/microsoft/login?user_id={user_id}
```
Redirects to Microsoft login page.

#### OAuth Callback
```http
GET /auth/microsoft/callback?code={code}&state={state}
```
Handled automatically by OAuth flow.

#### Check Auth Status
```http
GET /auth/status/{user_id}
```

Response:
```json
{
  "user_id": "123",
  "providers": {
    "microsoft": {
      "connected": true,
      "expired": false,
      "expires_at": "2025-11-08T10:00:00",
      "scopes": ["User.Read", "Calendars.Read"]
    }
  }
}
```

#### Refresh Token
```http
POST /auth/refresh
{
  "user_id": "123",
  "provider": "microsoft"
}
```

### Slack Authentication

#### Initiate Slack OAuth
```http
GET /auth/slack/login?user_id={user_id}
```
Redirects to Slack authorization page.

### Jira Authentication

#### Initiate Jira OAuth
```http
GET /auth/jira/login?user_id={user_id}
```
Redirects to Jira authorization page.

### Asana Authentication

#### Initiate Asana OAuth
```http
GET /auth/asana/login?user_id={user_id}
```
Redirects to Asana authorization page.

### Universal Endpoints

#### Check Auth Status (All Providers)
```http
GET /auth/status/{user_id}
```
Shows all connected providers (Microsoft, Slack, Jira, Asana, etc.)

#### Disconnect Any Provider
```http
DELETE /auth/disconnect/{provider}?user_id={user_id}
```

---

## Data Fetching Endpoints

#### Fetch Microsoft Data
```http
POST /data/microsoft/fetch
{
  "user_id": "123",
  "data_types": ["calendar", "email", "teams"],
  "days_back": 14
}
```

Response:
```json
{
  "status": "success",
  "user_id": "123",
  "provider": "microsoft",
  "results": {
    "calendar": {
      "count": 45,
      "events": [...]
    },
    "email": {
      "count": 120,
      "emails": [...]
    }
  }
}
```

#### Get Fetch History
```http
GET /data/fetch-history/{user_id}?provider=microsoft&limit=50
```

#### Fetch Slack Data
```http
POST /data/slack/fetch
{
  "user_id": "123",
  "data_types": ["messages", "reactions", "stats"],
  "days_back": 14
}
```

Response:
```json
{
  "status": "success",
  "user_id": "123",
  "provider": "slack",
  "results": {
    "messages": {
      "count": 450,
      "messages": [...]
    },
    "reactions": {
      "count": 89,
      "reactions": [...]
    },
    "stats": {
      "total_messages": 450,
      "unique_channels": 12,
      "after_hours_ratio": 0.23,
      "avg_messages_per_day": 32
    }
  }
}
```

#### Fetch Jira Data
```http
POST /data/jira/fetch
{
  "user_id": "123",
  "data_types": ["issues", "worklogs", "stats"],
  "days_back": 14
}
```

Response:
```json
{
  "status": "success",
  "user_id": "123",
  "provider": "jira",
  "results": {
    "issues": {
      "count": 23,
      "issues": [...]
    },
    "worklogs": {
      "count": 45,
      "worklogs": [...]
    },
    "stats": {
      "total_assigned_issues": 23,
      "total_resolved_issues": 18,
      "resolution_rate": 0.78,
      "total_time_logged_hours": 72.5,
      "context_switching_score": 4,
      "unique_projects": 4
    }
  }
}
```

#### Fetch Asana Data
```http
POST /data/asana/fetch
{
  "user_id": "123",
  "workspace_gid": "workspace-gid",
  "data_types": ["tasks", "projects", "stats"],
  "days_back": 14
}
```

Response:
```json
{
  "status": "success",
  "user_id": "123",
  "provider": "asana",
  "workspace_gid": "workspace-gid",
  "results": {
    "tasks": {
      "count": 34,
      "tasks": [...]
    },
    "projects": {
      "count": 5,
      "projects": [...]
    },
    "stats": {
      "total_tasks": 34,
      "completed_tasks": 28,
      "completion_rate": 0.82,
      "overdue_tasks": 2,
      "unique_projects": 5,
      "context_switching_score": 5,
      "avg_tasks_per_day": 2.4
    }
  }
}
```

### Users

#### Create User
```http
POST /users/
{
  "email": "user@example.com",
  "organization": "Nordic Health Agency"
}
```

#### Get User
```http
GET /users/{user_id}
```

## Security

### Token Encryption
All OAuth tokens are encrypted using **Fernet** (symmetric encryption) before storage:

```python
from cryptography.fernet import Fernet

# Generate key (do once, store in .env)
key = Fernet.generate_key()

# Encrypt
cipher = Fernet(key)
encrypted_token = cipher.encrypt(token.encode())

# Decrypt
decrypted_token = cipher.decrypt(encrypted_token)
```

### Best Practices
- Tokens encrypted at rest
- HTTPS only in production
- CORS properly configured
- OAuth state parameter for CSRF protection
- Token expiration tracking
- Automatic token refresh

## Testing

### Test Microsoft OAuth Flow

```bash
# 1. Create a user
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","organization":"Test Org"}'

# 2. Visit in browser (replace user_id)
http://localhost:8000/auth/microsoft/login?user_id=YOUR_USER_ID

# 3. After auth, check status
curl http://localhost:8000/auth/status/YOUR_USER_ID

# 4. Fetch Microsoft data
curl -X POST http://localhost:8000/data/microsoft/fetch \
  -H "Content-Type: application/json" \
  -d '{
    "user_id":"YOUR_USER_ID",
    "data_types":["calendar","email"],
    "days_back":7
  }'
```

### Test Slack OAuth Flow

```bash
# 1. Visit in browser (use same user_id)
http://localhost:8000/auth/slack/login?user_id=YOUR_USER_ID

# 2. After auth, check status
curl http://localhost:8000/auth/status/YOUR_USER_ID

# 3. Fetch Slack data
curl -X POST http://localhost:8000/data/slack/fetch \
  -H "Content-Type: application/json" \
  -d '{
    "user_id":"YOUR_USER_ID",
    "data_types":["messages","reactions","stats"],
    "days_back":14
  }'
```

## Database Schema

### Users
```sql
id (PK)
email (unique)
organization
created_at
updated_at
is_active
metadata (JSON)
```

### OAuth Tokens
```sql
id (PK)
user_id (FK)
provider (microsoft, slack, jira)
access_token (encrypted)
refresh_token (encrypted)
expires_at
scopes (JSON)
created_at
updated_at
```

### Data Fetches
```sql
id (PK)
user_id (FK)
provider
data_type (calendar, email, teams)
fetch_start
fetch_end
status (pending, success, failed)
records_fetched
error_message
created_at
```

## ML Features Extracted

### From Microsoft Graph
- Meetings per week
- Average meeting duration
- After-hours meeting ratio
- Focus time (calendar gaps)
- Email volume (sent/received)
- Collaboration network size

### From Slack
- Messages sent per day/hour
- After-hours message ratio
- Channel participation diversity
- Emoji reactions (sentiment proxy)
- Response patterns
- Unique channels active in

### From Jira
- Issues assigned per week
- Issue resolution rate
- Time logged per day
- Context switching score (project count)
- Priority distribution
- Worklog patterns by weekday
- Average time per issue

### From Asana
- Tasks completed per week
- Task completion rate
- Overdue task ratio
- Context switching score (project count)
- Average tasks per day
- Task status distribution
- Subtask complexity

### Coming Soon
- **HRIS**: Attendance, overtime, leave patterns
- **Surveys**: Self-reported stress, sentiment analysis

## Next Steps

1. **HRIS integration**: Attendance and shift data
2. **Feature extraction pipeline**: Automated ML feature computation
3. **Background jobs**: Celery tasks for periodic fetching
4. **ML models**: Burnout prediction, stress scoring
5. **Frontend**: React dashboard for visualizations

## Troubleshooting

### "Token expired" error
Tokens refresh automatically. If manual refresh needed:
```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"user_id":"123","provider":"microsoft"}'
```

### Database connection errors
Check PostgreSQL is running:
```bash
brew services list
psql -l  # List databases
```

### OAuth redirect mismatch
Ensure redirect URI in `.env` matches Azure app registration exactly.
