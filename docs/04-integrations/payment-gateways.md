# Payment Gateways Integration Guide

VidGen includes native support for **PayPal REST API v2** and **Stripe Webhooks** for global credit recharge packages.

---

## 💳 PayPal Integration Setup (`backend/.env`)

```bash
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_MODE=sandbox  # Use 'live' for production
FRONTEND_URL=https://yourdomain.com
```

---

## 💳 Stripe Webhook Integration (`backend/.env`)

```bash
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

When a `checkout.session.completed` event is received via webhook:
1. Validates signature with `STRIPE_WEBHOOK_SECRET`.
2. Locates order ID in transaction metadata.
3. Grants credits atomically to user account (`user.credits += package.credits`).
4. Updates order status to `COMPLETED`.
