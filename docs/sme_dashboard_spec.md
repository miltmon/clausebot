# SME Dashboard Specification

**Purpose:** SME review/approval workflow for clause ingestion and crosswalk mapping  
**Target:** Track Q051-Q110 expansion and D1.1:2025 migration with full traceability  
**Tags:** `#awsd1.1` `#cwi2025` `#sme-workflow`

---

## Architecture Overview

```
NotebookLM Export → Ingestion Script → Supabase (clause_embeddings)
                                            ↓
                                      Creates entry
                                            ↓
                                    Airtable SME Queue
                                            ↓
                                    SME Review & Approval
                                            ↓
                              Webhook → Update Supabase
                                            ↓
                                    clause_sme_log audit
```

---

## Data Sources

### Primary Store: Supabase

**Tables:**
1. `clause_embeddings` - Canonical content with NLM metadata
2. `clause_sme_log` - Audit trail of all SME actions
3. `miltmon_ndt_q_upload_log` - Priority 3 fallback queue (Q051-Q110)

### SME Interface: Airtable

**Base Name:** "ClauseBot SME Queue"

**Purpose:** Lightweight UI for SME review with email triggers and status tracking

---

## Airtable Schema

### Table 1: SME Queue

| Field | Type | Purpose | Required |
|-------|------|---------|----------|
| `canonical_id` | Single line text | Unique identifier | ✅ |
| `standard` | Single select | AWS D1.1:2020/2025, API 1104, ASME IX | ✅ |
| `clause_path` | Long text | Breadcrumb path (e.g., "Clause 4 > 4.8 > 4.8.3") | ✅ |
| `title` | Single line text | Clause title | ✅ |
| `content_snippet` | Long text | First 500 chars of content | ✅ |
| `content_hash` | Single line text | SHA-256 hash for verification | ✅ |
| `nlm_source_id` | Single line text | NotebookLM source reference | ✅ |
| `nlm_timestamp` | Date | UTC timestamp of NLM export | ✅ |
| `code_reference_primary` | Single line text | Primary clause ref (e.g., AWS D1.1:2020 6.26) | ✅ |
| `status` | Single select | submitted, in_review, approved, rejected | ✅ |
| `assigned_sme` | Collaborator | SME responsible for review | Required for in_review |
| `priority` | Single select | P0 (critical), P1 (high), P2 (medium), P3 (low) | ✅ |
| `sme_notes` | Long text | Review comments | Optional |
| `rejection_reason` | Single select | hash_mismatch, content_error, duplicate, other | For rejected only |
| `supabase_row_url` | URL | Direct link to Supabase dashboard record | Auto-generated |
| `screenshot_or_pdf` | Attachment | Supporting documentation | Optional |
| `date_submitted` | Date | Auto-filled on creation | ✅ |
| `date_reviewed` | Date | Set when status changes from submitted | Auto |
| `date_approved` | Date | Set when status = approved | Auto |
| `cms_tag` | Single line text | Must be "source: notebooklm" | ✅ |

### Table 2: SME Audit Log

**Purpose:** Mirror of `clause_sme_log` with webhook sync

| Field | Type | Purpose |
|-------|------|---------|
| `log_id` | UUID | Matches Supabase row ID |
| `canonical_id` | Linked record | Links to SME Queue |
| `sme_user` | Single line text | SME initials or email |
| `action` | Single select | submitted, approved, rejected, commented, merged |
| `action_note` | Long text | Free-form note |
| `timestamp` | Date | UTC timestamp |
| `priority` | Single select | P0/P1/P2/P3 |

### Table 3: MiltmonNDT Fallback Queue

**Purpose:** Tracks Priority 3 fallback queries requiring Q051-Q110 creation

