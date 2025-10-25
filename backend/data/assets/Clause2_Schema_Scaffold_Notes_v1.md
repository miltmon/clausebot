# Clause 2 Database Schema Scaffold Notes v1.0

**Status:** Schema Design Complete - Ready for Implementation
**Date:** August 28, 2025
**Purpose:** Modular database architecture for multi-track expansion

---

## 🎯 **Schema Design Overview**

The **Clause 2 Database Cluster** provides a normalized, scalable foundation for storing normative references across all MiltmonNDT tracks. This design enables:

- **Cross-track compatibility** (WeldTrack™ ↔ VoltTrack™ ↔ MediTrack™ ↔ PipeTrack™)
- **AI-powered interpretation caching** for ClauseBot performance
- **Knowledge graph relationships** between standards
- **Full-text search optimization** across all references

---

## 🗄️ **Core Tables Architecture**

### **1. Standards Catalog (Master Registry)**
```sql
standards_catalog
├── standard_code (AWS_A2.4, IEC_60601_1, IEEE_C37.20.1)
├── standard_name (Full descriptive name)
├── issuing_organization (AWS, IEC, IEEE, ASME, API)
├── current_edition (2020, 2021, 2012)
├── industry_vertical (welding, electrical, medical, piping)
└── status (active, superseded, withdrawn)
```

**Purpose:** Central registry of all industry standards across tracks

### **2. Normative References (Clause 2 Equivalent)**
```sql
normative_references
├── reference_id (Unique identifier: AWS_A2.4:2020)
├── parent_standard_id (Links to standards_catalog)
├── reference_type (normative, informative, superseded)
├── reference_title (Full reference title)
├── applicability_scope (When/where this reference applies)
├── industry_tags (Array: ['welding', 'piping'])
└── cross_references (JSONB: related clauses, see-also)
```

**Purpose:** Stores all Clause 2 normative references with full metadata

### **3. Cross-Standard Mappings**
```sql
cross_standard_mappings
├── source_reference_id → target_reference_id
├── mapping_type (equivalent, similar, supersedes, references)
├── confidence_score (0.0 - 1.0)
├── mapping_notes (Human validation notes)
└── validated_by (Expert who confirmed mapping)
```

**Purpose:** Links equivalent/related references across different standards

---

## 🛠️ **Track-Specific Extensions**

### **WeldTrack™ References**
```sql
weldtrack_references
├── weld_process_applicability (['SMAW', 'GMAW', 'GTAW'])
├── material_group (Steel, Aluminum, Stainless)
├── joint_type_applicability (['groove', 'fillet'])
├── position_applicability (['1G', '2G', '3G', '4G'])
├── inspection_method (['visual', 'RT', 'UT'])
├── cwi_exam_relevance (Boolean)
└── cwe_exam_relevance (Boolean)
```

### **VoltTrack™ References**
```sql
volttrack_references
├── voltage_class (Low, Medium, High, Extra-High)
├── current_type (AC, DC, Both)
├── equipment_category (['switchgear', 'transformers'])
├── safety_classification (Class I, II, III)
├── hazardous_location_applicability (['Division 1', 'Zone 0'])
├── nec_article_references (['Article 250', 'Article 430'])
└── ieee_standard_references (['IEEE C37.2', 'IEEE 1584'])
```

### **MediTrack™ References**
```sql
meditrack_references
├── device_classification (Class I, II, III)
├── risk_category (Low, Moderate, High)
├── regulatory_pathway (510(k), PMA, De Novo)
├── iso_13485_applicability (Boolean)
├── fda_guidance_references (['FDA-2019-D-1021'])
├── iec_60601_series_applicability (Boolean)
├── sterilization_method (['EtO', 'Gamma', 'Steam'])
└── biocompatibility_testing (Boolean)
```

### **PipeTrack™ References**
```sql
pipetrack_references
├── service_classification (Normal, Category D, Category M)
├── fluid_type (['water', 'steam', 'gas', 'chemical'])
├── pressure_class (150#, 300#, 600#, 900#)
├── temperature_range (-20F to 100F, etc.)
├── material_specification (['A106', 'A53', 'A333'])
├── code_applicability (['B31.1', 'B31.3', 'B31.4'])
└── inspection_requirements (['hydro', 'pneumatic', 'NDE'])
```

---

## 🤖 **AI Integration Tables**

### **AI Interpretation Cache**
```sql
ai_interpretation_cache
├── reference_id (Links to normative_references)
├── query_hash (SHA256 of normalized query)
├── query_text (Original user question)
├── ai_response (Full ClauseBot JSON response)
├── model_used (claude-3-sonnet, gpt-4)
├── confidence_score (0.0 - 1.0)
├── validation_status (pending, validated, flagged)
├── cache_expiry (TTL for cache invalidation)
└── usage_count (Performance analytics)
```

**Purpose:** Cache ClauseBot responses for performance and cost optimization

### **Knowledge Graph Relationships**
```sql
knowledge_graph_edges
├── source_reference_id → target_reference_id
├── relationship_type (cites, supersedes, clarifies, conflicts)
├── relationship_strength (0.0 - 1.0)
├── context_metadata (JSONB: section, topic, keywords)
├── auto_discovered (Boolean: AI-discovered relationship)
└── human_validated (Boolean: Expert-confirmed relationship)
```

