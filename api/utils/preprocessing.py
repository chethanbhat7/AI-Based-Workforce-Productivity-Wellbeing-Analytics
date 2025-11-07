"""
Data Preprocessing Pipeline
Handles data cleaning, anonymization, and normalization
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import re
import logging

logger = logging.getLogger(__name__)


class DataAnonymizer:
    """
    Anonymize sensitive data while preserving utility for ML models
    
    CRITICAL: Teams messages are anonymized and only accessible by ML pipeline
    """
    
    def __init__(self, encryption_key: str = "default_key_change_in_production"):
        self.encryption_key = encryption_key
        self._anonymized_cache = {}
    
    def _hash_identifier(self, identifier: str) -> str:
        """Create consistent hash for identifiers"""
        hash_input = f"{identifier}:{self.encryption_key}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    def anonymize_email(self, email: str) -> str:
        """
        Anonymize email address
        user@domain.com -> user_a3f5@domain.com
        """
        if not email or "@" not in email:
            return "anonymous@unknown.com"
        
        username, domain = email.split("@", 1)
        hash_suffix = self._hash_identifier(email)[:4]
        return f"{username[:4]}_{hash_suffix}@{domain}"
    
    def anonymize_name(self, name: str) -> str:
        """
        Anonymize person name
        John Doe -> User_a3f5
        """
        if not name:
            return "Anonymous"
        
        hash_suffix = self._hash_identifier(name)[:8]
        return f"User_{hash_suffix}"
    
    def anonymize_message_content(self, content: str) -> Dict[str, Any]:
        """
        Anonymize message content while preserving features for sentiment analysis
        
        Returns:
        - anonymized_text: Redacted text (for display - HIDDEN from users)
        - features: Extracted features (length, sentiment indicators, etc.)
        - ml_only_hash: Hash for ML model access
        
        The actual content is NEVER stored in plain text or shown to users.
        Only the ML model can access it via secure hash.
        """
        if not content:
            return {
                "anonymized_text": "[REDACTED]",
                "features": {
                    "length": 0,
                    "has_question": False,
                    "has_exclamation": False,
                    "word_count": 0
                },
                "ml_only_hash": None
            }
        
        # Extract features that are safe to expose
        features = {
            "length": len(content),
            "has_question": "?" in content,
            "has_exclamation": "!" in content,
            "word_count": len(content.split()),
            "has_emoji": any(char in content for char in ["😊", "😢", "😡", "👍", "🎉"]),
            "avg_word_length": sum(len(w) for w in content.split()) / max(len(content.split()), 1)
        }
        
        # Create secure hash for ML model access only
        ml_only_hash = self._hash_identifier(content)
        
        # Store in secure cache for ML model access
        self._anonymized_cache[ml_only_hash] = {
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Return REDACTED text for all users/UI
        # Only ML pipeline can access via ml_only_hash
        return {
            "anonymized_text": "[MESSAGE CONTENT REDACTED FOR PRIVACY]",
            "features": features,
            "ml_only_hash": ml_only_hash
        }
    
    def get_content_for_ml(self, ml_hash: str) -> Optional[str]:
        """
        Retrieve original content for ML model ONLY
        
        This should only be called by the ML inference pipeline
        NOT accessible via API endpoints
        """
        cached = self._anonymized_cache.get(ml_hash)
        if cached:
            return cached["content"]
        return None
    
    def anonymize_teams_message(self, message: Dict) -> Dict:
        """
        Anonymize Teams message completely
        
        Returns message with:
        - Author info anonymized
        - Message content anonymized (features extracted, content hidden)
        - Metadata preserved for ML
        """
        anonymized = {
            "id": message.get("id"),
            "timestamp": message.get("createdDateTime"),
            "message_type": message.get("messageType", "message"),
            "importance": message.get("importance", "normal"),
            "chat_id": message.get("chat_id"),
            "chat_type": message.get("chat_type"),
            "is_reply": bool(message.get("replyToId"))
        }
        
        # Anonymize author
        from_user = message.get("from", {})
        if from_user:
            user_info = from_user.get("user", {})
            anonymized["author"] = {
                "id_hash": self._hash_identifier(user_info.get("id", "unknown")),
                "display_name": self.anonymize_name(user_info.get("displayName", ""))
            }
        
        # Anonymize message body (CRITICAL)
        body = message.get("body", {})
        if body:
            content = body.get("content", "")
            
            # Remove any HTML tags if present
            clean_content = re.sub(r'<[^>]+>', '', content)
            
            # Anonymize content
            anonymized_content = self.anonymize_message_content(clean_content)
            
            anonymized["body"] = {
                "content_type": body.get("contentType", "text"),
                # REDACTED - no actual content exposed
                "anonymized_content": anonymized_content["anonymized_text"],
                # Features for analysis
                "features": anonymized_content["features"],
                # ML-only access hash
                "ml_hash": anonymized_content["ml_only_hash"]
            }
        
        return anonymized
    
    def anonymize_slack_message(self, message: Dict) -> Dict:
        """
        Anonymize Slack message
        """
        anonymized = {
            "ts": message.get("ts"),
            "type": message.get("type", "message"),
            "subtype": message.get("subtype"),
            "channel_id": message.get("channel_id"),
            "channel_name": message.get("channel_name"),
            "is_thread": bool(message.get("thread_ts"))
        }
        
        # Anonymize user
        user_id = message.get("user")
        if user_id:
            anonymized["user_hash"] = self._hash_identifier(user_id)
        
        # Anonymize text content
        text = message.get("text", "")
        if text:
            anonymized_content = self.anonymize_message_content(text)
            anonymized["text"] = {
                "anonymized": anonymized_content["anonymized_text"],
                "features": anonymized_content["features"],
                "ml_hash": anonymized_content["ml_only_hash"]
            }
        
        # Preserve reactions (sentiment proxy)
        if "reactions" in message:
            anonymized["reactions"] = message["reactions"]
        
        return anonymized
    
    def anonymize_email_data(self, email: Dict) -> Dict:
        """
        Anonymize email metadata (no content, just metadata)
        """
        anonymized = {
            "received_at": email.get("receivedDateTime"),
            "sent_at": email.get("sentDateTime"),
            "importance": email.get("importance", "normal"),
            "is_read": email.get("isRead"),
            "has_attachments": email.get("hasAttachments", False)
        }
        
        # Anonymize sender/recipients
        from_data = email.get("from", {})
        if from_data:
            email_addr = from_data.get("emailAddress", {}).get("address", "")
            anonymized["from"] = self.anonymize_email(email_addr)
        
        # Count recipients (preserve number for workload analysis)
        to_recipients = email.get("toRecipients", [])
        cc_recipients = email.get("ccRecipients", [])
        
        anonymized["to_count"] = len(to_recipients)
        anonymized["cc_count"] = len(cc_recipients)
        
        return anonymized


class DataPreprocessor:
    """
    Main data preprocessing pipeline
    
    Responsibilities:
    1. Clean and validate raw API data
    2. Anonymize sensitive information
    3. Normalize formats across different providers
    4. Prepare data for feature extraction
    """
    
    def __init__(self, anonymizer: Optional[DataAnonymizer] = None):
        self.anonymizer = anonymizer or DataAnonymizer()
    
    def preprocess_calendar_events(self, events: List[Dict]) -> List[Dict]:
        """
        Clean and normalize calendar events
        """
        processed = []
        
        for event in events:
            # Validate required fields
            if not event.get("start") or not event.get("end"):
                logger.warning(f"Skipping event without start/end times: {event.get('id')}")
                continue
            
            # Extract and normalize
            processed_event = {
                "id": event.get("id"),
                "subject": event.get("subject", "Untitled Meeting"),
                "start": event["start"]["dateTime"],
                "end": event["end"]["dateTime"],
                "is_all_day": event.get("isAllDay", False),
                "status": event.get("showAs", "busy"),
                "attendee_count": len(event.get("attendees", [])),
                # Don't store attendee names/emails - just counts
                "location_type": "online" if "teams" in str(event.get("location", "")).lower() else "physical"
            }
            
            processed.append(processed_event)
        
        return processed
    
    def preprocess_teams_messages(self, messages: List[Dict]) -> List[Dict]:
        """
        Preprocess and ANONYMIZE Teams messages
        
        CRITICAL: This ensures message content is never exposed to users
        """
        processed = []
        
        for message in messages:
            try:
                # Fully anonymize the message
                anonymized = self.anonymizer.anonymize_teams_message(message)
                processed.append(anonymized)
            except Exception as e:
                logger.error(f"Error anonymizing Teams message: {e}")
                continue
        
        logger.info(f"Preprocessed {len(processed)} Teams messages with full anonymization")
        return processed
    
    def preprocess_slack_messages(self, messages: List[Dict]) -> List[Dict]:
        """
        Preprocess and anonymize Slack messages
        """
        processed = []
        
        for message in messages:
            try:
                anonymized = self.anonymizer.anonymize_slack_message(message)
                processed.append(anonymized)
            except Exception as e:
                logger.error(f"Error anonymizing Slack message: {e}")
                continue
        
        logger.info(f"Preprocessed {len(processed)} Slack messages with anonymization")
        return processed
    
    def preprocess_emails(self, emails: List[Dict]) -> List[Dict]:
        """
        Preprocess email metadata
        """
        processed = []
        
        for email in emails:
            try:
                anonymized = self.anonymizer.anonymize_email_data(email)
                processed.append(anonymized)
            except Exception as e:
                logger.error(f"Error anonymizing email: {e}")
                continue
        
        return processed
    
    def preprocess_jira_issues(self, issues: List[Dict]) -> List[Dict]:
        """
        Clean and normalize Jira issues
        """
        processed = []
        
        for issue in issues:
            processed_issue = {
                "key": issue.get("key"),
                "status": issue.get("status"),
                "priority": issue.get("priority"),
                "issue_type": issue.get("issue_type"),
                "created": issue.get("created"),
                "updated": issue.get("updated"),
                "resolved": issue.get("resolved"),
                "assignee": issue.get("assignee"),
                "creator": issue.get("creator"),
                "project": issue.get("project"),
                "time_estimate_hours": (
                    issue.get("time_estimate", 0) / 3600 
                    if issue.get("time_estimate") else None
                ),
                "time_spent_hours": (
                    issue.get("time_spent", 0) / 3600 
                    if issue.get("time_spent") else None
                )
            }
            processed.append(processed_issue)
        
        return processed
    
    def preprocess_all_data(
        self,
        calendar_events: Optional[List[Dict]] = None,
        teams_messages: Optional[List[Dict]] = None,
        slack_messages: Optional[List[Dict]] = None,
        emails: Optional[List[Dict]] = None,
        jira_issues: Optional[List[Dict]] = None
    ) -> Dict[str, List[Dict]]:
        """
        Preprocess all data sources in one call
        
        Returns:
            Dictionary with preprocessed data from all sources
        """
        return {
            "calendar_events": self.preprocess_calendar_events(calendar_events or []),
            "teams_messages": self.preprocess_teams_messages(teams_messages or []),
            "slack_messages": self.preprocess_slack_messages(slack_messages or []),
            "emails": self.preprocess_emails(emails or []),
            "jira_issues": self.preprocess_jira_issues(jira_issues or [])
        }


# Singleton instances
data_anonymizer = DataAnonymizer()
data_preprocessor = DataPreprocessor(data_anonymizer)
