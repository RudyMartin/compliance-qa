"""
Script Generator - Infrastructure Utility

Generates environment setup scripts from settings.yaml configuration.
Creates platform-specific scripts for easy credential setup.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from .settings_loader import get_settings_loader

logger = logging.getLogger(__name__)

class ScriptGenerator:
    """Generates environment setup scripts from configuration."""

    def __init__(self):
        self.settings_loader = get_settings_loader()
        self.output_dir = Path(__file__).parent

    def generate_windows_script(self, output_path: str = None) -> str:
        """Generate Windows batch script for environment setup."""
        if output_path is None:
            output_path = self.output_dir / "set_env.bat"

        config = self.settings_loader.load_config()

        script_content = f"""@echo off
REM QA-Shipping Environment Setup - Windows
REM Generated automatically from settings.yaml on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
REM Sets all credentials for current session

echo Setting QA-Shipping environment variables...

REM Database credentials
set DB_HOST={config.db_host}
set DB_PORT={config.db_port}
set DB_NAME={config.db_name}
set DB_USERNAME={config.db_username}
set DB_PASSWORD={config.db_password}

REM AWS credentials
set AWS_ACCESS_KEY_ID={config.aws_access_key_id}
set AWS_SECRET_ACCESS_KEY={config.aws_secret_access_key}
set AWS_DEFAULT_REGION={config.aws_region}

REM MLflow settings
set MLFLOW_TRACKING_URI={config.mlflow_tracking_uri}

REM S3 settings
set S3_BUCKET={config.s3_bucket}
set S3_PREFIX={config.s3_prefix}

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
python -c "from infrastructure.settings_loader import get_settings_loader; loader = get_settings_loader(); summary = loader.get_settings_summary(); print('Settings loaded from:', summary['source_file'])" 2>nul && echo Settings loader: OK || echo Settings loader: FAIL

REM Test database connection
python -c "from infrastructure.credential_validator import quick_health_check; import asyncio; loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop); healthy = loop.run_until_complete(quick_health_check()); print('Database connection:', 'OK' if healthy else 'FAIL')" 2>nul || echo Database test: Could not run

REM Test AWS S3 (if session manager available)
python -c "from adapters.session.unified_session_manager import UnifiedSessionManager; sm = UnifiedSessionManager(); client = sm.get_s3_client(); print('S3 buckets:', len(client.list_buckets()['Buckets']))" 2>nul && echo S3 connection: OK || echo S3 connection: SKIP

echo.
echo Setup complete! To use these credentials:
echo   1. Run: call infrastructure\\set_env.bat
echo   2. Start Setup Portal: python -m streamlit run portals\\setup\\setup_portal.py --server.port 8512
echo   3. Access Portal: http://localhost:8512
echo.
echo For automatic setup (recommended):
echo   python -c "from infrastructure.settings_loader import setup_environment_from_settings; setup_environment_from_settings()"
"""

        with open(output_path, 'w') as f:
            f.write(script_content)

        logger.info(f"Windows script generated: {output_path}")
        return str(output_path)

    def generate_unix_script(self, output_path: str = None) -> str:
        """Generate Unix shell script for environment setup."""
        if output_path is None:
            output_path = self.output_dir / "set_env.sh"

        config = self.settings_loader.load_config()

        script_content = f"""#!/bin/bash
# QA-Shipping Environment Setup - Linux/Mac
# Generated automatically from settings.yaml on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Sets all credentials for current session

echo "Setting QA-Shipping environment variables..."

# Database credentials
export DB_HOST={config.db_host}
export DB_PORT={config.db_port}
export DB_NAME={config.db_name}
export DB_USERNAME={config.db_username}
export DB_PASSWORD={config.db_password}

# AWS credentials
export AWS_ACCESS_KEY_ID={config.aws_access_key_id}
export AWS_SECRET_ACCESS_KEY={config.aws_secret_access_key}
export AWS_DEFAULT_REGION={config.aws_region}

# MLflow settings
export MLFLOW_TRACKING_URI={config.mlflow_tracking_uri}

# S3 settings
export S3_BUCKET={config.s3_bucket}
export S3_PREFIX={config.s3_prefix}

echo "Environment variables set for current session"
echo "Database: $DB_HOST"
echo "AWS Region: $AWS_DEFAULT_REGION"
echo "MLflow: $MLFLOW_TRACKING_URI"

# Test infrastructure connectivity
echo ""
echo "Testing infrastructure connectivity..."

