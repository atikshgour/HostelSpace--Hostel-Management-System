<!-- Owner: Atiksh Gour | US-15 / GitHub #23 | Sprint 5 | Reviewer: Anvi Srinivas (pending) -->
# US-15 verification — 2026-10-29

Requirements: FR-08, SEC-03, supporting SEC-01/04. Test: TC-FR08-01.
Initial clean branch `Atiksh` at `901b192` (US-14 committed by the user).
Implemented student mess/coupon viewing and Mess Staff-only management. No commit,
push, issue closure, deployment, production migration or data reset was performed.

## Actual commands and results

The existing Python environment and isolated synthetic PostgreSQL cluster at
127.0.0.1:55413 were used, with the dedicated local test role and Django-created
test database. No production service was used. Browser sessions were synthetic;
their values are passed on stdin, never saved to traces or evidence. JUnit/server
logs are retained only in ignored `.local/`.

| Command | Observed result |
| --- | --- |
| Backend `python manage.py makemigrations student_services --no-header` | Django 5.2.18 generated `0003_messallocation_coupon_and_more.py`; existing migrations untouched |
| Backend `python manage.py check` | No issues, zero silenced |
| Backend `python manage.py makemigrations --check --dry-run` | No changes detected |
| Backend `python -m pytest -q --junitxml=../.local/us15-test-results.xml` | **148 passed in 14.36s**: 55 new mess cases plus all 93 prior backend cases |
| Backend `python -m pytest apps/student_services/tests/browser_us15.py -q --tb=short --junitxml=../.local/us15-browser-results.xml` | **1 passed in 18.32s**; Playwright 1.56.1/headless local Chrome, live Next.js and Django with PostgreSQL |
| Frontend `npm run test:ci` | **17 passed**, six suites; nine new mess cases plus eight prior cases |
| Frontend `npm run lint` | Pass, including all three implemented mess feature modules |
| Frontend `npm run build` | Production build passed; `/mess` and `/mess/manage` included |
| Root `python -m ruff check backend` | All checks passed |
| Root `python -m bandit -r backend/config backend/apps backend/manage.py -x '*/tests/*'` | No issues; 964 application lines scanned, zero suppressed checks |
| `git diff --check` | Pass; no whitespace errors |
| `SHOW server_version` on the isolated cluster | PostgreSQL 15.19 |
| `pg_ctl -D .local/us13-pg-20261027 -m fast -w stop` | Server stopped successfully after validation |

The existing Jest coverage thresholds for home/health were preserved. Its 100%
table covers those configured baseline files only, not total mess feature coverage.
No dependencies changed and no lockfile was edited. npm audit was not rerun for
this dependency-neutral slice; the prior US-14 audit is documented separately.

## Acceptance exercised

- Active Mess Staff alone create/update records. Director, Warden, Chief Warden,
  Maintenance, Laundry and Student roles are denied, including superuser variants.
  Real session writes enforce CSRF; inactive accounts and stale changed-role
  service callers are rejected. Deletion is unavailable.
- Students receive only their own current active allocation and active valid
  coupons. Identity query parameters cannot select another student. Staff lists
  retain inactive/expired/future records for management, hidden from students.
- Inclusive start/end boundaries, expired/future/inactive records, parent allocation
  validity and India midnight against UTC are tested. Empty results are explicit.
- Blank/missing/oversized/non-string name/code, invalid/reversed dates (including
  PATCH merged with stored values), invalid identities, forged server fields and
  non-boolean active flags are rejected without writes.
- PostgreSQL constraints reject duplicate student allocations, duplicate coupon
  codes within an allocation, blank names/codes and reversed dates. Concurrent
  allocation and coupon creates yield one success/one duplicate rejection.
  Concurrent updates yield one success/one stale-version rejection. Conflicting
  coupon-code edits leave both code and version unchanged.
- UI tests cover loading, errors/retry, empty records, staff creates/updates, date
  validation, server IDs/versions, CSRF and complete staff-list pagination.
- Playwright creates an allocation and four coupons through the staff UI (valid,
  expired, future, inactive), refreshes, checks the student's visible records and
  another student's empty view, verifies a 390px viewport without horizontal
  overflow, deactivates the allocation and confirms all its coupons disappear,
  then checks that student management access shows an error and no forms.
- No ordering, redemption, QR or billing controls/endpoints were introduced.

## Implementation decisions and review limits

The source SRS fields/FR-08 and repository US-15 instructions define personal
allocation/code/validity/active status and Mess Staff-only writes. Implementation
choices are explicit in [the contract](../backend/apps/student_services/MESS_API.md):
one configurable allocation per student; coupons tied to it; inclusive dates in
Asia/Kolkata; case-sensitive coupon codes unique per allocation; required current
version on PATCH. These are implementation choices for review, not claimed earlier
team decisions. Coupon date windows need not be contained within the allocation's
window, but both must be current for student visibility. Mess configuration is
mutable, with last-updater provenance; this does not invent an immutable audit ledger.

The first backend run had 145 passes and one **test helper** error: a duplicate
Python keyword argument for the invalid allocation-ID case. Renaming the helper's
positional parameter fixed that case; no assertion was weakened. The expanded
suite subsequently passed all 148 cases. The first UI/browser runs passed.
Import formatting was fixed using Ruff. No failed attempt is recorded as a pass.

Changed paths: backend student-services models/URLs plus isolated mess serializers,
services/views, tests and generated migration; frontend mess adapter/components,
actual App Router pages/tests and browser script; Docker source packaging and lint
script; README/contracts/schema/RTM plus migration/evidence documentation. Existing
complaint implementation/history, shared CSS and other owners' modules are preserved.

US-01 still owns login/logout and the shared client foundation. Tests bootstrap
synthetic Django sessions; no sign-in-screen coverage is claimed. The scoped mess
adapter should consolidate with the shared client when that placeholder is
implemented. PostgreSQL **15.19** was used; PostgreSQL 16, Docker image build/run,
remote CI and production migration are **Not Run**. Independent review is pending.
HISTORY.md, CHANGELOG.md and owner prompt handoff remain unchanged because the
repository requires human review before the final handoff/reviewed release entry.

For Atiksh's demonstration: with approved synthetic local sessions, open
`/mess/manage` as Mess Staff, create an allocation and valid/expired/inactive
coupons, then open `/mess` as the assigned student and as another student. Edit
active status and refresh to show persisted filtering. Anvi Srinivas should review
the diff, decisions and evidence before the truthful handoff is appended.
