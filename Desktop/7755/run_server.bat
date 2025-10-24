@echo off
echo ============================================
echo Starting Dating Chatbot Server
echo ============================================
echo.
echo Server will start at: http://localhost:8000
echo Web UI available at: http://localhost:8000/ui
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.

python -m uvicorn backend.main:app --reload

pause
