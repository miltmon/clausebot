-- clause_embeddings_nlm_migration.sql
-- Adds NotebookLM SSOT metadata fields to existing clause_embeddings table
-- Run after supabase_pgvector_rag.sql

-- Add NLM SSOT metadata columns to existing clause_embeddings table
ALTER TABLE clause_embeddings 
ADD COLUMN IF NOT EXISTS nlm_source_id TEXT,
ADD COLUMN IF NOT EXISTS nlm_timestamp TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS code_reference_primary TEXT,
ADD COLUMN IF NOT EXISTS sme_reviewer_initials TEXT CHECK (length(sme_reviewer_initials) BETWEEN 2 AND 4),
ADD COLUMN IF NOT EXISTS cms_tag TEXT CHECK (cms_tag = 'source: notebooklm'),
ADD COLUMN IF NOT EXISTS content_hash TEXT,
ADD COLUMN IF NOT EXISTS canonical_id TEXT UNIQUE,
ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'manual_upload',
ADD COLUMN IF NOT EXISTS source_url TEXT,
ADD COLUMN IF NOT EXISTS canonical BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1;

-- Create indexes for NLM fields
CREATE INDEX IF NOT EXISTS idx_clause_embeddings_nlm_source ON clause_embeddings(nlm_source_id);
CREATE INDEX IF NOT EXISTS idx_clause_embeddings_nlm_timestamp ON clause_embeddings(nlm_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_clause_embeddings_code_ref ON clause_embeddings(code_reference_primary);
CREATE INDEX IF NOT EXISTS idx_clause_embeddings_cms_tag ON clause_embeddings(cms_tag);
CREATE INDEX IF NOT EXISTS idx_clause_embeddings_canonical_id ON clause_embeddings(canonical_id);

-- SME review/ingestion log
CREATE TABLE IF NOT EXISTS clause_sme_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  canonical_id TEXT,
  clause_id TEXT,
  sme_user TEXT NOT NULL,
  action TEXT NOT NULL CHECK (action IN ('submitted','approved','rejected','commented','merged','revision_requested')),
  action_note TEXT,
  action_payload JSONB,
  priority TEXT CHECK (priority IN ('P0','P1','P2','P3')),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_clause_sme_log_canonical ON clause_sme_log(canonical_id);
CREATE INDEX IF NOT EXISTS idx_clause_sme_log_action ON clause_sme_log(action);
CREATE INDEX IF NOT EXISTS idx_clause_sme_log_priority ON clause_sme_log(priority);
CREATE INDEX IF NOT EXISTS idx_clause_sme_log_created ON clause_sme_log(created_at DESC);

-- MiltmonNDT Q Upload Log for SME review queue (Priority 3 fallbacks)
CREATE TABLE IF NOT EXISTS miltmon_ndt_q_upload_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp TIMESTAMPTZ DEFAULT now(),
  query TEXT NOT NULL,
  session_id TEXT,
  fallback_reason TEXT,
  retrieved_clause_ids TEXT[],
  sme_action_required BOOLEAN DEFAULT true,
  suggested_question_range TEXT DEFAULT 'Q051-Q110',
  priority TEXT CHECK (priority IN ('high','medium','low')) DEFAULT 'medium',
  status TEXT CHECK (status IN ('pending','assigned','in_progress','completed')) DEFAULT 'pending',
  assigned_sme TEXT,
  resolution_note TEXT,
  created_question_id TEXT,
  resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_miltmon_log_timestamp ON miltmon_ndt_q_upload_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_miltmon_log_status ON miltmon_ndt_q_upload_log(status);
CREATE INDEX IF NOT EXISTS idx_miltmon_log_priority ON miltmon_ndt_q_upload_log(priority);
CREATE INDEX IF NOT EXISTS idx_miltmon_log_sme ON miltmon_ndt_q_upload_log(assigned_sme);

-- Backfill canonical_id for existing rows (one-time migration)
UPDATE clause_embeddings 
SET canonical_id = clause_id 
WHERE canonical_id IS NULL AND clause_id IS NOT NULL;

-- Backfill content_hash for existing rows (requires application-level update)
-- Run this via script: UPDATE clause_embeddings SET content_hash = sha256(content::bytea)::text WHERE content_hash IS NULL;

COMMENT ON TABLE clause_sme_log IS 'Tracks SME review actions for content validation and approval';
COMMENT ON TABLE miltmon_ndt_q_upload_log IS 'Logs Priority 3 fallback queries requiring SME content creation (Q051-Q110)';
COMMENT ON COLUMN clause_embeddings.nlm_source_id IS 'NotebookLM source identifier for traceability';
COMMENT ON COLUMN clause_embeddings.nlm_timestamp IS 'UTC timestamp of NLM export for version control';
COMMENT ON COLUMN clause_embeddings.code_reference_primary IS 'Primary code clause reference (e.g., AWS D1.1:2020 4.2.3)';
COMMENT ON COLUMN clause_embeddings.sme_reviewer_initials IS 'SME who validated this content (2-4 characters)';
COMMENT ON COLUMN clause_embeddings.cms_tag IS 'Content management safeguard tag (must be source: notebooklm)';
COMMENT ON COLUMN clause_embeddings.content_hash IS 'SHA-256 hash of content for integrity verification';
COMMENT ON COLUMN clause_embeddings.canonical_id IS 'Unique canonical identifier across all versions';

