# Credit Economics & Anti-Double-Spending Architecture

This document explains VidGen's credit-based monetization model, database row locking, and automated task failure refund pipeline.

---

## 💰 Concurrency & Lock Mechanism

To prevent double-spending or negative balances under high concurrency:

```sql
-- Atomic Row Lock during generation request
SELECT credits FROM users WHERE id = :user_id FOR UPDATE;
```

1. **Verify**: Check `user.credits >= required_credits`.
2. **Deduct**: Subtract credits atomically (`user.credits -= required_credits`).
3. **Ledger Audit**: Write record to `credit_records` with `type = 'GENERATION_DEDUCTION'`.
4. **Commit**: Release DB row lock.

---

## 🔄 Automatic Refund on Task Failure

If a Celery Worker encounters an unhandled exception or provider timeout:
1. `Work` status is updated to `FAILED`.
2. `refund_credits(user_id, work_id)` is invoked inside a DB transaction:
   - Restores credit balance (`user.credits += refunded_credits`).
   - Audit log inserted with `type = 'REFUND'`.
3. Client notified via WebSocket.
