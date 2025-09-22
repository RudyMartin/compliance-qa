"""
Setup Dependencies Adapter
==========================
Adapter implementation that connects the domain setup service
to infrastructure services through the port interface.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from domain.ports.outbound.setup_dependencies_port import (
    SetupDependenciesPort,
    ConfigurationPort,
    EnvironmentPort,
    CredentialPort,
    PortalConfigPort,
    PackageInstallerPort,
    ScriptGeneratorPort,
    AWSServicePort,
    DatabasePort
)

logger = logging.getLogger(__name__)


class ConfigurationAdapter(ConfigurationPort):
    """Adapter for configuration management."""

    def __init__(self):
        """Initialize configuration adapter."""
        self._loader = None

    def _get_loader(self):
        """Lazy load the settings loader."""
        if self._loader is None:
            from infrastructure.yaml_loader import get_settings_loader
            self._loader = get_settings_loader()
        return self._loader

    def load_config(self) -> Any:
        """Load configuration."""
        return self._get_loader().load_config()

    def get_bedrock_config(self) -> Dict[str, Any]:
        """Get Bedrock configuration."""
        return self._get_loader().get_bedrock_config()

    def get_mlflow_config(self) -> Dict[str, Any]:
        """Get MLflow configuration."""
        return self._get_loader().get_mlflow_config()

    def setup_environment_from_settings(self) -> Dict[str, str]:
        """Setup environment variables from settings."""
        from infrastructure.yaml_loader import setup_environment_from_settings
        return setup_environment_from_settings()


class EnvironmentAdapter(EnvironmentPort):
    """Adapter for environment management."""

    def __init__(self):
        """Initialize environment adapter."""
        self._manager = None

    def _get_manager(self):
        """Lazy load the environment manager."""
        if self._manager is None:
            from infrastructure.environment_manager import get_environment_manager
            self._manager = get_environment_manager()
        return self._manager

    def get_variables(self) -> Dict[str, str]:
        """Get environment variables."""
        return self._get_manager().get_variables()

    def set_variable(self, key: str, value: str) -> None:
        """Set environment variable."""
        self._get_manager().set_variable(key, value)

    def validate_environment(self) -> Dict[str, Any]:
        """Validate environment setup."""
        return self._get_manager().validate_environment()


class CredentialAdapter(CredentialPort):
    """Adapter for credential management."""

    def validate_all_credentials(self) -> Dict[str, Any]:
        """Validate all configured credentials."""
        from infrastructure.credential_validator import validate_all_credentials
        return validate_all_credentials()

    def quick_health_check(self) -> Dict[str, bool]:
        """Perform quick health check on credentials."""
        from infrastructure.credential_validator import quick_health_check
        return quick_health_check()

    def sync_active_credential_state(self, status: str) -> None:
        """Sync active credential state."""
        from infrastructure.services.credential_carrier import sync_active_credential_state
        sync_active_credential_state(status)


class PortalConfigAdapter(PortalConfigPort):
    """Adapter for portal configuration."""

    def get_portal_summary(self) -> Dict[str, Any]:
        """Get portal configuration summary."""
        from infrastructure.portal_config import get_portal_summary
        return get_portal_summary()


class PackageInstallerAdapter(PackageInstallerPort):
    """Adapter for package installation."""

    def __init__(self):
        """Initialize package installer adapter."""
        self._installer = None

    def _get_installer(self):
        """Lazy load the package installer."""
        if self._installer is None:
            from infrastructure.install_packages import PackageInstaller
            self._installer = PackageInstaller()
        return self._installer

    def check_local_packages(self) -> List[Dict[str, Any]]:
        """Check status of local packages."""
        return self._get_installer().check_local_packages()

    def install_local_packages(self) -> Dict[str, Any]:
        """Install local packages."""
        return self._get_installer().install_local_packages()

    def run_tests(self, package_name: str, test_type: str = 'unit') -> Dict[str, Any]:
        """Run tests for a package."""
        return self._get_installer().run_tests(package_name, test_type)


class ScriptGeneratorAdapter(ScriptGeneratorPort):
    """Adapter for script generation."""

    def __init__(self):
        """Initialize script generator adapter."""
        self._generator = None

    def _get_generator(self):
        """Lazy load the script generator."""
        if self._generator is None:
            from infrastructure.script_generator import get_script_generator
            self._generator = get_script_generator()
        return self._generator

    def generate_startup_script(self, **kwargs) -> Path:
        """Generate startup script."""
        return self._get_generator().generate_startup_script(**kwargs)

    def generate_service_script(self, service: str, **kwargs) -> Path:
        """Generate service-specific script."""
        return self._get_generator().generate_service_script(service, **kwargs)


class AWSServiceAdapter(AWSServicePort):
    """Adapter for AWS service access."""

    def __init__(self):
        """Initialize AWS service adapter."""
        self._service = None

    def _get_service(self):
        """Lazy load the AWS service."""
        if self._service is None:
            from infrastructure.services.aws_service import get_aws_service
            self._service = get_aws_service()
        return self._service

    def is_available(self) -> bool:
        """Check if AWS service is available."""
        return self._get_service().is_available()

    def get_bedrock_client(self) -> Any:
        """Get Bedrock client."""
        return self._get_service().get_bedrock_client()

    def test_connection(self) -> Dict[str, Any]:
        """Test AWS connection."""
        return {
            'connected': self.is_available(),
            'has_bedrock': self.get_bedrock_client() is not None
        }

    def test_s3_access(self, bucket: str, prefix: str) -> Dict[str, Any]:
        """Test S3 bucket access with specific credentials."""
        service = self._get_service()
        results = {
            'credentials_valid': False,
            'bucket_accessible': False,
            'write_permission': False,
            'objects_found': 0,
            'errors': []
        }

        try:
            # Test credentials by listing buckets
            s3_client = service.get_s3_client()
            if s3_client:
                buckets = s3_client.list_buckets()
                results['credentials_valid'] = True
                results['bucket_count'] = len(buckets.get('Buckets', []))

                # Test specific bucket access
                if bucket:
                    objects = service.list_s3_objects(prefix, bucket)
                    results['bucket_accessible'] = True
                    results['objects_found'] = len(objects)

                    # Test write permission
                    test_key = f"{prefix}test_access.txt"
                    if service.upload_file(__file__, test_key, bucket):
                        results['write_permission'] = True
                        # Clean up test file
                        service.delete_s3_object(test_key, bucket)

        except Exception as e:
            results['errors'].append(str(e))

        return results

    def update_s3_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update S3 configuration in settings."""
        try:
            from infrastructure.yaml_loader import get_settings_loader
            import yaml

            settings_loader = get_settings_loader()
            current_settings = settings_loader._load_settings()  # Get raw dict

            # Update AWS credentials
            if 'credentials' not in current_settings:
                current_settings['credentials'] = {}
            if 'aws_basic' not in current_settings['credentials']:
                current_settings['credentials']['aws_basic'] = {}

            current_settings['credentials']['aws_basic'].update({
                'access_key_id': config.get('access_key_id'),
                'secret_access_key': config.get('secret_access_key'),
                'default_region': config.get('region', 'us-east-1'),
                'type': 'aws_credentials'
            })

            # Update S3 service configuration
            if 'services' not in current_settings:
                current_settings['services'] = {}
            if 's3' not in current_settings['services']:
                current_settings['services']['s3'] = {}

            current_settings['services']['s3'].update({
                'bucket': config.get('bucket'),
                'prefix': config.get('prefix'),
                'region': config.get('region', 'us-east-1'),
                'type': 's3_service'
            })

            # Save back to settings.yaml
            with open(settings_loader.settings_path, 'w') as f:
                yaml.safe_dump(current_settings, f, default_flow_style=False, indent=2)

            return {
                'success': True,
                'message': 'S3 configuration updated successfully'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to update S3 configuration: {str(e)}'
            }

    def test_model_access(self, model_id: str, model_type: str = "text") -> Dict[str, Any]:
        """Test access to a specific Bedrock model."""
        service = self._get_service()
        results = {
            'model_id': model_id,
            'model_type': model_type,
            'accessible': False,
            'response_time_ms': None,
            'error': None,
            'test_successful': False
        }

        try:
            import time
            import json
            start_time = time.time()

            # Get Bedrock client
            bedrock_client = service.get_bedrock_client()
            if not bedrock_client:
                results['error'] = 'Bedrock client not available'
                return results

            if model_type == "embedding":
                # Test embedding model
                test_text = "This is a test sentence for embedding."
                response = bedrock_client.invoke_model(
                    modelId=model_id,
                    body=json.dumps({
                        "inputText": test_text
                    }),
                    contentType="application/json",
                    accept="application/json"
                )

                response_body = json.loads(response['body'].read())
                if 'embedding' in response_body:
                    results['accessible'] = True
                    results['test_successful'] = True
                    results['embedding_dimension'] = len(response_body['embedding'])

            else:  # text/chat model
                # Test text generation model
                test_prompt = "Hello, this is a test prompt."
                response = bedrock_client.invoke_model(
                    modelId=model_id,
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "messages": [{"role": "user", "content": test_prompt}],
                        "max_tokens": 20
                    }),
                    contentType="application/json",
                    accept="application/json"
                )

                response_body = json.loads(response['body'].read())
                if 'content' in response_body:
                    results['accessible'] = True
                    results['test_successful'] = True

            end_time = time.time()
            results['response_time_ms'] = int((end_time - start_time) * 1000)

        except Exception as e:
            results['error'] = str(e)
            results['accessible'] = False

        return results

    def test_multiple_models(self, models: List[Dict[str, str]]) -> Dict[str, Any]:
        """Test access to multiple Bedrock models."""
        results = {
            'total_models': len(models),
            'accessible_models': 0,
            'failed_models': 0,
            'model_results': {},
            'summary': {}
        }

        for model_info in models:
            model_id = model_info.get('model_id')
            model_type = model_info.get('type', 'text')
            friendly_name = model_info.get('name', model_id)

            if model_id:
                test_result = self.test_model_access(model_id, model_type)
                results['model_results'][friendly_name] = test_result

                if test_result['accessible']:
                    results['accessible_models'] += 1
                else:
                    results['failed_models'] += 1

        # Generate summary
        results['summary'] = {
            'success_rate': (results['accessible_models'] / results['total_models']) * 100 if results['total_models'] > 0 else 0,
            'all_accessible': results['accessible_models'] == results['total_models'],
            'any_accessible': results['accessible_models'] > 0
        }

        return results

    def get_available_models(self, model_type: str = None) -> Dict[str, Any]:
        """Get list of available Bedrock models by type."""
        service = self._get_service()
        results = {
            'models': [],
            'total_count': 0,
            'by_type': {},
            'error': None
        }

        try:
            bedrock_client = service.get_bedrock_client()
            if not bedrock_client:
                results['error'] = 'Bedrock client not available'
                return results

            # List foundation models
            response = bedrock_client.list_foundation_models()
            models = response.get('modelSummaries', [])

            for model in models:
                model_info = {
                    'model_id': model.get('modelId'),
                    'model_name': model.get('modelName'),
                    'provider_name': model.get('providerName'),
                    'input_modalities': model.get('inputModalities', []),
                    'output_modalities': model.get('outputModalities', []),
                    'inference_types': model.get('inferenceTypesSupported', [])
                }

                # Determine model type
                if 'EMBEDDING' in model_info['inference_types']:
                    model_info['type'] = 'embedding'
                elif 'TEXT' in model_info['output_modalities']:
                    model_info['type'] = 'text'
                elif 'IMAGE' in model_info['output_modalities']:
                    model_info['type'] = 'image'
                else:
                    model_info['type'] = 'other'

                # Filter by type if specified
                if model_type is None or model_info['type'] == model_type:
                    results['models'].append(model_info)

                # Count by type
                model_type_key = model_info['type']
                if model_type_key not in results['by_type']:
                    results['by_type'][model_type_key] = 0
                results['by_type'][model_type_key] += 1

            results['total_count'] = len(results['models'])

        except Exception as e:
            results['error'] = str(e)

        return results

    def test_embedding_model(self, model_id: str, test_text: str = None) -> Dict[str, Any]:
        """Test embedding model with sample text."""
        if test_text is None:
            test_text = "This is a test sentence for embedding generation."

        return self.test_model_access(model_id, "embedding")

    def test_chat_model(self, model_id: str, test_message: str = None) -> Dict[str, Any]:
        """Test chat model with sample message."""
        if test_message is None:
            test_message = "Hello, please respond with a brief greeting."

        return self.test_model_access(model_id, "text")

    def validate_model_mapping(self, model_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Validate that all models in mapping are accessible."""
        results = {
            'mapping_valid': True,
            'total_mappings': len(model_mapping),
            'accessible_mappings': 0,
            'failed_mappings': [],
            'mapping_results': {}
        }

        for friendly_name, model_id in model_mapping.items():
            test_result = self.test_model_access(model_id)
            results['mapping_results'][friendly_name] = test_result

            if test_result['accessible']:
                results['accessible_mappings'] += 1
            else:
                results['failed_mappings'].append({
                    'friendly_name': friendly_name,
                    'model_id': model_id,
                    'error': test_result['error']
                })

        results['mapping_valid'] = len(results['failed_mappings']) == 0
        return results


class DatabaseAdapter(DatabasePort):
    """Adapter for database service access."""

    def __init__(self):
        """Initialize database adapter."""
        self._service = None

    def _get_service(self):
        """Lazy load the database service."""
        if self._service is None:
            from infrastructure.services.database_service import get_database_service
            self._service = get_database_service()
        return self._service

    def test_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test database connection with given configuration."""
        try:
            # Create a test database service with the provided config
            from infrastructure.services.database_service import DatabaseService
            test_service = DatabaseService(config)

            # Perform health check
            health_result = test_service.health_check()

            # Check if any database is healthy
            databases = health_result.get('databases', {})
            any_healthy = any(db.get('status') == 'healthy' for db in databases.values())

            if any_healthy:
                return {
                    'success': True,
                    'message': 'Database connection successful',
                    'details': health_result
                }
            else:
                return {
                    'success': False,
                    'message': 'Database connection failed',
                    'details': health_result
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Database connection test failed: {str(e)}',
                'error': str(e)
            }

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on database connections."""
        return self._get_service().health_check()

    def update_settings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update database configuration in settings."""
        try:
            # Load current settings (raw YAML, not dataclass)
            from infrastructure.yaml_loader import get_settings_loader
            settings_loader = get_settings_loader()
            current_config = settings_loader._load_settings()  # Get raw dict instead of dataclass

            # Update database configuration for postgresql_primary (current structure)
            if 'credentials' not in current_config:
                current_config['credentials'] = {}
            if 'postgresql_primary' not in current_config['credentials']:
                current_config['credentials']['postgresql_primary'] = {}

            # Update with new config
            current_config['credentials']['postgresql_primary'].update(config)

            # Save back to settings.yaml
            import yaml
            settings_path = settings_loader.settings_path
            with open(settings_path, 'w') as f:
                yaml.safe_dump(current_config, f, default_flow_style=False, indent=2)

            return {
                'success': True,
                'message': 'Database configuration updated successfully',
                'config_saved': config
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to update database configuration: {str(e)}',
                'error': str(e)
            }


class SetupDependenciesAdapter(SetupDependenciesPort):
    """Main adapter that provides all setup dependencies."""

    def __init__(self):
        """Initialize all service adapters."""
        self._config_service = None
        self._env_service = None
        self._cred_service = None
        self._portal_service = None
        self._package_service = None
        self._script_service = None
        self._aws_service = None
        self._database_service = None

    def get_configuration_service(self) -> ConfigurationPort:
        """Get configuration service."""
        if self._config_service is None:
            self._config_service = ConfigurationAdapter()
        return self._config_service

    def get_environment_service(self) -> EnvironmentPort:
        """Get environment service."""
        if self._env_service is None:
            self._env_service = EnvironmentAdapter()
        return self._env_service

    def get_credential_service(self) -> CredentialPort:
        """Get credential service."""
        if self._cred_service is None:
            self._cred_service = CredentialAdapter()
        return self._cred_service

    def get_portal_config_service(self) -> PortalConfigPort:
        """Get portal configuration service."""
        if self._portal_service is None:
            self._portal_service = PortalConfigAdapter()
        return self._portal_service

    def get_package_installer_service(self) -> PackageInstallerPort:
        """Get package installer service."""
        if self._package_service is None:
            self._package_service = PackageInstallerAdapter()
        return self._package_service

    def get_script_generator_service(self) -> ScriptGeneratorPort:
        """Get script generator service."""
        if self._script_service is None:
            self._script_service = ScriptGeneratorAdapter()
        return self._script_service

    def get_aws_service(self) -> AWSServicePort:
        """Get AWS service."""
        if self._aws_service is None:
            self._aws_service = AWSServiceAdapter()
        return self._aws_service

    def get_database_service(self) -> DatabasePort:
        """Get database service."""
        if self._database_service is None:
            self._database_service = DatabaseAdapter()
        return self._database_service


# Singleton instance
_adapter = None

def get_setup_dependencies_adapter() -> SetupDependenciesAdapter:
    """Get singleton adapter instance."""
    global _adapter
    if _adapter is None:
        _adapter = SetupDependenciesAdapter()
    return _adapter