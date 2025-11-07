# Burnout Feature Testing Guide

## Test Scenarios Configured

The system now has **5 predefined test scenarios** based on email patterns to easily test the burnout alert feature:

### Scenario 1: BURNT OUT Member (member1@...)
- **Wellbeing Score**: 45 (< 60 - BURNT OUT ❌)
- **Stress Level**: HIGH
- **Task Completion**: 55% (< 75% - NOT eligible to help)
- **Status**: Will appear as burnt out, will NOT receive burnout alerts

### Scenario 2: CAPABLE HELPER (member2@...)
- **Wellbeing Score**: 85 (>= 60 - HEALTHY ✅)
- **Stress Level**: LOW
- **Task Completion**: 92% (> 75% - ELIGIBLE to help ✅)
- **Status**: WILL receive burnout alerts for member1 and member5

### Scenario 3: STRUGGLING Member (member3@...)
- **Wellbeing Score**: 68 (>= 60 - HEALTHY ✅)
- **Stress Level**: MEDIUM
- **Task Completion**: 65% (< 75% - NOT eligible to help)
- **Status**: Not burnt out, but NOT eligible to help

### Scenario 4: PRODUCTIVE Member (member4@...)
- **Wellbeing Score**: 78 (>= 60 - HEALTHY ✅)
- **Stress Level**: LOW
- **Task Completion**: 88% (> 75% - ELIGIBLE to help ✅)
- **Status**: WILL receive burnout alerts for member1 and member5

### Scenario 5: STRESSED Member (member5@...)
- **Wellbeing Score**: 55 (< 60 - BURNT OUT ❌)
- **Stress Level**: HIGH
- **Task Completion**: 82% (> 75% but still burnt out)
- **Status**: Will appear as burnt out, will NOT receive burnout alerts

---

## Testing Steps

### Step 1: Register Test Users (Team 1)

Register these users to test all scenarios:

1. **member1@test.com** (Burnt Out)
   - Password: password123
   - Name: Burnt Out Member
   - Team: 1

2. **member2@test.com** (Capable Helper)
   - Password: password123
   - Name: Helpful Member
   - Team: 1

3. **member3@test.com** (Struggling)
   - Password: password123
   - Name: Struggling Member
   - Team: 1

4. **member4@test.com** (Productive)
   - Password: password123
   - Name: Productive Member
   - Team: 1

5. **member5@test.com** (Stressed)
   - Password: password123
   - Name: Stressed Member
   - Team: 1

6. **supervisor1@test.com** (Supervisor)
   - Password: password123
   - Name: Team Supervisor
   - Team: 1

### Step 2: Verify Burnout Display

**Login as Supervisor** (supervisor1@test.com):
- Go to "Team Overview" tab
- You should see:
  - ✅ Member1 - RED border, "Exhausted" chip, Wellbeing: 45
  - ✅ Member2 - GREEN border, Wellbeing: 85, Task Completion: 92%
  - ✅ Member3 - Wellbeing: 68, Task Completion: 65%
  - ✅ Member4 - Wellbeing: 78, Task Completion: 88%
  - ✅ Member5 - RED border, "Exhausted" chip, Wellbeing: 55

### Step 3: Test Notification Eligibility

**WHO GETS NOTIFICATIONS:**

**Login as Member2** (Capable Helper):
- Click bell icon 🔔
- Should see 2 notifications:
  1. "Burnt Out Member is experiencing high stress/burnout..."
  2. "Stressed Member is experiencing high stress/burnout..."
- Each notification has "Volunteer to Help" button ✅

**Login as Member4** (Productive):
- Click bell icon 🔔
- Should see 2 notifications (same as Member2) ✅

**WHO DOES NOT GET NOTIFICATIONS:**

**Login as Member1** (Burnt Out):
- Click bell icon 🔔
- Should see NO burnout alerts (because they're burnt out themselves) ❌

**Login as Member3** (Struggling):
- Click bell icon 🔔
- Should see NO burnout alerts (task completion too low: 65% < 75%) ❌

**Login as Member5** (Stressed):
- Click bell icon 🔔
- Should see NO burnout alerts (burnt out themselves) ❌

### Step 4: Test Volunteer Workflow

**Login as Member2**:
1. Click bell icon
2. Click "Volunteer to Help" on Member1's notification
3. Notification should disappear
4. Success!

**Login as Supervisor1**:
1. Click bell icon
2. Should see new notification:
   - "Helpful Member has volunteered to help Burnt Out Member who is experiencing high stress/burnout."

**Login as Member1**:
1. Click bell icon
2. Should see new notification:
   - "Helpful Member has offered to help you with some tasks. Your supervisor has been notified."

---

## Expected Results Summary

| Email            | Wellbeing | Stress | Task% | Gets Alerts? | Reason                              |
|------------------|-----------|--------|-------|--------------|-------------------------------------|
| member1@test.com | 45        | HIGH   | 55%   | ❌ NO        | Burnt out                           |
| member2@test.com | 85        | LOW    | 92%   | ✅ YES       | Healthy + High completion           |
| member3@test.com | 68        | MEDIUM | 65%   | ❌ NO        | Low task completion (< 75%)         |
| member4@test.com | 78        | LOW    | 88%   | ✅ YES       | Healthy + High completion           |
| member5@test.com | 55        | HIGH   | 82%   | ❌ NO        | Burnt out (despite high completion) |

---

## Testing the Feature

1. ✅ Clear localStorage: Open DevTools → Application → Storage → Clear Site Data
2. ✅ Register all 6 test users above
3. ✅ Login as each member and check notification count
4. ✅ Verify only Member2 and Member4 get burnout alerts
5. ✅ Test volunteering workflow
6. ✅ Verify supervisor receives volunteer notification

**App URL**: http://localhost:5174

The feature is fully configured and ready to test! 🎯
