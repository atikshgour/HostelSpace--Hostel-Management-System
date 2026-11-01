# US-16 validation record — 2026-10-31

Owner: Atiksh Gour. Independent review: pending (Anvi Srinivas). Jira issue shown by requester: #24.

Implemented fee listing, test order initiation, server verification/reconciliation, attempt history, student UI and generated migration. No live payment or real credentials used.

Actual commands and outcomes:

- `manage.py makemigrations student_services`: passed; generated `0004_feedue_paymentattempt_feedue_fee_positive_amount_and_more.py`. It warned that configured host `db` could not be resolved during migration history check.
- `manage.py check`: passed, zero issues.
- `ruff check` on changed backend sources and payment test: passed.
- Focused `pytest` against configured PostgreSQL: blocked by local password authentication failure, three setup errors.
- Focused `pytest` with explicit in-memory SQLite quick mode: three passed.
- Focused `jest app/fees/page.test.jsx --runInBand`: two passed.
- `npm.cmd run build`: passed; `/fees` and `/fees/result` included.
- `manage.py makemigrations --check --dry-run`: no model changes detected.
- PostgreSQL uniqueness/concurrency test: Not Run. Provider sandbox checkout: Not Run. Playwright complete flow: Not Run.

Remaining dependency: configure valid Razorpay test credentials and a PostgreSQL test database, provision synthetic fee dues through an authorized staff flow, run sandbox checkout and independent review. This evidence does not claim those checks passed.

## CI repair after commit `f8dd700` (2026-10-31)

The frontend Dockerfile now copies the fee feature used by `/fees`. The URL import block was corrected for Ruff. The payment adapter now uses an HTTPS connection to a fixed provider host, addressing Bandit B310.

Local results: `ruff check .` passed; `bandit -q -r config apps manage.py -x '*/tests/*'` passed; three focused payment API tests passed in explicit SQLite quick mode; `npm.cmd run build` passed and included `/fees` and `/fees/result`. `docker compose build frontend` was Not Run because the `docker` command is unavailable here. Remote CI rerun and PostgreSQL tests are pending.
