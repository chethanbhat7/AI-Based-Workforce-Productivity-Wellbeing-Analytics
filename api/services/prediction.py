"""
ML Prediction Service
Loads trained models and makes predictions on employee features
"""
import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class PredictionService:
    """
    Service for loading ML models and making predictions
    """

    def __init__(self, model_dir: str = None):
        """
        Initialize the prediction service

        Args:
            model_dir: Directory containing the trained models
        """
        if model_dir is None:
            # Default to model directory relative to api folder
            model_dir = Path(__file__).parent.parent.parent / "model"

        self.model_dir = Path(model_dir)
        self.models = {}
        self.label_encoders = {}
        self.scaler = None
        self.feature_names = None

        # Target columns
        self.target_cols = [
            "performance_score",
            "burnout_risk_score"
        ]

        self._load_models()

    def _load_models(self):
        """Load all trained models and the feature scaler"""
        try:
            # Load feature scaler
            scaler_path = self.model_dir / "feature_scaler.pkl"
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
                logger.info("✅ Loaded feature scaler")
            else:
                logger.warning(f"⚠️ Feature scaler not found at {scaler_path}")
                return

            # Load models for each target
            for target in self.target_cols:
                model_path = self.model_dir / f"model_{target}.pkl"

                if model_path.exists():
                    self.models[target] = joblib.load(model_path)
                    logger.info(f"✅ Loaded model for {target}")

                    # Try to load label encoder if it exists (for classification)
                    le_path = self.model_dir / f"label_encoder_{target}.pkl"
                    if le_path.exists():
                        self.label_encoders[target] = joblib.load(le_path)
                        logger.info(f"✅ Loaded label encoder for {target}")
                else:
                    logger.warning(f"⚠️ Model not found for {target} at {model_path}")

            # Define expected feature names (in correct order)
            self.feature_names = [
                'meeting_hours_per_week',
                'meeting_counts_per_week',
                'messages_sent_per_week',
                'messages_received_per_week',
                'avg_response_latency_min',
                'communication_burstiness',
                'after_hours_message_ratio',
                'communication_balance',
                'conversation_length_avg',
                'avg_tasks_assigned_per_week',
                'avg_tasks_completed_per_week',
                'task_completion_rate',
                'avg_task_age_days',
                'overdue_task_ratio',
                'task_comment_sentiment_mean',
                'logged_hours_per_week',
                'variance_in_work_hours',
                'late_start_count_per_week',
                'early_exit_count_per_week',
                'early_start_count_per_week',
                'late_exit_count_per_week',
                'absenteeism_rate',
                'avg_break_length_minutes_per_week'
            ]

            logger.info(f"✅ Prediction service initialized with {len(self.models)} models")

        except Exception as e:
            logger.error(f"❌ Error loading models: {e}")
            raise

    def predict(self, features: Dict) -> Dict:
        """
        Make predictions for employee metrics

        Args:
            features: Dictionary containing all required feature values

        Returns:
            Dictionary with predictions and interpretations
        """
        try:
            if not self.models:
                raise ValueError("No models loaded. Please train models first.")

            # Convert features dict to DataFrame
            if isinstance(features, dict):
                # Ensure all feature names are present
                feature_values = []
                for feature_name in self.feature_names:
                    if feature_name not in features:
                        logger.warning(f"⚠️ Missing feature: {feature_name}, using default 0")
                        feature_values.append(0)
                    else:
                        feature_values.append(features[feature_name])

                df = pd.DataFrame([feature_values], columns=self.feature_names)
            else:
                df = pd.DataFrame([features])

            # Scale features
            X_scaled = self.scaler.transform(df)

            # Make predictions
            predictions = {}

            for target in self.target_cols:
                if target not in self.models:
                    logger.warning(f"⚠️ No model available for {target}")
                    continue

                model = self.models[target]
                pred = model.predict(X_scaled)

                # If classification model, decode predictions
                if target in self.label_encoders:
                    pred_decoded = self.label_encoders[target].inverse_transform(pred.astype(int))
                    predictions[target] = pred_decoded[0]

                    # Get probability predictions if available
                    if hasattr(model, 'predict_proba'):
                        proba = model.predict_proba(X_scaled)
                        predictions[f"{target}_confidence"] = float(proba.max())

                        # Store class probabilities
                        classes = self.label_encoders[target].classes_
                        predictions[f"{target}_probabilities"] = {
                            str(cls): float(prob)
                            for cls, prob in zip(classes, proba[0])
                        }
                else:
                    # Regression model
                    predictions[target] = float(pred[0])

            # Add interpretations
            interpretations = self._interpret_predictions(predictions)

            return {
                'predictions': predictions,
                'interpretations': interpretations,
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"❌ Error making predictions: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def _interpret_predictions(self, predictions: Dict) -> Dict:
        """
        Provide human-readable interpretations of predictions

        Args:
            predictions: Dictionary of raw predictions

        Returns:
            Dictionary of interpretations
        """
        interpretations = {}

        # Interpret performance score
        if 'performance_score' in predictions:
            perf = predictions['performance_score']

            if isinstance(perf, (int, float)):
                if perf >= 0.7:
                    interpretations['performance'] = {
                        'level': 'high',
                        'description': 'High performance - exceeding expectations',
                        'emoji': '✅',
                        'score': float(perf)
                    }
                elif perf >= 0.5:
                    interpretations['performance'] = {
                        'level': 'average',
                        'description': 'Average performance - meeting expectations',
                        'emoji': '➡️',
                        'score': float(perf)
                    }
                else:
                    interpretations['performance'] = {
                        'level': 'low',
                        'description': 'Below average - may need support',
                        'emoji': '⚠️',
                        'score': float(perf)
                    }
            else:
                interpretations['performance'] = {
                    'level': str(perf),
                    'description': f'Performance level: {perf}',
                    'emoji': '📊'
                }

        # Interpret burnout risk
        if 'burnout_risk_score' in predictions:
            burnout = predictions['burnout_risk_score']

            if isinstance(burnout, (int, float)):
                if burnout >= 0.6:
                    interpretations['burnout'] = {
                        'level': 'high',
                        'description': 'HIGH RISK - Immediate intervention recommended',
                        'emoji': '🚨',
                        'score': float(burnout),
                        'recommendations': [
                            'Schedule immediate check-in with manager',
                            'Review workload distribution',
                            'Consider reducing meeting load',
                            'Encourage time off or mental health support'
                        ]
                    }
                elif burnout >= 0.4:
                    interpretations['burnout'] = {
                        'level': 'moderate',
                        'description': 'MODERATE RISK - Monitor closely and provide support',
                        'emoji': '⚠️',
                        'score': float(burnout),
                        'recommendations': [
                            'Monitor workload and stress levels',
                            'Promote work-life balance',
                            'Ensure regular breaks',
                            'Check in during 1-on-1s'
                        ]
                    }
                else:
                    interpretations['burnout'] = {
                        'level': 'low',
                        'description': 'LOW RISK - Employee wellbeing appears healthy',
                        'emoji': '✅',
                        'score': float(burnout),
                        'recommendations': [
                            'Maintain current work patterns',
                            'Continue regular check-ins',
                            'Recognize good performance'
                        ]
                    }
            else:
                interpretations['burnout'] = {
                    'level': str(burnout),
                    'description': f'Burnout risk level: {burnout}',
                    'emoji': '🔥'
                }

        # Add overall risk assessment
        if 'burnout' in interpretations and 'performance' in interpretations:
            burnout_level = interpretations['burnout']['level']
            perf_level = interpretations['performance']['level']

            if burnout_level == 'high':
                interpretations['overall_status'] = {
                    'status': 'critical',
                    'message': 'Employee at high risk of burnout - immediate action needed',
                    'priority': 'urgent'
                }
            elif burnout_level == 'moderate' and perf_level == 'low':
                interpretations['overall_status'] = {
                    'status': 'concerning',
                    'message': 'Employee showing signs of struggle - provide support',
                    'priority': 'high'
                }
            elif burnout_level == 'low' and perf_level == 'high':
                interpretations['overall_status'] = {
                    'status': 'excellent',
                    'message': 'Employee thriving - maintain current trajectory',
                    'priority': 'normal'
                }
            else:
                interpretations['overall_status'] = {
                    'status': 'stable',
                    'message': 'Employee in stable condition - continue monitoring',
                    'priority': 'normal'
                }

        return interpretations

    def batch_predict(self, features_list: List[Dict]) -> List[Dict]:
        """
        Make predictions for multiple employees

        Args:
            features_list: List of feature dictionaries

        Returns:
            List of prediction results
        """
        results = []

        for features in features_list:
            result = self.predict(features)
            results.append(result)

        return results

    def get_feature_importance(self, target: str = "burnout_risk_score") -> Dict:
        """
        Get feature importance for a specific model

        Args:
            target: Target variable to get importances for

        Returns:
            Dictionary mapping feature names to importance scores
        """
        if target not in self.models:
            raise ValueError(f"No model found for target: {target}")

        model = self.models[target]

        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_

            # Create feature importance dictionary
            feature_importance = {
                feature: float(importance)
                for feature, importance in zip(self.feature_names, importances)
            }

            # Sort by importance
            sorted_importance = dict(
                sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            )

            return sorted_importance
        else:
            return {}


# Global prediction service instance
_prediction_service = None


def get_prediction_service() -> PredictionService:
    """
    Get or create the global prediction service instance
    """
    global _prediction_service

    if _prediction_service is None:
        _prediction_service = PredictionService()

    return _prediction_service
