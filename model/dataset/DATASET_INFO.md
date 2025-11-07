# Realistic Employee Wellbeing Dataset

## Overview
Generated 300 realistic employee records with 113 features based on real-world research and typical workplace patterns.

## Dataset Details
- **Total Samples**: 300 employees
- **Total Features**: 113 (110 input features + 3 target variables)
- **File**: `realistic_emp_data.csv`
- **Generation Date**: November 7, 2025

## Target Variables Statistics

| Variable | Mean | Std Dev | Range |
|----------|------|---------|-------|
| **Burnout Risk Score** | 0.342 | 0.179 | [0.000, 1.000] |
| **Wellbeing Score** | 76.61 | 8.68 | [47.27, 99.91] |
| **Efficiency Score** | 43.78 | 26.21 | [0.00, 100.00] |

## Role Distribution
- **Developer**: 103 (34.3%)
- **Senior Developer**: 74 (24.7%)
- **Tech Lead**: 42 (14.0%)
- **Manager**: 38 (12.7%)
- **Designer**: 31 (10.3%)
- **QA Engineer**: 12 (4.0%)

## Feature Categories

### 1. Demographics (3 features)
- age, experience_years, role

### 2. Work Schedule (8 features)
- work_hours_per_day, days_worked_per_week, overtime_hours
- lunch_break_minutes, coffee_breaks_per_day
- daily_active_hours, weekend_work_hours, days_off_taken

### 3. Attendance & Biometrics (5 features)
- punctuality_score, attendance_rate, late_arrivals
- biometric_match_score, sick_days

### 4. Email Communication (6 features)
- emails_sent, emails_received, email_response_time
- after_hours_emails, average_email_length, sentiment_email_score

### 5. Meetings & Calendar (8 features)
- meetings_per_week, meeting_hours, meeting_acceptance_rate
- declined_meetings, meeting_preparation_score, meeting_participation_score
- focus_time_hours, one_on_ones_conducted

### 6. Instant Messaging (8 features)
- messages_sent, messages_received, after_hours_messages
- response_time_minutes, reactions_given
- average_message_length, sentiment_chat_score, informal_chats_per_week

### 7. Status/Presence (3 features)
- status_available_percentage, status_busy_percentage, status_away_percentage

### 8. GitHub/Code (9 features)
- commits_per_week, prs_created, prs_reviewed
- code_review_time_hours, pr_merge_rate, avg_pr_size_lines
- github_pr_merge_time, code_review_comments_received, refactoring_commits

### 9. Task Management (8 features)
- tasks_assigned, tasks_completed_per_week, task_completion_rate
- overdue_tasks, avg_task_completion_time, urgent_tasks_percentage
- tasks_completed_early, concurrent_tasks

### 10. Project & Context (7 features)
- projects_active, context_switches_per_day, hours_logged
- bugs_reported, bugs_fixed, blocked_time_hours, dependency_wait_time_hours

### 11. Collaboration (9 features)
- document_edits, shared_files, collaboration_score
- peer_interaction_frequency, unique_contacts_per_week
- cross_team_interactions, team_engagement_score
- feedback_received_count, feedback_given_count

### 12. Productivity Patterns (11 features)
- work_pattern_consistency, code_commit_consistency, task_velocity
- deliverables_completed, quality_score
- morning_productivity_score, afternoon_productivity_score
- interruptions_per_day, deep_work_blocks, task_switching_rate

### 13. Work-Life Balance (6 features)
- after_hours_activity_ratio, message_after_hours_ratio, email_after_hours_ratio
- work_life_balance_score, self_directed_work_percentage, decision_making_authority_score

### 14. Learning & Growth (6 features)
- training_hours, documentation_contributions, knowledge_base_contributions
- new_technologies_learned, skill_utilization_score, mentor_hours_per_week

### 15. Tools & Technology (3 features)
- tools_used, tool_switch_frequency, process_compliance_score

### 16. Team Management (2 features)
- team_size, one_on_ones_conducted

### 17. Innovation & Initiative (4 features)
- voluntary_contributions, initiative_score
- new_ideas_proposed, experiments_run

### 18. Response & Communication (4 features)
- avg_first_response_time_hours, response_rate
- communication_balance, meeting_to_work_ratio

### 19. Documentation (2 features)
- documentation_quality_score, documentation_contributions

## Realistic Value Ranges (Based on Research)

### Work Hours
- **Normal work day**: 6-12 hours (mean: 8.5 hours)
- **Overtime**: 0-15 hours/week (25% are chronic overworkers with 5-15 hrs)
- **Meeting time**: 0-25 meetings/week (mean: 5-7), 30-90 min each

