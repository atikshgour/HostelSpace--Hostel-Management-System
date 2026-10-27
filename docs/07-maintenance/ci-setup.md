<!-- Owner: Atiksh Gour | Reviewer: Anvi Srinivas | US-20 | NFR-05 | Sprint 1 -->
# Local stack and PR verification

This change supplies the minimum foundation authorized by the user on 2026-10-27.
The existing feature modules remain instruction placeholders. Frontend uses the
conventional root `frontend/app`; Next.js gives it precedence over `src/app`.
Do not implement new features under the inactive `src/app` until the team consolidates
the route trees. Shared CSS is imported unchanged. No feature/authentication completeness is claimed.

Dependencies: Node 22, Python 3.13, Docker with Compose v2 (supporting `up --wait`),
PostgreSQL 16. Runtime package pins are generated from the checked-in input manifests.
No SQLite fallback, production migration or deployment is included.

## Run locally

1. Copy `.env.example` to `.env`.
2. Fill both blank values with locally generated random values, for example using
   `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
3. Run `docker compose config --quiet`.
4. Run `docker compose up --build --wait --wait-timeout 180`.
5. Open http://localhost:3000 and check http://localhost:3000/health and
   http://localhost:8000/api/health/. API readiness executes a real database query.
6. Run `docker compose down` to stop. The named database volume is retained.

Only frontend/API ports bind to loopback. Database is internal. Startup does not
seed data or apply migrations. US-13 now enables minimal account/profile and complaint
models; see the [module setup contract](../../backend/apps/student_services/README.md)
for explicit migration steps on a fresh local synthetic database. Existing databases
need review.

## Checks

`CI` runs on every PR without path filters, pushes to main/Atiksh, merge groups,
and manual dispatch. Jobs use read-only repository access, disable persisted
checkout credentials, reference no repository/environment secrets, and never deploy.
The database password/key in CI are public, disposable test fixtures.

- Frontend: `npm ci`, `npm run lint`, `npm run test:ci -- --runInBand`, `npm run build`.
- Backend: install `requirements-dev.txt`, `ruff check .`, `python manage.py check`,
  PostgreSQL pytest with JUnit and coverage reports.
- Security: Bandit, pip-audit (all dependencies), npm audit (high/critical gate).
- Integration: build both images; wait for all three healthy services; HTTP smoke.
- `CI required` runs even after failures and rejects any failed/skipped/cancelled job.

No empty-test success flags are used. Tests and lint cover the implemented foundation;
starter feature files are outside the enabled application/test scope. Expand that scope
when each feature is implemented. Reports and container logs upload even on failure.
Treat CI as unverified until an actual remote run completes.

## Protect main (repository administrator)

Branch protection is GitHub state, not a setting installed by a workflow file.
In repository Settings → Branches, create/update the rule for `main`:

- Require a pull request and at least one independent approval.
- Dismiss stale approvals and require approval of the most recent reviewable push.
- Require status checks and an up-to-date branch; select the exact check `CI required`
  after this workflow has run.
- Require conversation resolution.
- Apply rules to administrators; disallow bypass, force pushes and branch deletion.

Inspect existing rules first; retain any stronger settings. Do not replace an existing
rule with a weaker configuration. Verify the rule with the administrator account.
No repository admin credentials or GitHub CLI are available in this local environment;
protection is pending, not claimed as applied.

## TC-CICD-01 acceptance evidence

After independent review and approval to commit/push, open a PR from `Atiksh`.
Confirm all jobs and their artifacts. In a temporary branch/PR, deliberately change
one test assertion to fail, then verify the test job and `CI required` fail and GitHub
disables merge under the main rule. Restore the assertion and verify a passing run.
Do not merge the deliberate failure. Record real run/PR URLs in the RTM after execution.

Local verification results are recorded in `evidence/ci-local-validation.md`.
Remote CI, merge-blocking experiment, branch protection and human review remain pending.
HISTORY.md and the owner handoff log are appended only after human review per AGENTS.md.

## Dependency refresh

Generate locks with actual tools; do not hand-edit:
```text
cd frontend
npm install --save-exact
cd ../backend
../.venv/Scripts/python.exe -m piptools compile --generate-hashes --output-file requirements.txt requirements.in
../.venv/Scripts/python.exe -m piptools compile --generate-hashes --allow-unsafe --strip-extras --output-file requirements-dev.txt requirements-dev.in
```
On Linux use `../.venv/bin/python`. Review lock diffs and rerun all gates.

ESLint 9.39.5 is pinned because the Next.js lint plugins declare peer support
through version 9. npm warns that ESLint 9 is deprecated. Follow up on a compatible
plugin upgrade before moving to ESLint 10; do not suppress peer conflicts.
Ownership metadata for JSON and generated files is in `ci-foundation-manifest.json`.

References checked during implementation:
[Next.js security update](https://nextjs.org/blog/nextjs-security-update-october-14-2026),
[Django supported versions](https://www.djangoproject.com/download/), and
[GitHub protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

