# Module 4 — Inspection & Nondestructive Examination (NDE)

**Scope:** AWS D1.1:2025 (Clause 8 + Annex H), ASME B31.1 (Ch. VI + N-VI), API 510 (with ASME Section V references)
**Tags:** #awsd1.1 #cwi2025 #codeupdate

## Learning outcomes (learner-facing)

1. Execute phased inspection (pre/during/postweld) with **VT as gatekeeper** before any advanced NDE. *(verify in code)*
2. Select the **right NDE method** (VT/MT/PT/RT/UT/PAUT) based on flaw type, geometry, and contract requirements. *(verify)*
3. Apply **acceptance criteria** across structural/piping/vessels—especially **crack zero-tolerance** and rounded/linear indication limits. *(verify)*
4. Produce **audit-ready reports** (procedure, personnel quals, coverage, sensitivity, disposition, data links). *(verify)*

---

## Lesson 4.1 (≤10 min) — Roles, Hold Points, VT as the Gate

**Objectives**

* Define who does what (Owner/Engineer/Contractor/Inspector/NDE personnel).
* Set inspection hold points and access/illumination requirements.

**Script (deliver to LMS)**

* **Scope & notice:** Inspector must be notified before operations requiring inspection. *(verify)*
* **Personnel quals:** NDE personnel qualified per employer practice to recognized standards (e.g., SNT-TC-1A/CP-189/ISO 9712). AWS QC1 ≠ NDE qualification. *(verify)*
* **Phased inspection:** Pre-weld (materials, WPS/PWHT setup) → In-process (fit-up, parameters) → Postweld **VT first**, then other NDE as required. *(verify)*
* **Access & lighting:** Provide access, surface prep, and illumination that meet code/technique needs. *(verify)*

**Micro-drill (2 items)**

* "Advanced NDE can start before VT on finished welds." → **False**. *(verify)*
* "Level I may test without Level II/III oversight." → **False** (method-specific; check employer practice and code). *(verify)*

---

## Lesson 4.2 (≤10 min) — Method Selection Matrix & Core Procedures

**Objectives**

* Map discontinuity class → method.
* State essential procedure elements for each method.

**Method selection (quick matrix)**

* **Surface-breaking** (cracks, laps, porosity at surface): **VT** always; **PT/MT** per material & magnetizability. *(verify)*
* **Near-surface**: **MT** (ferromagnetic), **PT** (all materials). *(verify)*
* **Volumetric**: **RT** (gas/slag, volumetric) or **UT/PAUT** (planar, fusion issues, depth/position). *(verify)*
* **Geometry/Access limits**: Consider thickness, joint type, backing, curvature, single-sided access. *(verify)*

**Procedure must-haves (each method)**

* **PT/MT:** Surface prep, sensitivity controls, dwell, developer/indication evaluation, lighting/contrast, post-clean. *(verify)*
* **RT:** Technique (film/digital), IQI type/placement, geometry/unsharpness, density/exposure window, coverage map. *(verify)*
* **UT:** Calibration blocks, angle/frequency, scan plan, DAC/TCG, search unit checks, reflectors. *(verify)*
* **PAUT (Annex-style):** Equipment capability, focal laws, wedge/probe, coverage map (S/B/C-scan), encoded scans, file retention—**digital records are part of the deliverable.** *(verify)*

---

## Lesson 4.3 (≤10 min) — Acceptance & Disposition (Structural Focus)

**Objectives**

* Apply AWS D1.1 acceptance for VT/UT/RT/MT/PT (static vs cyclic) and tubular notes.
* Document calls that would pass audit.

**Script**

* **Cracks:** Unacceptable, any size. *(verify)*
* **Fusion/profile:** Complete fusion required; control undercut, reinforcement, and profile per weld/service class. *(verify)*
* **Rounded/linear indications:** Use the proper limits and grouping rules; cyclic service is stricter. *(verify)*
* **UT acceptance:** Use the table applicable to static/cyclic and connection type; characterize planar vs rounded, record location/length/depth. *(verify)*
* **PAUT:** Treat as UT with specific annex requirements; maintain raw data & setup files. *(verify)*

**Mini cases (short answer)**

1. Fillet weld on cyclic member shows tight toe crack under MT—**Disposition?** Crack = reject; document location/length; recommend removal/repair per code. *(verify)*
2. UT finds planar reflector at mid-thickness in CJP groove—**Next step?** Size, locate, classify, evaluate against acceptance; if reject, mark-up and proceed to disposition. *(verify)*

---

## Lesson 4.4 (≤10 min) — B31.1 & API 510: Extent, Timing, and Alternatives

