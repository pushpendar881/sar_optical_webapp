@echo off
REM Windows batch script to setup and run the SAR-to-Optical web app

if "%1"=="" (
    echo Usage: setup.bat "C:\path\to\your\seg_cyclegan_project"
    echo.
    echo Example: setup.bat "C:\Users\YourName\Downloads\seg_cyclegan_project"
    pause
    exit /b 1
)

echo Setting up SAR-to-Optical web app...
python setup.py "%1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Setup failed! Press any key to exit.
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
pause