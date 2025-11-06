@echo off
REM Workforce Wellbeing Analysis - Development Setup Script for Windows

echo.
echo Workforce Wellbeing Analysis - Development Setup
echo ==================================================
echo.

if not exist "app" (
    echo Error: app folder not found
    exit /b 1
)

cd app

REM Backend Setup
echo Setting up Backend...
if not exist "backend\venv" (
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    if not exist ".env" (
        copy .env.example .env
        echo Created .env file
    )
    cd ..
    echo Backend setup complete
) else (
    echo Backend venv already exists
)

REM Frontend Setup
echo Setting up Frontend...
if not exist "frontend\node_modules" (
    cd frontend
    call npm install
    cd ..
    echo Frontend setup complete
) else (
    echo Frontend node_modules already exists
)

REM Display next steps
echo.
echo Setup Complete!
echo.
echo Next Steps:
echo.
echo Terminal 1 - Start Backend:
echo   cd app\backend
echo   venv\Scripts\activate.bat
echo   python main.py
echo.
echo Terminal 2 - Start Frontend:
echo   cd app\frontend
echo   npm run dev
echo.
echo Or use Docker:
echo   cd app
echo   docker-compose up
echo.
echo URLs:
echo   Frontend:  http://localhost:5173
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
