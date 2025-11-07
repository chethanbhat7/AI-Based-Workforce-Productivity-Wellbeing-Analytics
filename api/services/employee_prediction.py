"""
Employee Prediction Service
Fetches employee data from Firebase and runs ML predictions
"""
import sys
from pathlib import Path
from typing import Dict, Optional
import logging

# Add model directory to path
model_path = Path(__file__).parent.parent.parent / "model" / "models" / "inference"
sys.path.insert(0, str(model_path))

try:
    from predict import WorkforceAnalyticsPredictor
    predictor = WorkforceAnalyticsPredictor()
    logger = logging.getLogger(__name__)
    logger.info("✅ ML Predictor loaded successfully in service")
except Exception as e:
    logger = logging.getLogger(__name__)
    logger.error(f"❌ Failed to load predictor: {e}")
    predictor = None


class EmployeePredictionService:
    """Service to fetch employee data and generate predictions"""
    
    def __init__(self):
        self.predictor = predictor
    
    def extract_features_from_firebase(self, employee_data: Dict) -> Dict:
        """
        Extract ML features from Firebase employee data
        
        Args:
            employee_data: Raw employee data from Firebase
            
        Returns:
            Dictionary of features for ML model
        """
        features = {}
        
        # Map Firebase fields to model features
        # Basic info
        if 'age' in employee_data:
            features['age'] = employee_data['age']
        if 'experienceYears' in employee_data:
            features['experience_years'] = employee_data['experienceYears']
        
        # Work hours
        if 'workHoursPerDay' in employee_data:
            features['work_hours_per_day'] = employee_data['workHoursPerDay']
        if 'overtimeHours' in employee_data:
            features['overtime_hours'] = employee_data['overtimeHours']
        if 'loggedHours' in employee_data:
            features['hours_logged'] = employee_data['loggedHours']
        
        # Attendance
        if 'punctuality' in employee_data:
            features['punctuality_score'] = employee_data['punctuality'] / 100
        if 'attendance' in employee_data:
            features['attendance_rate'] = employee_data['attendance'] / 100
        if 'lateArrivals' in employee_data:
            features['late_arrivals'] = employee_data['lateArrivals']
        
        # Communication
        if 'emailsSent' in employee_data:
            features['emails_sent'] = employee_data['emailsSent']
        if 'emailsReceived' in employee_data:
            features['emails_received'] = employee_data['emailsReceived']
        if 'messagesSent' in employee_data:
            features['messages_sent'] = employee_data['messagesSent']
        if 'messagesReceived' in employee_data:
            features['messages_received'] = employee_data['messagesReceived']
        
        # Meetings
        if 'meetingCount' in employee_data:
            features['meetings_per_week'] = employee_data['meetingCount']
        if 'meetingHours' in employee_data:
            features['meeting_hours'] = employee_data['meetingHours']
        
        # Tasks
        if 'taskCompletion' in employee_data:
            features['task_completion_rate'] = employee_data['taskCompletion'] / 100
        if 'tasksCompleted' in employee_data:
            features['tasks_completed_per_week'] = employee_data['tasksCompleted']
        if 'tasksAssigned' in employee_data:
            features['tasks_assigned'] = employee_data['tasksAssigned']
        
        # Role mapping
        role = employee_data.get('role', 'Developer')
        features['role_Developer'] = 1 if role == 'Developer' else 0
        features['role_Designer'] = 1 if role == 'Designer' else 0
        features['role_Manager'] = 1 if role == 'Manager' else 0
        features['role_QA Engineer'] = 1 if role == 'QA Engineer' else 0
        features['role_Senior Developer'] = 1 if role == 'Senior Developer' else 0
        features['role_Tech Lead'] = 1 if role == 'Tech Lead' else 0
        
        return features
    
    def predict_for_employee(self, employee_data: Dict) -> Optional[Dict]:
        """
        Generate predictions for an employee
        
        Args:
            employee_data: Employee data from Firebase
            
        Returns:
            Predictions dict or None if predictor not available
        """
        if self.predictor is None:
            logger.error("Predictor not initialized")
            return None
        
        try:
            # Extract features
            features = self.extract_features_from_firebase(employee_data)
            
            # Get predictions
            predictions = self.predictor.predict_all(features)
            
            # Get categories
            risk_cat, risk_desc = self.predictor.get_risk_category(predictions['burnout_risk'])
            wellbeing_cat, wellbeing_desc = self.predictor.get_wellbeing_category(predictions['wellbeing'])
            efficiency_cat, efficiency_desc = self.predictor.get_efficiency_category(predictions['efficiency'])
            
            # Get imputation info
            imputation_info = self.predictor.get_imputed_summary(features)
            
            return {
                'burnout_risk': float(predictions['burnout_risk']),
                'burnout_percentage': float(predictions['burnout_risk'] * 100),
                'wellbeing_score': float(predictions['wellbeing']),
                'efficiency_score': float(predictions['efficiency']),
                'risk_category': risk_cat,
                'risk_description': risk_desc,
                'wellbeing_category': wellbeing_cat,
                'efficiency_category': efficiency_cat,
                'data_completeness': imputation_info['data_completeness'],
                'provided_features': imputation_info['provided_features'],
                'imputed_features': imputation_info['imputed_features']
            }
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return None


# Global instance
_employee_prediction_service = None


def get_employee_prediction_service() -> EmployeePredictionService:
    """Get or create global prediction service instance"""
    global _employee_prediction_service
    
    if _employee_prediction_service is None:
        _employee_prediction_service = EmployeePredictionService()
    
    return _employee_prediction_service
