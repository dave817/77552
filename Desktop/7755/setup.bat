@echo off
echo ==================================
echo Dating Chatbot Setup Script
echo ==================================

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo Installing dependencies...
python -m pip install -r requirements.txt

echo.
echo ==================================
echo Setup completed!
echo ==================================
echo.
echo Next steps:
echo 1. Run tests: python test_api.py
echo 2. Start server: python -m uvicorn backend.main:app --reload
echo 3. Open browser: http://localhost:8000/ui
echo.
pause
