# Analytics Events Configuration - Phase 3

## **REQUIRED EVENTS TO TRACK:**

### **✅ Beta Landing Events:**
```javascript
// Page view tracking
gtag('event', 'beta_landing_view', {
  'page_title': 'AWS CWI Quest App Beta',
  'page_location': window.location.href,
  'custom_parameter_1': 'beta_preview'
});

// CTA click tracking
gtag('event', 'beta_cta_click', {
  'event_category': 'engagement',
  'event_label': 'warmup_10', // or 'study_category', 'challenge_25'
  'value': 1
});

// Return home tracking
gtag('event', 'return_home_click', {
  'event_category': 'navigation',
  'event_label': 'header', // or 'footer'
  'page_location': window.location.href
});
```

### **✅ UTM Parameter Tracking:**
```javascript
// Capture UTM parameters on outbound links
const urlParams = new URLSearchParams(window.location.search);
const utmSource = urlParams.get('utm_source');
const utmMedium = urlParams.get('utm_medium');
const utmCampaign = urlParams.get('utm_campaign');

// Track with outbound clicks
gtag('event', 'outbound_click', {
  'event_category': 'external_link',
  'event_label': 'miltmonndt_home',
  'utm_source': utmSource,
  'utm_medium': utmMedium,
  'utm_campaign': utmCampaign
});
```

## **IMPLEMENTATION LOCATIONS:**

### **1. Beta Landing Page (`/beta/quest-app`):**
- `beta_landing_view` on page load
- `beta_cta_click` on each CTA button
- `return_home_click` on header/footer links

### **2. Quest App Pages:**
- `return_home_click` on all "Back to MiltmonNDT" links
- UTM parameter preservation on outbound links

### **3. Event Parameters:**
```javascript
// Standard event structure
{
  'event_category': 'beta_app',
  'event_label': 'specific_action',
  'value': 1,
  'custom_parameter_1': 'additional_context'
}
```

## **VERIFICATION CHECKLIST:**

### **✅ Google Analytics 4:**
- [ ] `beta_landing_view` events firing
- [ ] `beta_cta_click` events with correct labels
- [ ] `return_home_click` events from header/footer
- [ ] UTM parameters captured on outbound links
- [ ] Real-time events visible in GA4 dashboard

### **✅ Event Testing:**
- [ ] Load `/beta/quest-app` → check for `beta_landing_view`
- [ ] Click "Start 10-Question Warm-Up" → check for `beta_cta_click`
- [ ] Click "Back to MiltmonNDT" → check for `return_home_click`
- [ ] Test with UTM parameters → verify capture

### **✅ Data Quality:**
- [ ] Event names consistent
- [ ] Parameters properly formatted
- [ ] No duplicate events
- [ ] UTM parameters preserved correctly

## **DEBUGGING:**
```javascript
// Console logging for testing
console.log('Analytics Event:', {
  event: 'beta_cta_click',
  label: 'warmup_10',
  timestamp: new Date().toISOString()
});
```

## **STATUS:** ✅ READY FOR IMPLEMENTATION
