# AWS D1.1 Compliance Quick Reference Matrix
**ClauseBot Integration - Visual Acceptance Criteria**

---

## **Section 6: Inspection and Testing Requirements**

| Clause | Acceptance Criteria | Pass Example | Fail Example | Code Citation |
|--------|-------------------|--------------|--------------|---------------|
| **6.9.1** | Undercut ≤ 1/32" (0.8mm) any thickness | Smooth toe transition, minor undercut <1/32" | Deep groove >1/32" at weld toe | Table 6.1, Figure 6.3 |
| **6.9.2** | No undercut for material <1/4" thick | Clean weld toe, flush profile | Any visible undercut on thin material | 6.9.2.1 |
| **6.10.1** | Porosity: scattered ≤1/32" diameter | Small isolated pores, <3% area | Clustered pores >1/32" or >5% area | Figure 6.1, 6.10.1.1 |
| **6.11.1** | Incomplete fusion: none permitted | Full penetration, complete tie-in | Cold lap, incomplete sidewall fusion | 6.11.1.1 |
| **6.12.1** | Crack indications: none permitted | No linear indications on MT/PT | Any crack-like indication | 6.12.1.1 |
| **6.13.1** | Convexity (reinforcement) limits | Crown ≤1/8" for groove welds | Excessive buildup >1/8" | Figure 6.2 |

---

## **Section 4: Fabrication Requirements**

| Clause | Requirement | Acceptable Range | Code Citation |
|--------|-------------|------------------|---------------|
| **4.3.2** | Root opening | 0" to 1/4" depending on joint | Table 4.1 |
| **4.5.1** | Bevel angle | 30° ± 5° for standard V-groove | Figure 4.1 |
| **4.6.1** | Backing strip width | 2" minimum beyond weld | 4.6.1.1 |

---

## **Section 5: Welding Requirements**

| Clause | Parameter | Limits/Requirements | Code Citation |
|--------|-----------|-------------------|---------------|
| **5.8.2** | Interpass temperature | 50°F to 500°F maximum | Table 5.1 |
| **5.15.1** | Preheat (A36 steel) | 32°F minimum, no maximum | Table 5.1 |
| **5.22.1** | Post-weld heat treatment | When required by Table 5.2 | Table 5.2 |

---

## **Visual Testing Guide (Section 6.3)**

### **✅ ACCEPTABLE Weld Profiles**
```
Groove Weld:     Fillet Weld:      Corner Weld:
    ___             /|               /|
   /   \           / |              / |
  /     \         /__|             /__|
 /______\        Base              Base
   Base
```

### **❌ REJECTABLE Conditions**
- **Undercut**: >1/32" depth
- **Overlap**: Weld metal extending beyond toe
- **Excessive Convexity**: Crown >1/8" on groove welds
- **Incomplete Fusion**: Cold lap or sidewall LOF
- **Cracks**: Any size, any location
- **Arc Strikes**: Outside weld area

---

## **Nondestructive Testing Requirements**

| Test Method | When Required | Acceptance Standard |
|-------------|---------------|-------------------|
| **Visual (VT)** | 100% of all welds | Section 6, Part C |
| **Magnetic Particle (MT)** | As specified in WPS | ASTM E709 |
| **Penetrant Testing (PT)** | Non-magnetic materials | ASTM E165 |
| **Radiographic (RT)** | Groove welds as required | Section 6, Part B |
| **Ultrasonic (UT)** | Alternative to RT | Section 6, Part B |

---

## **Common Rejection Criteria Summary**

### **Immediate Rejection (No Tolerance)**
1. Any crack indication
2. Incomplete fusion/penetration
3. Undercut on material <1/4" thick
4. Porosity >1/32" diameter or clustered

### **Measured Rejections**
1. Undercut >1/32" on material ≥1/4" thick
2. Reinforcement >1/8" on groove welds
3. Misalignment beyond Table 6.1 limits

---

## **ClauseBot AI Integration**

### **Smart Query Examples**
- *"Is 1/16" undercut acceptable on 1/2" plate?"* → **NO, exceeds 1/32" limit**
- *"Maximum reinforcement for groove weld?"* → **1/8" per Section 6.13.1**
- *"Preheat required for A36 at 40°F?"* → **NO, minimum is 32°F**

### **Visual Recognition (Coming Q2 2026)**
- Photo upload for instant defect identification
- AI-powered measurement from images
- Automated accept/reject recommendations
- Direct code citation for findings

---

## **Quick Reference for Inspectors**

### **Essential Measurements**
- **Ruler/Gauge**: 1/32" increments for undercut
- **Weld Gauge**: Crown height, leg size verification
- **Calipers**: Precise defect measurement
- **Thermometer**: Preheat/interpass verification

### **Documentation Requirements**
- **Inspection Report**: Per QC1 or equivalent
- **NDE Reports**: Certified technician results
- **Corrective Action**: Repair procedure when required
- **Final Acceptance**: Inspector signature and date

---

**🎯 This matrix provides instant access to critical AWS D1.1 acceptance criteria with ClauseBot AI integration for real-time interpretation and guidance.**
