# WeldTrack Professional - Production Launch Checklist

**Date:** October 29, 2025  
**Status:** MVP Complete, Ready for Production  
**Goal:** Launch WeldTrack Professional to first paying customers

---

## ✅ PRE-LAUNCH VERIFICATION (COMPLETE)

### **Monetization Infrastructure**
- [x] Stripe test mode checkout working
- [x] 7-day free trial configured
- [x] Webhook automation tested
- [x] Database user tracking operational
- [x] Pro access gating enforced
- [x] Subscription dashboard functional
- [x] Customer portal integration working

### **Technical Stack**
- [x] Frontend: Vercel deployment (clausebot.vercel.app)
- [x] Backend: Render API service (clausebot-api.onrender.com)
- [x] Database: Supabase (users table with RLS)
- [x] Payments: Stripe (test mode verified)
- [x] Content: Module 1-2 live, Module 3+ gated

---

## 🚀 PRODUCTION LAUNCH STEPS

### **Step 1: Switch Stripe to Production Mode (30 minutes)**

**Critical: Test mode vs Production mode**

#### **1.1 Activate Production Mode in Stripe**
1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Toggle switch from "Test mode" to "Production mode" (top right)
3. Verify business profile is complete:
   - Company name: Miltmon NDT
   - Business address
   - Support email/phone
   - Statement descriptor: "MILTMONNDT WeldTrack"

#### **1.2 Create Production Price**
```bash
# In Stripe Dashboard → Products
1. Create new product: "WeldTrack Professional"
2. Price: $49.00 USD / month
3. Billing period: Monthly
4. Trial period: 7 days (set in checkout, not product)
5. Copy the production PRICE_ID (starts with price_...)
```

#### **1.3 Get Production API Keys**
```bash
# In Stripe Dashboard → Developers → API Keys
1. Copy "Publishable key" (starts with pk_live_...)
2. Copy "Secret key" (starts with sk_live_...)
3. Store securely - these are LIVE payment credentials
```

#### **1.4 Update Vercel Environment Variables**
```bash
# Go to Vercel Dashboard → clausebot project → Settings → Environment Variables

# REPLACE test keys with production keys:
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxx
STRIPE_PRICE_ID=price_xxxxxxxxxxxxx  # New production price ID

# Keep these the same:
SITE_URL=https://clausebot.vercel.app
VITE_SUPABASE_URL=<existing>
VITE_SUPABASE_ANON_KEY=<existing>
SUPABASE_SERVICE_ROLE_KEY=<existing>
```

#### **1.5 Create Production Webhook Endpoint**
```bash
# In Stripe Dashboard → Developers → Webhooks
1. Click "Add endpoint"
2. Endpoint URL: https://clausebot.vercel.app/api/stripe-webhook
3. Description: "Production subscription lifecycle"
4. Events to send:
   - checkout.session.completed
   - customer.subscription.created
   - customer.subscription.updated
   - customer.subscription.deleted
   - invoice.payment_succeeded
   - invoice.payment_failed
5. Click "Add endpoint"
6. Copy the "Signing secret" (starts with whsec_...)
```

#### **1.6 Add Production Webhook Secret to Vercel**
```bash
# Vercel → Environment Variables
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx  # Production webhook secret
```

#### **1.7 Redeploy Frontend**
```bash
# In Vercel Dashboard
1. Go to Deployments tab
2. Click "Redeploy" on latest deployment
3. Check "Use existing build cache" (optional)
4. Confirm deployment
5. Wait for deployment to complete (~2 min)
```

#### **1.8 Production Smoke Test**
```bash
# Test with REAL credit card (will charge you!)
1. Go to https://clausebot.vercel.app/pricing
2. Click "Start 7-Day Free Trial"
3. Use YOUR REAL EMAIL and credit card
4. Complete checkout
5. Verify:
   - Redirects to /success
   - Email confirmation from Stripe
   - Dashboard shows trial status
   - Supabase users table has your record
   - Stripe Dashboard shows customer + subscription

# IMPORTANT: Cancel this test subscription immediately after verification!
# Go to Dashboard → Manage Subscription → Cancel
```

---

### **Step 2: Set Up Monitoring & Alerts (45 minutes)**

#### **2.1 UptimeRobot (Free Tier)**

**Monitor these endpoints:**
```
Service: WeldTrack Frontend
URL: https://clausebot.vercel.app
Interval: 5 minutes
Alert: Email + SMS (if available)

Service: WeldTrack API Health
URL: https://clausebot-api.onrender.com/health
Interval: 5 minutes
Alert: Email + SMS

Service: Stripe Webhook (test via Stripe dashboard)
Monitor: Check webhook delivery in Stripe logs
Alert: Manual check daily for first week
```

