# Google Sheets Integration for Attendance Tracking

## Overview

This integration uses **Google Sheets** as a lightweight, accessible database for storing weekly employee attendance punch records. Google Sheets provides several advantages for attendance tracking:

- ✅ **Real-time Collaboration**: HR and managers can view attendance data in real-time
- ✅ **Easy Access**: No database setup required - accessible from any browser
- ✅ **Visual Dashboard**: Built-in charting and pivot tables for attendance analytics
- ✅ **Audit Trail**: Version history tracks all changes
- ✅ **Export Options**: Easy export to Excel, CSV, PDF
- ✅ **Cost-Effective**: Free for up to 10 million cells per spreadsheet

## Spreadsheet Structure

The attendance tracking spreadsheet contains **two sheets**:

### 1. Punch Records Sheet
Stores all individual punch in/out events.

| Column | Description | Example |
|--------|-------------|---------|
| Employee ID | Unique employee identifier | EMP001 |
| Punch Type | IN or OUT | IN |
| Punch Time | Full timestamp (ISO 8601) | 2025-11-07T09:15:30 |
| Date | Date only (YYYY-MM-DD) | 2025-11-07 |
| Time | Time only (HH:MM:SS) | 09:15:30 |
| Biometric Match Score | Confidence score (0-100) | 98.5 |
| Location | Punch location/branch | Main Office |
| Device ID | Biometric device identifier | DEVICE_01 |
| Verified | Biometric verification status | Yes |
| Week Number | ISO week number | 45 |
| Year | Year | 2025 |
| Notes | Additional comments | - |

### 2. Weekly Summary Sheet
Aggregated weekly attendance metrics per employee.

| Column | Description | Example |
|--------|-------------|---------|
| Employee ID | Unique employee identifier | EMP001 |
| Week Start Date | Monday of the week | 2025-11-04 |
| Week End Date | Sunday of the week | 2025-11-10 |
| Total Days Present | Number of days worked | 5 |
| Total Hours | Total hours worked | 42.5 |
| Late Arrivals | Number of late punches | 1 |
| Early Departures | Number of early exits | 0 |
| Overtime Hours | Hours worked beyond standard | 2.5 |
| Avg Daily Hours | Average hours per day | 8.5 |
| Punctuality Score | Score 0-100 | 92.0 |
| Total Punches | Total IN/OUT records | 10 |
| Break Duration (min) | Total break time | 60 |
| Avg Break Duration | Average break per day | 12.0 |
| Attendance Rate (%) | Present / Expected days | 100.0 |
| Notes | Additional comments | - |

## Setup Instructions

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable **Google Sheets API**:
   - Navigate to **APIs & Services > Library**
   - Search for "Google Sheets API"
   - Click **Enable**
4. Enable **Google Drive API** (required for file creation):
   - Search for "Google Drive API"
   - Click **Enable**

### 2. Create OAuth2 Credentials

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth client ID**
3. Configure OAuth consent screen (if first time):
   - User Type: **Internal** (for organization) or **External** (for testing)
   - App name: "Workforce Wellbeing Analytics"
   - User support email: Your email
   - Scopes: Add `../auth/spreadsheets` and `../auth/drive.file`
4. Create OAuth client ID:
   - Application type: **Web application**
   - Name: "Workforce Wellbeing API"
   - Authorized redirect URIs: `http://localhost:8000/auth/google/callback`
5. Copy **Client ID** and **Client Secret**

### 3. Configure Environment Variables

Add to your `.env` file:

```bash
# Google Sheets OAuth2
GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-client-secret"
GOOGLE_REDIRECT_URI="http://localhost:8000/auth/google/callback"
GOOGLE_ATTENDANCE_SPREADSHEET_ID=""  # Leave empty - will be created automatically
```

### 4. Create Attendance Spreadsheet

You can create the spreadsheet in two ways:

#### Option A: Automatically via API
```python
from integrations.google_sheets import GoogleSheetsAPI

# After user authorizes with Google
sheets_api = GoogleSheetsAPI(access_token=user_access_token)
result = await sheets_api.create_attendance_spreadsheet(
    title="Employee Attendance Records - 2025"
)
spreadsheet_id = result["spreadsheetId"]
spreadsheet_url = result["spreadsheetUrl"]

print(f"Spreadsheet created: {spreadsheet_url}")
# Save spreadsheet_id to GOOGLE_ATTENDANCE_SPREADSHEET_ID in .env
```

