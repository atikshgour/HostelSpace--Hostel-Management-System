# Team integration verification - 2026-11-16

Status: implementation and automated review; independent human review pending.
The user explicitly authorized PR creation, integration of all four branches,
required fixes, pushes and integration-to-main merge after checks.
No deployment, live payment or production database action was performed.

## Source and merge review

- Anvi PR #33: `origin/pr-33` (exact GitHub PR head).
- Arin PR #34: `origin/pr-34`.
- Aryan PR #35: `origin/pr-35` (lowercase `aryan`, distinct from stale `Aryan`).
- Atiksh PR #36: `4ab7cd14910b738d53ed3ae275304922dfd8fe64`.
- All four merged into `integration` with merge commits. PR bases retargeted to
  integration so main receives one combined, tested result.
- Compared with local `Hostel Management System/`; source paths/hashes and PR
  heads are in `docs/07-maintenance/team-integration-manifest.json`.
- Anvi uploads included misplaced root modules and duplicate frontend configs.
  Canonical module versions replace these; originals/conflicts remain text under
  `docs/07-maintenance/branch-imports/`. Git ancestry retains every branch head.
- Registered all Django apps/URLs and consolidated Next.js routes into `src/app`.
  Preserved tested Python 3.12-compatible hash locks, session/CSRF proxy,
  container setup and unique payment-success constraint from Atiksh.
- PDF permissions take precedence over source-folder extensions: Director manages
  accounts and assigns complaints; Content Staff/Director publishes content and
  study status; Mess Staff updates mess/coupons; students cannot self-select.
  Warden/Chief overview cannot expose fee/complaint/laundry counters.
- Fixed a laundry handover race: receive/policy controls wait for policy loading,
  so a newly opened form uses the persisted turnaround time.
- Arin concurrency tests now import shared accounts rather than demo-only models.
- Unified browser journeys under `frontend/e2e`; tests package forwards to them.
  Fixture sessions are held in worker memory, never persisted to artifacts.

## Commands actually executed locally

Windows, Python 3.13.7, PostgreSQL 15 on isolated port 55419, Node installed locally.
CI separately targets Python 3.12, Node 22 and PostgreSQL 16.

| Command | Observed result |
|---|---|
| `ruff check backend` | Pass |
| `python backend/manage.py check` | No issues |
| `python backend/manage.py makemigrations --check --dry-run` | No changes detected |
| Fresh local database: `migrate --noinput`, `seed_demo` | All migrations applied; synthetic users seeded; existing databases not reset |
| From backend: `pytest --tb=short -q --cov=apps --cov=config ...` | 115 passed, 30.64 seconds; 76% combined branch coverage; excludes tests/migrations |
| `coverage report --include=config/health.py --fail-under=100` | 100%, pass |
| From frontend: `npm run lint` | Pass |
| `npm run test:ci -- --runInBand` | 14 suites, 18 tests pass; measured imported-module coverage 59.92% lines |
| `npm run build` | Pass; all 30 application route entries built |
| `bandit -r backend/config backend/apps backend/manage.py -x '*/tests/*' -q` | Pass |
| Chromium expanded browser run | All 10 functional journeys + health smoke passed; privacy heading mismatch was then corrected |
| `playwright test privacy.spec.js --project=chromium` after correction | Both privacy checks passed |
| From tests: `npm install --package-lock-only --ignore-scripts --offline` | Generated forwarding-package lock, no dependencies, 0 vulnerabilities |
| `git diff --check` | Pass before final documentation staging |

Initial integration test failures (demo-only import, laundry async policy race,
student display-name selector and incorrect privacy heading) were corrected and
rerun as described. These failures are not represented as successful executions.

## PDF acceptance evidence and limits

FR-01/02: real session/profile/mobile navigation, content publication and active
rules; FR-03/04: study status, automatic laundry grouping, unchanged historical
return dates, receipt-to-ready-to-collected; FR-05/06/10: captured Warden leave,
Chief escalation, one-time location attendance, duplicate/concurrent rejection,
no raw sample storage and immutable deviation weight snapshots; FR-07/08/09:
owned complaints, authorized progression, read-only student mess/coupons, simulated
payment plus signature/amount/retry tests; FR-11: Director accounts/settings and
reports with authoritative backend counts. See module API tests and browser specs.

Automated tests do not constitute all STP acceptance. Provider sandbox/live payment,
20-user/100-warm-visit load, complete manual usability acceptance, staging promotion,
production security inspection and rollback/restore rehearsal remain Not Run.
The proposed 80% target is not claimed. Human owner/reviewer sign-off is pending;
HISTORY.md is not populated with an invented human handoff.
Hosted CI and final merge URLs will be reported from actual GitHub results.


## Hosted Firefox fixture correction

Initial integration push/PR CI passed backend, frontend, security, Compose,
Chromium and Edge. Firefox rejected attendance as STALE_SAMPLE; its subsequent
worker restart also lost cached test sessions and hit the login throttle.
A local isolated probe of pinned Firefox 142.0.1 / build 1495 measured the
emulated sample age as -86398.428 seconds (about one day in the future).
The Firefox browser fixture now supplies a fresh timestamp when delivering that
synthetic position. Production timestamp handling and server freshness checks
are unchanged. A focused backend regression asserts future samples still fail.
The original failing CI run is 43921175330; corrected hosted results are checked
before merging to main.
