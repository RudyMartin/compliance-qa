"""
Credential Validator for compliance-qa Portal System

Validates all system credentials and connections at startup.
Prevents runtime failures due to invalid or missing credentials.

Security-focused approach inspired by hexagonal architecture lessons.
"""

import asyncio
import logging
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from .environment_manager import get_environment_manager
from .infra_delegate import get_infra_delegate

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a credential validation check."""
    component: str
    status: str  # 'success', 'warning', 'error'
    message: str
    details: Dict[str, Any]
    timestamp: datetime


class CredentialValidator:
    """
    Validates all system credentials and external connections.

    Performs comprehensive validation of:
    - Database connections
    - AWS credentials and permissions
    - MLflow service availability
    - External service connectivity
    """

    def __init__(self):
        self.env_manager = get_environment_manager()
        self.validation_results: List[ValidationResult] = []

    async def validate_all_credentials(self) -> Dict[str, Any]:
        """
        Validate all system credentials and connections.

        Returns:
            Comprehensive validation report
        """
        logger.info("Starting comprehensive credential validation...")
        self.validation_results.clear()

        # Run all validations
        await asyncio.gather(
            self._validate_database_connection(),
            self._validate_aws_credentials(),
            self._validate_mlflow_connection(),
            return_exceptions=True
        )

        # Generate summary report
        return self._generate_validation_report()

    async def _validate_database_connection(self):
        """Validate database connectivity and credentials."""
        logger.info("Validating database connection...")

        try:
            # Use infrastructure delegate for connection
            infra = get_infra_delegate()
            conn = infra.get_db_connection()

            if not conn:
                raise Exception("Failed to get database connection from infrastructure")

            # Test basic query
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]

            cursor.close()
            infra.return_db_connection(conn)

            self.validation_results.append(ValidationResult(
                component="database",
                status="success",
                message="Database connection successful",
                details={
                    "host": db_config.host,
                    "port": db_config.port,
                    "database": db_config.database,
                    "version": version[:50] + "..." if len(version) > 50 else version
                },
                timestamp=datetime.now()
            ))

        except psycopg2.OperationalError as e:
            self.validation_results.append(ValidationResult(
                component="database",
                status="error",
                message=f"Database connection failed: {str(e)}",
                details={"error_type": "connection_error"},
                timestamp=datetime.now()
            ))

        except Exception as e:
            self.validation_results.append(ValidationResult(
                component="database",
                status="error",
                message=f"Database validation error: {str(e)}",
                details={"error_type": "validation_error"},
                timestamp=datetime.now()
            ))

    async def _validate_aws_credentials(self):
        """Validate AWS credentials and basic permissions."""
        logger.info("Validating AWS credentials...")

        try:
            aws_config = self.env_manager.get_aws_config()

            # Create session with explicit credentials if provided
            session_kwargs = {'region_name': aws_config.region}
            if aws_config.access_key_id and aws_config.secret_access_key:
                session_kwargs.update({
                    'aws_access_key_id': aws_config.access_key_id,
                    'aws_secret_access_key': aws_config.secret_access_key
                })
            elif aws_config.profile:
                session_kwargs['profile_name'] = aws_config.profile

            session = boto3.Session(**session_kwargs)

            # Test STS (Security Token Service) - basic AWS access
            sts = session.client('sts')
            identity = sts.get_caller_identity()

            # Test Bedrock access (if available)
            bedrock_status = await self._test_bedrock_access(session)

            self.validation_results.append(ValidationResult(
                component="aws",
                status="success",
                message="AWS credentials validated successfully",
                details={
                    "account_id": identity.get('Account', 'Unknown'),
                    "user_arn": identity.get('Arn', 'Unknown'),
                    "region": aws_config.region,
                    "bedrock_access": bedrock_status
                },
                timestamp=datetime.now()
            ))

        except NoCredentialsError:
            self.validation_results.append(ValidationResult(
                component="aws",
                status="warning",
                message="No AWS credentials found - using default profile/IAM role",
                details={"suggestion": "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY if needed"},
                timestamp=datetime.now()
            ))

        except ClientError as e:
            error_code = e.response['Error']['Code']
            self.validation_results.append(ValidationResult(
                component="aws",
                status="error",
                message=f"AWS credential validation failed: {error_code}",
                details={"error_code": error_code, "error_message": str(e)},
                timestamp=datetime.now()
            ))

        except Exception as e:
            self.validation_results.append(ValidationResult(
                component="aws",
                status="error",
                message=f"AWS validation error: {str(e)}",
                details={"error_type": "validation_error"},
                timestamp=datetime.now()
            ))

    async def _test_bedrock_access(self, session) -> str:
        """Test AWS Bedrock access."""
        try:
            bedrock = session.client('bedrock')
            models = bedrock.list_foundation_models()
            model_count = len(models.get('modelSummaries', []))
            return f"Available ({model_count} models)"
        except ClientError as e:
            if e.response['Error']['Code'] == 'UnauthorizedOperation':
                return "Unauthorized (check permissions)"
            return f"Error: {e.response['Error']['Code']}"
        except Exception:
            return "Not available in region"

    async def _validate_mlflow_connection(self):
        """Validate MLflow service connectivity."""
        logger.info("Validating MLflow connection...")

        try:
            mlflow_config = self.env_manager.get_mlflow_config()

            # Test MLflow tracking server
            import mlflow
            import requests

            # Set tracking URI
            mlflow.set_tracking_uri(mlflow_config.tracking_uri)

            # Test connection with simple request
            if mlflow_config.tracking_uri.startswith('http'):
                response = requests.get(f"{mlflow_config.tracking_uri}/health", timeout=10)
                if response.status_code == 200:
                    status = "success"
                    message = "MLflow server is healthy"
                else:
                    status = "warning"
                    message = f"MLflow server responded with status {response.status_code}"
            else:
                # File-based tracking
                status = "success"
                message = "Using file-based MLflow tracking"

            self.validation_results.append(ValidationResult(
                component="mlflow",
                status=status,
                message=message,
                details={
                    "tracking_uri": mlflow_config.tracking_uri,
                    "artifact_root": mlflow_config.artifact_root
                },
                timestamp=datetime.now()
            ))

        except requests.exceptions.ConnectionError:
            self.validation_results.append(ValidationResult(
                component="mlflow",
                status="warning",
                message="MLflow server not accessible - using local tracking",
                details={"suggestion": "Start MLflow server or use file-based tracking"},
                timestamp=datetime.now()
            ))

        except Exception as e:
            self.validation_results.append(ValidationResult(
                component="mlflow",
                status="error",
                message=f"MLflow validation error: {str(e)}",
                details={"error_type": "validation_error"},
                timestamp=datetime.now()
            ))

    def _generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        success_count = sum(1 for r in self.validation_results if r.status == "success")
        warning_count = sum(1 for r in self.validation_results if r.status == "warning")
        error_count = sum(1 for r in self.validation_results if r.status == "error")

        overall_status = "healthy"
        if error_count > 0:
            overall_status = "unhealthy"
        elif warning_count > 0:
            overall_status = "degraded"

        return {
            "overall_status": overall_status,
            "summary": {
                "total_checks": len(self.validation_results),
                "successful": success_count,
                "warnings": warning_count,
                "errors": error_count
            },
            "results": [
                {
                    "component": r.component,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in self.validation_results
            ],
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []

        for result in self.validation_results:
            if result.status == "error":
                if result.component == "database":
                    recommendations.append(
                        "Fix database connection: Check DB_HOST, DB_PORT, DB_USERNAME, DB_PASSWORD environment variables"
                    )
                elif result.component == "aws":
                    recommendations.append(
                        "Configure AWS credentials: Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY or configure AWS profile"
                    )
                elif result.component == "mlflow":
                    recommendations.append(
                        "Start MLflow server or configure MLFLOW_TRACKING_URI for file-based tracking"
                    )

            elif result.status == "warning":
                if result.component == "aws":
                    recommendations.append(
                        "Consider setting explicit AWS credentials for production deployments"
                    )
                elif result.component == "mlflow":
                    recommendations.append(
                        "MLflow server recommended for production tracking and model management"
                    )

        return recommendations

    async def quick_health_check(self) -> bool:
        """
        Quick health check for essential services.

        Returns:
            True if all essential services are healthy
        """
        essential_components = ["database"]

        for component in essential_components:
            if component == "database":
                try:
                    # Use infrastructure delegate for connection
                    infra = get_infra_delegate()
                    conn = infra.get_db_connection()
                    if conn:
                        infra.return_db_connection(conn)
                    else:
                        raise Exception("No database connection available")
                except Exception:
                    return False

        return True


# Convenience functions
async def validate_all_credentials() -> Dict[str, Any]:
    """Quick access to full credential validation."""
    validator = CredentialValidator()
    return await validator.validate_all_credentials()

async def quick_health_check() -> bool:
    """Quick access to health check."""
    validator = CredentialValidator()
    return await validator.quick_health_check()


if __name__ == "__main__":
    # Test the credential validator
    async def test_validation():
        validator = CredentialValidator()
        report = await validator.validate_all_credentials()

        print("Credential Validation Report:")
        print(f"Overall Status: {report['overall_status']}")
        print(f"Summary: {report['summary']}")

        print("\nDetailed Results:")
        for result in report['results']:
            status_icon = {"success": "✅", "warning": "⚠️", "error": "❌"}[result['status']]
            print(f"{status_icon} {result['component']}: {result['message']}")

        if report['recommendations']:
            print("\nRecommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec}")

    asyncio.run(test_validation())