# Quick Testing Steps for Burnout Alert System

## 🚀 Step-by-Step Testing Guide

### 1. Register Test Accounts (6 Total)

**Navigate to:** http://localhost:5175

#### Register 5 Members (All Team 1):
1. **member1@test.com** (Password: test123)
   - Name: Test Member 1
   - Team Number: 1
   - Role: Member
   - Expected: Burnt out (Wellbeing: 45, High stress, 55% completion)

2. **member2@test.com** (Password: test123)
   - Name: Test Member 2
   - Team Number: 1
   - Role: Member
   - Expected: Capable helper (Wellbeing: 85, Low stress, 92% completion) ✅ ELIGIBLE

3. **member3@test.com** (Password: test123)
   - Name: Test Member 3
   - Team Number: 1
   - Role: Member
   - Expected: Struggling (Wellbeing: 68, Medium stress, 65% completion) ❌ NOT ELIGIBLE

4. **member4@test.com** (Password: test123)
   - Name: Test Member 4
   - Team Number: 1
   - Role: Member
   - Expected: Productive (Wellbeing: 78, Low stress, 88% completion) ✅ ELIGIBLE

5. **member5@test.com** (Password: test123)
   - Name: Test Member 5
   - Team Number: 1
   - Role: Member
   - Expected: Stressed (Wellbeing: 55, High stress, 82% completion) ❌ NOT ELIGIBLE

#### Register 1 Supervisor:
6. **supervisor1@test.com** (Password: test123)
   - Name: Test Supervisor 1
   - Team Number: 1
   - Role: Supervisor

---

### 2. Verify Burnout Detection

**Login as:** supervisor1@test.com

**Check Team Overview:**
- Should see 5 team members
- **member1** should have RED border (burnt out)
- **member5** should have RED border (stressed)
- member2, member3, member4 should have NORMAL borders

**Expected Values:**
- member1: Wellbeing 45, High stress
- member2: Wellbeing 85, Low stress
- member3: Wellbeing 68, Medium stress
- member4: Wellbeing 78, Low stress
- member5: Wellbeing 55, High stress

---

### 3. Test Notification Eligibility

#### Test A: Login as member2 (ELIGIBLE)
**Expected:** 🔔 Should see **2 burnout alerts** in notification bell
- Alert 1: "member1@test.com needs help with workload"
- Alert 2: "member5@test.com needs help with workload"
- Both should have "Volunteer to Help" button

#### Test B: Login as member4 (ELIGIBLE)
**Expected:** 🔔 Should see **2 burnout alerts** in notification bell
- Alert 1: "member1@test.com needs help with workload"
- Alert 2: "member5@test.com needs help with workload"

#### Test C: Login as member1 (BURNT OUT - NOT ELIGIBLE)
**Expected:** ❌ Should see **0 burnout alerts**
- No notifications (user is burnt out themselves)

#### Test D: Login as member3 (LOW COMPLETION - NOT ELIGIBLE)
**Expected:** ❌ Should see **0 burnout alerts**
- No notifications (task completion 65% < 75% threshold)

#### Test E: Login as member5 (BURNT OUT - NOT ELIGIBLE)
**Expected:** ❌ Should see **0 burnout alerts**
- No notifications (user is stressed themselves)

---

### 4. Test Volunteer Workflow

**Login as:** member2@test.com

1. Click the 🔔 bell icon (should show badge with "2")
2. Click on member1's burnout alert
3. Click "Volunteer to Help" button
4. Alert should disappear from member2's notifications

**Login as:** supervisor1@test.com

5. Click the 🔔 bell icon
6. Should see notification: "Test Member 2 volunteered to help member1@test.com"

**Login as:** member1@test.com

7. Click the 🔔 bell icon
8. Should see notification: "Good news! member2@test.com volunteered to help you"

---

### 5. Clear Notifications for Fresh Testing

**Browser DevTools:**
1. Press F12
2. Go to Application tab
3. Storage → Local Storage → http://localhost:5175
4. Find keys starting with `burnout_check_`
5. Right-click → Clear
6. Refresh page

---

## ✅ Expected Results Summary

| User | Wellbeing | Task Completion | Status | Alerts Received | Can Volunteer? |
|------|-----------|-----------------|--------|-----------------|----------------|
| member1 | 45 | 55% | 🔴 Burnt Out | 0 | ❌ No |
| member2 | 85 | 92% | ✅ Healthy | 2 (for member1, member5) | ✅ Yes |
| member3 | 68 | 65% | 🟡 Low Completion | 0 | ❌ No |
| member4 | 78 | 88% | ✅ Productive | 2 (for member1, member5) | ✅ Yes |
| member5 | 55 | 82% | 🔴 Stressed | 0 | ❌ No |

---

## 🐛 Troubleshooting

**If notifications don't appear:**
1. Check localStorage was cleared (burnout check runs once per day)
2. Logout and login again to trigger BurnoutNotificationService
3. Check browser console for errors (F12)
4. Verify all users are in Team 1

**If wellbeing scores don't match:**
1. Ensure exact email addresses: member1@test.com (not member1@gmail.com)
2. Refresh the page
3. Check WellbeingProfile.tsx is using getTestScenarioValues()

**If team members don't show:**
1. Verify supervisor and members have matching team numbers (all should be 1)
2. Check Firestore console to verify user documents were created
3. Refresh the supervisor dashboard

---

## 🎯 Success Criteria

✅ **Burnout Detection:** member1 and member5 show red borders in Team Overview
✅ **Smart Filtering:** Only member2 and member4 receive burnout alerts
✅ **Volunteer Flow:** Clicking "Volunteer" creates notifications for supervisor and burnt-out member
✅ **No Spam:** Alerts only sent once per day per user
✅ **Team Filtering:** Supervisor only sees Team 1 members

---

## 📝 Notes

- All test data is deterministic based on email patterns
- Notifications persist in Firestore (can be viewed in Firebase Console)
- LocalStorage prevents notification spam (one check per day per user)
- Real analytics data will override test scenarios when implemented
