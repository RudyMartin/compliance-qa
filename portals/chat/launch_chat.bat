@echo off
echo ========================================
echo   Unified Chat Portal Launcher
echo ========================================
echo.

REM Check if port argument provided
if "%1"=="" (
    set PORT=8502
) else (
    set PORT=%1
)

echo Starting Unified Chat Portal on port %PORT%...
echo URL: http://localhost:%PORT%
echo.
echo Features:
echo   - Chat with multiple modes
echo   - Workflow management
echo   - QA Compliance checking
echo   - Flow Agreements
echo.
echo Press CTRL+C to stop the server
echo ========================================
echo.

REM Run Streamlit with specified port
streamlit run chat_portal_unified.py --server.port=%PORT% --server.headless=true

pause