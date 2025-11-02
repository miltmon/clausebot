# ClauseBot RAG Golden Datasets

**Purpose:** Curated test queries with known correct clause citations for automated RAG validation

---

## 📁 Files in This Directory

| File | Standard | Tests | Purpose | Status |
|------|----------|-------|---------|--------|
| `golden.json` | AWS D1.1:2020 | 30 | Production validation for current system | ✅ Active |
| `golden_d11_2025.json` | AWS D1.1:2025 | 25 | Migration validation for 2025 update | 🔄 Pending ingestion |

---

## 🎯 When to Use Each Dataset

### Use `golden.json` (D1.1:2020)

**Current Production System**
- After any code changes to RAG service
- Daily/weekly validation runs
- CI/CD smoke tests
- Performance regression testing

**Run Command:**
```bash
python ops/golden-validate.py \
  --golden ops/golden_dataset/golden.json \
  --api-base https://clausebot-api.onrender.com \
  --pass-rate 0.90
```

### Use `golden_d11_2025.json` (D1.1:2025)

**After 2025 Corpus Ingestion**
- Validate 2025 clause retrieval accuracy
- Test crosswalk mapping effectiveness
- Ensure new content (PAUT, Digital RT, LRFD) retrievable
- Compare performance vs 2020 baseline

**Run Command:**
```bash
python ops/golden-validate.py \
  --golden ops/golden_dataset/golden_d11_2025.json \
  --api-base https://clausebot-api.onrender.com \
  --pass-rate 0.85  # Lower threshold initially
```

**⚠️ Prerequisites:**
1. Run `backend/scripts/ingest_aws_d11.py` with 2025 corpus
2. Update all `TBD` clause IDs in `golden_d11_2025.json` using crosswalk
3. Verify `standard = "AWS D1.1:2025"` filter works in ClauseBot

---

## 📊 Dataset Comparison

### `golden.json` (D1.1:2020)

**Coverage:**
- 30 comprehensive tests
- Difficulty: 8 easy, 15 medium, 7 hard
- Categories: preheat, inspection, qualification, joint design, workmanship

**Focus:**
- Broad coverage of entire 2020 standard
- Edge cases (tack welds, essential variables, cold weather)
- Common CWI queries from field usage

**Maintenance:**
- Stable (no updates unless D1.1:2020 corpus re-ingested)
- Add tests when new query patterns identified

### `golden_d11_2025.json` (D1.1:2025)

**Coverage:**
- 25 strategic tests
- Organized into 5 change categories
- Focus on Clauses 4, 5, 6, 8 (highest-impact changes)

**Change Categories:**
1. **WPS & Qualification** (5 tests) - Clause 6 waveform, PJP, CVN
2. **Advanced NDT** (5 tests) - Annex H PAUT, digital RT
3. **Preheat & Materials** (5 tests) - Table 5.8 updates, filler metal removals
4. **Inspection & RT** (5 tests) - Digital RT acceptance, inspector qualifications
5. **Crosswalk & Design** (5 tests) - Clause renumbering, LRFD additions

**Maintenance:**
- **CRITICAL:** Replace all `TBD` clause IDs before first run
- Update `expected_clauses` using `docs/crosswalk/aws_d11_2020_to_2025.csv`
- Expand to 50-75 tests after initial validation

---

## 🔧 Maintaining Golden Datasets

### Adding New Tests

1. **Identify Query Source**
   - User support tickets (frequent questions)
   - Quiz baseline (exam-relevant queries)
   - SME review (edge cases, ambiguous clauses)

2. **Create Test Entry**
   ```json
   {
     "id": "gd-XXX",
     "query": "What is [specific compliance question]?",
     "standard": "AWS D1.1:2020",  // or 2025
     "expected_clauses": ["X.Y.Z", "Table X.Y"],
     "min_similarity": 0.70,
     "source": "ticket_12345",
     "difficulty": "medium",
     "category": "preheat_qualification"
   }
   ```

3. **Validate Locally**
   ```bash
   python ops/golden-validate.py \
     --golden ops/golden_dataset/golden.json \
     --topk 10 \
     --pass-rate 0.0  # No threshold for testing
   ```

4. **Review Output**
   - Check `ops/reports/golden-report-*.csv`
   - If similarity too low, adjust `min_similarity`
   - If wrong clauses returned, investigate chunking/embeddings

