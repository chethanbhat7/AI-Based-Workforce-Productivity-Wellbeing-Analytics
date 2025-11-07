# One Sheet Per Employee Per Week - Google Sheets Structure

## Overview

Instead of having all employees' data mixed in one giant sheet, the system now creates **individual sheets for each employee for each week**. This provides better organization, privacy, and ease of access.

## Spreadsheet Structure

### Main Spreadsheet
One master Google Sheet with multiple tabs (sheets):

```
📊 Employee Attendance Records
├── 📄 Index (directory of all employee-week sheets)
├── 📄 EMP001_2025-W45 (John Doe's week 45)
├── 📄 EMP001_2025-W46 (John Doe's week 46)
├── 📄 EMP002_2025-W45 (Jane Smith's week 45)
├── 📄 EMP002_2025-W46 (Jane Smith's week 46)
└── ... (more sheets created automatically)
```

## Sheet Naming Convention

**Format**: `{EMPLOYEE_ID}_{YEAR}-W{WEEK_NUMBER}`

Examples:
- `EMP001_2025-W45` = Employee EMP001, Year 2025, Week 45
- `EMP042_2025-W52` = Employee EMP042, Year 2025, Week 52

## Index Sheet

The **Index** sheet acts as a table of contents:

| Employee ID | Employee Name | Week Start Date | Week End Date | Sheet Name | Last Updated |
|-------------|---------------|-----------------|---------------|------------|--------------|
| EMP001 | John Doe | 2025-11-04 | 2025-11-10 | EMP001_2025-W45 | 2025-11-07 10:30:00 |
| EMP001 | John Doe | 2025-11-11 | 2025-11-17 | EMP001_2025-W46 | 2025-11-14 09:15:00 |
| EMP002 | Jane Smith | 2025-11-04 | 2025-11-10 | EMP002_2025-W45 | 2025-11-07 10:32:00 |

**Purpose**: Quickly find which sheet contains a specific employee's data for a given week.

## Individual Employee Week Sheet

Each employee gets their own sheet for each week with this structure:

### Header Section (Rows 1-3)
```
Row 1: Employee: John Doe (EMP001)
Row 2: Week: 2025-11-04 to 2025-11-10
Row 3: [empty row for spacing]
```

### Column Headers (Row 4)
| Date | Day | Punch In Time | Punch Out Time | Total Hours | Break Duration (min) | Biometric Score (In) | Biometric Score (Out) | Location | Status | Overtime | Notes |
|------|-----|---------------|----------------|-------------|---------------------|---------------------|----------------------|----------|--------|----------|-------|

### Daily Records (Rows 5+)
| Date | Day | Punch In Time | Punch Out Time | Total Hours | Break (min) | Bio In | Bio Out | Location | Status | OT | Notes |
|------|-----|---------------|----------------|-------------|------------|--------|---------|----------|--------|-----|-------|
| 2025-11-04 | Monday | 09:00:00 | 18:00:00 | 8.00 | 60 | 98.5 | 97.2 | Main Office | Present | 0.00 | |
| 2025-11-05 | Tuesday | 09:15:00 | 18:30:00 | 8.25 | 60 | 99.1 | 98.8 | Main Office | Late | 0.25 | Traffic |
| 2025-11-06 | Wednesday | 08:45:00 | 17:00:00 | 7.25 | 60 | 97.8 | 96.5 | Main Office | Present | 0.00 | |
| 2025-11-07 | Thursday | 09:00:00 | 19:00:00 | 9.00 | 60 | 98.2 | 97.9 | Main Office | Present | 1.00 | Project deadline |
| 2025-11-08 | Friday | 09:00:00 | 18:00:00 | 8.00 | 60 | 99.0 | 98.1 | Main Office | Present | 0.00 | |
| 2025-11-09 | Saturday | | | | | | | | Absent | | Weekend |
| 2025-11-10 | Sunday | | | | | | | | Absent | | Weekend |

