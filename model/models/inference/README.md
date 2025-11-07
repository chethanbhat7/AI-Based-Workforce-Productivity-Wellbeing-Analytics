# Workforce Analytics Inference Module

This module provides a simple Python interface for making predictions using the trained workforce analytics models.

## Features

- **Three Prediction Types:**
  - Burnout Risk (0-1 scale)
  - Wellbeing Score (0-100 scale)
  - Efficiency Score (0-100 scale)

- **Easy-to-use API:**
  - Single employee predictions
  - Batch predictions for multiple employees
  - Comprehensive prediction reports

- **Automatic Feature Handling:**
  - Missing features are automatically imputed using intelligent strategies
  - NaN and None values in input data are handled gracefully
  - Uses scikit-learn's SimpleImputer with median strategy
  - Proper feature scaling applied automatically
  - Default role is 'Developer' if no role specified

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Basic Usage (with Partial Data)

```python
from predict import WorkforceAnalyticsPredictor

# Initialize predictor
predictor = WorkforceAnalyticsPredictor()

# You only need to provide features you have - missing ones are auto-imputed
employee_data = {
    'age': 32,
    'experience_years': 5,
    'work_hours_per_day': 9.5,
    'overtime_hours': 15,
    'task_completion_rate': 0.75,
    'emails_sent': 45,
    'meetings_per_week': 12,
    'role_Developer': 1,
    # Other 106 features will be automatically imputed!
}

# Predict all metrics at once
predictions = predictor.predict_all(employee_data)

print(f"Burnout Risk: {predictions['burnout_risk']:.2%}")
print(f"Wellbeing: {predictions['wellbeing']:.1f}/100")
print(f"Efficiency: {predictions['efficiency']:.1f}/100")
```

### 4. Individual Predictions

```python
# See which features were missing and imputed
imputation_info = predictor.get_imputed_summary(employee_data)

print(f"Data Completeness: {imputation_info['data_completeness']}")
print(f"Provided: {imputation_info['provided_features']} features")
print(f"Imputed: {imputation_info['imputed_features']} features")
print(f"Missing features: {imputation_info['missing_feature_names'][:5]}...")
```

### 3. Handle NaN/None Values

```python
# The predictor handles NaN and None automatically
import numpy as np

employee_with_missing = {
    'age': 28,
    'work_hours_per_day': np.nan,  # Will be imputed
    'overtime_hours': None,         # Will be imputed
    'emails_sent': 30,              # Provided
    'meetings_per_week': np.nan,    # Will be imputed
    'task_completion_rate': 0.85,   # Provided
    'role_QA Engineer': 1,
}

# Works perfectly fine!
predictions = predictor.predict_all(employee_with_missing)
```

```python
# Predict only burnout risk
burnout = predictor.predict_burnout_risk(employee_data)

# Predict only wellbeing
wellbeing = predictor.predict_wellbeing(employee_data)

# Predict only efficiency
efficiency = predictor.predict_efficiency(employee_data)
```

### 5. Generate Full Report

```python
report = predictor.generate_report(employee_data, "John Doe")
print(report)
```

Output:
```
======================================================================
WORKFORCE ANALYTICS PREDICTION REPORT
======================================================================

Employee: John Doe
Generated: 2025-11-07 14:30:00

======================================================================
PREDICTIONS
======================================================================

1. BURNOUT RISK
   Score: 45.23%
   Category: Moderate
   Assessment: Employee may be experiencing some stress

2. WELLBEING SCORE
   Score: 68.5/100
   Category: Good
   Assessment: Employee's wellbeing is satisfactory

3. EFFICIENCY SCORE
   Score: 72.3/100
   Category: Good
   Assessment: Performing well with room for improvement

======================================================================
RECOMMENDATIONS
======================================================================

• Continue monitoring employee metrics
• Maintain current support and engagement levels

======================================================================
```

### 6. Batch Predictions

```python
import pandas as pd

# Multiple employees
employees_df = pd.DataFrame([
    {'age': 30, 'experience_years': 4, 'overtime_hours': 10, ...},
    {'age': 28, 'experience_years': 3, 'overtime_hours': 20, ...},
    {'age': 35, 'experience_years': 8, 'overtime_hours': 5, ...}
])

# Predict for all employees
burnout_risks = predictor.predict_burnout_risk(employees_df)
wellbeing_scores = predictor.predict_wellbeing(employees_df)
efficiency_scores = predictor.predict_efficiency(employees_df)
```

### 7. Get Feature Importance

```python
# Top 10 features for burnout risk prediction
importance = predictor.get_feature_importance('burnout_risk', top_n=10)
print(importance)
```

## API Reference

### WorkforceAnalyticsPredictor

#### Methods

