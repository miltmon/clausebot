# ClauseBot Knowledge Base  
**Document ID:** 03_DATABASE_SCHEMA.md  
**Last Updated:** October 23, 2025  
**Maintainer:** Database Team

---

# ClauseBot AI — Database Schema

Complete documentation of database structures, relationships, and data flow between Supabase (primary) and Airtable (fallback).

---

## 🗄️ **Database Architecture**

### **Dual-Database Strategy**

```
┌─────────────────────────────────────────┐
│           ClauseBot API                 │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────┐      ┌─────────────┐  │
│  │  Supabase   │      │  Airtable   │  │
│  │  (Primary)  │      │ (Fallback)  │  │
│  │             │      │             │  │
│  │ PostgreSQL  │      │  No-Code    │  │
│  │ + REST API  │      │   Database  │  │
│  └─────────────┘      └─────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

**Rationale:**
- **Supabase** — Scalable PostgreSQL with built-in auth, real-time, and full-text search
- **Airtable** — Rapid content updates by non-technical team members
- **Fallback Strategy** — Hardcoded questions if both sources fail

---

## 📊 **Supabase Schema (PostgreSQL)**

### **Connection Details**

```python
SUPABASE_URL = "https://hqhughgdraokwmreronk.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "***"  # Stored in environment
```

### **Tables**

#### **`questions` (Operational)**

Quiz questions with full-text search capabilities.

```sql
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    tags TEXT[],
    airtable_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Full-text search index
CREATE INDEX questions_question_fts_idx 
    ON questions USING GIN (to_tsvector('english', question));

-- Airtable ID lookup index
CREATE INDEX questions_airtable_id_idx 
    ON questions (airtable_id);
```

**Columns:**

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | No | Primary key, auto-generated |
| `question` | TEXT | No | Question text |
| `answer` | TEXT | No | Answer text |
| `tags` | TEXT[] | Yes | Array of tags (e.g., ["aws", "d1.1"]) |
| `airtable_id` | VARCHAR(255) | Yes | Reference to Airtable record |
| `created_at` | TIMESTAMPTZ | No | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | No | Last update timestamp |

**Usage Example:**
```python
# Full-text search
response = supabase.table("questions").select("*").text_search(
    "question", "undercut"
).limit(10).execute()

# Pagination
response = supabase.table("questions").select("*").range(0, 9).execute()
```

---

#### **`v_primetime_proof` (View - Operational)**

Deployment health monitoring view.

```sql
CREATE VIEW v_primetime_proof AS
SELECT 
    date_trunc('day', check_time) AS day,
    'ClauseBot' AS base_name,
    max(check_time) AS last_check,
    EXTRACT(EPOCH FROM (now() - max(check_time))) / 3600 AS freshness_hours,
    count(CASE WHEN status != 'ok' THEN 1 END) AS drift_tables_24h
FROM data_sync_health
WHERE check_time > now() - interval '24 hours'
GROUP BY day;
```

**Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `day` | DATE | Aggregation date |
| `base_name` | TEXT | System identifier |
| `last_check` | TIMESTAMPTZ | Most recent health check |
| `freshness_hours` | NUMERIC | Hours since last check |
| `drift_tables_24h` | BIGINT | Number of non-OK syncs in 24h |

**Purpose:** Powers primetime health validation and `PRIMETIME_PROOF_2025-10-11.md` reports.

---

#### **`v_daily_check` (View - Operational)**

Daily sync validation aggregation.

```sql
CREATE VIEW v_daily_check AS
SELECT 
    date_trunc('day', check_time) AS check_day,
    count(*) AS total_checks,
    count(CASE WHEN status = 'ok' THEN 1 END) AS ok_count,
    count(CASE WHEN status != 'ok' THEN 1 END) AS fail_count