### Weekly Summary (Bottom of sheet)
```
WEEKLY SUMMARY
Total Days Present:      5
Total Hours Worked:      40.50
Average Daily Hours:     8.10
Late Arrivals:           1
Early Departures:        0
Overtime Hours:          1.25
Punctuality Score:       95.0%
Attendance Rate:         100.0%
```

## How It Works

### 1. **Sheet Creation (Automatic)**
When an employee punches in/out for the first time in a new week:

```python
# System automatically:
# 1. Checks if sheet exists for this employee-week
# 2. If not, creates new sheet: "EMP001_2025-W45"
# 3. Adds headers and employee info
# 4. Adds entry to Index sheet

await sheets_api.append_daily_record(
    spreadsheet_id=settings.GOOGLE_ATTENDANCE_SPREADSHEET_ID,
    employee_id="EMP001",
    employee_name="John Doe",
    date=datetime(2025, 11, 7),
    punch_in_time=datetime(2025, 11, 7, 9, 0, 0),
    punch_out_time=datetime(2025, 11, 7, 18, 0, 0),
    biometric_score_in=98.5,
    biometric_score_out=97.2,
    location="Main Office",
    status="Present"
)
```

### 2. **Daily Updates**
Every day, a new row is added to the employee's current week sheet with:
- Punch in/out times
- Total hours calculated automatically
- Break duration estimated
- Biometric match scores
- Status (Present, Late, Absent)

### 3. **Weekly Summary**
At the end of each week (Sunday night or Monday morning), the system:
- Calculates weekly metrics
- Appends summary section to the bottom of the sheet
- Creates a new sheet for the next week

## Benefits

### ✅ **Privacy & Security**
- Each employee's data is isolated in their own sheet
- Easy to grant access: just share specific sheets with managers
- Example: Manager of Team A only sees Team A employee sheets

### ✅ **Easy Navigation**
- HR can quickly jump to any employee's specific week
- Use Index sheet to find the right tab
- No scrolling through thousands of rows

### ✅ **Clean & Organized**
- Each sheet has only 7-14 rows (one week of data)
- Clear headers showing employee name and week range
- Summary at the bottom for quick insights

### ✅ **Scalable**
- No performance issues with large datasets
- Each sheet is independent
- Old weeks can be archived or deleted

### ✅ **Manager-Friendly**
- Managers can view their team's weekly attendance at a glance
- Copy/paste weekly data for reports
- Add comments/notes directly in the sheet

## Example Use Cases

### **Scenario 1: Check Employee's Current Week**
HR wants to see John Doe's attendance this week:
1. Open the spreadsheet
2. Click on the Index tab
3. Find "EMP001" for current week
4. Click the sheet link: `EMP001_2025-W45`
5. View daily attendance and summary

### **Scenario 2: Monthly Report**
Manager needs to report on team attendance for November:
1. Filter Index sheet by date range (November 1-30)
2. Get list of all relevant sheets
3. Open each employee's sheets for weeks 44, 45, 46, 47
4. Copy weekly summaries into report template

### **Scenario 3: Investigate Late Arrivals**
HR notices John Doe has been late 3 times:
1. Open his current week sheet: `EMP001_2025-W45`
2. Look at the "Punch In Time" column
3. See which days he arrived after 9:00 AM
4. Check the "Notes" column for reasons
5. Add a comment in the Notes column if needed

## Data Flow

```
Employee Punches In
      ↓
CloudABIS Verifies Biometric
      ↓
API Receives punch data
      ↓
Check if employee's week sheet exists
      ↓
If NO: Create new sheet (EMP001_2025-W45)
      ↓
If YES: Open existing sheet
      ↓
Add/Update daily record row
      ↓
Google Sheets updates in real-time
      ↓
HR/Managers see updated data instantly
```

## Technical Details

