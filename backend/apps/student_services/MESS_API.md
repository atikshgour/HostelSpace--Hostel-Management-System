<!-- Owner: Atiksh Gour | US-15 / #23 | Sprint 5 (development plan: 3) | Reviewer: Anvi Srinivas (pending) -->
# Mess allocation and coupon contract

US-15 implements FR-08, SEC-03, and supporting SEC-01/04; TC-FR08-01.
The selected Sprint 5 matches the original SRS; the starter's proposed development
mapping is Sprint 3. This records the implementation for independent review, not
previous team approval. Dependencies: existing User model and Django sessions;
US-01 still owns sign-in/out and shared frontend API-client integration.

## Access and endpoints

All endpoints require an active Django session and return uncached JSON. Unsafe
requests require the session's CSRF cookie in `X-CSRFToken`. Read endpoints set
that cookie. Errors retain `{code,message,fields}`. No superuser/Director bypass:
only role `mess_staff` can create or update mess records. Students have read-only
access to their own current records; all other roles are denied that student view.

| Method | Endpoint | Access / result |
| --- | --- | --- |
| GET | `/api/mess/` | Student; `{as_of,timezone,allocation,coupons}` |
| GET | `/api/mess/students/` | Mess Staff; active student IDs/usernames/names for selection |
| GET, POST | `/api/mess/allocations/` | Mess Staff; all allocations, or create one |
| GET, PATCH | `/api/mess/allocations/{id}/` | Mess Staff; inspect/update allocation |
| GET, POST | `/api/mess/coupons/` | Mess Staff; all coupons, or create one |
| GET, PATCH | `/api/mess/coupons/{id}/` | Mess Staff; inspect/update coupon |

Staff list endpoints use `{count,next,previous,results}`, 20 rows per page.
Management deliberately includes inactive, expired and future records for editing.
The student endpoint does not accept a target student: query parameters cannot
override the authenticated owner. An empty result is 200 with `allocation:null`
and `coupons:[]`. Staff details return 404 for missing IDs. POST returns 201;
PATCH returns 200. DELETE/PUT and ordering/redemption endpoints are not exposed.

## Fields and validity

One configured allocation exists per student. A coupon belongs to that allocation;
it cannot be moved between allocations. The student's allocation identity also
cannot be changed by PATCH. These choices implement the story's singular assigned
mess and prevent transfers of another student's records. A staff member updates
the allocation's dates/name/active flag instead of creating a second allocation.

Create allocation:
```json
{"student":3,"mess_name":"Synthetic mess","valid_from":"2026-10-29","valid_until":"2026-11-30","is_active":true}
```

Create coupon:
```json
{"allocation":8,"code":"SYNTHETIC-COUPON","valid_from":"2026-10-29","valid_until":"2026-10-31","is_active":true}
```

IDs are illustrative; use IDs returned by the APIs. Names/codes are trimmed strings
of 1–100 / 1–80 characters, respectively; numeric coercion is rejected. Dates use
ISO `YYYY-MM-DD`; valid_until must be on/after valid_from, including on partial
updates. Both dates are required on creation. is_active defaults to true on create
and accepts only a JSON boolean. Coupon codes are case-sensitive and unique within
their allocation; a duplicate create or conflicting update returns field validation.
Codes are display records only, not redeemable tokens or payment credentials.

Current validity uses the server's date in **Asia/Kolkata**, inclusive at both
endpoints. This explicitly follows the Bangalore hostel context without changing
the application's shared timezone. The student receives only an active allocation
valid today, and only active coupons valid today for that allocation. A future,
expired or inactive allocation hides its coupons as well. Coupon dates need not
be contained within allocation dates: both independent validity windows must hold
when read. A response includes its evaluated date/timezone; refresh requests new
server state. Nothing is fabricated in the UI.

Allocation responses include `id,student,mess_name,valid_from,valid_until,is_active,
version,updated_by,updated_at`. Coupons use `allocation,code` instead of student/name.
updated_by/updated_at/version are server-owned; unexpected fields are rejected.

PATCH example:
```json
{"is_active":false,"expected_version":1}
```

At least one mutable field and the current expected_version are required. The
server increments version and records the actor/server update time atomically.
Stale edits return 400 under `expected_version`; reload and review before retrying.
No automatic replay of writes is performed. Updating an allocation does not rewrite
coupon codes or validity; staff can deactivate coupons separately. These mutable
mess records do not add an audit ledger; immutable complaint history is unchanged.

## Database and UI integration

The additive generated migration is `0003_messallocation_coupon_and_more.py`.
It adds MessAllocation and Coupon only, with protected references, a unique student
allocation, date/blank-field constraints and per-allocation code uniqueness.
Existing complaint records/migrations/history are preserved. The
[migration sidecar](../../../docs/07-maintenance/us15-migration-manifest.json)
records ownership and generation. No production migration was run.

Services lock authoritative actor/target records inside PostgreSQL transactions.
Creation locks the student or parent allocation before checking uniqueness; updates
lock the record and compare the version. Coupon operations lock parent before child.
User NO KEY UPDATE locks block role/deactivation changes while allowing FK checks.
Direct ORM/SQL callers remain responsible for authorized service use; HTTP routes
never call the model save path without service authorization.

Student page: `/mess`; Mess Staff page: `/mess/manage`. Both use shared CSS cards,
grid, spacing and focus styles. Loading, empty, error, retry and success states are
implemented; staff forms use required labels/date fields, active flags and current
version values. The scoped adapter uses the existing Next-to-Django proxy, session
cookies and CSRF. The shared US-01 client remains an unimplemented placeholder;
consolidation is pending, as for the existing complaint feature. No new dependency
or lockfile was needed. Docker copies only the implemented mess feature modules.

Before applying to an approved **local synthetic database**, inspect
`python manage.py migrate --plan`, then apply `python manage.py migrate` using its
local PostgreSQL configuration. Tests instead create/drop Django's isolated test
database; never point them at production. The opt-in browser test runs from backend:
`python -m pytest apps/student_services/tests/browser_us15.py -q`. It requires the
installed frontend dependencies, local Chrome, Node and free port 3315. Sessions
are synthetic and travel only through subprocess stdin; no cookie traces are saved.

See [actual verification and remaining gaps](../../../evidence/us15-validation.md).
