# 🚀 Vercel Stripe Integration Setup Guide

**Evidence-Based Fix for Frontend → Edge Function Connection**

---

## ✅ **What's Already Working**

Based on your evidence:
- ✅ Supabase Edge Function `create-checkout-session` exists
- ✅ Stripe test product created: "ClauseBot Pro Subscription"
- ✅ Stripe price: `price_1SNmJlGX27lkbwbwhCjF2SX9` ($19/month test)
- ✅ Webhook configured and ready
- ✅ Backend infrastructure complete

---

## ❌ **The Issue**

**Problem:** Frontend calling wrong endpoint
- ❌ Was calling: `${VITE_API_BASE}/api/create-checkout-session`
- ✅ Should call: Supabase Edge Function via `supabase.functions.invoke()`

**Result:** Edge Function has **ZERO invocations** (confirmed in logs)

---

## 🔧 **The Fix Applied**

### **Updated Files:**

#### 1. `frontend/src/pages/Checkout.tsx`
```typescript
// OLD (wrong):
const response = await fetch(`${import.meta.env.VITE_API_BASE}/api/create-checkout-session`, {...});

// NEW (correct):
const { data, error } = await supabase.functions.invoke('create-checkout-session', {
  body: {
    priceId: selectedPlan.priceId,
    plan: plan,
    successUrl: `${window.location.origin}/checkout?success=true&plan=${plan}`,
    cancelUrl: `${window.location.origin}/pricing`,
  },
});
```

#### 2. Updated Price IDs
```typescript
priceId: "price_1SNmJlGX27lkbwbwhCjF2SX9" // Your actual Stripe test price
```

---

## 📋 **Required Vercel Environment Variables**

### **Check Current Configuration:**

1. Go to: https://vercel.com/miltmonllc/clausebot/settings/environment-variables

2. **Required Variables:**

```bash
# Supabase Configuration
VITE_SUPABASE_URL=https://hqhughgdraokwmreronk.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Optional (if still using Render backend for other features)
VITE_API_BASE=https://clausebot-api.onrender.com

# Google Analytics (if applicable)
VITE_GA_ID=your-ga-id
```

### **How to Add/Update:**

```bash
# Via Vercel CLI (if linked)
vercel env add VITE_SUPABASE_URL production
vercel env add VITE_SUPABASE_PUBLISHABLE_KEY production

# Via Dashboard (recommended)
# 1. Go to Project Settings → Environment Variables
# 2. Add/Edit variables
# 3. Select: Production, Preview, Development (as needed)
# 4. Save changes
# 5. Redeploy
```

---

## 🚀 **Deployment Steps**

### **Step 1: Commit and Push Changes**

```bash
cd c:\ClauseBot_API_Deploy\clausebot
git add frontend/src/pages/Checkout.tsx
git commit -m "fix: connect checkout to Supabase Edge Function

- Update Checkout to use supabase.functions.invoke()
- Add real Stripe test price ID
- Fix frontend-to-backend connection
- Edge Function will now be invoked"
git push origin main
```

### **Step 2: Verify Vercel Environment Variables**

1. Visit: https://vercel.com/miltmonllc/clausebot/settings/environment-variables
2. Confirm `VITE_SUPABASE_URL` is set
3. Confirm `VITE_SUPABASE_PUBLISHABLE_KEY` is set

### **Step 3: Trigger Vercel Deployment**

Vercel will auto-deploy from the git push. Monitor at:
- https://vercel.com/miltmonllc/clausebot/deployments

### **Step 4: Test Checkout Flow**

Once deployed:

1. Visit: https://clausebot.vercel.app/pricing
2. Click "Upgrade to Pro"
3. On checkout page, click "Continue to Payment"
4. Should redirect to Stripe Checkout

### **Step 5: Verify Edge Function Invocation**

After test:

1. Go to: https://supabase.com/dashboard/project/hqhughgdraokwmreronk/functions/create-checkout-session/invocations
2. **Should now show: 1+ invocation** (no longer zero!)
3. Check logs for any errors

---

## 🧪 **Testing Checklist**

After deployment:

- [ ] Visit pricing page: https://clausebot.vercel.app/pricing
- [ ] Click "Upgrade to Pro" button
- [ ] Should navigate to: `/checkout?plan=pro`
- [ ] Click "Continue to Payment"
- [ ] Should redirect to Stripe Checkout page
- [ ] Complete test payment (use test card: 4242 4242 4242 4242)
- [ ] Should redirect back to success page

### **Verify in Supabase:**

- [ ] Edge Function invocations count > 0
- [ ] Check logs for successful execution
- [ ] No errors in function logs

### **Verify in Stripe:**

- [ ] New customer created
- [ ] New subscription created
- [ ] Webhook events received

### **Verify in Database:**

- [ ] Check for new record in appropriate table
- [ ] Subscription status = "trialing"
- [ ] Customer ID matches Stripe

---

## 🐛 **Troubleshooting**

### **Issue: Edge Function Still Not Invoked**

**Check:**
1. Browser console for errors
2. Network tab - is the function being called?
3. CORS errors?

**Fix:**
- Ensure Supabase URL is correct in env vars
- Check CORS settings in Supabase dashboard
- Verify anon key has proper permissions

### **Issue: "No such price" Error**

**Check:**
- Price ID in Checkout.tsx matches Stripe dashboard
- Using TEST mode price with TEST mode keys

**Fix:**
```typescript
// Confirm this matches your Stripe dashboard:
priceId: "price_1SNmJlGX27lkbwbwhCjF2SX9"
```

### **Issue: Stripe Checkout Opens But No Database Record**

**Check:**
- Webhook is configured and enabled
- Webhook secret is correct in Supabase Edge Function
- Check webhook delivery logs in Stripe

**Fix:**
- Verify webhook URL: `https://hqhughgdraokwmreronk.supabase.co/functions/v1/stripe-webhook`
- Check webhook signing secret matches

---

## 📊 **Expected Results**

### **Before Fix:**
```
Edge Function Invocations: 0
Stripe Customers: 0
Stripe Subscriptions: 0
Database Records: 0
```

### **After Fix:**
```
✅ Edge Function Invocations: 1+
✅ Stripe Customers: 1+
✅ Stripe Subscriptions: 1+
✅ Database Records: 1+
```

---

## 🎯 **Success Criteria**

You'll know it's working when:

1. ✅ Edge Function shows invocations in Supabase
2. ✅ Stripe shows new customer in test dashboard
3. ✅ Stripe shows new subscription
4. ✅ Database has subscription record
5. ✅ User receives confirmation email

---

## 📞 **Next Steps**

1. **Commit changes** (code already updated)
2. **Push to GitHub** (triggers Vercel deployment)
3. **Wait for deployment** (~2-3 minutes)
4. **Test checkout flow**
5. **Verify Edge Function invocation** (no longer zero!)
6. **Report success** with evidence:
   - Screenshot of Edge Function invocations > 0
   - Screenshot of Stripe customer created
   - Screenshot of database record

---

## 🎉 **Bottom Line**

**The fix is simple:**
- Frontend now calls correct endpoint (Supabase Edge Function)
- Using real Stripe test price ID
- All backend infrastructure already working

**Deploy, test, and verify with actual evidence.** 🚀

---

**Commit:** `fix: connect checkout to Supabase Edge Function`  
**File Modified:** `frontend/src/pages/Checkout.tsx`  
**Next:** Deploy and test with real checkout attempt