FROM data_sync_health
WHERE check_time > now() - interval '24 hours'
GROUP BY check_day
ORDER BY check_day DESC;
```

**Purpose:** Track sync reliability and detect anomalies.

---

#### **`data_sync_health` (Planned)**

Health check logs for Airtable ↔ Supabase sync operations.

```sql
CREATE TABLE data_sync_health (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    check_time TIMESTAMP WITH TIME ZONE DEFAULT now(),
    source VARCHAR(50) NOT NULL,  -- 'airtable', 'supabase'
    status VARCHAR(20) NOT NULL,  -- 'ok', 'error', 'warning'
    message TEXT,
    record_count INT,
    duration_ms INT
);

CREATE INDEX data_sync_health_check_time_idx 
    ON data_sync_health (check_time DESC);
```

---

#### **`users` (Planned)**

User authentication and profile management.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',  -- 'user', 'admin', 'inspector'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    last_login TIMESTAMP WITH TIME ZONE
);
```

---

#### **`audit_logs` (Planned)**

Security and compliance audit trail.

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
    event_type VARCHAR(100) NOT NULL,  -- 'api_call', 'auth_failure', etc.
    user_id UUID REFERENCES users(id),
    request_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    details JSONB
);

CREATE INDEX audit_logs_timestamp_idx ON audit_logs (timestamp DESC);
CREATE INDEX audit_logs_event_type_idx ON audit_logs (event_type);
CREATE INDEX audit_logs_user_id_idx ON audit_logs (user_id);
```

---

## 🗂️ **Airtable Schema**

### **Connection Details**

```python
AIRTABLE_TOKEN = "***"  # Personal Access Token
AIRTABLE_BASE_ID = "appJQ23u70iwOl5Nn"
AIRTABLE_TABLE_ID = "tblvvclz8NSpiSVR9"
AIRTABLE_VIEW_ID = "viw5Q9YwrJ9Saz8ca"  # Optional filter view
```

### **Base: Quiz Questions**

#### **Table: `Questions`**

Primary quiz question repository managed by content team.

**Fields:**

| Field Name | Type | Description |
|------------|------|-------------|
| `Record ID` | Auto | Airtable internal ID (e.g., rec123456) |
| `Question` | Long Text | Question text |
| `Answer Choice A` | Single Line | First answer option |
| `Answer Choice B` | Single Line | Second answer option |
| `Answer Choice C` | Single Line | Third answer option |
| `Answer Choice D` | Single Line | Fourth answer option |
| `Correct Answer` | Single Select | Correct choice key (A, B, C, D) |
| `Primary Code Reference` | Single Line | Clause reference (e.g., "6.9.1") |
| `Question Category` | Single Select | Category (Visual Inspection, Preheat, etc.) |
| `Explanation of Correct Answer` | Long Text | Detailed explanation |
| `Difficulty Level` | Single Select | Easy, Medium, Hard |
| `Active` | Checkbox | Include in quiz pool |
| `Created Time` | Created Time | Auto-populated |
| `Last Modified Time` | Last Modified | Auto-populated |

**View: `Active Questions (viw5Q9YwrJ9Saz8ca)`**

Filters: `Active = TRUE`  
Sort: `Created Time DESC`

---

### **Data Normalization**

ClauseBot transforms Airtable records into a consistent format:

```python
# Airtable record
{
    "id": "rec123456",
    "fields": {
        "Question": "According to AWS D1.1, what is...",
        "Answer Choice A": "1/32 inch (0.8 mm)",
        "Answer Choice B": "1/16 inch (1.6 mm)",
        "Answer Choice C": "3/32 inch (2.4 mm)",
        "Answer Choice D": "1/8 inch (3.2 mm)",
        "Correct Answer": "A",
        "Primary Code Reference": "6.9.1",
        "Question Category": "Visual Inspection",
        "Explanation of Correct Answer": "For statically loaded..."
    }
}

# Normalized output
{
    "id": "rec123456",
    "question": "According to AWS D1.1, what is...",
    "choices": [
        "1/32 inch (0.8 mm)",
        "1/16 inch (1.6 mm)",
        "3/32 inch (2.4 mm)",
        "1/8 inch (3.2 mm)"
    ],
    "correct": "A",
    "clause": "6.9.1",
    "category": "Visual Inspection",
    "explanation": "For statically loaded...",
    "source": "airtable"
}
```

---

## 🔄 **Data Flow & Synchronization**

### **Quiz Question Flow**

```
1. Content Team Updates Airtable
   │
   ├─► Checkbox "Active" = TRUE
   │
   ▼
