# ClauseBot RAG MVP - Project Parking Documentation

**Park Date:** 2025-11-02  
**Park Tag:** `v1.0-rag-mvp-park`  
**Status:** ✅ Complete, Feature-Gated, Production-Safe  
**Next Owner:** Manus (Website/Content), SME Team (Crosswalk/Curriculum)

---

## 🎯 **Why We're Parking**

**Strategic Decision:** All technical implementation complete. Shifting focus to:
1. **Website work with Manus** - Content updates, marketing materials
2. **SME crosswalk completion** - D1.1:2020 → D1.1:2025 mapping
3. **Curriculum updates** - LMS modules, flashcards, exam DB expansion (Q051-Q110)

**No blocking technical issues.** System is production-ready when business/content ready.

---

## 📦 **What's Been Delivered**

### **Phase 1: RAG Backend (100% Complete)**
- ✅ PostgreSQL + pgvector schema (Supabase)
- ✅ RAG service (embed → retrieve → generate → log)
- ✅ FastAPI router (`/v1/chat/compliance`)
- ✅ Feature flag: `RAG_ENABLED=false` (safe default)
- ✅ Ingestion script for AWS D1.1:2020
- ✅ Rate limiting (10 req/min)
- ✅ Citation audit trail

### **Phase 2: Operations & CI/CD (100% Complete)**
- ✅ Smoke tests (post-deploy validation)
- ✅ Rollback playbook (30-second disable)
- ✅ Golden validator (30 tests, 90% pass threshold)
- ✅ GitHub Actions workflows (smoke + golden validation)
- ✅ Failure triage checklist
- ✅ Team responsibilities matrix

### **Phase 3: Documentation (100% Complete)**
- ✅ Deployment runbook (7-phase guide)
- ✅ Team responsibilities & escalation paths
- ✅ Stakeholder announcement template
- ✅ Complete operational guides

### **Phase 4: D1.1:2025 Migration Prep (100% Complete)**
- ✅ Crosswalk CSV (20 starter rows, 200+ needed)
- ✅ Golden dataset for D1.1:2025 (25 tests)
- ✅ Migration architecture documented
- ✅ Dual-version strategy defined

### **Phase 5: NotebookLM SSOT (100% Complete)**
- ✅ NLM metadata schema (11 new columns)
- ✅ Priority routing service (3-tier logic)
- ✅ Content hash guard (integrity verification)
- ✅ SME dashboard specification
- ✅ MiltmonNDT Q Upload Log (Q051-Q110 expansion)

---

## 🚦 **Current System State**

### **Production Environment**
```
Backend: https://clausebot-api.onrender.com
Frontend: https://clausebot.vercel.app
Status: OPERATIONAL (RAG disabled)
```

**Environment Variables (Render):**
```
RAG_ENABLED=false          # ⚠️ RAG disabled for safe parking
OPENAI_API_KEY=sk-***      # Configured but unused
SUPABASE_URL=https://***    # Database ready
SUPABASE_SERVICE_ROLE_KEY=***  # Ingestion ready
```

**Database State:**
- `clause_embeddings` table: Created, awaiting ingestion
- `chat_citations` table: Created, empty
- `clause_sme_log` table: Created (NLM SSOT)
- `miltmon_ndt_q_upload_log` table: Created (fallback queue)

### **GitHub Repository**
```
Branch: feat/welding-resources-api (merged to main)
Tag: v1.0-rag-mvp-park
Commits: 4 major feature commits (31 files, 7,195+ lines)
Status: All pushed, CI passing
```

### **What's NOT Done (Intentional)**
- ❌ AWS D1.1:2020 data NOT ingested (awaiting source files)
- ❌ RAG endpoints NOT enabled (feature flag OFF)
- ❌ D1.1:2025 crosswalk NOT finalized (SME work required)
- ❌ Airtable SME dashboard NOT set up (operational decision)
- ❌ Golden validation NOT run (no ingested data yet)

