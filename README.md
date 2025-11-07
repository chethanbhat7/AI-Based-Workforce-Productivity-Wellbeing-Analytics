# 🏥 AI-Based Workforce Productivity & Wellbeing Analytics

> An intelligent system for early burnout detection and workforce wellbeing monitoring using machine learning and workplace integrations.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Problem Statement

Healthcare and public sector organizations across Denmark, Norway, Sweden, and Finland are facing:
- **Staff shortages** and high turnover rates
- **Burnout** leading to increased absenteeism
- **Low morale** due to increased service demands and aging populations
- **Lack of early warning signals** when teams are under stress
- **Imbalanced workloads** without visibility

Traditional HR systems only record attendance, shifts, and sick leaves — they don't provide actionable insights into workforce wellbeing. By the time employees report stress, it's often too late.

## 💡 Solution

An **AI-powered analytics platform** that:
- ✅ **Continuously monitors** workforce wellbeing indicators
- ✅ **Detects early signs** of burnout using machine learning
- ✅ **Provides actionable insights** for managers and supervisors
- ✅ **Integrates with existing tools** (Microsoft 365, Slack, Jira, Asana)
- ✅ **Recommends proactive measures** to improve productivity and morale

## 🚀 Features

### For Supervisors
- 📊 **Team Overview Dashboard** - Real-time team health metrics
- ⚠️ **Burnout Alerts** - Early warning for high-risk team members
- 📈 **Productivity Analytics** - Track team performance trends
- 🎯 **Workload Balancing** - Identify imbalanced task distribution
- 💬 **Support Requests** - Team members can request help

### For Team Members
- 🏥 **Wellbeing Profile** - Personal productivity and health metrics
- 📉 **Burnout Risk Score** - AI-powered burnout prediction (0-100%)
- ⚡ **Efficiency Tracking** - Work pattern analysis
- 📅 **Meeting Analytics** - Time spent in meetings vs. focused work
- 💌 **Anonymous Support** - Request help when feeling overwhelmed

### AI/ML Capabilities
- 🤖 **XGBoost Models** - Trained on workforce productivity data
- 🎯 **23 Feature Extraction** - From meetings, tasks, communication, work hours
- 📊 **Dual Predictions**:
  - **Performance Score** (0-100%)
  - **Burnout Risk Score** (0-100%)
- 🔍 **Interpretable Results** - Understand what drives predictions
- 📈 **Trend Analysis** - Historical tracking and forecasting

## 🏗️ Architecture

```
┌─────────────┐
│   Frontend  │ React + TypeScript + Material-UI
│  (Port 5173)│
└──────┬──────┘
       │
       ├──────────────────┐
       │                  │
┌──────▼───────┐   ┌──────▼──────┐
│ Flask Backend│   │   Firebase  │
│  (Port 5000) │   │  Firestore  │
└──────┬───────┘   └─────────────┘
       │
┌──────▼──────────┐
│ FastAPI Backend │ ML Prediction Engine
│  (Port 8000)    │
└──────┬──────────┘
       │
       ├─────────┬─────────┬─────────┐
       │         │         │         │
┌──────▼────┐ ┌─▼────┐ ┌──▼───┐ ┌───▼──┐
│ Microsoft │ │Slack │ │ Jira │ │Asana │
│   Graph   │ │      │ │      │ │      │
└───────────┘ └──────┘ └──────┘ └──────┘
```

See [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md) for detailed diagrams.

## 📦 Tech Stack

### Frontend
- **React 18** with TypeScript
- **Material-UI (MUI)** for components
- **Vite** for fast development
- **Firebase** for authentication & data storage

### Backend
- **Flask** - Web backend and API gateway
- **FastAPI** - ML prediction service
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Production database
- **SQLite** - Development database

### Machine Learning
- **XGBoost** - Gradient boosting models
- **scikit-learn** - Feature scaling and preprocessing
- **pandas** - Data manipulation
- **NumPy** - Numerical operations

### Integrations
- **Microsoft Graph API** - Calendar, Teams, Outlook
- **Slack API** - Messages, reactions, user activity
- **Jira API** - Issues, worklogs, time tracking
- **Asana API** - Tasks, projects, completion rates

## 🛠️ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/AI-Based-Workforce-Productivity-Wellbeing-Analytics.git
cd AI-Based-Workforce-Productivity-Wellbeing-Analytics
```

### 2. Setup Backend (Automated)
```bash
./setup_backend.sh
```

Or manually:

```bash
# Setup Flask backend
cd app/backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup FastAPI backend
cd ../../api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment

**app/backend/.env:**
```bash
FLASK_PORT=5000
DATABASE_URL=sqlite:///workforce.db
FASTAPI_URL=http://localhost:8000
```

**api/.env:**
```bash
PORT=8000
DATABASE_URL=sqlite:///api.db

# Integration credentials
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
# ... (see setup_backend.sh for full template)
```

### 4. Start Services

**Terminal 1 - FastAPI (Analytics Engine):**
```bash
cd api
source venv/bin/activate
python main.py
# Runs on http://localhost:8000
```

**Terminal 2 - Flask (Web Backend):**
```bash
cd app/backend
source venv/bin/activate
python app.py
# Runs on http://localhost:5000
```

