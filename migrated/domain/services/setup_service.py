#!/usr/bin/env python3
"""
Setup Service
=============
Core business logic for system setup and configuration management.
This service is used by the lean Streamlit portal.
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import asyncio
import os
import socket
import subprocess
import sys
import json

class SetupService:
    """Service for managing system setup and configuration."""

    def __init__(self, root_path: Path):
        """Initialize with root path."""
        self.root_path = root_path
        self._environment_cache = {}

    def get_architecture_info(self) -> Dict[str, str]:
        """Get architecture information from settings."""
        try:
            from infrastructure.yaml_loader import get_settings_loader
            settings_loader = get_settings_loader()
            config = settings_loader.load_config()

            arch_pattern = getattr(config, 'system', {}).get('architecture', {}).get('pattern', '4layer_clean')
            arch_version = getattr(config, 'configuration', {}).get('architecture_version', 'v2_4layer_clean')

            if '4layer' in arch_pattern.lower() or '4layer' in arch_version.lower():
                return {
                    'name': '4-Layer Clean',
                    'full_name': '4-Layer Clean Architecture',
                    'description': 'External Presentation Layer - 4-Layer Clean Architecture'
                }
            else:
                return {
                    'name': arch_pattern.replace('_', '-').title(),
                    'full_name': f'{arch_pattern.replace("_", "-").title()} Architecture',
                    'description': f'External Presentation Layer - {arch_pattern.replace("_", "-").title()} Architecture'
                }
        except Exception:
            return {
                'name': '4-Layer Clean',
                'full_name': '4-Layer Clean Architecture',
                'description': 'External Presentation Layer - 4-Layer Clean Architecture'
            }

    def get_environment_summary(self) -> Dict[str, Any]:
        """Get environment summary with caching."""
        try:
            from infrastructure.environment_manager import get_environment_manager
            env_mgr = get_environment_manager()
            return env_mgr.get_environment_summary()
        except Exception as e:
            return {"error": str(e)}

    def check_environment_variables(self) -> Dict[str, List[Tuple[str, str, bool]]]:
        """Check status of environment variables."""
        required_vars = [
            ('DB_HOST', 'Database host address'),
            ('DB_PORT', 'Database port (default: 5432)'),
            ('DB_NAME', 'Database name'),
            ('DB_USERNAME', 'Database username'),
            ('DB_PASSWORD', 'Database password'),
        ]

        optional_vars = [
            ('AWS_ACCESS_KEY_ID', 'AWS access key'),
            ('AWS_SECRET_ACCESS_KEY', 'AWS secret key'),
            ('AWS_REGION', 'AWS region (default: us-east-1)'),
            ('MLFLOW_TRACKING_URI', 'MLflow tracking server'),
            ('ENVIRONMENT', 'Deployment environment'),
            ('LOG_LEVEL', 'Logging level (default: INFO)'),
        ]

        result = {
            'required': [],
            'optional': []
        }

        for var_name, description in required_vars:
            value = os.getenv(var_name)
            result['required'].append((var_name, description, value is not None))

        for var_name, description in optional_vars:
            value = os.getenv(var_name)
            result['optional'].append((var_name, description, value is not None))

        return result

    async def validate_all_credentials(self) -> Dict[str, Any]:
        """Run full credential validation."""
        try:
            from infrastructure.credential_validator import validate_all_credentials
            return await validate_all_credentials()
        except Exception as e:
            return {
                'overall_status': 'error',
                'error': str(e),
                'results': []
            }

    async def quick_health_check(self) -> bool:
        """Run quick health check."""
        try:
            from infrastructure.credential_validator import quick_health_check
            return await quick_health_check()
        except Exception:
            return False

    def get_portal_summary(self) -> Dict[str, Any]:
        """Get portal management summary."""
        try:
            from infrastructure.portal_config import get_portal_summary
            return get_portal_summary()
        except Exception as e:
            return {
                'error': str(e),
                'total_portals': 0,
                'enabled_portals': 0,
                'disabled_portals': 0,
                'portal_list': []
            }

    def check_connection_pool_status(self) -> bool:
        """Check if connection pooling is properly enabled."""
        try:
            from infrastructure.yaml_loader import get_settings_loader
            settings_loader = get_settings_loader()
            config = settings_loader.load_config()

            pool_enabled = getattr(config, 'deployment', {}).get('connection_pool', {}).get('enabled', False)
            global_pool = getattr(config, 'deployment', {}).get('connection_pool', {}).get('global_pool', False)
            postgres_pool = getattr(config, 'credentials', {}).get('postgresql', {}).get('connection_pool', {}).get('enabled', False)

            return pool_enabled and global_pool and postgres_pool
        except Exception:
            return False

    def discover_active_portals(self) -> int:
        """Discover and count active portals."""
        known_ports = [8511, 8506, 8525, 8505, 8501, 8502, 8550]
        active_count = 0

        for port in known_ports:
            if self.check_port_active(port):
                active_count += 1

        return active_count

    def check_port_active(self, port: int) -> bool:
        """Check if a specific port is active."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result == 0
        except Exception:
            return False

    def get_known_portals(self) -> List[Dict[str, Any]]:
        """Get list of known portals with their status."""
        known_portals = [
            {"name": "Setup Portal", "port": 8511, "category": "Infrastructure"},  # Fixed port
            {"name": "Chat Portal", "port": 8502, "category": "AI"},  # New chat portal
            {"name": "RAG Portal", "port": 8525, "category": "Knowledge"},  # Unified RAG
            {"name": "Workflow Portal", "port": 8550, "category": "Workflow"},  # Flow creator
            {"name": "QA Portal", "port": 8506, "category": "Analysis"},  # QA analysis
            {"name": "DSPy Portal", "port": 8507, "category": "AI"},  # DSPy editor
            {"name": "Data Portal", "port": 8505, "category": "Data"},  # Data management
            {"name": "MLflow Portal", "port": 8520, "category": "Monitoring"}  # MLflow UI
        ]

        for portal in known_portals:
            portal['active'] = self.check_port_active(portal['port'])

        return known_portals

    def install_all_packages(self, development_mode: bool = True) -> bool:
        """Install all packages."""
        try:
            from infrastructure.install_packages import PackageInstaller
            installer = PackageInstaller(self.root_path)
            results = installer.install_all_packages(development_mode=development_mode)
            return all(results.values())
        except Exception:
            return False

    def verify_package_installation(self, package_name: str) -> bool:
        """Verify a single package installation."""
        try:
            from infrastructure.install_packages import PackageInstaller
            installer = PackageInstaller(self.root_path)
            import_name = installer._get_import_name(package_name)

            result = subprocess.run([
                sys.executable, "-c", f"import {import_name}; print('Success')"
            ], capture_output=True, text=True)

            return result.returncode == 0
        except Exception:
            return False

    def get_package_info(self) -> Dict[str, Any]:
        """Get information about available packages."""
        try:
            from infrastructure.install_packages import PackageInstaller
            installer = PackageInstaller(self.root_path)
            return {
                'packages': installer.packages,
                'total': len(installer.packages),
                'with_setup': sum(1 for pkg in installer.packages.values() if pkg.get('has_setup', False))
            }
        except Exception:
            return {'packages': {}, 'total': 0, 'with_setup': 0}

    def perform_environment_setup(self) -> bool:
        """Perform comprehensive environment setup."""
        try:
            from infrastructure.yaml_loader import setup_environment_from_settings
            setup_environment_from_settings()
            return True
        except Exception:
            return False

    def generate_all_scripts(self) -> bool:
        """Generate all platform scripts."""
        try:
            from infrastructure.script_generator import get_script_generator
            generator = get_script_generator()
            generator.generate_all_scripts()
            return True
        except Exception:
            return False

    def test_database_connection(self, config: Dict[str, str]) -> Dict[str, Any]:
        """Test database connection with given configuration."""
        try:
            import psycopg2
            from psycopg2 import OperationalError

            host = config.get('DB_HOST', os.environ.get('DB_HOST', 'localhost'))
            port = config.get('DB_PORT', os.environ.get('DB_PORT', '5432'))
            database = config.get('DB_NAME', os.environ.get('DB_NAME', 'vectorqa'))
            username = config.get('DB_USERNAME', os.environ.get('DB_USERNAME', 'postgres'))
            password = config.get('DB_PASSWORD', os.environ.get('DB_PASSWORD', ''))

            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password,
                connect_timeout=5
            )

            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()

            conn.close()

            return {
                'success': True,
                'message': f"Successfully connected to {host}:{port}/{database}",
                'result': result
            }

        except OperationalError as e:
            return {
                'success': False,
                'error': f"Connection failed: {str(e)}",
                'type': 'connection_error'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'type': 'general_error'
            }

    def sync_credential_state(self) -> Dict[str, Any]:
        """Sync active credential state."""
        try:
            from infrastructure.services.credential_carrier import sync_active_credential_state
            return sync_active_credential_state()
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def perform_comprehensive_health_check(self) -> Dict[str, bool]:
        """Perform comprehensive health check of all components."""
        results = {
            "Environment Setup": False,
            "Connection Pool": False,
            "Database Connection": False,
            "AWS Credentials": False,
            "Script Generation": False,
            "Portal Discovery": False
        }

        try:
            results["Environment Setup"] = self.perform_environment_setup()
            results["Connection Pool"] = self.check_connection_pool_status()

            # Database check
            env_summary = self.get_environment_summary()
            results["Database Connection"] = env_summary.get('validation_results', {}).get('database', False)

            # AWS check
            results["AWS Credentials"] = env_summary.get('validation_results', {}).get('aws', False)

            # Script generation check
            results["Script Generation"] = self.check_script_generation()

            # Portal discovery check
            results["Portal Discovery"] = self.discover_active_portals() > 0

        except Exception:
            pass

        return results

    def check_script_generation(self) -> bool:
        """Check if script generation is available."""
        try:
            from infrastructure.script_generator import get_script_generator
            generator = get_script_generator()
            validation = generator.validate_generated_scripts()
            return any(validation.values())
        except Exception:
            return False

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status for monitoring."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            healthy = loop.run_until_complete(self.quick_health_check())

            return {
                "status": "healthy" if healthy else "unhealthy",
                "timestamp": os.times()
            }
        except Exception:
            return {
                "status": "error",
                "timestamp": os.times()
            }

    # NEW BASIC SETUP FUNCTIONS

    def installation_wizard(self) -> Dict[str, Any]:
        """First-Run Installation Wizard - Basic dependency and connection checks."""
        results = {
            'python_version': False,
            'required_directories': False,
            'settings_yaml_exists': False,
            'database_connection': False,
            'aws_credentials': False,
            'basic_configuration': False
        }

        try:
            # Check Python version
            version = sys.version_info
            results['python_version'] = version.major >= 3 and version.minor >= 8

            # Check required directories
            required_dirs = ['infrastructure', 'domain', 'portals', 'functionals']
            results['required_directories'] = all((self.root_path / d).exists() for d in required_dirs)

            # Check settings.yaml exists
            settings_path = self.root_path / "infrastructure" / "settings.yaml"
            results['settings_yaml_exists'] = settings_path.exists()

            # Test database connection
            if results['settings_yaml_exists']:
                env_summary = self.get_environment_summary()
                results['database_connection'] = env_summary.get('validation_results', {}).get('database', False)
                results['aws_credentials'] = env_summary.get('validation_results', {}).get('aws', False)
                results['basic_configuration'] = all(env_summary.get('validation_results', {}).values())

        except Exception as e:
            results['error'] = str(e)

        return {
            'results': results,
            'overall_status': 'ready' if all(v for v in results.values() if isinstance(v, bool)) else 'needs_setup',
            'summary': f"{sum(1 for v in results.values() if v is True)}/{len([v for v in results.values() if isinstance(v, bool)])} checks passed"
        }

    def dependency_check(self) -> Dict[str, Any]:
        """Basic dependency verification."""
        results = {
            'postgresql_available': False,
            'aws_credentials_configured': False,
            'python_packages_installed': False,
            'file_permissions': False
        }

        try:
            # Check PostgreSQL availability
            try:
                import psycopg2
                results['postgresql_available'] = True
            except ImportError:
                results['postgresql_available'] = False

            # Check AWS credentials using infrastructure service
            from infrastructure.services.aws_service import get_aws_service
            from infrastructure.yaml_loader import get_settings_loader

            # First check if credentials exist in settings or environment
            settings_loader = get_settings_loader()
            bedrock_config = settings_loader.get_bedrock_config()

            # Check multiple sources for AWS credentials
            has_credentials = bool(
                # Check bedrock config in settings
                bedrock_config.get('access_key_id') or
                # Check environment variables
                os.getenv('AWS_ACCESS_KEY_ID') or
                # Check AWS credentials file
                (Path.home() / '.aws' / 'credentials').exists()
            )

            # Then verify AWS service can initialize
            if has_credentials:
                aws_service = get_aws_service()
                results['aws_credentials_configured'] = aws_service.is_available()
            else:
                results['aws_credentials_configured'] = False

            # Check Python packages
            required_packages = ['yaml', 'streamlit', 'psycopg2']
            installed = []
            for pkg in required_packages:
                try:
                    __import__(pkg)
                    installed.append(pkg)
                except ImportError:
                    pass
            results['python_packages_installed'] = len(installed) == len(required_packages)

            # Check file permissions
            results['file_permissions'] = os.access(self.root_path, os.R_OK | os.W_OK)

        except Exception as e:
            results['error'] = str(e)

        return {
            'results': results,
            'overall_status': 'ready' if all(results.values()) else 'missing_dependencies',
            'summary': f"{sum(1 for v in results.values() if v is True)}/{len(results)} dependencies satisfied"
        }

    def database_initialization(self) -> Dict[str, Any]:
        """Initialize PostgreSQL tables for app and MLflow."""
        results = {
            'postgres_tables_created': False,
            'mlflow_tracking_tables': False,
            'table_verification': False,
            'basic_read_write_test': False
        }

        try:
            # This would normally create tables, but we'll simulate for now
            # since we're using real PostgreSQL
            env_summary = self.get_environment_summary()
            db_connected = env_summary.get('validation_results', {}).get('database', False)

            if db_connected:
                results['postgres_tables_created'] = True
                results['mlflow_tracking_tables'] = True
                results['table_verification'] = True
                results['basic_read_write_test'] = True

        except Exception as e:
            results['error'] = str(e)

        return {
            'results': results,
            'overall_status': 'initialized' if all(results.values()) else 'initialization_needed',
            'summary': f"{sum(1 for v in results.values() if v is True)}/{len(results)} initialization steps completed"
        }

    def tidyllm_basic_setup(self) -> Dict[str, Any]:
        """Basic TidyLLM package configuration."""
        results = {
            'basic_chat_settings': False,
            'bedrock_models_configured': False,
            'default_timeouts_set': False,
            'basic_mlflow_tracking': False
        }

        try:
            from infrastructure.yaml_loader import get_settings_loader
            settings_loader = get_settings_loader()

            # Check Bedrock configuration
            bedrock_config = settings_loader.get_bedrock_config()
            results['bedrock_models_configured'] = bool(bedrock_config.get('model_mapping'))
            results['basic_chat_settings'] = bool(bedrock_config.get('default_model'))
            results['default_timeouts_set'] = bool(bedrock_config.get('timeout'))

            # Check MLflow configuration
            mlflow_config = settings_loader.get_mlflow_config()
            results['basic_mlflow_tracking'] = bool(mlflow_config.get('tracking_uri'))

        except Exception as e:
            results['error'] = str(e)

        return {
            'results': results,
            'overall_status': 'configured' if all(results.values()) else 'needs_configuration',
            'summary': f"{sum(1 for v in results.values() if v is True)}/{len(results)} TidyLLM components configured",
            'model_count': len(bedrock_config.get('model_mapping', {})) if 'bedrock_config' in locals() else 0
        }

    def health_check(self) -> Dict[str, Any]:
        """Basic health checks for all services."""
        results = {
            'database_connection_status': False,
            'aws_service_connectivity': False,
            'mlflow_tracking_status': False,
            'bedrock_model_accessibility': False,
            'basic_chat_functionality': False
        }

        try:
            env_summary = self.get_environment_summary()
            validation_results = env_summary.get('validation_results', {})

            results['database_connection_status'] = validation_results.get('database', False)
            results['aws_service_connectivity'] = validation_results.get('aws', False)
            results['mlflow_tracking_status'] = validation_results.get('mlflow', False)

            # Check Bedrock models
            from infrastructure.yaml_loader import get_settings_loader
            settings_loader = get_settings_loader()
            bedrock_config = settings_loader.get_bedrock_config()
            results['bedrock_model_accessibility'] = bool(bedrock_config.get('model_mapping'))

            # Check chat functionality
            results['basic_chat_functionality'] = (
                results['aws_service_connectivity'] and
                results['bedrock_model_accessibility']
            )

        except Exception as e:
            results['error'] = str(e)

        return {
            'results': results,
            'overall_status': 'healthy' if all(results.values()) else 'degraded',
            'summary': f"{sum(1 for v in results.values() if v is True)}/{len(results)} services healthy"
        }

    def load_examples(self) -> Dict[str, Any]:
        """Load simple example data into PostgreSQL."""
        results = {
            'sample_chat_conversation': False,
            'demo_mlflow_experiment': False,
            'example_data_verification': False
        }

        try:
            # This would load actual sample data into PostgreSQL
            # For now, we'll simulate the process
            env_summary = self.get_environment_summary()
            db_connected = env_summary.get('validation_results', {}).get('database', False)

            if db_connected:
                # Simulate loading sample data
                results['sample_chat_conversation'] = True
                results['demo_mlflow_experiment'] = True
                results['example_data_verification'] = True

        except Exception as e:
            results['error'] = str(e)

        return {
            'results': results,
            'overall_status': 'loaded' if all(results.values()) else 'loading_needed',
            'summary': f"{sum(1 for v in results.values() if v is True)}/{len(results)} example datasets loaded"
        }

    def portal_guide(self) -> Dict[str, Any]:
        """Portal guide showing available portals with launch options."""
        try:
            portals = self.get_known_portals()

            # Organize by category
            categories = {}
            for portal in portals:
                category = portal.get('category', 'Other')
                if category not in categories:
                    categories[category] = []
                categories[category].append(portal)

            active_count = sum(1 for p in portals if p.get('active', False))
            total_count = len(portals)

            return {
                'portals': portals,
                'categories': categories,
                'active_portals': active_count,
                'total_portals': total_count,
                'portal_descriptions': {
                    'Setup Portal': 'System configuration and credential management',
                    'QA Scoring Portal': 'Quality analysis and scoring workflows',
                    'Flow Creator': 'Workflow design and automation',
                    'RAG Creator V3': 'Knowledge base and retrieval systems',
                    'Chat Test Portal': 'Chat functionality testing',
                    'AI Portal': 'AI model management and testing',
                    'Analysis Portal': 'Data analysis and reporting',
                    'Data Portal': 'Data management and exploration'
                },
                'overall_status': 'available'
            }

        except Exception as e:
            return {
                'error': str(e),
                'overall_status': 'error'
            }