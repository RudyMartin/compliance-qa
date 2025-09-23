#!/usr/bin/env python3
"""
Restore MLflow Database Schema
===============================
Python script to restore complete MLflow schema with all tables, indexes, and functions.
Safe to run multiple times - only creates missing components.
"""

import psycopg2
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

class MLflowSchemaRestorer:
    """Restore and verify MLflow database schema."""

    def __init__(self):
        """Initialize with database credentials from settings."""
        settings_path = Path(__file__).parent.parent / 'settings.yaml'
        with open(settings_path) as f:
            config = yaml.safe_load(f)

        self.pg_config = config['credentials']['postgresql_primary']
        self.conn = None
        self.cur = None

    def connect(self):
        """Connect to PostgreSQL database."""
        self.conn = psycopg2.connect(
            host=self.pg_config['host'],
            port=self.pg_config['port'],
            database=self.pg_config['database'],
            user=self.pg_config['username'],
            password=self.pg_config['password']
        )
        self.cur = self.conn.cursor()
        print(f"Connected to: {self.pg_config['database']} at {self.pg_config['host']}")

    def disconnect(self):
        """Close database connection."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def create_core_tables(self) -> List[str]:
        """Create core MLflow tables."""
        created = []

        # Core tables with their SQL
        tables = {
            'experiments': """
                CREATE TABLE IF NOT EXISTS experiments (
                    experiment_id SERIAL PRIMARY KEY,
                    name VARCHAR(256) UNIQUE NOT NULL,
                    artifact_location VARCHAR(256),
                    lifecycle_stage VARCHAR(32) DEFAULT 'active',
                    creation_time BIGINT,
                    last_update_time BIGINT
                )
            """,

            'runs': """
                CREATE TABLE IF NOT EXISTS runs (
                    run_uuid VARCHAR(32) PRIMARY KEY,
                    name VARCHAR(250),
                    source_type VARCHAR(20),
                    source_name VARCHAR(500),
                    entry_point_name VARCHAR(50),
                    user_id VARCHAR(256),
                    status VARCHAR(20),
                    start_time BIGINT,
                    end_time BIGINT,
                    source_version VARCHAR(50),
                    lifecycle_stage VARCHAR(20),
                    artifact_uri VARCHAR(200),
                    experiment_id INTEGER,
                    deleted_time BIGINT,
                    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
                )
            """,

            'metrics': """
                CREATE TABLE IF NOT EXISTS metrics (
                    key VARCHAR(250) NOT NULL,
                    value DOUBLE PRECISION NOT NULL,
                    timestamp BIGINT NOT NULL,
                    run_uuid VARCHAR(32) NOT NULL,
                    step BIGINT NOT NULL DEFAULT 0,
                    is_nan BOOLEAN NOT NULL DEFAULT FALSE,
                    PRIMARY KEY (key, timestamp, step, run_uuid, value, is_nan),
                    FOREIGN KEY (run_uuid) REFERENCES runs(run_uuid)
                )
            """,

            'latest_metrics': """
                CREATE TABLE IF NOT EXISTS latest_metrics (
                    key VARCHAR(250) NOT NULL,
                    value DOUBLE PRECISION NOT NULL,
                    timestamp BIGINT NOT NULL,
                    run_uuid VARCHAR(32) NOT NULL,
                    step BIGINT NOT NULL,
                    is_nan BOOLEAN NOT NULL,
                    PRIMARY KEY (key, run_uuid),
                    FOREIGN KEY (run_uuid) REFERENCES runs(run_uuid)
                )
            """,

            'params': """
                CREATE TABLE IF NOT EXISTS params (
                    key VARCHAR(250) NOT NULL,
                    value VARCHAR(500) NOT NULL,
                    run_uuid VARCHAR(32) NOT NULL,
                    PRIMARY KEY (key, run_uuid),
                    FOREIGN KEY (run_uuid) REFERENCES runs(run_uuid)
                )
            """,

            'tags': """
                CREATE TABLE IF NOT EXISTS tags (
                    key VARCHAR(250) NOT NULL,
                    value VARCHAR(5000),
                    run_uuid VARCHAR(32) NOT NULL,
                    PRIMARY KEY (key, run_uuid),
                    FOREIGN KEY (run_uuid) REFERENCES runs(run_uuid)
                )
            """
        }

        for table_name, sql in tables.items():
            try:
                # Check if table exists first
                self.cur.execute(
                    "SELECT 1 FROM pg_tables WHERE tablename = %s AND schemaname = 'public'",
                    (table_name,)
                )
                exists = self.cur.fetchone() is not None

                if not exists:
                    self.cur.execute(sql)
                    created.append(table_name)
                    print(f"  Created table: {table_name}")
                else:
                    print(f"  [EXISTS] {table_name}")
            except Exception as e:
                print(f"  [ERROR] {table_name}: {e}")

        return created

    def create_tag_tables(self) -> List[str]:
        """Create tag tables."""
        created = []

        tables = {
            'experiment_tags': """
                CREATE TABLE IF NOT EXISTS experiment_tags (
                    key VARCHAR(250) NOT NULL,
                    value VARCHAR(5000),
                    experiment_id INTEGER NOT NULL,
                    PRIMARY KEY (key, experiment_id),
                    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
                )
            """,

            'run_tags': """
                CREATE TABLE IF NOT EXISTS run_tags (
                    key VARCHAR(250) NOT NULL,
                    value VARCHAR(5000),
                    run_uuid VARCHAR(32) NOT NULL,
                    PRIMARY KEY (key, run_uuid),
                    FOREIGN KEY (run_uuid) REFERENCES runs(run_uuid)
                )
            """
        }

        for table_name, sql in tables.items():
            try:
                # Check if table exists first
                self.cur.execute(
                    "SELECT 1 FROM pg_tables WHERE tablename = %s AND schemaname = 'public'",
                    (table_name,)
                )
                exists = self.cur.fetchone() is not None

                if not exists:
                    self.cur.execute(sql)
                    created.append(table_name)
                    print(f"  Created table: {table_name}")
                else:
                    print(f"  [EXISTS] {table_name}")
            except Exception as e:
                print(f"  [ERROR] {table_name}: {e}")

        return created

    def create_model_registry_tables(self) -> List[str]:
        """Create model registry tables."""
        created = []

        tables = {
            'registered_models': """
                CREATE TABLE IF NOT EXISTS registered_models (
                    name VARCHAR(256) PRIMARY KEY,
                    creation_time BIGINT,
                    last_updated_time BIGINT,
                    description VARCHAR(5000)
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
                    FOREIGN KEY (run_id) REFERENCES runs(run_uuid)
                )
            """,

            'model_version_tags': """
                CREATE TABLE IF NOT EXISTS model_version_tags (
                    name VARCHAR(256) NOT NULL,
                    version INTEGER NOT NULL,
                    key VARCHAR(250) NOT NULL,
                    value VARCHAR(5000),
                    PRIMARY KEY (name, version, key),
                    FOREIGN KEY (name, version) REFERENCES model_versions(name, version) ON DELETE CASCADE
                )
            """,

            'registered_model_tags': """
                CREATE TABLE IF NOT EXISTS registered_model_tags (
                    name VARCHAR(256) NOT NULL,
                    key VARCHAR(250) NOT NULL,
                    value VARCHAR(5000),
                    PRIMARY KEY (name, key),
                    FOREIGN KEY (name) REFERENCES registered_models(name) ON DELETE CASCADE
                )
            """,

            'registered_model_aliases': """
                CREATE TABLE IF NOT EXISTS registered_model_aliases (
                    name VARCHAR(256) NOT NULL,
                    alias VARCHAR(256) NOT NULL,
                    version INTEGER NOT NULL,
                    PRIMARY KEY (name, alias),
                    FOREIGN KEY (name, version) REFERENCES model_versions(name, version) ON DELETE CASCADE
                )
            """,

            'logged_models': """
                CREATE TABLE IF NOT EXISTS logged_models (
                    model_uuid VARCHAR(36) PRIMARY KEY,
                    run_uuid VARCHAR(32) NOT NULL,
                    artifact_path VARCHAR(500) NOT NULL,
                    flavors TEXT,
                    FOREIGN KEY (run_uuid) REFERENCES runs(run_uuid)
                )
            """,

            'logged_model_tags': """
                CREATE TABLE IF NOT EXISTS logged_model_tags (
                    model_uuid VARCHAR(36) NOT NULL,
                    key VARCHAR(250) NOT NULL,
                    value VARCHAR(5000),
                    PRIMARY KEY (model_uuid, key),
                    FOREIGN KEY (model_uuid) REFERENCES logged_models(model_uuid) ON DELETE CASCADE
                )
            """,

            'logged_model_metrics': """
                CREATE TABLE IF NOT EXISTS logged_model_metrics (
                    model_uuid VARCHAR(36) NOT NULL,
                    key VARCHAR(250) NOT NULL,
                    value DOUBLE PRECISION NOT NULL,
                    timestamp BIGINT NOT NULL,
                    step BIGINT NOT NULL DEFAULT 0,
                    PRIMARY KEY (model_uuid, key),
                    FOREIGN KEY (model_uuid) REFERENCES logged_models(model_uuid) ON DELETE CASCADE
                )
            """,

            'logged_model_params': """
                CREATE TABLE IF NOT EXISTS logged_model_params (
                    model_uuid VARCHAR(36) NOT NULL,
                    key VARCHAR(250) NOT NULL,
                    value VARCHAR(500) NOT NULL,
                    PRIMARY KEY (model_uuid, key),
                    FOREIGN KEY (model_uuid) REFERENCES logged_models(model_uuid) ON DELETE CASCADE
                )
            """
        }

        for table_name, sql in tables.items():
            try:
                # Check if table exists first
                self.cur.execute(
                    "SELECT 1 FROM pg_tables WHERE tablename = %s AND schemaname = 'public'",
                    (table_name,)
                )
                exists = self.cur.fetchone() is not None

                if not exists:
                    self.cur.execute(sql)
                    created.append(table_name)
                    print(f"  Created table: {table_name}")
                else:
                    print(f"  [EXISTS] {table_name}")
            except Exception as e:
                print(f"  [ERROR] {table_name}: {e}")

        return created

    def create_dataset_tables(self) -> List[str]:
        """Create dataset and input tracking tables."""
        created = []

        tables = {
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
                    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id),
                    CONSTRAINT dataset_uuid_unique UNIQUE (dataset_uuid)
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
                    CONSTRAINT input_uuid_unique UNIQUE (input_uuid)
                )
            """,

            'input_tags': """
                CREATE TABLE IF NOT EXISTS input_tags (
                    input_uuid VARCHAR(36) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    value VARCHAR(500),
                    PRIMARY KEY (input_uuid, name)
                )
            """
        }

        for table_name, sql in tables.items():
            try:
                # Check if table exists first
                self.cur.execute(
                    "SELECT 1 FROM pg_tables WHERE tablename = %s AND schemaname = 'public'",
                    (table_name,)
                )
                exists = self.cur.fetchone() is not None

                if not exists:
                    self.cur.execute(sql)
                    created.append(table_name)
                    print(f"  Created table: {table_name}")
                else:
                    print(f"  [EXISTS] {table_name}")
            except Exception as e:
                print(f"  [ERROR] {table_name}: {e}")

        return created

    def create_trace_tables(self) -> List[str]:
        """Create trace telemetry tables."""
        created = []

        tables = {
            'trace_info': """
                CREATE TABLE IF NOT EXISTS trace_info (
                    request_id VARCHAR(50) PRIMARY KEY,
                    experiment_id INTEGER NOT NULL,
                    timestamp_ms BIGINT NOT NULL,
                    execution_time_ms BIGINT,
                    status VARCHAR(50) NOT NULL,
                    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
                )
            """,

            'trace_tags': """
                CREATE TABLE IF NOT EXISTS trace_tags (
                    request_id VARCHAR(50) NOT NULL,
                    key VARCHAR(250) NOT NULL,
                    value VARCHAR(8000),
                    PRIMARY KEY (request_id, key),
                    FOREIGN KEY (request_id) REFERENCES trace_info(request_id) ON DELETE CASCADE
                )
            """,

            'trace_request_metadata': """
                CREATE TABLE IF NOT EXISTS trace_request_metadata (
                    request_id VARCHAR(50) NOT NULL,
                    key VARCHAR(250) NOT NULL,
                    value VARCHAR(8000),
                    PRIMARY KEY (request_id, key),
                    FOREIGN KEY (request_id) REFERENCES trace_info(request_id) ON DELETE CASCADE
                )
            """
        }

        for table_name, sql in tables.items():
            try:
                # Check if table exists first
                self.cur.execute(
                    "SELECT 1 FROM pg_tables WHERE tablename = %s AND schemaname = 'public'",
                    (table_name,)
                )
                exists = self.cur.fetchone() is not None

                if not exists:
                    self.cur.execute(sql)
                    created.append(table_name)
                    print(f"  Created table: {table_name}")
                else:
                    print(f"  [EXISTS] {table_name}")
            except Exception as e:
                print(f"  [ERROR] {table_name}: {e}")

        return created

    def create_system_tables(self) -> List[str]:
        """Create system tables."""
        created = []

        tables = {
            'alembic_version': """
                CREATE TABLE IF NOT EXISTS alembic_version (
                    version_num VARCHAR(32) NOT NULL,
                    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                )
            """,

            'mlflow_integration': """
                CREATE TABLE IF NOT EXISTS mlflow_integration (
                    integration_id SERIAL PRIMARY KEY,
                    service_name VARCHAR(100) NOT NULL,
                    last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'active'
                )
            """
        }

        for table_name, sql in tables.items():
            try:
                # Check if table exists first
                self.cur.execute(
                    "SELECT 1 FROM pg_tables WHERE tablename = %s AND schemaname = 'public'",
                    (table_name,)
                )
                exists = self.cur.fetchone() is not None

                if not exists:
                    self.cur.execute(sql)
                    created.append(table_name)
                    print(f"  Created table: {table_name}")
                else:
                    print(f"  [EXISTS] {table_name}")
            except Exception as e:
                print(f"  [ERROR] {table_name}: {e}")

        # Insert MLflow schema version if not exists
        try:
            self.cur.execute("""
                INSERT INTO alembic_version (version_num)
                VALUES ('1a0cddfcaa16')
                ON CONFLICT (version_num) DO NOTHING
            """)
        except Exception as e:
            print(f"  [WARNING] Could not insert alembic version: {e}")

        return created

    def create_indexes(self):
        """Create performance indexes."""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_experiments_name ON experiments(name)",
            "CREATE INDEX IF NOT EXISTS idx_experiments_lifecycle_stage ON experiments(lifecycle_stage)",
            "CREATE INDEX IF NOT EXISTS idx_runs_experiment_id ON runs(experiment_id)",
            "CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status)",
            "CREATE INDEX IF NOT EXISTS idx_runs_start_time ON runs(start_time)",
            "CREATE INDEX IF NOT EXISTS idx_runs_lifecycle_stage ON runs(lifecycle_stage)",
            "CREATE INDEX IF NOT EXISTS idx_metrics_run_uuid ON metrics(run_uuid)",
            "CREATE INDEX IF NOT EXISTS idx_metrics_key ON metrics(key)",
            "CREATE INDEX IF NOT EXISTS idx_latest_metrics_run_uuid ON latest_metrics(run_uuid)",
            "CREATE INDEX IF NOT EXISTS idx_params_run_uuid ON params(run_uuid)",
            "CREATE INDEX IF NOT EXISTS idx_tags_run_uuid ON tags(run_uuid)",
            "CREATE INDEX IF NOT EXISTS idx_experiment_tags_experiment_id ON experiment_tags(experiment_id)",
            "CREATE INDEX IF NOT EXISTS idx_run_tags_run_uuid ON run_tags(run_uuid)",
            "CREATE INDEX IF NOT EXISTS idx_model_versions_run_id ON model_versions(run_id)",
            "CREATE INDEX IF NOT EXISTS idx_model_versions_name ON model_versions(name)",
            "CREATE INDEX IF NOT EXISTS idx_model_versions_stage ON model_versions(current_stage)",
            "CREATE INDEX IF NOT EXISTS idx_datasets_experiment_id ON datasets(experiment_id)",
            "CREATE INDEX IF NOT EXISTS idx_datasets_uuid ON datasets(dataset_uuid)",
            "CREATE INDEX IF NOT EXISTS idx_inputs_destination ON inputs(destination_type, destination_id)",
            "CREATE INDEX IF NOT EXISTS idx_inputs_source ON inputs(source_type, source_id)",
            "CREATE INDEX IF NOT EXISTS idx_input_tags_input_uuid ON input_tags(input_uuid)",
            "CREATE INDEX IF NOT EXISTS idx_trace_info_experiment_id ON trace_info(experiment_id)",
            "CREATE INDEX IF NOT EXISTS idx_trace_info_timestamp ON trace_info(timestamp_ms)"
        ]

        created = 0
        for idx_sql in indexes:
            try:
                self.cur.execute(idx_sql)
                if self.cur.statusmessage == 'CREATE INDEX':
                    created += 1
            except Exception as e:
                print(f"  [WARNING] Index creation: {e}")

        if created > 0:
            print(f"  Created {created} new indexes")
        else:
            print(f"  [EXISTS] All indexes already present")

    def verify_schema(self) -> Tuple[int, List[str]]:
        """Verify the schema is complete."""
        # Get all MLflow-related tables
        self.cur.execute("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
            AND (tablename LIKE '%experiment%' OR tablename LIKE '%run%'
                 OR tablename LIKE '%metric%' OR tablename LIKE '%model%'
                 OR tablename LIKE '%dataset%' OR tablename LIKE '%trace%'
                 OR tablename LIKE '%input%' OR tablename LIKE '%tag%'
                 OR tablename = 'alembic_version')
            ORDER BY tablename
        """)

        tables = [row[0] for row in self.cur.fetchall()]

        # Expected tables
        expected = [
            'alembic_version', 'datasets', 'experiment_tags', 'experiments',
            'input_tags', 'inputs', 'latest_metrics', 'logged_model_metrics',
            'logged_model_params', 'logged_model_tags', 'logged_models',
            'metrics', 'model_version_tags', 'model_versions', 'params',
            'registered_model_aliases', 'registered_model_tags',
            'registered_models', 'run_tags', 'runs', 'tags',
            'trace_info', 'trace_request_metadata', 'trace_tags'
        ]

        missing = [t for t in expected if t not in tables]

        return len(tables), missing

    def restore(self):
        """Execute full restoration."""
        print("MLFLOW DATABASE SCHEMA RESTORATION")
        print("=" * 60)

        try:
            self.connect()

            all_created = []

            print("\n1. Creating Core Tables...")
            created = self.create_core_tables()
            all_created.extend(created)

            print("\n2. Creating Tag Tables...")
            created = self.create_tag_tables()
            all_created.extend(created)

            print("\n3. Creating Model Registry Tables...")
            created = self.create_model_registry_tables()
            all_created.extend(created)

            print("\n4. Creating Dataset Tables...")
            created = self.create_dataset_tables()
            all_created.extend(created)

            print("\n5. Creating Trace Tables...")
            created = self.create_trace_tables()
            all_created.extend(created)

            print("\n6. Creating System Tables...")
            created = self.create_system_tables()
            all_created.extend(created)

            print("\n7. Creating Indexes...")
            self.create_indexes()

            # Commit all changes
            self.conn.commit()

            print("\n8. Verifying Schema...")
            table_count, missing = self.verify_schema()

            print(f"\nSUMMARY:")
            print(f"  Total MLflow tables: {table_count}")
            print(f"  Newly created: {len(all_created)}")

            if missing:
                print(f"  WARNING - Missing tables: {missing}")
            else:
                print("  SUCCESS - All required tables present!")

            if all_created:
                print(f"\nNewly created tables:")
                for table in all_created:
                    print(f"  - {table}")

            print("\nMLflow database restoration complete!")

        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()

        finally:
            self.disconnect()


def main():
    """Main execution."""
    restorer = MLflowSchemaRestorer()
    restorer.restore()

    # Test MLflow connectivity
    print("\n" + "=" * 60)
    print("TESTING MLFLOW CONNECTIVITY")
    print("=" * 60)

    try:
        import os
        import mlflow
        import yaml
        from pathlib import Path

        # Load settings for complete configuration
        settings_path = Path(__file__).parent.parent / 'settings.yaml'
        with open(settings_path) as f:
            config = yaml.safe_load(f)

        # Set AWS credentials for S3
        aws = config['credentials']['aws_basic']
        os.environ['AWS_ACCESS_KEY_ID'] = aws['access_key_id']
        os.environ['AWS_SECRET_ACCESS_KEY'] = aws['secret_access_key']
        os.environ['AWS_DEFAULT_REGION'] = aws['default_region']

        # Configure MLflow
        pg = config['credentials']['postgresql_primary']
        tracking_uri = f"postgresql://{pg['username']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['database']}"
        mlflow.set_tracking_uri(tracking_uri)

        # Test connection
        client = mlflow.tracking.MlflowClient()
        experiments = client.search_experiments()

        print(f"[OK] MLflow connection successful")
        print(f"[OK] Found {len(experiments)} experiments")
        print(f"[OK] Database schema verified")
        print("\nMLflow is ready for use!")

    except Exception as e:
        print(f"[WARNING] Could not test MLflow: {e}")
        print("Run 'python check_mlflow_pooled.py' to test MLflow connectivity")


if __name__ == "__main__":
    main()