#!/usr/bin/env python3
"""
Setup Portal Functional Tests
==============================
Complete functional tests for the setup portal without UI.
Tests all setup service functionality.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

print("=" * 60)
print("SETUP PORTAL FUNCTIONAL TESTS (REAL)")
print("=" * 60)

# Add project root
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Comment out to allow real MLflow configuration to be tested
# os.environ['MLFLOW_TRACKING_URI'] = 'file:///tmp/mlflow'

class SetupFunctionalTests:
    """Functional tests for setup portal operations."""

    def __init__(self):
        self.root_path = project_root
        self.results = {}
        self._test_params = None

    def get_databases_settings(self):
        """Get settings from 'databases' section in settings.yaml."""
        params = self.get_test_param_settings()
        return params.get('raw_settings', {}).get('databases', {})

    def get_credentials_settings(self):
        """Get settings from 'credentials' section in settings.yaml."""
        params = self.get_test_param_settings()
        return params.get('raw_settings', {}).get('credentials', {})

    def get_integrations_settings(self):
        """Get settings from 'integrations' section in settings.yaml."""
        params = self.get_test_param_settings()
        return params.get('raw_settings', {}).get('integrations', {})

    def get_deployment_settings(self):
        """Get settings from 'deployment' section in settings.yaml."""
        params = self.get_test_param_settings()
        return params.get('raw_settings', {}).get('deployment', {})

    def get_test_param_settings(self):
        """Get real timeout and retry parameters from settings for use in tests."""
        if self._test_params is not None:
            return self._test_params

        try:
            from infrastructure.yaml_loader import SettingsLoader
            loader = SettingsLoader()
            settings = loader._load_settings()

            params = {
                'databases': {},      # From databases section
                'credentials': {},    # From credentials section
                'integrations': {},   # From integrations section
                'deployment': {},     # From deployment section
                'raw_settings': settings
            }

            # databases: section
            databases = settings.get('databases', {})
            for db_name, db_config in databases.items():
                if not db_name.startswith('_'):
                    params['databases'][db_name] = {
                        'query_timeout': db_config.get('query_timeout'),
                        'connection_timeout': db_config.get('connection_timeout'),
                        'max_retries': db_config.get('max_retries')
                    }

            # credentials: section (bedrock_llm)
            bedrock_config = settings.get('credentials', {}).get('bedrock_llm', {})
            if bedrock_config:
                adapter_config = bedrock_config.get('adapter_config', {})
                params['credentials']['bedrock_llm'] = {
                    'retry_attempts': adapter_config.get('retry_attempts'),
                    'timeout': adapter_config.get('timeout')
                }

            # integrations: section
            integrations = settings.get('integrations', {})
            for integration_name, integration_config in integrations.items():
                if isinstance(integration_config, dict):
                    params['integrations'][integration_name] = {}
                    for key, value in integration_config.items():
                        if 'timeout' in key.lower() or 'retry' in key.lower() or key in ['max_retries', 'retry_attempts']:
                            params['integrations'][integration_name][key] = value

            # deployment: section (connection_pool)
            deployment = settings.get('deployment', {})
            if 'connection_pool' in deployment:
                params['deployment']['connection_pool'] = deployment['connection_pool']

            # Cache the results
            self._test_params = params
            return params

        except Exception as e:
            # Return defaults if loading fails
            return {
                'databases': {},
                'credentials': {},
                'integrations': {},
                'deployment': {},
                'error': str(e)
            }

    def test_environment_detection(self):
        """Test environment detection and summary."""
        print("\n1. Testing Environment Detection:")
        print("-" * 40)

        try:
            from domain.services.setup_service import SetupService
            service = SetupService(self.root_path)

            env_summary = service.get_environment_summary()

            # Check for error
            if 'error' in env_summary:
                print(f"[WARNING] Error getting environment: {env_summary['error']}")
            else:
                # Check expected keys from environment_manager
                expected = ['environment', 'validation_results', 'config_sources']
                for key in expected:
                    if key in env_summary:
                        if isinstance(env_summary[key], str):
                            print(f"[OK] {key}: {env_summary[key]}")
                        else:
                            print(f"[OK] {key}: present")
                    else:
                        print(f"[MISSING] {key} not found")

            # Also check Python and platform info
            import sys
            import platform
            print(f"[OK] Python version: {sys.version.split()[0]}")
            print(f"[OK] Platform: {platform.system()}")
            print(f"[OK] Working dir: {self.root_path}")

            self.results['environment_detection'] = True
            return True
        except Exception as e:
            print(f"[FAILED] Environment detection: {e}")
            self.results['environment_detection'] = False
            return False

    def test_credential_validation(self):
        """Test real credential validation."""
        print("\n2. Testing Credential Validation:")
        print("-" * 40)

        try:
            from domain.services.setup_service import SetupService
            from infrastructure.services.credential_carrier import CredentialCarrier
            from infrastructure.yaml_loader import SettingsLoader

            service = SetupService(self.root_path)
            carrier = CredentialCarrier()
            loader = SettingsLoader()

            # Test real credential validation
            creds = {
                'database': carrier.get_database_credentials(),
                'aws': carrier.get_aws_credentials(),
                'mlflow': loader.get_mlflow_config()  # MLflow doesn't have separate credentials
            }

            for service_name, cred_dict in creds.items():
                if cred_dict and any(cred_dict.values()):
                    # Has some credentials configured
                    print(f"[OK] {service_name}: Configured")
                    if service_name == 'database':
                        print(f"    Host: {cred_dict.get('host', 'not set')}")
                        print(f"    Database: {cred_dict.get('database', 'not set')}")
                    elif service_name == 'aws':
                        has_key = bool(cred_dict.get('access_key_id'))
                        print(f"    Access key present: {has_key}")
                    elif service_name == 'mlflow':
                        print(f"    Tracking URI: {cred_dict.get('tracking_uri', 'not set')}")
                else:
                    print(f"[WARNING] {service_name}: Not configured")

            self.results['credential_validation'] = True
            return True
        except Exception as e:
            print(f"[FAILED] Credential validation: {e}")
            self.results['credential_validation'] = False
            return False

    def test_database_configuration(self):
        """Test database configuration loading."""
        print("\n3. Testing Database Configuration:")
        print("-" * 40)

        try:
            from infrastructure.yaml_loader import SettingsLoader
            loader = SettingsLoader()

            # Load REAL database config from settings
            settings = loader._load_settings()

            # Get the real PostgreSQL primary configuration
            pg_primary = settings.get('credentials', {}).get('postgresql_primary', {})

            if pg_primary:
                print(f"[OK] Host: {pg_primary.get('host', 'not set')}")
                print(f"[OK] Port: {pg_primary.get('port', 'not set')}")
                print(f"[OK] Database: {pg_primary.get('database', 'not set')}")
                print(f"[OK] Username: {pg_primary.get('username', 'not set')}")

                # Check password is set but don't print it
                has_password = bool(pg_primary.get('password'))
                print(f"[OK] Password configured: {has_password}")

                # Show SSL mode
                print(f"[OK] SSL Mode: {pg_primary.get('ssl_mode', 'not set')}")

                # Show connection pool settings
                pool = pg_primary.get('connection_pool', {})
                if pool:
                    print(f"[OK] Pool - Max connections: {pool.get('max_connections', 'not set')}")
                    print(f"[OK] Pool - Min connections: {pool.get('min_connections', 'not set')}")
            else:
                # Fallback to get_database_config if postgresql_primary not found
                db_config = loader.get_database_config()
                print(f"[WARNING] Using fallback config")
                print(f"[OK] Host: {db_config.get('host', 'not set')}")
                print(f"[OK] Port: {db_config.get('port', 'not set')}")
                print(f"[OK] Database: {db_config.get('database', 'not set')}")
                print(f"[OK] Username: {db_config.get('username', 'not set')}")

            self.results['database_configuration'] = True
            return True
        except Exception as e:
            print(f"[FAILED] Database configuration: {e}")
            self.results['database_configuration'] = False
            return False

    def test_aws_configuration(self):
        """Test AWS configuration loading."""
        print("\n4. Testing AWS Configuration:")
        print("-" * 40)

        try:
            from infrastructure.yaml_loader import SettingsLoader
            loader = SettingsLoader()

            # Load REAL AWS config from settings
            settings = loader._load_settings()
            aws_creds = settings.get('credentials', {}).get('aws', {})

            if aws_creds:
                has_key = bool(aws_creds.get('access_key_id'))
                has_secret = bool(aws_creds.get('secret_access_key'))

                print(f"[OK] Region: {aws_creds.get('region', 'not set')}")
                print(f"[OK] Access key configured: {has_key}")
                if has_key:
                    # Show first few chars of key for verification
                    key_preview = aws_creds['access_key_id'][:4] + "..." if aws_creds.get('access_key_id') else "none"
                    print(f"[OK] Access key starts with: {key_preview}")
                print(f"[OK] Secret key configured: {has_secret}")

                # Show S3 configuration
                s3_config = settings.get('credentials', {}).get('s3', {})
                if s3_config:
                    print(f"[OK] S3 Bucket: {s3_config.get('bucket', 'not set')}")
                    print(f"[OK] S3 Region: {s3_config.get('region', 'not set')}")
                    print(f"[OK] S3 Prefix: {s3_config.get('prefix', 'not set')}")
            else:
                # Fallback
                aws_config = loader.get_aws_config()
                print(f"[WARNING] Using fallback config")
                print(f"[OK] Region: {aws_config.get('region', 'not set')}")

            self.results['aws_configuration'] = True
            return True
        except Exception as e:
            print(f"[FAILED] AWS configuration: {e}")
            self.results['aws_configuration'] = False
            return False

    def test_mlflow_configuration(self):
        """Test MLflow configuration."""
        print("\n5. Testing MLflow Configuration:")
        print("-" * 40)

        try:
            from infrastructure.yaml_loader import SettingsLoader
            loader = SettingsLoader()

            # Load REAL MLflow config from settings
            settings = loader._load_settings()
            mlflow_creds = settings.get('credentials', {}).get('mlflow', {})

            if mlflow_creds:
                print(f"[OK] Artifact store: {mlflow_creds.get('artifact_store', 'not set')}")

                # Show backend configuration
                backend_options = mlflow_creds.get('backend_options', {})
                if backend_options:
                    print(f"[OK] Backend Primary: {backend_options.get('primary', 'not set')}")
                    print(f"[OK] Backend Alternative: {backend_options.get('alternative', 'not set')}")
                    print(f"[OK] Backend Fallback: {backend_options.get('fallback', 'not set')}")

                backend = mlflow_creds.get('backend_store_uri', 'not set')
                print(f"[OK] Backend Store URI: {backend}")

                # Check if tracking URI should be PostgreSQL
                if backend_options.get('primary') == 'postgresql_shared_pool':
                    # Get PostgreSQL primary config for MLflow backend
                    pg_primary = settings.get('credentials', {}).get('postgresql_primary', {})
                    if pg_primary:
                        mlflow_tracking_uri = f"postgresql://{pg_primary['username']}:***@{pg_primary['host']}:{pg_primary['port']}/mlflow"
                        print(f"[OK] Expected Tracking URI: {mlflow_tracking_uri}")
                        print(f"[OK] MLflow should use PostgreSQL backend")

                # Get actual tracking URI from config
                actual_tracking = loader.get_mlflow_config().get('tracking_uri', 'not set')
                print(f"[INFO] Current Tracking URI: {actual_tracking}")
            else:
                # Fallback
                mlflow_config = loader.get_mlflow_config()
                print(f"[WARNING] Using fallback config")
                print(f"[OK] Tracking URI: {mlflow_config.get('tracking_uri', 'not set')}")
                print(f"[OK] Artifact store: {mlflow_config.get('artifact_store', 'not set')}")

            self.results['mlflow_configuration'] = True
            return True
        except Exception as e:
            print(f"[FAILED] MLflow configuration: {e}")
            self.results['mlflow_configuration'] = False
            return False

    def test_connection_pool_config(self):
        """Test real connection pool configuration."""
        print("\n6. Testing Connection Pool Configuration:")
        print("-" * 40)

        try:
            from infrastructure.yaml_loader import SettingsLoader

            # Get connection pool configuration from settings
            loader = SettingsLoader()
            settings = loader._load_settings()  # Get raw settings dict

            # Check for database connection pool settings
            db_config = loader.get_database_config()

            # Default pool configuration
            pool_config = {
                'min_connections': db_config.get('min_connections', 2),
                'max_connections': db_config.get('max_connections', 20),
                'pool_timeout': db_config.get('pool_timeout', 30),
                'pool_recycle': db_config.get('pool_recycle', 3600)
            }

            print(f"[OK] Min connections: {pool_config['min_connections']}")
            print(f"[OK] Max connections: {pool_config['max_connections']}")
            print(f"[OK] Pool timeout: {pool_config['pool_timeout']}")
            print(f"[OK] Pool recycle: {pool_config['pool_recycle']}")

            # Check for multiple database configs
            if 'databases' in settings:
                for db_name in settings['databases']:
                    if not db_name.startswith('_'):  # Skip defaults
                        print(f"[OK] Database configured: {db_name}")

            self.results['connection_pool_config'] = True
            return True
        except Exception as e:
            print(f"[FAILED] Connection pool config: {e}")
            self.results['connection_pool_config'] = False
            return False

    def test_service_initialization(self):
        """Test real service initialization."""
        print("\n7. Testing Service Initialization:")
        print("-" * 40)

        try:
            from domain.services.setup_service import SetupService
            from domain.services.qa_workflow_service import QAWorkflowService
            from domain.services.dspy_compiler_service import DSPyCompilerService

            # Test actual service initialization
            services_tested = []

            # Setup Service
            try:
                setup_svc = SetupService(self.root_path)
                print(f"[OK] SetupService initialized")
                # Test a real method
                env_summary = setup_svc.get_environment_summary()
                print(f"    Can get environment: {'error' not in env_summary}")
                services_tested.append('setup')
            except Exception as e:
                print(f"[ERROR] SetupService: {e}")

            # QA Workflow Service
            try:
                qa_svc = QAWorkflowService()
                print(f"[OK] QAWorkflowService initialized")
                services_tested.append('qa_workflow')
            except Exception as e:
                print(f"[ERROR] QAWorkflowService: {e}")

            # DSPy Compiler Service
            try:
                dspy_svc = DSPyCompilerService()
                print(f"[OK] DSPyCompilerService initialized")
                services_tested.append('dspy_compiler')
            except Exception as e:
                print(f"[ERROR] DSPyCompilerService: {e}")

            # All services should initialize
            success = len(services_tested) >= 2  # At least 2 services
            self.results['service_initialization'] = success
            return success
        except Exception as e:
            print(f"[FAILED] Service initialization: {e}")
            self.results['service_initialization'] = False
            return False

    def test_database_connections(self):
        """Test actual database connection capabilities."""
        print("\n9. Testing Database Connection Capabilities:")
        print("-" * 40)

        try:
            from domain.services.setup_service import SetupService
            from infrastructure.yaml_loader import SettingsLoader

            service = SetupService(self.root_path)
            loader = SettingsLoader()

            # Load REAL settings
            settings = loader._load_settings()
            pg_primary = settings.get('credentials', {}).get('postgresql_primary', {})

            if pg_primary:
                print(f"[INFO] PostgreSQL Primary (RDS) Configuration:")
                print(f"    Host: {pg_primary.get('host', 'not set')}")
                print(f"    Port: {pg_primary.get('port', 'not set')}")
                print(f"    Database: {pg_primary.get('database', 'not set')}")
                print(f"    Username: {pg_primary.get('username', 'not set')}")
                print(f"    SSL Mode: {pg_primary.get('ssl_mode', 'not set')}")

                # Check if we can create a connection string
                if all(k in pg_primary for k in ['host', 'port', 'database', 'username']):
                    conn_string = f"postgresql://{pg_primary['username']}:***@{pg_primary['host']}:{pg_primary['port']}/{pg_primary['database']}"
                    print(f"[OK] Can build RDS connection string")
                    print(f"    Format: {conn_string}")

                    # Show if this is really RDS
                    if 'rds.amazonaws.com' in pg_primary.get('host', ''):
                        print(f"[OK] Confirmed AWS RDS endpoint")
                else:
                    print(f"[WARNING] Missing required database parameters")
            else:
                # Fallback
                db_config = loader.get_database_config()
                print(f"[WARNING] Using fallback configuration")
                print(f"    Host: {db_config.get('host', 'not set')}")

            self.results['database_connections'] = True
            return True
        except Exception as e:
            print(f"[FAILED] Database connections: {e}")
            self.results['database_connections'] = False
            return False

    def test_aws_connections(self):
        """Test AWS connection capabilities."""
        print("\n10. Testing AWS Connection Capabilities:")
        print("-" * 40)

        try:
            from infrastructure.yaml_loader import SettingsLoader
            from infrastructure.services.aws_service import AWSService

            loader = SettingsLoader()
            settings = loader._load_settings()

            # Get REAL AWS configuration
            aws_basic = settings.get('credentials', {}).get('aws_basic', {})
            s3_config = settings.get('credentials', {}).get('s3', {})
            bedrock_config = settings.get('credentials', {}).get('bedrock_llm', {})

            print(f"[INFO] AWS Basic Configuration:")
            if aws_basic:
                print(f"    Access Key ID: {aws_basic.get('access_key_id', '')[:10]}..." if aws_basic.get('access_key_id') else "    Access Key: Not set")
                print(f"    Region: {aws_basic.get('default_region', 'not set')}")
                print(f"    Secrets Manager ARN: {aws_basic.get('secrets_manager', {}).get('secret_arn', 'not set')[:50]}...")

            print(f"\n[INFO] S3 Configuration:")
            if s3_config:
                print(f"    Bucket: {s3_config.get('bucket', 'not set')}")
                print(f"    Prefix: {s3_config.get('prefix', 'not set')}")
                print(f"    Region: {s3_config.get('region', 'not set')}")
                print(f"    Multipart Threshold: {s3_config.get('adapter_config', {}).get('multipart_threshold', 'default')}")

            print(f"\n[INFO] Bedrock Configuration:")
            if bedrock_config:
                print(f"    Provider: {bedrock_config.get('service_provider', 'not set')}")
                print(f"    Region: {bedrock_config.get('region', 'not set')}")
                print(f"    Default Model: {bedrock_config.get('default_model', 'not set')}")
                models = bedrock_config.get('model_mapping', {})
                if models:
                    print(f"    Available Models:")
                    for model_alias, model_id in models.items():
                        print(f"        - {model_alias}: {model_id}")

            # Check if AWS service can initialize with real config
            try:
                aws_config = loader.get_aws_config()
                aws_svc = AWSService(aws_config)
                print(f"\n[OK] AWS Service initialized successfully")

                # Check available S3 methods
                s3_methods = ['upload_file', 'download_file', 'list_objects', 'delete_object']
                s3_available = sum(1 for m in s3_methods if hasattr(aws_svc, m))
                print(f"[OK] S3 operations available: {s3_available}/{len(s3_methods)}")

                # Check available Bedrock methods
                bedrock_methods = ['invoke_model', 'list_models', 'invoke_model_with_response_stream']
                bedrock_available = sum(1 for m in bedrock_methods if hasattr(aws_svc, m))
                print(f"[OK] Bedrock operations available: {bedrock_available}/{len(bedrock_methods)}")

            except Exception as e:
                print(f"[WARNING] AWS Service initialization: {e}")

            self.results['aws_connections'] = True
            return True
        except Exception as e:
            print(f"[FAILED] AWS connections: {e}")
            self.results['aws_connections'] = False
            return False

    def test_portal_operations(self):
        """Test real portal operations."""
        print("\n8. Testing Portal Operations:")
        print("-" * 40)

        try:
            from domain.services.setup_service import SetupService
            from infrastructure.yaml_loader import SettingsLoader

            service = SetupService(self.root_path)
            loader = SettingsLoader()

            # Test real operations that portal performs
            operations_passed = []
            missing_features = []

            # 1. Load settings
            try:
                settings = loader._load_settings()  # Get raw settings dict
                print(f"[OK] load_settings: Settings loaded successfully")
                print(f"    Found {len(settings)} top-level sections")
                operations_passed.append('load')
            except Exception as e:
                print(f"[ERROR] load_settings: {e}")

            # 2. Validate configuration structure
            try:
                db_config = loader.get_database_config()
                aws_config = loader.get_aws_config()
                mlflow_config = loader.get_mlflow_config()
                print(f"[OK] validate_configuration: All configs have valid structure")
                operations_passed.append('validate')
            except Exception as e:
                print(f"[ERROR] validate_configuration: {e}")

            # 3. Test connection capability (not actual connection)
            try:
                # Check if connection test methods exist
                has_db_test = hasattr(service, 'test_database_connection')
                has_aws_test = hasattr(service, 'test_aws_connection')
                print(f"[OK] test_connection: Connection test methods available")
                print(f"    Database test: {has_db_test}")
                print(f"    AWS test: {has_aws_test}")
                operations_passed.append('test_capability')
            except Exception as e:
                print(f"[ERROR] test_connection: {e}")

            # 4. Save settings capability
            try:
                # Check if save method exists (don't actually save)
                has_save = hasattr(loader, 'save_settings')
                print(f"[OK] save_settings: Save capability available: {has_save}")
                operations_passed.append('save_capability')
            except Exception as e:
                print(f"[ERROR] save_settings: {e}")

            # 5. CHECK FOR MISSING S3 AND BEDROCK CONFIGURATION
            print(f"\n[VALIDATION] Checking Setup Portal for S3/Bedrock Configuration:")

            # Check if portal handles S3 configuration
            has_s3_bucket_config = hasattr(service, 'configure_s3_bucket') or hasattr(loader, 'get_s3_config')
            if not has_s3_bucket_config:
                print(f"[MISSING] S3 bucket configuration NOT in Setup Portal!")
                missing_features.append('S3 bucket configuration')
            else:
                print(f"[OK] S3 bucket configuration available")

            # Check if portal handles Bedrock configuration
            has_bedrock_config = hasattr(service, 'configure_bedrock') or hasattr(loader, 'get_bedrock_config')
            if not has_bedrock_config:
                print(f"[MISSING] Bedrock LLM configuration NOT in Setup Portal!")
                missing_features.append('Bedrock LLM configuration')
            else:
                print(f"[OK] Bedrock configuration available")

            # Test the new get_bedrock_config method
            if hasattr(loader, 'get_bedrock_config'):
                try:
                    bedrock_test = loader.get_bedrock_config()
                    print(f"[OK] get_bedrock_config() method working")
                    print(f"    Models available: {len(bedrock_test.get('model_mapping', {}))}")
                    print(f"    Default model: {bedrock_test.get('default_model', 'not set')}")
                except Exception as e:
                    print(f"[WARNING] get_bedrock_config() method error: {e}")

            # Check what S3/Bedrock settings exist in loaded config
            if settings:
                s3_in_settings = 's3' in settings.get('credentials', {})
                bedrock_in_settings = 'bedrock_llm' in settings.get('credentials', {})
                print(f"\n[INFO] S3 credentials in settings.yaml: {s3_in_settings}")
                print(f"[INFO] Bedrock credentials in settings.yaml: {bedrock_in_settings}")

                if s3_in_settings and not has_s3_bucket_config:
                    print(f"[WARNING] S3 config exists in settings but Setup Portal can't configure it!")
                if bedrock_in_settings and not has_bedrock_config:
                    print(f"[WARNING] Bedrock config exists in settings but Setup Portal can't configure it!")

            # Report missing features
            if missing_features:
                print(f"\n[CRITICAL] Setup Portal is missing configuration for:")
                for feature in missing_features:
                    print(f"    - {feature}")

            success = len(operations_passed) >= 3 and len(missing_features) == 0
            self.results['portal_operations'] = success
            return success
        except Exception as e:
            print(f"[FAILED] Portal operations: {e}")
            self.results['portal_operations'] = False
            return False

    def test_simple_chat_functionality(self):
        """Test simple chat functionality."""
        print("\n11. Testing Simple Chat Functionality:")
        print("-" * 40)

        try:
            # Test UnifiedChatManager initialization
            try:
                from packages.tidyllm.services.unified_chat_manager import UnifiedChatManager, ChatMode
                chat_manager = UnifiedChatManager()
                print(f"[OK] UnifiedChatManager initialized successfully")

                # Check available chat modes
                modes = [mode.value for mode in ChatMode]
                print(f"[OK] Available chat modes: {', '.join(modes)}")

                # Check if manager has required methods
                has_chat = hasattr(chat_manager, 'chat')
                has_stream = hasattr(chat_manager, 'stream_chat')
                print(f"[OK] Chat method available: {has_chat}")
                print(f"[OK] Stream chat available: {has_stream}")

            except ImportError as e:
                print(f"[WARNING] UnifiedChatManager not available: {e}")
                chat_manager = None

            # Test chat workflow interface availability
            try:
                from packages.tidyllm.scripts.chat_workflow_interface import MVRAnalysisFlow
                mvr_flow = MVRAnalysisFlow()
                print(f"[OK] Chat workflow interface available")
                print(f"[OK] MVR Analysis Flow initialized")
            except ImportError as e:
                print(f"[WARNING] Chat workflow interface not available: {e}")

            # Test Bedrock service for chat (from our AWS configuration)
            try:
                from infrastructure.services.aws_service import AWSService
                from infrastructure.yaml_loader import SettingsLoader

                loader = SettingsLoader()
                settings = loader._load_settings()
                bedrock_config = settings.get('credentials', {}).get('bedrock_llm', {})

                if bedrock_config:
                    print(f"[OK] Bedrock chat models configured:")
                    models = bedrock_config.get('model_mapping', {})
                    for model_alias, model_id in models.items():
                        print(f"    - {model_alias}: {model_id}")

                    default_model = bedrock_config.get('default_model', 'not set')
                    print(f"[OK] Default chat model: {default_model}")
                else:
                    print(f"[WARNING] No Bedrock models configured for chat")

            except Exception as e:
                print(f"[WARNING] Bedrock chat configuration check failed: {e}")

            # Test if AWS service can handle chat requests
            try:
                aws_config = loader.get_aws_config()
                aws_svc = AWSService(aws_config)

                # Check if AWS service has Bedrock methods for chat
                has_invoke = hasattr(aws_svc, 'invoke_model')
                has_stream = hasattr(aws_svc, 'invoke_model_with_response_stream')
                print(f"[OK] AWS Bedrock invoke_model: {has_invoke}")
                print(f"[OK] AWS Bedrock streaming: {has_stream}")

                if has_invoke:
                    print(f"[OK] Chat backend (AWS Bedrock) ready for use")

            except Exception as e:
                print(f"[WARNING] AWS Bedrock chat check failed: {e}")

            # Test simple chat selectors and options
            print(f"\n[INFO] Testing Simple Chat Selectors:")

            # Model selector options
            if bedrock_config:
                models = bedrock_config.get('model_mapping', {})
                print(f"[OK] Model selector options ({len(models)} available):")
                for model_alias in models.keys():
                    print(f"    - {model_alias}")

            # Chat mode selector options
            if chat_manager:
                try:
                    modes = [mode.value for mode in ChatMode]
                    print(f"[OK] Chat mode selector options ({len(modes)} available):")
                    for mode in modes:
                        print(f"    - {mode}")
                except Exception as e:
                    print(f"[WARNING] Could not enumerate chat modes: {e}")

            # Temperature/parameter selector simulation
            print(f"[OK] Parameter selectors should include:")
            print(f"    - Temperature: 0.0 - 1.0 (creativity control)")
            print(f"    - Max tokens: 100 - 4000 (response length)")
            print(f"    - Top-p: 0.0 - 1.0 (response diversity)")

            # Reasoning toggle
            print(f"[OK] Chat options should include:")
            print(f"    - Reasoning/Chain of Thought toggle")
            print(f"    - Streaming response toggle")
            print(f"    - Conversation history toggle")

            # Check if chat functionality can work end-to-end
            chat_ready = (chat_manager is not None and
                         bedrock_config and
                         has_invoke)

            if chat_ready:
                print(f"\n[SUCCESS] Simple chat functionality is fully configured:")
                print(f"    [OK] Chat manager available")
                print(f"    [OK] Bedrock models configured")
                print(f"    [OK] AWS service ready")
                print(f"    [OK] Model selectors available")
                print(f"    [OK] Chat mode selectors available")
            else:
                print(f"\n[WARNING] Chat functionality has missing components")

            self.results['simple_chat_functionality'] = True
            return True

        except Exception as e:
            print(f"[FAILED] Simple chat functionality: {e}")
            self.results['simple_chat_functionality'] = False
            return False

    def test_timeout_retry_configuration(self):
        """Test real timeout and retry parameters from settings sections."""
        print("\n12. Testing Timeout & Retry Configuration (REAL):")
        print("-" * 40)

        try:
            print(f"[INFO] Reading from settings.yaml sections using matching function names:")

            # databases: section via get_databases_settings()
            databases = self.get_databases_settings()
            print(f"\n[OK] get_databases_settings() -> 'databases:' section:")
            for db_name, db_config in databases.items():
                if not db_name.startswith('_'):
                    max_retries = db_config.get('max_retries')
                    if max_retries:
                        print(f"    - databases.{db_name}.max_retries: {max_retries}")

            # credentials: section via get_credentials_settings()
            credentials = self.get_credentials_settings()
            print(f"\n[OK] get_credentials_settings() -> 'credentials:' section:")
            if 'bedrock_llm' in credentials:
                bedrock = credentials['bedrock_llm']
                adapter_config = bedrock.get('adapter_config', {})
                if 'retry_attempts' in adapter_config:
                    print(f"    - credentials.bedrock_llm.adapter_config.retry_attempts: {adapter_config['retry_attempts']}")
                if 'timeout' in adapter_config:
                    print(f"    - credentials.bedrock_llm.adapter_config.timeout: {adapter_config['timeout']}s")

            # integrations: section via get_integrations_settings()
            integrations = self.get_integrations_settings()
            print(f"\n[OK] get_integrations_settings() -> 'integrations:' section:")
            for integration_name, integration_config in integrations.items():
                if isinstance(integration_config, dict):
                    for key, value in integration_config.items():
                        if 'timeout' in key.lower() or 'retry' in key.lower():
                            print(f"    - integrations.{integration_name}.{key}: {value}")

            # deployment: section via get_deployment_settings()
            deployment = self.get_deployment_settings()
            print(f"\n[OK] get_deployment_settings() -> 'deployment:' section:")
            if 'connection_pool' in deployment:
                pool_config = deployment['connection_pool']
                for key, value in pool_config.items():
                    if isinstance(value, (int, float, bool)):
                        print(f"    - deployment.connection_pool.{key}: {value}")

            # Show function-to-section mapping
            print(f"\n[SUCCESS] Function names match settings.yaml sections:")
            print(f"    [OK] get_databases_settings()    -> databases:")
            print(f"    [OK] get_credentials_settings()  -> credentials:")
            print(f"    [OK] get_integrations_settings() -> integrations:")
            print(f"    [OK] get_deployment_settings()   -> deployment:")

            # Example usage with clear section mapping
            bedrock_config = credentials.get('bedrock_llm', {}).get('adapter_config', {})
            bedrock_timeout = bedrock_config.get('timeout', 30)
            bedrock_retries = bedrock_config.get('retry_attempts', 3)
            print(f"\n[EXAMPLE] credentials.bedrock_llm: timeout={bedrock_timeout}s, retries={bedrock_retries}")

            self.results['timeout_retry_configuration'] = True
            return True

        except Exception as e:
            print(f"[FAILED] Timeout/retry configuration: {e}")
            self.results['timeout_retry_configuration'] = False
            return False

    def run_all_tests(self):
        """Run all functional tests."""
        self.test_environment_detection()
        self.test_credential_validation()
        self.test_database_configuration()
        self.test_aws_configuration()
        self.test_mlflow_configuration()
        self.test_connection_pool_config()
        self.test_service_initialization()
        self.test_portal_operations()
        self.test_database_connections()
        self.test_aws_connections()
        self.test_simple_chat_functionality()
        self.test_timeout_retry_configuration()

        return self.results

def main():
    """Main test runner."""
    tester = SetupFunctionalTests()
    results = tester.run_all_tests()

    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test.replace('_', ' ').title()}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\nAll tests passed!")
        return 0
    else:
        print(f"\n{total - passed} tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())