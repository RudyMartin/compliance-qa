-- ============================================================================
-- MLflow Database Schema Restoration Script
-- ============================================================================
-- Purpose: Restore complete MLflow schema with all tables, indexes, and constraints
-- Database: PostgreSQL
-- Usage: psql -U username -d database_name -f restore_mlflow.sql
-- ============================================================================

-- Start transaction for atomic execution
BEGIN;

-- ============================================================================
-- CORE EXPERIMENT AND RUN TABLES
-- ============================================================================

-- Experiments table (main experiment tracking)
CREATE TABLE IF NOT EXISTS experiments (
    experiment_id SERIAL PRIMARY KEY,
    name VARCHAR(256) UNIQUE NOT NULL,
    artifact_location VARCHAR(256),
    lifecycle_stage VARCHAR(32) DEFAULT 'active',
    creation_time BIGINT,
    last_update_time BIGINT
);

-- Runs table (individual ML runs)
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
);

-- ============================================================================
-- METRICS AND PARAMETERS
-- ============================================================================

-- Metrics table (numeric measurements)
CREATE TABLE IF NOT EXISTS metrics (
    key VARCHAR(250) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    timestamp BIGINT NOT NULL,
    run_uuid VARCHAR(32) NOT NULL,
    step BIGINT NOT NULL DEFAULT 0,
    is_nan BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (key, timestamp, step, run_uuid, value, is_nan),
    FOREIGN KEY (run_uuid) REFERENCES runs(run_uuid)
);

-- Latest metrics view table (for performance)
CREATE TABLE IF NOT EXISTS latest_metrics (
    key VARCHAR(250) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    timestamp BIGINT NOT NULL,
    run_uuid VARCHAR(32) NOT NULL,
    step BIGINT NOT NULL,
    is_nan BOOLEAN NOT NULL,
    PRIMARY KEY (key, run_uuid),
    FOREIGN KEY (run_uuid) REFERENCES runs(run_uuid)
);

-- Parameters table (hyperparameters)
CREATE TABLE IF NOT EXISTS params (
    key VARCHAR(250) NOT NULL,
    value VARCHAR(500) NOT NULL,
    run_uuid VARCHAR(32) NOT NULL,
    PRIMARY KEY (key, run_uuid),
    FOREIGN KEY (run_uuid) REFERENCES runs(run_uuid)
);

-- ============================================================================
-- TAG TABLES
-- ============================================================================

-- Experiment tags
CREATE TABLE IF NOT EXISTS experiment_tags (
    key VARCHAR(250) NOT NULL,
    value VARCHAR(5000),
    experiment_id INTEGER NOT NULL,
    PRIMARY KEY (key, experiment_id),
    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
);

-- Run tags
CREATE TABLE IF NOT EXISTS run_tags (
    key VARCHAR(250) NOT NULL,
    value VARCHAR(5000),
    run_uuid VARCHAR(32) NOT NULL,
    PRIMARY KEY (key, run_uuid),
    FOREIGN KEY (run_uuid) REFERENCES runs(run_uuid)
);

-- General tags table
CREATE TABLE IF NOT EXISTS tags (
    key VARCHAR(250) NOT NULL,
    value VARCHAR(5000),
    run_uuid VARCHAR(32) NOT NULL,
    PRIMARY KEY (key, run_uuid),
    FOREIGN KEY (run_uuid) REFERENCES runs(run_uuid)
);

-- ============================================================================
-- MODEL REGISTRY TABLES
-- ============================================================================

-- Registered models
CREATE TABLE IF NOT EXISTS registered_models (
    name VARCHAR(256) PRIMARY KEY,
    creation_time BIGINT,
    last_updated_time BIGINT,
    description VARCHAR(5000)
);

-- Model versions
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
    FOREIGN KEY (run_id) REFERENCES runs(run_uuid),
    FOREIGN KEY (name) REFERENCES registered_models(name) ON DELETE CASCADE
);

-- Model version tags
CREATE TABLE IF NOT EXISTS model_version_tags (
    name VARCHAR(256) NOT NULL,
    version INTEGER NOT NULL,
    key VARCHAR(250) NOT NULL,
    value VARCHAR(5000),
    PRIMARY KEY (name, version, key),
    FOREIGN KEY (name, version) REFERENCES model_versions(name, version) ON DELETE CASCADE
);

-- Registered model tags
CREATE TABLE IF NOT EXISTS registered_model_tags (
    name VARCHAR(256) NOT NULL,
    key VARCHAR(250) NOT NULL,
    value VARCHAR(5000),
    PRIMARY KEY (name, key),
    FOREIGN KEY (name) REFERENCES registered_models(name) ON DELETE CASCADE
);

-- Registered model aliases
CREATE TABLE IF NOT EXISTS registered_model_aliases (
    name VARCHAR(256) NOT NULL,
    alias VARCHAR(256) NOT NULL,
    version INTEGER NOT NULL,
    PRIMARY KEY (name, alias),
    FOREIGN KEY (name, version) REFERENCES model_versions(name, version) ON DELETE CASCADE
);

