"""
Feature Extraction Utilities
Maps raw API data to ML features matching employee_data.csv schema
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import numpy as np
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    Extract ML features from raw API data
    
    Features extracted (matching employee_data.csv):
    - meeting_hours_per_week
    - meeting_counts_per_week
    - messages_sent_per_day
    - messages_received_per_day
    - avg_response_latency_min
    - communication_burstiness
    - after_hours_message_ratio
    - communication_balance
    - conversation_length_avg
    - avg_tasks_assigned_per_week
    - avg_tasks_completed_per_week
    - task_completion_rate
    - avg_task_age_days
    - overdue_task_ratio
    - task_comment_sentiment_mean
    - logged_hours_per_week
    - variance_in_work_hours
    - late_start_count_per_month
    - early_exit_count_per_month
    - absenteeism_rate
    - avg_break_length_minutes
    - performance_score
    - burnout_risk_score (computed by ML model)
    """
    
    def __init__(self):
        self.work_hours_start = 8  # 8 AM
        self.work_hours_end = 18  # 6 PM
    
    def extract_calendar_features(
        self,
        calendar_events: List[Dict],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """
        Extract meeting-related features from calendar events
        
        Returns:
        - meeting_hours_per_week
        - meeting_counts_per_week
        - after_hours_meeting_ratio
        - focus_time_hours_per_week
        """
        if not calendar_events:
            return {
                "meeting_hours_per_week": 0.0,
                "meeting_counts_per_week": 0.0,
                "after_hours_meeting_ratio": 0.0,
                "focus_time_hours_per_week": 40.0
            }
        
        total_meeting_hours = 0.0
        after_hours_meeting_hours = 0.0
        meeting_count = len(calendar_events)
        
        for event in calendar_events:
            # Parse event times
            start = datetime.fromisoformat(
                event.get("start", {}).get("dateTime", "").replace("Z", "+00:00")
            )
            end = datetime.fromisoformat(
                event.get("end", {}).get("dateTime", "").replace("Z", "+00:00")
            )
            
            # Calculate duration
            duration_hours = (end - start).total_seconds() / 3600
            total_meeting_hours += duration_hours
            
            # Check if after hours
            if start.hour < self.work_hours_start or start.hour >= self.work_hours_end:
                after_hours_meeting_hours += duration_hours
        
        # Calculate per week metrics
        days_in_range = (end_date - start_date).days + 1
        weeks = max(days_in_range / 7, 1)
        
        meeting_hours_per_week = total_meeting_hours / weeks
        meeting_counts_per_week = meeting_count / weeks
        after_hours_ratio = (
            after_hours_meeting_hours / total_meeting_hours 
            if total_meeting_hours > 0 else 0.0
        )
        
        # Estimate focus time (40 hours - meeting hours)
        focus_time = max(0, 40 - meeting_hours_per_week)
        
        return {
            "meeting_hours_per_week": round(meeting_hours_per_week, 2),
            "meeting_counts_per_week": round(meeting_counts_per_week, 1),
            "after_hours_meeting_ratio": round(after_hours_ratio, 3),
            "focus_time_hours_per_week": round(focus_time, 2)
        }
    
    def extract_communication_features(
        self,
        messages: List[Dict],
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """
        Extract communication features from messages (Slack/Teams)
        
        Returns:
        - messages_sent_per_day
        - messages_received_per_day
        - avg_response_latency_min
        - communication_burstiness
        - after_hours_message_ratio
        - communication_balance
        - conversation_length_avg
        """
        if not messages:
            return {
                "messages_sent_per_day": 0.0,
                "messages_received_per_day": 0.0,
                "avg_response_latency_min": 0.0,
                "communication_burstiness": 0.0,
                "after_hours_message_ratio": 0.0,
                "communication_balance": 1.0,
                "conversation_length_avg": 0.0
            }
        
        sent_count = 0
        received_count = 0
        after_hours_count = 0
        
        # For burstiness calculation (time between messages)
        message_times = []
        
        # For conversation length (thread depth)
        conversation_lengths = []
        
        # For response latency
        response_times = []
        
        for msg in messages:
            # Parse timestamp (handle both Slack and Teams formats)
            if "ts" in msg:  # Slack
                timestamp = datetime.fromtimestamp(float(msg["ts"]))
                msg_user = msg.get("user")
            elif "createdDateTime" in msg:  # Teams
                timestamp = datetime.fromisoformat(
                    msg["createdDateTime"].replace("Z", "+00:00")
                )
                msg_user = msg.get("from", {}).get("user", {}).get("id")
            else:
                continue
            
            # Count sent vs received
            if msg_user == user_id:
                sent_count += 1
            else:
                received_count += 1
            
            # Track message times for burstiness
            message_times.append(timestamp)
            
            # After hours check
            if timestamp.hour < self.work_hours_start or timestamp.hour >= self.work_hours_end:
                after_hours_count += 1
            
            # Conversation length (simplified - count replies)
            if msg.get("replyToId") or msg.get("thread_ts"):
                # This is a reply, add to conversation length tracking
                conversation_lengths.append(1)
        
        # Calculate per-day metrics
        days_in_range = max((end_date - start_date).days, 1)
        messages_sent_per_day = sent_count / days_in_range
        messages_received_per_day = received_count / days_in_range
        
        # Communication balance (sent / received ratio)
        communication_balance = (
            sent_count / received_count if received_count > 0 else 0.0
        )
        
        # After hours ratio
        total_messages = sent_count + received_count
        after_hours_ratio = (
            after_hours_count / total_messages if total_messages > 0 else 0.0
        )
        
        # Burstiness (variance in message timing)
        burstiness = 0.0
        if len(message_times) > 1:
            # Sort messages by time
            message_times.sort()
            
            # Calculate intervals between messages (in minutes)
            intervals = [
                (message_times[i+1] - message_times[i]).total_seconds() / 60
                for i in range(len(message_times) - 1)
            ]
            
            if intervals:
                mean_interval = np.mean(intervals)
                std_interval = np.std(intervals)
                # Burstiness coefficient
                burstiness = std_interval / mean_interval if mean_interval > 0 else 0.0
        
        # Average conversation length
        avg_conversation_length = (
            np.mean(conversation_lengths) if conversation_lengths else 5.0
        )
        
        # Response latency (simplified - random for now, would need thread analysis)
        # In production, analyze reply times in threads
        avg_response_latency = np.random.uniform(1, 20)
        
        return {
            "messages_sent_per_day": round(messages_sent_per_day, 1),
            "messages_received_per_day": round(messages_received_per_day, 1),
            "avg_response_latency_min": round(avg_response_latency, 1),
            "communication_burstiness": round(min(burstiness, 1.0), 2),
            "after_hours_message_ratio": round(after_hours_ratio, 3),
            "communication_balance": round(communication_balance, 2),
            "conversation_length_avg": round(avg_conversation_length, 1)
        }
    
    def extract_task_features(
        self,
        issues: List[Dict],
        account_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """
        Extract task management features from Jira/Asana data
        
        Returns:
        - avg_tasks_assigned_per_week
        - avg_tasks_completed_per_week
        - task_completion_rate
        - avg_task_age_days
        - overdue_task_ratio
        - task_comment_sentiment_mean
        """
        if not issues:
            return {
                "avg_tasks_assigned_per_week": 0.0,
                "avg_tasks_completed_per_week": 0.0,
                "task_completion_rate": 0.0,
                "avg_task_age_days": 0.0,
                "overdue_task_ratio": 0.0,
                "task_comment_sentiment_mean": 0.0
            }
        
        assigned_tasks = [
            task for task in issues 
            if task.get("assignee") == account_id
        ]
        
        completed_tasks = [
            task for task in assigned_tasks
            if task.get("status") in ["Done", "Resolved", "Closed", "completed"]
            or task.get("resolved") is not None
        ]
        
        # Calculate task ages
        task_ages = []
        overdue_count = 0
        
        now = datetime.utcnow()
        
        for task in assigned_tasks:
            # Parse created date
            created_str = task.get("created") or task.get("created_at")
            if created_str:
                created = datetime.fromisoformat(
                    created_str.replace("Z", "+00:00")
                )
                age_days = (now - created).days
                task_ages.append(age_days)
                
                # Check if overdue (simplified - task older than 30 days and not done)
                if age_days > 30 and task not in completed_tasks:
                    overdue_count += 1
        
        # Calculate per-week metrics
        weeks = max((end_date - start_date).days / 7, 1)
        
        avg_tasks_assigned = len(assigned_tasks) / weeks
        avg_tasks_completed = len(completed_tasks) / weeks
        
        completion_rate = (
            len(completed_tasks) / len(assigned_tasks) 
            if assigned_tasks else 0.0
        )
        
        avg_task_age = np.mean(task_ages) if task_ages else 0.0
        
        overdue_ratio = (
            overdue_count / len(assigned_tasks) 
            if assigned_tasks else 0.0
        )
        
        # Sentiment analysis placeholder (would use NLP on comments)
        # For now, random sentiment between -1 and 1
        task_comment_sentiment = np.random.uniform(-0.5, 0.5)
        
        return {
            "avg_tasks_assigned_per_week": round(avg_tasks_assigned, 1),
            "avg_tasks_completed_per_week": round(avg_tasks_completed, 1),
            "task_completion_rate": round(completion_rate, 2),
            "avg_task_age_days": round(avg_task_age, 1),
            "overdue_task_ratio": round(overdue_ratio, 2),
            "task_comment_sentiment_mean": round(task_comment_sentiment, 2)
        }
    
    def extract_worklog_features(
        self,
        worklogs: List[Dict],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """
        Extract work hours and attendance features from worklogs
        
        Returns:
        - logged_hours_per_week
        - variance_in_work_hours
        - late_start_count_per_month
        - early_exit_count_per_month
        - avg_break_length_minutes
        """
        if not worklogs:
            return {
                "logged_hours_per_week": 40.0,
                "variance_in_work_hours": 1.0,
                "late_start_count_per_month": 0.0,
                "early_exit_count_per_month": 0.0,
                "avg_break_length_minutes": 45.0
            }
        
        # Calculate total logged time
        total_seconds = sum(
            log.get("time_spent_seconds", 0) or log.get("timeSpentSeconds", 0)
            for log in worklogs
        )
        
        total_hours = total_seconds / 3600
        
        # Calculate per-week
        weeks = max((end_date - start_date).days / 7, 1)
        logged_hours_per_week = total_hours / weeks
        
        # Group by day to calculate variance
        daily_hours = defaultdict(float)
        
        for log in worklogs:
            started_str = log.get("started") or log.get("created_at")
            if started_str:
                started = datetime.fromisoformat(
                    started_str.replace("Z", "+00:00")
                )
                day_key = started.date()
                time_hours = (
                    log.get("time_spent_seconds", 0) or 
                    log.get("timeSpentSeconds", 0)
                ) / 3600
                daily_hours[day_key] += time_hours
        
        # Calculate variance
        if daily_hours:
            hours_list = list(daily_hours.values())
            variance = np.var(hours_list)
        else:
            variance = 1.0
        
        # Simplified attendance metrics (would need more detailed time tracking)
        # For now, use random values
        late_start_count = np.random.randint(0, 5)
        early_exit_count = np.random.randint(0, 3)
        avg_break_length = np.random.uniform(30, 60)
        
        return {
            "logged_hours_per_week": round(logged_hours_per_week, 1),
            "variance_in_work_hours": round(variance, 2),
            "late_start_count_per_month": late_start_count,
            "early_exit_count_per_month": early_exit_count,
            "avg_break_length_minutes": round(avg_break_length, 1)
        }
    
    def extract_github_features(
        self,
        github_stats: Dict,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """
        Extract GitHub contribution features
        
        Args:
            github_stats: Output from GitHubAPI.get_user_stats()
            start_date: Start date
            end_date: End date
        
        Returns:
            GitHub-based productivity features
        """
        if not github_stats:
            return {
                "github_commits_per_week": 0.0,
                "github_prs_per_week": 0.0,
                "github_pr_merge_rate": 0.0,
                "github_reviews_per_week": 0.0,
                "github_repo_context_switching": 0.0,
                "github_activity_consistency": 0.0
            }
        
        return {
            "github_commits_per_week": round(github_stats.get("commits_per_week", 0.0), 1),
            "github_prs_per_week": round(github_stats.get("prs_per_week", 0.0), 1),
            "github_pr_merge_rate": round(github_stats.get("pr_merge_rate", 0.0), 2),
            "github_reviews_per_week": round(github_stats.get("reviews_per_week", 0.0), 1),
            "github_repo_context_switching": github_stats.get("repo_context_switching", 0),
            "github_activity_consistency": round(github_stats.get("activity_consistency", 0.0), 2)
        }
    
    def calculate_performance_score(
        self,
        task_completion_rate: float,
        communication_balance: float,
        logged_hours_per_week: float
    ) -> float:
        """
        Calculate overall performance score (0-1)
        
        Weighted combination of:
        - Task completion rate (50%)
        - Communication balance (25%)
        - Work hours adherence (25%)
        """
        # Normalize communication balance (1.0 is ideal)
        comm_score = 1.0 - abs(1.0 - min(communication_balance, 2.0))
        
        # Normalize work hours (40 is ideal)
        hours_score = 1.0 - abs(40 - logged_hours_per_week) / 40
        hours_score = max(0, min(1, hours_score))
        
        # Weighted score
        performance = (
            0.5 * task_completion_rate +
            0.25 * comm_score +
            0.25 * hours_score
        )
        
        return round(performance, 2)
    
    def extract_all_features(
        self,
        calendar_events: List[Dict],
        messages: List[Dict],
        tasks: List[Dict],
        worklogs: List[Dict],
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        attendance_records: Optional[List[Dict]] = None,
        github_stats: Optional[Dict] = None
    ) -> Dict[str, float]:
        """
        Extract all features from all data sources
        
        Returns a complete feature dictionary matching employee_data.csv schema
        
        Args:
            github_stats: Optional GitHub statistics from GitHubAPI.get_user_stats()
        """
        # Extract features from each source
        calendar_features = self.extract_calendar_features(
            calendar_events, start_date, end_date
        )
        
        comm_features = self.extract_communication_features(
            messages, user_id, start_date, end_date
        )
        
        task_features = self.extract_task_features(
            tasks, user_id, start_date, end_date
        )
        
        worklog_features = self.extract_worklog_features(
            worklogs, start_date, end_date
        )
        
        absenteeism_rate = self.calculate_absenteeism_rate(
            attendance_records or [], start_date, end_date
        )
        
        # Extract GitHub features if available
        github_features = self.extract_github_features(
            github_stats or {}, start_date, end_date
        )
        
        # Calculate performance score
        performance_score = self.calculate_performance_score(
            task_features["task_completion_rate"],
            comm_features["communication_balance"],
            worklog_features["logged_hours_per_week"]
        )
        
        # Combine all features
        features = {
            **calendar_features,
            **comm_features,
            **task_features,
            **worklog_features,
            **github_features,
            "absenteeism_rate": absenteeism_rate,
            "performance_score": performance_score,
            # Burnout risk will be calculated by ML model
            "burnout_risk_score": 0.0  # Placeholder
        }
        
        # Remove focus_time as it's not in the CSV
        features.pop("focus_time_hours_per_week", None)
        features.pop("after_hours_meeting_ratio", None)
        
        return features


# Singleton instance
feature_extractor = FeatureExtractor()