**Set up:**
1. Go to [UptimeRobot.com](https://uptimerobot.com)
2. Sign up (free tier: 50 monitors)
3. Add monitors above
4. Configure alert contacts (email, SMS, Slack)
5. Set alert threshold: 2 failures within 10 minutes

#### **2.2 Stripe Dashboard Monitoring**

**Daily checks (first 2 weeks):**
```
1. Customers tab: Track new signups
2. Subscriptions tab: Monitor trial→paid conversions
3. Webhooks tab: Check delivery success rate (should be >99%)
4. Failed payments: Monitor and follow up
5. Disputes/Chargebacks: Should be zero initially
```

**Set up Stripe email alerts:**
- Failed payments → Immediate email
- Subscription cancellations → Daily digest
- Successful payments → Weekly digest

#### **2.3 Supabase Monitoring**

**Database health checks:**
```sql
-- Run daily for first week
-- Check user growth
SELECT 
  DATE(created_at) as date,
  COUNT(*) as new_users,
  SUM(CASE WHEN has_pro_access THEN 1 ELSE 0 END) as pro_users
FROM users
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Check trial conversions
SELECT 
  subscription_status,
  COUNT(*) as count,
  ROUND(AVG(EXTRACT(EPOCH FROM (NOW() - created_at))/86400), 1) as avg_days_since_signup
FROM users
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY subscription_status;
```

**Set up Supabase alerts:**
1. Go to Supabase Dashboard → Project Settings
2. Enable email alerts for:
   - Database size approaching limit
   - High error rates
   - Authentication issues

#### **2.4 Vercel Monitoring**

**Check Vercel Analytics:**
```
Daily checks (first week):
- Deployment status (should be green)
- Function errors (should be <1%)
- Bandwidth usage
- Build times

Set up alerts:
- Failed deployments → Immediate email
- Function errors >5% → Immediate email
```

#### **2.5 Google Analytics (if configured)**

**Track key events:**
```
Events to monitor:
- page_view on /pricing
- button_click "Start Trial"
- checkout_initiated
- subscription_created (via webhook)
- module_started
- module_completed

Weekly review:
- Pricing page conversion rate
- Trial signup rate
- Module completion rate
```

---

### **Step 3: Support & Customer Success Setup (30 minutes)**

#### **3.1 Support Email**
```
Create: support@miltmonndt.com
Forward to: your primary email
Auto-reply: "Thanks for contacting WeldTrack support. We'll respond within 24 hours."

Test:
- Send test email
- Verify auto-reply
- Verify forwarding
```

#### **3.2 Support Documentation (Minimal MVP)**

**Create simple FAQ page or Google Doc:**
```
Common Questions:
1. How do I start my free trial?
2. When will I be charged?
3. How do I cancel my subscription?
4. What's included in Professional vs Foundation?
5. How do I access Pro modules?
6. What if I have technical issues?
7. Do you offer refunds?
8. Can I switch plans?

Link from:
- Footer of website
- Pricing page
- Dashboard
- Success/checkout pages
```

#### **3.3 Customer Communication Templates**

**Welcome Email (manual for MVP):**
```
Subject: Welcome to WeldTrack Professional! 🎉

Hi [Name],

Thanks for starting your free trial of WeldTrack Professional!

Here's what you get:
✓ Full access to all learning modules
✓ 200+ AWS D1.1:2025 exam questions
✓ Progress tracking and analytics
✓ 7 days free, then $49/month

Getting Started:
1. Visit your dashboard: https://clausebot.vercel.app/dashboard
2. Start with Module 1: AWS D1.1 Fundamentals
3. Track your progress and aim for 70%+ scores

Questions? Reply to this email or visit [support link]

Your trial ends: [Date]
You can cancel anytime before then (no charge)

Happy learning!
The MiltmonNDT Team
```

**Trial Ending Reminder (2 days before - manual for MVP):**
```
Subject: Your WeldTrack trial ends in 2 days

Hi [Name],

Your free trial of WeldTrack Professional ends in 2 days ([Date]).

What happens next?
- If you do nothing: We'll charge $49 on [Date] and continue your access
- To cancel: Visit your dashboard → Manage Subscription → Cancel

So far you've completed:
- [X] modules
- [Y] questions
- [Z]% average score

Want to keep your progress and continue learning? No action needed!

Questions? Just reply to this email.

- The MiltmonNDT Team
```

---

### **Step 4: Legal & Compliance (1 hour)**

#### **4.1 Required Pages (if not already exists)**

**Create or verify:**
- [ ] Privacy Policy (https://clausebot.vercel.app/privacy)
- [ ] Terms of Service (https://clausebot.vercel.app/terms)
- [ ] Refund Policy (https://clausebot.vercel.app/refund-policy)

**Use templates:**
- [Termly.io](https://termly.io) (free tier for small businesses)
- [TermsFeed](https://www.termsfeed.com)

**Minimum requirements:**
```
Privacy Policy must include:
- What data you collect (email, payment info)
- How you use it (service delivery, billing)
- Third parties (Stripe, Vercel, Supabase)
- User rights (access, deletion, export)
- Contact information

Terms must include:
- Service description
- Payment terms (trial, subscription, cancellation)
- Refund policy (7-day trial, then no refunds after billing)
- Intellectual property
- Limitation of liability
- Dispute resolution

Refund Policy:
- Free trial: Cancel anytime during trial (no charge)
- After trial: No refunds for partial months
- Exception: Technical issues preventing access
```

#### **4.2 Link Legal Pages**
```
Add links to footer:
- Privacy Policy
- Terms of Service
- Refund Policy

Add to checkout flow:
"By clicking Start Trial, you agree to our Terms of Service and Privacy Policy"
(with clickable links)
```

---

### **Step 5: Soft Launch (First 10 Customers - Week 1)**

#### **5.1 Beta Customer Outreach**

**Target audience:**
```
Ideal beta customers:
- CWI candidates currently studying
- Welding instructors (will give feedback)
- QC inspectors needing recertification
- Your personal network in welding industry
```

**Outreach message template:**
```
Subject: Beta Access: WeldTrack CWI Exam Prep (7 days free)

Hi [Name],

I've just launched WeldTrack Professional - a focused CWI exam prep platform 
with 200+ AWS D1.1:2025 questions and structured learning modules.

As a beta user, you'll get:
✓ 7-day free trial (full access)
✓ Then $49/month (cancel anytime)
✓ Early access to new modules as we build them
✓ Direct line to me for feedback/features

Interested? Start here: https://clausebot.vercel.app/pricing

Looking for [5-10] beta users to help refine the platform before wider launch.

Questions? Just reply!

[Your name]
```

#### **5.2 Beta Customer Success Checklist**

**For each new signup (first 10 customers):**
```
Day 0 (signup):
[ ] Send personal welcome email
[ ] Add to "beta customers" tracking spreadsheet
[ ] Monitor their first module completion

Day 2:
[ ] Check if they've started any modules
[ ] If not, send gentle nudge: "Need help getting started?"

Day 5 (2 days before trial ends):
[ ] Send trial ending reminder
[ ] Ask for feedback: "How's it going? Any issues?"

Day 7 (trial ends):
[ ] If converted: Thank them, ask for testimonial
[ ] If canceled: Ask why (improve product)

Day 14:
[ ] Check usage stats (modules completed)
[ ] Send "how's it going" email
[ ] Ask for feature requests

Day 30:
[ ] Request review/testimonial
[ ] Ask for referrals
```

#### **5.3 Beta Feedback Collection**

**Create simple feedback form (Google Forms):**
```
Questions:
1. How did you hear about WeldTrack?
2. What's your role? (CWI candidate, instructor, inspector, etc.)
3. How many modules have you completed?
4. What's working well?
5. What needs improvement?
6. What features are you missing?
7. Would you recommend this to a colleague? (1-10)
8. Any other feedback?
```

**Share link:**
- In welcome email
- Dashboard footer
- After module completion (optional)

---

### **Step 6: Marketing & Growth Setup (Ongoing)**

#### **6.1 Landing Page Optimization**

**Verify messaging on https://clausebot.vercel.app:**
```
Hero section should have:
- Clear headline: "Pass the CWI Exam with Confidence"
- Subheadline: "200+ AWS D1.1:2025 questions, structured modules, 7-day free trial"
- Primary CTA: "Start Free Trial" (prominent button)
- Social proof: "Join [X] inspectors preparing for CWI certification"

Features section:
- 3-4 key benefits (mobile-friendly, exam-accurate, progress tracking)
- Screenshots or demo
- Pricing clarity

Pricing page:
- 3 tiers visible (Foundation, Professional, Enterprise)
- Clear value prop for each
- "Most Popular" badge on Professional
- FAQ section

Trust signals:
- "Based on AWS D1.1:2025"
- "7-day free trial, cancel anytime"
- "Trusted by [X] welding professionals"
```

#### **6.2 Content Marketing (Long-term)**

**Week 1-2: Validation mode (manual, low-effort)**
```
Focus: Get first 10 paying customers via direct outreach
Don't spend time on content yet - validate demand first
```

**Week 3-4: If first 10 customers convert well**
```
Start content strategy:
- LinkedIn posts (2x/week): CWI exam tips, code updates
- YouTube shorts: Quick code explanations, study tips
- Blog posts: "How to pass CWI Part B", "AWS D1.1 changes in 2025"
```

#### **6.3 Referral Program (Future)**

**Once you have 25+ customers:**
```
Simple referral incentive:
- "Refer a colleague, get 1 month free"
- They get 10% off first month
- Track via unique referral codes
```

---

## 📊 SUCCESS METRICS (First 30 Days)

### **Week 1 Goals**
```
Signups: 10 trial starts
Conversions: 3 trial→paid (30% conversion)
MRR: $147 (3 × $49)
Churn: 0 (too early)
Support tickets: <5
Uptime: >99.5%
```

### **Week 2-4 Goals**
```
Signups: 25 total trial starts
Conversions: 10 trial→paid (40% target)
MRR: $490 (10 × $49)
Churn: <10% monthly
Module completion: >50% complete at least 1 module
Uptime: >99.9%
```

### **Key Metrics to Track**

**Acquisition:**
- Trial signups per day/week
- Source of signups (direct, LinkedIn, referral)
- Pricing page conversion rate

**Activation:**
- % who complete onboarding (start Module 1)
- Time to first module completion
- Average score on first quiz

**Retention:**
- Trial→paid conversion rate (target: 35-50%)
- Monthly churn rate (target: <5%)
- Module completion rate

**Revenue:**
- MRR (Monthly Recurring Revenue)
- ARPU (Average Revenue Per User) = $49
- LTV (Lifetime Value) = $49 / monthly churn rate

**Product:**
- Average modules completed per user
- Average quiz score (should improve over time)
- Support ticket volume (should be low)

---

## 🚨 LAUNCH DAY CHECKLIST

**Morning of Launch:**
```
[ ] Verify Stripe production mode active
[ ] Test checkout flow with real card (cancel immediately after)
[ ] Check all 3 environments:
    [ ] Frontend: clausebot.vercel.app
    [ ] API: clausebot-api.onrender.com/health
    [ ] Database: Supabase console accessible
[ ] Verify webhook endpoint responding (Stripe dashboard)
[ ] Test Pro content gating (Module 3+ should be locked for free users)
[ ] Confirm monitoring active (UptimeRobot, email alerts)
[ ] Have support email ready (check every 2 hours on launch day)
```

**Launch Announcement:**
```
[ ] Post to LinkedIn
[ ] Email personal network
[ ] Post in relevant welding/CWI communities (if allowed)
[ ] Update website banner: "Now Live: Start Your Free Trial"
```

**End of Day 1:**
```
[ ] Check Stripe Dashboard for signups
[ ] Check Supabase users table
[ ] Review any error logs (Vercel functions)
[ ] Respond to any support emails
[ ] Celebrate first customer! 🎉
```

---

## 🆘 TROUBLESHOOTING

### **Common Issues & Solutions**

**Issue: Webhook not firing**
```
1. Check Stripe Dashboard → Webhooks → Event logs
2. Verify webhook URL is correct (https://clausebot.vercel.app/api/stripe-webhook)
3. Check webhook secret in Vercel matches Stripe
4. Look for errors in Vercel function logs
5. Test webhook manually in Stripe dashboard ("Send test webhook")
```

**Issue: Pro access not granted after payment**
```
1. Check webhook delivered successfully in Stripe
2. Check Supabase users table - is record created?
3. Look at user's email - does it match checkout email?
4. Check has_pro_access column value
5. Try manual update: UPDATE users SET has_pro_access = true WHERE email = 'user@email.com'
```

**Issue: Trial not counting down**
```
1. Check trial_ends_at timestamp in Supabase
2. Verify dashboard is reading correct field
3. Check timezone conversions (should be UTC in database)
```

**Issue: Payment failing**
```
1. Check Stripe Dashboard → Payments for decline reason
2. Common reasons: Insufficient funds, card declined, fraud detection
3. Stripe sends email to customer automatically
4. You can retry payment in Stripe dashboard
```

**Issue: Customer can't access dashboard**
```
1. Check if email is in localStorage (success page should set it)
2. Verify Supabase RLS policies allow read access
3. Check CORS settings on Supabase API
4. Look at browser console for errors
```

---

## ✅ LAUNCH APPROVAL

**Sign off when all items complete:**

- [ ] Stripe production mode active
- [ ] Production webhook configured
- [ ] Live payment test successful (and canceled)
- [ ] Monitoring and alerts active
- [ ] Support email configured
- [ ] Legal pages live (Privacy, Terms, Refund)
- [ ] Beta customer list ready (5-10 people)
- [ ] Launch announcement drafted
- [ ] Emergency contact available (you!) for first 24 hours

**Approved by:** _________________  
**Date:** _________________  
**First customer target:** Within 72 hours of launch

---

**YOU ARE READY TO LAUNCH! 🚀**

Remember: 
- Perfect is the enemy of shipped
- First 10 customers will be forgiving (beta users)
- Iterate based on real feedback
- Monitor closely for first week
- Celebrate small wins!

**Good luck! You've built something real. Now go get customers!** 💪

