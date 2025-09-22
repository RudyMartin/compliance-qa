#!/usr/bin/env python3
"""
Test script for resilient pool functionality

STANDARDIZED TEST CONFIG:
- NO mocks - uses real infrastructure
- 3 max retries for all operations
- Timeouts set to avoid hangs
"""

import asyncio
import logging
import os
import time
from infrastructure.services.credential_carrier import get_credential_carrier, sync_active_credential_state

# Standardized test configuration
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
CONNECTION_TIMEOUT = 10

# Use existing environment management infrastructure
try:
    from infrastructure.environment_manager import setup_environment_from_settings
    setup_environment_from_settings()
except ImportError:
    # Fallback if environment manager not available
    pass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_resilient_pools():
    """Test the resilient pool manager functionality"""

    print("[TEST] Testing Resilient Pool Manager")
    print("=" * 50)

    # 1. Sync credentials first
    print("\n1. Syncing credentials...")
    sync_result = sync_active_credential_state()
    print(f"   Credential sync: {'[SUCCESS]' if sync_result.get('success') else '[FAILED]'}")

    if not sync_result.get('success'):
        print(f"   Error: {sync_result.get('error')}")
        return

    # 2. Get credential carrier
    print("\n2. Getting credential carrier...")
    credential_carrier = get_credential_carrier()

    # 3. Test database credentials
    print("\n3. Testing database credentials...")
    db_creds = credential_carrier.get_database_credentials()
    if db_creds:
        print(f"   [SUCCESS] Database credentials available from {credential_carrier._credential_sources.get('database', 'unknown')}")
        print(f"   Host: {db_creds.get('host', 'N/A')}")
        print(f"   Database: {db_creds.get('database', 'N/A')}")
    else:
        print("   [FAILED] No database credentials available")
        return

    # 4. Test resilient connection (this will initialize the pool manager)
    print("\n4. Testing resilient database connection...")
    try:
        with credential_carrier.get_resilient_database_connection(timeout=10) as conn:
            print(f"   [SUCCESS] Got resilient database connection: {type(conn)}")

            # Test simple query
            if hasattr(conn, 'cursor'):
                with conn.cursor() as cur:
                    cur.execute("SELECT 1 as test_value")
                    result = cur.fetchone()
                    print(f"   [SUCCESS] Query test successful: {result}")
            else:
                print(f"   [INFO] Connection type doesn't support cursor interface")

    except Exception as e:
        print(f"   [FAILED] Failed to get resilient connection: {e}")
        return

    # 5. Check pool status
    print("\n5. Checking pool status...")
    pool_status = credential_carrier.get_pool_status()

    for pool_name, status in pool_status.items():
        if isinstance(status, dict):
            health = status.get('health_status', 'unknown')
            success_rate = status.get('success_rate', 0)
            print(f"   Pool {pool_name}: {health} (Success rate: {success_rate:.1f}%)")
        else:
            print(f"   Pool {pool_name}: {status}")

    # 6. Test multiple connections to stress test
    print("\n6. Stress testing with multiple connections...")
    connection_count = 3

    for i in range(connection_count):
        try:
            with credential_carrier.get_resilient_database_connection(timeout=5) as conn:
                print(f"   [SUCCESS] Connection {i+1}/{connection_count} successful")
                time.sleep(0.1)  # Small delay
        except Exception as e:
            print(f"   [FAILED] Connection {i+1}/{connection_count} failed: {e}")

    # 7. Final pool status
    print("\n7. Final pool status...")
    final_status = credential_carrier.get_pool_status()

    for pool_name, status in final_status.items():
        if isinstance(status, dict):
            health = status.get('health_status', 'unknown')
            total_requests = status.get('total_requests', 0)
            failed_requests = status.get('failed_requests', 0)
            avg_time = status.get('avg_response_time', 0)
            print(f"   Pool {pool_name}: {health}")
            print(f"     Requests: {total_requests} total, {failed_requests} failed")
            print(f"     Avg response time: {avg_time:.3f}s")

    print("\n[COMPLETE] Resilient pool testing completed!")

if __name__ == "__main__":
    asyncio.run(test_resilient_pools())