# Test environment loading
python3 -c "from infrastructure.environment_manager import get_environment_manager; env_mgr = get_environment_manager(); summary = env_mgr.get_environment_summary(); print('System Status:', 'OK' if all(summary['validation_results'].values()) else 'ISSUES')" 2>/dev/null && echo "System validation: OK" || echo "System validation: FAIL"

# Test settings loader
python3 -c "from infrastructure.settings_loader import get_settings_loader; loader = get_settings_loader(); summary = loader.get_settings_summary(); print('Settings loaded from:', summary['source_file'])" 2>/dev/null && echo "Settings loader: OK" || echo "Settings loader: FAIL"

# Test database connection
python3 -c "from infrastructure.credential_validator import quick_health_check; import asyncio; loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop); healthy = loop.run_until_complete(quick_health_check()); print('Database connection:', 'OK' if healthy else 'FAIL')" 2>/dev/null || echo "Database test: Could not run"

# Test AWS S3 (if session manager available)
python3 -c "from adapters.session.unified_session_manager import UnifiedSessionManager; sm = UnifiedSessionManager(); client = sm.get_s3_client(); print('S3 buckets:', len(client.list_buckets()['Buckets']))" 2>/dev/null && echo "S3 connection: OK" || echo "S3 connection: SKIP"

echo ""
echo "Setup complete! To use these credentials:"
echo "  1. Run: source infrastructure/set_env.sh"
echo "  2. Start Setup Portal: python -m streamlit run portals/setup/setup_portal.py --server.port 8512"
echo "  3. Access Portal: http://localhost:8512"
echo ""
echo "For automatic setup (recommended):"
echo "  python -c \\"from infrastructure.settings_loader import setup_environment_from_settings; setup_environment_from_settings()\\""
"""

        with open(output_path, 'w') as f:
            f.write(script_content)

        # Make executable
        os.chmod(output_path, 0o755)

        logger.info(f"Unix script generated: {output_path}")
        return str(output_path)

    def generate_docker_env(self, output_path: str = None) -> str:
        """Generate Docker environment file."""
        if output_path is None:
            output_path = self.output_dir / ".env"

        config = self.settings_loader.load_config()

        env_content = f"""# QA-Shipping Docker Environment
# Generated automatically from settings.yaml on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Database Configuration
DB_HOST={config.db_host}
DB_PORT={config.db_port}
DB_NAME={config.db_name}
DB_USERNAME={config.db_username}
DB_PASSWORD={config.db_password}

# AWS Configuration
AWS_ACCESS_KEY_ID={config.aws_access_key_id}
AWS_SECRET_ACCESS_KEY={config.aws_secret_access_key}
AWS_DEFAULT_REGION={config.aws_region}

# MLflow Configuration
MLFLOW_TRACKING_URI={config.mlflow_tracking_uri}

# S3 Configuration
S3_BUCKET={config.s3_bucket}
S3_PREFIX={config.s3_prefix}

# QA-Shipping Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
"""

        with open(output_path, 'w') as f:
            f.write(env_content)

        logger.info(f"Docker env file generated: {output_path}")
        return str(output_path)

    def generate_powershell_script(self, output_path: str = None) -> str:
        """Generate PowerShell script for Windows environments."""
        if output_path is None:
            output_path = self.output_dir / "set_env.ps1"

        config = self.settings_loader.load_config()

        script_content = f"""# QA-Shipping Environment Setup - PowerShell
# Generated automatically from settings.yaml on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Write-Host "Setting QA-Shipping environment variables..." -ForegroundColor Green

# Database credentials
$env:DB_HOST = "{config.db_host}"
$env:DB_PORT = "{config.db_port}"
$env:DB_NAME = "{config.db_name}"
$env:DB_USERNAME = "{config.db_username}"
$env:DB_PASSWORD = "{config.db_password}"

# AWS credentials
$env:AWS_ACCESS_KEY_ID = "{config.aws_access_key_id}"
$env:AWS_SECRET_ACCESS_KEY = "{config.aws_secret_access_key}"
$env:AWS_DEFAULT_REGION = "{config.aws_region}"

# MLflow settings
$env:MLFLOW_TRACKING_URI = "{config.mlflow_tracking_uri}"

# S3 settings
$env:S3_BUCKET = "{config.s3_bucket}"
$env:S3_PREFIX = "{config.s3_prefix}"

Write-Host "Environment variables set for current session" -ForegroundColor Yellow
Write-Host "Database: $env:DB_HOST"
Write-Host "AWS Region: $env:AWS_DEFAULT_REGION"
Write-Host "MLflow: $env:MLFLOW_TRACKING_URI"

