#!/usr/bin/env python3
"""
Verify MLflow Connection Pooling Configuration
==============================================

Quick script to verify that MLflow pooling is properly configured
and to test the connection latency improvements.
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def verify_pooling_config():
    """Verify MLflow pooling environment variables are set."""

    print("MLflow Connection Pooling Verification")
    print("=" * 60)

    # First configure pooling if not already done
    from configure_mlflow_pooling import configure_mlflow_pooling
    db_uri, pooling_config = configure_mlflow_pooling()

    print("\n" + "=" * 60)
    print("Verification Results:")
    print("-" * 40)

    # Check critical pooling variables
    pooling_vars = [
        'MLFLOW_SQLALCHEMY_POOL_SIZE',
        'MLFLOW_SQLALCHEMY_MAX_OVERFLOW',
        'MLFLOW_SQLALCHEMY_POOL_TIMEOUT',
        'MLFLOW_SQLALCHEMY_POOL_RECYCLE',
        'MLFLOW_SQLALCHEMY_POOL_PRE_PING',
        'MLFLOW_SQLALCHEMY_POOL_USE_LIFO',
        'MLFLOW_TRACKING_URI'
    ]

    print("\nPooling Configuration:")
    print("-" * 40)
    configured = True
    for var in pooling_vars:
        value = os.environ.get(var, 'NOT SET')
        if value == 'NOT SET':
            configured = False
            print(f"[X] {var}: {value}")
        else:
            # Hide sensitive data
            if 'URI' in var or 'PASSWORD' in var:
                display_value = value[:30] + '...' if len(value) > 30 else value
            else:
                display_value = value
            print(f"[OK] {var}: {display_value}")

    print("\n" + "-" * 40)

    if configured:
        print("[SUCCESS] All pooling variables are configured")
        print("\nExpected Performance:")
        print("  - Home to AWS: 50-150ms -> 10-30ms (with warm pool)")
        print("  - AWS to AWS: <5ms -> 2-3ms (with warm pool)")
    else:
        print("[WARNING] Some pooling variables are missing")
        print("Run: python infrastructure/services/enhanced_mlflow_service.py")
        print("Or: python start_mlflow_server_pooled.py")

    # Test actual connection if configured
    if configured:
        print("\n" + "=" * 60)
        print("Testing MLflow Connection...")
        print("-" * 40)

        try:
            import mlflow

            # Time a simple MLflow operation
            start = time.time()
            mlflow.get_tracking_uri()
            latency = (time.time() - start) * 1000

            print(f"[OK] MLflow tracking URI retrieved in {latency:.1f}ms")

            # Try to list experiments (actual DB query)
            start = time.time()
            experiments = mlflow.search_experiments(max_results=1)
            query_latency = (time.time() - start) * 1000

            print(f"[OK] Database query completed in {query_latency:.1f}ms")

            if query_latency > 200:
                print("\n[WARNING] High latency detected (>200ms)")
                print("This is expected from home network to AWS RDS")
                print("Latency will be <10ms when running on AWS SageMaker")
            elif query_latency > 50:
                print("\n[OK] Moderate latency (50-200ms) - typical for home to AWS")
            else:
                print("\n[OK] Excellent latency (<50ms) - pool is warm or running on AWS")

        except Exception as e:
            print(f"[WARNING] Could not test MLflow connection: {e}")
            print("This is normal if MLflow server is not running")

    return configured


if __name__ == "__main__":
    verify_pooling_config()