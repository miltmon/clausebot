-- ClauseBot Incidents Table Schema for Supabase
-- Execute this in your Supabase SQL Editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create incidents table
CREATE TABLE IF NOT EXISTS incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL CHECK (source IN ('cursor', 'windsurf', 'exa', 'manual')),
    title TEXT NOT NULL CHECK (length(title) >= 3 AND length(title) <= 200),
    description TEXT,
    severity TEXT NOT NULL DEFAULT 'low' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    confidence DECIMAL(3,2) NOT NULL DEFAULT 0 CHECK (confidence >= 0 AND confidence <= 1),
    payload JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_incidents_created_at ON incidents(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_incidents_source ON incidents(source);
CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity);
CREATE INDEX IF NOT EXISTS idx_incidents_title_trgm ON incidents USING gin (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_incidents_description_trgm ON incidents USING gin (description gin_trgm_ops);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_incidents_updated_at 
    BEFORE UPDATE ON incidents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;

-- Policy: Allow public read access
CREATE POLICY "Allow public read access" ON incidents
    FOR SELECT USING (true);

-- Policy: Allow service role full access
CREATE POLICY "Allow service role full access" ON incidents
    FOR ALL USING (auth.role() = 'service_role');

-- Policy: Allow authenticated users to insert
CREATE POLICY "Allow authenticated insert" ON incidents
    FOR INSERT WITH CHECK (auth.role() = 'authenticated' OR auth.role() = 'service_role');

-- Create search function using pg_trgm
CREATE OR REPLACE FUNCTION search_incidents(search_query TEXT, result_limit INTEGER DEFAULT 25)
RETURNS TABLE (
    id UUID,
    source TEXT,
    title TEXT,
    description TEXT,
    severity TEXT,
    confidence DECIMAL,
    payload JSONB,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    similarity_score REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        i.id,
        i.source,
        i.title,
        i.description,
        i.severity,
        i.confidence,
        i.payload,
        i.created_at,
        i.updated_at,
        GREATEST(
            similarity(i.title, search_query),
            COALESCE(similarity(i.description, search_query), 0)
        ) as similarity_score
    FROM incidents i
    WHERE 
        i.title % search_query 
        OR (i.description IS NOT NULL AND i.description % search_query)
    ORDER BY similarity_score DESC, i.created_at DESC
    LIMIT result_limit;
END;
$$ LANGUAGE plpgsql;

-- Create model usage table for cost tracking
CREATE TABLE IF NOT EXISTS model_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    estimated_cost_usd DECIMAL(10,6) NOT NULL,
    request_id TEXT,
    user_id TEXT,
    endpoint TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for model usage
CREATE INDEX IF NOT EXISTS idx_model_usage_timestamp ON model_usage(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_model_usage_provider ON model_usage(provider);
CREATE INDEX IF NOT EXISTS idx_model_usage_user_id ON model_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_model_usage_endpoint ON model_usage(endpoint);

-- RLS policies for model usage
ALTER TABLE model_usage ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read model usage" ON model_usage
    FOR SELECT USING (true);

CREATE POLICY "Allow service role full access model usage" ON model_usage
    FOR ALL USING (auth.role() = 'service_role');

-- Insert sample data for testing
INSERT INTO incidents (source, title, description, severity, confidence, payload) VALUES
('cursor', 'Chrome RESULT_CODE_HUNG detected', 'GPU driver issue causing Chrome tab hangs', 'high', 0.85, '{"gpu_driver": "31.0.101.4826", "chrome_version": "118.0.5993.88"}'),
('manual', 'Welding procedure validation needed', 'AWS D1.1 Section 6.1.4 compliance check required', 'medium', 0.75, '{"section": "6.1.4", "standard": "AWS D1.1"}'),
('exa', 'New ASME compliance update detected', 'ASME Section IX revision impacts current procedures', 'critical', 0.92, '{"standard": "ASME Section IX", "impact_sections": ["QW-200", "QW-300"]}}')
ON CONFLICT DO NOTHING;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON incidents TO service_role;
GRANT SELECT ON incidents TO anon, authenticated;
GRANT INSERT ON incidents TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION search_incidents TO anon, authenticated, service_role;

-- Verify setup
SELECT 'Schema setup complete. Incidents table created with ' || COUNT(*) || ' sample records.' as status
FROM incidents;