2. API Request: GET /v1/quiz
   │
   ▼
3. AirtableDataSource.iter_records()
   │
   ├─► Try: Fetch from Airtable
   │   │
   │   ├─► Success: Return live data
   │   │
   │   └─► Fail: Return fallback
   │
   ▼
4. Normalize & Filter
   │
   ├─► Filter by category (if requested)
   ├─► Shuffle (if requested)
   └─► Limit to count
   │
   ▼
5. Return JSON to client
```

### **Fallback Hierarchy**

```
Primary: Airtable (Real-time)
    ↓ (on connection failure)
Secondary: Hardcoded Fallback (3 sample questions)
    ↓ (on complete failure)
Error: HTTP 503 Service Unavailable
```

---

## 🔐 **Security & Access Control**

### **Supabase Security**

**Row-Level Security (RLS) - Planned:**
```sql
-- Enable RLS
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;

-- Public read access
CREATE POLICY "Public read access"
    ON questions FOR SELECT
    USING (true);

-- Admin write access
CREATE POLICY "Admin write access"
    ON questions FOR ALL
    USING (auth.jwt() ->> 'role' = 'admin');
```

**Service Role Key:**
- Bypasses RLS for server-side operations
- Stored in environment variables only
- Never exposed to client

---

### **Airtable Security**

**Personal Access Token (PAT):**
- Scoped to specific base
- Read-only for API operations
- Rotated quarterly

**Access Levels:**
- Content Team: Editor (via Airtable UI)
- API: Read-only (via PAT)
- Public: No direct access

---

## 📈 **Performance Optimization**

### **Supabase Indexes**

```sql
-- Full-text search (questions)
CREATE INDEX questions_question_fts_idx 
    ON questions USING GIN (to_tsvector('english', question));

-- Tag filtering
CREATE INDEX questions_tags_idx 
    ON questions USING GIN (tags);

-- Temporal queries
CREATE INDEX audit_logs_timestamp_idx 
    ON audit_logs (timestamp DESC);
```

### **Airtable Best Practices**

- **Use Views** to pre-filter active questions
- **Limit fields** in API requests (`select=*` only when needed)
- **Cache locally** for 5-10 minutes to reduce API calls
- **Batch operations** when syncing to Supabase

---

## 🔮 **Planned Schema Extensions**

### **Clause References Table**

```sql
CREATE TABLE clause_references (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) NOT NULL,  -- 'AWS_D1.1', 'ASME_IX', 'API_1104'
    clause VARCHAR(50) NOT NULL,
    title TEXT,
    content TEXT,
    parent_clause VARCHAR(50),
    annexes TEXT[],
    notes TEXT[],
    figures TEXT[],
    tables TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(code, clause)
);

CREATE INDEX clause_references_code_clause_idx 
    ON clause_references (code, clause);
```

### **User Progress Tracking**

```sql
CREATE TABLE user_quiz_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    question_id UUID REFERENCES questions(id),
    selected_answer VARCHAR(1),
    is_correct BOOLEAN,
    time_spent_seconds INT,
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX user_quiz_attempts_user_id_idx 
    ON user_quiz_attempts (user_id);
```

---

## 🛠️ **Migration & Maintenance**

### **Schema Version Control**

Managed via Supabase migrations:
```bash
supabase/migrations/
├── 20251001_init_questions.sql
├── 20251015_add_audit_logs.sql
└── 20251023_clause_references.sql
```

### **Backup Strategy**

- **Supabase:** Daily automated backups (7-day retention)
- **Airtable:** Manual exports weekly
- **Critical data:** Replicated to GitHub as JSON

---

## 🔗 **Related Documentation**

- **API Reference:** See `02_API_REFERENCE.md`
- **Architecture:** See `01_ARCHITECTURE_GUIDE.md`
- **Security:** See `05_DATA_HANDLING_AND_SECURITY.md`

---

**Document Version:** 1.0  
**Next Review:** January 2026