- **`__init__(models_dir=None)`**
  - Initialize the predictor
  - Loads all models and metadata
  - `models_dir`: Optional path to models directory

- **`predict_burnout_risk(employee_data)`**
  - Predict burnout risk (0-1)
  - Args: dict or DataFrame with employee features
  - Returns: float or numpy array

- **`predict_wellbeing(employee_data)`**
  - Predict wellbeing score (0-100)
  - Args: dict or DataFrame with employee features
  - Returns: float or numpy array

- **`predict_efficiency(employee_data)`**
  - Predict efficiency score (0-100)
  - Args: dict or DataFrame with employee features
  - Returns: float or numpy array

- **`predict_all(employee_data)`**
  - Predict all three metrics
  - Args: dict or DataFrame with employee features
  - Returns: dict with 'burnout_risk', 'wellbeing', 'efficiency'

- **`generate_report(employee_data, employee_name="Employee")`**
  - Generate comprehensive prediction report
  - Returns: formatted string report

- **`get_feature_importance(model_type, top_n=10)`**
  - Get top N important features for a model
  - `model_type`: 'burnout_risk', 'wellbeing', or 'efficiency'
  - Returns: DataFrame with feature names and importance scores

- **`get_missing_features(employee_data)`**
  - Get list of features missing from input data
  - Returns: List of feature names that will be imputed

- **`get_imputed_summary(employee_data)`**
  - Get summary of data completeness
  - Returns: Dict with total/provided/imputed feature counts and percentages

- **`get_risk_category(burnout_risk)`**
  - Categorize burnout risk level
  - Returns: tuple of (category, description)

- **`get_wellbeing_category(wellbeing)`**
  - Categorize wellbeing level
  - Returns: tuple of (category, description)

- **`get_efficiency_category(efficiency)`**
  - Categorize efficiency level
  - Returns: tuple of (category, description)

## Feature Requirements

The model expects 114 features, but **you don't need to provide all of them**!

### How Missing Values Are Handled

1. **Intelligent Imputation**: Missing features are filled with sensible median values based on feature type:
   - Work hours → 8 hours (standard workday)
   - Percentages/ratios → 0.5 (middle value)
   - Counts/frequencies → 5 (reasonable default)
   - Overtime hours → 2 hours
   - Age → 32 years (average)

2. **Role Defaults**: If no role is specified, defaults to 'Developer'

3. **NaN/None Handling**: Explicit NaN or None values in your input are automatically imputed

### Recommended Minimum Features

For best accuracy, try to provide at least these key features:
- **Basic**: age, experience_years, role
- **Work patterns**: work_hours_per_day, overtime_hours, attendance_rate
- **Tasks**: task_completion_rate, tasks_completed_per_week
- **Communication**: emails_sent, meetings_per_week
- **Code** (if applicable): commits_per_week, prs_created

**The more features you provide, the more accurate the predictions!**

**Required feature categories:**
- Demographics: age, experience_years
- Work patterns: work_hours_per_day, overtime_hours, etc.
- Attendance: punctuality_score, attendance_rate, late_arrivals
- Communication: emails_sent/received, messages_sent/received
- Meetings: meetings_per_week, meeting_hours
- Code/Tasks: commits_per_week, tasks_completed, task_completion_rate
- Role: one-hot encoded (role_Developer, role_Designer, etc.)

See `feature_columns.json` for the complete list.

## Running the Example

```bash
cd /path/to/model/models/inference
python predict.py
```

This will run example predictions and show feature importance.

## Model Performance

Current model metrics (test set):

- **Burnout Risk Model:** R² = 0.583, RMSE = 0.107
- **Wellbeing Model:** R² = 0.565, RMSE = 6.178
- **Efficiency Model:** R² = 0.963, RMSE = 5.022

## Integration with Main App

To integrate this inference module into your FastAPI backend:

```python
# In your FastAPI app
from model.models.inference.predict import WorkforceAnalyticsPredictor

# Initialize once at startup
predictor = WorkforceAnalyticsPredictor()

# Use in endpoint
@app.post("/predict")
async def predict_employee_metrics(employee_data: dict):
    predictions = predictor.predict_all(employee_data)
    return predictions
```

## Notes

- Models are trained on realistic synthetic data
- Predictions should be used as indicators, not definitive assessments
- Always combine model predictions with human judgment
- Feature importance files show which metrics matter most for each prediction

## Troubleshooting

**Issue:** `FileNotFoundError` for model files
- Solution: Ensure you're running from the correct directory or specify `models_dir` parameter

**Issue:** Unexpected predictions
- Solution: Check that you're providing realistic feature values
- Solution: Verify role one-hot encoding (only one role should be 1, others 0)

**Issue:** Import errors
- Solution: Install requirements: `pip install -r requirements.txt`
