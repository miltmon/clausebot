# AWS D1.1:2020 → D1.1:2025 Crosswalk

**Purpose:** Track clause ID changes, content reorganization, and strategic impacts for CWI instruction materials

**Tags:** `#awsd1.1` `#cwi2025` `#codeupdate`

---

## 📋 Files in This Directory

- `aws_d11_2020_to_2025.csv` - Main crosswalk mapping file (20 starter rows, expand to 200+)

---

## 🎯 How to Use This Crosswalk

### For Content/SME Team

1. **Populate TBD Clause IDs**
   - Obtain AWS D1.1:2025 official document
   - Map each `old_clause_id` to actual `new_clause_id`
   - Update `new_short_title` with official 2025 wording
   - Change `confidence` from "high" to "verified" after confirmation

2. **Update Status Column**
   ```
   pending → in_progress → review → completed
   ```

3. **Priority Mapping Order**
   - **High Priority (weeks 1-2):** Clauses 4, 5, 6, 8 (inspection-critical)
   - **Medium Priority (weeks 3-4):** Clauses 9, 10, annexes
   - **Low Priority (weeks 5-6):** Informative annexes, commentary

### For Engineering Team

1. **Update Ingestion Script**
   - Use this CSV to map old clause IDs to new when processing 2025 corpus
   - Create `clause_id_aliases` table for backward compatibility
   
2. **Update ClauseBot Logic**
   ```python
   # Example: Load crosswalk for query expansion
   crosswalk = load_crosswalk('docs/crosswalk/aws_d11_2020_to_2025.csv')
   
   # When user queries "Clause 6.26" (2020)
   # Expand to also search "Table 6.7" (2025)
   ```

3. **Golden Dataset Updates**
   - After CSV complete, update `ops/golden_dataset/golden_d11_2025.json`
   - Replace all `TBD` clause IDs with verified mappings

### For Curriculum/LMS Team

1. **Filter by Action Column**
   ```bash
   # Get all modules needing updates
   grep "update_curriculum" aws_d11_2020_to_2025.csv
   
   # Get all new modules to create
   grep "create_new_module" aws_d11_2020_to_2025.csv
   ```

2. **Update Module References**
   - Replace old clause numbers with new in all slide decks
   - Add "formerly Clause X.Y (2020)" notes for 6 months post-launch
   - Update all decision trees, flowcharts, and tables

### For QA/Assessment Team

1. **Question Bank Tagging**
   - Tag each question with `standard_version: 2020` or `2025`
   - Questions referencing changed clauses → mark for review
   - Use `note` column to identify strategic changes requiring new questions

2. **Exam Mapping**
   - Any question citing `old_clause_id` → review answer key
   - High-impact changes (CVN, PAUT, digital RT) → create new question sets

---

## 📊 Crosswalk CSV Schema

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `old_clause_id` | TEXT | D1.1:2020 clause number | `6.26`, `8.16`, `Annex H` |
| `old_short_title` | TEXT | 2020 clause title (abbreviated) | `CVN Toughness Testing` |
| `new_clause_id` | TEXT | D1.1:2025 clause number (TBD until verified) | `TBD` → `6.X` → `Table 6.7` |
| `new_short_title` | TEXT | 2025 clause title (abbreviated) | `CVN Requirements Consolidated` |
| `note` | TEXT | Strategic impact, action items, SME notes | `Update LMS module X; add digital RT primer` |
| `confidence` | ENUM | Mapping certainty | `high`, `medium`, `low`, `verified` |
| `action` | ENUM | Required downstream work | `update_curriculum`, `create_new_module`, `update_tables` |
| `owner` | TEXT | Team/tag responsible | `#awsd1.1`, `@content-team`, `@sme-john` |
| `status` | ENUM | Progress tracking | `pending`, `in_progress`, `review`, `completed` |
| `last_updated` | DATE | Last modification date | `2025-11-02` |

---

## 🔍 Key Change Categories

### 1. Consolidations (e.g., CVN → Table 6.7)
- **Challenge:** Multiple 2020 clauses → single 2025 table
- **Solution:** Create one-to-many mapping; update all referencing materials

### 2. Reorganizations (e.g., Clause 6 PJP)
- **Challenge:** Content moved but not fundamentally changed
- **Solution:** Simple ID swap + cross-reference note

### 3. New Additions (e.g., Annex H PAUT, Clause 4.7 LRFD)
- **Challenge:** No 2020 equivalent
- **Solution:** Mark `old_clause_id` as `N/A`; create new curriculum module

### 4. Removals (e.g., A5.36 filler metals, tubular calcs)
- **Challenge:** 2020 content no longer present
- **Solution:** Note removal in CSV; redirect users to external references (AISC, A5 specs)

### 5. Technology Updates (e.g., Digital RT, PAUT)
- **Challenge:** New technology provisions added mid-lifecycle
- **Solution:** Create supplemental modules; flag as "2025 new technology"

---

## ⚠️ Critical Crosswalk Rules

### DO:
✅ Verify every mapping against official D1.1:2025 document  
✅ Document rationale in `note` column for non-obvious changes  
✅ Update `last_updated` date when modifying any row  
✅ Use `confidence: verified` only after SME sign-off  
✅ Keep crosswalk in sync with `golden_d11_2025.json`  

### DON'T:
❌ Guess at clause mappings (use `TBD` until verified)  
❌ Delete rows (even if clause removed - mark action as `archive`)  
❌ Skip `action` column (needed for downstream task tracking)  
❌ Use informal clause titles (match official wording)  
❌ Forget to update golden dataset after finalizing mappings  

---

## 📈 Completion Tracking

**Current Status:** 20 / 200+ rows (10% complete)

**Target Completion:**
- Phase 1 (Clauses 4, 5, 6, 8): Week 2
- Phase 2 (Remaining clauses): Week 4
- Phase 3 (Verification): Week 6

**Progress Dashboard:**
```bash
# Count by status
grep -c "status,pending" aws_d11_2020_to_2025.csv    # Remaining
grep -c "status,completed" aws_d11_2020_to_2025.csv  # Done

# Count by confidence
grep -c "confidence,verified" aws_d11_2020_to_2025.csv  # Confirmed mappings
```

---

## 🔗 Related Documentation

- **Golden Dataset (2025):** `ops/golden_dataset/golden_d11_2025.json`
- **Golden Dataset (2020):** `ops/golden_dataset/golden.json`
- **Ingestion Script:** `backend/scripts/ingest_aws_d11.py`
- **Deployment Runbook:** `backend/DEPLOYMENT_RUNBOOK_CURSOR.md`
- **Migration Strategy:** (See this session's comprehensive roadmap)

---

## 📞 Contacts & Ownership

- **Content Lead / SME Coordination:** [Add name/Slack]
- **Engineering / ClauseBot Integration:** [Add name/Slack]
- **Curriculum / LMS Updates:** [Add name/Slack]
- **QA / Assessment Team:** [Add name/Slack]

---

**Last Updated:** 2025-11-02  
**Maintained By:** Content & Engineering Teams  
**Review Frequency:** Weekly until Phase 3 complete, then monthly

