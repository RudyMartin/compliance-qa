-- TidyLLM Heiros Database Indexes
-- Performance optimization indexes for all Heiros tables

-- =============================================================================
-- PRIMARY PERFORMANCE INDEXES
-- =============================================================================

-- Session indexes
CREATE INDEX idx_heiros_sessions_user_id ON heiros_sessions(user_id);
CREATE INDEX idx_heiros_sessions_topic ON heiros_sessions(topic);
CREATE INDEX idx_heiros_sessions_created_at ON heiros_sessions(created_at);
CREATE INDEX idx_heiros_sessions_status ON heiros_sessions(status);
CREATE INDEX idx_heiros_sessions_completed_at ON heiros_sessions(completed_at);

-- Paper indexes
CREATE INDEX idx_heiros_papers_arxiv_id ON heiros_papers(arxiv_id);
CREATE INDEX idx_heiros_papers_composite_score ON heiros_papers(composite_score DESC);
CREATE INDEX idx_heiros_papers_publication_date ON heiros_papers(publication_date DESC);
CREATE INDEX idx_heiros_papers_y_score ON heiros_papers(y_score DESC);
CREATE INDEX idx_heiros_papers_r_score ON heiros_papers(r_score DESC);
CREATE INDEX idx_heiros_papers_s_score ON heiros_papers(s_score DESC);
CREATE INDEX idx_heiros_papers_n_score ON heiros_papers(n_score DESC);
CREATE INDEX idx_heiros_papers_macro_quality ON heiros_papers(macro_quality DESC);

-- Session-paper relationship indexes
CREATE INDEX idx_heiros_session_papers_session_id ON heiros_session_papers(session_id);
CREATE INDEX idx_heiros_session_papers_paper_id ON heiros_session_papers(paper_id);
CREATE INDEX idx_heiros_session_papers_rank_position ON heiros_session_papers(rank_position);
CREATE INDEX idx_heiros_session_papers_bt_strategy ON heiros_session_papers(bt_strategy_used);

-- =============================================================================
-- METRICS INDEXES
-- =============================================================================

-- Performance metrics indexes
CREATE INDEX idx_heiros_performance_metrics_session_id ON heiros_performance_metrics(session_id);
CREATE INDEX idx_heiros_performance_metrics_node_name ON heiros_performance_metrics(node_name);
CREATE INDEX idx_heiros_performance_metrics_status ON heiros_performance_metrics(status);
CREATE INDEX idx_heiros_performance_metrics_execution_time ON heiros_performance_metrics(execution_time_ms);
CREATE INDEX idx_heiros_performance_metrics_created_at ON heiros_performance_metrics(created_at);

-- Quality metrics indexes
CREATE INDEX idx_heiros_quality_metrics_session_id ON heiros_quality_metrics(session_id);
CREATE INDEX idx_heiros_quality_metrics_avg_r_score ON heiros_quality_metrics(avg_r_score DESC);
CREATE INDEX idx_heiros_quality_metrics_avg_s_score ON heiros_quality_metrics(avg_s_score DESC);
CREATE INDEX idx_heiros_quality_metrics_avg_n_score ON heiros_quality_metrics(avg_n_score DESC);
CREATE INDEX idx_heiros_quality_metrics_avg_macro_quality ON heiros_quality_metrics(avg_macro_quality DESC);
CREATE INDEX idx_heiros_quality_metrics_diversity_score ON heiros_quality_metrics(diversity_score DESC);

-- Adaptive threshold indexes
CREATE INDEX idx_heiros_adaptive_thresholds_session_id ON heiros_adaptive_thresholds(session_id);
CREATE INDEX idx_heiros_adaptive_thresholds_strategy ON heiros_adaptive_thresholds(selected_strategy);
CREATE INDEX idx_heiros_adaptive_thresholds_effectiveness ON heiros_adaptive_thresholds(strategy_effectiveness DESC);

-- =============================================================================
-- USER INTERACTION INDEXES
-- =============================================================================

-- User interaction indexes
CREATE INDEX idx_heiros_user_interactions_user_id ON heiros_user_interactions(user_id);
CREATE INDEX idx_heiros_user_interactions_session_id ON heiros_user_interactions(session_id);
CREATE INDEX idx_heiros_user_interactions_type ON heiros_user_interactions(interaction_type);
CREATE INDEX idx_heiros_user_interactions_satisfaction ON heiros_user_interactions(satisfaction_rating);
CREATE INDEX idx_heiros_user_interactions_created_at ON heiros_user_interactions(created_at);

-- Context rating indexes
CREATE INDEX idx_heiros_context_ratings_user_id ON heiros_context_ratings(user_id);
CREATE INDEX idx_heiros_context_ratings_session_id ON heiros_context_ratings(session_id);
CREATE INDEX idx_heiros_context_ratings_quality ON heiros_context_ratings(context_quality_rating);
CREATE INDEX idx_heiros_context_ratings_relevance ON heiros_context_ratings(relevance_rating);
CREATE INDEX idx_heiros_context_ratings_coverage ON heiros_context_ratings(coverage_rating);

