#!/usr/bin/env python3
"""
Generate Template YAML
======================
Generates a blanked template.yaml file from scratch with:
- Credentials and keys replaced with <ITEM> format (no quotes)
- Base path auto-detected at runtime
- Preserves ports, model names, feature flags
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Union
from datetime import datetime

def get_auto_detected_base_path() -> str:
    """Auto-detect the base path at runtime"""
    # Try to find the compliance-qa root directory
    current_path = Path(__file__).resolve()

    # Walk up until we find compliance-qa directory
    while current_path.name != 'compliance-qa' and current_path.parent != current_path:
        current_path = current_path.parent

    if current_path.name == 'compliance-qa':
        return str(current_path).replace('/', '\\')  # Windows style paths

    # Fallback to relative path
    return str(Path(__file__).parent.parent.parent.resolve()).replace('/', '\\')

def blank_sensitive_value(key: str, value: Any, path: str = "") -> Any:
    """
    Replace sensitive values with blanked templates.
    NO QUOTES in the YAML output.
    """
    full_path = f"{path}.{key}" if path else key

    # List of keys to blank
    sensitive_keys = [
        'access_key_id', 'secret_access_key', 'password', 'db_password',
        'secret_string_value', 'secret_arn', 'artifact_store', 'tracking_uri',
        'mlflow_gateway_uri', 'host', 'database', 'bucket', 'username',
        'profile', 'default_region', 'region', 'secret_string_key'
    ]

    # Check if this key should be blanked
    if any(sk in key.lower() for sk in sensitive_keys):
        if 'access_key_id' in key.lower():
            return '<AWS_ACCESS_KEY_ID>'
        elif 'secret_access_key' in key.lower():
            return '<AWS_SECRET_ACCESS_KEY>'
        elif 'password' in key.lower():
            return '<PASSWORD>'
        elif 'secret_arn' in key.lower():
            return '<SECRET_ARN>'
        elif 'artifact_store' in key.lower():
            return '<S3_ARTIFACT_STORE>'
        elif 'tracking_uri' in key.lower() or 'mlflow_gateway_uri' in key.lower():
            return '<MLFLOW_URI>'
        elif 'host' in key.lower():
            if 'rds.amazonaws.com' in str(value):
                return '<RDS_HOST>'
            elif 'localhost' in str(value) or '0.0.0.0' in str(value):
                return value  # Keep localhost/0.0.0.0
            else:
                return '<DATABASE_HOST>'
        elif 'database' in key.lower():
            if 'mlflow' in str(value).lower():
                return '<MLFLOW_DATABASE>'
            elif '.db' in str(value):
                return value  # Keep local sqlite paths
            else:
                return '<DATABASE_NAME>'
        elif 'bucket' in key.lower():
            return '<S3_BUCKET>'
        elif 'username' in key.lower():
            return '<USERNAME>'
        elif 'region' in key.lower():
            return value  # Keep regions as-is
        elif 'secret_string_key' in key.lower():
            return '<SECRET_KEY>'

    return value

def process_dict(data: Dict[str, Any], path: str = "") -> Dict[str, Any]:
    """Recursively process dictionary to blank sensitive values"""
    result = {}

    for key, value in data.items():
        current_path = f"{path}.{key}" if path else key

        if isinstance(value, dict):
            result[key] = process_dict(value, current_path)
        elif isinstance(value, list):
            result[key] = value  # Keep lists as-is
        else:
            result[key] = blank_sensitive_value(key, value, path)

    return result

def generate_template() -> Dict[str, Any]:
    """Generate the complete template structure"""

    base_path = get_auto_detected_base_path()

    template = {
        # Domain-Driven Architecture Paths Configuration
        'paths': {
            'root_path': base_path,  # Auto-detected
            'path_separator': '\\',

            # Domain Layer - Business Logic
            'domain_folder': 'domain',
            'templates_folder': 'domain/templates',
            'workflows_folder': 'domain/workflows',

            # Portal Layer - User Interfaces
            'portals_folder': 'portals',

            # Infrastructure Layer - Technical Concerns
            'cache_folder': 'infrastructure/cache',
            'config_folder': 'infrastructure/admin',
            'data_folder': 'infrastructure/data',
            'logs_folder': 'infrastructure/logs',
            'temp_folder': 'infrastructure/temp',
            'onboarding_folder': 'infrastructure/onboarding'
        },

        'configuration': {
            'architecture_version': 'v2_4layer_clean',
            'credential_patterns': [
                '*password*',
                '*secret*',
                '*key*',
                'api_keys.*',
                'credentials.*',
                'postgres.db_password',
                'aws.access_key_id',
                'aws.secret_access_key'
            ],
            'environment': 'staging',
            'environment_overrides': {
                'development': {
                    'adapter_debug': True,
                    'log_level': 'DEBUG',
                    's3_prefix': 'dev/'
                },
                'local': {
                    'adapter_development': True,
                    'log_level': 'INFO',
                    's3_prefix': 'local/'
                },
                'production': {
                    'adapter_optimization': True,
                    'log_level': 'WARNING',
                    's3_prefix': 'prod/'
                },
                'staging': {
                    'adapter_monitoring': True,
                    'log_level': 'INFO',
                    's3_prefix': 'staging/'
                }
            },
            'generated_from': 'v2_4layer_clean_template',
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'loaded_by': 'v2_config_loader',
            'official': {
                'contains_credentials': True,
                'is_template_source': True,
                'location': 'tidyllm/admin/settings.yaml',
                'v2_compliant': True
            },
            'security': {
                'adapter_validation': True,
                'audit_changes': True,
                'connection_pool_validation': True,
                'encrypt_at_rest': False,
                'file_permissions': '0600',
                'validate_on_load': True
            },
            'template_generation': {
                'add_placeholders': True,
                'mask_sensitive': True,
                'output_template': 'onboarding/template.settings.yaml',
                'strip_credentials': True,
                'v2_annotations': True
            },
            'version': '2.0.0'
        },

        'credentials': {
            'aws_basic': {
                'access_key_id': '<AWS_ACCESS_KEY_ID>',
                'default_region': 'us-east-1',
                'profile': None,
                'secret_access_key': '<AWS_SECRET_ACCESS_KEY>',
                'secrets_manager': {
                    'access_control': 'corporate_managed',
                    'auto_refresh': True,
                    'cache_ttl_seconds': 3600,
                    'enabled': True,
                    'managed_by': 'corporate_dba',
                    'region': 'us-east-1',
                    'secret_arn': '<SECRET_ARN>',
                    'secret_string_key': '<SECRET_KEY>',
                    'secret_string_value': '<PASSWORD>'
                },
                'type': 'aws_credentials'
            },
            'bedrock_llm': {
                'adapter_config': {
                    'circuit_breaker': True,
                    'retry_attempts': 3,
                    'timeout': 60
                },
                'default_model': 'anthropic.claude-3-sonnet-20240229-v1:0',
                'disabled_models': [],
                'embeddings': {
                    'batch_size': 25,
                    'cache_enabled': True,
                    'dimensions': 1024,
                    'max_chunk_size': 2000,
                    'model_id': 'cohere.embed-english-v3',
                    'normalize': True,
                    'timeout': 30,
                    'type': 'bedrock_embeddings'
                },
                'model_mapping': {
                    'claude-3-5-sonnet': 'anthropic.claude-3-5-sonnet-20240620-v1:0',
                    'claude-3-haiku': 'anthropic.claude-3-haiku-20240307-v1:0',
                    'claude-3-opus': 'anthropic.claude-3-opus-20240229-v1:0',
                    'claude-3-sonnet': 'anthropic.claude-3-sonnet-20240229-v1:0',
                    'titan-v2-recommended-1024d': 'amazon.titan-embed-text-v2:0'
                },
                'region': 'us-east-1',
                'service_provider': 'aws_bedrock',
                'type': 'llm_service'
            },
            'mlflow_alt_db': {
                'database': '<MLFLOW_DATABASE>',
                'engine': 'postgresql',
                'host': '<RDS_HOST>',
                'password': '<PASSWORD>',
                'port': 5432,
                'purpose': 'alternative_mlflow_backend',
                'ssl_mode': 'require',
                'type': 'database_credentials',
                'username': '<USERNAME>'
            },
            'mlflow_api': {
                'artifact_store': '<S3_ARTIFACT_STORE>',
                'service': 'mlflow',
                'tracking_uri': 'http://localhost:5000',
                'type': 'api_credentials'
            },
            'postgresql_primary': {
                'connection_pool': {
                    'enabled': True,
                    'max_connections': 20,
                    'min_connections': 2,
                    'pool_recycle': 3600,
                    'pool_timeout': 30
                },
                'database': '<DATABASE_NAME>',
                'engine': 'postgresql',
                'host': '<RDS_HOST>',
                'password': '<PASSWORD>',
                'port': 5432,
                'ssl_mode': 'require',
                'type': 'database_credentials',
                'username': '<USERNAME>'
            },
            'sqlite_backup': {
                'database': './data/backup.db',
                'engine': 'sqlite',
                'host': './data/backup.db',
                'password': '<PASSWORD>',
                'security': {
                    'encryption': False,
                    'file_permissions': '0600'
                },
                'type': 'database_credentials',
                'username': '<USERNAME>'
            }
        },

        'databases': {
            'backup': {
                'auto_create': True,
                'backup_rotation': {
                    'enabled': True,
                    'location': './data/backups/',
                    'retention_days': 7
                },
                'connection_pool_size': 1,
                'credential_ref': 'sqlite_backup',
                'db_path': './data/backup.db',
                'engine': 'sqlite',
                'max_retries': 3,
                'retry_delay': 2,
                'security': {
                    'encryption': False,
                    'file_permissions': '0600',
                    'secure_delete': True,
                    'wal_mode': True
                },
                'type': 'v2_sqlite_adapter'
            },
            'primary': {
                'connection_pool_size': 5,
                'credential_ref': 'postgresql_primary',
                'engine': 'postgresql',
                'features': {
                    'connection_validation': True,
                    'health_monitoring': True,
                    'performance_metrics': True,
                    'query_logging': True
                },
                'max_retries': 3,
                'pool_client_name': 'primary_adapter',
                'retry_delay': 2,
                'ssl_mode': 'require',
                'type': 'v2_postgres_adapter',
                'use_connection_pool': True
            },
            'secondary': {
                'connection_pool_size': 3,
                'credential_ref': 'secondary_credentials',
                'database': '<DATABASE_NAME>',
                'engine': 'postgresql',
                'host': 'localhost',
                'max_retries': 3,
                'password': '<PASSWORD>',
                'port': 5432,
                'retry_delay': 2,
                'ssl_mode': 'prefer',
                'type': 'v2_postgres_adapter',
                'username': '<USERNAME>'
            }
        }
    }

    # Add remaining sections (keeping structure but blanking sensitive values)
    template.update({
        'deployment': {
            'adapter_registry': {
                'auto_discovery': True,
                'enabled': True,
                'health_monitoring': True,
                'validation': True
            },
            'architecture': 'v2_4layer_clean',
            'backup': {
                'enabled': True,
                'format': 'settings_backup_{timestamp}.yaml',
                'location': './admin/backups/',
                'retention_days': 30,
                'v2_metadata': True
            },
            'connection_pool': {
                'enabled': True,
                'global_pool': True,
                'health_checks': True,
                'monitoring': True,
                'statistics': True
            },
            'mode': 'staging',
            'search_paths': [
                {
                    'description': 'V2 Official admin config with credentials',
                    'path': 'tidyllm/admin/settings.yaml',
                    'permissions': '0600',
                    'v2_compliant': True
                },
                {
                    'description': 'V2 Local development config',
                    'path': './settings.yaml',
                    'permissions': '0600',
                    'v2_fallback': True
                },
                {
                    'description': 'V2 Repository-level config',
                    'path': '../settings.yaml',
                    'permissions': '0600',
                    'v2_template': True
                },
                {
                    'description': 'V2 User profile config',
                    'path': '~/.tidyllm/settings.yaml',
                    'permissions': '0600',
                    'v2_personal': True
                }
            ]
        },

        'features': {
            'gateways': {
                'ai_processing': {
                    'adapter_type': 'AIProcessingAdapter',
                    'batch_processing': True,
                    'enabled': True,
                    'retry_attempts': 2,
                    'timeout': 45
                },
                'corporate_llm': {
                    'adapter_type': 'CorporateLLMAdapter',
                    'circuit_breaker': True,
                    'enabled': True,
                    'retry_attempts': 3,
                    'timeout': 30
                },
                'knowledge_mcp': {
                    'adapter_type': 'KnowledgeMCPAdapter',
                    'enabled': False,
                    'retry_attempts': 3,
                    'timeout': 30,
                    'vector_search': False
                },
                'workflow_optimizer': {
                    'adapter_type': 'WorkflowOptimizerAdapter',
                    'dag_support': True,
                    'enabled': True,
                    'retry_attempts': 2,
                    'timeout': 60
                }
            },
            'security': {
                'access': {
                    'auth_adapter': 'V2AuthAdapter',
                    'rate_limit': {
                        'adapter_type': 'RateLimitAdapter',
                        'enabled': True,
                        'requests_per_hour': 1000,
                        'requests_per_minute': 100
                    },
                    'require_auth': False
                },
                'audit': {
                    'audit_adapter': 'V2AuditAdapter',
                    'audit_all_requests': False,
                    'audit_retention_days': 7,
                    'enabled': True
                },
                'data': {
                    'cache_retention_days': 1,
                    'encrypt_cache': False,
                    'encrypt_logs': False,
                    'encryption_adapter': 'V2EncryptionAdapter',
                    'log_retention_days': 7,
                    'mask_sensitive_data': True
                }
            },
            'workflow_optimizer': {
                'adapter_config': {
                    'circuit_breaker': True,
                    'enable_metrics': False,
                    'use_hexagonal_ports': True
                },
                'audit_trail': False,
                'compliance_mode': False,
                'enable_auto_optimization': False,
                'enable_dag_manager': False,
                'enable_flow_agreements': True,
                'max_workflow_depth': 10,
                'optimization_level': 0,
                'performance_threshold': 0.8,
                'timeout': 60
            }
        }
    })

    # Continue with remaining sections...
    template.update({
        'integrations': {
            'ldap': {
                'adapter_type': 'V2LDAPAdapter',
                'connection_pool': True,
                'enabled': False,
                'type': 'ldap_integration'
            },
            'mlflow': {
                'adapter_type': 'V2MLflowAdapter',
                'artifact_store': '<S3_ARTIFACT_STORE>',
                'backend_options': {
                    'alternative': 'mlflow_alt_db',
                    'fallback': 'file://./mlflow_data',
                    'primary': 'postgresql_shared_pool',
                    'test_mode': None
                },
                'backend_store_uri': 'auto_select',
                'credential_ref': 'mlflow_api',
                'enabled': True,
                'integration_config': {
                    'backend_fallback_enabled': True,
                    'circuit_breaker': True,
                    'health_monitoring': False,
                    'metrics_collection': False,
                    'pool_client_name': 'mlflow_integration',
                    'test_backend_on_startup': True,
                    'use_shared_pool': True
                },
                'mlflow_gateway_uri': 'http://localhost:5000',
                'server': {
                    'host': '0.0.0.0',
                    'port': 5000
                },
                'tracking_uri': 'http://localhost:5000',
                'type': 'tracking_integration'
            },
            'observability': {
                'datadog': {
                    'adapter_type': 'V2DatadogAdapter',
                    'enabled': False
                },
                'newrelic': {
                    'adapter_type': 'V2NewRelicAdapter',
                    'enabled': False
                },
                'type': 'observability_integration'
            },
            'sso': {
                'adapter_type': 'V2SSOAdapter',
                'enabled': False,
                'token_validation': True,
                'type': 'sso_integration'
            }
        },

        'onboarding': {
            'allow_updates': True,
            'architecture_version': 'v2',
            'auto_detect_root_path': True,
            'backup_before_update': True,
            'enable_health_checks': True,
            'health_checks': {
                'connection_pool': False,
                'database_adapters': False,
                'external_adapters': False,
                'integration_adapters': False,
                'service_adapters': False
            },
            'max_retry_attempts': 3,
            'refresh_interval': 5,
            'show_debug_info': False,
            'template_source': True,
            'v2_features': {
                'adapter_validation': True,
                'architecture_compliance': True,
                'architecture_verification': True,
                'connection_pool_init': True,
                'port_binding_check': True
            }
        },

        'operations': {
            'logging': {
                'adapter_type': 'V2LoggingAdapter',
                'backup_count': 5,
                'file_rotation': True,
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'handlers': {
                    'file': {
                        'backup_count': 3,
                        'enabled': True,
                        'max_size_mb': 50,
                        'path': './logs/tidyllm.log'
                    }
                },
                'include_request_id': True,
                'include_session_id': True,
                'include_user_id': False,
                'level': 'INFO',
                'log_correlation': True,
                'max_file_size': '10MB',
                'structured_logging': True
            },
            'monitoring': {
                'adapter_type': 'V2MonitoringAdapter',
                'alerts': {
                    'alert_adapter': 'V2AlertAdapter',
                    'enabled': False
                },
                'enabled': True,
                'health_check': {
                    'adapter_validation': True,
                    'enabled': True,
                    'endpoint': '/health',
                    'interval_seconds': 120
                },
                'metrics': {
                    'adapter_metrics': True,
                    'connection_pool_metrics': True,
                    'enabled': True,
                    'export_to_prometheus': False
                }
            },
            'network': {
                'adapter_type': 'V2NetworkAdapter',
                'proxy': {
                    'enabled': False,
                    'proxy_adapter': 'V2ProxyAdapter'
                },
                'ssl': {
                    'cert_validation': True,
                    'verify': True
                },
                'timeouts': {
                    'adapter_timeout': 30,
                    'connect_timeout': 15,
                    'read_timeout': 60,
                    'total_timeout': 120
                }
            }
        },

        'search_paths': [
            {
                'description': 'V2 Official admin config with credentials',
                'path': 'tidyllm/admin/settings.yaml',
                'permissions': '0600',
                'v2_compliant': True
            }
        ],

        'services': {
            'aws_infrastructure': {
                'credential_ref': 'aws_basic',
                'region': 'us-east-1',
                'secrets_manager': {
                    'access_control': 'corporate_managed',
                    'adapter_config': {
                        'cache_enabled': True,
                        'cache_ttl_seconds': 3600,
                        'circuit_breaker': True,
                        'retry_attempts': 3,
                        'timeout': 30
                    },
                    'adapter_type': 'V2SecretsManagerAdapter',
                    'enabled': True,
                    'health_check_interval': 300,
                    'managed_by': 'corporate_dba',
                    'region': 'us-east-1',
                    'secret_arn': '<SECRET_ARN>',
                    'secret_string_value': '<PASSWORD>'
                },
                'type': 'aws_service'
            },
            'data_tracking': {
                'adapter_config': {
                    'health_check': True,
                    'pool_client_name': 'mlflow_service',
                    'use_connection_pool': True
                },
                'artifact_store': '<S3_ARTIFACT_STORE>',
                'backend_options': {
                    'alternative': 'mlflow_alt_db',
                    'fallback': 'file://./mlflow_data',
                    'primary': 'postgresql_shared_pool',
                    's3_artifacts_only': True
                },
                'backend_store_uri': 'auto_select',
                'credential_ref': 'mlflow_api',
                'enabled': True,
                'mlflow_gateway_uri': 'http://localhost:5000',
                'server': {
                    'host': '0.0.0.0',
                    'port': 5000
                },
                'tracking_uri': 'http://localhost:5000',
                'type': 'tracking_service'
            },
            'database_service': {
                'adapter_type': 'V2PostgresAdapter',
                'credential_ref': 'postgresql_primary',
                'health_check_interval': 60,
                'query_timeout': 30,
                'type': 'database_service',
                'use_shared_pool': True
            },
            'llm_processing': {
                'credential_ref': 'bedrock_llm',
                'enabled': True,
                'type': 'llm_service'
            },
            's3': {
                'adapter_config': {
                    'chunk_size': 8388608,
                    'max_concurrency': 10,
                    'multipart_threshold': 67108864
                },
                'bucket': '<S3_BUCKET>',
                'connection_timeout': 30,
                'max_retries': 3,
                'prefix': 'staging/new/',
                'region': 'us-east-1',
                'test_marker': 'test_marker_v2',
                'type': 's3_service'
            }
        },

        'system': {
            'architecture': {
                'enable_adapters': True,
                'enable_ports': True,
                'pattern': '4layer_clean',
                'strict_boundaries': True,
                'version': 'v2'
            },
            'auto_detect_root_path': True,
            'corporate_mode': False,
            'deep_folder_support': True,
            'deployment_type': 'development',
            'environment': 'staging',
            'organization': 'TidyLLM V2',
            'test_deployment': True
        },

        'testing': {
            'environment_variables': {
                'DB_TIMEOUT': 10,
                'DISABLE_MLFLOW_TELEMETRY': '1',
                'MLFLOW_HTTP_TIMEOUT': 15,
                'MLFLOW_TELEMETRY_OPT_OUT': '1',
                'MLFLOW_TRACKING_TIMEOUT': 15,
                'POOL_TIMEOUT': 10,
                'REQUESTS_TIMEOUT': 10
            },
            'retry_policies': {
                'api_calls': 3,
                'connection_attempts': 3,
                'database_operations': 3,
                'mlflow_operations': 3
            },
            'standardized_config': {
                'connection_timeout': 10,
                'default_timeout': 30,
                'max_retries': 3,
                'mlflow_timeout': 15,
                'no_mocks_policy': True,
                'use_real_infrastructure': True
            }
        }
    })

    return template

def custom_yaml_dumper():
    """Create custom YAML dumper that doesn't add quotes around strings"""
    class NoQuotesStringDumper(yaml.SafeDumper):
        pass

    def str_presenter(dumper, data):
        # For our placeholder values, use plain style (no quotes)
        if data.startswith('<') and data.endswith('>'):
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='')
        # Check if string needs quotes
        if any(c in data for c in ['\n', ':', '#', '@', '!']) or data.startswith('*'):
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')
        # Default: no quotes
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='')

    NoQuotesStringDumper.add_representer(str, str_presenter)
    return NoQuotesStringDumper

