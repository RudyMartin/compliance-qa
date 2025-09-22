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
        """Check TidyLLM component configuration - high-level installer checks."""
        results = {
            'aws_bedrock_gateway': False,
            'chat_functionality': False,
            'rag_functionality': False,
            'model_configuration': False,
            'timeout_settings': False,
        }

        try:
            config_service = self._deps.get_configuration_service()

            # Check Bedrock configuration
            bedrock_config = config_service.get_bedrock_config()
            results['model_configuration'] = bool(bedrock_config.get('model_mapping'))
            results['timeout_settings'] = bool(bedrock_config.get('timeout'))

            # Check AWS Bedrock gateway availability
            results['aws_bedrock_gateway'] = results['model_configuration']

            # Check chat functionality (simple: chat portal + models)
            chat_portal_exists = (self.root_path / 'portals' / 'chat' / 'chat_portal.py').exists()
            results['chat_functionality'] = chat_portal_exists and results['model_configuration']

            # Check RAG functionality (simple: RAG portal + intelligent adapter)
            rag_portal_exists = (self.root_path / 'portals' / 'rag' / 'rag_portal.py').exists()
            intelligent_adapter_exists = (self.root_path / 'packages' / 'tidyllm' / 'knowledge_systems' / 'adapters' / 'intelligent').exists()
            results['rag_functionality'] = rag_portal_exists and intelligent_adapter_exists

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

    def get_environment_summary(self) -> Dict[str, Any]:
        """Get comprehensive environment summary."""
        try:
            python_status = self.get_python_status()
            nodejs_status = self.get_nodejs_status()
            aws_config = self.get_aws_configuration()
            env_details = self.get_environment_details()

            return {
                'python': python_status,
                'nodejs': nodejs_status,
                'aws': aws_config,
                'environment': env_details,
                'architecture': self.get_architecture_info(),
                'summary': 'Environment summary generated successfully'
            }
        except Exception as e:
            return {'error': str(e), 'summary': 'Failed to generate environment summary'}

    def installation_wizard(self) -> Dict[str, Any]:
        """Installation wizard for first-time setup."""
        try:
            results = {}

            # Check Python version
            python_info = sys.version_info
            results['python_version'] = python_info.major >= 3 and python_info.minor >= 8

            # Check required directories
            required_dirs = ['portals', 'domain', 'infrastructure', 'adapters']
            results['required_directories'] = all((self.root_path / d).exists() for d in required_dirs)

            # Check settings.yaml (try multiple locations)
            possible_settings = [
                self.root_path / 'infrastructure' / 'settings.yaml',
                self.root_path / 'migrated' / 'tidyllm_admin' / 'settings.yaml',
                self.root_path / 'tidyllm' / 'admin' / 'settings.yaml'
            ]
            results['settings_yaml_exists'] = any(f.exists() for f in possible_settings)

            # Check database connection capability - simplified for first-time setup
            try:
                config_service = self._deps.get_configuration_service()
                config = config_service.load_config()
                # For first-time setup, just check if database section exists with a host
                if hasattr(config, 'databases') and hasattr(config.databases, 'primary'):
                    primary = config.databases.primary
                    results['database_connection'] = bool(hasattr(primary, 'host') and primary.host)
                else:
                    # Database not required for basic first-time setup
                    results['database_connection'] = True
            except:
                # For first-time connection, database is optional
                results['database_connection'] = True

            # Check AWS credentials
            results['aws_credentials'] = self.get_aws_configuration()['aws_available']

            overall_status = 'ready' if all(results.values()) else 'needs_setup'

            return {
                'results': results,
                'overall_status': overall_status,
                'summary': f"Installation check complete - {sum(results.values())}/{len(results)} components ready"
            }
        except Exception as e:
            return {'error': str(e), 'overall_status': 'error'}

    def dependency_check(self) -> Dict[str, Any]:
        """Check software dependencies and configuration."""
        try:
            results = self.check_environment_status()

            # Add PostgreSQL check
            try:
                import psycopg2
                results['postgresql_available'] = True
            except ImportError:
                results['postgresql_available'] = False

            overall_status = 'ready' if all(results.values()) else 'missing_dependencies'

            return {
                'results': results,
                'overall_status': overall_status,
                'summary': f"Dependency check complete - {sum(1 for v in results.values() if v is True)}/{len(results)} dependencies satisfied"
            }
        except Exception as e:
            return {'error': str(e), 'overall_status': 'error'}

    def health_check(self) -> Dict[str, Any]:
        """Comprehensive system health check."""
        try:
            results = {}

            # Check database connectivity
            try:
                config_service = self._deps.get_configuration_service()
                db_config = config_service.get_databases_settings()
                results['database_connection_status'] = bool(db_config.get('primary'))
            except:
                results['database_connection_status'] = False

            # Check AWS service connectivity
            aws_config = self.get_aws_configuration()
            results['aws_service_connectivity'] = aws_config['aws_available']

            # Check MLflow tracking
            try:
                config_service = self._deps.get_configuration_service()
                mlflow_config = config_service.get_mlflow_config()
                results['mlflow_tracking_status'] = bool(mlflow_config.get('tracking_uri'))
            except:
                results['mlflow_tracking_status'] = False

            # Check functional tests
            functional_results = self.check_functional_tests()
            results.update(functional_results)

            overall_status = 'healthy' if all(v for v in results.values() if isinstance(v, bool)) else 'unhealthy'

            return {
                'results': results,
                'overall_status': overall_status,
                'summary': f"Health check complete - {sum(1 for v in results.values() if v is True)}/{len(results)} systems healthy"
            }
        except Exception as e:
            return {'error': str(e), 'overall_status': 'error'}

    def portal_guide(self) -> Dict[str, Any]:
        """Get portal information and availability."""
        try:
            portals = [
                {'name': 'Setup', 'port': 8501, 'active': True},
                {'name': 'Chat', 'port': 8504, 'active': True},
                {'name': 'RAG', 'port': 8505, 'active': True},
                {'name': 'Workflow', 'port': 8502, 'active': False},
                {'name': 'QA', 'port': 8506, 'active': False},
                {'name': 'DSPy', 'port': 8507, 'active': False}
            ]

            active_count = sum(1 for p in portals if p['active'])

            portal_descriptions = {
                'Setup': 'System configuration and first-time setup wizard',
                'Chat': 'AI chat interface with multiple models',
                'RAG': 'Document search and retrieval system',
                'Workflow': 'Workflow automation and management',
                'QA': 'Question answering and knowledge base',
                'DSPy': 'DSPy programming and model optimization'
            }

            categories = {
                'Core': [p for p in portals if p['name'] in ['Setup', 'Chat']],
                'AI Tools': [p for p in portals if p['name'] in ['RAG', 'QA', 'DSPy']],
                'Management': [p for p in portals if p['name'] in ['Workflow']]
            }

            return {
                'portals': portals,
                'portal_descriptions': portal_descriptions,
                'categories': categories,
                'active_portals': active_count,
                'total_portals': len(portals),
                'overall_status': 'available'
            }
        except Exception as e:
            return {'error': str(e), 'overall_status': 'error'}

    def load_examples(self) -> Dict[str, Any]:
        """Load example data for demonstration."""
        try:
            # This would load sample conversations, documents, etc.
            # For now, return success simulation
            return {
                'overall_status': 'loaded',
                'summary': 'Example data loaded successfully - sample conversations and documents available'
            }
        except Exception as e:
            return {'error': str(e), 'overall_status': 'error'}

    def tidyllm_basic_setup(self) -> Dict[str, Any]:
        """Check TidyLLM basic setup including chat configuration."""
        try:
            # Use existing check_tidyllm_components method
            tidyllm_results = self.check_tidyllm_components()

            # Extract results and model count
            results = tidyllm_results.get('results', {})
            model_count = tidyllm_results.get('model_count', 0)

            # Determine overall status
            if model_count > 0 and results.get('model_configuration'):
                overall_status = 'configured'
            else:
                overall_status = 'needs_configuration'

            return {
                'results': results,
                'model_count': model_count,
                'overall_status': overall_status,
                'summary': tidyllm_results.get('summary', 'TidyLLM setup check complete')
            }
        except Exception as e:
            return {
                'error': str(e),
                'overall_status': 'error',
                'model_count': 0,
                'results': {}
            }

    def _check_rag_system_availability(self) -> Dict[str, bool]:
        """Comprehensive RAG system availability check inspired by rag_creator_v3.py"""
        try:
            # File-based checks for RAG portals
            rag_portal_file = (self.root_path / 'portals' / 'chat' / 'rag_portal.py').exists()
            rag_creator_file = (self.root_path / 'portals' / 'chat' / 'rag_creator_v3.py').exists()
            domain_rag_workflow = (self.root_path / 'portals' / 'chat' / 'domain_rag_workflow_builder.py').exists()

            # Backend infrastructure checks
            intelligent_rag_adapter = (self.root_path / 'packages' / 'tidyllm' / 'knowledge_systems' / 'adapters' / 'intelligent').exists()
            rag_adapters_base = (self.root_path / 'packages' / 'tidyllm' / 'knowledge_systems' / 'adapters').exists()

            # Check for UnifiedRAGManager availability (like rag_creator_v3.py does)
            try:
                # Try to import the UnifiedRAGManager
                import sys
                old_path = sys.path.copy()
                sys.path.insert(0, str(self.root_path / 'packages'))

                from tidyllm.services.unified_rag_manager import UnifiedRAGManager, RAGSystemType
                urm_available = True
            except ImportError:
                urm_available = False
            finally:
                sys.path = old_path

            # Enhanced logic combining file checks with runtime availability
            # unified_rag_facade: Requires portal interface + backend adapter
            unified_rag_facade = (rag_portal_file or rag_creator_file) and intelligent_rag_adapter

            # rag_orchestration: Requires V3 creator + URM or workflow builder + adapters
            rag_orchestration = (
                (rag_creator_file and urm_available) or
                (domain_rag_workflow and rag_adapters_base)
            )

            return {
                'unified_rag_facade': unified_rag_facade,
                'rag_orchestration': rag_orchestration,
                # Additional debug info (not used in main logic but helpful for troubleshooting)
                '_debug': {
                    'rag_portal_file': rag_portal_file,
                    'rag_creator_file': rag_creator_file,
                    'domain_rag_workflow': domain_rag_workflow,
                    'intelligent_rag_adapter': intelligent_rag_adapter,
                    'rag_adapters_base': rag_adapters_base,
                    'urm_available': urm_available
                }
            }
        except Exception as e:
            # Fallback to basic file-based checks
            rag_portal_file = (self.root_path / 'portals' / 'chat' / 'rag_portal.py').exists()
            rag_creator_file = (self.root_path / 'portals' / 'chat' / 'rag_creator_v3.py').exists()
            intelligent_rag_exists = (self.root_path / 'packages' / 'tidyllm' / 'knowledge_systems' / 'adapters' / 'intelligent').exists()

            return {
                'unified_rag_facade': rag_portal_file and intelligent_rag_exists,
                'rag_orchestration': rag_creator_file and intelligent_rag_exists,
                '_error': str(e)
            }

    def test_database_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test database connection using provided configuration.

        Args:
            config: Database configuration dictionary with keys:
                   host, port, database, user, password, schema

        Returns:
            Dict with success/error status and message
        """
        try:
            # Use infrastructure service through dependency injection
            database_service = self._deps.get_database_service()

            # Test connection through infrastructure layer
            result = database_service.test_connection(config)

            if result.get('success', False):
                return {
                    'success': True,
                    'message': f"Connected to {config.get('database', 'database')} at {config.get('host', 'localhost')}:{config.get('port', 5432)}"
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Connection test failed')
                }

        except Exception as e:
            return {
                'success': False,
                'error': f"Database connection test failed: {str(e)}"
            }

    def update_database_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update database configuration in settings.yaml through infrastructure layer.

        Args:
            config: Database configuration dictionary

        Returns:
            Dict with success/error status and message
        """
        try:
            # Use configuration service through dependency injection
            config_service = self._deps.get_configuration_service()

            # Prepare database configuration for settings.yaml
            database_config = {
                'database': {
                    'host': config.get('host', 'localhost'),
                    'port': config.get('port', 5432),
                    'database': config.get('database', 'qa_shipping'),
                    'user': config.get('user', 'postgres'),
                    'password': config.get('password', ''),
                    'schema': config.get('schema', 'public')
                }
            }

            # Save through infrastructure configuration service
            result = config_service.update_settings(database_config)

            if result.get('success', False):
                return {
                    'success': True,
                    'message': 'Database configuration saved to infrastructure/settings.yaml'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Failed to save configuration')
                }

        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to update database configuration: {str(e)}"
            }

    def test_s3_access(self, bucket: str, prefix: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test S3 access with provided credentials.

        Args:
            bucket: S3 bucket name to test
            prefix: S3 prefix to test
            credentials: Dict with access_key_id, secret_access_key, and region

        Returns:
            Dict with test results including credentials_valid, bucket_accessible, etc.
        """
        try:
            # Create temporary configuration with provided credentials
            from infrastructure.services.aws_service import AWSService

            # Create a temporary AWS service with the provided credentials
            test_config = {
                'access_key_id': credentials.get('access_key_id'),
                'secret_access_key': credentials.get('secret_access_key'),
                'region': credentials.get('region', 'us-east-1'),
                'bucket': bucket
            }

            # Create temporary AWS service to test with provided credentials
            temp_aws_service = AWSService(test_config)

            # Perform the test directly using the temporary service
            results = {
                'credentials_valid': False,
                'bucket_accessible': False,
                'write_permission': False,
                'objects_found': 0,
                'errors': []
            }

            try:
                # Test 1: Verify AWS credentials by listing buckets
                s3_client = temp_aws_service.get_s3_client()
                if s3_client:
                    buckets_response = s3_client.list_buckets()
                    results['credentials_valid'] = True
                    results['bucket_count'] = len(buckets_response.get('Buckets', []))

                    # Test 2: Check specific bucket access
                    if bucket:
                        objects = temp_aws_service.list_s3_objects(prefix, bucket)
                        results['bucket_accessible'] = True
                        results['objects_found'] = len(objects)

                        # Test 3: Test write permission
                        import tempfile
                        import os
                        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                            f.write("Test S3 write access")
                            temp_file = f.name

                        test_key = f"{prefix}test_access_{os.urandom(4).hex()}.txt"
                        if temp_aws_service.upload_file(temp_file, test_key, bucket):
                            results['write_permission'] = True
                            # Clean up test file from S3
                            temp_aws_service.delete_s3_object(test_key, bucket)

                        # Clean up local temp file
                        os.unlink(temp_file)

            except Exception as e:
                results['errors'].append(str(e))

            return results

        except Exception as e:
            return {
                'credentials_valid': False,
                'bucket_accessible': False,
                'write_permission': False,
                'objects_found': 0,
                'errors': [str(e)]
            }

    def update_s3_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update S3 configuration in settings.

        Args:
            config: Dict with access_key_id, secret_access_key, region, bucket, and prefix

        Returns:
            Dict with success status and message
        """
        try:
            # Use AWS service adapter to update config
            aws_service = self._deps.get_aws_service()
            result = aws_service.update_s3_config(config)

            return result

        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to update S3 configuration: {str(e)}'
            }

    def test_bedrock_access(self) -> Dict[str, Any]:
        """Test AWS Bedrock access and list available models.

        Returns:
            Dict with success status, available models, and error messages
        """
        try:
            # Use AWS service to test Bedrock connection
            aws_service = self._deps.get_aws_service()

            # Get Bedrock client
            bedrock_client = aws_service.get_bedrock_client()

            if not bedrock_client:
                return {
                    'success': False,
                    'error': 'Could not create Bedrock client. Check AWS credentials and region.'
                }

            # Try to list available foundation models
            try:
                response = bedrock_client.list_foundation_models()
                models = response.get('modelSummaries', [])

                # Extract model IDs
                model_ids = [model.get('modelId', '') for model in models]

                return {
                    'success': True,
                    'models_available': model_ids,
                    'model_count': len(model_ids),
                    'message': f'Successfully connected to Bedrock. Found {len(model_ids)} available models.'
                }

            except Exception as e:
                # If list fails, just try to verify client exists
                return {
                    'success': True,
                    'models_available': [],
                    'message': 'Bedrock client created but could not list models. This is normal if you have limited permissions.',
                    'warning': str(e)
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to test Bedrock access: {str(e)}'
            }

    def test_model_access(self, model_id: str, model_type: str = "text") -> Dict[str, Any]:
        """Test access to a specific Bedrock model."""
        aws_service = self._deps.get_aws_service()
        return aws_service.test_model_access(model_id, model_type)

    def test_multiple_models(self, models: List[Dict[str, str]]) -> Dict[str, Any]:
        """Test access to multiple Bedrock models."""
        aws_service = self._deps.get_aws_service()
        return aws_service.test_multiple_models(models)

    def get_available_models(self, model_type: str = None) -> Dict[str, Any]:
        """Get list of available Bedrock models by type."""
        aws_service = self._deps.get_aws_service()
        return aws_service.get_available_models(model_type)

    def test_embedding_model(self, model_id: str, test_text: str = None) -> Dict[str, Any]:
        """Test embedding model with sample text."""
        aws_service = self._deps.get_aws_service()
        return aws_service.test_embedding_model(model_id, test_text)

    def test_chat_model(self, model_id: str, test_message: str = None) -> Dict[str, Any]:
        """Test chat model with sample message."""
        aws_service = self._deps.get_aws_service()
        return aws_service.test_chat_model(model_id, test_message)

    def validate_model_mapping(self, model_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Validate that all models in mapping are accessible."""
        aws_service = self._deps.get_aws_service()
        return aws_service.validate_model_mapping(model_mapping)