| Field | Type | Purpose |
|-------|------|---------|
| `query` | Long text | User's original query |
| `session_id` | Single line text | Session identifier |
| `fallback_reason` | Single line text | Why priority routing failed |
| `retrieved_clauses` | Long text | What ClauseBot returned (generic) |
| `priority` | Single select | high (ASME/AWS ref), medium, low |
| `status` | Single select | pending, assigned, in_progress, completed |
| `assigned_sme` | Collaborator | SME creating content |
| `suggested_question_range` | Single line text | Default: "Q051-Q110" |
| `resolution_note` | Long text | What was created to resolve |
| `created_question_id` | Single line text | e.g., "Q062" |
| `timestamp` | Date | When logged |
| `resolved_at` | Date | When completed |

---

## Workflows

### Workflow 1: Content Ingestion & Review

1. **Ingestion Script** writes to Supabase `clause_embeddings`
   - Validates content_hash, cms_tag, NLM metadata
   - Sets `canonical=false` until SME approved
   
2. **Webhook Trigger** (Supabase → Airtable)
   - On INSERT to `clause_embeddings`, create Airtable "SME Queue" row
   - Auto-assign priority based on standard + clause:
     - P0: Clause 4, 6, 8 (inspection-critical)
     - P1: Clause 5, 9, 10
     - P2: Annexes, tables
     - P3: Informative content

3. **SME Review** (in Airtable)
   - SME opens assigned item
   - Reviews content snippet vs code reference
   - Sets status:
     - `approved` → Trigger webhook to update Supabase
     - `rejected` → Add rejection_reason, trigger webhook
     - `in_review` → Request more info, add notes

4. **Airtable Webhook** → Supabase
   - On status = `approved`:
     - UPDATE `clause_embeddings` SET `canonical=true`, `version=version+1`
     - INSERT `clause_sme_log` with action='approved'
   - On status = `rejected`:
     - INSERT `clause_sme_log` with action='rejected', note=rejection_reason

### Workflow 2: Priority 3 Fallback → Q051-Q110 Creation

1. **Priority Router** logs fallback query to `miltmon_ndt_q_upload_log`
2. **Webhook** creates Airtable "MiltmonNDT Fallback Queue" row
3. **SME Assignment** (daily triage)
   - High priority queries assigned within 24h
   - SME creates new quiz question (Q051-Q110) or NLM content snippet
4. **Resolution**
   - SME updates status to `completed`
   - Adds `created_question_id` (e.g., "Q062")
   - Writes resolution_note
5. **Webhook** updates Supabase `miltmon_ndt_q_upload_log`

---

## API Endpoints (FastAPI)

### POST `/v1/sme/submit`

**Purpose:** Submit content for SME review (called by ingestion script)

**Request:**
```json
{
  "canonical_id": "aws_d1.1_2025_4.8.3",
  "standard": "AWS D1.1:2025",
  "clause_path": "Clause 4 > 4.8 > 4.8.3",
  "title": "Preheat Requirements",
  "content": "Full content text...",
  "content_hash": "sha256_hash_here",
  "nlm_source_id": "NLM-AWS-D11-2025-4.8.3-001",
  "nlm_timestamp": "2025-11-02T15:30:00Z",
  "code_reference_primary": "AWS D1.1:2025 4.8.3",
  "sme_reviewer_initials": "JD",
  "cms_tag": "source: notebooklm",
  "priority": "P0"
}
```

**Response:**
```json
{
  "canonical_id": "aws_d1.1_2025_4.8.3",
  "status": "submitted",
  "airtable_record_id": "recXXXXXXXXXX",
  "supabase_row_id": "uuid-here",
  "estimated_review_time_hours": 48
}
```

### GET `/v1/sme/queue`

**Purpose:** Get pending SME review items (permissioned)

**Query Params:**
- `status`: submitted, in_review, approved, rejected
- `priority`: P0, P1, P2, P3
- `standard`: AWS D1.1:2020, AWS D1.1:2025
- `assigned_sme`: Filter by SME initials