def main():
    """Main function to generate the template"""
    print("Generating template.yaml...")
    print(f"Auto-detected base path: {get_auto_detected_base_path()}")

    # Generate template
    template = generate_template()

    # Write to file
    output_path = Path(__file__).parent / 'new_template.yaml'

    with open(output_path, 'w') as f:
        yaml.dump(template, f, Dumper=custom_yaml_dumper(),
                  default_flow_style=False, sort_keys=False, width=120)

    print(f"Generated new_template.yaml at {output_path}")

    # Compare with existing template if it exists
    existing_template = Path(__file__).parent.parent / 'template.yaml'
    if existing_template.exists():
        print("\nComparing with existing template.yaml...")

        with open(existing_template, 'r') as f:
            existing = yaml.safe_load(f)

        # Basic comparison
        if existing.keys() == template.keys():
            print("[OK] Top-level keys match")
        else:
            print("[WARN] Top-level keys differ")
            print(f"  Existing: {set(existing.keys())}")
            print(f"  Generated: {set(template.keys())}")

        # Check sensitive values are blanked
        sensitive_found = []
        for key in ['access_key_id', 'secret_access_key', 'password']:
            if str(template.get('credentials', {}).get('aws_basic', {}).get(key, '')).startswith('<'):
                print(f"[OK] {key} is properly blanked")
            else:
                sensitive_found.append(key)

        if sensitive_found:
            print(f"[WARN] Warning: These values may not be blanked: {sensitive_found}")

    print("\n" + "=" * 60)
    print("✅ TEMPLATE GENERATION COMPLETE!")
    print("=" * 60)
    print(f"\n📄 Template saved to: {output_path.absolute()}")
    print(f"   Relative path: infrastructure/setup/new_template.yaml")
    print("\n📋 Next steps:")
    print("   1. Review the template at the path above")
    print("   2. Fill in the <PLACEHOLDER> values with actual credentials")
    print("   3. Save as 'settings.yaml' in the infrastructure folder")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()