-- ============================================================================
-- LOGGED MODEL TABLES
-- ============================================================================

-- Logged models
CREATE TABLE IF NOT EXISTS logged_models (
    model_uuid VARCHAR(36) PRIMARY KEY,
    run_uuid VARCHAR(32) NOT NULL,
    artifact_path VARCHAR(500) NOT NULL,
    flavors TEXT,
    FOREIGN KEY (run_uuid) REFERENCES runs(run_uuid)
);

-- Logged model tags
CREATE TABLE IF NOT EXISTS logged_model_tags (
    model_uuid VARCHAR(36) NOT NULL,
    key VARCHAR(250) NOT NULL,
    value VARCHAR(5000),
    PRIMARY KEY (model_uuid, key),
    FOREIGN KEY (model_uuid) REFERENCES logged_models(model_uuid) ON DELETE CASCADE
);

-- Logged model metrics
CREATE TABLE IF NOT EXISTS logged_model_metrics (
    model_uuid VARCHAR(36) NOT NULL,
    key VARCHAR(250) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    timestamp BIGINT NOT NULL,
    step BIGINT NOT NULL DEFAULT 0,
    PRIMARY KEY (model_uuid, key),
    FOREIGN KEY (model_uuid) REFERENCES logged_models(model_uuid) ON DELETE CASCADE
);

-- Logged model params
CREATE TABLE IF NOT EXISTS logged_model_params (
    model_uuid VARCHAR(36) NOT NULL,
    key VARCHAR(250) NOT NULL,
    value VARCHAR(500) NOT NULL,
    PRIMARY KEY (model_uuid, key),
    FOREIGN KEY (model_uuid) REFERENCES logged_models(model_uuid) ON DELETE CASCADE
);

-- ============================================================================
-- DATASET AND INPUT TRACKING TABLES
-- ============================================================================

-- Datasets table
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
);

-- Inputs table (tracks data inputs)
CREATE TABLE IF NOT EXISTS inputs (
    input_uuid VARCHAR(36) NOT NULL,
    source_type VARCHAR(36) NOT NULL,
    source_id VARCHAR(36) NOT NULL,
    destination_type VARCHAR(36) NOT NULL,
    destination_id VARCHAR(36) NOT NULL,
    PRIMARY KEY (source_type, source_id, destination_type, destination_id),
    CONSTRAINT input_uuid_unique UNIQUE (input_uuid)
);

-- Input tags
CREATE TABLE IF NOT EXISTS input_tags (
    input_uuid VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    value VARCHAR(500),
    PRIMARY KEY (input_uuid, name)
);

-- ============================================================================
-- TRACE AND TELEMETRY TABLES
-- ============================================================================

-- Trace info
CREATE TABLE IF NOT EXISTS trace_info (
    request_id VARCHAR(50) PRIMARY KEY,
    experiment_id INTEGER NOT NULL,
    timestamp_ms BIGINT NOT NULL,
    execution_time_ms BIGINT,
    status VARCHAR(50) NOT NULL,
    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
);

-- Trace tags
CREATE TABLE IF NOT EXISTS trace_tags (
    request_id VARCHAR(50) NOT NULL,
    key VARCHAR(250) NOT NULL,
    value VARCHAR(8000),
    PRIMARY KEY (request_id, key),
    FOREIGN KEY (request_id) REFERENCES trace_info(request_id) ON DELETE CASCADE
);

-- Trace request metadata
CREATE TABLE IF NOT EXISTS trace_request_metadata (
    request_id VARCHAR(50) NOT NULL,
    key VARCHAR(250) NOT NULL,
    value VARCHAR(8000),
    PRIMARY KEY (request_id, key),
    FOREIGN KEY (request_id) REFERENCES trace_info(request_id) ON DELETE CASCADE
);

-- ============================================================================
-- MIGRATION TRACKING
-- ============================================================================

-- Alembic version tracking (for MLflow migrations)
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Insert current MLflow schema version if not exists
INSERT INTO alembic_version (version_num)
VALUES ('1a0cddfcaa16')
ON CONFLICT (version_num) DO NOTHING;

-- ============================================================================
-- CUSTOM TABLES FOR INTEGRATION
-- ============================================================================

-- MLflow integration tracking
CREATE TABLE IF NOT EXISTS mlflow_integration (
    integration_id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Experiment indexes
CREATE INDEX IF NOT EXISTS idx_experiments_name ON experiments(name);
CREATE INDEX IF NOT EXISTS idx_experiments_lifecycle_stage ON experiments(lifecycle_stage);

-- Run indexes
CREATE INDEX IF NOT EXISTS idx_runs_experiment_id ON runs(experiment_id);
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);
CREATE INDEX IF NOT EXISTS idx_runs_start_time ON runs(start_time);
CREATE INDEX IF NOT EXISTS idx_runs_lifecycle_stage ON runs(lifecycle_stage);

