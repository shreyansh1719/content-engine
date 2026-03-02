@echo off
echo ========================================
echo    AdCraft Pro - Starting Services
echo ========================================
echo.

REM Check that the venv exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo Run:  py -3 -m venv venv
    echo Then: venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check that .env exists
if not exist ".env" (
    echo [WARNING] .env file not found. Copy .env.example and add your OPENAI_API_KEY.
    echo.
)

echo [1/2] Starting FastAPI backend on port 8000...
start /B venv\Scripts\python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload

echo Waiting for backend to initialise...
timeout /t 3 /nobreak >nul

echo [2/2] Starting Streamlit frontend...
echo.
echo ----------------------------------------
echo  Backend API : http://localhost:8000
echo  Frontend    : http://localhost:8501
echo  API Docs    : http://localhost:8000/docs
echo  Health      : http://localhost:8000/health
echo ----------------------------------------
echo.
echo Press Ctrl+C to stop the frontend.
echo The backend process will continue in the background.
echo.

venv\Scripts\streamlit run frontend_app.py