**Purpose:** Build knowledge graph for advanced AI reasoning

---

## 📊 **Sample Data Structure**

### **Core Standards Loaded:**
- **AWS A2.4:2020** - Standard Symbols for Welding, Brazing, and NDT
- **AWS B2.1:2014** - Specification for Welding Procedure and Performance Qualification
- **API 1104:2013** - Welding of Pipelines and Related Facilities
- **ASME IX:2021** - Welding and Brazing Qualifications
- **IEC 60601-1:2012** - Medical Electrical Equipment - General Requirements
- **IEEE C37.20.1:2015** - Metal-Enclosed Low-Voltage AC Power Circuit Breaker Switchgear

### **Cross-Track Compatibility Matrix:**
| Standard | WeldTrack™ | VoltTrack™ | MediTrack™ | PipeTrack™ |
|----------|------------|------------|------------|------------|
| AWS A2.4 | ✅ Primary | ❌ No | ❌ No | ✅ Secondary |
| ASME IX | ✅ Primary | ❌ No | ❌ No | ✅ Primary |
| IEC 60601-1 | ❌ No | ✅ Secondary | ✅ Primary | ❌ No |
| IEEE C37.20.1 | ❌ No | ✅ Primary | ✅ Secondary | ❌ No |
| API 1104 | ✅ Secondary | ❌ No | ❌ No | ✅ Primary |

---

## 🔍 **Performance Optimizations**

### **Indexes Created:**
- **Full-text search** on standard names and reference titles
- **GIN indexes** for array fields (process applicability, equipment categories)
- **Composite indexes** for common query patterns
- **Partial indexes** for cache expiry optimization

### **Views for Common Queries:**
- `v_all_references` - Track-agnostic reference search
- `v_cross_track_compatibility` - Multi-track compatibility matrix

### **Triggers:**
- Auto-update `updated_at` timestamps
- Cache invalidation on reference updates
- Cross-reference integrity checks

---

## 🚀 **Implementation Roadmap**

### **Phase 1: Core Schema (Complete)**
- [x] Design normalized schema architecture
- [x] Create track-specific extension tables
- [x] Define AI integration tables
- [x] Add performance indexes and views
- [x] Document sample data structure

### **Phase 2: Data Population (Next)**
- [ ] Load AWS A2.4, B2.1 normative references
- [ ] Load ASME IX, API 1104 normative references
- [ ] Load IEC 60601-1, IEEE C37.20.1 normative references
- [ ] Create cross-standard mappings
- [ ] Validate data integrity

### **Phase 3: ClauseBot Integration (Future)**
- [ ] Update ClauseBot to query new schema
- [ ] Implement AI response caching
- [ ] Build knowledge graph relationships
- [ ] Add cross-track reference suggestions

### **Phase 4: Track Deployment (Future)**
- [ ] Deploy WeldTrack™ with new schema
- [ ] Deploy VoltTrack™ with electrical references
- [ ] Deploy MediTrack™ with medical device standards
- [ ] Deploy PipeTrack™ with piping codes

---

## ⚡ **Integration with Bubble Dashboard**

The schema is designed to seamlessly integrate with the **Bubble WeldKnowledge Dashboard**:

```json
// Example API response using new schema
{
  "reference_id": "AWS_A2.4:2020",
  "reference_title": "Standard Symbols for Welding, Brazing, and Nondestructive Examination",
  "standard_name": "AWS A2.4",
  "issuing_organization": "American Welding Society",
  "industry_tags": ["welding"],
  "track_compatibility": {
    "weldtrack": true,
    "pipetrack": true,
    "volttrack": false,
    "meditrack": false
  },
  "cross_references": [
    "AWS_D1.1:2025",
    "ASME_IX:2021"
  ]
}
```

---

## 🎯 **Strategic Benefits**

### **Scalability**
- **Modular design** allows easy addition of new tracks
- **Normalized structure** prevents data duplication
- **Industry tagging** enables cross-track queries

### **AI Performance**
- **Response caching** reduces API costs
- **Knowledge graph** enables advanced reasoning
- **Confidence scoring** improves answer quality

### **User Experience**
- **Cross-track compatibility** shows related standards
- **Full-text search** finds relevant references quickly
- **Validation status** indicates expert-verified content

### **Business Value**
- **Multi-track licensing** opportunities
- **Enterprise integration** capabilities
- **Standards compliance** documentation
- **Knowledge base monetization**

---

## 📋 **Next Action Items**

1. **Commander Review** - Approve schema design approach
2. **Database Deployment** - Apply schema to production ClauseBot database
3. **Data Migration** - Import existing clause data into new structure
4. **ClauseBot Updates** - Modify API to use new schema
5. **Bubble Integration** - Update API contracts for new data structure

---

**Commander, the Clause 2 Database Schema Scaffold is architecturally complete and ready for deployment! This foundation will support the entire multi-track expansion strategy while maintaining performance and scalability. 🎯⚡🛡️**
