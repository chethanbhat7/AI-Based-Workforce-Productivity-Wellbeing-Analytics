from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import logging

from database import get_db, Feature, WellbeingScore, User
from routers.features import extract_features_for_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/member/{user_id}/overview")
async def get_member_dashboard_overview(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get complete dashboard data for a team member
    
    Returns all metrics matching the ProductivityMetrics.tsx component
    """
    try:
        # Get latest features
        cutoff = datetime.utcnow() - timedelta(days=7)
        features = db.query(Feature).filter(
            Feature.user_id == user_id,
            Feature.date >= cutoff
        ).order_by(Feature.date.desc()).all()
        
        if not features:
            # No features yet - trigger extraction
            raise HTTPException(
                status_code=404,
                detail="No data available. Please connect your workplace tools first."
            )
        
        # Group features by name and get latest value
        feature_dict = {}
        for f in features:
            if f.feature_name not in feature_dict:
                feature_dict[f.feature_name] = f.feature_value
        
        # Map to frontend structure
        dashboard_data = {
            "user_id": user_id,
            "last_updated": max(f.created_at for f in features).isoformat(),
            
            # Communication metrics
            "communication": {
                "meeting_hours_per_week": feature_dict.get("meeting_hours_per_week", 0),
                "meeting_counts_per_week": feature_dict.get("meeting_counts_per_week", 0),
                "messages_sent_per_day": feature_dict.get("messages_sent_per_day", 0),
                "messages_received_per_day": feature_dict.get("messages_received_per_day", 0),
                "avg_response_latency_min": feature_dict.get("avg_response_latency_min", 0),
                "communication_balance": feature_dict.get("communication_balance", 1.0),
                "after_hours_message_ratio": feature_dict.get("after_hours_message_ratio", 0)
            },
            
            # Task metrics
            "tasks": {
                "avg_tasks_assigned_per_week": feature_dict.get("avg_tasks_assigned_per_week", 0),
                "avg_tasks_completed_per_week": feature_dict.get("avg_tasks_completed_per_week", 0),
                "task_completion_rate": feature_dict.get("task_completion_rate", 0),
                "avg_task_age_days": feature_dict.get("avg_task_age_days", 0),
                "overdue_task_ratio": feature_dict.get("overdue_task_ratio", 0)
            },
            
            # Work hours
            "work_hours": {
                "logged_hours_per_week": feature_dict.get("logged_hours_per_week", 40),
                "variance_in_work_hours": feature_dict.get("variance_in_work_hours", 1.0),
                "late_start_count_per_month": feature_dict.get("late_start_count_per_month", 0),
                "early_exit_count_per_month": feature_dict.get("early_exit_count_per_month", 0),
                "avg_break_length_minutes": feature_dict.get("avg_break_length_minutes", 45)
            },
            
            # Performance
            "performance": {
                "performance_score": feature_dict.get("performance_score", 0.7),
                "burnout_risk_score": feature_dict.get("burnout_risk_score", 0.3)
            }
        }
        
        return dashboard_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/member/{user_id}/wellbeing")
async def get_member_wellbeing_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get wellbeing profile data for WellbeingProfile.tsx component
    """
    try:
        # Get latest wellbeing score
        wellbeing = db.query(WellbeingScore).filter(
            WellbeingScore.user_id == user_id
        ).order_by(WellbeingScore.created_at.desc()).first()
        
        if not wellbeing:
            # Calculate from features
            features = db.query(Feature).filter(
                Feature.user_id == user_id
            ).order_by(Feature.created_at.desc()).limit(30).all()
            
            if not features:
                raise HTTPException(
                    status_code=404,
                    detail="No wellbeing data available yet"
                )
            
            # Create synthetic wellbeing scores
            feature_dict = {}
            for f in features:
                feature_dict[f.feature_name] = f.feature_value
            
            # Calculate wellbeing categories
            task_completion = feature_dict.get("task_completion_rate", 0.7)
            burnout_risk = feature_dict.get("burnout_risk_score", 0.3)
            comm_balance = feature_dict.get("communication_balance", 1.0)
            work_hours = feature_dict.get("logged_hours_per_week", 40)
            
            # Mental health score (inverse of burnout)
            mental_health_score = int((1 - burnout_risk) * 100)
            
            # Physical health score (based on work hours balance)
            hours_deviation = abs(work_hours - 40) / 40
            physical_health_score = int((1 - hours_deviation) * 100)
            
            # Work-life balance (based on after-hours work)
            after_hours_ratio = feature_dict.get("after_hours_message_ratio", 0.1)
            work_life_balance_score = int((1 - after_hours_ratio) * 100)
            
            # Stress management (based on task completion and burnout)
            stress_score = int((task_completion * (1 - burnout_risk)) * 100)
            
            return {
                "user_id": user_id,
                "overall_score": int((mental_health_score + physical_health_score + 
                                     work_life_balance_score + stress_score) / 4),
                "categories": {
                    "mental_health": mental_health_score,
                    "physical_health": physical_health_score,
                    "work_life_balance": work_life_balance_score,
                    "stress_management": stress_score
                },
                "check_ins": 0,  # Would track actual check-ins
                "streak_days": 0,
                "status": "Good" if mental_health_score > 70 else "Fair"
            }
        
        return {
            "user_id": user_id,
            "overall_score": wellbeing.focus_time_score or 70,
            "categories": {
                "mental_health": wellbeing.stress_score or 75,
                "physical_health": 80,
                "work_life_balance": wellbeing.collaboration_balance or 72,
                "stress_management": wellbeing.workload_balance or 68
            },
            "burnout_risk": wellbeing.burnout_risk or "low",
            "recommendations": wellbeing.recommendations or []
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting wellbeing profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/member/{user_id}/metrics")
async def get_productivity_metrics(
    user_id: str,
    period: str = "week",  # week, month
    db: Session = Depends(get_db)
):
    """
    Get detailed productivity metrics for ProductivityMetrics.tsx
    
    Returns data formatted for the frontend component
    """
    try:
        # Get features
        if period == "week":
            days_back = 7
        elif period == "month":
            days_back = 30
        else:
            days_back = 7
        
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        features = db.query(Feature).filter(
            Feature.user_id == user_id,
            Feature.date >= cutoff
        ).order_by(Feature.date.desc()).all()
        
        if not features:
            raise HTTPException(
                status_code=404,
                detail="No productivity data available"
            )
        
        # Get latest values
        feature_dict = {}
        for f in features:
            if f.feature_name not in feature_dict:
                feature_dict[f.feature_name] = f.feature_value
        
        # Calculate weekly metrics (for display)
        metrics = {
            "meeting_hours": feature_dict.get("meeting_hours_per_week", 0),
            "meeting_counts": int(feature_dict.get("meeting_counts_per_week", 0)),
            "messages_sent": int(feature_dict.get("messages_sent_per_day", 0) * 7),
            "messages_received": int(feature_dict.get("messages_received_per_day", 0) * 7),
            "task_completion_rate": int(feature_dict.get("task_completion_rate", 0) * 100),
            "logged_hours": feature_dict.get("logged_hours_per_week", 40),
            "early_starts": int(feature_dict.get("late_start_count_per_month", 0) / 4),
            "late_exits": 2,  # Placeholder
            "late_starts": int(feature_dict.get("late_start_count_per_month", 0) / 4),
            "early_exits": int(feature_dict.get("early_exit_count_per_month", 0) / 4)
        }
        
        # Calculate efficiency score
        task_score = metrics["task_completion_rate"]
        meeting_score = max(0, 100 - (metrics["meeting_counts"] * 3))
        hours_score = min(100, (metrics["logged_hours"] / 40) * 100)
        efficiency_score = int((task_score + meeting_score + hours_score) / 3)
        
        return {
            "user_id": user_id,
            "period": period,
            "efficiency_score": efficiency_score,
            "metrics": metrics,
            "insights": [
                {
                    "type": "positive" if task_score > 80 else "warning",
                    "title": "Strong Performance" if task_score > 80 else "Room for Improvement",
                    "description": f"{task_score}% task completion rate"
                },
                {
                    "type": "info",
                    "title": "Meeting Load",
                    "description": f"{metrics['meeting_hours']:.1f} hours per week in meetings"
                },
                {
                    "type": "positive" if metrics["messages_sent"] > 100 else "info",
                    "title": "Communication",
                    "description": f"{metrics['messages_sent']} messages sent this week"
                }
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting productivity metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/member/{user_id}/refresh")
async def refresh_dashboard_data(
    user_id: str,
    days_back: int = 14,
    db: Session = Depends(get_db)
):
    """
    Trigger data refresh for a user
    
    This will:
    1. Fetch fresh data from all connected providers
    2. Preprocess and anonymize
    3. Extract features
    4. Update dashboard
    """
    try:
        # Trigger feature extraction
        result = await extract_features_for_user(
            user_id=user_id,
            days_back=days_back,
            providers=None,  # All providers
            db=db
        )
        
        return {
            "status": "success",
            "message": "Dashboard data refreshed successfully",
            "user_id": user_id,
            "features_extracted": len(result.get("features", {})),
            "data_counts": result.get("data_counts", {}),
            "privacy_notice": "Teams messages have been fully anonymized"
        }
    
    except Exception as e:
        logger.error(f"Error refreshing dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supervisor/team-overview")
async def get_team_overview(
    supervisor_id: str,
    team_ids: Optional[str] = None,  # Comma-separated user IDs
    db: Session = Depends(get_db)
):
    """
    Get team overview for supervisor dashboard
    
    Returns aggregated metrics for the team
    """
    try:
        # Parse team member IDs
        if team_ids:
            member_ids = [uid.strip() for uid in team_ids.split(",")]
        else:
            # Get all team members (would need team structure in DB)
            # For now, return empty
            member_ids = []
        
        if not member_ids:
            return {
                "supervisor_id": supervisor_id,
                "team_size": 0,
                "team_metrics": {},
                "message": "No team members configured"
            }
        
        # Aggregate metrics for team
        team_metrics = []
        
        for member_id in member_ids:
            # Get latest features for member
            features = db.query(Feature).filter(
                Feature.user_id == member_id
            ).order_by(Feature.created_at.desc()).limit(30).all()
            
            if features:
                feature_dict = {}
                for f in features:
                    feature_dict[f.feature_name] = f.feature_value
                
                team_metrics.append({
                    "user_id": member_id,
                    "burnout_risk": feature_dict.get("burnout_risk_score", 0),
                    "performance_score": feature_dict.get("performance_score", 0),
                    "task_completion_rate": feature_dict.get("task_completion_rate", 0),
                    "work_hours": feature_dict.get("logged_hours_per_week", 40)
                })
        
        # Calculate team averages
        if team_metrics:
            avg_burnout = sum(m["burnout_risk"] for m in team_metrics) / len(team_metrics)
            avg_performance = sum(m["performance_score"] for m in team_metrics) / len(team_metrics)
            avg_task_completion = sum(m["task_completion_rate"] for m in team_metrics) / len(team_metrics)
            
            # Identify at-risk members
            at_risk = [m for m in team_metrics if m["burnout_risk"] > 0.6]
            high_performers = [m for m in team_metrics if m["performance_score"] > 0.8]
            
            return {
                "supervisor_id": supervisor_id,
                "team_size": len(member_ids),
                "team_averages": {
                    "burnout_risk": round(avg_burnout, 2),
                    "performance_score": round(avg_performance, 2),
                    "task_completion_rate": round(avg_task_completion, 2)
                },
                "at_risk_count": len(at_risk),
                "at_risk_members": [m["user_id"] for m in at_risk],
                "high_performers_count": len(high_performers),
                "recommendations": [
                    f"{len(at_risk)} team members showing elevated burnout risk" if at_risk else "Team wellbeing is healthy",
                    f"Team average task completion: {int(avg_task_completion * 100)}%",
                    f"Consider workload redistribution" if avg_burnout > 0.5 else "Workload appears balanced"
                ]
            }
        
        return {
            "supervisor_id": supervisor_id,
            "team_size": 0,
            "message": "No data available for team members"
        }
    
    except Exception as e:
        logger.error(f"Error getting team overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))
