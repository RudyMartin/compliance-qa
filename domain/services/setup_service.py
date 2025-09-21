#!/usr/bin/env python3
"""
Setup Service
=============
Core business logic for system setup and configuration management.
This service uses dependency injection to comply with hexagonal architecture.
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import asyncio
import os
import socket
import subprocess
import sys
import json

from domain.ports.outbound.setup_dependencies_port import SetupDependenciesPort


class SetupService:
    """Service for managing system setup and configuration."""

    def __init__(self, root_path: Path, dependencies: Optional[SetupDependenciesPort] = None):
        """
        Initialize with root path and optional dependencies.

        Args:
            root_path: Root path of the project
            dependencies: Port for accessing infrastructure services (dependency injection)
        """
        self.root_path = root_path
        self._environment_cache = {}
        self._deps = dependencies

        # If no dependencies provided, get default adapter
        # This maintains backward compatibility while allowing testing
        if self._deps is None:
            from adapters.secondary.setup.setup_dependencies_adapter import get_setup_dependencies_adapter
            self._deps = get_setup_dependencies_adapter()

    def get_architecture_info(self) -> Dict[str, str]:
        """Get architecture information from settings."""
        try:
            config = self._deps.get_configuration_service().load_config()

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
                'description': 'External Presentation Layer - 4-Layer Clean Architecture (Default)'
            }

    def get_environment_details(self) -> Dict[str, Any]:
        """Get environment details from environment manager."""
        try:
            env_service = self._deps.get_environment_service()
            return env_service.get_variables()
        except Exception as e:
            return {'error': str(e)}

    def get_python_status(self) -> Dict[str, Any]:
        """Check Python installation status."""
        return {
            'installed': True,
            'version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'executable': sys.executable,
            'venv': hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix),
            'site_packages': [p for p in sys.path if 'site-packages' in p]
        }

    def get_nodejs_status(self) -> Dict[str, Any]:
        """Check Node.js and npm installation status."""
        try:
            node_version = subprocess.check_output(['node', '--version'], text=True).strip()
            npm_version = subprocess.check_output(['npm', '--version'], text=True).strip()
            return {
                'installed': True,
                'node_version': node_version,
                'npm_version': npm_version
            }
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {'installed': False}

    async def validate_all_credentials(self) -> Dict[str, Any]:
        """Validate all configured credentials."""
        try:
            cred_service = self._deps.get_credential_service()
            return cred_service.validate_all_credentials()
        except Exception as e:
            return {'error': str(e), 'status': 'failed'}

    async def quick_health_check(self) -> Dict[str, bool]:
        """Quick health check of all systems."""
        try:
            cred_service = self._deps.get_credential_service()
            return cred_service.quick_health_check()
        except Exception as e:
            return {'error': str(e)}

    def get_portal_summary(self) -> Dict[str, Any]:
        """Get portal configuration summary."""
        try:
            portal_service = self._deps.get_portal_config_service()
            return portal_service.get_portal_summary()
        except Exception as e:
            return {
                'available_portals': [],
                'count': 0,
                'summary': 'Unable to load portal configuration',
                'error': str(e)
            }

    def check_network_connectivity(self) -> Dict[str, bool]:
        """Check network connectivity to various endpoints."""
        results = {}
        test_hosts = [
            ('google.com', 80, 'Internet'),
            ('github.com', 443, 'GitHub'),
            ('pypi.org', 443, 'PyPI'),
            ('registry.npmjs.org', 443, 'NPM Registry')
        ]

        for host, port, name in test_hosts:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host, port))
                results[name] = result == 0
                sock.close()
            except Exception:
                results[name] = False

        return results

    def get_system_resources(self) -> Dict[str, Any]:
        """Get system resource information."""
        import psutil

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(str(self.root_path))

            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count()
                },
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'percent': memory.percent
                },
                'disk': {
                    'total_gb': round(disk.total / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2),
                    'percent': disk.percent
                }
            }
        except ImportError:
            return {'error': 'psutil not installed'}

    def get_package_status(self) -> List[Dict[str, Any]]:
        """Check status of local packages."""
        try:
            package_service = self._deps.get_package_installer_service()
            return package_service.check_local_packages()
        except Exception as e:
            return [{'error': str(e)}]

    def install_local_packages(self) -> Dict[str, Any]:
        """Install local packages."""
        try:
            package_service = self._deps.get_package_installer_service()
            return package_service.install_local_packages()
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def run_package_tests(self, package_name: str, test_type: str = 'unit') -> Dict[str, Any]:
        """Run tests for a specific package."""
        try:
            package_service = self._deps.get_package_installer_service()
            return package_service.run_tests(package_name, test_type)
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def setup_environment(self) -> Dict[str, Any]:
        """Setup environment variables from settings."""
        try:
            config_service = self._deps.get_configuration_service()
            return config_service.setup_environment_from_settings()
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def generate_startup_script(self, script_type: str = 'bash') -> Dict[str, Any]:
        """Generate startup script for the system."""
        try:
            script_service = self._deps.get_script_generator_service()

            # Generate appropriate script based on type
            if script_type == 'powershell':
                script_path = script_service.generate_service_script('powershell', root_path=self.root_path)
            else:
                script_path = script_service.generate_startup_script(root_path=self.root_path)

            return {
                'success': True,
                'script_path': str(script_path),
                'script_type': script_type
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_available_operations(self) -> List[str]:
        """Get list of available setup operations."""
        return [
            'check_environment',
            'validate_credentials',
            'install_packages',
            'run_tests',
            'generate_scripts',
            'setup_environment'
        ]

    def sync_credential_state(self, status: str) -> None:
        """Sync credential state across the system."""
        try:
            cred_service = self._deps.get_credential_service()
            cred_service.sync_active_credential_state(status)
        except Exception as e:
            # Log error but don't raise
            print(f"Error syncing credential state: {e}")

    def get_aws_configuration(self) -> Dict[str, Any]:
        """Get AWS configuration status."""
        try:
            aws_service = self._deps.get_aws_service()
            config_service = self._deps.get_configuration_service()

            # Get Bedrock config from settings
            bedrock_config = config_service.get_bedrock_config()

            return {
                'aws_available': aws_service.is_available(),
                'bedrock_configured': bool(bedrock_config.get('default_model')),
                'region': bedrock_config.get('region', 'us-east-1'),
                'has_credentials': aws_service.is_available()
            }
        except Exception as e:
            return {'error': str(e), 'aws_available': False}

    def check_environment_status(self) -> Dict[str, bool]:
        """Comprehensive environment status check."""
        results = {}

        try:
            # Check AWS credentials
            aws_service = self._deps.get_aws_service()
            config_service = self._deps.get_configuration_service()
            bedrock_config = config_service.get_bedrock_config()

            # Check multiple sources for AWS credentials
            has_credentials = bool(
                bedrock_config.get('access_key_id') or
                os.getenv('AWS_ACCESS_KEY_ID') or
                (Path.home() / '.aws' / 'credentials').exists()
            )

            # Then verify AWS service can initialize
            if has_credentials:
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

        return results

    def check_tidyllm_components(self) -> Dict[str, Any]:
        """Check TidyLLM component configuration."""
        results = {
            'corporate_llm_gateway': False,
            'unified_rag_facade': False,
            'rag_orchestration': False,
            'basic_chat_settings': False,
            'bedrock_models_configured': False,
            'default_timeouts_set': False,
        }

        try:
            config_service = self._deps.get_configuration_service()

            # Check Bedrock configuration
            bedrock_config = config_service.get_bedrock_config()
            results['bedrock_models_configured'] = bool(bedrock_config.get('model_mapping'))
            results['basic_chat_settings'] = bool(bedrock_config.get('default_model'))
            results['default_timeouts_set'] = bool(bedrock_config.get('timeout'))

            # Check MLflow configuration
            mlflow_config = config_service.get_mlflow_config()
            results['mlflow_configured'] = bool(mlflow_config.get('tracking_uri'))

            # Check gateway availability
            results['corporate_llm_gateway'] = results['bedrock_models_configured']

            return {
                'results': results,
                'summary': f"{sum(1 for v in results.values() if v is True)}/{len(results)} TidyLLM components configured",
                'model_count': len(bedrock_config.get('model_mapping', {}))
            }
        except Exception as e:
            return {'error': str(e), 'results': results}

    def check_functional_tests(self) -> Dict[str, bool]:
        """Check functional test components."""
        results = {
            'aws_service_connectivity': False,
            'mlflow_tracking_status': False,
            'bedrock_model_accessibility': False,
            'basic_chat_functionality': False
        }

        try:
            # Check AWS connectivity
            aws_service = self._deps.get_aws_service()
            results['aws_service_connectivity'] = aws_service.is_available()

            # Check Bedrock models
            config_service = self._deps.get_configuration_service()
            bedrock_config = config_service.get_bedrock_config()
            results['bedrock_model_accessibility'] = bool(bedrock_config.get('model_mapping'))

            # Check basic chat
            results['basic_chat_functionality'] = (
                results['aws_service_connectivity'] and
                results['bedrock_model_accessibility']
            )

            return results
        except Exception as e:
            return {'error': str(e), **results}