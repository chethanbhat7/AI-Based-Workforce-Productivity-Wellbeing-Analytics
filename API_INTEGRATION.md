# API-Frontend Integration Guide

## Overview

This document describes the complete integration between API endpoints, data preprocessing, feature extraction, and the frontend dashboard.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  (React + TypeScript + Material UI)                         │
│                                                              │
│  Components:                                                 │
│  - MemberDashboard.tsx                                       │
│  - SupervisorDashboard.tsx                                   │
│  - WellbeingProfile.tsx                                      │
│  - ProductivityMetrics.tsx                                   │
│                                                              │
│  Services:                                                   │
│  - api.ts (API client)                                       │
│  - useDashboardData.ts (React hooks)                         │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP/REST
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND                          │
│                                                              │
│  Routers:                                                    │
│  ├─ /dashboard  → Dashboard endpoints (frontend-ready)      │
│  ├─ /features   → Feature extraction                        │
│  ├─ /data       → Raw data fetching                         │
│  └─ /auth       → OAuth2 authentication                     │
│                                                              │
│  Utilities:                                                  │
│  ├─ preprocessing.py → Data anonymization                   │
│  └─ feature_extraction.py → ML feature computation          │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                 EXTERNAL APIs (OAuth2)                       │
│                                                              │
│  - Microsoft Graph (Calendar, Email, Teams)                 │
│  - Slack (Messages, Reactions)                              │
│  - Jira (Issues, Worklogs)                                  │
│  - Asana (Tasks, Projects)                                  │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Data Collection
```
User clicks "Refresh Data" 
  ↓
Frontend: POST /dashboard/member/{user_id}/refresh
  ↓
Backend: Fetches data from all connected providers
  - Microsoft Graph API
  - Slack API  
  - Jira API
  ↓
Raw API responses stored temporarily
```

### 2. Data Preprocessing & Anonymization
```
Raw data from APIs
  ↓
preprocessing.py → DataPreprocessor
  ↓
CRITICAL: Teams messages anonymized
  - Message content → [REDACTED]
  - Features extracted (length, sentiment indicators)
  - ML-only hash generated for model access
  - Content NEVER exposed to users or UI
  ↓
Preprocessed, anonymized data
```

### 3. Feature Extraction
```
Preprocessed data
  ↓
feature_extraction.py → FeatureExtractor
  ↓
Extracts 23 features matching employee_data.csv:
  
Communication Features:
  - meeting_hours_per_week
  - meeting_counts_per_week
  - messages_sent_per_day
  - messages_received_per_day
  - avg_response_latency_min
  - communication_burstiness
  - after_hours_message_ratio
  - communication_balance
  - conversation_length_avg

Task Features:
  - avg_tasks_assigned_per_week
  - avg_tasks_completed_per_week
  - task_completion_rate
  - avg_task_age_days
  - overdue_task_ratio
  - task_comment_sentiment_mean

Work Hours Features:
  - logged_hours_per_week
  - variance_in_work_hours
  - late_start_count_per_month
  - early_exit_count_per_month
  - absenteeism_rate
  - avg_break_length_minutes

Performance Features:
  - performance_score
  - burnout_risk_score (computed by ML model)
  ↓
Features stored in database
```

### 4. Frontend Display
```
Features from database
  ↓
Dashboard API formats for frontend
  ↓
React components render visualizations
```

## API Endpoints

### Dashboard Endpoints (Frontend-Ready)

#### Get Member Overview
```
GET /dashboard/member/{user_id}/overview

Response:
{
  "user_id": "user123",
  "last_updated": "2024-11-07T12:00:00",
  "communication": {
    "meeting_hours_per_week": 12.5,
    "messages_sent_per_day": 35,
    ...
  },
  "tasks": {
    "task_completion_rate": 0.92,
    ...
  },
  "work_hours": {
    "logged_hours_per_week": 38.5,
    ...
  },
  "performance": {
    "performance_score": 0.75,
    "burnout_risk_score": 0.30
  }
}
```

#### Get Wellbeing Profile
```
GET /dashboard/member/{user_id}/wellbeing

Response:
{
  "user_id": "user123",
  "overall_score": 75,
  "categories": {
    "mental_health": 78,
    "physical_health": 82,
    "work_life_balance": 70,
    "stress_management": 68
  }
}
```

#### Get Productivity Metrics
```
GET /dashboard/member/{user_id}/metrics?period=week

Response:
{
  "efficiency_score": 82,
  "metrics": {
    "meeting_hours": 12.5,
    "task_completion_rate": 92,
    ...
  },
  "insights": [...]
}
```

#### Refresh Data
```
POST /dashboard/member/{user_id}/refresh
{
  "days_back": 14
}

Response:
{
  "status": "success",
  "features_extracted": 23,
  "privacy_notice": "Teams messages have been fully anonymized"
}
```

### Feature Extraction Endpoints

#### Extract Features
```
POST /features/extract/{user_id}
{
  "days_back": 14,
  "providers": ["microsoft", "slack", "jira"]
}

Response:
{
  "status": "success",
  "features": {
    "meeting_hours_per_week": 12.5,
    "messages_sent_per_day": 35,
    ...all 23 features...
  },
  "privacy_notice": "Teams messages have been fully anonymized"
}
```

