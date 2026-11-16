# Final test summary and release recommendation

Owner: Aryan Singh · Reviewer: Atiksh Gour · Stories: US-09, US-10, US-11, US-12, US-19, US-23

## Aryan's verification run (13–15 November 2026)

These are the checks Aryan ran while reviewing and importing the facilities, infrastructure and test batches onto branch `aryan` (Sprints 1–5).

**What was tested.** Branch `aryan` holds only Aryan's paths. The accounts, settings, shared UI and other members' modules are still starter templates on `main`. So every check below ran against a full copy of the team's integrated handoff snapshot, where Aryan's files are byte-identical to the committed ones. The checks have **not** been run on `aryan` merged with the other members' real branches.

Environment: macOS (Apple Silicon), Python 3.13.0, Django 5.2.18, DRF 3.16.1, Node 24.11.0, npm 11.6.2, Next.js 16.4.1, Playwright 1.64.1 (Chromium headless shell), PostgreSQL 16.15. All data was synthetic and disposable.

| Date | Check | Command | Observed result |
|---|---|---|---|
| 2026-11-13 | Django system check | `manage.py check` | No issues |
| 2026-11-13 | Migration drift | `manage.py makemigrations --check --dry-run` | No changes detected |
| 2026-11-13 | Migrations + demo seed (SQLite) | `migrate`, `seed_demo` | Succeeded; 9 demo users |
| 2026-11-13 | Full backend suite (SQLite) | `pytest -q` | **104 passed, 3 skipped** (the skips need PostgreSQL row locking) |
| 2026-11-15 | Full backend suite (PostgreSQL 16) | `pytest -q` with `HOSTELSPACE_SQLITE=0` | **107 passed, 0 skipped** |
| 2026-11-15 | Facilities backend | `pytest apps/facilities -q` | **13 passed** |
| 2026-11-14 | Frontend lint | `npm run lint` | No problems reported |
| 2026-11-14 | Frontend unit tests | `npm run test:ci` | **13 suites, 17 tests passed** |
| 2026-11-15 | Laundry + study-room Jest | `jest src/features/laundry src/features/study-room` | **2 suites, 2 tests passed** |
| 2026-11-14 | Production build | `npm run build` | Succeeded |
| 2026-11-14 | Browser workflows | `npx playwright test` against `next start` + Django `runserver`, fresh seeded SQLite DB, labelled payment simulation | **12 passed** (10 critical flows, 1 privacy check, 1 health smoke) |

Browser coverage: session/profile/mobile navigation; announcements, rules and study-room status; Warden account creation without privilege grants; automatic laundry groups, configurable return days, Ready and Collected; leave escalation; one-time attendance and deviations; complaint assignment and resolution; mess capacity; test-only payment and Admin reports; anonymous access protection.

### Not run / gaps

- **Docker / Compose:** not run, because Docker is not installed on the test machine. `compose.yaml` and both Dockerfiles are unverified at runtime.
- **Hosted CI (GitHub Actions):** not run for this branch.
- **PostgreSQL 17:** the README recommends 17+. Only 16.15 was tested.
- **Performance:** only the low-volume health smoke ran (8 sequential `/health/` requests, each under 5 s). The proposed baseline (20 users, 100 warm visits, p95 ≤ 3 s) was **not** executed.
- **Integration with teammates' branches:** not tested. Atiksh's branch has different versions of the Docker/compose/ignore files, and the team must reconcile them before merging.
- No real payment provider, deployment, backup/restore rehearsal or independent reviewer sign-off is claimed.

### Recommendation

The facilities module (study room and laundry), demo seeding and browser regression harness are ready for team review in a PR from `aryan`. They are not approved for a live hostel deployment. Before release, merge with the other members' modules on the integration branch, then re-run the backend, frontend and browser suites and the Docker startup there.

## Prior packaging record (from the team handoff snapshot, not run by Aryan)

The integrated handoff snapshot recorded these earlier results. They are kept for provenance only.

| Check | Recorded result |
|---|---|
| PostgreSQL backend | 107 passed |
| SQLite backend | 104 passed, 3 skipped |
| Frontend | 13 suites / 17 tests passed; lint and build passed |
| Browser against production frontend | 12 passed |
| Frontend dependency audit | 0 reported vulnerabilities at check time (not a security certification) |

An older record in the same snapshot reported 88 PostgreSQL / 86 SQLite tests, 16 frontend tests and 10 browser checks. The table above supersedes it.
