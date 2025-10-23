-- TidyLLM Heiros Database Schema
-- Create all tables for the TidyLLM Heiros system

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to calculate composite score
CREATE OR REPLACE FUNCTION calculate_composite_score(
    y_score DECIMAL,
    r_score DECIMAL,
    s_score DECIMAL,
    n_score DECIMAL,
    macro_quality DECIMAL
) RETURNS DECIMAL AS $$
BEGIN
    RETURN (y_score * 0.2 + r_score * 0.3 + s_score * 0.2 + n_score * 0.2 + macro_quality * 0.1);
END;
$$ LANGUAGE plpgsql;

-- 1. Core session management
CREATE TABLE heiros_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    topic VARCHAR(500) NOT NULL,
    requirements JSONB,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    execution_time_ms INTEGER,
    papers_analyzed INTEGER,
    papers_selected INTEGER
);

-- 2. Paper storage and metadata
CREATE TABLE heiros_papers (
    paper_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    arxiv_id VARCHAR(50) UNIQUE,
    title TEXT NOT NULL,
    abstract TEXT,
    authors TEXT[],
    categories TEXT[],
    publication_date DATE,
    y_score DECIMAL(4,3),
    r_score DECIMAL(4,3),
    s_score DECIMAL(4,3),
    n_score DECIMAL(4,3),
    macro_quality DECIMAL(4,3),
    composite_score DECIMAL(4,3),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. Session-paper relationships
CREATE TABLE heiros_session_papers (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES heiros_sessions(session_id) ON DELETE CASCADE,
    paper_id UUID REFERENCES heiros_papers(paper_id) ON DELETE CASCADE,
    selection_reason VARCHAR(100),
    rank_position INTEGER,
    bt_strategy_used VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. Performance metrics tracking
CREATE TABLE heiros_performance_metrics (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES heiros_sessions(session_id) ON DELETE CASCADE,
    node_name VARCHAR(100),
    execution_time_ms INTEGER,
    status VARCHAR(20),
    error_message TEXT,
    bt_path TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. Quality metrics aggregation
CREATE TABLE heiros_quality_metrics (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES heiros_sessions(session_id) ON DELETE CASCADE,
    avg_r_score DECIMAL(4,3),
    avg_s_score DECIMAL(4,3),
    avg_n_score DECIMAL(4,3),
    avg_macro_quality DECIMAL(4,3),
    diversity_score DECIMAL(4,3),
    relevance_coverage DECIMAL(4,3),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 6. Adaptive threshold management
CREATE TABLE heiros_adaptive_thresholds (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES heiros_sessions(session_id) ON DELETE CASCADE,
    initial_r_median DECIMAL(4,3),
    selected_strategy VARCHAR(50),
    threshold_r_min DECIMAL(4,3),
    threshold_s_max DECIMAL(4,3),
    threshold_n_min DECIMAL(4,3),
    strategy_effectiveness DECIMAL(4,3),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. User interaction tracking
CREATE TABLE heiros_user_interactions (
    id SERIAL PRIMARY KEY,
    user_id UUID,
    session_id UUID REFERENCES heiros_sessions(session_id) ON DELETE CASCADE,
    interaction_type VARCHAR(50),
    interaction_data JSONB,
    satisfaction_rating INTEGER CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5),
    feedback_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 8. Context quality ratings
CREATE TABLE heiros_context_ratings (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES heiros_sessions(session_id) ON DELETE CASCADE,
    user_id UUID,
    context_quality_rating INTEGER CHECK (context_quality_rating >= 1 AND context_quality_rating <= 5),
    relevance_rating INTEGER CHECK (relevance_rating >= 1 AND relevance_rating <= 5),
    coverage_rating INTEGER CHECK (coverage_rating >= 1 AND coverage_rating <= 5),
    comments TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 9. Paper embeddings (pgvector)
CREATE TABLE heiros_paper_embeddings (
    paper_id UUID PRIMARY KEY REFERENCES heiros_papers(paper_id) ON DELETE CASCADE,
    title_embedding vector(1536),
    abstract_embedding vector(1536),
    combined_embedding vector(1536),
    embedding_model VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 10. Query embeddings (pgvector)
CREATE TABLE heiros_query_embeddings (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES heiros_sessions(session_id) ON DELETE CASCADE,
    query_text TEXT,
    query_embedding vector(1536),
    embedding_model VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 11. Analytics summary
CREATE TABLE heiros_analytics_summary (
    id SERIAL PRIMARY KEY,
    date DATE,
    total_sessions INTEGER,
    avg_execution_time_ms INTEGER,
    avg_quality_score DECIMAL(4,3),
    avg_user_satisfaction DECIMAL(4,3),
    success_rate DECIMAL(4,3),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 12. Strategy performance tracking
CREATE TABLE heiros_strategy_performance (
    id SERIAL PRIMARY KEY,
    strategy_name VARCHAR(50),
    usage_count INTEGER,
    avg_effectiveness DECIMAL(4,3),
    avg_quality_score DECIMAL(4,3),
    success_rate DECIMAL(4,3),
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 13. Macro patterns and usage
CREATE TABLE heiros_macro_patterns (
    id SERIAL PRIMARY KEY,
    pattern_name VARCHAR(100),
    pattern_description TEXT,
    usage_frequency INTEGER,
    success_rate DECIMAL(4,3),
    avg_complexity DECIMAL(4,3),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 14. Corpus statistics
CREATE TABLE heiros_corpus_statistics (
    id SERIAL PRIMARY KEY,
    corpus_name VARCHAR(100),
    total_papers INTEGER,
    avg_y_score DECIMAL(4,3),
    avg_r_score DECIMAL(4,3),
    avg_s_score DECIMAL(4,3),
    avg_n_score DECIMAL(4,3),
    quality_distribution JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 15. Error logging and debugging
CREATE TABLE heiros_error_logs (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES heiros_sessions(session_id) ON DELETE CASCADE,
    error_type VARCHAR(50),
    error_message TEXT,
    stack_trace TEXT,
    context_data JSONB,
    severity VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add triggers for updated_at columns
CREATE TRIGGER update_heiros_papers_updated_at 
    BEFORE UPDATE ON heiros_papers 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_heiros_macro_patterns_updated_at 
    BEFORE UPDATE ON heiros_macro_patterns 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_heiros_corpus_statistics_updated_at 
    BEFORE UPDATE ON heiros_corpus_statistics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE heiros_sessions IS 'Core session management for Heiros workflows';
COMMENT ON TABLE heiros_papers IS 'Paper storage with Y=R+S+N scoring';
COMMENT ON TABLE heiros_session_papers IS 'Many-to-many relationship between sessions and papers';
COMMENT ON TABLE heiros_performance_metrics IS 'Performance tracking for BT nodes and workflows';
COMMENT ON TABLE heiros_quality_metrics IS 'Aggregated quality metrics per session';
COMMENT ON TABLE heiros_adaptive_thresholds IS 'Dynamic threshold management for paper selection';
COMMENT ON TABLE heiros_user_interactions IS 'User interaction and feedback tracking';
COMMENT ON TABLE heiros_context_ratings IS 'User ratings for context quality assessment';
COMMENT ON TABLE heiros_paper_embeddings IS 'Vector embeddings for paper similarity search';
COMMENT ON TABLE heiros_query_embeddings IS 'Vector embeddings for query processing';
COMMENT ON TABLE heiros_analytics_summary IS 'Daily analytics aggregation';
COMMENT ON TABLE heiros_strategy_performance IS 'Strategy effectiveness tracking';
COMMENT ON TABLE heiros_macro_patterns IS 'Macro usage patterns and performance';
COMMENT ON TABLE heiros_corpus_statistics IS 'Corpus-level statistics for normalization';
COMMENT ON TABLE heiros_error_logs IS 'Error tracking and debugging information';
