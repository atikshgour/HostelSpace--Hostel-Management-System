# FR-09 / US-16 fee contract
Owner: Atiksh Gour; reviewer: Anvi Srinivas (pending).

Session/CSRF and no-store apply throughout. `GET /api/fees/` is student-owned;
Director may administer dues with `POST /api/fees/`. Students cannot supply identity,
amount or status at checkout. `POST /api/payments/initiate/` accepts `{fee}`;
`POST /api/payments/verify/` accepts `{attempt,payment_id,signature}`.
`GET /api/payments/attempts/` returns retained owner-scoped attempts.
Razorpay TEST credentials use `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET`.
Payment mode defaults disabled. Local-only opt-in simulation uses
`POST /api/payments/simulate/` and is not sandbox verification evidence.
Server verification checks signature, captured state, order, amount and currency.
One successful attempt per fee is enforced in PostgreSQL; retries are idempotent.
Failed/cancelled attempts retain history and leave the fee unpaid. No credentials
are collected. See the PDF mapping and actual execution evidence.