**Response:**
```json
{
  "items": [
    {
      "canonical_id": "...",
      "title": "...",
      "status": "submitted",
      "priority": "P0",
      "date_submitted": "2025-11-02T15:30:00Z"
    }
  ],
  "total_pending": 45,
  "avg_review_time_hours": 36
}
```

### POST `/v1/sme/approve`

**Purpose:** Approve content (called by Airtable webhook)

**Request:**
```json
{
  "canonical_id": "aws_d1.1_2025_4.8.3",
  "sme_initials": "JD",
  "action_note": "Content verified against official PDF"
}
```

**Response:**
```json
{
  "canonical_id": "aws_d1.1_2025_4.8.3",
  "canonical": true,
  "version": 1,
  "sme_log_id": "uuid-here"
}
```

---

## Audit & Reporting

### Daily Digest (Email to SME Lead)

**Contents:**
- New submissions in last 24h (grouped by priority)
- Pending items >72h (escalation)
- Rejection reasons summary
- Average review time by SME

### Weekly Dashboard Metrics

- Submission volume (by standard)
- Approval rate (%)
- Average review time (hours)
- Top rejection reasons
- SME workload distribution

### SLA Tracking

| Priority | Response Time | Resolution Time |
|----------|---------------|-----------------|
| P0 | 4 hours | 24 hours |
| P1 | 24 hours | 48 hours |
| P2 | 48 hours | 5 business days |
| P3 | 5 days | 10 business days |

**Escalation:** P0 items >24h unresolved → Alert SME Lead

---

## Security & Roles

### Airtable Permissions

- **SME (Reviewer):** Edit assigned records, comment, change status
- **SME Lead:** Full access, assign items, configure base
- **System (Webhook):** Create/update via API key

### API Security

- **Authentication:** JWT tokens + API keys
- **Authorization:** Role-based (sme_reviewer, sme_lead, admin)
- **Webhook Secret:** Signed payloads to prevent spoofing
- **Service Role Key:** Restricted to backend server only

### Audit Compliance

- All actions logged to `clause_sme_log` with timestamps
- Immutable audit trail (no deletes, only inserts)
- 12-month retention for regulatory compliance

---

## Monitoring & Alerts

### Metrics to Track

1. **Submission Rate:** Items/day entering queue
2. **Review Velocity:** Items/day processed by SME
3. **Approval Rate:** % approved on first review
4. **Rejection Reasons:** Top 5 causes
5. **SLA Compliance:** % meeting response/resolution SLAs
6. **Fallback Volume:** Priority 3 queries/day requiring Q051-Q110

### Alert Conditions

- P0 item pending >4h → SMS to SME Lead
- Submission spike >50 items/day → Review capacity
- Approval rate <80% → Check ingestion quality
- Fallback volume >10/day → Expand golden dataset

---

## Implementation Checklist

**Phase 1: Foundation (Week 1)**
- [ ] Create Airtable base with 3 tables
- [ ] Set up Supabase webhooks → Airtable
- [ ] Implement `/v1/sme/submit` endpoint
- [ ] Deploy ContentHashGuardMiddleware

**Phase 2: Integration (Week 2)**
- [ ] Set up Airtable webhooks → Supabase
- [ ] Implement `/v1/sme/approve` endpoint
- [ ] Test end-to-end workflow with 5 test clauses
- [ ] Configure email notifications

**Phase 3: Operations (Week 3)**
- [ ] Train SME team on Airtable interface
- [ ] Establish SLA monitoring dashboard
- [ ] Run pilot with 20 D1.1:2025 clauses
- [ ] Document troubleshooting procedures

---

## Contact & Ownership

- **SME Lead:** [Add name/contact]
- **Platform Engineering:** [Add name/contact]
- **Airtable Admin:** [Add name/contact]
- **Compliance Officer:** [Add name/contact]

---

**Last Updated:** 2025-11-02  
**Maintained By:** Platform + Content Teams  
**Review Frequency:** Monthly

