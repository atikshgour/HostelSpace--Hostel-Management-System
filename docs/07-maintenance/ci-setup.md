# CI setup and team integration

Owner: Atiksh Gour | US-20 | Independent reviewer: Anvi Srinivas (pending).

CI runs on every branch push, pull request, merge queue and manual dispatch.
`CI required` rejects failure, cancellation and skipped prerequisite jobs.
The jobs run frontend lint/Jest/build, backend Ruff/check/migration-drift/pytest
against PostgreSQL 16, Bandit/pip-audit/npm audit, Compose build/health checks,
and the full-project browser workflows in Chromium, Edge and Firefox. Reports and
failure screenshots are artifacts. No job deploys or has production credentials.
CI/containers use the PDF baseline Python 3.12 and Node 22. Local execution on
this machine uses installed Python 3.13.7; hosted CI verifies the Python 3.12 run.

Configure GitHub main-branch protection to require `CI required` and independent
PR review. Workflow files cannot themselves enforce branch protection. The
manual release workflow builds downloadable images only; staging promotion,
production approval and recovery rehearsal remain unimplemented.

The development Compose API applies migrations to its local PostgreSQL volume
before starting Gunicorn. Synthetic accounts require the explicit local seed command
and a privately supplied password; no production configuration or data is used.

## Reproduce checks

Install `backend/requirements-dev.txt` in a virtual environment and run `npm ci`
in `frontend`. Export `DATABASE_URL` for an isolated PostgreSQL database,
`HOSTELSPACE_SQLITE=0` and `DJANGO_SETTINGS_MODULE=config.settings.ci`.
From `backend`, run `ruff check .`, `python manage.py check`,
`python manage.py makemigrations --check --dry-run`, and `pytest`.
From `frontend`, run `npm run lint`, `npm run test:ci` and `npm run build`.

Browser checks use a separate disposable database, local settings,
`PAYMENT_MODE=simulation`, `ALLOW_PAYMENT_SIMULATION=1`, and privately supplied
`HOSTELSPACE_DEMO_PASSWORD` (12+ characters). Run migrations, then
`python manage.py seed_demo`. Start Django on 127.0.0.1:8000 and the
built frontend on 127.0.0.1:3000. Run `npx playwright install chromium firefox msedge`
and `npm run test:e2e` from frontend. Fixtures are synthetic; seeding refuses
non-local settings and does not reset existing passwords.

## Integrated project

All four PR heads are integrated: Anvi #33, Arin #34, Aryan #35 and Atiksh #36.
The completed local folder supplied the runnable module versions. Shared settings
register accounts, information, leave/attendance, facilities, student-services and
Director APIs. Next.js uses only `frontend/src/app`; the old route-export generator
is retired. `tests/npm test` forwards to the same Playwright suite as frontend.

Permissions follow the PDF and the user's explicit decision to enforce it.
Director manages users/reports/settings and complaint assignment; assigned
Maintenance progresses complaints; Mess Staff changes allocations/coupons;
Content Staff/Director publishes information and study-room status; Laundry Staff
updates laundry. Students read their own records; Warden/Chief access stays scoped
to leave, attendance and deviations. See `docs/04-design/role-permissions.md`.

Conflicting uploaded files and policy tests are preserved as text in
`docs/07-maintenance/branch-imports/`. They are historical comparison material,
not executable code. Full provenance and actual verification are recorded in
`evidence/team-integration-2026-11-16.md`. Independent human review remains pending.

The supplied project uses a different migration baseline from earlier Atiksh work.
The user confirmed only disposable local databases exist. Old migrations/tests
are retained as text under `legacy-migrations`/`legacy-tests`; active migrations
match the supplied schema, plus a generated unique-success constraint. Create a
fresh local database for this version. This is not an upgrade path for databases
using the previous schema; no existing database was deleted or reset.

See `docs/05-validation/atiksh-stp-mapping.md` for the PDF test-plan mapping.
