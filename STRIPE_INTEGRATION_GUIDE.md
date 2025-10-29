# 🎯 Stripe Checkout Integration Guide

## ✅ Frontend Complete (Deployed)

Your frontend Stripe integration is **LIVE** and ready! Here's what's deployed:

### Routes
- ✅ `/pricing` - Full pricing page with 3 tiers
- ✅ `/checkout` - Stripe checkout flow with plan selection
- ✅ `/checkout?plan=pro` - Direct link to Pro plan
- ✅ `/checkout?plan=enterprise` - Direct link to Enterprise (email contact)
- ✅ `/checkout?success=true` - Success callback page

### Features
- ✅ Dynamic page titles for SEO
- ✅ Plan selection with URL params
- ✅ Success/error handling
- ✅ Email fallback for Enterprise
- ✅ Beautiful UI with loading states

---

## 🔧 Backend Setup Required

To enable live payments, add this endpoint to your backend:

### 1. **Install Stripe SDK** (Backend)

```bash
cd backend
pip install stripe
```

### 2. **Add Stripe Keys to Environment**

Add to your `backend/.env` or Render environment variables:

```bash
STRIPE_SECRET_KEY=sk_live_xxxxx  # From Stripe Dashboard
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx  # For webhook verification
```

### 3. **Create Checkout Session Endpoint** (Backend)

Add this route to your backend (e.g., `backend/clausebot_api/routes/stripe.py`):

```python
from flask import Blueprint, request, jsonify
import stripe
import os

stripe_bp = Blueprint('stripe', __name__)
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@stripe_bp.route('/api/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        data = request.json
        price_id = data.get('priceId')
        plan = data.get('plan')
        success_url = data.get('successUrl')
        cancel_url = data.get('cancelUrl')
        
        # Create Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'plan': plan
            },
            allow_promotion_codes=True,
            billing_address_collection='required',
            # Optional: prefill customer email if logged in
            # customer_email=current_user.email,
        )
        
        return jsonify({'url': session.url})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@stripe_bp.route('/api/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events (payment success, subscription updates, etc.)"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Fulfill the purchase (create user subscription, send welcome email, etc.)
        handle_checkout_session_completed(session)
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        # Handle subscription cancellation
        handle_subscription_deleted(subscription)
    
    return jsonify({'status': 'success'})


def handle_checkout_session_completed(session):
    """Create user subscription record and send welcome email"""
    # TODO: Implement your business logic
    # - Create user subscription in database
    # - Send welcome email
    # - Grant access to features
    pass


def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    # TODO: Implement your business logic
    # - Update user subscription status
    # - Revoke access
    # - Send cancellation email
    pass
```

### 4. **Register Blueprint** (Backend)

In your `backend/clausebot_api/__init__.py`:

```python
from clausebot_api.routes.stripe import stripe_bp

def create_app():
    app = Flask(__name__)
    
    # ... existing code ...
    
    app.register_blueprint(stripe_bp)
    
    return app
```

---

## 🎨 Stripe Dashboard Setup

### 1. **Create Products & Prices**

Go to: https://dashboard.stripe.com/products

**Create these products:**

1. **ClauseBot.Ai** - $49.00/month
   - Copy the Price ID (e.g., `price_1ABC123`)
   
2. **ClauseBot Pro** - $99.00/month
   - Copy the Price ID (e.g., `price_1DEF456`)

### 2. **Update Frontend Price IDs**

Edit `frontend/src/pages/Checkout.tsx` and replace the placeholder Price IDs:

```typescript
const planDetails: Record<string, { ... }> = {
  basic: {
    // ...
    priceId: "price_1ABC123", // ← Your actual Stripe Price ID
  },
  pro: {
    // ...
    priceId: "price_1DEF456", // ← Your actual Stripe Price ID
  },
  // ...
};
```

### 3. **Configure Webhooks**

Go to: https://dashboard.stripe.com/webhooks

**Add endpoint:**
- **URL**: `https://clausebot-api.onrender.com/api/stripe-webhook`
- **Events to send**:
  - `checkout.session.completed`
  - `customer.subscription.created`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
  - `invoice.payment_succeeded`
  - `invoice.payment_failed`

Copy the **Signing Secret** and add to your backend environment as `STRIPE_WEBHOOK_SECRET`.

---

## 🧪 Testing Flow

### Test Mode (Development)

1. Use Stripe **test keys** (start with `sk_test_` and `pk_test_`)
2. Visit: https://clausebot.vercel.app/pricing
3. Click "Upgrade to Pro"
4. Use test card: `4242 4242 4242 4242`
   - Expiry: Any future date
   - CVC: Any 3 digits
   - ZIP: Any 5 digits

### Live Mode (Production)

1. Switch to **live keys** in Stripe Dashboard
2. Update backend environment variables
3. Test with real credit card
4. Verify webhook events are received

---

## 📊 Current Status

### ✅ Completed
- [x] Checkout page UI
- [x] Pricing page integration
- [x] Plan selection flow
- [x] Success/error handling
- [x] Dynamic page titles
- [x] Vercel deployment

### ⏳ Pending (Backend)
- [ ] Create Stripe checkout endpoint
- [ ] Set up webhook handler
- [ ] Configure Stripe products & prices
- [ ] Update frontend with real Price IDs
- [ ] Test end-to-end payment flow
- [ ] Deploy backend changes to Render

---

## 🎯 Next Steps

1. **Set up Stripe account** (if not already done)
2. **Create products & prices** in Stripe Dashboard
3. **Add backend endpoint** (`/api/create-checkout-session`)
4. **Configure webhooks** in Stripe Dashboard
5. **Update Price IDs** in frontend `Checkout.tsx`
6. **Deploy backend** to Render
7. **Test end-to-end** flow with test cards

---

## 📞 Support

- **Stripe Docs**: https://stripe.com/docs/payments/checkout
- **Stripe Dashboard**: https://dashboard.stripe.com
- **ClauseBot Support**: support@clausebot.pro

---

**Your revenue infrastructure is ready to go live! 🚀**

