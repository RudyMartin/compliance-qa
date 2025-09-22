@echo off
echo [START] Launching Flow Portal V4...
cd /d "%~dp0"
python -m streamlit run flow_portal_v4.py --server.port=8550 --server.headless=false
pause