# Checklist completion and validation record

Validated on 19 November 2026 against source commit `0b7d40c` on `main`.

This record maps the evaluator checklist to versioned repository evidence. It
does not represent a production-release approval, external payment-provider
acceptance, or an assertion about GitHub-side settings that cannot be verified
from a local checkout.

## Part 1 - requirements and design deliverables

| Checklist area | Repository evidence | Status |
| --- | --- | --- |
| SRS, SAD and STP submitted together | `deliverables/SRS_SAD_STP_ SE_Deliverable_2_3_4.pdf` | Present |
| Project proposal | `deliverables/HostelSpace_Synopsis_Project_Proposal_Team11_Deliverable_1.pdf` | Present |
| Architecture, components, security and traceability | `docs/03-architecture/architecture.md`, `docs/04-design/schema.md`, `docs/04-design/role-permissions.md`, `docs/05-validation/rtm.md` | Present |
| API and error-handling design | `docs/04-design/api-contract.md`, `backend/config/exceptions.py` | Present |
| Test plan, mapped cases and security validation | `docs/05-validation/cases.md`, `docs/05-validation/rtm.md`, `tests/security/README.md` | Present |

The submitted PDF is the controlled evidence for IEEE formatting and UML
diagrams. The Markdown documents above provide the maintained implementation
contracts and traceability.

## Part 2 - planning, collaboration and sprint evidence

| Checklist area | Repository evidence | Status |
| --- | --- | --- |
| Backlog, owners and estimates | `STORIES.json` | Present in repository |
| CI automation | `.github/workflows/ci.yml`, `.github/workflows/release.yml` | Present |
| Contribution and integration evidence | `evidence/team-integration-2026-11-16.md`, `docs/07-maintenance/team-integration-manifest.json` | Present |
| Sprints 1-3 demo | `demo_video/HostelSpace_Sprints_1-3_Demo.mp4` | Present |
| Sprints 4-6 demo | `demo_video/HostelSpace_Sprints_4-6_Demo.mp4` (Git LFS) | Present |

GitHub Project board linkage, assignee display, PR authorship and formal remote
reviews are GitHub-account records. They must be shown from the GitHub UI during
evaluation; they cannot be proven solely by files in a local clone.

## Part 3 - testing and quality assurance

### Current local validation

The following checks were executed on 19 November 2026. SQLite was selected
explicitly for the backend run because local Docker/PostgreSQL was unavailable.
The eight skipped backend cases are marked as database-concurrency cases in the
suite; they require the PostgreSQL environment documented in the project README.

| Check | Command | Result |
| --- | --- | --- |
| Backend lint | `ruff check backend` | Passed |
| Django configuration | `python backend/manage.py check` | Passed |
| Migration drift | `python backend/manage.py makemigrations --check --dry-run` | Passed; no changes detected |
| Backend suite | `python -m pytest --tb=short -q` | 170 passed, 8 skipped, 8 subtests passed |
| Frontend lint | `npm run lint` | Passed |
| Frontend unit/component suite | `npm run test:ci -- --runInBand` | 24 suites, 121 tests passed |
| Frontend production build | `npm run build` | Passed |

### Existing generated evidence

The retained reports preserve the fuller PostgreSQL/browser validation recorded
on 17 November 2026:

- `unit_test_report.md`: 178 backend executions passed and 105 Jest/RTL
  executions passed.
- `system_test_report.md`: 13 Chromium browser journeys passed, including
  authentication, role scope, leave, attendance, laundry, complaint, mess,
  payment simulation and publishing flows.
- `branch-coverage-summary.json`: backend branch coverage 90.52%, frontend
  branch coverage 97.34%, overall opportunity-weighted branch coverage 95.39%.
- `raw/commands.md`, `raw/backend-junit.xml`, `raw/frontend-results.json` and
  `raw/browser-results.json`: executable command and machine-readable evidence.

The current local run did not rerun the browser suite or PostgreSQL-only
concurrency checks. It therefore supplements rather than replaces the recorded
PostgreSQL/browser evidence.

## Part 4 - final evaluation handoff

The current implementation, setup instructions and demonstration material are
available in `README.md`, `docs/07-maintenance/ci-setup.md`,
`docs/09-presentation/demo-script.md`, `deliverables/` and `demo_video/`.
The application has been verified through the checks above, but these limits
remain explicit:

- Next.js 16.4.3 reports an upstream security-upgrade advisory during builds.
- A live payment-provider acceptance, load test, hosted cross-browser run,
  recovery rehearsal and independent human review are not claimed complete.
- GitHub Project/PR metadata and viva performance require evaluator review in
  the hosted GitHub project and live demonstration.

## Evaluator quick path

1. Open `deliverables/SRS_SAD_STP_ SE_Deliverable_2_3_4.pdf` for the submitted
   SRS/SAD/STP.
2. Review `docs/05-validation/rtm.md` and `docs/05-validation/cases.md` for
   requirements-to-test traceability.
3. Review `unit_test_report.md`, `system_test_report.md` and the raw artifacts
   listed above for generated verification evidence.
4. Play the two files under `demo_video/` and inspect the GitHub Project/PRs in
   the hosted repository for the checklist items that are not local files.