-- Metric indexes
CREATE INDEX IF NOT EXISTS idx_metrics_run_uuid ON metrics(run_uuid);
CREATE INDEX IF NOT EXISTS idx_metrics_key ON metrics(key);
CREATE INDEX IF NOT EXISTS idx_latest_metrics_run_uuid ON latest_metrics(run_uuid);

-- Parameter indexes
CREATE INDEX IF NOT EXISTS idx_params_run_uuid ON params(run_uuid);

-- Tag indexes
CREATE INDEX IF NOT EXISTS idx_tags_run_uuid ON tags(run_uuid);
CREATE INDEX IF NOT EXISTS idx_experiment_tags_experiment_id ON experiment_tags(experiment_id);
CREATE INDEX IF NOT EXISTS idx_run_tags_run_uuid ON run_tags(run_uuid);

-- Model indexes
CREATE INDEX IF NOT EXISTS idx_model_versions_run_id ON model_versions(run_id);
CREATE INDEX IF NOT EXISTS idx_model_versions_name ON model_versions(name);
CREATE INDEX IF NOT EXISTS idx_model_versions_stage ON model_versions(current_stage);

-- Dataset indexes
CREATE INDEX IF NOT EXISTS idx_datasets_experiment_id ON datasets(experiment_id);
CREATE INDEX IF NOT EXISTS idx_datasets_uuid ON datasets(dataset_uuid);

-- Input indexes
CREATE INDEX IF NOT EXISTS idx_inputs_destination ON inputs(destination_type, destination_id);
CREATE INDEX IF NOT EXISTS idx_inputs_source ON inputs(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_input_tags_input_uuid ON input_tags(input_uuid);

-- Trace indexes
CREATE INDEX IF NOT EXISTS idx_trace_info_experiment_id ON trace_info(experiment_id);
CREATE INDEX IF NOT EXISTS idx_trace_info_timestamp ON trace_info(timestamp_ms);

-- ============================================================================
-- FUNCTIONS FOR CLEANUP AND MAINTENANCE
-- ============================================================================

-- Function to clean up old runs
CREATE OR REPLACE FUNCTION cleanup_old_runs(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM runs
    WHERE lifecycle_stage = 'deleted'
    AND deleted_time < EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - INTERVAL '1 day' * days_to_keep)) * 1000;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get experiment statistics
CREATE OR REPLACE FUNCTION get_experiment_stats(exp_id INTEGER)
RETURNS TABLE(
    total_runs BIGINT,
    active_runs BIGINT,
    deleted_runs BIGINT,
    avg_duration DOUBLE PRECISION,
    last_run_time TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*) as total_runs,
        COUNT(*) FILTER (WHERE lifecycle_stage = 'active') as active_runs,
        COUNT(*) FILTER (WHERE lifecycle_stage = 'deleted') as deleted_runs,
        AVG(end_time - start_time) as avg_duration,
        TO_TIMESTAMP(MAX(start_time)/1000.0) as last_run_time
    FROM runs
    WHERE experiment_id = exp_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GRANTS (Uncomment and modify as needed)
-- ============================================================================

-- GRANT ALL ON ALL TABLES IN SCHEMA public TO mlflow_user;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO mlflow_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO mlflow_user;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Check that all required tables exist
DO $$
DECLARE
    required_tables TEXT[] := ARRAY[
        'experiments', 'runs', 'metrics', 'latest_metrics', 'params',
        'experiment_tags', 'run_tags', 'tags', 'registered_models',
        'model_versions', 'model_version_tags', 'registered_model_tags',
        'registered_model_aliases', 'logged_models', 'logged_model_tags',
        'logged_model_metrics', 'logged_model_params', 'datasets',
        'inputs', 'input_tags', 'trace_info', 'trace_tags',
        'trace_request_metadata', 'alembic_version'
    ];
    missing_tables TEXT[] := ARRAY[]::TEXT[];
    tbl TEXT;
BEGIN
    FOREACH tbl IN ARRAY required_tables
    LOOP
        IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = tbl AND schemaname = 'public') THEN
            missing_tables := array_append(missing_tables, tbl);
        END IF;
    END LOOP;

    IF array_length(missing_tables, 1) > 0 THEN
        RAISE WARNING 'Missing tables: %', missing_tables;
    ELSE
        RAISE NOTICE 'All MLflow tables successfully created!';
    END IF;
END $$;

-- Commit transaction
COMMIT;

-- ============================================================================
-- POST-RESTORATION VERIFICATION QUERIES
-- ============================================================================

-- Count tables created
SELECT COUNT(*) as table_count FROM pg_tables
WHERE schemaname = 'public'
AND (tablename LIKE '%experiment%' OR tablename LIKE '%run%'
     OR tablename LIKE '%metric%' OR tablename LIKE '%model%'
     OR tablename LIKE '%dataset%' OR tablename LIKE '%trace%');

-- Show table sizes
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
AND (tablename LIKE '%experiment%' OR tablename LIKE '%run%'
     OR tablename LIKE '%metric%' OR tablename LIKE '%model%')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- ============================================================================
-- END OF RESTORATION SCRIPT
-- ============================================================================