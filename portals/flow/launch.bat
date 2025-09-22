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

REM Run Streamlit with specified port
streamlit run flow_portal_v4.py --server.port=%PORT% --server.headless=true

pause