#### Option B: Manually
1. Go to [Google Sheets](https://sheets.google.com/)
2. Create a new blank spreadsheet
3. Name it "Employee Attendance Records"
4. Create two sheets: "Punch Records" and "Weekly Summary"
5. Add headers from the tables above
6. Get the spreadsheet ID from the URL:
   - URL format: `https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit`
7. Add the ID to your `.env` file

## API Usage

### Recording Punch Events

```python
from integrations.google_sheets import GoogleSheetsAPI
from datetime import datetime

# Initialize API with user's access token
sheets_api = GoogleSheetsAPI(access_token=access_token)

# Record punch-in
await sheets_api.append_punch_record(
    spreadsheet_id=settings.GOOGLE_ATTENDANCE_SPREADSHEET_ID,
    employee_id="EMP001",
    punch_type="IN",
    punch_time=datetime.now(),
    biometric_match_score=98.5,
    location="Main Office",
    device_id="DEVICE_01",
    verified=True
)

# Record punch-out
await sheets_api.append_punch_record(
    spreadsheet_id=settings.GOOGLE_ATTENDANCE_SPREADSHEET_ID,
    employee_id="EMP001",
    punch_type="OUT",
    punch_time=datetime.now(),
    biometric_match_score=97.2,
    location="Main Office",
    device_id="DEVICE_01",
    verified=True
)
```

### Storing Weekly Summaries

```python
from datetime import datetime, timedelta

# Calculate week start (Monday)
today = datetime.now()
week_start = today - timedelta(days=today.weekday())
week_end = week_start + timedelta(days=6)

# Prepare summary data
summary_data = {
    "days_present": 5,
    "total_hours": 42.5,
    "late_arrivals": 1,
    "early_departures": 0,
    "overtime_hours": 2.5,
    "avg_daily_hours": 8.5,
    "punctuality_score": 92.0,
    "total_punches": 10,
    "break_duration_minutes": 60,
    "avg_break_duration": 12.0,
    "attendance_rate": 100.0,
    "notes": "Good week overall"
}

# Append weekly summary
await sheets_api.append_weekly_summary(
    spreadsheet_id=settings.GOOGLE_ATTENDANCE_SPREADSHEET_ID,
    employee_id="EMP001",
    week_start=week_start,
    week_end=week_end,
    summary_data=summary_data
)
```

### Retrieving Records

```python
# Get all punch records for an employee
records = await sheets_api.get_punch_records(
    spreadsheet_id=settings.GOOGLE_ATTENDANCE_SPREADSHEET_ID,
    employee_id="EMP001"
)

# Get punch records for a date range
from datetime import datetime, timedelta

start_date = datetime.now() - timedelta(days=7)
end_date = datetime.now()

records = await sheets_api.get_punch_records(
    spreadsheet_id=settings.GOOGLE_ATTENDANCE_SPREADSHEET_ID,
    employee_id="EMP001",
    start_date=start_date,
    end_date=end_date
)

# Get weekly summaries
summaries = await sheets_api.get_weekly_summary(
    spreadsheet_id=settings.GOOGLE_ATTENDANCE_SPREADSHEET_ID,
    employee_id="EMP001"
)
```

## Integration with Attendance Routes

Update `api/routers/attendance.py` to store punch records in Google Sheets:

```python
from integrations.google_sheets import GoogleSheetsAPI
from config import settings

@router.post("/punch-in")
async def punch_in(request: PunchInRequest):
    # Record punch with CloudABIS
    result = await cloudabis_api.record_punch_in(...)
    
    if result["success"]:
        punch_record = result["punch_record"]
        
        # Store in Google Sheets
        # Note: You'll need to get the user's Google access token from DB
        sheets_api = GoogleSheetsAPI(access_token=user_google_token)
        
        await sheets_api.append_punch_record(
            spreadsheet_id=settings.GOOGLE_ATTENDANCE_SPREADSHEET_ID,
            employee_id=punch_record["employee_id"],
            punch_type="IN",
            punch_time=datetime.fromisoformat(punch_record["punch_time"]),
            biometric_match_score=punch_record["biometric_match_score"],
            location=punch_record["location"],
            device_id=punch_record["device_id"],
            verified=punch_record["verified"]
        )
    
    return result
```

## Token Management

Google OAuth2 tokens expire after 1 hour. Store the **refresh token** in your database to get new access tokens:

```python
# After initial authorization
token_data = await google_sheets_oauth.exchange_code_for_token(code)

# Store in database:
# - access_token (expires in 1 hour)
# - refresh_token (valid until revoked)
# - expires_in (3600 seconds)

# When access token expires, refresh it:
new_token_data = await google_sheets_oauth.refresh_access_token(
    refresh_token=stored_refresh_token
)
# Update access_token in database
```

## Automated Weekly Reports

You can set up a scheduled task to generate weekly summaries:

```python
from datetime import datetime, timedelta
from integrations.cloudabis import cloudabis_api
from integrations.google_sheets import GoogleSheetsAPI

async def generate_weekly_reports():
    """Run this every Monday to generate last week's summary"""
    
    # Calculate last week's date range
    today = datetime.now()
    last_monday = today - timedelta(days=today.weekday() + 7)
    last_sunday = last_monday + timedelta(days=6)
    
    # Get all employees
    employees = await get_all_employees()  # Your function
    
    for employee in employees:
        # Calculate attendance metrics from CloudABIS
        metrics = await cloudabis_api.calculate_attendance_metrics(
            employee_id=employee.id,
            start_date=last_monday,
            end_date=last_sunday
        )
        
        # Store in Google Sheets
        sheets_api = GoogleSheetsAPI(access_token=employee.google_token)
        await sheets_api.append_weekly_summary(
            spreadsheet_id=settings.GOOGLE_ATTENDANCE_SPREADSHEET_ID,
            employee_id=employee.id,
            week_start=last_monday,
            week_end=last_sunday,
            summary_data=metrics
        )
```

## Data Analytics with Google Sheets

### Pivot Tables
1. Select data in "Punch Records" sheet
2. Insert > Pivot Table
3. Create summaries by:
   - Row: Employee ID
   - Values: Count of Punch Type, Average Match Score
   - Filter: Date range

### Charts
1. Select "Weekly Summary" data
2. Insert > Chart
3. Create visualizations:
   - **Attendance Rate Trend**: Line chart of attendance % over weeks
   - **Punctuality Distribution**: Bar chart of punctuality scores
   - **Hours Worked**: Stacked column chart of regular vs. overtime hours

### Conditional Formatting
Highlight issues automatically:
- Late arrivals > 2 per week → Red background
- Punctuality score < 80 → Orange background
- Attendance rate < 95% → Yellow background

## Rate Limits

Google Sheets API has the following quotas:

- **Read requests**: 100 per 100 seconds per user
- **Write requests**: 100 per 100 seconds per user
- **Total requests**: 300 per 60 seconds per project

For high-traffic scenarios:
- Batch writes instead of individual append operations
- Cache spreadsheet reads
- Use exponential backoff for retry logic

## Security Best Practices

1. **Service Account** (recommended for production):
   - Create a service account in Google Cloud Console
   - Share the spreadsheet with the service account email
   - Use service account credentials instead of user OAuth

2. **Access Control**:
   - Set spreadsheet to "Anyone with link can view" (read-only)
   - Only grant "Editor" access to the service account
   - Use Google Workspace to restrict sharing outside organization

3. **Data Privacy**:
   - Avoid storing sensitive biometric data in sheets (only match scores)
   - Use employee IDs instead of names if required by privacy policy
   - Enable 2-factor authentication for Google accounts with access

## Troubleshooting

### Error: "The caller does not have permission"
- Ensure the OAuth token has the `spreadsheets` scope
- Check that the user has edit access to the spreadsheet

### Error: "Requested entity was not found"
- Verify the spreadsheet ID is correct
- Ensure the sheet names match exactly (case-sensitive)

### Token expired errors
- Implement automatic token refresh using the refresh token
- Add error handling to detect 401 responses and refresh token

### Quota exceeded errors
- Implement rate limiting in your API
- Use batch operations to reduce API calls
- Consider caching frequently accessed data

## Migration Path

If you later decide to migrate to a SQL database:

1. Export sheets to CSV
2. Import using pandas:
```python
import pandas as pd

df_punches = pd.read_csv("punch_records.csv")
df_summary = pd.read_csv("weekly_summary.csv")

# Insert into PostgreSQL
df_punches.to_sql("punch_records", engine, if_exists="append", index=False)
df_summary.to_sql("weekly_summary", engine, if_exists="append", index=False)
```

## Next Steps

1. ✅ Set up Google Cloud project and enable APIs
2. ✅ Create OAuth credentials
3. ✅ Configure environment variables
4. ✅ Create attendance spreadsheet
5. 🔲 Update attendance routes to store in Sheets
6. 🔲 Implement OAuth callback handler for Google
7. 🔲 Test punch-in/out workflow
8. 🔲 Set up weekly report automation
9. 🔲 Create dashboard visualizations in Sheets
10. 🔲 Train HR staff on accessing and analyzing data