---

## 📋 **Handoff Responsibilities**

### **Manus (Website/Marketing Lead)**
**Timeline:** Immediate (Weeks 1-4)

**Deliverables:**
1. D1.1:2025 announcement page
2. Change log (Clauses 4, 5, 6, 8 highlights)
3. FAQ for inspectors ("Which edition do we test to?")
4. Training landing page updates
5. CTA blocks ("Update course", "Join pilot", "View change log")

**Resources Provided:**
- `STAKEHOLDER_ANNOUNCEMENT.md` (email template)
- `docs/crosswalk/README.md` (change categories)
- `RAG_DEPLOYMENT_SUMMARY.md` (executive overview)

**Contact:** Platform Team for technical questions

---

### **SME Team (Content/Curriculum Lead)**
**Timeline:** Weeks 2-6

**Deliverables:**
1. Complete crosswalk CSV (20 → 200+ rows)
   - Replace all `TBD` clause IDs with verified D1.1:2025 numbers
   - Update `confidence` from "high" to "verified"
   - Set `sme_verified_date` for completed rows

2. Update curriculum modules per `action` column:
   - `update_curriculum`: Refresh existing modules
   - `create_new_module`: Build PAUT, LRFD, digital RT primers
   - `update_tables_flashcards`: Refresh Table 5.8, 6.7 content

3. Expand Exam DB (Q032-Q050 → Q051-Q110)
   - Use `miltmon_ndt_q_upload_log` for priority queue
   - Focus on D1.1:2025 changed clauses

**Resources Provided:**
- `docs/crosswalk/aws_d11_2020_to_2025.csv` (starter rows)
- `ops/golden_dataset/golden_d11_2025.json` (25 test queries)
- `docs/sme_dashboard_spec.md` (workflow guide)

**Contact:** Platform Team for Airtable setup, NLM ingestion support

---

### **Platform/Engineering Team**
**Timeline:** On-demand (resumption support)

**Responsibilities:**
1. **When resuming:** Run `RESUME_CHECKLIST.md` steps
2. **Support SME workflow:** Set up Airtable base if requested
3. **Ingestion support:** Run `ingest_aws_d11.py` when source files ready
4. **Monitor:** GitHub Actions (smoke tests, golden validation)

**On-Call Escalation:**
- P0 (Production down): Existing endpoints still work (no RAG impact)
- P1 (Resume blocked): Review `RESUME_CHECKLIST.md`
- P2 (Questions): Consult `backend/DEPLOYMENT_RUNBOOK_CURSOR.md`

---

## ⏸️ **Why This Park is Safe**

### **Zero Production Risk**
1. ✅ **Feature flag OFF:** `RAG_ENABLED=false` - no new endpoints exposed
2. ✅ **Existing functionality intact:** Quiz, health, welding resources unaffected
3. ✅ **Database changes additive:** New tables don't impact existing queries
4. ✅ **No breaking changes:** All modifications backward-compatible

### **Easy Resumption**
1. ✅ **Complete documentation:** 11 comprehensive guides
2. ✅ **Automated testing:** CI/CD workflows ready to validate
3. ✅ **Clear next steps:** `RESUME_CHECKLIST.md` step-by-step
4. ✅ **Rollback ready:** 30-second disable, 5-minute full revert

### **Business Continuity**
1. ✅ **Content work unblocked:** Website, curriculum updates proceed independently
2. ✅ **SME work unblocked:** Crosswalk completion doesn't require active RAG
3. ✅ **Training unaffected:** Existing ClauseBot functionality operational
4. ✅ **Revenue protected:** No disruption to existing services

---

## 📞 **Contact Matrix**

| Role | Contact | Responsibility |
|------|---------|----------------|
| **Platform Lead** | [Add contact] | RAG architecture, deployment |
| **Content Lead** | [Add contact] | Crosswalk, curriculum updates |
| **Manus (Website)** | [Add contact] | Marketing materials, announcements |
| **SME Lead** | [Add contact] | Quiz expansion, SME workflow |
| **On-Call SRE** | [PagerDuty] | Production incidents (existing services) |

