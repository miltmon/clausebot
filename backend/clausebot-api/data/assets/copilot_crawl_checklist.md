# Copilot Crawl & Reroute Checklist

## **CRAWL TARGETS:**

### **✅ Main Pages:**
- [ ] `/beta/quest-app` - Primary beta landing
- [ ] `/` - Home page with beta CTA
- [ ] `/clausetalk` - Existing content
- [ ] `/clausebot-watch-demo` - Demo page

### **✅ Stub Pages (Should 301 Redirect):**
- [ ] `/services-7` → `/beta/quest-app`
- [ ] `/services-2` → `/beta/quest-app`
- [ ] `/blank-1` → `/beta/quest-app`
- [ ] `/blank-5` → `/beta/quest-app`
- [ ] `/blank` → `/beta/quest-app`
- [ ] `/category/all-products` → `/beta/quest-app`

### **✅ CTAs to Check:**
- [ ] "Try the Beta Quest App" buttons
- [ ] "Start 10-Question Warm-Up" links
- [ ] "Study by Category" links
- [ ] "Start 25-Question Challenge" links
- [ ] "Back to MiltmonNDT" links
- [ ] "Enroll" buttons (should show "Coming Soon")

## **ANCHOR VERIFICATION:**

### **✅ Internal Links:**
- [ ] All internal links work
- [ ] No broken anchor tags
- [ ] Proper href attributes
- [ ] Consistent link styling

### **✅ External Links:**
- [ ] "Back to MiltmonNDT" links to correct URL
- [ ] UTM parameters preserved
- [ ] Links open in correct tab/window
- [ ] No dead external links

## **REDIRECT VERIFICATION:**

### **✅ 301 Redirects:**
- [ ] Stub pages redirect properly
- [ ] 301 status code returned
- [ ] Destination loads correctly
- [ ] No redirect loops

### **✅ Missing Redirects:**
- [ ] Flag any missed CTAs
- [ ] Identify broken anchors
- [ ] Check for orphaned pages
- [ ] Verify navigation flows

## **CRAWL TOOLS:**
```bash
# Basic crawl check
curl -I https://www.miltmonndt.com/beta/quest-app

# Redirect check
curl -L -I https://www.miltmonndt.com/services-7

# Link validation
# Use tools like:
# - Screaming Frog SEO Spider
# - Sitebulb
# - Ahrefs Site Audit
```

## **ISSUES TO FLAG:**
- Broken internal links
- Missing 301 redirects
- CTAs that don't work
- Orphaned pages
- Redirect loops
- Missing anchor tags

## **REVIEW FOCUS:**
- Complete site crawl
- Redirect verification
- CTA functionality
- Anchor tag validation

## **STATUS:** ✅ READY FOR COPILOT CRAWL
