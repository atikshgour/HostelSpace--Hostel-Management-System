<!-- Owner: Atiksh Gour | US-13 | Sprint 4 | Reviewer: Anvi Srinivas (pending) -->
# US-13 backend verification — 2026-10-27

Requirements: FR-07 student submission/tracking portion, SEC-03; supporting SEC-01/04.
Test: TC-FR07-01. Branch: `Atiksh`, initially clean at `514f5c0`.
The user explicitly approved the minimal User/Profile dependency assigned to another owner.
No frontend files, commits, pushes, production migrations, data resets or deployments.
No independent review, Jira key, remote CI run or historical approval is claimed.

## Actual results

| Command / action | Observed result |
| --- | --- |
| Read repository instructions/contracts, Git history/diff and supplied SRS PDF pp. 3–5 | Complaint/profile fields confirmed; contracts and account models were placeholders; no category vocabulary defined |
| `python manage.py check` | No issues; none silenced |
| `python manage.py makemigrations accounts student_services --no-header` | Django 5.2.18 generated real initial migrations after removing only untouched instruction placeholders |
| `python manage.py makemigrations --check --dry-run` against isolated PostgreSQL | No changes detected |
| `python -m ruff check backend` / backend `ruff check .` | Pass after tool-fixed import formatting in the new test module |
| `python -m pytest --junitxml=../.local/us13-test-results.xml --cov=config.health --cov-report=term-missing --cov-fail-under=100 -q` | **57 passed in 8.56s**; 54 complaint/dependency cases plus three existing health tests; health coverage remains 100% |
| `python -m bandit -r backend/config backend/apps backend/manage.py -x '*/tests/*'` | No issues; 467 lines scanned, zero suppressed checks. Test assertions are checked by pytest; Bandit scans application code |
| Temporary cluster `SHOW server_version` | PostgreSQL **15.19**, not 16 |
| Stop temporary cluster with `pg_ctl ... -m fast -w stop` | Server stopped successfully; existing PostgreSQL service was not stopped or modified |

Validation used Python 3.13.7 and the already installed pinned Django 5.2.18/DRF
dependencies. No dependencies or lockfiles changed for US-13. The test cluster lived
in ignored `.local/us13-pg-20261027`, bound only to 127.0.0.1:55413, with synthetic
records and a dedicated local test role. Django created and removed its test
database; no production database was migrated. Generated local JUnit output is
retained under ignored `.local/` and is not a remote CI artifact.

## Acceptance exercised

- Valid submission gets persisted ID, `Open` status, server timestamp and profile-derived
  room. A new session client can read it back.
- Missing/blank/oversized/non-string description, invalid/inactive category,
  missing profile/room and forged protected fields reject without records.
- Students list only their own complaints; foreign and missing IDs return 404.
  Reads return current database state. Pagination is deterministic and scoped.
- All six staff roles, including superusers, are denied by this student API.
  Anonymous/inactive sessions and changed roles are denied. Real session POST
  enforces CSRF; no force-authentication bypass is used for CSRF checks.
- Students cannot update/delete either their own or another student's complaint.
- Initial history preserves actor, server time, old/new status and remarks.
  Model/QuerySet guards block history rewrites and routine deletion.
- Failed history insertion rolls back the complaint; 500 errors omit internals.
- PostgreSQL constraints reject blank room/description and unknown status.
  Concurrent submissions retain distinct IDs and complete history.
- Django hashes passwords, authenticates a real test login and enforces one profile per user.

## Issues found and corrected

The first full run had 49 passes and one failure: Django Http404 was wrapped with
generic `error` rather than `not_found`. Ownership filtering already returned 404;
the error handler was corrected and the expanded 57-case suite passed afterward.

Initial migration generation warned that the default local connection could not
authenticate while checking migration consistency, but still generated the files.
Validation then used a separate synthetic cluster and migration consistency passed.
No successful connection or migration was made to the existing database service by
that initial command.

Windows sandbox startup could not create PostgreSQL's restricted token. Approved
execution started the separate workspace cluster, which was explicitly stopped
afterward. No approval rejection occurred.

## Remaining limits / review

- PostgreSQL 16, Docker image build/start, and remote CI were **Not Run** here. CI
  targets PostgreSQL 16 and now discovers complaint tests and checks migration drift.
  The backend image now copies the enabled app modules.
- US-01 login/logout/CSRF-bootstrap and profile-management APIs remain unimplemented;
  this slice consumes sessions and adds only the approved models/middleware.
- A maintainer must provision reviewed categories; no actual category list is invented.
- US-14 staff assignment/updates, other feature modules and UI remain separate.
- Initial custom-user migrations need a fresh local test database or a reviewed
  conversion plan for databases that already used auth.User. No reset/fake migration
  or production conversion is authorized.
- History guards apply through this API/ORM interface; privileged direct SQL must
  follow retention rules. No database-administrator immutability guarantee is claimed.
- Contract/account dependency require independent review. Sprint mappings are preserved:
  user-selected/original SRS Sprint 4; prior proposed development mapping 2.

Review the actual diff with `git diff` and new files with
`git ls-files --others --exclude-standard`. Source scope: accounts models/app config,
student_services complaint modules/tests/migrations, shared settings/URLs/errors,
Docker app inclusion, pytest/lint discovery and CI scanning/migration checks.
Documentation records the scoped contract, schema, permissions, RTM and ownership.
No other owner's implemented module was overwritten.

Anvi Srinivas should demonstrate valid/invalid submission and two-session isolation,
and review category/API choices. Anvi/Arin should review the account dependency.
Append HISTORY.md and the Atiksh prompt-log handoff only after human review, as
required by AGENTS.md. Complete FR-07, remote CI and human acceptance are not claimed passed.
