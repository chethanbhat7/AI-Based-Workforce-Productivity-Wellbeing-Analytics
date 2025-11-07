"""
Feature Extraction Service
Transforms raw API data into model input features
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    Extracts ML features from integrated workplace data sources
    """

    @staticmethod
    def extract_meeting_features(calendar_events: List[Dict]) -> Dict:
        """
        Extract meeting-related features from calendar events

        Returns:
            - meeting_hours_per_week
            - meeting_counts_per_week
        """
        if not calendar_events:
            return {
                "meeting_hours_per_week": 0.0,
                "meeting_counts_per_week": 0
            }

        total_hours = 0.0
        meeting_count = 0

        for event in calendar_events:
            # Skip all-day events
            if event.get("isAllDay"):
                continue

            # Parse start and end times
            start = event.get("start", {})
            end = event.get("end", {})

            if start.get("dateTime") and end.get("dateTime"):
                start_dt = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(end["dateTime"].replace("Z", "+00:00"))

                # Calculate duration in hours
                duration = (end_dt - start_dt).total_seconds() / 3600
                total_hours += duration
                meeting_count += 1

        # Calculate weeks from date range
        if calendar_events:
            dates = []
            for event in calendar_events:
                start = event.get("start", {})
                if start.get("dateTime"):
                    dt = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
                    dates.append(dt)

            if dates:
                weeks = max((max(dates) - min(dates)).days / 7, 1)
            else:
                weeks = 1
        else:
            weeks = 1

        return {
            "meeting_hours_per_week": round(total_hours / weeks, 2),
            "meeting_counts_per_week": int(meeting_count / weeks)
        }

    @staticmethod
    def extract_communication_features(
        messages: List[Dict],
        source: str = "teams"  # "teams" or "slack"
    ) -> Dict:
        """
        Extract communication-related features from messages

        Returns:
            - messages_sent_per_week
            - messages_received_per_week
            - avg_response_latency_min
            - communication_burstiness
            - after_hours_message_ratio
            - communication_balance
            - conversation_length_avg
        """
        if not messages:
            return {
                "messages_sent_per_week": 0,
                "messages_received_per_week": 0,
                "avg_response_latency_min": 0.0,
                "communication_burstiness": 0.0,
                "after_hours_message_ratio": 0.0,
                "communication_balance": 1.0,
                "conversation_length_avg": 0.0
            }

        # Parse messages based on source
        sent_messages = []
        received_messages = []
        timestamps = []

        for msg in messages:
            if source == "teams":
                created = msg.get("createdDateTime")
                if created:
                    dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    timestamps.append(dt)

                    # Check if user sent or received
                    from_user = msg.get("from", {})
                    # For now, assume all are sent (would need user ID comparison)
                    sent_messages.append(msg)

            elif source == "slack":
                ts = msg.get("ts")
                if ts:
                    dt = datetime.fromtimestamp(float(ts))
                    timestamps.append(dt)
                    sent_messages.append(msg)

        # Calculate weeks
        if timestamps:
            weeks = max((max(timestamps) - min(timestamps)).days / 7, 1)
        else:
            weeks = 1

        # Messages per week
        messages_sent = len(sent_messages)
        messages_received = len(received_messages) if received_messages else int(messages_sent * 1.2)  # Estimate

        # After-hours ratio (before 8am or after 6pm)
        after_hours_count = 0
        for dt in timestamps:
            if dt.hour < 8 or dt.hour >= 18:
                after_hours_count += 1

        after_hours_ratio = after_hours_count / len(timestamps) if timestamps else 0

        # Communication balance (sent / received)
        comm_balance = messages_sent / messages_received if messages_received > 0 else 1.0

        # Burstiness (variance in message timing)
        if len(timestamps) > 1:
            # Calculate time gaps in minutes
            sorted_times = sorted(timestamps)
            gaps = [(sorted_times[i+1] - sorted_times[i]).total_seconds() / 60
                   for i in range(len(sorted_times) - 1)]

            if gaps:
                mean_gap = np.mean(gaps)
                std_gap = np.std(gaps)
                burstiness = std_gap / mean_gap if mean_gap > 0 else 0
            else:
                burstiness = 0
        else:
            burstiness = 0

        # Average conversation length (messages per thread)
        # Simplified: assume avg thread has 10-15 messages
        conversation_length = 12.0  # Default estimate

        # Response latency (simplified estimate)
        response_latency = 10.0  # Default 10 minutes

        return {
            "messages_sent_per_week": int(messages_sent / weeks),
            "messages_received_per_week": int(messages_received / weeks),
            "avg_response_latency_min": round(response_latency, 2),
            "communication_burstiness": round(min(burstiness, 1.0), 2),
            "after_hours_message_ratio": round(after_hours_ratio, 3),
            "communication_balance": round(comm_balance, 2),
            "conversation_length_avg": round(conversation_length, 1)
        }

    @staticmethod
    def extract_task_features(
        tasks: List[Dict],
        source: str = "jira"  # "jira" or "asana"
    ) -> Dict:
        """
        Extract task management features

        Returns:
            - avg_tasks_assigned_per_week
            - avg_tasks_completed_per_week
            - task_completion_rate
            - avg_task_age_days
            - overdue_task_ratio
            - task_comment_sentiment_mean
        """
        if not tasks:
            return {
                "avg_tasks_assigned_per_week": 0,
                "avg_tasks_completed_per_week": 0,
                "task_completion_rate": 0.0,
                "avg_task_age_days": 0.0,
                "overdue_task_ratio": 0.0,
                "task_comment_sentiment_mean": 0.0
            }

        completed_tasks = []
        task_ages = []
        overdue_count = 0

        for task in tasks:
            if source == "jira":
                status = task.get("status", "").lower()
                created = task.get("created")
                resolved = task.get("resolved")

                # Check if completed
                if status in ["done", "resolved", "closed"]:
                    completed_tasks.append(task)

                # Calculate task age
                if created:
                    created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))

                    if resolved:
                        resolved_dt = datetime.fromisoformat(resolved.replace("Z", "+00:00"))
                        age = (resolved_dt - created_dt).days
                    else:
                        age = (datetime.now() - created_dt).days

                    task_ages.append(age)

                # Check if overdue (simplified)
                if status not in ["done", "resolved", "closed"]:
                    if created:
                        created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        if (datetime.now() - created_dt).days > 14:
                            overdue_count += 1

            elif source == "asana":
                completed = task.get("completed", False)
                created = task.get("created_at")
                completed_at = task.get("completed_at")

                if completed:
                    completed_tasks.append(task)

                # Calculate age
                if created:
                    created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))

                    if completed_at:
                        completed_dt = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                        age = (completed_dt - created_dt).days
                    else:
                        age = (datetime.now() - created_dt).days

                    task_ages.append(age)

                # Check overdue
                due_on = task.get("due_on")
                if not completed and due_on:
                    due_dt = datetime.fromisoformat(due_on)
                    if datetime.now() > due_dt:
                        overdue_count += 1

        # Calculate metrics
        total_tasks = len(tasks)
        completed_count = len(completed_tasks)
        completion_rate = completed_count / total_tasks if total_tasks > 0 else 0
        avg_age = np.mean(task_ages) if task_ages else 0
        overdue_ratio = overdue_count / total_tasks if total_tasks > 0 else 0

        # Estimate weeks
        weeks = 2  # Default to 2 weeks if we can't calculate
        if task_ages:
            # Estimate from task creation times
            weeks = max(max(task_ages) / 7, 1)

        # Sentiment (default neutral for now, would need NLP)
        sentiment_mean = 0.0

        return {
            "avg_tasks_assigned_per_week": int(total_tasks / weeks),
            "avg_tasks_completed_per_week": int(completed_count / weeks),
            "task_completion_rate": round(completion_rate, 2),
            "avg_task_age_days": round(avg_age, 1),
            "overdue_task_ratio": round(overdue_ratio, 2),
            "task_comment_sentiment_mean": round(sentiment_mean, 2)
        }

    @staticmethod
    def extract_work_hours_features(
        worklogs: List[Dict],
        calendar_events: List[Dict],
        source: str = "jira"  # "jira" or "calendar"
    ) -> Dict:
        """
        Extract work hours and attendance features

        Returns:
            - logged_hours_per_week
            - variance_in_work_hours
            - late_start_count_per_week
            - early_exit_count_per_week
            - early_start_count_per_week
            - late_exit_count_per_week
            - absenteeism_rate
            - avg_break_length_minutes_per_week
        """
        if source == "jira" and worklogs:
            # Extract from Jira worklogs
            hours_by_day = {}

            for log in worklogs:
                time_spent = log.get("time_spent_seconds", 0)
                started = log.get("started")

                if started:
                    dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                    day_key = dt.date()

                    if day_key not in hours_by_day:
                        hours_by_day[day_key] = 0

                    hours_by_day[day_key] += time_spent / 3600

            # Calculate statistics
            daily_hours = list(hours_by_day.values())

            if daily_hours:
                avg_hours = np.mean(daily_hours)
                variance_hours = np.var(daily_hours)
                weeks = len(daily_hours) / 5  # Assume 5 work days per week
            else:
                avg_hours = 40.0
                variance_hours = 1.0
                weeks = 1

        elif calendar_events:
            # Estimate from calendar
            hours_by_day = {}

            for event in calendar_events:
                if event.get("isAllDay"):
                    continue

                start = event.get("start", {})
                end = event.get("end", {})

                if start.get("dateTime") and end.get("dateTime"):
                    start_dt = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
                    end_dt = datetime.fromisoformat(end["dateTime"].replace("Z", "+00:00"))

                    day_key = start_dt.date()
                    duration = (end_dt - start_dt).total_seconds() / 3600

                    if day_key not in hours_by_day:
                        hours_by_day[day_key] = 0

                    hours_by_day[day_key] += duration

            daily_hours = list(hours_by_day.values())

            if daily_hours:
                # Add baseline work hours
                avg_hours = max(np.mean(daily_hours), 8.0)
                variance_hours = np.var(daily_hours)
                weeks = len(daily_hours) / 5
            else:
                avg_hours = 40.0
                variance_hours = 1.0
                weeks = 1
        else:
            # Default values
            avg_hours = 40.0
            variance_hours = 1.0
            weeks = 1

        # Simplified attendance metrics (would need more detailed data)
        late_starts = 3  # Default estimate
        early_exits = 1
        early_starts = 2
        late_exits = 1
        absenteeism = 0.03  # 3% default
        avg_break = 45.0  # 45 minutes default

        return {
            "logged_hours_per_week": round(avg_hours, 1),
            "variance_in_work_hours": round(variance_hours, 2),
            "late_start_count_per_week": late_starts,
            "early_exit_count_per_week": early_exits,
            "early_start_count_per_week": early_starts,
            "late_exit_count_per_week": late_exits,
            "absenteeism_rate": round(absenteeism, 3),
            "avg_break_length_minutes_per_week": round(avg_break, 1)
        }

    @staticmethod
    def extract_all_features(
        calendar_events: Optional[List[Dict]] = None,
        messages: Optional[List[Dict]] = None,
        tasks: Optional[List[Dict]] = None,
        worklogs: Optional[List[Dict]] = None,
        message_source: str = "teams",
        task_source: str = "jira"
    ) -> Dict:
        """
        Extract all features required by the ML model

        Returns a dictionary with all 23 features needed for prediction
        """
        features = {}

        # Meeting features
        if calendar_events:
            features.update(FeatureExtractor.extract_meeting_features(calendar_events))
        else:
            features.update({
                "meeting_hours_per_week": 8.0,
                "meeting_counts_per_week": 10
            })

        # Communication features
        if messages:
            features.update(FeatureExtractor.extract_communication_features(messages, message_source))
        else:
            features.update({
                "messages_sent_per_week": 70,
                "messages_received_per_week": 100,
                "avg_response_latency_min": 10.0,
                "communication_burstiness": 0.3,
                "after_hours_message_ratio": 0.1,
                "communication_balance": 0.7,
                "conversation_length_avg": 12.0
            })

        # Task features
        if tasks:
            features.update(FeatureExtractor.extract_task_features(tasks, task_source))
        else:
            features.update({
                "avg_tasks_assigned_per_week": 20,
                "avg_tasks_completed_per_week": 16,
                "task_completion_rate": 0.8,
                "avg_task_age_days": 7.0,
                "overdue_task_ratio": 0.2,
                "task_comment_sentiment_mean": 0.0
            })

        # Work hours features
        features.update(FeatureExtractor.extract_work_hours_features(
            worklogs or [],
            calendar_events or [],
            "jira" if worklogs else "calendar"
        ))

        logger.info(f"Extracted {len(features)} features for ML model")

        return features