**Terminal 3 - React Frontend:**
```bash
cd app/frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

### 5. Test Integration

```bash
python test_backend_integration.py
```

Expected output:
```
✅ Flask Backend is running
✅ FastAPI Backend is running
✅ User registered successfully
✅ Analytics updated successfully
📈 Analytics Summary:
  Wellbeing Score:      72%
  Burnout Risk:         38%
  Efficiency:           85%
```

## 📚 Documentation

### Core Documentation
- **[BACKEND_INTEGRATION_SUMMARY.md](BACKEND_INTEGRATION_SUMMARY.md)** - Complete integration overview
- **[FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md)** - Frontend integration guide
- **[ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)** - System architecture diagrams
- **[PREDICTION_INTEGRATION.md](api/PREDICTION_INTEGRATION.md)** - ML model details

### Integration Guides
- **[JIRA_INTEGRATION.md](api/JIRA_INTEGRATION.md)** - Jira setup and usage
- **[INTEGRATION_EXAMPLES.tsx](app/frontend/INTEGRATION_EXAMPLES.tsx)** - Frontend code examples

### API Documentation
- **Flask API** - `http://localhost:5000/docs` (after starting)
- **FastAPI API** - `http://localhost:8000/docs` (interactive Swagger UI)

## 🔌 API Endpoints

### Flask Backend (Port 5000)

#### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - User login
- `GET /api/health` - Health check

#### Analytics
- `POST /api/analytics/update/{user_id}` - Update user analytics
- `GET /api/analytics/{user_id}` - Get user analytics
- `POST /api/analytics/batch` - Batch update multiple users

### FastAPI Backend (Port 8000)

#### Predictions
- `POST /features/predict/{user_id}` - Get ML predictions
- `POST /features/extract/{user_id}` - Extract features only
- `POST /features/predict/batch` - Batch predictions
- `GET /features/importance/{target}` - Feature importance

#### OAuth Integration
- `GET /auth/{provider}/authorize` - Start OAuth flow
- `GET /auth/{provider}/callback` - OAuth callback
- `GET /auth/status/{user_id}` - Check integration status

## 🧪 Testing

### Run Backend Integration Tests
```bash
python test_backend_integration.py
```

### Run ML Model Tests
```bash
cd api
pytest tests/
```

### Manual Testing
```bash
# Test Flask backend
curl http://localhost:5000/api/health

# Test FastAPI backend
curl http://localhost:8000/health

# Update analytics for a user
curl -X POST http://localhost:5000/api/analytics/update/USER_ID
```

## 🔐 Security

- ✅ OAuth2 for external API authentication
- ✅ Encrypted token storage in database
- ✅ CORS protection
- ✅ Password hashing with bcrypt
- ✅ Environment-based configuration
- ✅ Input validation and sanitization

## 📊 ML Model Details

### Input Features (23 total)

**Meeting Metrics (4):**
- meeting_hours_per_week
- meeting_count_per_week
- avg_meeting_duration_hours
- recurring_meeting_ratio

**Communication Metrics (5):**
- messages_sent_per_week
- messages_received_per_week
- avg_response_time_hours
- communication_balance
- reaction_count_per_week

**Task Metrics (6):**
- task_completion_rate
- tasks_completed_per_week
- tasks_in_progress
- avg_task_duration_days
- overdue_tasks_ratio
- task_priority_distribution

**Work Hours Metrics (8):**
- logged_hours_per_week
- early_starts_count
- late_exits_count
- weekend_work_hours
- and more...

### Outputs

- **Performance Score** (0-100%): Overall productivity metric
- **Burnout Risk Score** (0-100%): Likelihood of burnout

### Model Performance
- Algorithm: XGBoost (Gradient Boosting)
- Training: Employee productivity dataset
- Validation: Cross-validation with 80/20 split

## 🚀 Deployment

### Production Checklist

- [ ] Set up PostgreSQL database
- [ ] Configure Redis for caching
- [ ] Set up Celery for background jobs
- [ ] Configure environment variables
- [ ] Set up reverse proxy (Nginx)
- [ ] Enable HTTPS
- [ ] Configure monitoring (Prometheus/Grafana)
- [ ] Set up logging aggregation
- [ ] Configure backup strategy

See [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md) for production deployment details.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Backend Development** - Flask & FastAPI integration
- **Frontend Development** - React & Material-UI
- **ML Engineering** - XGBoost models & feature engineering
- **Integration** - OAuth2 & external APIs

## 📧 Support

For issues or questions:
- 📖 Check the documentation in the `/docs` folder
- 🐛 Open an issue on GitHub
- 💬 Contact the development team

## 🎯 Roadmap

### Current Version (v1.0)
- ✅ Basic analytics dashboard
- ✅ ML-powered predictions
- ✅ Integration with 4 major platforms
- ✅ Real-time burnout alerts

### Upcoming Features
- 🔄 Historical trend analysis
- 📊 Advanced visualization dashboards
- 🤖 Automated intervention recommendations
- 📱 Mobile app
- 🌐 Multi-language support (Danish, Norwegian, Swedish, Finnish)
- 🔔 Proactive notification system
- 📈 Team comparison and benchmarking

## 🙏 Acknowledgments

- XGBoost for the excellent ML library
- FastAPI for the high-performance Python framework
- React and Material-UI for the beautiful frontend
- All the open-source contributors who made this possible

---

**Made with ❤️ for better workforce wellbeing**