-- =============================================================================
-- VECTOR INDEXES (pgvector)
-- =============================================================================

-- Paper embedding indexes
CREATE INDEX idx_heiros_paper_embeddings_title ON heiros_paper_embeddings USING ivfflat (title_embedding vector_cosine_ops);
CREATE INDEX idx_heiros_paper_embeddings_abstract ON heiros_paper_embeddings USING ivfflat (abstract_embedding vector_cosine_ops);
CREATE INDEX idx_heiros_paper_embeddings_combined ON heiros_paper_embeddings USING ivfflat (combined_embedding vector_cosine_ops);
CREATE INDEX idx_heiros_paper_embeddings_model ON heiros_paper_embeddings(embedding_model);

-- Query embedding indexes
CREATE INDEX idx_heiros_query_embeddings_session_id ON heiros_query_embeddings(session_id);
CREATE INDEX idx_heiros_query_embeddings_query ON heiros_query_embeddings USING ivfflat (query_embedding vector_cosine_ops);
CREATE INDEX idx_heiros_query_embeddings_model ON heiros_query_embeddings(embedding_model);

-- =============================================================================
-- ANALYTICS INDEXES
-- =============================================================================

-- Analytics summary indexes
CREATE INDEX idx_heiros_analytics_summary_date ON heiros_analytics_summary(date);
CREATE INDEX idx_heiros_analytics_summary_quality_score ON heiros_analytics_summary(avg_quality_score DESC);
CREATE INDEX idx_heiros_analytics_summary_satisfaction ON heiros_analytics_summary(avg_user_satisfaction DESC);
CREATE INDEX idx_heiros_analytics_summary_success_rate ON heiros_analytics_summary(success_rate DESC);

-- Strategy performance indexes
CREATE INDEX idx_heiros_strategy_performance_name ON heiros_strategy_performance(strategy_name);
CREATE INDEX idx_heiros_strategy_performance_effectiveness ON heiros_strategy_performance(avg_effectiveness DESC);
CREATE INDEX idx_heiros_strategy_performance_quality ON heiros_strategy_performance(avg_quality_score DESC);
CREATE INDEX idx_heiros_strategy_performance_success_rate ON heiros_strategy_performance(success_rate DESC);
CREATE INDEX idx_heiros_strategy_performance_usage ON heiros_strategy_performance(usage_count DESC);
CREATE INDEX idx_heiros_strategy_performance_last_used ON heiros_strategy_performance(last_used);

-- =============================================================================
-- UTILITY TABLE INDEXES
-- =============================================================================

-- Macro pattern indexes
CREATE INDEX idx_heiros_macro_patterns_name ON heiros_macro_patterns(pattern_name);
CREATE INDEX idx_heiros_macro_patterns_frequency ON heiros_macro_patterns(usage_frequency DESC);
CREATE INDEX idx_heiros_macro_patterns_success_rate ON heiros_macro_patterns(success_rate DESC);
CREATE INDEX idx_heiros_macro_patterns_complexity ON heiros_macro_patterns(avg_complexity);

-- Corpus statistics indexes
CREATE INDEX idx_heiros_corpus_statistics_name ON heiros_corpus_statistics(corpus_name);
CREATE INDEX idx_heiros_corpus_statistics_avg_y_score ON heiros_corpus_statistics(avg_y_score DESC);
CREATE INDEX idx_heiros_corpus_statistics_avg_r_score ON heiros_corpus_statistics(avg_r_score DESC);
CREATE INDEX idx_heiros_corpus_statistics_avg_s_score ON heiros_corpus_statistics(avg_s_score DESC);
CREATE INDEX idx_heiros_corpus_statistics_avg_n_score ON heiros_corpus_statistics(avg_n_score DESC);

-- Error log indexes
CREATE INDEX idx_heiros_error_logs_session_id ON heiros_error_logs(session_id);
CREATE INDEX idx_heiros_error_logs_type ON heiros_error_logs(error_type);
CREATE INDEX idx_heiros_error_logs_severity ON heiros_error_logs(severity);
CREATE INDEX idx_heiros_error_logs_created_at ON heiros_error_logs(created_at);

-- =============================================================================
-- COMPOSITE INDEXES FOR COMMON QUERIES
-- =============================================================================

-- Session performance composite index
CREATE INDEX idx_heiros_sessions_performance ON heiros_sessions(user_id, created_at, status);

-- Paper quality composite index
CREATE INDEX idx_heiros_papers_quality ON heiros_papers(composite_score DESC, publication_date DESC);

-- Metrics composite index
CREATE INDEX idx_heiros_metrics_session_time ON heiros_performance_metrics(session_id, created_at);