**Objectives**

* Apply B31.1 extent (what must be 100% volumetric vs surface) and PWHT timing.
* Use API 510 in-service logic (Section V articles) + when NDE may substitute for pressure test.

**Script**

* **B31.1 extent:** Specific weld categories require **100% RT or 100% UT** (verify table). Smaller attachment/fillet/socket/seal welds need VT and often MT/PT per table. *(verify)*
* **Timing:** For certain P-Nos, perform NDE **after PWHT** unless design specifies otherwise; others may be before/after per rules. *(verify)*
* **Nonmetallic:** Follow N-VI—agree method/extent/acceptance with Owner; VT per Article 9. *(verify)*
* **API 510:** In-service inspection references ASME Section V (Articles 1/2/6/7/23). For some repairs/alterations, **NDE may substitute pressure test** with Engineer/Inspector approval; specify technique, coverage, sensitivity, and examiner qualification. *(verify)*
* **WFMT vs PT:** For tight surface cracks (e.g., wet H2S), **WFMT** often preferred over PT. *(verify)*

**Exit checks**

* "B31.1 weld on listed alloy got NDE **before** PWHT." → Verify material group; may need **post-PWHT** exam. *(verify)*
* "API 510 alteration without pressure test." → Allowable only with proper **NDE substitution plan** and approvals. *(verify)*

---

## Practical artifacts (ready to publish)

1. **VT Card — Field Checklist (fillable)**

   * Work ID, joint ID, WPS ref; lighting check; surface prep; profile/size/undercut; crack check; disposition + (verify in code).

2. **NDE Request & Report (one-pager)**

   * Method; procedure ID/rev; calibration/technique essentials (IQI, focal laws, search units); coverage map; sensitivity; personnel quals; findings table (type, size, loc, class); **Disposition** (Accept/Repair/Re-examine) + (verify).

3. **PAUT Mini Scan-Plan (template)**

   * Equipment; probe/wedge; focal laws; coverage slices; encoder settings; calibration (block/reflectors); data package naming & retention; acceptance reference; operator certs. *(verify in annex/Section V)*

4. **Method Selection Card (laminated)**

   * Discontinuity → VT/PT/MT/RT/UT/PAUT quick map + notes for cyclic/tubular/pressure service. *(verify)*

*(If you want, I can render these as fillable PDFs now.)*

---

## Short practice tasks (free-response)

* **SP-NDE-1 (Method pick):** FCAW CJP on cyclic member; suspected lack of fusion at mid-thickness; one-side access. Choose method, justify technique, state acceptance reference. *(verify)*
* **SP-NDE-2 (Timing):** Alloy weld requiring PWHT—when do you perform final UT? State rationale. *(verify)*
* **SP-NDE-3 (API 510):** Closure weld after alteration—no pressure test planned. Propose NDE substitution and approvals required. *(verify)*

---

## Quiz (10 MCQs with rationales)

1. **VT as gatekeeper**
   Advanced NDE should commence:
   A) Any time after welding  B) **After acceptable VT**  C) Before VT  D) Only after RT
   **Answer:** B — VT first prevents wasted/invalid advanced NDE. *(verify)*

2. **Personnel quals**
   Which qualifies someone to perform MT/PT?
   A) AWS QC1 only  B) **Employer program to recognized NDE standard**  C) Welder continuity  D) Any SCWI
   **Answer:** B — Method certification per employer practice/standard. *(verify)*

3. **Surface cracks on carbon steel**
   Best primary method after VT?
   A) PT  B) **MT (ferromagnetic)**  C) RT  D) ET
   **Answer:** B — MT is preferred for ferromagnetic surface/near-surface cracks. *(verify)*

4. **Volumetric gas porosity**
   Best primary volumetric method?
   A) **RT**  B) PT  C) MT  D) ET
   **Answer:** A — RT excels at volumetric gas/slag detection. *(verify)*

5. **Planar fusion flaw at depth**
   Best choice with one-side access?
   A) PT  B) RT only  C) **UT/PAUT with angle-beam plan**  D) MT only
   **Answer:** C — Angle-beam UT/PAUT for planar subsurface; one-side workable. *(verify)*

6. **Cyclic service**
   Compared to static, cyclic acceptance is generally:
   A) Looser  B) Same  C) **More restrictive**  D) Not defined
   **Answer:** C — Cyclic members have tighter limits. *(verify)*

7. **PAUT records**
   Which is true?
   A) Raw data optional  B) **Digital data (raw + setup) are part of deliverable**  C) Only screen shots  D) Only report text
   **Answer:** B — Retain raw data and setups. *(verify)*

