"""
Inference Script for Workforce Analytics Models

This script loads the trained models and performs predictions on new employee data.
It supports three prediction types:
1. Burnout Risk (0-1 scale)
2. Wellbeing Score (0-100 scale)
3. Efficiency Score (0-100 scale)
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Union, Tuple
from pathlib import Path
from sklearn.impute import SimpleImputer


class WorkforceAnalyticsPredictor:
    """
    A predictor class for workforce analytics that loads trained models
    and performs inference on employee data.
    """
    
    def __init__(self, models_dir: str = None):
        """
        Initialize the predictor by loading models and metadata.
        
        Args:
            models_dir: Path to the directory containing model files.
                       If None, uses the parent directory of this script.
        """
        if models_dir is None:
            # Get parent directory (model/models/)
            models_dir = Path(__file__).parent.parent
        
        self.models_dir = Path(models_dir)
        
        # Load models and scalers
        self.models = {}
        self.scalers = {}
        
        # Load burnout risk model
        self.models['burnout_risk'] = self._load_pickle('burnout_risk_model.pkl')
        self.scalers['burnout_risk'] = self._load_pickle('burnout_risk_scaler.pkl')
        
        # Load wellbeing model
        self.models['wellbeing'] = self._load_pickle('wellbeing_model.pkl')
        self.scalers['wellbeing'] = self._load_pickle('wellbeing_scaler.pkl')
        
        # Load efficiency model
        self.models['efficiency'] = self._load_pickle('efficiency_model.pkl')
        self.scalers['efficiency'] = self._load_pickle('efficiency_scaler.pkl')
        
        # Load feature columns
        with open(self.models_dir / 'feature_columns.json', 'r') as f:
            self.feature_columns = json.load(f)
        
        # Load model metrics for reference
        with open(self.models_dir / 'model_metrics.json', 'r') as f:
            self.metrics = json.load(f)
        
        # Initialize imputers for handling missing values
        # Use median strategy for numeric features (more robust to outliers)
        self.imputer = SimpleImputer(strategy='median', missing_values=np.nan)
        
        # Fit imputer on reasonable default values for each feature type
        self._initialize_imputer()
        
        print(f"✓ Loaded all models successfully")
        print(f"✓ Feature columns: {len(self.feature_columns)}")
        print(f"✓ Imputer initialized for handling missing values")
        print(f"✓ Model performance:")
        print(f"  - Burnout Risk: R² = {self.metrics['burnout_risk']['test_r2']:.3f}")
        print(f"  - Wellbeing: R² = {self.metrics['wellbeing']['test_r2']:.3f}")
        print(f"  - Efficiency: R² = {self.metrics['efficiency']['test_r2']:.3f}")
    
    def _initialize_imputer(self):
        """
        Initialize the imputer with sensible default values for different feature types.
        This creates a reference DataFrame to fit the imputer on.
        """
        # Create default values based on feature categories
        defaults = {}
        
        for feature in self.feature_columns:
            # Role features (one-hot encoded) - default to 0
            if feature.startswith('role_'):
                defaults[feature] = 0
            
            # Percentage/ratio features - default to 0.5 (middle value)
            elif any(x in feature for x in ['_rate', '_percentage', '_ratio', '_score']):
                defaults[feature] = 0.5
            
            # Count/frequency features - default to median-ish values
            elif any(x in feature for x in ['_per_', 'count', 'frequency']):
                defaults[feature] = 5
            
            # Hour-based features
            elif 'hours' in feature or 'time' in feature:
                if 'work_hours' in feature:
                    defaults[feature] = 8  # Standard work day
                elif 'overtime' in feature or 'after_hours' in feature:
                    defaults[feature] = 2  # Some overtime
                else:
                    defaults[feature] = 4  # Generic hours
            
            # Day-based features
            elif 'days' in feature:
                if 'days_worked' in feature:
                    defaults[feature] = 5
                else:
                    defaults[feature] = 2
            
            # Age and experience
            elif feature == 'age':
                defaults[feature] = 32  # Average age
            elif feature == 'experience_years':
                defaults[feature] = 5  # Average experience
            
            # Minutes
            elif 'minutes' in feature:
                defaults[feature] = 30
            
            # General numeric features - default to median-ish value
            else:
                defaults[feature] = 5
        
        # Create a small reference DataFrame and fit imputer
        reference_df = pd.DataFrame([defaults] * 10)  # Create 10 rows of defaults
        self.imputer.fit(reference_df)
        
        # Store defaults for later use
        self.feature_defaults = defaults
    
    def _load_pickle(self, filename: str):
        """Load a pickle file from the models directory."""
        filepath = self.models_dir / filename
        try:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            print(f"File path: {filepath}")
            print(f"File exists: {filepath.exists()}")
            raise
    
    def prepare_features(self, employee_data: Union[Dict, pd.DataFrame]) -> pd.DataFrame:
        """
        Prepare employee data for prediction by ensuring all required features are present.
        Handles missing values using intelligent imputation.
        
        Args:
            employee_data: Dictionary or DataFrame with employee features
        
        Returns:
            DataFrame with all required features in the correct order, missing values imputed
        """
        # Convert to DataFrame if dict
        if isinstance(employee_data, dict):
            df = pd.DataFrame([employee_data])
        else:
            df = employee_data.copy()
        
        # Create a DataFrame with all required columns
        complete_df = pd.DataFrame(columns=self.feature_columns)
        
        # Fill in provided values
        for col in df.columns:
            if col in complete_df.columns:
                complete_df[col] = df[col].values
        
        # Convert to numeric, replacing any non-numeric values with NaN
        for col in complete_df.columns:
            complete_df[col] = pd.to_numeric(complete_df[col], errors='coerce')
        
        # Handle role columns specially - ensure only one is 1, rest are 0
        role_columns = [col for col in self.feature_columns if col.startswith('role_')]
        
        # Check if any role was provided
        role_provided = False
        for role_col in role_columns:
            if role_col in df.columns and pd.notna(df[role_col].iloc[0]) and df[role_col].iloc[0] == 1:
                role_provided = True
                break
        
        # If no role provided, default to Developer
        if not role_provided:
            for role_col in role_columns:
                if role_col == 'role_Developer':
                    complete_df[role_col] = 1
                else:
                    complete_df[role_col] = 0
        else:
            # Fill missing role columns with 0
            for role_col in role_columns:
                if pd.isna(complete_df[role_col].iloc[0]):
                    complete_df[role_col] = 0
        
        # Use imputer to fill remaining missing values
        # First, get columns that are not roles (already handled)
        non_role_columns = [col for col in self.feature_columns if not col.startswith('role_')]
        
        # Apply imputation to non-role columns
        if complete_df[non_role_columns].isna().any().any():
            # Replace NaN with median values from imputer
            imputed_values = self.imputer.transform(complete_df[self.feature_columns])
            complete_df = pd.DataFrame(imputed_values, columns=self.feature_columns)
        
        # Ensure correct order
        complete_df = complete_df[self.feature_columns]
        
        return complete_df
    
    def get_missing_features(self, employee_data: Union[Dict, pd.DataFrame]) -> List[str]:
        """
        Get list of features that were missing from the input data.
        
        Args:
            employee_data: Dictionary or DataFrame with employee features
        
        Returns:
            List of feature names that were missing (and will be imputed)
        """
        # Convert to DataFrame if dict
        if isinstance(employee_data, dict):
            df = pd.DataFrame([employee_data])
        else:
            df = employee_data.copy()
        
        missing_features = []
        for col in self.feature_columns:
            if col not in df.columns or (col in df.columns and pd.isna(df[col].iloc[0])):
                missing_features.append(col)
        
        return missing_features
    
    def get_imputed_summary(self, employee_data: Union[Dict, pd.DataFrame]) -> Dict[str, any]:
        """
        Get summary of how many features were provided vs imputed.
        
        Args:
            employee_data: Dictionary or DataFrame with employee features
        
        Returns:
            Dictionary with statistics about provided and imputed features
        """
        missing = self.get_missing_features(employee_data)
        
        return {
            'total_features': len(self.feature_columns),
            'provided_features': len(self.feature_columns) - len(missing),
            'imputed_features': len(missing),
            'missing_feature_names': missing,
            'data_completeness': f"{((len(self.feature_columns) - len(missing)) / len(self.feature_columns) * 100):.1f}%"
        }
    
    def predict_burnout_risk(self, employee_data: Union[Dict, pd.DataFrame]) -> Union[float, np.ndarray]:
        """
        Predict burnout risk for employee(s).
        
        Args:
            employee_data: Employee features (dict for single, DataFrame for multiple)
        
        Returns:
            Burnout risk score(s) between 0 and 1 (higher = more risk)
        """
        features = self.prepare_features(employee_data)
        features_scaled = self.scalers['burnout_risk'].transform(features)
        predictions = self.models['burnout_risk'].predict(features_scaled)
        
        # Clip predictions to valid range [0, 1]
        predictions = np.clip(predictions, 0, 1)
        
        return predictions[0] if len(predictions) == 1 else predictions
    
    def predict_wellbeing(self, employee_data: Union[Dict, pd.DataFrame]) -> Union[float, np.ndarray]:
        """
        Predict wellbeing score for employee(s).
        
        Args:
            employee_data: Employee features (dict for single, DataFrame for multiple)
        
        Returns:
            Wellbeing score(s) between 0 and 100 (higher = better wellbeing)
        """
        features = self.prepare_features(employee_data)
        features_scaled = self.scalers['wellbeing'].transform(features)
        predictions = self.models['wellbeing'].predict(features_scaled)
        
        # Clip predictions to valid range [0, 100]
        predictions = np.clip(predictions, 0, 100)
        
        return predictions[0] if len(predictions) == 1 else predictions
    
    def predict_efficiency(self, employee_data: Union[Dict, pd.DataFrame]) -> Union[float, np.ndarray]:
        """
        Predict efficiency score for employee(s).
        
        Args:
            employee_data: Employee features (dict for single, DataFrame for multiple)
        
        Returns:
            Efficiency score(s) between 0 and 100 (higher = more efficient)
        """
        features = self.prepare_features(employee_data)
        features_scaled = self.scalers['efficiency'].transform(features)
        predictions = self.models['efficiency'].predict(features_scaled)
        
        # Clip predictions to valid range [0, 100]
        predictions = np.clip(predictions, 0, 100)
        
        return predictions[0] if len(predictions) == 1 else predictions
    
    def predict_all(self, employee_data: Union[Dict, pd.DataFrame]) -> Dict[str, Union[float, np.ndarray]]:
        """
        Predict all three metrics for employee(s).
        
        Args:
            employee_data: Employee features (dict for single, DataFrame for multiple)
        
        Returns:
            Dictionary with burnout_risk, wellbeing, and efficiency predictions
        """
        return {
            'burnout_risk': self.predict_burnout_risk(employee_data),
            'wellbeing': self.predict_wellbeing(employee_data),
            'efficiency': self.predict_efficiency(employee_data)
        }
    
    def get_risk_category(self, burnout_risk: float) -> Tuple[str, str]:
        """
        Categorize burnout risk level.
        
        Args:
            burnout_risk: Burnout risk score (0-1)
        
        Returns:
            Tuple of (category, description)
        """
        if burnout_risk < 0.3:
            return ("Low", "Employee shows minimal signs of burnout")
        elif burnout_risk < 0.6:
            return ("Moderate", "Employee may be experiencing some stress")
        elif burnout_risk < 0.8:
            return ("High", "Employee shows concerning signs of burnout")
        else:
            return ("Critical", "Immediate intervention recommended")
    
    def get_wellbeing_category(self, wellbeing: float) -> Tuple[str, str]:
        """
        Categorize wellbeing level.
        
        Args:
            wellbeing: Wellbeing score (0-100)
        
        Returns:
            Tuple of (category, description)
        """
        if wellbeing >= 80:
            return ("Excellent", "Employee has strong mental and physical wellbeing")
        elif wellbeing >= 60:
            return ("Good", "Employee's wellbeing is satisfactory")
        elif wellbeing >= 40:
            return ("Fair", "Employee's wellbeing needs attention")
        else:
            return ("Poor", "Employee's wellbeing requires immediate support")
    
    def get_efficiency_category(self, efficiency: float) -> Tuple[str, str]:
        """
        Categorize efficiency level.
        
        Args:
            efficiency: Efficiency score (0-100)
        
        Returns:
            Tuple of (category, description)
        """
        if efficiency >= 80:
            return ("Excellent", "Highly productive and efficient")
        elif efficiency >= 60:
            return ("Good", "Performing well with room for improvement")
        elif efficiency >= 40:
            return ("Moderate", "Performance is below expected levels")
        else:
            return ("Low", "Significant performance concerns")
    
    def get_feature_importance(self, model_type: str, top_n: int = 10) -> pd.DataFrame:
        """
        Get top N most important features for a model.
        
        Args:
            model_type: One of 'burnout_risk', 'wellbeing', 'efficiency'
            top_n: Number of top features to return
        
        Returns:
            DataFrame with feature names and importance scores
        """
        importance_file = self.models_dir / f'{model_type}_feature_importance.csv'
        
        if not importance_file.exists():
            raise ValueError(f"Feature importance file not found for {model_type}")
        
        df = pd.read_csv(importance_file)
        return df.head(top_n)
    
    def generate_report(self, employee_data: Dict, employee_name: str = "Employee") -> str:
        """
        Generate a comprehensive prediction report for an employee.
        
        Args:
            employee_data: Dictionary with employee features
            employee_name: Name of the employee for the report
        
        Returns:
            Formatted string report
        """
        predictions = self.predict_all(employee_data)
        
        burnout_risk = predictions['burnout_risk']
        wellbeing = predictions['wellbeing']
        efficiency = predictions['efficiency']
        
        risk_cat, risk_desc = self.get_risk_category(burnout_risk)
        wellbeing_cat, wellbeing_desc = self.get_wellbeing_category(wellbeing)
        efficiency_cat, efficiency_desc = self.get_efficiency_category(efficiency)
        
        report = f"""
{'='*70}
WORKFORCE ANALYTICS PREDICTION REPORT
{'='*70}

