@echo off
echo ========================================
echo Relaunching Flow Portal V4...
echo ========================================
echo.

REM Kill existing Streamlit instances on port 8516
echo Stopping existing portal on port 8516...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8516') do (
    taskkill /F /PID %%a 2>nul
)

timeout /t 2 /nobreak >nul

REM Change to flow portal directory
cd /d "C:\Users\marti\compliance-qa\portals\flow"

REM Launch the portal
echo Starting Flow Portal V4 on port 8516...
echo.
echo Portal will be available at: http://localhost:8516
echo.
echo Press Ctrl+C to stop the portal
echo ========================================
echo.

python relaunch.py