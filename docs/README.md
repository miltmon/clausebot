# ClauseBot Documentation Index

## 📚 Monitoring Documentation

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **[MONITORING_GUIDE.md](MONITORING_GUIDE.md)** | Comprehensive operational manual (735 lines) | Full setup, incident response, disaster recovery, reporting procedures |
| **[MONITORING_QUICK_REF.md](MONITORING_QUICK_REF.md)** | One-page cheat sheet (25 lines) | Rapid triage, quick fixes, on-call reference |
| **[MONITORING_DISCOVERY_RESULTS.md](MONITORING_DISCOVERY_RESULTS.md)** | API endpoint verification audit | Understanding how monitoring targets were validated |

## 🔐 Integrity Protection

| File | Purpose |
|------|---------|
| `monitoring_quick_ref.hash` | SHA-256 checksum for MONITORING_QUICK_REF.md |

**Update hash after editing:**
```powershell
$file = "docs\MONITORING_QUICK_REF.md"
(Get-FileHash $file -Algorithm SHA256).Hash | Out-File -Encoding ascii "docs\monitoring_quick_ref.hash"
```

## 🚀 Deployment Documentation

| Document | Purpose |
|----------|---------|
| **[DEPLOY_VERIFY_ROLLBACK.md](DEPLOY_VERIFY_ROLLBACK.md)** | Deployment runbook with rollback procedures |

## 📋 Quick Links

### For New Team Members
1. Start with **MONITORING_QUICK_REF.md** for overview
2. Review **MONITORING_GUIDE.md** for comprehensive procedures
3. Bookmark **DEPLOY_VERIFY_ROLLBACK.md** for deployment emergencies

### During Incidents
1. **Quick triage:** Use MONITORING_QUICK_REF.md
2. **Complex issues:** Follow MONITORING_GUIDE.md incident response procedures
3. **Deployment failures:** Follow DEPLOY_VERIFY_ROLLBACK.md

### For Monitoring Setup (Nov 2, 2025)
1. Review **MONITORING_DISCOVERY_RESULTS.md** (understand endpoint validation)
2. Follow **MONITORING_GUIDE.md** Phase 1-5 (comprehensive setup)
3. Keep **MONITORING_QUICK_REF.md** handy (quick lookups during setup)

---

**Last Updated:** October 25, 2025  
**Monitoring Go-Live:** November 2, 2025 @ 10:00 AM PT
