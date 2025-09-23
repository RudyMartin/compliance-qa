#!/usr/bin/env python3
"""
Fix MLflow database schema by creating all missing tables
This will create the complete MLflow schema in PostgreSQL
"""

import psycopg2
import yaml
from pathlib import Path

# Load PostgreSQL credentials
settings_path = Path('infrastructure/settings.yaml')
with open(settings_path) as f:
    config = yaml.safe_load(f)

pg = config['credentials']['postgresql_primary']

print('FIXING MLFLOW DATABASE SCHEMA')
print('=' * 60)
print(f'Database: {pg["database"]} at {pg["host"]}')
print()

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=pg['host'],
        port=pg['port'],
        database=pg['database'],
        user=pg['username'],
        password=pg['password']
    )
    cur = conn.cursor()

    # Check what tables already exist
    cur.execute("""
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename
    """)
    existing_tables = [row[0] for row in cur.fetchall()]
    print(f'Found {len(existing_tables)} existing tables')

    # Define all MLflow tables that should exist
    mlflow_tables_sql = {
        'datasets': """
            CREATE TABLE IF NOT EXISTS datasets (
                dataset_uuid VARCHAR(36) NOT NULL,
                experiment_id INTEGER NOT NULL,
                name VARCHAR(500) NOT NULL,
                digest VARCHAR(36) NOT NULL,
                dataset_source_type VARCHAR(36),
                dataset_source TEXT,
                dataset_schema TEXT,
                dataset_profile TEXT,
                PRIMARY KEY (experiment_id, name, digest),
                FOREIGN KEY(experiment_id) REFERENCES experiments (experiment_id),
                CONSTRAINT dataset_uuid UNIQUE (dataset_uuid)
            )
        """,

        'inputs': """
            CREATE TABLE IF NOT EXISTS inputs (
                input_uuid VARCHAR(36) NOT NULL,
                source_type VARCHAR(36) NOT NULL,
                source_id VARCHAR(36) NOT NULL,
                destination_type VARCHAR(36) NOT NULL,
                destination_id VARCHAR(36) NOT NULL,
                PRIMARY KEY (source_type, source_id, destination_type, destination_id),
                CONSTRAINT input_uuid UNIQUE (input_uuid)
            )
        """,

        'input_tags': """
            CREATE TABLE IF NOT EXISTS input_tags (
                input_uuid VARCHAR(36) NOT NULL,
                name VARCHAR(255) NOT NULL,
                value VARCHAR(500),
                PRIMARY KEY (input_uuid, name)
            )
        """,

        'model_versions': """
            CREATE TABLE IF NOT EXISTS model_versions (
                name VARCHAR(256) NOT NULL,
                version INTEGER NOT NULL,
                creation_time BIGINT,
                last_updated_time BIGINT,
                description VARCHAR(5000),
                user_id VARCHAR(256),
                current_stage VARCHAR(20),
                source VARCHAR(500),
                run_id VARCHAR(32),
                status VARCHAR(20),
                status_message VARCHAR(500),
                run_link VARCHAR(500),
                storage_location VARCHAR(500),
                PRIMARY KEY (name, version),
                FOREIGN KEY(run_id) REFERENCES runs (run_uuid)
            )
        """,

        'model_version_tags': """
            CREATE TABLE IF NOT EXISTS model_version_tags (
                name VARCHAR(256) NOT NULL,
                version INTEGER NOT NULL,
                key VARCHAR(250) NOT NULL,
                value VARCHAR(5000),
                PRIMARY KEY (name, version, key),
                FOREIGN KEY(name, version) REFERENCES model_versions (name, version) ON DELETE CASCADE
            )
        """,

        'registered_models': """
            CREATE TABLE IF NOT EXISTS registered_models (
                name VARCHAR(256) NOT NULL,
                creation_time BIGINT,
                last_updated_time BIGINT,
                description VARCHAR(5000),
                PRIMARY KEY (name)
            )
        """,

        'registered_model_tags': """
            CREATE TABLE IF NOT EXISTS registered_model_tags (
                name VARCHAR(256) NOT NULL,
                key VARCHAR(250) NOT NULL,
                value VARCHAR(5000),
                PRIMARY KEY (name, key),
                FOREIGN KEY(name) REFERENCES registered_models (name) ON DELETE CASCADE
            )
        """,

        'registered_model_aliases': """
            CREATE TABLE IF NOT EXISTS registered_model_aliases (
                name VARCHAR(256) NOT NULL,
                alias VARCHAR(256) NOT NULL,
                version INTEGER NOT NULL,
                PRIMARY KEY (name, alias),
                FOREIGN KEY(name, version) REFERENCES model_versions (name, version) ON DELETE CASCADE
            )
        """,

        'experiment_tags': """
            CREATE TABLE IF NOT EXISTS experiment_tags (
                key VARCHAR(250) NOT NULL,
                value VARCHAR(5000),
                experiment_id INTEGER NOT NULL,
                PRIMARY KEY (key, experiment_id),
                FOREIGN KEY(experiment_id) REFERENCES experiments (experiment_id)
            )
        """,

        'run_tags': """
            CREATE TABLE IF NOT EXISTS run_tags (
                key VARCHAR(250) NOT NULL,
                value VARCHAR(5000),
                run_uuid VARCHAR(32) NOT NULL,
                PRIMARY KEY (key, run_uuid),
                FOREIGN KEY(run_uuid) REFERENCES runs (run_uuid)
            )
        """,

        'trace_info': """
            CREATE TABLE IF NOT EXISTS trace_info (
                request_id VARCHAR(50) NOT NULL,
                experiment_id INTEGER NOT NULL,
                timestamp_ms BIGINT NOT NULL,
                execution_time_ms BIGINT,
                status VARCHAR(50) NOT NULL,
                PRIMARY KEY (request_id),
                FOREIGN KEY(experiment_id) REFERENCES experiments (experiment_id)
            )
        """,

        'trace_tags': """
            CREATE TABLE IF NOT EXISTS trace_tags (
                request_id VARCHAR(50) NOT NULL,
                key VARCHAR(250) NOT NULL,
                value VARCHAR(8000),
                PRIMARY KEY (request_id, key)
            )
        """,

        'trace_request_metadata': """
            CREATE TABLE IF NOT EXISTS trace_request_metadata (
                request_id VARCHAR(50) NOT NULL,
                key VARCHAR(250) NOT NULL,
                value VARCHAR(8000),
                PRIMARY KEY (request_id, key)
            )
        """
    }

    # Create missing tables
    created_tables = []
    for table_name, create_sql in mlflow_tables_sql.items():
        if table_name not in existing_tables:
            print(f'Creating table: {table_name}')
            cur.execute(create_sql)
            created_tables.append(table_name)
        else:
            print(f'[EXISTS] Table: {table_name}')

    # Create indexes for better performance
    indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_datasets_experiment_id ON datasets(experiment_id)",
        "CREATE INDEX IF NOT EXISTS idx_datasets_uuid ON datasets(dataset_uuid)",
        "CREATE INDEX IF NOT EXISTS idx_inputs_destination_type_id ON inputs(destination_type, destination_id)",
        "CREATE INDEX IF NOT EXISTS idx_inputs_source_type_id ON inputs(source_type, source_id)",
        "CREATE INDEX IF NOT EXISTS idx_input_tags_input_uuid ON input_tags(input_uuid)",
        "CREATE INDEX IF NOT EXISTS idx_model_versions_run_id ON model_versions(run_id)",
        "CREATE INDEX IF NOT EXISTS idx_experiment_tags_experiment_id ON experiment_tags(experiment_id)",
        "CREATE INDEX IF NOT EXISTS idx_run_tags_run_uuid ON run_tags(run_uuid)"
    ]

    print()
    print('Creating indexes for performance...')
    for idx_sql in indexes_sql:
        cur.execute(idx_sql)

    # Commit all changes
    conn.commit()

    # Verify final state
    cur.execute("""
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
        AND tablename LIKE '%mlflow%' OR tablename LIKE '%experiment%'
        OR tablename LIKE '%run%' OR tablename LIKE '%dataset%'
        OR tablename LIKE '%model%' OR tablename LIKE '%input%'
        OR tablename LIKE '%trace%'
        ORDER BY tablename
    """)
    final_tables = cur.fetchall()

    print()
    print('FINAL MLflow TABLES:')
    print('-' * 30)
    for table in final_tables:
        print(f'  - {table[0]}')

    print()
    print('SUCCESS! MLflow schema is now complete.')
    print(f'Created {len(created_tables)} new tables:')
    for table in created_tables:
        print(f'  [NEW] {table}')

    cur.close()
    conn.close()

    print()
    print('MLflow should now work without schema errors!')

except Exception as e:
    print(f'ERROR: {e}')
    print()
    print('This might be due to:')
    print('1. Permission issues (user cannot create tables)')
    print('2. Foreign key constraints (dependent tables missing)')
    print('3. Connection issues')