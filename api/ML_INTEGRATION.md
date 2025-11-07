# ML Model Integration Guide

## Overview

The ML inference models are now integrated with the FastAPI backend. The system can predict:
1. **Burnout Risk** (0-100%): Higher = more risk
2. **Wellbeing Score** (0-100): Higher = better wellbeing  
3. **Efficiency Score** (0-100): Higher = more efficient

## API Endpoints

### 1. Predict Employee Metrics

**POST** `/api/predictions/predict`

Predicts burnout, wellbeing, and efficiency for a single employee.

**Request Body:**
```json
{
  "employee_id": "emp123",
  "features": {
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
```

**Response:**
```json
{
  "employee_id": "emp123",
  "burnout_risk": 0.45,
  "burnout_percentage": 45.0,
  "wellbeing_score": 72.5,
  "efficiency_score": 85.3,
  "risk_category": "Moderate",
  "risk_description": "Employee may be experiencing some stress",
  "wellbeing_category": "Good",
  "efficiency_category": "Excellent",
  "data_completeness": "7.3%",
  "provided_features": 8,
  "imputed_features": 102,
  "recommendations": [
    "⚠️ Monitor closely - signs of stress detected",
    "Review meeting schedule and task distribution",
    "Encourage regular breaks and time off"
  ]
}
```

### 2. Batch Prediction

**POST** `/api/predictions/predict/batch`

Predict metrics for multiple employees at once.

### 3. Feature Importance

**GET** `/api/predictions/feature-importance/{model_type}?top_n=10`

Get the most important features for a specific model.

**Parameters:**
- `model_type`: One of `burnout_risk`, `wellbeing`, `efficiency`
- `top_n`: Number of top features to return (default: 10)

### 4. Model Information

**GET** `/api/predictions/model-info`

Get information about loaded models and their performance metrics.

## Frontend Integration

### Update Burnout Percentage in UI

Here's how to integrate predictions in your React frontend:

```typescript
// services/api.ts
export const getPrediction = async (employeeData: any) => {
  const response = await fetch(`${API_URL}/api/predictions/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      employee_id: employeeData.uid,
      features: {
        age: employeeData.age,
        work_hours_per_day: employeeData.workHoursPerDay,
        overtime_hours: employeeData.overtimeHours,
        emails_sent: employeeData.emailsSent,
        meetings_per_week: employeeData.meetingCount,
        task_completion_rate: employeeData.taskCompletion / 100,
        role_Developer: employeeData.role === 'Developer' ? 1 : 0,
        // Add more fields as available
      }
    })
  });
  
  return await response.json();
};
```

### Usage in Components

```typescript
// In your dashboard component
import { getPrediction } from '../services/api';

const [predictions, setPredictions] = useState<any>(null);

useEffect(() => {
  const fetchPredictions = async () => {
    try {
      const result = await getPrediction(employeeData);
      setPredictions(result);
      
      // Update burnout percentage
      console.log(`Burnout Risk: ${result.burnout_percentage}%`);
      console.log(`Wellbeing: ${result.wellbeing_score}/100`);
      console.log(`Efficiency: ${result.efficiency_score}/100`);
    } catch (error) {
      console.error('Failed to get predictions:', error);
    }
  };
  
  fetchPredictions();
}, [employeeData]);

// Display in UI
<Box>
  <Typography>Burnout Risk: {predictions?.burnout_percentage}%</Typography>
  <Typography>Category: {predictions?.risk_category}</Typography>
  <LinearProgress 
    variant="determinate" 
    value={predictions?.burnout_percentage} 
  />
</Box>
```

## Feature Mapping

The model expects 110+ features but can handle missing data. Here's how Firebase fields map to model features:

| Firebase Field | Model Feature | Type |
|---|---|---|
| `age` | `age` | int |
| `experienceYears` | `experience_years` | float |
| `workHoursPerDay` | `work_hours_per_day` | float |
| `overtimeHours` | `overtime_hours` | float |
| `emailsSent` | `emails_sent` | int |
| `emailsReceived` | `emails_received` | int |
| `messagesSent` | `messages_sent` | int |
| `messagesReceived` | `messages_received` | int |
| `meetingCount` | `meetings_per_week` | int |
| `meetingHours` | `meeting_hours` | float |
| `taskCompletion` | `task_completion_rate` | float (0-1) |
| `tasksCompleted` | `tasks_completed_per_week` | int |
| `role` | `role_*` | one-hot encoded |

## Important Notes

1. **Missing Data Handling**: The model automatically imputes missing features using median values. You only need to provide the data you have available.

2. **Minimum Data**: For best accuracy, try to provide at least:
   - Work hours and overtime
   - Task completion rate
   - Email/meeting metrics  
   - Attendance data
   - Role information

3. **Data Completeness**: The response includes `data_completeness` percentage showing how much data was provided vs imputed.

4. **Recommendations**: The API automatically generates actionable recommendations based on the predictions.

## Testing the API

### Using cURL

```bash
curl -X POST "http://localhost:8000/api/predictions/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "test123",
    "features": {
      "age": 28,
      "work_hours_per_day": 10,
      "overtime_hours": 20,
      "task_completion_rate": 0.65,
      "meetings_per_week": 15,
      "role_Developer": 1
    }
  }'
```

### Using FastAPI Docs

1. Start the backend: `cd api && python main.py`
2. Open browser: `http://localhost:8000/docs`
3. Navigate to "ML Predictions" section
4. Click "Try it out" on `/api/predictions/predict`
5. Enter test data and execute

## Model Performance

The models have been trained on 300 realistic samples with 110+ features:

- **Burnout Risk**: R² = ~0.85, MAE = ~0.08
- **Wellbeing**: R² = ~0.83, MAE = ~7.5
- **Efficiency**: R² = ~0.81, MAE = ~8.2

See `/api/predictions/model-info` for exact metrics.

## Troubleshooting

**Error: "ML Predictor not initialized"**
- Ensure model files exist in `model/models/` directory
- Check that all required `.pkl` and `.json` files are present
- Verify Python can import from the model directory

**Error: "Import predict could not be resolved"**
- This is a linting error and can be ignored
- The import works at runtime due to dynamic path insertion

**Inaccurate Predictions**
- Provide more features for better accuracy
- Check data quality and ranges
- Verify role encoding is correct

## Next Steps

1. ✅ Models integrated with FastAPI
2. ✅ Prediction endpoints created
3. ✅ Feature mapping from Firebase
4. 🔄 Update frontend to call prediction API
5. 🔄 Display burnout percentage in UI
6. 🔄 Show recommendations to supervisors
7. 🔄 Schedule automatic prediction updates
