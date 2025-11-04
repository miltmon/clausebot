-- Golden Test Ingestion: Q026-Q041
-- AWS D1.1:2025 Canonical Items
-- Run against Supabase/PostgreSQL staging, then promote to production

-- ========================================
-- PHASE 1: STAGING INGESTION
-- ========================================

-- Create staging table if not exists
CREATE TABLE IF NOT EXISTS golden_tests_staging (
    id TEXT PRIMARY KEY,
    standard TEXT NOT NULL,
    query TEXT NOT NULL,
    expected_answer TEXT,
    category TEXT,
    difficulty TEXT,
    content JSONB NOT NULL,
    metadata JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert Q026-Q041 from JSON files
-- Note: This assumes COPY from files or manual INSERT via app
-- For manual testing, use INSERT statements like:

/*
INSERT INTO golden_tests_staging (id, standard, query, expected_answer, category, difficulty, content, metadata)
SELECT 
    (content->>'id')::TEXT,
    (content->>'standard')::TEXT,
    (content->>'query')::TEXT,
    (content->>'expected_answer')::TEXT,
    (content->>'category')::TEXT,
    (content->>'difficulty')::TEXT,
    content,
    content->'metadata'
FROM json_file_import
WHERE (content->>'id')::TEXT BETWEEN 'Q026' AND 'Q041';
*/

-- Alternative: Use application-level ingestion (recommended)
-- Call backend API: POST /v1/golden/ingest with JSON payload

-- ========================================
-- PHASE 2: VALIDATION QUERIES
-- ========================================

-- Count rows inserted
SELECT COUNT(*) AS inserted_count 
FROM golden_tests_staging 
WHERE id BETWEEN 'Q026' AND 'Q041';
-- Expected: 16

-- Verify SSOT metadata compliance
SELECT 
    id,
    metadata->>'nlm_source_id' AS nlm_id,
    metadata->>'sme_reviewer_initials' AS sme_initials,
    metadata->>'cms_tag' AS cms_tag,
    metadata->>'code_reference_primary' AS clause_ref
FROM golden_tests_staging
WHERE id BETWEEN 'Q026' AND 'Q041'
ORDER BY id;

-- Check for any missing required metadata fields
SELECT id, 'Missing nlm_source_id' AS issue
FROM golden_tests_staging
WHERE id BETWEEN 'Q026' AND 'Q041'
  AND (metadata->>'nlm_source_id' IS NULL OR metadata->>'nlm_source_id' = '')
UNION ALL
SELECT id, 'Missing cms_tag' AS issue
FROM golden_tests_staging
WHERE id BETWEEN 'Q026' AND 'Q041'
  AND (metadata->>'cms_tag' IS NULL OR metadata->>'cms_tag' != 'source:notebooklm')
UNION ALL
SELECT id, 'Missing code_reference_primary' AS issue
FROM golden_tests_staging
WHERE id BETWEEN 'Q026' AND 'Q041'
  AND (metadata->>'code_reference_primary' IS NULL OR metadata->>'code_reference_primary' = '');

-- If above returns rows, fix metadata before proceeding

-- ========================================
-- PHASE 3: PRODUCTION PROMOTION
-- ========================================

-- Create production table if not exists
CREATE TABLE IF NOT EXISTS golden_tests (
    id TEXT PRIMARY KEY,
    standard TEXT NOT NULL,
    query TEXT NOT NULL,
    expected_answer TEXT,
    category TEXT,
    difficulty TEXT,
    content JSONB NOT NULL,
    metadata JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Promote from staging to production (UPSERT)
-- Run ONLY after QA sign-off
INSERT INTO golden_tests (id, standard, query, expected_answer, category, difficulty, content, metadata, created_at, updated_at)
SELECT 
    id,
    standard,
    query,
    expected_answer,
    category,
    difficulty,
    content,
    metadata,
    created_at,
    NOW() AS updated_at
FROM golden_tests_staging
WHERE id BETWEEN 'Q026' AND 'Q041'
ON CONFLICT (id) DO UPDATE SET
    standard = EXCLUDED.standard,
    query = EXCLUDED.query,
    expected_answer = EXCLUDED.expected_answer,
    category = EXCLUDED.category,
    difficulty = EXCLUDED.difficulty,
    content = EXCLUDED.content,
    metadata = EXCLUDED.metadata,
    updated_at = NOW();

-- Verify production counts
SELECT COUNT(*) AS production_count
FROM golden_tests
WHERE id BETWEEN 'Q026' AND 'Q041';
-- Expected: 16

-- ========================================
-- PHASE 4: AUDIT LOG
-- ========================================

-- Create audit log entry
CREATE TABLE IF NOT EXISTS golden_tests_audit (
    audit_id SERIAL PRIMARY KEY,
    action TEXT NOT NULL,
    test_ids TEXT[],
    performed_by TEXT,
    performed_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);

INSERT INTO golden_tests_audit (action, test_ids, performed_by, notes)
VALUES (
    'PRODUCTION_PROMOTION',
    ARRAY(SELECT id FROM golden_tests WHERE id BETWEEN 'Q026' AND 'Q041' ORDER BY id),
    CURRENT_USER,
    'D1.1:2025 canonical golden tests Q026-Q041 promoted from staging after SME/QA approval'
);

-- ========================================
-- ROLLBACK PROCEDURE
-- ========================================

-- If issues discovered, execute rollback:
/*
BEGIN;

-- Remove from production
DELETE FROM golden_tests WHERE id BETWEEN 'Q026' AND 'Q041';

-- Log rollback
INSERT INTO golden_tests_audit (action, test_ids, performed_by, notes)
VALUES (
    'ROLLBACK',
    ARRAY['Q026','Q027','Q028','Q029','Q030','Q031','Q032','Q033','Q034','Q035','Q036','Q037','Q038','Q039','Q040','Q041'],
    CURRENT_USER,
    'Rolled back Q026-Q041 due to: [REASON]'
);

COMMIT;
*/

-- ========================================
-- VERIFICATION REPORT
-- ========================================

-- Final summary report
SELECT 
    'Q026-Q041 Ingestion Summary' AS report_title,
    (SELECT COUNT(*) FROM golden_tests_staging WHERE id BETWEEN 'Q026' AND 'Q041') AS staging_count,
    (SELECT COUNT(*) FROM golden_tests WHERE id BETWEEN 'Q026' AND 'Q041') AS production_count,
    (SELECT COUNT(*) FROM golden_tests WHERE id BETWEEN 'Q026' AND 'Q041' AND metadata->>'sme_reviewer_initials' = 'TBD') AS pending_sme_review,
    NOW() AS report_timestamp;

