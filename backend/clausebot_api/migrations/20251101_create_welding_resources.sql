-- Migration: Create welding_resources table for Pro feature
-- Date: 2025-11-01
-- Purpose: Store welding symbols and CWI resources articles for Pro users

-- Create welding_resources table
CREATE TABLE IF NOT EXISTS welding_resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    author TEXT,
    published_date TIMESTAMPTZ,
    category TEXT NOT NULL CHECK (category IN ('welding_symbols', 'cwi_resources')),
    summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_welding_resources_category ON welding_resources(category);
CREATE INDEX IF NOT EXISTS idx_welding_resources_created_at ON welding_resources(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_welding_resources_url ON welding_resources(url);

-- Enable full-text search on title and description
CREATE INDEX IF NOT EXISTS idx_welding_resources_search 
    ON welding_resources USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')));

-- Add Row Level Security (RLS)
ALTER TABLE welding_resources ENABLE ROW LEVEL SECURITY;

-- Policy: Allow authenticated users with Pro subscription to read
CREATE POLICY "Pro users can read welding resources"
    ON welding_resources
    FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM subscription_access
            WHERE subscription_access.user_id = auth.uid()
            AND subscription_access.access_level IN ('professional', 'enterprise')
            AND subscription_access.status = 'active'
        )
    );

-- Policy: Allow service role to insert/update (for data ingestion)
CREATE POLICY "Service role can manage welding resources"
    ON welding_resources
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Add trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_welding_resources_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_welding_resources_updated_at
    BEFORE UPDATE ON welding_resources
    FOR EACH ROW
    EXECUTE FUNCTION update_welding_resources_updated_at();

-- Add comments for documentation
COMMENT ON TABLE welding_resources IS 'Curated welding symbols and CWI resources articles for Pro users';
COMMENT ON COLUMN welding_resources.category IS 'Type of resource: welding_symbols or cwi_resources';
COMMENT ON COLUMN welding_resources.url IS 'Unique URL of the article';
COMMENT ON COLUMN welding_resources.title IS 'Article title';
COMMENT ON COLUMN welding_resources.description IS 'Article description';
COMMENT ON COLUMN welding_resources.summary IS 'AI-generated summary of the article';

