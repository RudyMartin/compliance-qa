@echo off
echo ========================================
echo   Flow Portal V4 Launcher
echo ========================================
echo.

REM Check if port argument provided
if "%1"=="" (
    set PORT=8501
) else (
    set PORT=%1
)

echo Starting Flow Portal on port %PORT%...
echo URL: http://localhost:%PORT%
echo.
echo Press CTRL+C to stop the server
echo ========================================
echo.

REM Run unified launcher with specified port
python launch_portal.py --port %PORT%

pause