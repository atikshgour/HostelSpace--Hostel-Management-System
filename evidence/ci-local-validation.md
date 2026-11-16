<!-- Owner: Atiksh Gour | Reviewer: Anvi Srinivas (pending) | US-20 | Sprint 1 -->
# NFR-05 / TC-CICD-01 local evidence — 2026-10-27

Branch: `Atiksh`. Initial working tree was clean. No commit, push, deployment,
production migration or data reset was performed. Independent review is pending.
The user explicitly authorized implementing the missing minimal foundation.

## Observed checks

| Command/check | Actual result |
| --- | --- |
| `npm install --save-exact` and final `npm install --save-dev --save-exact eslint@9.39.5` | Installed dependencies and generated matching real lock; zero vulnerabilities reported |
| Final `npm ci --fetch-retries=0 --fetch-timeout=30000` | Pass; 658 packages installed, 659 audited, zero vulnerabilities; dependency deprecation warnings remain |
| `npm run lint` | Pass, no warnings |
| `npm run test:ci -- --runInBand` | 2 suites, 2 tests passed; 100% statements/branches/functions/lines for `app/page.js` and `app/health/route.js` only |
| `npm run build` | Pass; Next.js 16.4.3 production build with `/` and `/health` |
| Started built frontend with `node node_modules/next/dist/bin/next start --port 3100`; requested `/` and `/health` | Both HTTP 200; application title rendered and health returned uncached JSON; process stopped afterward |
| `npm audit --audit-level=high` | Zero vulnerabilities; subsequent final ESLint install also reported zero |
| pip-tools 7.6.2 `compile --generate-hashes` on runtime input | Generated `backend/requirements.txt` |
| pip-tools `compile --generate-hashes --allow-unsafe --strip-extras` on development input | Generated `backend/requirements-dev.txt`, including pinned pip dependency |
| `.venv/Scripts/python.exe -m pip install -r backend/requirements-dev.txt` | Pass, hash-locked backend dependencies installed |
| `ruff check .` in backend | Pass |
| `python manage.py check` with disposable local environment values | No issues, none silenced |
| `pytest -q -k 'not test_health_checks_postgresql'` | 2 passed, 1 deselected; database outage sanitization/cache policy and rejected writes |
| `bandit -r config manage.py` | No issues; 57 lines scanned, zero suppressed checks |
| `pip_audit -r backend/requirements-dev.txt --progress-spinner off` | No known vulnerabilities found |
| Parsed workflow/Compose with PyYAML | Five CI jobs and three Compose services parsed successfully; this does not replace Docker or GitHub validation |
| Executed the actual `CI required` Python script extracted from workflow with success/failure/skipped/cancelled dependency results | Exit codes 0/1/1/1 respectively |
| `git -c core.safecrlf=false diff --check` | Pass after removing an extra workflow EOF blank line |

Commands above ran from the appropriate frontend/backend directory. Backend local
checks used public disposable environment values, not account credentials.

## Issues found and corrected

- Frontend config exports initially caused two ESLint warnings; named exports fixed them.
- Jest's Node environment docblock was initially below the ownership comment; moving it
  first fixed the missing `Response` global. Asserting the exported dynamic-cache policy
  exercised the remaining route statement and satisfied coverage.
- Django `never_cache` sets multiple directives; tests now verify the required `no-store`
  directive without incorrectly requiring it to be the only directive.
- Initial development lock omitted pip's hash pin; regenerated with `--allow-unsafe`.
  An attempted install mixing a hashed requirements file and unpinned CLI packages was
  rejected by pip; installation from the corrected complete lock succeeded.
- ESLint 10 produced plugin peer conflicts. Final pin is compatible ESLint 9.39.5;
  npm reports its deprecation. Follow-up dependency work is documented in the setup guide.
- Initial registry access was denied by sandboxing; approved registry access was then used.

## Pending acceptance evidence

| Acceptance criterion | Current evidence / gap |
| --- | --- |
| Compose starts frontend, API and PostgreSQL 16 | Implemented configuration, Dockerfiles and CI smoke job; **Not Run locally**, Docker unavailable |
| PR runs lint, scanners, tests and build without secrets | Workflow implemented with read-only token, no deployment secrets and disposable fixtures; **remote run pending** |
| Failing test blocks merge | Gate behavior verified locally; **failing-test PR experiment and required-check enforcement pending** |
| main protected | Exact setup documented; **not applied or verified**, GitHub admin connection unavailable |
| PostgreSQL backend positive test | Implemented and configured in CI; **Not Run locally**, only PostgreSQL 15 is installed |

TC-CICD-01 is **partially verified, not passed**. No PR/CI URLs, Jira key or human
approval are fabricated. Deployment remains outside this requested slice.

## Review scope

Delivery: `.github/workflows/ci.yml`, `compose.yaml`, both Dockerfiles and
`.dockerignore` files, root `.env.example`.

Authorized foundation: backend manage/config health, URLs, WSGI, base/local/CI
settings, dependency inputs and generated locks, pytest/Ruff configuration and
`backend/tests/test_health.py`; frontend package/configuration and generated lock,
new `frontend/app` layout/home/health and tests. Existing feature modules and shared
CSS are preserved. Root `app` takes precedence over the inactive starter `src/app`.

Documentation: README update, delivery setup guide and ownership sidecar, this evidence
record and appended partial RTM entry. Review the complete diff with `git diff` and
the new files with `git ls-files --others --exclude-standard`.

Anvi Srinivas should independently review the foundation and demonstrate local Compose
startup and a real PR's passing/failing checks. After human review, append the truthful
handoff to HISTORY.md and docs/prompts/atiksh/prompt-log.md per AGENTS.md.
