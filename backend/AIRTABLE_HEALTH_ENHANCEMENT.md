# Enhanced Airtable Health Endpoint

## Code Enhancement for /health/airtable

Add this to your health endpoint to expose schema alignment without leaking secrets:

```python
def get_airtable_health() -> Dict[str, Any]:
    ok = test_airtable_connection()
    sample = None
    sample_count = 0
    field_names = []
    
    if ok:
        try:
            tbl = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE)
            records = tbl.all(view=AIRTABLE_VIEW, max_records=5)
            sample_count = len(records)
            
            if records:
                # Get field names from first record
                field_names = list(records[0]['fields'].keys())
                
                # Try to normalize first record for sample
                n = _normalize(records[0])
                if n:
                    sample = {"q": n["q"], "category": n["category"], "clause_ref": n["clause_ref"]}
        except Exception as e:
            logger.error("Health sample failed: %s", e)
            ok = False
    
    return {
        "service": "airtable",
        "status": "connected" if ok else "disconnected",
        "configured": bool(AIRTABLE_API_KEY and AIRTABLE_BASE_ID and AIRTABLE_TABLE),
        "base_prefix": f"{AIRTABLE_BASE_ID[:4]}…{AIRTABLE_BASE_ID[-3:]}" if AIRTABLE_BASE_ID else None,
        "table": AIRTABLE_TABLE,
        "view": AIRTABLE_VIEW,
        "category_field": CATEGORY_FIELD,
        "fields_present": {
            "category": CATEGORY_FIELD in field_names,
            "active": "Active" in field_names,
            "question": any(field in field_names for field in STEM_FIELDS)
        },
        "sample_count": sample_count,
        "sample": sample,
    }
```

## Benefits

- **Schema visibility:** See exactly what fields are available
- **No secret leakage:** Base ID masked, no PATs exposed
- **Instant diagnosis:** Know immediately if fields are missing/hidden
- **Sample validation:** Confirm records are accessible and parseable