---

## 🔗 **Key Documentation Links**

**Resumption:**
- `RESUME_CHECKLIST.md` - Step-by-step unpark guide
- `backend/DEPLOYMENT_RUNBOOK_CURSOR.md` - Full deployment procedures

**Operations:**
- `ops/rollback-playbook.md` - Emergency procedures
- `backend/TEAM_RESPONSIBILITIES.md` - Ownership matrix
- `.github/workflows/GOLDEN_FAILURE_CHECKLIST.md` - Triage guide

**Migration:**
- `docs/crosswalk/aws_d11_2020_to_2025.csv` - Crosswalk template
- `ops/golden_dataset/golden_d11_2025.json` - D1.1:2025 tests
- `docs/sme_dashboard_spec.md` - SME workflow

**Reference:**
- `RAG_DEPLOYMENT_SUMMARY.md` - Executive overview
- `STAKEHOLDER_ANNOUNCEMENT.md` - Email template
- `COMMIT_MANIFEST.md` - Complete file inventory

---

## 📅 **Recommended Timeline for Resumption**

### **Phase 1: Content Foundation (Weeks 1-4)**
- Manus completes website updates
- SME team finalizes crosswalk (50% complete)
- Q032-Q050 quiz questions reviewed

### **Phase 2: Data Preparation (Weeks 5-6)**
- Obtain AWS D1.1:2020 source files (PDF or JSON)
- Run ingestion script (`backend/scripts/ingest_aws_d11.py`)
- Verify: `SELECT count(*) FROM clause_embeddings;` > 1000

### **Phase 3: Internal Validation (Weeks 7-8)**
- Enable `RAG_ENABLED=true` in Render
- Run golden validation locally
- Internal team testing (5-10 queries/day)
- Monitor costs (OpenAI usage)

### **Phase 4: Pilot (Weeks 9-12)**
- Select 2 pilot schools/contractors
- Enable for pilot users only (session-based flag)
- Collect feedback, tune thresholds
- Achieve 90% golden validation pass rate

### **Phase 5: General Availability (Month 4+)**
- Public announcement via Manus materials
- Enable for all users
- Monitor performance, costs, accuracy
- Continuous improvement based on fallback logs

**Estimated Total Timeline:** 12-16 weeks from unpark to GA

---

## ⚠️ **Important Notes**

### **Cost Considerations**
- **Current:** $0/month (RAG disabled)
- **Projected (500 queries/day):** ~$180/month OpenAI usage
- **Monitor:** Set budget alerts in OpenAI dashboard

### **Compliance & Licensing**
- AWS D1.1 content licensed from AWS
- License #: [Add when obtained]
- Citation-only mode compliant with fair use
- Full-text display requires enterprise license

### **Security**
- `SUPABASE_SERVICE_ROLE_KEY` restricted to backend only
- `OPENAI_API_KEY` rotated quarterly
- GitHub Secrets configured, not committed to repo
- Rate limiting enforces 10 req/min per session

---

## ✅ **Park Validation Checklist**

- [x] All code committed and pushed to main
- [x] Feature flag confirmed OFF in production
- [x] Existing functionality validated (smoke tests pass)
- [x] Documentation complete (11 files)
- [x] Handoff responsibilities assigned
- [x] Tag created: `v1.0-rag-mvp-park`
- [x] GitHub release published
- [x] Slack notifications sent
- [x] RESUME_CHECKLIST.md created
- [x] COMMIT_MANIFEST.md created

---

**🎉 Project successfully parked! Resume when content/business ready.**

**Questions?** Check `RESUME_CHECKLIST.md` or contact Platform Lead.

---

**Last Updated:** 2025-11-02  
**Park Tag:** `v1.0-rag-mvp-park`  
**Next Review:** When Manus completes website updates (Week 4)

