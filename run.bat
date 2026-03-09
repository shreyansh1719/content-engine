@echo off
echo.
echo   AdCraft Pro
echo   Starting servers...
echo.

if not exist "venv\Scripts\python.exe" (
    echo   ERROR: venv not found.
    echo   Run: py -3 -m venv venv ^&^& venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

start "AdCraft API" cmd /c "cd /d %~dp0 && venv\Scripts\python -m uvicorn api:app --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul
start "AdCraft Frontend" cmd /c "cd /d %~dp0 && venv\Scripts\streamlit run frontend_app.py --server.port 8501"

echo.
echo   API:      http://localhost:8000
echo   Frontend: http://localhost:8501
echo   Docs:     http://localhost:8000/docs
echo.
pause