Employee: {employee_name}
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*70}
PREDICTIONS
{'='*70}

1. BURNOUT RISK
   Score: {burnout_risk:.2%}
   Category: {risk_cat}
   Assessment: {risk_desc}

2. WELLBEING SCORE
   Score: {wellbeing:.1f}/100
   Category: {wellbeing_cat}
   Assessment: {wellbeing_desc}

3. EFFICIENCY SCORE
   Score: {efficiency:.1f}/100
   Category: {efficiency_cat}
   Assessment: {efficiency_desc}

{'='*70}
RECOMMENDATIONS
{'='*70}
"""
        
        # Add recommendations based on predictions
        recommendations = []
        
        if burnout_risk > 0.6:
            recommendations.append("• Schedule immediate one-on-one to discuss workload")
            recommendations.append("• Consider reducing work hours or redistributing tasks")
            recommendations.append("• Encourage time off and stress management resources")
        
        if wellbeing < 60:
            recommendations.append("• Provide access to mental health support")
            recommendations.append("• Evaluate work-life balance concerns")
            recommendations.append("• Consider wellness program enrollment")
        
        if efficiency < 60:
            recommendations.append("• Review task assignments and priorities")
            recommendations.append("• Identify blockers or skill gaps")
            recommendations.append("• Provide additional training or support")
        
        if not recommendations:
            recommendations.append("• Continue monitoring employee metrics")
            recommendations.append("• Maintain current support and engagement levels")
        
        report += "\n".join(recommendations)
        report += f"\n\n{'='*70}\n"
        
        return report


def main():
    """
    Example usage of the WorkforceAnalyticsPredictor.
    Demonstrates handling of missing values and partial data.
    """
    # Initialize predictor
    predictor = WorkforceAnalyticsPredictor()
    
    print("\n" + "="*70)
    print("EXAMPLE 1: Partial Employee Data (Missing Values Handled)")
    print("="*70 + "\n")
    
    # Example with only partial data - most features missing
    partial_employee = {
        'age': 32,
        'experience_years': 5,
        'work_hours_per_day': 9.5,
        'overtime_hours': 15,
        'emails_sent': 45,
        'meetings_per_week': 12,
        'task_completion_rate': 0.75,
        'role_Developer': 1,
    }
    
    # Show what's missing
    print("Provided features:")
    for key, value in partial_employee.items():
        print(f"  {key}: {value}")
    
    print("\n" + "-"*70)
    
    # Get imputation summary
    imputation_info = predictor.get_imputed_summary(partial_employee)
    print(f"\nData Completeness: {imputation_info['data_completeness']}")
    print(f"Provided: {imputation_info['provided_features']} features")
    print(f"Imputed: {imputation_info['imputed_features']} features")
    print(f"\nFirst 10 imputed features:")
    for feature in imputation_info['missing_feature_names'][:10]:
        print(f"  - {feature}")
    print(f"  ... and {len(imputation_info['missing_feature_names']) - 10} more")
    
    # Make predictions
    predictions = predictor.predict_all(partial_employee)
    
    print("\n" + "="*70)
    print("PREDICTIONS (with imputed missing values)")
    print("="*70)
    print(f"Burnout Risk: {predictions['burnout_risk']:.2%}")
    print(f"Wellbeing: {predictions['wellbeing']:.1f}/100")
    print(f"Efficiency: {predictions['efficiency']:.1f}/100")
    
    print("\n" + "="*70)
    print("EXAMPLE 2: Complete Employee Data")
    print("="*70 + "\n")
    
    # Example employee data
    example_employee = {
        'age': 32,
        'experience_years': 5,
        'work_hours_per_day': 9.5,
        'days_worked_per_week': 5,
        'overtime_hours': 15,
        'lunch_break_minutes': 30,
        'coffee_breaks_per_day': 2,
        'punctuality_score': 0.85,
        'attendance_rate': 0.95,
        'late_arrivals': 2,
        'biometric_match_score': 0.98,
        'emails_sent': 45,
        'emails_received': 60,
        'email_response_time': 2.5,
        'after_hours_emails': 8,
        'meetings_per_week': 12,
        'meeting_hours': 10,
        'meeting_acceptance_rate': 0.9,
        'declined_meetings': 1,
        'focus_time_hours': 20,
        'messages_sent': 150,
        'messages_received': 180,
        'after_hours_messages': 20,
        'response_time_minutes': 15,
        'reactions_given': 30,
        'status_available_percentage': 0.7,
        'status_busy_percentage': 0.2,
        'status_away_percentage': 0.1,
        'commits_per_week': 15,
        'prs_created': 3,
        'prs_reviewed': 5,
        'code_review_time_hours': 4,
        'pr_merge_rate': 0.85,
        'avg_pr_size_lines': 200,
        'github_pr_merge_time': 24,
        'tasks_assigned': 20,
        'tasks_completed_per_week': 15,
        'task_completion_rate': 0.75,
        'overdue_tasks': 2,
        'avg_task_completion_time': 3,
        'hours_logged': 40,
        'projects_active': 3,
        'context_switches_per_day': 8,
        'bugs_reported': 5,
        'bugs_fixed': 4,
        'document_edits': 10,
        'shared_files': 5,
        'work_pattern_consistency': 0.8,
        'after_hours_activity_ratio': 0.15,
        'communication_balance': 0.7,
        'meeting_to_work_ratio': 0.25,
        'code_commit_consistency': 0.85,
        'task_velocity': 0.75,
        'collaboration_score': 0.8,
        'peer_interaction_frequency': 25,
        'message_after_hours_ratio': 0.13,
        'email_after_hours_ratio': 0.18,
        'weekend_work_hours': 2,
        'daily_active_hours': 8.5,
        'work_life_balance_score': 0.7,
        'days_off_taken': 10,
        'sick_days': 2,
        'tools_used': 8,
        'tool_switch_frequency': 5,
        'training_hours': 5,
        'documentation_contributions': 8,
        'team_size': 7,
        'one_on_ones_conducted': 2,
        'deliverables_completed': 12,
        'quality_score': 0.85,
        'average_email_length': 150,
        'average_message_length': 50,
        'sentiment_email_score': 0.6,
        'sentiment_chat_score': 0.7,
        'voluntary_contributions': 5,
        'initiative_score': 0.75,
        'unique_contacts_per_week': 15,
        'cross_team_interactions': 8,
        'code_review_comments_received': 10,
        'refactoring_commits': 3,
        'blocked_time_hours': 2,
        'dependency_wait_time_hours': 3,
        'new_ideas_proposed': 2,
        'experiments_run': 1,
        'avg_first_response_time_hours': 1.5,
        'response_rate': 0.9,
        'meeting_preparation_score': 0.8,
        'meeting_participation_score': 0.85,
        'interruptions_per_day': 5,
        'deep_work_blocks': 2,
        'concurrent_tasks': 4,
        'task_switching_rate': 6,
        'urgent_tasks_percentage': 0.2,
        'tasks_completed_early': 5,
        'mentor_hours_per_week': 2,
        'knowledge_base_contributions': 3,
        'process_compliance_score': 0.9,
        'documentation_quality_score': 0.85,
        'morning_productivity_score': 0.8,
        'afternoon_productivity_score': 0.7,
        'informal_chats_per_week': 10,
        'team_engagement_score': 0.8,
        'self_directed_work_percentage': 0.7,
        'decision_making_authority_score': 0.75,
        'feedback_received_count': 5,
        'feedback_given_count': 6,
        'new_technologies_learned': 2,
        'skill_utilization_score': 0.8,
        'role_Developer': 1,
        'role_Designer': 0,
        'role_Manager': 0,
        'role_QA Engineer': 0,
        'role_Senior Developer': 0,
        'role_Tech Lead': 0
    }
    
    # Generate and print report
    report = predictor.generate_report(example_employee, "John Doe")
    print(report)
    
    print("\n" + "="*70)
    print("EXAMPLE 3: Data with Explicit NaN/None Values")
    print("="*70 + "\n")
    
    # Example with explicit NaN and None values
    employee_with_nans = {
        'age': 28,
        'experience_years': 3,
        'work_hours_per_day': np.nan,  # Missing data
        'overtime_hours': None,         # Missing data
        'emails_sent': 30,
        'meetings_per_week': np.nan,    # Missing data
        'task_completion_rate': 0.85,
        'attendance_rate': None,        # Missing data
        'role_QA Engineer': 1,
    }
    
    print("Input data with NaN/None values:")
    for key, value in employee_with_nans.items():
        print(f"  {key}: {value}")
    
    # Make predictions - NaN and None will be handled automatically
    predictions_nan = predictor.predict_all(employee_with_nans)
    
    print("\n" + "-"*70)
    print("PREDICTIONS (NaN/None values imputed automatically)")
    print("-"*70)
    print(f"Burnout Risk: {predictions_nan['burnout_risk']:.2%}")
    print(f"Wellbeing: {predictions_nan['wellbeing']:.1f}/100")
    print(f"Efficiency: {predictions_nan['efficiency']:.1f}/100")
    
    # Show top features for each model
    print("\n" + "="*70)
    print("TOP 5 IMPORTANT FEATURES FOR EACH MODEL")
    print("="*70 + "\n")
    
    for model_type in ['burnout_risk', 'wellbeing', 'efficiency']:
        print(f"\n{model_type.replace('_', ' ').title()}:")
        print("-" * 50)
        importance = predictor.get_feature_importance(model_type, top_n=5)
        for _, row in importance.iterrows():
            print(f"  {row['feature']:.<40} {row['importance']:.4f}")
    
    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
✓ Missing features are automatically imputed using median values
✓ NaN and None values in input are handled gracefully
✓ You only need to provide the features you have available
✓ Default role is 'Developer' if no role is specified
✓ Imputation summary shows what was filled in
✓ The more features you provide, the more accurate the predictions

RECOMMENDATION: Try to provide at least these key features:
  - Work hours and overtime
  - Task completion rate
  - Email/meeting metrics
  - Attendance and punctuality
  - Role information
""")


if __name__ == "__main__":
    main()
