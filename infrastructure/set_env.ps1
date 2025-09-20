# QA-Shipping Environment Setup - PowerShell
# Generated automatically from settings.yaml on 2025-09-20 06:24:02

Write-Host "Setting QA-Shipping environment variables..." -ForegroundColor Green

# Database credentials
$env:DB_HOST = "vectorqa-cluster.cluster-cu562e4m02nq.us-east-1.rds.amazonaws.com"
$env:DB_PORT = "5432"
$env:DB_NAME = "vectorqa"
$env:DB_USERNAME = "vectorqa_user"
$env:DB_PASSWORD = "***REMOVED***"

# AWS credentials
$env:AWS_ACCESS_KEY_ID = "***REMOVED***"
$env:AWS_SECRET_ACCESS_KEY = "***REMOVED***"
$env:AWS_DEFAULT_REGION = "us-east-1"

# MLflow settings
$env:MLFLOW_TRACKING_URI = "http://localhost:5000"

# S3 settings
$env:S3_BUCKET = "nsc-mvp1"
$env:S3_PREFIX = "staging/"

Write-Host "Environment variables set for current session" -ForegroundColor Yellow
Write-Host "Database: $env:DB_HOST"
Write-Host "AWS Region: $env:AWS_DEFAULT_REGION"
Write-Host "MLflow: $env:MLFLOW_TRACKING_URI"

Write-Host ""
Write-Host "Testing infrastructure connectivity..." -ForegroundColor Cyan

# Test environment loading
try {
    python -c "from infrastructure.environment_manager import get_environment_manager; env_mgr = get_environment_manager(); summary = env_mgr.get_environment_summary(); print('System Status:', 'OK' if all(summary['validation_results'].values()) else 'ISSUES')"
    Write-Host "System validation: OK" -ForegroundColor Green
} catch {
    Write-Host "System validation: FAIL" -ForegroundColor Red
}

Write-Host ""
Write-Host "Setup complete! To use these credentials:" -ForegroundColor Green
Write-Host "  1. Run: .\infrastructure\set_env.ps1"
Write-Host "  2. Start Setup Portal: python -m streamlit run portals\setup\setup_portal.py --server.port 8512"
Write-Host "  3. Access Portal: http://localhost:8512"
Write-Host ""
Write-Host "For automatic setup (recommended):" -ForegroundColor Yellow
Write-Host '  python -c "from infrastructure.yaml_loader import setup_environment_from_settings; setup_environment_from_settings()"'
