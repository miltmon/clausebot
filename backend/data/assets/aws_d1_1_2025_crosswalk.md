# AWS D1.1:2025 Code Update Summary

**Strategic Notes for CWI Instruction — Internal Tracking**
#awsd1.1 #cwi2025 #codeupdate

**Owner:** _____________ • **Backup:** _____________ • **Version:** v1.0 • **Status:** Draft for verification
**Baselines:** D1.1:2025 (teach/assess now) • **Monitor:** D1.1:2025 (verify before publish)
**No-Drift Banner:** "This content references D1.1:2025. D1.1:2025 changes pending verification."

---

## A) Overarching Changes (navigation risk)

* **Clause renumbering/reorg (verify 2025):** Expect location shifts; re-tab and re-index before instruction.
* **New Clause 2—Normative References (verify 2025):** Consolidated references moved from 1.9/Annex S → Clause 2.
* **New Clause 4—Terms & Definitions (verify 2025):** Centralized definitions moved from 1.3/Annex J → Clause 4.
  **Impact:** Update code-nav drills, tab sets, and search macros; refresh every lesson slide that screenshots clause headers.

---

## B) Crosswalk Matrix (2020 → 2025)

*(Fill the right-hand "2025 ref" after verification; teach from 2020 until QA clears.)*

| Topic                             | 2020 Ref (teach)            | 2025 Ref (verify)                     | Change Summary (plain language)            | Instruction Impact            | Downstream Action                   |
| --------------------------------- | --------------------------- | ------------------------------------- | ------------------------------------------ | ----------------------------- | ----------------------------------- |
| Normative refs consolidated       | 1.9 + Annex S               | Clause 2 (verify)                     | References centralized                     | Update nav tips               | ClauseBot map; Flashcards term card |
| Definitions centralized           | 1.3 + Annex J               | Clause 4 (verify)                     | Definitions in one clause                  | Intro slides & drills         | Flashcards Glossary set             |
| **Design—Tubular strength calcs** | Clause 10 notes             | AISC hand-off (verify)                | Static strength calcs removed → AISC       | Teach interplay w/ AISC       | Exam DB scenario note               |
| **Prequalified WPS—structure**    | Clause 5                    | Clause 5 (restructured) (verify)      | Flow matches WPS authoring                 | Re-order lesson steps         | Update WPS template/cues            |
| **Table 5.2 (prequal EVs)**       | Tbl 5.2                     | Tbl 5.2 (reorg) (verify)              | Variables re-grouped/clearer               | Retrain "EV scan"             | Flashcards; ClauseBot table map     |
| **Shielding gas options (GMAW)**  | —                           | New Tbl 5.7 (verify)                  | A5.18/A5.18M gas mapping                   | Add gas checks to WPS reviews | Exam DB items; WPS checklist        |
| **Approved base metals**          | Tbl 5.3                     | Tbl 5.3 (updated) (verify)            | Added materials                            | Preheat chart changes         | Flashcards; WPS preheat logic       |
| **Preheat/interpass**             | Tbl 5.8                     | Tbl 5.8 (updated) (verify)            | Limits adjusted/expanded                   | Revise drills                 | ClauseBot quick-calc                |
| **WPS qual—waveform tech**        | Clause 6 (notes)            | Clause 6 (revised) (verify)           | Clearer requirements                       | Add waveform scenarios        | Exam DB "pulsed vs short-arc"       |
| **CVN consolidation**             | Tbl 6.7                     | Tbl 6.7 (consolidated) (verify)       | One stop for CVN triggers                  | Teach single table nav        | Flashcards; ClauseBot link          |
| **WPS retest clarifications**     | Clause 6                    | Clause 6 (clarified) (verify)         | Retest rules clearer                       | Update decision tree          | Exam DB contrast Qs                 |
| **PJP qualification**             | Fig 5.2 ↔ Clause 6          | PJP section (reorg) (verify)          | Clarifies PJP via joint details            | Add PJP review task           | LMS practice set                    |
| **Inspection—personnel, roles**   | Clause 8                    | Clause 8 (updated) (verify)           | Inspector quals, Engineer duties clarified | Revise ethics/role slides     | Flashcards; policy sheet            |
| **Digital RT & Ug eqn**           | Clause 8 (RT-D)             | Clause 8 (aligned to ASME V) (verify) | Digital RT explicit; Ug eqn aligned        | Update RT math                | Exam DB calc item                   |
| **UT attenuation factor**         | Clause 8                    | Clause 8 (fractional dB) (verify)     | Method updated                             | Adjust UT drills              | Flashcards mini-math                |
| **PAUT—Annex H**                  | Annex H (normative in 2020) | Annex H (verify any changes)          | PAUT remains normative w/ commentary       | Deepen PAUT module            | PAUT scan plan artifact             |
| **Ovalizing alpha**               | Tubulars + notes            | Informative Annex R (verify)          | Preliminary design info moved              | Teach "where to look"         | ClauseBot pointer                   |

> **Teacher note:** Every "verify" entry is a gating item—no public teach/assess change until edition and line location are confirmed.

---

## C) Teaching Emphasis (what changes for us)

* **Navigation first:** Re-train muscle memory—new clause numbers, two new "hub" clauses (2 & 4).
* **Prequalification checks:** Gas tables, materials, and preheat updates = more checkboxes on prequal WPS template.
* **Qualification clarity:** Waveform tech + CVN in one table + PJP clarity → better "does this change force re-qual?" drills.
* **Inspection modernization:** Digital RT math alignment; PAUT procedures; personnel/Engineer duty slides refreshed.

---

## D) Downstream Worklist (who does what)

**ClauseBot (Owner: ___ | Due: ___)**

