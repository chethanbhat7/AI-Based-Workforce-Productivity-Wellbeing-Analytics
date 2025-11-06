# Workforce Wellbeing Analytics - API Backend

OAuth2-based integration platform for workplace productivity and wellbeing analysis.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│         (React/Next.js - User connects apps)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ OAuth2 Routes│  │ Data Fetching│  │   Features   │     │
│  │              │  │              │  │  Extraction  │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                  │              │
│         ▼                 ▼                  ▼              │
│  ┌─────────────────────────────────────────────────┐       │
│  │         Encrypted Token Storage (PostgreSQL)    │       │
│  └─────────────────────────────────────────────────┘       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              External APIs (OAuth2)                          │
│  Microsoft Graph │ Slack │ Jira │ HRIS │ Surveys           │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Features

### ✅ Implemented
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
  
- **Database Models**
  - Users
  - OAuth tokens (encrypted)
  - Data fetch tracking
  - Features storage
  - Wellbeing scores

### 🚧 Coming Soon
- Slack integration
- Jira integration
- HRIS integration
- Survey platforms
- Feature extraction pipeline
- ML model integration
- Background job scheduler

## 📁 Project Structure

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
│   ├── slack.py          # Slack integration (TODO)
│   └── jira.py           # Jira integration (TODO)
│
└── utils/
    └── encryption.py      # Token encryption utilities
```

## 🔧 Setup

### Prerequisites
- Python 3.11+
- PostgreSQL
- Microsoft Azure App Registration (for Microsoft Graph)

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

### 5. Run the API

```bash
uvicorn main:app --reload --port 8000
```

Visit: `http://localhost:8000/docs` for API documentation

## 📡 API Endpoints

### Authentication

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

#### Disconnect Provider
```http
DELETE /auth/disconnect/{provider}?user_id={user_id}
```

### Data Fetching

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

## 🔐 Security

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
- ✅ Tokens encrypted at rest
- ✅ HTTPS only in production
- ✅ CORS properly configured
- ✅ OAuth state parameter for CSRF protection
- ✅ Token expiration tracking
- ✅ Automatic token refresh

## 🧪 Testing

Test the OAuth flow:

```bash
# 1. Create a user
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","organization":"Test Org"}'

# 2. Visit in browser (replace user_id)
http://localhost:8000/auth/microsoft/login?user_id=YOUR_USER_ID

# 3. After auth, check status
curl http://localhost:8000/auth/status/YOUR_USER_ID

# 4. Fetch data
curl -X POST http://localhost:8000/data/microsoft/fetch \
  -H "Content-Type: application/json" \
  -d '{
    "user_id":"YOUR_USER_ID",
    "data_types":["calendar","email"],
    "days_back":7
  }'
```

## 🗄️ Database Schema

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

## 📊 Next Steps

1. **Add more providers**: Slack, Jira, HRIS
2. **Feature extraction**: Build ML feature pipeline
3. **Background jobs**: Celery tasks for periodic fetching
4. **ML models**: Burnout prediction, stress scoring
5. **Frontend**: React dashboard for visualizations

## 🐛 Troubleshooting

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

## 📝 License

[Your License]
