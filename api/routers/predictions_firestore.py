"""
Prediction Router - ML Model Inference Endpoints
Connects the trained ML models with employee data from Firebase
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional
import sys
from pathlib import Path
import logging

# Add model directory to path
model_path = Path(__file__).parent.parent.parent / "model" / "models" / "inference"
sys.path.insert(0, str(model_path))

from predict import WorkforceAnalyticsPredictor

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize predictor (global instance)
try:
    predictor = WorkforceAnalyticsPredictor()
    logger.info("✅ ML Predictor initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize predictor: {e}")
    predictor = None


class EmployeeFeatures(BaseModel):
    """Employee features for prediction"""
    # Basic Info
    age: Optional[int] = None
    experience_years: Optional[float] = None
    
    # Work Hours
    work_hours_per_day: Optional[float] = None
    days_worked_per_week: Optional[int] = None
    overtime_hours: Optional[float] = None
    weekend_work_hours: Optional[float] = None
    
    # Attendance
    punctuality_score: Optional[float] = None
    attendance_rate: Optional[float] = None
    late_arrivals: Optional[int] = None
    days_off_taken: Optional[int] = None
    sick_days: Optional[int] = None
    
    # Communication
    emails_sent: Optional[int] = None
    emails_received: Optional[int] = None
    email_response_time: Optional[float] = None
    after_hours_emails: Optional[int] = None
    messages_sent: Optional[int] = None
    messages_received: Optional[int] = None
    after_hours_messages: Optional[int] = None
    response_time_minutes: Optional[float] = None
    
    # Meetings
    meetings_per_week: Optional[int] = None
    meeting_hours: Optional[float] = None
    meeting_acceptance_rate: Optional[float] = None
    declined_meetings: Optional[int] = None
    
    # Tasks
    tasks_assigned: Optional[int] = None
    tasks_completed_per_week: Optional[int] = None
    task_completion_rate: Optional[float] = None
    overdue_tasks: Optional[int] = None
    avg_task_completion_time: Optional[float] = None
    
    # GitHub/Code
    commits_per_week: Optional[int] = None
    prs_created: Optional[int] = None
    prs_reviewed: Optional[int] = None
    code_review_time_hours: Optional[float] = None
    pr_merge_rate: Optional[float] = None
    
    # Role (one-hot encoded)
    role_Developer: Optional[int] = 0
    role_Designer: Optional[int] = 0
    role_Manager: Optional[int] = 0
    role_QA_Engineer: Optional[int] = 0
    role_Senior_Developer: Optional[int] = 0
    role_Tech_Lead: Optional[int] = 0
    
    # Additional fields can be added as needed
    focus_time_hours: Optional[float] = None
    hours_logged: Optional[float] = None
    projects_active: Optional[int] = None
    bugs_reported: Optional[int] = None
    bugs_fixed: Optional[int] = None
    
    class Config:
        schema_extra = {
            "example": {
                "age": 32,
                "experience_years": 5,
                "work_hours_per_day": 9.5,
                "overtime_hours": 15,
                "emails_sent": 45,
                "meetings_per_week": 12,
                "task_completion_rate": 0.75,
                "role_Developer": 1
            }
        }


class PredictionRequest(BaseModel):
    """Request for employee predictions"""
    employee_id: str
    features: Optional[EmployeeFeatures] = None
    fetch_from_integrations: bool = False


class PredictionResponse(BaseModel):
    """Response with predictions"""
    employee_id: str
    burnout_risk: float
    burnout_percentage: float  # burnout_risk * 100 for display
    wellbeing_score: float
    efficiency_score: float
    risk_category: str
    risk_description: str
    wellbeing_category: str
    efficiency_category: str
    data_completeness: str
    provided_features: int
    imputed_features: int
    recommendations: List[str]


@router.post("/predict", response_model=PredictionResponse)
async def predict_employee_metrics(request: PredictionRequest):
    """
    Predict burnout risk, wellbeing, and efficiency for an employee
    
    - **employee_id**: Employee identifier
    - **features**: Employee features (if not provided, will fetch from integrations)
    - **fetch_from_integrations**: Whether to fetch data from connected integrations
    """
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="ML Predictor not initialized. Please ensure models are trained."
        )
    
    try:
        # Convert Pydantic model to dict, filtering out None values
        if request.features:
            features_dict = {
                k: v for k, v in request.features.dict().items() 
                if v is not None
            }
        else:
            # TODO: Fetch from integrations if fetch_from_integrations=True
            raise HTTPException(
                status_code=400,
                detail="Features must be provided. Integration fetching not yet implemented."
            )
        
        # Get predictions
        predictions = predictor.predict_all(features_dict)
        
        # Get categories
        risk_cat, risk_desc = predictor.get_risk_category(predictions['burnout_risk'])
        wellbeing_cat, wellbeing_desc = predictor.get_wellbeing_category(predictions['wellbeing'])
        efficiency_cat, efficiency_desc = predictor.get_efficiency_category(predictions['efficiency'])
        
        # Get imputation info
        imputation_info = predictor.get_imputed_summary(features_dict)
        
        # Generate recommendations
        recommendations = _generate_recommendations(
            predictions['burnout_risk'],
            predictions['wellbeing'],
            predictions['efficiency']
        )
        
        return PredictionResponse(
            employee_id=request.employee_id,
            burnout_risk=float(predictions['burnout_risk']),
            burnout_percentage=float(predictions['burnout_risk'] * 100),
            wellbeing_score=float(predictions['wellbeing']),
            efficiency_score=float(predictions['efficiency']),
            risk_category=risk_cat,
            risk_description=risk_desc,
            wellbeing_category=wellbeing_cat,
            efficiency_category=efficiency_cat,
            data_completeness=imputation_info['data_completeness'],
            provided_features=imputation_info['provided_features'],
            imputed_features=imputation_info['imputed_features'],
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/batch")
async def predict_batch(employees: List[PredictionRequest]):
    """
    Batch prediction for multiple employees
    """
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="ML Predictor not initialized."
        )
    
    results = []
    for employee in employees:
        try:
            result = await predict_employee_metrics(employee)
            results.append(result)
        except Exception as e:
            logger.error(f"Error predicting for {employee.employee_id}: {e}")
            results.append({
                "employee_id": employee.employee_id,
                "error": str(e)
            })
    
    return results


@router.get("/feature-importance/{model_type}")
async def get_feature_importance(model_type: str, top_n: int = 10):
    """
    Get top N important features for a specific model
    
    - **model_type**: One of 'burnout_risk', 'wellbeing', 'efficiency'
    - **top_n**: Number of top features to return (default: 10)
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="ML Predictor not initialized.")
    
    valid_types = ['burnout_risk', 'wellbeing', 'efficiency']
    if model_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model_type. Must be one of: {valid_types}"
        )
    
    try:
        importance_df = predictor.get_feature_importance(model_type, top_n=top_n)
        return {
            "model_type": model_type,
            "top_features": importance_df.to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-info")
async def get_model_info():
    """
    Get information about the loaded models
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="ML Predictor not initialized.")
    
    return {
        "status": "loaded",
        "models": {
            "burnout_risk": {
                "r2_score": predictor.metrics['burnout_risk']['test_r2'],
                "mae": predictor.metrics['burnout_risk']['test_mae'],
                "rmse": predictor.metrics['burnout_risk']['test_rmse']
            },
            "wellbeing": {
                "r2_score": predictor.metrics['wellbeing']['test_r2'],
                "mae": predictor.metrics['wellbeing']['test_mae'],
                "rmse": predictor.metrics['wellbeing']['test_rmse']
            },
            "efficiency": {
                "r2_score": predictor.metrics['efficiency']['test_r2'],
                "mae": predictor.metrics['efficiency']['test_mae'],
                "rmse": predictor.metrics['efficiency']['test_rmse']
            }
        },
        "total_features": len(predictor.feature_columns),
        "feature_columns": predictor.feature_columns[:10] + ["... and more"]
    }


def _generate_recommendations(burnout_risk: float, wellbeing: float, efficiency: float) -> List[str]:
    """Generate actionable recommendations based on predictions"""
    recommendations = []
    
    if burnout_risk > 0.7:
        recommendations.append("🚨 URGENT: Schedule immediate one-on-one meeting")
        recommendations.append("Consider immediate workload reduction")
        recommendations.append("Provide access to mental health resources")
    elif burnout_risk > 0.5:
        recommendations.append("⚠️ Monitor closely - signs of stress detected")
        recommendations.append("Review meeting schedule and task distribution")
        recommendations.append("Encourage regular breaks and time off")
    
    if wellbeing < 50:
        recommendations.append("🏥 Wellbeing support needed")
        recommendations.append("Evaluate work-life balance concerns")
        recommendations.append("Consider wellness program enrollment")
    elif wellbeing < 70:
        recommendations.append("📊 Monitor wellbeing trends")
        recommendations.append("Promote healthy work practices")
    
    if efficiency < 50:
        recommendations.append("📉 Performance concerns detected")
        recommendations.append("Identify blockers and skill gaps")
        recommendations.append("Provide additional training or mentorship")
    elif efficiency < 70:
        recommendations.append("💡 Opportunities for productivity improvement")
        recommendations.append("Review task priorities and deadlines")
    
    if not recommendations:
        recommendations.append("✅ Employee metrics are healthy")
        recommendations.append("Continue current engagement practices")
        recommendations.append("Recognize and reward good performance")
    
    return recommendations