* Map new clause numbers; add fast-paths: `gas:tbl5.7`, `cvn:tbl6.7`.
* Add AISC cross-jump for tubular strength (design queries).
* Set monitor flags on all D1.1 links until 2025 verification toggled.

**LMS (Owner: ___ | Due: ___)**

* Update M2/M3/M4/M5 lessons where tables/figures referenced; add "2025 verify" notes in margins.
* Insert **Code-Nav Re-orientation** mini-lesson (5 min) at the start of D1.1 tracks.

**Flashcards (Owner: ___ | Due: ___)**

* New cards: Clause 2/4 hubs; Tbl 5.7 gases; Tbl 5.3/5.8 changes; Tbl 6.7 CVN; RT Ug formula; PAUT anchors.

**Exam DB (Owner: ___ | Due: ___)**

* Tag existing D1.1:2025 items; clone to "2025 pending" with updated clause/table placeholders.
* Add 10 new "apply the change" scenarios (waveform, gases, CVN, PJP, digital RT).

**QA/No-Drift (Owner: ___ | Due: ___)**

* Turn on **EditionVerificationBanner** across all D1.1 lessons/quizzes.
* Create one-click regression pack: 20 nav prompts → confirm clause/table in 2025.
* SLA: update within 7 days of final 2025 verification.

---

## E) Instructor crib notes (one-liners to teach the delta)

* "**Two new hubs**—Clause 2 (refs) & Clause 4 (defs). Start there."
* "**Prequal got tidier**—gas table (5.7), metals (5.3), preheat (5.8). Don't assume old ranges."
* "**Waveform & CVN clarity**—Table 6.7 is your CVN home; waveform rules are explicit."
* "**Design handoff**—static tubular strength calcs? Go to **AISC**; D1.1 points the way."
* "**Inspection is digital-forward**—RT math aligned to ASME V, PAUT remains center stage."

---

## F) JSON seeds (No-Drift + Crosswalk)

*(Adapt keys to your Supabase/LMS; safe placeholders included.)*

```json
{
  "edition_map": {
    "code": "AWS D1.1",
    "baseline": "2020",
    "monitor": "2025",
    "status": "pending_verification",
    "owners": { "primary": "___", "backup": "___" }
  },
  "diffs": [
    {
      "topic": "Normative references consolidated",
      "from": "1.9 + Annex S (2020)",
      "to": "Clause 2 (2025, verify)",
      "impact": "navigation",
      "actions": ["update_clausebot_map","retab_codebook"],
      "due": "YYYY-MM-DD"
    },
    {
      "topic": "Prequal shielding gases",
      "from": "n/a (2020)",
      "to": "Table 5.7 (2025, verify)",
      "impact": "WPS authoring",
      "actions": ["add_wps_checklist_item","create_exam_items","flashcard_new"],
      "due": "YYYY-MM-DD"
    },
    {
      "topic": "CVN consolidation",
      "from": "Table 6.7 (2020 layout)",
      "to": "Table 6.7 (2025 consolidated, verify)",
      "impact": "qualification logic",
      "actions": ["update_lesson","add_nav_drill","clausebot_shortcut_cvn"],
      "due": "YYYY-MM-DD"
    }
  ]
}
```

---

## G) Ship checklist (15 minutes)

1. Paste this doc into **/ops/editions/d1.1_2025_crosswalk.md**.
2. Add JSON seeds to **/ops/no-drift/edition_diffs.json**; link to dashboard.
3. Enable **EditionVerificationBanner** for all D1.1 lessons/quizzes.
4. Create 1× "Code-Nav Re-orientation" micro-lesson (tabs/index demo).
5. Open 4 JIRAs: ClauseBot map, LMS edits, Flashcards, Exam DB clones.

---

## H) Risk controls (what can bite us)

* **Mis-tabs after renumbering:** Mitigate via 20-prompt nav regression drill.
* **Prequal mis-application (gases/preheat):** Enforce new WPS checklist rows; require (verify) clicks.
* **CVN oversight:** Single-table teaching reduces misses; add two "CVN or not" fork items.
* **Design calc confusion:** Add AISC cross-reference card in Specialty Codes module.

---

## I) Communication snippet (Slack/Email)

> **Heads-up:** D1.1:2025 introduces clause renumbering and new Clause 2/4 hubs. Prequalified WPS content is reorganized (new gas table; updated materials/preheat), qualification clarity improves (waveform, CVN Table 6.7), and inspection modernizes (digital RT alignment, PAUT anchoring). We'll continue **teaching/testing from 2020** until 2025 text is verified. No-Drift banners are live; owners will flip statuses module-by-module after checks.

---

## J) Implementation Timeline

### **Phase 1: Preparation (Week 1-2)**
- [ ] Deploy No-Drift banners across all D1.1 content
- [ ] Create Code-Nav Re-orientation micro-lesson
- [ ] Set up edition tracking dashboard
- [ ] Assign owners and due dates for each workstream

### **Phase 2: Content Updates (Week 3-4)**
- [ ] Update ClauseBot mapping and shortcuts
- [ ] Revise LMS lessons with 2025 verify notes
- [ ] Create new flashcards for key changes
- [ ] Clone Exam DB items with 2025 placeholders

### **Phase 3: Verification & Deployment (Week 5-6)**
- [ ] Verify 2025 text against crosswalk matrix
- [ ] Update all "verify" entries with confirmed references
- [ ] Deploy updated content module by module
- [ ] Run regression testing on navigation drills

### **Phase 4: Monitoring & Refinement (Week 7-8)**
- [ ] Monitor learner performance on updated content
- [ ] Collect feedback on navigation changes
- [ ] Refine instructor crib notes based on experience
- [ ] Document lessons learned for future editions

---

*This crosswalk package ensures smooth transition from D1.1:2025 to D1.1:2025 while maintaining instructional quality and content accuracy.*
