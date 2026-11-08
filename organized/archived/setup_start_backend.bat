@echo off
echo.
echo ================================
echo   SAR-to-Optical Backend Server
echo ================================
echo.
echo Starting backend server...
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo ================================
echo.

python start_backend.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Failed to start backend server!
    echo.
    echo 💡 Make sure you have the required dependencies:
    echo    pip install fastapi uvicorn torch pillow numpy python-multipart
    echo.
    pause
)