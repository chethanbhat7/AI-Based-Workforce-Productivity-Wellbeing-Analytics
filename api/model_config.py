"""
Configuration for ML Model Storage
Models should be hosted externally for serverless deployment
"""
import os

# Model Storage Configuration
MODEL_STORAGE_TYPE = os.getenv("MODEL_STORAGE_TYPE", "local")  # 'local', 's3', 'gcs', 'url'

# For URL-based storage (simplest for Vercel)
MODEL_URLS = {
    "burnout_risk_model": os.getenv("BURNOUT_MODEL_URL", ""),
    "efficiency_model": os.getenv("EFFICIENCY_MODEL_URL", ""),
    "wellbeing_model": os.getenv("WELLBEING_MODEL_URL", ""),
    "burnout_risk_scaler": os.getenv("BURNOUT_SCALER_URL", ""),
    "efficiency_scaler": os.getenv("EFFICIENCY_SCALER_URL", ""),
    "wellbeing_scaler": os.getenv("WELLBEING_SCALER_URL", ""),
}

# Local fallback paths (for development)
LOCAL_MODEL_PATHS = {
    "burnout_risk_model": "../model/models/burnout_risk_model.pkl",
    "efficiency_model": "../model/models/efficiency_model.pkl",
    "wellbeing_model": "../model/models/wellbeing_model.pkl",
    "burnout_risk_scaler": "../model/models/burnout_risk_scaler.pkl",
    "efficiency_scaler": "../model/models/efficiency_scaler.pkl",
    "wellbeing_scaler": "../model/models/wellbeing_scaler.pkl",
}

# Feature columns path
FEATURE_COLUMNS_URL = os.getenv("FEATURE_COLUMNS_URL", "")
LOCAL_FEATURE_COLUMNS_PATH = "../model/models/feature_columns.json"
