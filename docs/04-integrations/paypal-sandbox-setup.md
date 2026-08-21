# PayPal Sandbox Testing & Verification Guide

This guide explains how to set up and test PayPal payments in sandbox mode for VidGen.

---

## 🛠️ Step 1: PayPal Developer Credentials

1. Log in to [PayPal Developer Dashboard](https://developer.paypal.com/).
2. Create a Sandbox Application named `"VidGen Sandbox"`.
3. Copy your **Client ID** and **Secret Key**.

---

## ⚙️ Step 2: Environment Setup (`backend/.env`)

```bash
PAYPAL_CLIENT_ID=your_sandbox_client_id_here
PAYPAL_CLIENT_SECRET=your_sandbox_secret_here
PAYPAL_MODE=sandbox
FRONTEND_URL=http://localhost:3000
```

---

## 🧪 Step 3: Test Payment Checkout

1. Start local servers (`uvicorn` & `npm run dev`).
2. Navigate to `http://localhost:3000/recharge`.
3. Select a package and click "Buy Now".
4. When redirected to PayPal Sandbox, sign in with a **Personal Buyer Test Account** (not your Merchant Business Account) or use a test credit card:
   - **Visa Test Card**: `4111111111111111` (CVV: `123`, Expiry: Any future date).
5. Verify order capture and atomic credit top-up in backend logs.
