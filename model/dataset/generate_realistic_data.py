"""
Generate realistic employee wellbeing dataset with 200-400 samples.
Based on real-world research and typical workplace metrics.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Number of samples to generate
NUM_SAMPLES = 300

def generate_realistic_data():
    """Generate realistic employee data based on research and typical workplace patterns."""
    
    data = []
    
    for i in range(NUM_SAMPLES):
        employee_id = f"EMP{str(i+1).zfill(3)}"
        
        # Employee demographics and role
        age = np.random.choice([25, 28, 30, 32, 35, 38, 40, 42, 45, 48, 50, 52, 55], 
                               p=[0.05, 0.08, 0.1, 0.12, 0.15, 0.12, 0.1, 0.08, 0.08, 0.05, 0.04, 0.02, 0.01])
        experience_years = min(age - 22, np.random.randint(1, age - 21))
        role = np.random.choice(['Developer', 'Senior Developer', 'Tech Lead', 'Manager', 'Designer', 'QA Engineer'],
                               p=[0.35, 0.25, 0.15, 0.10, 0.10, 0.05])
        
        # Work schedule patterns (realistic for tech companies)
        work_hours_per_day = np.random.normal(8.5, 1.2)  # Average 8.5 hours, some work more/less
        work_hours_per_day = np.clip(work_hours_per_day, 6, 12)
        
        days_worked_per_week = np.random.choice([5, 6], p=[0.85, 0.15])  # Most work 5 days
        
        # Overtime patterns (some employees consistently work overtime)
        is_overworker = random.random() < 0.25  # 25% are chronic overworkers
        if is_overworker:
            overtime_hours = np.random.uniform(5, 15)
        else:
            overtime_hours = np.random.uniform(0, 5)
        
        # Break patterns
        lunch_break_minutes = np.random.choice([30, 45, 60], p=[0.3, 0.5, 0.2])
        coffee_breaks_per_day = np.random.choice([0, 1, 2, 3], p=[0.1, 0.3, 0.4, 0.2])
        
        # Attendance patterns (realistic based on CloudABIS biometric)
        punctuality_score = np.random.beta(8, 2) * 100  # Most employees are punctual
        attendance_rate = np.random.beta(9, 1) * 100  # High attendance typical
        late_arrivals = int((100 - punctuality_score) / 10)
        biometric_match_score = np.random.uniform(85, 99.5)  # High match rates for enrolled users
        
        # Email metrics (based on typical corporate email patterns)
        emails_sent = int(np.random.gamma(3, 5))  # Right-skewed: most send 10-20, some send 50+
        emails_received = int(np.random.gamma(4, 8))  # Receive more than send
        email_response_time = np.random.lognormal(2.5, 0.8)  # Hours, log-normal distribution
        email_response_time = np.clip(email_response_time, 0.1, 48)
        after_hours_emails = int(emails_sent * np.random.uniform(0.05, 0.30))  # 5-30% after hours
        
        # Calendar/Meeting metrics (realistic for tech workers)
        meetings_per_week = int(np.random.gamma(2.5, 2))  # Average 5-7 meetings
        meetings_per_week = np.clip(meetings_per_week, 0, 25)
        meeting_hours = meetings_per_week * np.random.uniform(0.5, 1.5)  # 30-90 min per meeting
        meeting_acceptance_rate = np.random.beta(7, 2) * 100
        declined_meetings = int(meetings_per_week * (1 - meeting_acceptance_rate/100))
        
        # Focus time (inversely related to meetings)
        focus_time_hours = work_hours_per_day - (meeting_hours / days_worked_per_week) - (lunch_break_minutes / 60)
        focus_time_hours = np.clip(focus_time_hours, 2, 10)
        
        # Teams/Slack messaging patterns
        messages_sent = int(np.random.gamma(4, 8))  # 20-40 messages typical
        messages_received = int(messages_sent * np.random.uniform(1.2, 2.5))
        after_hours_messages = int(messages_sent * np.random.uniform(0.1, 0.35))
        response_time_minutes = np.random.lognormal(2, 1)  # Minutes, faster than email
        response_time_minutes = np.clip(response_time_minutes, 1, 180)
        reactions_given = int(messages_received * np.random.uniform(0.1, 0.4))
        
        # Status patterns (Teams/Slack presence)
        status_available_percentage = np.random.uniform(50, 85)
        status_busy_percentage = np.random.uniform(10, 30)
        status_away_percentage = 100 - status_available_percentage - status_busy_percentage
        
        # GitHub metrics (for developers)
        if role in ['Developer', 'Senior Developer', 'Tech Lead']:
            commits_per_week = int(np.random.gamma(3, 3))  # 5-15 commits typical
            commits_per_week = np.clip(commits_per_week, 1, 50)
            prs_created = max(1, int(commits_per_week / np.random.uniform(3, 8)))  # 1 PR per 3-8 commits
            prs_reviewed = int(np.random.gamma(2, 2))  # 2-6 reviews typical
            prs_reviewed = np.clip(prs_reviewed, 0, 20)
            code_review_time_hours = prs_reviewed * np.random.uniform(0.3, 1.5)
            pr_merge_rate = np.random.beta(8, 2) * 100  # Most PRs get merged
            avg_pr_size_lines = int(np.random.lognormal(4.5, 1))  # Log-normal: small PRs common, large ones rare
            avg_pr_size_lines = np.clip(avg_pr_size_lines, 20, 2000)
            github_pr_merge_time = np.random.lognormal(2, 0.8)  # Hours to merge
            github_pr_merge_time = np.clip(github_pr_merge_time, 1, 72)
        else:
            commits_per_week = 0
            prs_created = 0
            prs_reviewed = int(np.random.uniform(0, 3))  # Non-devs might review occasionally
            code_review_time_hours = prs_reviewed * 0.5
            pr_merge_rate = 0
            avg_pr_size_lines = 0
            github_pr_merge_time = 0
        
        # Jira/Asana task metrics
        tasks_assigned = int(np.random.gamma(2.5, 2))  # 3-7 tasks typical
        tasks_assigned = np.clip(tasks_assigned, 1, 20)
        tasks_completed_per_week = int(tasks_assigned * np.random.uniform(0.5, 1.2))
        task_completion_rate = min(100, (tasks_completed_per_week / tasks_assigned) * 100)
        overdue_tasks = max(0, int((tasks_assigned - tasks_completed_per_week) * np.random.uniform(0, 0.5)))
        avg_task_completion_time = np.random.lognormal(2.8, 0.7)  # Days
        avg_task_completion_time = np.clip(avg_task_completion_time, 0.5, 30)
        
        # Work logged (Jira timesheets)
        hours_logged = work_hours_per_day * days_worked_per_week * np.random.uniform(0.7, 1.1)
        
        # Project switching (context switching indicator)
        projects_active = np.random.choice([1, 2, 3, 4], p=[0.4, 0.35, 0.20, 0.05])
        context_switches_per_day = projects_active * np.random.uniform(2, 5)
        
        # Bug-related metrics
        bugs_reported = int(np.random.poisson(2))
        bugs_fixed = int(bugs_reported * np.random.uniform(0.5, 1.5))
        
        # Collaboration metrics
        document_edits = int(np.random.gamma(2, 3))  # Google Docs/Office edits
        shared_files = int(np.random.gamma(1.5, 2))
        
        # Work consistency (how regular their patterns are)
        work_pattern_consistency = np.random.beta(5, 2) * 100  # Higher = more consistent
        
        # Derived behavioral metrics
        after_hours_activity_ratio = (after_hours_emails + after_hours_messages) / (emails_sent + messages_sent + 1)
        communication_balance = messages_sent / (emails_sent + 1)  # Prefer chat vs email
        meeting_to_work_ratio = (meeting_hours * days_worked_per_week) / (work_hours_per_day * days_worked_per_week)
        
        # Productivity proxies
        code_commit_consistency = np.random.uniform(0.6, 1.0) if commits_per_week > 0 else 0
        task_velocity = tasks_completed_per_week / (work_hours_per_day * days_worked_per_week)
        
        # Collaboration scores
        collaboration_score = (prs_reviewed + reactions_given + shared_files) / 3
        peer_interaction_frequency = (messages_sent + reactions_given + prs_reviewed) / days_worked_per_week
        
        # Stress indicators
        message_after_hours_ratio = after_hours_messages / (messages_sent + 1)
        email_after_hours_ratio = after_hours_emails / (emails_sent + 1)
        weekend_work_hours = overtime_hours * np.random.uniform(0.2, 0.6) if overtime_hours > 5 else 0
        
        # Work-life balance indicators
        daily_active_hours = work_hours_per_day + (overtime_hours / days_worked_per_week)
        work_life_balance_score = 100 - (daily_active_hours - 8) * 8  # Decreases with longer hours
        work_life_balance_score = np.clip(work_life_balance_score, 20, 100)
        
        # Recovery metrics
        days_off_taken = np.random.poisson(0.5)  # Per month
        sick_days = np.random.poisson(0.3)
        
        # Technology/Tool usage
        tools_used = np.random.choice([3, 4, 5, 6, 7], p=[0.1, 0.2, 0.4, 0.2, 0.1])
        tool_switch_frequency = tools_used * np.random.uniform(5, 15)  # Switches per day
        
        # Learning/Growth indicators
        training_hours = np.random.gamma(1, 0.5)  # Hours per week
        documentation_contributions = int(np.random.poisson(1))
        
        # Manager/Team metrics
        team_size = np.random.choice([0, 3, 5, 8, 12], p=[0.7, 0.1, 0.1, 0.05, 0.05])  # 0 if not a manager
        one_on_ones_conducted = team_size if team_size > 0 else 0
        
        # Performance indicators
        deliverables_completed = tasks_completed_per_week + (prs_created * 0.5)
        quality_score = np.random.beta(7, 2) * 100  # Code review approval rate proxy
        
        # Communication patterns
        average_email_length = np.random.uniform(50, 300)  # Words
        average_message_length = np.random.uniform(10, 50)  # Words
        
        # Sentiment proxies (to be replaced by actual sentiment analysis later)
        sentiment_email_score = np.random.beta(6, 3) * 100  # Slightly positive bias
        sentiment_chat_score = np.random.beta(6, 3) * 100
        
        # Engagement metrics
        voluntary_contributions = int(np.random.poisson(1.5))  # Beyond assigned tasks
        initiative_score = np.random.beta(4, 4) * 100  # Self-started work
        
        # Network/Influence metrics
        unique_contacts_per_week = int(np.random.gamma(2, 3))
        cross_team_interactions = int(unique_contacts_per_week * np.random.uniform(0.2, 0.5))
        
        # Technical debt indicators (for developers)
        if role in ['Developer', 'Senior Developer', 'Tech Lead']:
            code_review_comments_received = int(prs_created * np.random.uniform(2, 8))
            refactoring_commits = int(commits_per_week * np.random.uniform(0.1, 0.3))
        else:
            code_review_comments_received = 0
            refactoring_commits = 0
        
        # Blockers/Dependencies
        blocked_time_hours = np.random.gamma(1, 0.5)  # Hours per week
        dependency_wait_time_hours = np.random.gamma(1.5, 1)
        
        # Innovation metrics
        new_ideas_proposed = int(np.random.poisson(0.8))
        experiments_run = int(np.random.poisson(0.5))
        
        # Response patterns
        avg_first_response_time_hours = email_response_time * np.random.uniform(0.3, 0.7)
        response_rate = np.random.beta(8, 2) * 100
        
        # Meeting quality indicators
        meeting_preparation_score = np.random.beta(4, 3) * 100
        meeting_participation_score = np.random.beta(5, 3) * 100
        
        # Focus/Interruption metrics
        interruptions_per_day = int(messages_received / days_worked_per_week * np.random.uniform(0.2, 0.4))
        deep_work_blocks = int(focus_time_hours / 2)  # Assume 2-hour blocks
        
        # Multitasking indicators
        concurrent_tasks = np.random.choice([1, 2, 3, 4], p=[0.3, 0.4, 0.2, 0.1])
        task_switching_rate = context_switches_per_day / work_hours_per_day
        
        # Deadline pressure
        urgent_tasks_percentage = np.random.uniform(10, 40)
        tasks_completed_early = int(tasks_completed_per_week * np.random.uniform(0.2, 0.6))
        
        # Knowledge sharing
        mentor_hours_per_week = np.random.gamma(1, 0.3) if experience_years > 3 else 0
        knowledge_base_contributions = int(np.random.poisson(0.5))
        
        # Process adherence
        process_compliance_score = np.random.beta(6, 2) * 100
        documentation_quality_score = np.random.beta(5, 3) * 100
        
        # Energy/Vitality proxies
        morning_productivity_score = np.random.beta(5, 3) * 100
        afternoon_productivity_score = np.random.beta(4, 4) * 100
        
        # Social connection
        informal_chats_per_week = int(np.random.gamma(2, 2))
        team_engagement_score = np.random.beta(5, 3) * 100
        
        # Autonomy/Control
        self_directed_work_percentage = np.random.uniform(30, 80)
        decision_making_authority_score = np.random.beta(4, 3) * 100
        
        # Feedback loops
        feedback_received_count = int(np.random.poisson(1))
        feedback_given_count = int(np.random.poisson(1.2))
        
        # Technical skills usage
        new_technologies_learned = int(np.random.poisson(0.3))
        skill_utilization_score = np.random.beta(6, 3) * 100
        
        # ===== TARGET VARIABLES =====
        # These are influenced by the features above to create realistic correlations
        
        # Burnout Risk Score (0-1): Higher with long hours, high stress, low balance
        burnout_risk = (
            (daily_active_hours - 8) * 0.05 +  # Long hours increase burnout
            (meeting_to_work_ratio * 0.3) +  # Too many meetings
            (after_hours_activity_ratio * 0.2) +  # After-hours work
            (1 - work_life_balance_score / 100) * 0.3 +  # Poor balance
            (overtime_hours / 20) * 0.1 +  # Overtime
            (context_switches_per_day / 20) * 0.05 +  # Context switching stress
            np.random.normal(0, 0.1)  # Random noise
        )
        burnout_risk = np.clip(burnout_risk, 0, 1)
        
        # Wellbeing Score (0-100): Higher with balance, engagement, positive interactions
        wellbeing = (
            work_life_balance_score * 0.3 +
            (attendance_rate / 100) * 15 +  # Good attendance
            (team_engagement_score / 100) * 20 +  # Social connection
            (1 - burnout_risk) * 25 +  # Inverse of burnout
            (focus_time_hours / 8) * 10 +  # Adequate focus time
            np.random.normal(0, 5)  # Noise
        )
        wellbeing = np.clip(wellbeing, 0, 100)
        
        # Efficiency Score (0-100): Productivity relative to hours worked
        efficiency = (
            (tasks_completed_per_week / (work_hours_per_day * days_worked_per_week / 5)) * 25 +  # Task velocity
            (task_completion_rate / 100) * 20 +  # Completion rate
            quality_score * 0.15 +  # Quality
            (focus_time_hours / daily_active_hours) * 20 +  # Focus ratio
            (1 - meeting_to_work_ratio) * 10 +  # Less meeting overhead
            (commits_per_week / 15) * 10 if commits_per_week > 0 else 5 +  # Code output
            np.random.normal(0, 5)  # Noise
        )
        efficiency = np.clip(efficiency, 0, 100)
        
        # Create employee record
        record = {
            'employee_id': employee_id,
            'age': age,
            'experience_years': experience_years,
            'role': role,
            'work_hours_per_day': round(work_hours_per_day, 2),
            'days_worked_per_week': days_worked_per_week,
            'overtime_hours': round(overtime_hours, 2),
            'lunch_break_minutes': lunch_break_minutes,
            'coffee_breaks_per_day': coffee_breaks_per_day,
            'punctuality_score': round(punctuality_score, 2),
            'attendance_rate': round(attendance_rate, 2),
            'late_arrivals': late_arrivals,
            'biometric_match_score': round(biometric_match_score, 2),
            'emails_sent': emails_sent,
            'emails_received': emails_received,
            'email_response_time': round(email_response_time, 2),
            'after_hours_emails': after_hours_emails,
            'meetings_per_week': meetings_per_week,
            'meeting_hours': round(meeting_hours, 2),
            'meeting_acceptance_rate': round(meeting_acceptance_rate, 2),
            'declined_meetings': declined_meetings,
            'focus_time_hours': round(focus_time_hours, 2),
            'messages_sent': messages_sent,
            'messages_received': messages_received,
            'after_hours_messages': after_hours_messages,
            'response_time_minutes': round(response_time_minutes, 2),
            'reactions_given': reactions_given,
            'status_available_percentage': round(status_available_percentage, 2),
            'status_busy_percentage': round(status_busy_percentage, 2),
            'status_away_percentage': round(status_away_percentage, 2),
            'commits_per_week': commits_per_week,
            'prs_created': prs_created,
            'prs_reviewed': prs_reviewed,
            'code_review_time_hours': round(code_review_time_hours, 2),
            'pr_merge_rate': round(pr_merge_rate, 2),
            'avg_pr_size_lines': avg_pr_size_lines,
            'github_pr_merge_time': round(github_pr_merge_time, 2),
            'tasks_assigned': tasks_assigned,
            'tasks_completed_per_week': tasks_completed_per_week,
            'task_completion_rate': round(task_completion_rate, 2),
            'overdue_tasks': overdue_tasks,
            'avg_task_completion_time': round(avg_task_completion_time, 2),
            'hours_logged': round(hours_logged, 2),
            'projects_active': projects_active,
            'context_switches_per_day': round(context_switches_per_day, 2),
            'bugs_reported': bugs_reported,
            'bugs_fixed': bugs_fixed,
            'document_edits': document_edits,
            'shared_files': shared_files,
            'work_pattern_consistency': round(work_pattern_consistency, 2),
            'after_hours_activity_ratio': round(after_hours_activity_ratio, 4),
            'communication_balance': round(communication_balance, 2),
            'meeting_to_work_ratio': round(meeting_to_work_ratio, 4),
            'code_commit_consistency': round(code_commit_consistency, 2),
            'task_velocity': round(task_velocity, 4),
            'collaboration_score': round(collaboration_score, 2),
            'peer_interaction_frequency': round(peer_interaction_frequency, 2),
            'message_after_hours_ratio': round(message_after_hours_ratio, 4),
            'email_after_hours_ratio': round(email_after_hours_ratio, 4),
            'weekend_work_hours': round(weekend_work_hours, 2),
            'daily_active_hours': round(daily_active_hours, 2),
            'work_life_balance_score': round(work_life_balance_score, 2),
            'days_off_taken': days_off_taken,
            'sick_days': sick_days,
            'tools_used': tools_used,
            'tool_switch_frequency': round(tool_switch_frequency, 2),
            'training_hours': round(training_hours, 2),
            'documentation_contributions': documentation_contributions,
            'team_size': team_size,
            'one_on_ones_conducted': one_on_ones_conducted,
            'deliverables_completed': round(deliverables_completed, 2),
            'quality_score': round(quality_score, 2),
            'average_email_length': round(average_email_length, 2),
            'average_message_length': round(average_message_length, 2),
            'sentiment_email_score': round(sentiment_email_score, 2),
            'sentiment_chat_score': round(sentiment_chat_score, 2),
            'voluntary_contributions': voluntary_contributions,
            'initiative_score': round(initiative_score, 2),
            'unique_contacts_per_week': unique_contacts_per_week,
            'cross_team_interactions': cross_team_interactions,
            'code_review_comments_received': code_review_comments_received,
            'refactoring_commits': refactoring_commits,
            'blocked_time_hours': round(blocked_time_hours, 2),
            'dependency_wait_time_hours': round(dependency_wait_time_hours, 2),
            'new_ideas_proposed': new_ideas_proposed,
            'experiments_run': experiments_run,
            'avg_first_response_time_hours': round(avg_first_response_time_hours, 2),
            'response_rate': round(response_rate, 2),
            'meeting_preparation_score': round(meeting_preparation_score, 2),
            'meeting_participation_score': round(meeting_participation_score, 2),
            'interruptions_per_day': interruptions_per_day,
            'deep_work_blocks': deep_work_blocks,
            'concurrent_tasks': concurrent_tasks,
            'task_switching_rate': round(task_switching_rate, 4),
            'urgent_tasks_percentage': round(urgent_tasks_percentage, 2),
            'tasks_completed_early': tasks_completed_early,
            'mentor_hours_per_week': round(mentor_hours_per_week, 2),
            'knowledge_base_contributions': knowledge_base_contributions,
            'process_compliance_score': round(process_compliance_score, 2),
            'documentation_quality_score': round(documentation_quality_score, 2),
            'morning_productivity_score': round(morning_productivity_score, 2),
            'afternoon_productivity_score': round(afternoon_productivity_score, 2),
            'informal_chats_per_week': informal_chats_per_week,
            'team_engagement_score': round(team_engagement_score, 2),
            'self_directed_work_percentage': round(self_directed_work_percentage, 2),
            'decision_making_authority_score': round(decision_making_authority_score, 2),
            'feedback_received_count': feedback_received_count,
            'feedback_given_count': feedback_given_count,
            'new_technologies_learned': new_technologies_learned,
            'skill_utilization_score': round(skill_utilization_score, 2),
            'burnout_risk_score': round(burnout_risk, 4),
            'wellbeing_score': round(wellbeing, 2),
            'efficiency_score': round(efficiency, 2)
        }
        
        data.append(record)
    
    return pd.DataFrame(data)


if __name__ == "__main__":
    print("Generating realistic employee wellbeing dataset...")
    print(f"Number of samples: {NUM_SAMPLES}")
    print()
    
    # Generate data
    df = generate_realistic_data()
    
    # Save to CSV
    output_file = "realistic_emp_data.csv"
    df.to_csv(output_file, index=False)
    
    print(f"✓ Dataset saved to {output_file}")
    print(f"✓ Total columns: {len(df.columns)}")
    print(f"✓ Total rows: {len(df)}")
    print()
    
    # Display statistics
    print("=== TARGET VARIABLE STATISTICS ===")
    print(f"Burnout Risk Score: mean={df['burnout_risk_score'].mean():.3f}, std={df['burnout_risk_score'].std():.3f}, range=[{df['burnout_risk_score'].min():.3f}, {df['burnout_risk_score'].max():.3f}]")
    print(f"Wellbeing Score: mean={df['wellbeing_score'].mean():.2f}, std={df['wellbeing_score'].std():.2f}, range=[{df['wellbeing_score'].min():.2f}, {df['wellbeing_score'].max():.2f}]")
    print(f"Efficiency Score: mean={df['efficiency_score'].mean():.2f}, std={df['efficiency_score'].std():.2f}, range=[{df['efficiency_score'].min():.2f}, {df['efficiency_score'].max():.2f}]")
    print()
    
    # Show sample data
    print("=== SAMPLE RECORDS (first 3 employees) ===")
    print(df[['employee_id', 'role', 'work_hours_per_day', 'overtime_hours', 
              'meetings_per_week', 'commits_per_week', 'tasks_completed_per_week',
              'burnout_risk_score', 'wellbeing_score', 'efficiency_score']].head(3))
    print()
    
    print("=== ROLE DISTRIBUTION ===")
    print(df['role'].value_counts())
    print()
    
    print("Dataset generation complete!")
