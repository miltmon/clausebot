-- supabase_pgvector_rag.sql
-- ClauseBot RAG Schema for Supabase
-- Run this in Supabase SQL Editor with service role privileges

-- 1) Enable required extensions
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2) Clause embeddings table
CREATE TABLE IF NOT EXISTS clause_embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clause_id TEXT NOT NULL UNIQUE,           -- e.g., "aws_d1.1_2020_4.8.3"
  standard TEXT NOT NULL,                   -- "AWS D1.1:2020"
  section TEXT NOT NULL,                    -- "4.8.3"
  parent_section TEXT,                      -- "4.8"
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  chunk_type TEXT NOT NULL CHECK (chunk_type IN ('paragraph','table','figure','definition')),
  embedding vector(3072),                   -- text-embedding-3-large dimension
  effective_date DATE NOT NULL DEFAULT now(),
  page_number INTEGER,
  jurisdiction TEXT DEFAULT 'US',
  keywords TEXT[],
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- 3) Indexes for vector search + hybrid fallback
-- IVFFlat index for semantic similarity search
CREATE INDEX IF NOT EXISTS idx_clause_embeddings_embedding_ivfflat
  ON clause_embeddings USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- Full-text search index for hybrid search
CREATE INDEX IF NOT EXISTS idx_clause_embeddings_content_fts
  ON clause_embeddings USING gin(to_tsvector('english', title || ' ' || content));

-- Filter indexes for common queries
CREATE INDEX IF NOT EXISTS idx_clause_embeddings_standard ON clause_embeddings(standard);
CREATE INDEX IF NOT EXISTS idx_clause_embeddings_section ON clause_embeddings(section);
CREATE INDEX IF NOT EXISTS idx_clause_embeddings_effective_date ON clause_embeddings(effective_date DESC);
CREATE INDEX IF NOT EXISTS idx_clause_embeddings_keywords ON clause_embeddings USING gin(keywords);

-- 4) Citation logging table (audit trail)
CREATE TABLE IF NOT EXISTS chat_citations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT NOT NULL,
  query TEXT NOT NULL,
  clause_id TEXT NOT NULL REFERENCES clause_embeddings(clause_id),
  similarity_score FLOAT NOT NULL,
  used_in_response BOOLEAN DEFAULT TRUE,
  user_feedback TEXT CHECK (user_feedback IN ('helpful','not_helpful','incorrect')),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_chat_citations_session ON chat_citations(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_citations_clause ON chat_citations(clause_id);
CREATE INDEX IF NOT EXISTS idx_chat_citations_created ON chat_citations(created_at DESC);

-- 5) Hybrid search function: semantic similarity + full-text ranking
CREATE OR REPLACE FUNCTION search_clauses_hybrid(
  query_embedding vector(3072),
  query_text TEXT,
  match_threshold FLOAT DEFAULT 0.60,
  match_count INT DEFAULT 5,
  filter_standard TEXT DEFAULT NULL
)
RETURNS TABLE (
  clause_id TEXT,
  standard TEXT,
  section TEXT,
  title TEXT,
  content TEXT,
  similarity FLOAT,
  rank FLOAT
)
LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT
    ce.clause_id,
    ce.standard,
    ce.section,
    ce.title,
    ce.content,
    1 - (ce.embedding <=> query_embedding) AS similarity,
    ts_rank(to_tsvector('english', ce.title || ' ' || ce.content), plainto_tsquery(query_text)) AS rank
  FROM clause_embeddings ce
  WHERE
    (1 - (ce.embedding <=> query_embedding)) > match_threshold
    AND (filter_standard IS NULL OR ce.standard = filter_standard)
  ORDER BY
    -- Weighted combination: 75% semantic, 25% text rank
    ((1 - (ce.embedding <=> query_embedding)) * 0.75) + 
    (ts_rank(to_tsvector('english', ce.title || ' ' || ce.content), plainto_tsquery(query_text)) * 0.25) DESC
  LIMIT match_count;
END;
$$;

-- 6) Helper function for health checks (optional)
CREATE OR REPLACE FUNCTION count_clause_embeddings()
RETURNS TABLE (count BIGINT)
LANGUAGE sql AS $$
  SELECT COUNT(*) FROM clause_embeddings;
$$;

-- 7) Grant permissions (adjust for your Supabase setup)
-- If using RLS, configure policies as needed
-- For service role access, no additional grants required

COMMENT ON TABLE clause_embeddings IS 'Stores clause content and embeddings for RAG retrieval';
COMMENT ON TABLE chat_citations IS 'Audit log of RAG queries and retrieved clauses';
COMMENT ON FUNCTION search_clauses_hybrid IS 'Hybrid semantic + full-text search for compliance clauses';

