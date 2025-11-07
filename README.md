# Workforce Wellbeing Analysis

An intelligent system for early burnout detection and workforce wellbeing monitoring using machine learning and workplace integrations.

## Overview

This platform continuously monitors workforce wellbeing indicators, detects early signs of burnout using machine learning, and provides actionable insights for managers and supervisors. It integrates with existing tools like Microsoft 365, Slack, Jira, and Asana to collect real-time data.

## Features

### For Supervisors
- Team health metrics dashboard
- Early warning alerts for high-risk team members
- Productivity analytics and trends
- Workload distribution analysis
- Team support request tracking

### For Team Members
- Personal productivity and wellbeing metrics
- AI-powered burnout risk prediction (0-1 scale)
- Work pattern analysis
- Meeting time vs. focused work analysis
- Support request system

### Machine Learning
- Three separate RandomForest models for burnout risk, wellbeing score, and efficiency score
- 110+ features extracted from workplace integrations
- Predictions: Burnout Risk (0-1), Wellbeing Score (0-100), Efficiency Score (0-100)
- Feature importance analysis for interpretability
- Historical tracking and trend analysis

## Tech Stack

**Frontend:** React 18, TypeScript, Material-UI, Vite, Firebase

**Backend:** FastAPI (ML service), SQLAlchemy, PostgreSQL

**Machine Learning:** RandomForest, scikit-learn, pandas, NumPy, XGBoost

**Integrations:** Microsoft Graph API, Slack API, Jira API, Asana API, GitHub API, Google Sheets API, CloudABIS API

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/Workforce-Wellbeing-Analysis.git
cd Workforce-Wellbeing-Analysis
```

2. Setup backend
```bash
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configure environment variables in `api/.env`
```bash
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
SLACK_CLIENT_ID=your_client_id
# ... (see api/.env.example for full template)
```

4. Setup frontend
```bash
cd app/frontend
npm install
```

### Running the Application

Start the FastAPI backend:
```bash
cd api
source venv/bin/activate
python main.py
```

Start the frontend:
```bash
cd app/frontend
npm run dev
```

Access the application at http://localhost:5173

## Training Models

Train the machine learning models using the Jupyter notebook:

```bash
cd model
jupyter notebook train_realistic_models.ipynb
```

The notebook will:
- Load the realistic dataset (300 samples, 110+ features)
- Train three separate models (burnout risk, wellbeing, efficiency)
- Perform cross-validation and model selection
- Save trained models to `model_realistic/` directory
- Generate feature importance analysis and visualizations
## Documentation

- `api/JIRA_INTEGRATION.md` - Jira setup and usage guide
- `api/integrations/GOOGLE_SHEETS_INTEGRATION.md` - Google Sheets attendance tracking
- `api/integrations/CLOUDABIS_INTEGRATION.md` - CloudABIS biometric system setup
- `model/dataset/DATASET_INFO.md` - Dataset information and statistics

## Security

- OAuth2 authentication for external APIs
- Encrypted token storage in database
- Environment-based configuration
- Input validation and sanitization

## License

This project is licensed under the MIT License.

