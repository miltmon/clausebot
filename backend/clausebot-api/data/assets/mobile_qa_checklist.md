# Mobile QA Checklist - Phase 3

## **TESTING PLATFORMS:**
- **iOS Safari** (iPhone 12/13/14/15)
- **Android Chrome** (Samsung Galaxy, Pixel)

## **CRITICAL CHECKS:**

### **✅ Header Navigation:**
- [ ] "Back to MiltmonNDT" link visible and tappable
- [ ] Link uses `VITE_RETURN_HOME_URL` environment variable
- [ ] Link opens in same tab (not new tab)
- [ ] Link text readable at mobile font sizes

### **✅ Tap Targets:**
- [ ] All buttons ≥44px minimum touch target
- [ ] CTA buttons ("Start 10-Question Warm-Up", "Study by Category", "Start 25-Question Challenge")
- [ ] Category tiles have adequate spacing
- [ ] "Back to MiltmonNDT" links in header and footer
- [ ] API status badge (if present)

### **✅ Layout & Scrolling:**
- [ ] No horizontal scroll on any screen size
- [ ] Content fits within viewport width
- [ ] Vertical scrolling works smoothly
- [ ] No content cut off at edges

### **✅ Performance:**
- [ ] No Cumulative Layout Shift (CLS) on page load
- [ ] Images load without causing layout jumps
- [ ] Text renders immediately (no FOUT/FOIT)
- [ ] Smooth transitions between states

### **✅ Beta Messaging:**
- [ ] "Beta Preview — mobile-optimized; features may change." visible
- [ ] Message positioned under primary CTA
- [ ] Text readable on mobile screens
- [ ] Consistent with brand styling

## **TEST SCENARIOS:**

### **Scenario 1: Home Page Load**
1. Navigate to `/beta/quest-app`
2. Verify page loads without horizontal scroll
3. Check "Back to MiltmonNDT" visible in header
4. Confirm beta messaging present
5. Test all CTA buttons are tappable

### **Scenario 2: Navigation Flow**
1. Tap "Start 10-Question Warm-Up"
2. Verify smooth transition
3. Check "Back to MiltmonNDT" still visible
4. Test "Explain" button functionality
5. Return to home via header link

### **Scenario 3: Category Selection**
1. Tap "Study by Category"
2. Select "Definitions" category
3. Verify only that category appears
4. Check tap targets on category tiles
5. Test return navigation

## **ISSUES TO FLAG:**
- Any horizontal scrolling
- Tap targets <44px
- Missing "Back to MiltmonNDT" links
- CLS on page load
- Broken navigation flows
- Unreadable text on mobile

## **STATUS:** ✅ READY FOR TESTING