### Email Patterns
- **Sent**: 5-50+ emails/week (right-skewed distribution)
- **Received**: More than sent (1.2-2.5x ratio)
- **Response time**: 0.1-48 hours (log-normal distribution)
- **After hours**: 5-30% of total emails

### Messaging (Slack/Teams)
- **Messages sent**: 20-40/day typical
- **Response time**: 1-180 minutes (faster than email)
- **After hours**: 10-35% of messages

### Developer Metrics
- **Commits**: 1-50/week (mean: 5-15)
- **PRs created**: 1 PR per 3-8 commits
- **PRs reviewed**: 0-20/week (mean: 2-6)
- **PR size**: 20-2000 lines (log-normal: small PRs common)
- **Merge time**: 1-72 hours

### Task Management
- **Tasks assigned**: 1-20/week (mean: 3-7)
- **Completion rate**: 50-120% (some complete more than assigned)
- **Overdue tasks**: 0-50% of incomplete tasks

### Attendance
- **Punctuality**: Beta(8,2) - most employees are punctual
- **Attendance rate**: Beta(9,1) - high attendance typical (>85%)
- **Biometric match**: 85-99.5% (high accuracy for enrolled users)

## Correlations Built Into Data

### Burnout Risk ↑ when:
- Long work hours (daily_active_hours > 8)
- High meeting overhead (meeting_to_work_ratio)
- Frequent after-hours work
- Poor work-life balance
- Excessive context switching

### Wellbeing Score ↑ when:
- Good work-life balance
- High attendance rate
- Strong team engagement
- Low burnout risk
- Adequate focus time

### Efficiency Score ↑ when:
- High task completion velocity
- Good quality scores
- More focus time relative to total hours
- Lower meeting overhead
- Consistent code commits (for developers)

## Data Generation Approach

### Distributions Used:
- **Normal**: Work hours, break times
- **Beta**: Scores/percentages (punctuality, attendance, quality)
- **Gamma**: Count data (commits, tasks, meetings)
- **Log-normal**: Response times (skewed right)
- **Poisson**: Rare events (sick days, innovations)
- **Uniform**: Ratios and proportions

### Realistic Patterns:
1. **Role-based differences**: Developers have GitHub metrics, Managers have team metrics
2. **Overworker profile**: 25% work consistent overtime (5-15 hrs/week)
3. **Experience correlation**: Senior roles require years > 3
4. **Meeting burden**: Managers have more meetings than developers
5. **Email vs Chat**: Younger generations prefer chat (higher message ratio)

## Usage Examples

### Training Models
```python
import pandas as pd
from sklearn.model_selection import train_test_split

# Load data
df = pd.read_csv('realistic_emp_data.csv')

# Prepare features and targets
X = df.drop(['employee_id', 'burnout_risk_score', 'wellbeing_score', 'efficiency_score'], axis=1)
y_burnout = df['burnout_risk_score']
y_wellbeing = df['wellbeing_score']
y_efficiency = df['efficiency_score']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y_burnout, test_size=0.2, random_state=42)
```

### Analyzing Patterns
```python
# High burnout employees
high_burnout = df[df['burnout_risk_score'] > 0.7]
print(f"High burnout employees: {len(high_burnout)}")
print(f"Average work hours: {high_burnout['work_hours_per_day'].mean():.2f}")
print(f"Average overtime: {high_burnout['overtime_hours'].mean():.2f}")

# Most efficient employees
top_efficient = df.nlargest(10, 'efficiency_score')
print(f"\nTop 10 efficient employees:")
print(top_efficient[['employee_id', 'role', 'efficiency_score', 'task_velocity', 'focus_time_hours']])
```

## Key Improvements Over Previous Dataset
1. ✅ **Realistic distributions**: Used appropriate statistical distributions for each feature type
2. ✅ **Role-based logic**: Developers have GitHub metrics, non-developers don't
3. ✅ **Meaningful correlations**: Target variables influenced by relevant features
4. ✅ **Research-based ranges**: All values based on actual workplace studies
5. ✅ **Natural variation**: Added noise to prevent perfect correlations
6. ✅ **Edge cases**: Includes both high performers and struggling employees
7. ✅ **Temporal patterns**: After-hours work, weekend hours, consistency metrics

## Data Quality Notes
- All numeric values are rounded appropriately (2-4 decimal places)
- No missing values (complete dataset)
- All percentages sum correctly (e.g., status percentages = 100%)
- Logical constraints enforced (e.g., tasks_completed ≤ tasks_assigned * 1.2)
- Role-specific features set to 0 when not applicable

## Next Steps
1. Train three separate models using this data
2. Evaluate feature importance for each target
3. Compare with previous model8 results
4. Deploy best-performing models to API
5. Collect real API data to further improve models
