@echo off
REM QA-Shipping Environment Setup - Windows
REM Generated automatically from settings.yaml on 2025-09-20 06:24:02
REM Sets all credentials for current session

echo Setting QA-Shipping environment variables...

REM Database credentials
set DB_HOST=vectorqa-cluster.cluster-cu562e4m02nq.us-east-1.rds.amazonaws.com
set DB_PORT=5432
set DB_NAME=vectorqa
set DB_USERNAME=vectorqa_user
set DB_PASSWORD=***REMOVED***

REM AWS credentials
set AWS_ACCESS_KEY_ID=***REMOVED***
set AWS_SECRET_ACCESS_KEY=***REMOVED***
set AWS_DEFAULT_REGION=us-east-1

REM MLflow settings
set MLFLOW_TRACKING_URI=http://localhost:5000

REM S3 settings
set S3_BUCKET=nsc-mvp1
set S3_PREFIX=staging/

echo Environment variables set for current session
echo Database: %DB_HOST%
echo AWS Region: %AWS_DEFAULT_REGION%
echo MLflow: %MLFLOW_TRACKING_URI%

REM Test infrastructure connectivity
echo.
echo Testing infrastructure connectivity...

REM Test environment loading
python -c "from infrastructure.environment_manager import get_environment_manager; env_mgr = get_environment_manager(); summary = env_mgr.get_environment_summary(); print('System Status:', 'OK' if all(summary['validation_results'].values()) else 'ISSUES')" 2>nul && echo System validation: OK || echo System validation: FAIL

REM Test settings loader
python -c "from infrastructure.yaml_loader import get_settings_loader; loader = get_settings_loader(); summary = loader.get_settings_summary(); print('Settings loaded from:', summary['source_file'])" 2>nul && echo Settings loader: OK || echo Settings loader: FAIL

REM Test database connection
python -c "from infrastructure.credential_validator import quick_health_check; import asyncio; loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop); healthy = loop.run_until_complete(quick_health_check()); print('Database connection:', 'OK' if healthy else 'FAIL')" 2>nul || echo Database test: Could not run

REM Test AWS S3 (if session manager available)
python -c "from adapters.session.unified_session_manager import UnifiedSessionManager; sm = UnifiedSessionManager(); client = sm.get_s3_client(); print('S3 buckets:', len(client.list_buckets()['Buckets']))" 2>nul && echo S3 connection: OK || echo S3 connection: SKIP

echo.
echo Setup complete! To use these credentials:
echo   1. Run: call infrastructure\set_env.bat
echo   2. Start Setup Portal: python -m streamlit run portals\setup\setup_portal.py --server.port 8512
echo   3. Access Portal: http://localhost:8512
echo.
echo For automatic setup (recommended):
echo   python -c "from infrastructure.yaml_loader import setup_environment_from_settings; setup_environment_from_settings()"
