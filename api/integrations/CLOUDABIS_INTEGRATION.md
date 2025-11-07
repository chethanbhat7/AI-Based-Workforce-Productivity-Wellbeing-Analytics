# M2SYS CloudABIS Biometric Integration

## Overview
This integration connects to M2SYS CloudABIS for biometric identification and attendance tracking using fingerprint, face, or iris recognition.

## CloudABIS Setup

### 1. Account Setup
1. Sign up at [M2SYS CloudABIS](https://www.m2sys.com/cloudabis/)
2. Create a new application in the CloudABIS portal
3. Note your credentials:
   - **App Key**: Application identifier
   - **Secret Key**: Authentication secret
   - **Customer Key**: Your customer identifier

### 2. Configure Biometric Engine
Choose your biometric modality:
- **FACE**: Face recognition
- **FINGERPRINT**: Fingerprint scanning
- **IRIS**: Iris recognition
- **MULTIMODAL**: Combination of multiple biometrics

### 3. Environment Configuration
Add to `.env` file:
```env
CLOUDABIS_APP_KEY=your-app-key
CLOUDABIS_SECRET_KEY=your-secret-key
CLOUDABIS_CUSTOMER_KEY=your-customer-key
CLOUDABIS_BASE_URL=https://cloud.m2sys.com/CloudABIS/api
CLOUDABIS_ENGINE_NAME=FACE
```

## API Endpoints

### Base URL
```
https://cloud.m2sys.com/CloudABIS/api
```

### Authentication
CloudABIS uses Basic Authentication:
```
Authorization: Basic Base64(AppKey:SecretKey)
```

## Core Features

### 1. Employee Registration
Register employee biometric data for future identification.

```python
from integrations.cloudabis import cloudabis_api

# Register employee
result = await cloudabis_api.register_employee(
    employee_id="EMP001",
    biometric_data={
        "fingerprint": "base64_encoded_fingerprint_template",
        "face": "base64_encoded_face_image"
    }
)

# Response
{
    "success": True,
    "message": "Registration successful",
    "registration_id": "EMP001",
    "employee_id": "EMP001"
}
```

### 2. Employee Identification (1:N)
Identify who the person is from a biometric sample.

```python
# Identify from fingerprint
result = await cloudabis_api.identify_employee(
    biometric_sample="base64_encoded_sample",
    biometric_type="fingerprint"
)

# Response
{
    "success": True,
    "employee_id": "EMP001",
    "match_score": 95.7,
    "match_count": 1,
    "timestamp": "2025-11-07T10:30:00"
}
```

### 3. Employee Verification (1:1)
Verify if the person is who they claim to be.

```python
# Verify specific employee
result = await cloudabis_api.verify_employee(
    employee_id="EMP001",
    biometric_sample="base64_encoded_sample",
    biometric_type="face"
)

# Response
{
    "success": True,
    "verified": True,
    "match_score": 98.2,
    "employee_id": "EMP001"
}
```

### 4. Punch In (Clock In)
Record employee arrival with biometric verification.

```python
# Employee arrives and scans fingerprint
result = await cloudabis_api.record_punch_in(
    employee_id="EMP001",
    biometric_sample="base64_encoded_fingerprint",
    location="Main Office",
    device_id="DEVICE_01"
)

# Response
{
    "success": True,
    "punch_record": {
        "employee_id": "EMP001",
        "punch_type": "IN",
        "punch_time": "2025-11-07T09:05:23",
        "biometric_match_score": 96.5,
        "location": "Main Office",
        "device_id": "DEVICE_01",
        "verified": True
    },
    "message": "Punch-in successful"
}
```

### 5. Punch Out (Clock Out)
Record employee departure with biometric verification.

```python
# Employee leaves and scans fingerprint
result = await cloudabis_api.record_punch_out(
    employee_id="EMP001",
    biometric_sample="base64_encoded_fingerprint",
    location="Main Office",
    device_id="DEVICE_01"
)

# Response
{
    "success": True,
    "punch_record": {
        "employee_id": "EMP001",
        "punch_type": "OUT",
        "punch_time": "2025-11-07T18:02:15",
        "biometric_match_score": 97.1,
        "location": "Main Office",
        "device_id": "DEVICE_01",
        "verified": True
    },
    "message": "Punch-out successful"
}
```

### 6. Calculate Attendance Metrics
Generate attendance statistics from punch records.

```python
from datetime import datetime, timedelta

# Get metrics for last 30 days
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

metrics = await cloudabis_api.calculate_attendance_metrics(
    employee_id="EMP001",
    start_date=start_date,
    end_date=end_date
)

# Response
{
    "employee_id": "EMP001",
    "date_range": {
        "start": "2025-10-08T00:00:00",
        "end": "2025-11-07T00:00:00"
    },
    "total_days_present": 22,
    "total_days_expected": 22,
    "late_start_count_per_week": 1.2,
    "early_exit_count_per_week": 0.5,
    "total_hours_per_week": 42.3,
    "variance_in_work_hours": 1.8,
    "absenteeism_rate": 0.0,
    "avg_daily_hours": 8.5,
    "punctuality_score": 0.85,
    "overtime_hours": 10.5,
    "daily_hours_list": [8.2, 8.5, 9.1, ...]
}
```

### 7. Real-time Status
Check if employee is currently in office.

```python
# Get current status
status = await cloudabis_api.get_realtime_attendance_status(
    employee_id="EMP001"
)

# Response
{
    "employee_id": "EMP001",
    "status": "IN_OFFICE",  # IN_OFFICE, OUT, ON_BREAK
    "last_punch_time": "2025-11-07T09:05:23",
    "last_punch_type": "IN",
    "hours_today": 5.2
}
```

## Attendance Features Extracted

The CloudABIS integration provides these real-time attendance metrics:

### Daily Metrics
- `punch_in_time` - Exact login timestamp
- `punch_out_time` - Exact logout timestamp
- `total_logged_hours_day` - Hours between punch in/out
- `late_arrival_flag` - Boolean (late if after 9:00 AM)
- `early_departure_flag` - Boolean (early if before 5:00 PM)
- `break_duration_minutes` - Total break time
- `biometric_match_score` - Authentication confidence (0-100)
- `punch_location` - Location/branch identifier
- `attendance_status` - Present/Absent/Half-day
- `overtime_hours` - Hours beyond 8 hours

### Weekly/Monthly Aggregates
- `late_start_count_per_week` - Count of late arrivals
- `early_exit_count_per_week` - Count of early departures
- `total_hours_per_week` - Sum of daily hours
- `variance_in_work_hours` - Consistency metric
- `absenteeism_rate` - Absence percentage
- `avg_daily_hours` - Mean hours per day
- `punctuality_score` - On-time arrival percentage (0-1)

## Workflow Integration

### Complete Daily Workflow

```python
# 1. MORNING - Employee Arrives
punch_in = await cloudabis_api.record_punch_in(
    employee_id="EMP001",
    biometric_sample=fingerprint_scan,
    location="Main Office"
)

if punch_in["success"]:
    # Store punch record in database
    # Trigger data collection from other APIs:
    # - Microsoft Graph (calendar)
    # - Slack/Teams (messages)
    # - Jira/Asana (tasks)
    # - GitHub (commits)
    pass

# 2. DURING WORK - Monitor activity
# Continuous data collection from APIs happens in background

# 3. EVENING - Employee Leaves
punch_out = await cloudabis_api.record_punch_out(
    employee_id="EMP001",
    biometric_sample=fingerprint_scan
)

if punch_out["success"]:
    # Calculate daily metrics
    # Generate end-of-day report
    # Update ML features
    pass

# 4. WEEKLY - Generate Reports
metrics = await cloudabis_api.calculate_attendance_metrics(
    employee_id="EMP001",
    start_date=week_start,
    end_date=week_end
)
```

## Database Schema

### Punch Records Table
```sql
CREATE TABLE punch_records (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    punch_type VARCHAR(10) NOT NULL,  -- 'IN' or 'OUT'
    punch_time TIMESTAMP NOT NULL,
    biometric_match_score FLOAT,
    location VARCHAR(100),
    device_id VARCHAR(50),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_employee_date ON punch_records(employee_id, DATE(punch_time));
```

### Daily Attendance Summary Table
```sql
CREATE TABLE daily_attendance (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    punch_in_time TIMESTAMP,
    punch_out_time TIMESTAMP,
    total_hours FLOAT,
    late_arrival BOOLEAN,
    early_departure BOOLEAN,
    overtime_hours FLOAT,
    status VARCHAR(20),  -- 'present', 'absent', 'half_day'
    UNIQUE(employee_id, date)
);
```

## Security Considerations

### 1. Biometric Data Storage
- **DO NOT** store raw biometric images
- Store only:
  - Biometric templates (mathematical representation)
  - Match scores
  - Timestamps
  - Metadata

### 2. Privacy Compliance
- GDPR compliance:
  - Obtain employee consent
  - Allow data deletion requests
  - Provide data access reports
- BIPA (Illinois) compliance if applicable
- CCPA compliance for California employees

### 3. Data Encryption
- Encrypt biometric templates at rest
- Use HTTPS for all API calls
- Secure storage of CloudABIS credentials

### 4. Audit Logging
```python
# Log all biometric operations
{
    "timestamp": "2025-11-07T09:05:23",
    "operation": "IDENTIFY",
    "employee_id": "EMP001",
    "success": True,
    "match_score": 96.5,
    "ip_address": "192.168.1.100",
    "device_id": "DEVICE_01"
}
```

## Error Handling

### Common Errors

1. **Verification Failed**
```python
{
    "success": False,
    "error": "VERIFICATION_FAILED",
    "message": "Biometric verification failed"
}
```

2. **Employee ID Mismatch**
```python
{
    "success": False,
    "error": "ID_MISMATCH",
    "message": "Employee ID mismatch"
}
```

3. **Low Match Score**
```python
{
    "success": False,
    "error": "LOW_CONFIDENCE",
    "message": "Biometric match score below threshold"
}
```

## Testing

### Test Employee Registration
```bash
curl -X POST https://cloud.m2sys.com/CloudABIS/api/Register \
  -H "Authorization: Basic <your-base64-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "CustomerKey": "your-customer-key",
    "EngineName": "FACE",
    "RegistrationID": "TEST001",
    "Format": "ISO",
    "BiometricXml": "<BiometricData><Face>...</Face></BiometricData>"
  }'
```

### Test Identification
```bash
curl -X POST https://cloud.m2sys.com/CloudABIS/api/Identify \
  -H "Authorization: Basic <your-base64-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "CustomerKey": "your-customer-key",
    "EngineName": "FACE",
    "Format": "ISO",
    "BiometricXml": "<BiometricData><Face>...</Face></BiometricData>"
  }'
```

## Rate Limits

- **Standard Plan**: 1,000 API calls/day
- **Professional Plan**: 10,000 API calls/day
- **Enterprise Plan**: Unlimited

## Cost Considerations

Typical CloudABIS pricing (contact M2SYS for exact pricing):
- Registration: ~$0.10 per employee (one-time)
- Identification: ~$0.02 per scan
- Storage: ~$0.50 per employee per month

For 100 employees with 2 scans/day:
- Monthly scans: 100 × 2 × 22 = 4,400
- Monthly cost: ~$88 + $50 = ~$138/month

## Next Steps

1. **Set up CloudABIS account** and get credentials
2. **Choose biometric modality** (Face recommended for ease of use)
3. **Design punch record database** schema
4. **Create attendance API routes** in FastAPI
5. **Build frontend** for biometric capture
6. **Test with sample employees**
7. **Deploy biometric devices** at office entrances

## Support

- CloudABIS Documentation: https://docs.m2sys.com
- API Reference: https://cloud.m2sys.com/CloudABIS/Help
- Support Email: support@m2sys.com
- Phone: +1-770-393-0986