### Updating Expected Clauses

**When to Update:**
- Crosswalk finalized (D1.1:2025 mappings confirmed)
- Re-ingestion changes clause IDs
- Chunking strategy revised

**Process:**
1. Run validator, export failures to CSV
2. For each failed test, manually query ClauseBot
3. Verify returned clauses are correct (but ID changed)
4. Update `expected_clauses` in JSON
5. Re-run validation until pass rate acceptable

### Tuning Similarity Thresholds

**Guidelines:**
- **Easy queries (direct matches):** `min_similarity: 0.75-0.80`
- **Medium queries (paraphrase):** `min_similarity: 0.65-0.75`
- **Hard queries (inference, edge cases):** `min_similarity: 0.60-0.70`

**Avoid:**
- Thresholds <0.55 (too lenient, allows irrelevant matches)
- Thresholds >0.85 (too strict, fails on valid paraphrases)

---

## 📈 Validation Best Practices

### CI Integration

**Nightly Validation (D1.1:2020)**
```yaml
# .github/workflows/golden-validation.yml
- Golden validation runs at 03:00 UTC
- Pass rate threshold: 90%
- Alerts on failure
```

**Weekly Validation (D1.1:2025)**
```bash
# Manual until stable
# Run every Monday after weekend ingestion tests
python ops/golden-validate.py --golden ops/golden_dataset/golden_d11_2025.json
```

### Pass Rate Targets

| Phase | D1.1:2020 | D1.1:2025 | Action |
|-------|-----------|-----------|--------|
| **Development** | ≥80% | ≥75% | Fix chunking, embeddings |
| **Staging** | ≥90% | ≥85% | Tune thresholds, update dataset |
| **Production** | ≥95% | ≥90% | Monitor, investigate regressions |

### Failure Triage

1. **Download report CSV** from workflow artifacts
2. **Group failures by `reason`:**
   - `expected_clause_not_in_topk` → Retrieval issue
   - `match_below_similarity_threshold` → Threshold too strict
   - `error_timeout` → Infrastructure issue
3. **Follow `.github/workflows/GOLDEN_FAILURE_CHECKLIST.md`**

---

## 🔗 Integration with Other Systems

### Crosswalk CSV
- `golden_d11_2025.json` depends on `docs/crosswalk/aws_d11_2020_to_2025.csv`
- Before running 2025 validation, finalize crosswalk mappings
- Script to auto-update golden from crosswalk: (future enhancement)

### LMS/Curriculum
- Failed golden tests → potential curriculum gaps
- High-difficulty tests failing → add training module
- New query patterns → expand golden dataset + add flashcards

### Exam DB
- Golden tests = exam question candidates
- Use `difficulty` and `category` for item banking
- Track which tests align with CWI exam blueprint

---

## 📞 Ownership & Contacts

- **Golden Dataset Maintenance:** QA Lead + Content Team
- **RAG Engineering / Validation:** Platform Team
- **Crosswalk Integration:** Content + Engineering
- **CI/CD Workflows:** DevOps / SRE

---

## 🎯 Roadmap

### Phase 1: D1.1:2020 Stabilization (Weeks 1-2)
- [x] Create 30-test golden dataset
- [x] Integrate with CI/CD
- [ ] Achieve 95% pass rate for 2 consecutive weeks

### Phase 2: D1.1:2025 Preparation (Weeks 3-4)
- [x] Create 25-test 2025 golden dataset (strategic focus)
- [ ] Finalize crosswalk CSV
- [ ] Update all TBD clause IDs
- [ ] Run first 2025 validation (target: 75% pass)

### Phase 3: Dual-Version Operation (Weeks 5-8)
- [ ] Expand 2025 dataset to 50 tests
- [ ] Achieve 90% pass rate on both datasets
- [ ] Add version selector to UI
- [ ] Pilot with 2 early-adopter schools

### Phase 4: Migration Complete (Weeks 9-12)
- [ ] Make D1.1:2025 default (keep 2020 available)
- [ ] Archive old 2020 tests (keep for historical queries)
- [ ] Continuous monitoring and dataset expansion

---

**Last Updated:** 2025-11-02  
**Maintained By:** QA & Content Teams  
**Review Frequency:** Weekly during migration, monthly post-launch

