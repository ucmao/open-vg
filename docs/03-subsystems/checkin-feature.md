# Daily Check-in & Streak Reward System Specification

This document details the business logic, environment configuration, API endpoints, and database schema for the **Daily Check-in & Streak Reward** feature in VidGen.

---

## 💡 Feature Overview

The daily check-in feature boosts user retention and platform engagement on the user portal:
- Users can check in once per calendar day to claim base credit rewards.
- Consecutive check-ins over multiple days trigger tier-based bonus multiplier credits.
- Missing a day resets the consecutive streak count back to Day 1.

---

## ⚙️ Environment Variables (`backend/.env`)

```bash
CHECKIN_BASE_REWARD=5                  # Base credit reward for Day 1 check-in
CHECKIN_CONSECUTIVE_BONUS=2            # Additional streak bonus credits per consecutive day
CHECKIN_MAX_CONSECUTIVE=7              # Consecutive streak multiplier cap in days
CHECKIN_REWARD_EXPIRY_DAYS=60          # Reward credit expiration period in days
```

### Credit Calculation Formula

Using default parameters (Base: 5, Multiplier: +2/day, Cap: Day 7):
- **Day 1**: 5 credits
- **Day 2**: 5 + 2 = 7 credits
- **Day 3**: 5 + 4 = 9 credits
- **Day 4**: 5 + 6 = 11 credits
- **Day 5**: 5 + 8 = 13 credits
- **Day 6**: 5 + 10 = 15 credits
- **Day 7+**: 5 + 12 = 17 credits (Streak Bonus Cap)

---

## 📡 API Specification

- `POST /api/checkin`: Perform daily check-in.
- `GET /api/checkin/status`: Query today's check-in status and streak dates.
- `GET /api/checkin/history`: Fetch paginated check-in history.

---

## 🗄️ Database Schema (`checkins`)

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | Primary Key | Record ID |
| `user_id` | Integer | Foreign Key (`users.id`) | User ID |
| `check_date` | Date | Not Null | Date (`YYYY-MM-DD`) |
| `consecutive_days` | Integer | Default 1 | Current streak count |
| `reward_credits` | Integer | Not Null | Credits awarded |

> Unique constraint `(user_id, check_date)` prevents duplicate daily claims at the database level.