Write-Host ""
Write-Host "Testing infrastructure connectivity..." -ForegroundColor Cyan

# Test environment loading
try {{
    python -c "from infrastructure.environment_manager import get_environment_manager; env_mgr = get_environment_manager(); summary = env_mgr.get_environment_summary(); print('System Status:', 'OK' if all(summary['validation_results'].values()) else 'ISSUES')"
    Write-Host "System validation: OK" -ForegroundColor Green
}} catch {{
    Write-Host "System validation: FAIL" -ForegroundColor Red
}}

Write-Host ""
Write-Host "Setup complete! To use these credentials:" -ForegroundColor Green
Write-Host "  1. Run: .\\infrastructure\\set_env.ps1"
Write-Host "  2. Start Setup Portal: python -m streamlit run portals\\setup\\setup_portal.py --server.port 8512"
Write-Host "  3. Access Portal: http://localhost:8512"
Write-Host ""
Write-Host "For automatic setup (recommended):" -ForegroundColor Yellow
Write-Host '  python -c "from infrastructure.settings_loader import setup_environment_from_settings; setup_environment_from_settings()"'
"""

        with open(output_path, 'w') as f:
            f.write(script_content)

        logger.info(f"PowerShell script generated: {output_path}")
        return str(output_path)

    def generate_all_scripts(self) -> Dict[str, str]:
        """Generate all environment setup scripts."""
        generated_files = {}

        try:
            generated_files['windows_bat'] = self.generate_windows_script()
            generated_files['unix_sh'] = self.generate_unix_script()
            generated_files['powershell'] = self.generate_powershell_script()
            generated_files['docker_env'] = self.generate_docker_env()

            logger.info(f"Generated {len(generated_files)} script files")
            return generated_files

        except Exception as e:
            logger.error(f"Error generating scripts: {e}")
            raise

    def validate_generated_scripts(self) -> Dict[str, bool]:
        """Validate that generated scripts exist and are readable."""
        scripts = {
            'set_env.bat': self.output_dir / "set_env.bat",
            'set_env.sh': self.output_dir / "set_env.sh",
            'set_env.ps1': self.output_dir / "set_env.ps1",
            '.env': self.output_dir / ".env"
        }

        validation_results = {}
        for name, path in scripts.items():
            validation_results[name] = path.exists() and path.is_file()

        return validation_results

    def get_script_info(self) -> Dict[str, Any]:
        """Get information about generated scripts."""
        config = self.settings_loader.load_config()

        return {
            'source_settings': self.settings_loader.settings_path,
            'output_directory': str(self.output_dir),
            'environment_type': self.settings_loader.get_environment_type(),
            'database_host': config.db_host,
            'aws_region': config.aws_region,
            'mlflow_uri': config.mlflow_tracking_uri,
            'generated_scripts': self.validate_generated_scripts(),
            'generation_time': datetime.now().isoformat()
        }


# Global script generator instance
_script_generator = None

def get_script_generator() -> ScriptGenerator:
    """Get global script generator instance."""
    global _script_generator
    if _script_generator is None:
        _script_generator = ScriptGenerator()
    return _script_generator

def generate_all_setup_scripts() -> Dict[str, str]:
    """Generate all environment setup scripts."""
    return get_script_generator().generate_all_scripts()

def regenerate_scripts_from_settings():
    """Regenerate all scripts from current settings.yaml."""
    generator = get_script_generator()
    generated = generator.generate_all_scripts()

    print("Environment setup scripts generated:")
    for script_type, path in generated.items():
        print(f"  {script_type}: {path}")

    return generated


if __name__ == "__main__":
    # Demo the script generator
    print("QA-Shipping Script Generator Demo")
    print("=" * 40)

    try:
        generator = ScriptGenerator()

        print("Generating environment setup scripts...")
        generated = generator.generate_all_scripts()

        print(f"Generated {len(generated)} scripts:")
        for script_type, path in generated.items():
            print(f"  {script_type}: {path}")

        print("\nScript validation:")
        validation = generator.validate_generated_scripts()
        for script, valid in validation.items():
            status = "✓" if valid else "✗"
            print(f"  {status} {script}")

        print("\nScript info:")
        info = generator.get_script_info()
        print(f"  Source: {info['source_settings']}")
        print(f"  Environment: {info['environment_type']}")
        print(f"  Database: {info['database_host']}")
        print(f"  AWS Region: {info['aws_region']}")

    except Exception as e:
        print(f"Error: {e}")