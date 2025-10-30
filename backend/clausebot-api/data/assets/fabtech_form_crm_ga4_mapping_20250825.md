# FABTECH Lead Form → CRM & GA4 Mapping (One‑Pager)
_Last updated: 2025-08-26 02:35 _

## 1) Wix Form Fields (with types)
| Form Label | Field Key          | Type        | Required | Notes |
|------------|--------------------|-------------|----------|-------|
| Name       | name               | text        | yes      | Full name |
| Email      | email              | email       | yes      | Validate format |
| Company    | company            | text        | yes      | - |
| Track Interest | track_interest | single-select | yes   | WeldTrack, PipeTrack, StructureTrack, QualityTrack, MaterialTrack, MasterTrack |
| Lead Source | lead_source       | single-select | yes   | FABTECH Booth, Website, Social, Referral |
| Message    | message            | long-text   | no       | Optional notes |

## 2) CRM Columns (Airtable/Sheets)
| CRM Column         | From Form Key  | Example                 |
|--------------------|----------------|-------------------------|
| Contact Name       | name           | Milton Miltmon          |
| Email Address      | email          | milton@example.com      |
| Organization       | company        | MiltmonNDT              |
| Interest Category  | track_interest | WeldTrack               |
| Source Channel     | lead_source    | FABTECH Booth           |
| Message            | message        | Ready for demo          |
| Created At (UTC)   | server_time    | 2025-08-25T19:35:00Z    |

## 3) GA4 Event Spec
**Event Name:** `form_submit`
**Recommended Params:**
- `form_id` (e.g., `"fabtech_lead_2025"`)
- `lead_source` (from `lead_source`)
- `track_interest` (from `track_interest`)
- `company` (string)
- `email_domain` (derived, e.g., `example.com`)
- `value` (1)
- `currency` (`"USD"`)

**gtag() example (Wix Custom Code or Velo):**
```html
<!-- Ensure base GA4 tag is installed with your MEASUREMENT_ID -->
<script>
  // on successful submit:
  gtag('event', 'form_submit', {
    form_id: 'fabtech_lead_2025',
    lead_source: form.lead_source,
    track_interest: form.track_interest,
    company: form.company,
    email_domain: (form.email || '').split('@')[1] || '',
    value: 1,
    currency: 'USD'
  });
</script>
```

## 4) Wix → CRM Automation
- **Option A (Airtable/Make/Zapier):** POST webhook from Wix form submit → Add row to CRM table; add GA4 `form_submit` event in parallel.
- **Option B (Wix Velo HTTP):** Velo backend `http-functions.js` receives form payload → writes to Google Sheets or Airtable API → returns 200.

**Sample webhook payload (JSON):**
```json
{
  "name": "Milton Miltmon",
  "email": "milton@example.com",
  "company": "MiltmonNDT",
  "track_interest": "WeldTrack",
  "lead_source": "FABTECH Booth",
  "message": "Ready for demo",
  "server_time": "2025-08-25T19:35:00Z"
}
```

## 5) Test Plan (10 minutes)
1. Submit test lead with unique email → verify CRM row and GA4 DebugView event.
2. Ensure `email_domain` populates.
3. Verify UTM params on landing page feed into GA4 session (optional): `utm_source`, `utm_medium`, `utm_campaign=FABTECH2025`.
4. Check double‑submit prevention: disable button after first click; show spinner; re‑enable on failure only.
5. Privacy copy present; consent checkbox if needed.

## 6) Ownership
- **Form owner:** Marketing Ops
- **CRM owner:** Sales Ops
- **Analytics owner:** Data/Analytics
- **SLA:** New lead → CRM within 60s; GA4 event in DebugView within 30s.

---

### Drop‑in Velo (Wix) snippet — derive email_domain and push GA4
```js
// public/pages/<page>.js
$w.onReady(function () {
  $w('#leadForm').onWixFormSubmitted((event) => {
    const data = event.fields.reduce((acc,f)=> (acc[f.id]=f.value, acc), {});
    const emailDomain = (data.email||'').split('@')[1] || '';
    // GA4
    if (typeof window !== 'undefined' && window.gtag) {
      gtag('event','form_submit', {
        form_id: 'fabtech_lead_2025',
        lead_source: data.lead_source,
        track_interest: data.track_interest,
        company: data.company,
        email_domain: emailDomain,
        value: 1, currency: 'USD'
      });
    }
  });
});
```