8. **B31.1 PWHT timing**
   For listed alloy groups, final UT shall be:
   A) Before PWHT  B) **After PWHT unless design states otherwise**  C) Not required  D) Either, at contractor choice
   **Answer:** B — Timing is material-dependent; verify table/note. *(verify)*

9. **API 510 substitution**
   Skipping pressure test requires:
   A) Inspector verbal OK  B) **Engineer + Inspector approval and defined NDE plan**  C) Welder sign-off  D) Fabricator policy
   **Answer:** B — Formal approvals + specific NDE. *(verify)*

10. **Rounded indications grouping rule**
    When grouped tightly in a line they can be:
    A) Always acceptable  B) **Rejectable per grouping limits**  C) Ignored if random  D) Only rejectable in vessels
    **Answer:** B — Grouping limits apply; check code table. *(verify)*

*(Rationales in LMS end with "(verify in code)" and avoid verbatim quotes.)*

---

## Drop-in seeds (JSON)

**module**

```json
{
  "course_slug": "cwi-core",
  "module_slug": "m4-nde",
  "title": "Module 4 — Inspection & NDE",
  "order_index": 4,
  "status": "active",
  "tags": ["awsd1.1","cwi2025","codeupdate","b31.1","api510"]
}
```

**lessons**

```json
[
  {"module_slug":"m4-nde","lesson_slug":"l1-vt-holdpoints","title":"Roles, Hold Points, and VT Gate","duration_min":10,"content_markdown":"## VT First\\n- Inspector notice; VT before advanced NDE; personnel quals per recognized standards. (verify)\\n- Phased inspection & access/lighting requirements. (verify)"},
  {"module_slug":"m4-nde","lesson_slug":"l2-methods-procedures","title":"Method Selection & Core Procedures","duration_min":10,"content_markdown":"## Selection\\n- Surface vs volumetric mapping. (verify)\\n## Procedures\\n- PT/MT, RT, UT, PAUT essentials; records. (verify)"},
  {"module_slug":"m4-nde","lesson_slug":"l3-acceptance-disposition","title":"Acceptance Criteria & Dispositions (Structural)","duration_min":10,"content_markdown":"## Acceptance\\n- Cracks, fusion, rounded/linear limits; static vs cyclic; UT tables; PAUT data. (verify)\\n## Dispositions\\n- Accept/Repair/Re-examine with clause anchors. (verify)"},
  {"module_slug":"m4-nde","lesson_slug":"l4-b31-api510","title":"Power Piping & Pressure Vessels: B31.1 + API 510","duration_min":10,"content_markdown":"## B31.1\\n- Extent tables; PWHT timing; nonmetallic section. (verify)\\n## API 510\\n- Section V articles; pressure-test substitutions; WFMT preference cases. (verify)"}
]
```

**quiz**

```json
{"module_slug":"m4-nde","quiz_slug":"qz-m4-core","title":"M4 Core Quiz — Inspection & NDE","num_items":10,"time_limit_min":18,"attempts_allowed":3}
```

**short_tasks**

```json
[
  {"module_slug":"m4-nde","task_slug":"sp-nde-1-method-pick","title":"Method Selection on Cyclic Member","instructions":"Pick method for suspected LOF on cyclic member with one-side access; justify technique + acceptance ref (verify)."},
  {"module_slug":"m4-nde","task_slug":"sp-nde-2-pwht-timing","title":"PWHT Timing for B31.1 Alloy","instructions":"State when final UT occurs and why; cite (verify)."},
  {"module_slug":"m4-nde","task_slug":"sp-nde-3-510-substitution","title":"API 510 Pressure Test Substitution","instructions":"Propose NDE plan + approvals to substitute for pressure test; cite (verify)."}
]
```

**governance tags (No-Drift)**

```json
{
  "code_refs":[
    {"code":"AWS D1.1","edition":"2020"},
    {"code":"ASME B31.1","edition":"current"},
    {"code":"API 510","edition":"current"},
    {"code":"ASME Section V","edition":"current"}
  ]
}
```

**analytics**

```json
{"events":["lesson_view","quiz_start","quiz_submit","task_submit"],"module":"m4-nde"}
```

---

## Instructor crib — one-liners to model

* **Reject:** *Toe crack detected by MT on cyclic member; cracks are non-permissible. (verify)*
* **Accept:** *Rounded indications within count/size/grouping limits for static member; see table note. (verify)*
* **Hold:** *Alloy weld required PWHT; final UT scheduled **after** PWHT per material note. (verify)*
* **Plan:** *Closure weld—pressure test waived; UT shear-wave encoded path with Engineer/Inspector approval per plan. (verify)*