#### Get Latest Features
```
GET /features/user/{user_id}/latest

Response:
{
  "date": "2024-11-07T12:00:00",
  "features": {...}
}
```

## Privacy & Anonymization

### Teams Message Anonymization

**CRITICAL SECURITY FEATURE:**

All Microsoft Teams messages are fully anonymized before storage:

1. **Message Content**: 
   - Raw text → `[MESSAGE CONTENT REDACTED FOR PRIVACY]`
   - Never stored in plain text
   - Never exposed to users or UI
   - Only accessible to ML model via secure hash

2. **Features Extracted**:
   ```python
   {
     "length": 150,
     "has_question": true,
     "word_count": 28,
     "has_emoji": false,
     "avg_word_length": 5.2
   }
   ```

3. **ML-Only Access**:
   - Secure hash generated: `ml_hash: "a3f5b2e9"`
   - Only ML inference pipeline can access original content
   - Content stored in encrypted cache
   - Expires after processing

4. **Author Anonymization**:
   ```python
   {
     "author": {
       "id_hash": "user_a3f5b2e9",
       "display_name": "User_a3f5b2e9"
     }
   }
   ```

### Implementation

See `/api/utils/preprocessing.py`:
- `DataAnonymizer.anonymize_teams_message()`
- `DataAnonymizer.anonymize_message_content()`
- `DataAnonymizer.get_content_for_ml()` (ML-only)

## Frontend Integration

### Using the API

```typescript
import { dashboardApi } from './services/api';

// Get dashboard data
const response = await dashboardApi.getMemberOverview(userId);
if (response.data) {
  console.log(response.data.communication);
}

// Refresh data
await dashboardApi.refreshData(userId, 14);
```

### Using React Hooks

```typescript
import { useDashboardData } from './hooks/useDashboardData';

function MyComponent() {
  const { data, loading, error, refetch } = useDashboardData(userId);
  
  if (loading) return <Loading />;
  if (error) return <Error message={error} />;
  
  return <Dashboard data={data} />;
}
```

## Setup Instructions

### Backend Setup

1. Install dependencies:
```bash
cd api
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OAuth credentials
```

3. Run migrations:
```bash
alembic upgrade head
```

4. Start the server:
```bash
uvicorn main:app --reload
```

### Frontend Setup

1. Install dependencies:
```bash
cd app/frontend
npm install
```

2. Set up environment:
```bash
# Create .env
VITE_API_URL=http://localhost:8000
```

3. Start development server:
```bash
npm run dev
```

## Testing the Integration

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
```

### 2. Extract Features for Test User
```bash
curl -X POST http://localhost:8000/features/extract/test_user \
  -H "Content-Type: application/json" \
  -d '{"days_back": 14, "providers": ["microsoft"]}'
```

### 3. Get Dashboard Data
```bash
curl http://localhost:8000/dashboard/member/test_user/overview
```

### 4. Access Frontend
```
Open http://localhost:5173
Login as member
View dashboard with real-time data
```

## Feature Mapping

Features match the `employee_data.csv` schema exactly:

| CSV Column | API Feature | Source |
|------------|-------------|--------|
| meeting_hours_per_week | meeting_hours_per_week | Microsoft Calendar |
| meeting_counts_per_week | meeting_counts_per_week | Microsoft Calendar |
| messages_sent_per_day | messages_sent_per_day | Teams + Slack |
| messages_received_per_day | messages_received_per_day | Teams + Slack |
| avg_tasks_completed_per_week | avg_tasks_completed_per_week | Jira |
| task_completion_rate | task_completion_rate | Jira |
| logged_hours_per_week | logged_hours_per_week | Jira Worklogs |
| performance_score | performance_score | Calculated |
| burnout_risk_score | burnout_risk_score | ML Model |

## ML Model Integration (Future)

The extracted features are ready for ML model consumption:

```python
# In your ML pipeline
from api.utils.preprocessing import data_anonymizer

# Access anonymized content for sentiment analysis
ml_hash = message["body"]["ml_hash"]
original_content = data_anonymizer.get_content_for_ml(ml_hash)

# Run sentiment analysis
sentiment = sentiment_model.predict(original_content)
```

## Troubleshooting

### No Data Showing in Dashboard

1. Check if OAuth tokens are connected:
```bash
curl http://localhost:8000/users/{user_id}/connections
```

2. Trigger data refresh:
```bash
curl -X POST http://localhost:8000/dashboard/member/{user_id}/refresh
```

3. Check feature extraction:
```bash
curl http://localhost:8000/features/user/{user_id}/latest
```

### Privacy Concerns

- Teams message content is **NEVER** exposed to users
- All message bodies show: `[MESSAGE CONTENT REDACTED FOR PRIVACY]`
- Only the ML model can access via secure hash
- Content expires after processing

## Contributing

When adding new features:

1. Add to `feature_extraction.py`
2. Update the schema in `/features/` endpoint
3. Update dashboard API to include new feature
4. Update frontend TypeScript types
5. Document in this README

## License

See main project LICENSE file.
