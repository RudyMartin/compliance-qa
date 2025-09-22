@echo off
echo ============================================
echo   SETUP PORTAL - SPECIAL EDITION
echo   Port 8510 (10th Streamlit Instance)
echo ============================================
echo.
echo You have 9 active Streamlit instances
echo This will be instance #10 on port 8510
echo.
echo Starting Special Edition...
echo URL: http://localhost:8510
echo.
echo Press CTRL+C to stop
echo ============================================
echo.

REM Run unified launcher on special port with special theme
python launch_portal.py --port 8510 --theme special

pause