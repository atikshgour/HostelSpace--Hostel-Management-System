<!-- Owner: Atiksh Gour | US-14 / GitHub #19 | Sprint 4 | Reviewer: Anvi Srinivas (pending) -->
# US-14 verification — 2026-10-29

Implemented FR-07 staff assignment/progress and SEC-01, with supporting SEC-03/04
checks. TC-FR07-01 staff portion. Initial tree was clean at `69c761e` on `Atiksh`.
No commit, push, deployment, production migration, data reset or issue closure.
Independent human review remains pending. HISTORY.md, CHANGELOG.md and owner
prompt handoff were preserved: repository instructions require human review before
appending the final handoff or recording a reviewed release.

## Actual commands and results

Commands used the existing Python environment and isolated synthetic PostgreSQL
cluster at localhost:55413, never the existing database service. Test configuration
selected the dedicated `us13_test` role and `postgres` maintenance database;
pytest created/dropped its isolated test database. No real account was provisioned.
Environment values and session cookies are not reproduced here.

| Command (backend unless specified) | Actual result |
| --- | --- |
| `python manage.py makemigrations student_services --no-header` | Django 5.2.18 generated additive `0002_complaint_assigned_to_and_more.py` |
| `python manage.py check` | No issues, zero silenced |
| `python manage.py makemigrations --check --dry-run` | No changes detected |
| `python -m pytest -q --junitxml=../.local/us14-test-results.xml` | **93 passed in 11.10s**: 36 new management cases and all 54 US-13 cases plus three health cases |
| `python -m pytest apps/student_services/tests/browser_us14.py -q --tb=short --junitxml=../.local/us14-browser-results.xml` | **1 passed in 13.52s**, Playwright 1.56.1 with local headless Chrome, live Next.js and Django plus PostgreSQL |
| Frontend `npm run test:ci` | **8 passed**, four suites; existing home/health coverage thresholds unchanged. Coverage table measures only the existing configured home/health files, not total feature coverage |
| Frontend `npm run lint` | Pass, including both implemented complaint feature modules explicitly |
| Frontend `npm run build` | Production build passed; `/complaints/manage` included |
| Root `python -m ruff check backend` | All checks passed |
| Root `python -m bandit -r backend/config backend/apps backend/manage.py -x '*/tests/*'` | No issues; zero suppressed checks |
| Frontend `npm audit --audit-level=high` | Exit 0; five low-severity findings in the existing Jest/deepmerge dependency tree; no forced dependency downgrade applied |
| `git diff --check` | Pass; no whitespace errors |
| `pg_ctl -D .local/us13-pg-20261027 -m fast -w stop` | Approved execution stopped the isolated cluster successfully; sandbox could not signal that process |

Pinned Playwright was installed with npm; its lockfile was tool-generated. The
Next.js development server also generated `frontend/AGENTS.md`; it is retained
without manual edits and recorded in the generated-artifact sidecar. The installed
Next.js client-component, rewrite and trailing-slash guides were inspected.
Windows sandbox blocked registry access and PostgreSQL restricted-token creation;
approved execution performed those actions. No automatic approval rejection occurred.
Local JUnit/browser server logs live under ignored `.local/`, not remote CI artifacts.

## Acceptance and negative checks

- Director assigns only active Maintenance Staff. Assignment/reassignment keeps
  actor, server time, old/new assignee, unchanged status and required remarks.
- Assigned Maintenance Staff or Director can advance Open → In Progress → Resolved.
  Starting requires an assignment. Skips, reversals, repeat transitions, stale
  expected status, duplicate assignments and resolved reassignment are rejected.
- Maintenance queries exclude other assignments. Missing and foreign IDs both
  return 404. Students, unrelated staff and superusers have no staff privileges.
- Inactive/changed roles are checked from authoritative database state; writes
  enforce real session CSRF and standardized JSON errors. Private responses are uncached.
- Invalid/unknown fields, invalid assignees and blank/non-string/oversized remarks
  leave state/history unchanged. Failed history insertion rolls back state.
- Two competing PostgreSQL progress transactions produce one transition and one
  stale-status rejection. Existing immutable-history guards and US-13 tests pass.
- UI tests cover loading, assignment/progress requests, expected current status,
  resolved read-only behavior, errors/retry, empty results, CSRF and staff pagination.
- Playwright exercises Director assignment, reload persistence, assigned staff
  starting/resolving, resolved refresh, other-staff empty results, and the student's
  read-only persisted final state/history via the proxied student API.

## Problems found and corrected

The initial backend run had 84 passes and one real PostgreSQL deadlock: history
foreign-key checks conflicted with user FOR UPDATE locks held by competing actors.
NO KEY UPDATE user locks preserve role/deactivation exclusion while permitting
foreign-key key-share locks; the full expanded suite now passes.

The initial frontend build exposed Windows text encoding in the new JSX; source
was normalized to UTF-8. An npm test command initially ran from the repository
root without a package.json; rerunning from frontend passed. Browser harness
attempts first exposed absent static/media test settings and were corrected with
a scoped test server fixture. Browser network checks then found a real slash
redirect loop: Next.js rewrites dropped Django's canonical trailing slash. The
proxy now preserves it and disables automatic slash removal. The unchanged full
workflow assertions subsequently passed. Early audit access was sandbox-blocked;
the approved audit completed successfully. No failed attempt is counted as a pass.

## Scope and remaining review

Changed paths comprise the complaint backend (models, services, permissions,
serializers, views, URLs, tests and generated migration); complaint UI/API adapter,
the actual Next App Router page/tests, browser harness; local CSRF/proxy/Docker
source packaging; package manifest/generated lockfile; and linked contract/schema/
RTM/migration/evidence documentation. See the working-tree diff for exact changes.
No other owner's implemented feature module was overwritten; shared CSS is reused.

US-01 still owns login/logout and the shared API-client foundation. Tests bootstrap
synthetic Django sessions; they do not claim to test a sign-in screen. The scoped
complaint API adapter must eventually consolidate with the unimplemented shared
client. Production cookie/origin setup remains deployment work. PostgreSQL 16,
Docker image build/run, remote CI and production migration are **Not Run** here;
local PostgreSQL is 15.19. No human review, approved release or review handoff is claimed.

For Atiksh's demonstration: provision only approved synthetic local accounts and
categories, open `/complaints/manage` with a Director session, assign staff with
remarks, then use the assigned staff session to start and resolve. Refresh to show
persisted status/history, and demonstrate denial for another Maintenance account.
Anvi Srinivas should independently inspect the diff and evidence; only after that
review should the truthful HISTORY and owner prompt-log handoff be appended.