### Creating a New Employee Week Sheet
```python
sheet_name = await sheets_api.create_employee_week_sheet(
    spreadsheet_id="your-spreadsheet-id",
    employee_id="EMP001",
    employee_name="John Doe",
    week_start=datetime(2025, 11, 4)  # Monday
)
# Returns: "EMP001_2025-W45"
```

### Adding Daily Record
```python
await sheets_api.append_daily_record(
    spreadsheet_id="your-spreadsheet-id",
    employee_id="EMP001",
    employee_name="John Doe",
    date=datetime(2025, 11, 7),
    punch_in_time=datetime(2025, 11, 7, 9, 0, 0),
    punch_out_time=datetime(2025, 11, 7, 18, 0, 0),
    biometric_score_in=98.5,
    biometric_score_out=97.2,
    location="Main Office",
    status="Present",
    notes=""
)
```

### Retrieving Week Data
```python
records = await sheets_api.get_employee_week_data(
    spreadsheet_id="your-spreadsheet-id",
    employee_id="EMP001",
    week_start=datetime(2025, 11, 4)
)
# Returns list of daily records for that week
```

### Adding Weekly Summary
```python
summary_data = {
    "days_present": 5,
    "total_hours": 40.5,
    "avg_daily_hours": 8.1,
    "late_arrivals": 1,
    "early_departures": 0,
    "overtime_hours": 1.25,
    "punctuality_score": 95.0,
    "attendance_rate": 100.0
}

await sheets_api.append_weekly_summary(
    spreadsheet_id="your-spreadsheet-id",
    employee_id="EMP001",
    employee_name="John Doe",
    week_start=datetime(2025, 11, 4),
    summary_data=summary_data
)
```

## Comparison: Old vs New Structure

### ❌ Old Structure (All in One Sheet)
```
Punch Records Sheet (10,000+ rows)
Employee ID | Punch Type | Punch Time           | ...
EMP001     | IN         | 2025-11-04 09:00:00  | ...
EMP001     | OUT        | 2025-11-04 18:00:00  | ...
EMP002     | IN         | 2025-11-04 08:45:00  | ...
EMP001     | IN         | 2025-11-05 09:15:00  | ...
...
```
**Problems**:
- Hard to find specific employee's data
- Slow to load with thousands of rows
- No clear week separation
- Privacy issues (everyone's data together)

### ✅ New Structure (One Sheet Per Employee Per Week)
```
Index Sheet
EMP001 | John Doe | 2025-11-04 | 2025-11-10 | EMP001_2025-W45

EMP001_2025-W45 Sheet
Date       | Day      | In Time  | Out Time | Hours
2025-11-04 | Monday   | 09:00:00 | 18:00:00 | 8.00
2025-11-05 | Tuesday  | 09:15:00 | 18:30:00 | 8.25
...
```
**Benefits**:
- Instant access to specific employee-week
- Fast loading (only 7-14 rows per sheet)
- Clear weekly view
- Better privacy control

## Next Steps

1. ✅ **Setup Complete** - Google Sheets integration implemented
2. 🔲 **Configure OAuth** - Set up Google Cloud credentials
3. 🔲 **Update Attendance Routes** - Modify punch-in/out to use new sheet structure
4. 🔲 **Test Sheet Creation** - Verify automatic sheet creation works
5. 🔲 **Add Scheduled Job** - Create weekly summary automation
6. 🔲 **Train HR Staff** - Show how to navigate employee week sheets

## Summary

**One sheet per employee per week** provides:
- 📊 **Better Organization**: Easy to find and navigate
- 🔒 **Privacy**: Isolate each employee's data
- ⚡ **Performance**: Smaller sheets load faster
- 📈 **Insights**: Weekly summaries at a glance
- 👥 **Collaboration**: Share specific sheets with managers
- 🎯 **Focus**: Clear weekly view for each employee

This structure is **perfect for weekly attendance tracking** while maintaining ease of access and strong data organization!
