# US-16 fee and test payment contract

Owner: Atiksh Gour. Reviewer: Anvi Srinivas (pending).

All endpoints require an active student session. Mutations require CSRF. All reads are owner scoped and uncached. Errors use `{code,message,fields}`.

- `GET /api/fees/` returns `{results:[{id,description,amount,currency,status,paid_at,attempts:[{id,status,created_at,resolved_at}]}]}`.
- `POST /api/fees/{id}/initiate/` creates a Razorpay **test** order using the server fee amount and returns `{attempt_id,order_id,key_id,amount,currency}`. It rejects paid fees and dues with an unresolved attempt. The public test key is the only provider credential returned.
- `POST /api/payment-attempts/{id}/verify/` accepts `{payment_id,signature}` from test checkout, `{cancelled:true}` on checkout dismissal, or `{}` to refresh the result from the provider. Only the provider's captured payment matching the stored order, amount, currency and current fee marks Paid. A failed provider payment or an empty dismissed order leaves Unpaid. Other results stay Pending. Repeated resolved calls return the stored attempt.

The application does not create fee dues through a student endpoint. An authorized administrative data flow must supply them. Set `RAZORPAY_TEST_KEY_ID` and `RAZORPAY_TEST_KEY_SECRET` in the server environment to enable checkout. The key ID must begin `rzp_test_`; no live key is accepted. Never enter real payment credentials or use live funds.

The `FeeDue` and `PaymentAttempt` models are separate. Provider order ID and payment reference have database uniqueness constraints. A transaction locks both records during verification. Attempt outcomes and timestamps remain available to the student.