-- User satisfaction composite index
CREATE INDEX idx_heiros_user_satisfaction_composite ON heiros_user_interactions(user_id, interaction_type, satisfaction_rating);

-- Strategy effectiveness composite index
CREATE INDEX idx_heiros_strategy_effectiveness_composite ON heiros_strategy_performance(strategy_name, avg_effectiveness DESC, usage_count DESC);

-- =============================================================================
-- PARTIAL INDEXES FOR SPECIFIC FILTERING
-- =============================================================================

-- Active sessions only
CREATE INDEX idx_heiros_sessions_active ON heiros_sessions(user_id, created_at) WHERE status = 'active';

-- High-quality papers only
CREATE INDEX idx_heiros_papers_high_quality ON heiros_papers(paper_id, composite_score) WHERE composite_score >= 0.7;

-- Successful strategies only
CREATE INDEX idx_heiros_strategy_successful ON heiros_strategy_performance(strategy_name, success_rate) WHERE success_rate >= 0.8;

-- Recent errors only
CREATE INDEX idx_heiros_errors_recent ON heiros_error_logs(session_id, error_type) WHERE created_at >= NOW() - INTERVAL '7 days';

-- =============================================================================
-- GIN INDEXES FOR JSONB FIELDS
-- =============================================================================

-- JSONB field indexes
CREATE INDEX idx_heiros_sessions_requirements_gin ON heiros_sessions USING GIN (requirements);
CREATE INDEX idx_heiros_user_interactions_data_gin ON heiros_user_interactions USING GIN (interaction_data);
CREATE INDEX idx_heiros_macro_patterns_description_gin ON heiros_macro_patterns USING GIN (pattern_description);
CREATE INDEX idx_heiros_corpus_statistics_quality_dist_gin ON heiros_corpus_statistics USING GIN (quality_distribution);
CREATE INDEX idx_heiros_error_logs_context_gin ON heiros_error_logs USING GIN (context_data);

-- =============================================================================
-- BRIN INDEXES FOR LARGE TIME-SERIES TABLES
-- =============================================================================

-- Time-series BRIN indexes for large tables
CREATE INDEX idx_heiros_performance_metrics_time_brin ON heiros_performance_metrics USING BRIN (created_at);
CREATE INDEX idx_heiros_user_interactions_time_brin ON heiros_user_interactions USING BRIN (created_at);
CREATE INDEX idx_heiros_error_logs_time_brin ON heiros_error_logs USING BRIN (created_at);

-- =============================================================================
-- INDEX MAINTENANCE FUNCTIONS
-- =============================================================================

-- Function to analyze all Heiros indexes
CREATE OR REPLACE FUNCTION analyze_heiros_indexes()
RETURNS TABLE (
    table_name TEXT,
    index_name TEXT,
    index_size TEXT,
    index_usage_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        schemaname::TEXT,
        indexname::TEXT,
        pg_size_pretty(pg_relation_size(indexname::regclass))::TEXT,
        idx_scan
    FROM pg_stat_user_indexes 
    WHERE schemaname = 'public' 
    AND indexname LIKE 'idx_heiros_%'
    ORDER BY pg_relation_size(indexname::regclass) DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get index statistics
CREATE OR REPLACE FUNCTION get_heiros_index_stats()
RETURNS TABLE (
    table_name TEXT,
    total_indexes INTEGER,
    total_index_size TEXT,
    avg_index_size TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.table_name::TEXT,
        COUNT(i.indexname)::INTEGER,
        pg_size_pretty(SUM(pg_relation_size(i.indexname::regclass)))::TEXT,
        pg_size_pretty(AVG(pg_relation_size(i.indexname::regclass)))::TEXT
    FROM pg_tables t
    LEFT JOIN pg_stat_user_indexes i ON t.tablename = i.relname
    WHERE t.schemaname = 'public' 
    AND t.tablename LIKE 'heiros_%'
    AND (i.indexname IS NULL OR i.indexname LIKE 'idx_heiros_%')
    GROUP BY t.table_name
    ORDER BY SUM(pg_relation_size(i.indexname::regclass)) DESC;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- INDEX COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON INDEX idx_heiros_sessions_performance IS 'Optimized for session performance queries';
COMMENT ON INDEX idx_heiros_papers_high_quality IS 'Fast access to high-quality papers only';
COMMENT ON INDEX idx_heiros_papers_quality IS 'Optimized for quality-based paper selection';
COMMENT ON INDEX idx_heiros_paper_embeddings_combined IS 'Vector similarity search for paper embeddings';
COMMENT ON INDEX idx_heiros_query_embeddings_query IS 'Vector similarity search for query embeddings';
COMMENT ON INDEX idx_heiros_strategy_effectiveness_composite IS 'Optimized for strategy performance analysis';
COMMENT ON INDEX idx_heiros_user_satisfaction_composite IS 'Optimized for user satisfaction analysis';
COMMENT ON INDEX idx_heiros_errors_recent IS 'Fast access to recent error logs';
