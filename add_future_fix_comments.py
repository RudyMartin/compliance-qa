#!/usr/bin/env python3
"""
Add #future_fix comments to scripts with direct DB connections
"""

import os
import re
from pathlib import Path

# Files that need #future_fix comments
target_files = [
    "packages/tidyllm/infrastructure/tools/mlflow_evidence_checker.py",
    "packages/tidyllm/infrastructure/tools/record_locator.py",
    "packages/tidyllm/infrastructure/session/unified.py",
    "packages/tidyllm/infrastructure/adapters/evidence_adapter.py",
    "packages/tidyllm/infrastructure/adapters/database_adapter.py",
    "packages/tidyllm/infrastructure/credential_setup.py",
    "packages/tidyllm/infrastructure/diagnostics.py",
    "packages/tidyllm/infrastructure/connection_pool.py",
    "packages/tidyllm/knowledge_systems/vector_manager.py",
    "packages/tidyllm/scripts/pre_connection_manager.py",
    "packages/tidyllm/scripts/document_database.py",
    "packages/tidyllm/scripts/execute_robots3_workflow.py",
    "infrastructure/services/resilient_pool_manager.py",
    "adapters/session/unified_session_manager.py",
    "infrastructure/credential_validator.py"
]

# Patterns that indicate direct DB connections
db_patterns = [
    r"import psycopg2",
    r"import sqlite3",
    r"from sqlalchemy",
    r"mlflow\.set_tracking_uri",
    r"mlflow\.tracking\.MlflowClient\(\)",
    r"psycopg2\.connect",
    r"sqlite3\.connect",
    r"create_engine\(",
    r"postgresql://",
    r"localhost.*5432",
    r"os\.environ\[.*DB_",
    r"getenv\(.*DB_"
]

def add_future_fix_comment(file_path):
    """Add #future_fix comment to problematic DB connection patterns"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        modified = False

        for i, line in enumerate(lines):
            # Check if line matches DB connection patterns
            for pattern in db_patterns:
                if re.search(pattern, line):
                    # Check if #future_fix comment doesn't already exist
                    if '#future_fix' not in line and i > 0 and '#future_fix' not in lines[i-1]:
                        # Add comment before the problematic line
                        lines.insert(i, "    # #future_fix: Convert to use enhanced service infrastructure")
                        modified = True
                        print(f"Added #future_fix comment in {file_path} at line {i+1}")
                        break

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            return True
        else:
            print(f"No modifications needed for {file_path}")
            return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    print("Adding #future_fix comments to scripts with direct DB connections...")
    print("=" * 70)

    modified_count = 0

    for file_path in target_files:
        print(f"\nProcessing: {file_path}")
        if add_future_fix_comment(file_path):
            modified_count += 1

    print(f"\n" + "=" * 70)
    print(f"COMPLETED: Modified {modified_count} files with #future_fix comments")
    print("All direct DB connection scripts now marked for conversion to enhanced service infrastructure")

if __name__ == "__main__":
    main()