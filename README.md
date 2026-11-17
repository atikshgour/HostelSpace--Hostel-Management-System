# HostelSpace

<!-- Owner: Anvi Srinivas | US-17 | Development/SRS sprint 1 | Reviewer: Arin Singh (pending) -->

HostelSpace is a browser-based hostel management system built by **Team 11** for **UE24CS341A — Software Engineering**, PES University, Bangalore. It brings student services and staff workflows into one role-based portal using Next.js, Django REST Framework and PostgreSQL.

The application integrates all four team modules: authentication and information, leave and attendance, study-room and laundry services, and complaints, mess and fees. It includes working frontend screens, backend APIs, generated database migrations, synthetic demo data and automated tests. Payment demonstrations use explicit local simulation or a Razorpay TEST integration; no live payment acceptance or production release is claimed.

## Implemented features

| Feature | Current behavior |
|---|---|
| Authentication and profiles | Session-based sign-in/out, role-specific dashboards, active-account checks and student profile viewing with phone-only edits |
| Hostel information | Notices, contacts, information and rules, with authorized publishing and current-content visibility |
| Study room | Open/Closed status, timings and messages; Director/Content Staff updates |
| Laundry | Stable automatic weekday grouping, upcoming drop-off/return dates, staff receipt, Ready and Collected states, and retained historical receipt details |
| Leave | Student applications, assigned-Warden approval/rejection/escalation, supervising Chief decisions and retained transition history |
| Attendance | Explicit one-time location submission, server-side time/accuracy/freshness/radius checks, derived outcomes and duplicate Accepted prevention |
| Deviations | Authorized recording, historical rule-title/weight snapshots, active totals and retained deactivation reasons |
| Complaints | Student submission and owned tracking, Director assignment, assigned Maintenance Staff progression and audit history |
| Mess and coupons | Staff-managed allocations/options/coupons and student-owned, read-only views |
| Fees | Server-owned dues, payment-attempt history, test-mode order/verification, explicit local simulation and single-success database protection |
| Director operations | Authorized account/assignment management, settings and backend-derived reports/overview |

Students access their own personal records. Staff access depends on role and assignment, enforced by Django even for direct API requests. Historical leave/complaint transitions, laundry receipts, deviation weights and payment attempts are retained.

Study-room booking, student selection of laundry days, continuous location tracking, full accounting, inventory, biometrics and native mobile applications are outside the project scope.

## Roles and ownership

| Role | Main permissions |
|---|---|
| Student | Read personal services, submit leave/attendance/complaints and initiate own test fee payments |
| Warden | Assigned-student leave, attendance sessions and deviation workflows |
| Chief Warden | Supervised escalations and scoped attendance/deviation oversight |
| Hostel Director | Accounts, settings, reports, content/study status, complaint assignment and authorized oversight |
| Content Staff | Publish hostel information/rules and update study-room status |
| Laundry Staff | Laundry receipt, readiness, collection and policy management |
| Maintenance Staff | Progress assigned complaints |
| Mess Staff | Manage mess allocations/options and coupons |

The [role matrix](docs/04-design/role-permissions.md) details record-level access. Warden/Chief access does not extend to fee, complaint or laundry counters. Students cannot self-select mess allocations or manually change laundry days.

| Team member | USN | Accountable modules | Shared responsibilities |
|---|---|---|---|
| Anvi Srinivas | PES1UG24CS076 | US-01–04: auth/profile, information and Director | US-17 architecture; US-21 usability/handoff |
| Arin Singh | PES1UG24CS079 | US-05–08: leave, attendance and deviations | US-18 schema/contracts; US-22 validation |
| Aryan Singh | PES1UG24CS086 | US-09–12: study room and laundry | US-19 Docker/demo setup; US-23 integration |
| Atiksh Gour | PES1UG24CS096 | US-13–16: complaints, mess and fees | US-20 CI; US-24 recovery/maintenance |

## Stack and architecture

- **Frontend:** JavaScript/JSX, Next.js App Router, React, CSS and Tailwind.
- **Backend:** Python, Django and Django REST Framework; Django ORM for database access.
- **Database:** PostgreSQL 16 in Compose/CI. SQLite is available only as explicit local quick mode.
- **Authentication:** Django sessions and CSRF-protected writes, including login; no JWT/localStorage authentication.
- **Testing:** pytest/pytest-django/pytest-cov, Jest/React Testing Library and Playwright.
- **Delivery:** Docker Compose, GitHub Actions, Git/GitHub and pinned dependency lockfiles.

```text
Browser / React UI
        |
        v
Next.js App Router + same-origin /api routing
        |
        v
Django / DRF: sessions, CSRF, permissions, validation, services
        |
        v
Django ORM -> PostgreSQL

Browser geolocation -> one-time attendance check in Django
Django payment adapter -> Razorpay TEST API
GitHub Actions -> lint / build / tests / security / container checks
```

The frontend does not access SQL directly. Authenticated requests and responses use no-store/private behavior, and API errors follow `{code, message, fields}`. Raw student location samples are not retained as attendance records.

## Run locally with Docker Compose

Prerequisites: Git, Docker and Docker Compose v2. Run these commands from the repository root. Use a fresh local database/Compose volume for this integrated version: its migration baseline is **not an upgrade path for databases from the earlier implementation**. Preserve existing data and plan any upgrade separately.

1. Copy `.env.example` to `.env` if you do not already have local configuration:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Set private, nonempty `POSTGRES_PASSWORD` and `DJANGO_SECRET_KEY` values in `.env`. Use a URL-safe database password for the Compose connection URL. Keep the default loopback bindings for local use; do not commit `.env`.
3. Build and start the services:

   ```powershell
   docker compose up --build -d
   docker compose ps
   ```

4. Create synthetic demo records:

   ```powershell
   docker compose exec api python manage.py seed_demo
   ```

   The command privately prompts for a password of at least 12 characters. It creates new demo users and does not reset existing passwords. Seeding requires local settings with `DEBUG=True`.
5. Open [http://localhost:3000](http://localhost:3000) and sign in. Health endpoints are [frontend /health](http://localhost:3000/health) and [Django /api/health/](http://localhost:8000/api/health/).

Demo usernames: `student`, `student2`, `warden`, `chief`, `director`, `content`, `laundry`, `maintenance` and `mess`. Use the password supplied during seeding; there is no published default password.

```powershell
docker compose logs api frontend
docker compose stop
```

Compose applies migrations to its local database before starting the API. Payments are disabled by default in the supplied Compose configuration. See the payment configuration notes below before demonstrating checkout.

## Run without containers

Use Python 3.12, Node.js 22 and a fresh local PostgreSQL database. The recorded local tests also ran on Python 3.13.7 and PostgreSQL 15.19. Install dependencies from the checked-in lockfiles.

From the repository root, in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r backend/requirements-dev.txt
$env:DJANGO_SETTINGS_MODULE = 'config.settings.local'
$env:HOSTELSPACE_SQLITE = '0'
```

Set `DATABASE_URL` privately to the connection URL for your local database before continuing. For example, its format is `postgresql://USER:PASSWORD@127.0.0.1:5432/DATABASE`; URL-encode credentials when necessary. Direct Python commands read exported environment variables, not the root Compose `.env` file.

```powershell
.\.venv\Scripts\python.exe backend/manage.py migrate
.\.venv\Scripts\python.exe backend/manage.py seed_demo
.\.venv\Scripts\python.exe backend/manage.py runserver 127.0.0.1:8000
```

In a second terminal, from `frontend`:

```powershell
npm ci
npm run dev
```

The frontend defaults to `http://127.0.0.1:8000` for its Django origin. Set server-only `DJANGO_API_ORIGIN` before starting/building the frontend if the API runs elsewhere. Use `npm run build` followed by `npm run start` for a local production-build frontend.

### Environment and payment modes

| Variable | Purpose |
|---|---|
| `DATABASE_URL`, `HOSTELSPACE_SQLITE=0` | PostgreSQL connection and explicit database selection |
| `DJANGO_SETTINGS_MODULE` | `config.settings.local` for local use; `config.settings.ci` for automated checks |
| `DJANGO_SECRET_KEY` | Private Django key; local settings generate a local development key when absent |
| `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` | Allowed backend hosts and trusted frontend origins |
| `DJANGO_API_ORIGIN` | Server-only frontend proxy destination |
| `HOSTELSPACE_DEMO_PASSWORD` | Optional private alternative to the seed command's password prompt; also used by browser fixtures |
| `PAYMENT_MODE` | `disabled` by default, `simulation` for local demos or `razorpay` for TEST-provider integration |
| `ALLOW_PAYMENT_SIMULATION=1` | Explicit simulation gate; simulation also requires `DEBUG=True` |
| `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET` | Private TEST credentials; the adapter rejects non-test key IDs |

For a native local simulated checkout, export `PAYMENT_MODE=simulation` and `ALLOW_PAYMENT_SIMULATION=1` in the backend terminal before starting Django. This takes no payment credentials and is labelled as simulation. Real TEST-provider acceptance requires separate credentials and verification; passing simulation/mocked tests does not demonstrate a gateway payment.

Compose forwards `PAYMENT_MODE`, `ALLOW_PAYMENT_SIMULATION` and the optional private `HOSTELSPACE_DEMO_PASSWORD` from the local environment; TEST provider credentials still require explicit configuration. See the [fee contract](backend/apps/student_services/FEES_API.md) and [setup guide](docs/07-maintenance/ci-setup.md).

## Tests and verification

Backend checks require a disposable PostgreSQL database whose user can create pytest's test database. Export the connection and `HOSTELSPACE_SQLITE=0`, then use `DJANGO_SETTINGS_MODULE=config.settings.ci` in the test terminal.

From the repository root:

```powershell
.\.venv\Scripts\ruff.exe check backend
.\.venv\Scripts\python.exe backend/manage.py check
.\.venv\Scripts\python.exe backend/manage.py makemigrations --check --dry-run
```

From `backend`:

```powershell
..\.venv\Scripts\python.exe -m pytest --tb=short -q
```

From `frontend`:

```powershell
npm run lint
npm run test:ci -- --runInBand
npm run build
```

Playwright requires running Django and the built frontend, a separate synthetic local database, explicit payment simulation, and a privately exported `HOSTELSPACE_DEMO_PASSWORD` matching the seeded users. Follow the [browser setup](docs/07-maintenance/ci-setup.md), then run from `frontend`:

```powershell
npx playwright install chromium firefox msedge
npm run test:e2e
```

### Recorded results and open issues

The 16 November 2026 execution snapshot, published in `c7d71bc`, recorded:

| Layer | Executed | Passed | Failed |
|---|---:|---:|---:|
| Backend pytest | 146 | 143 | 3 |
| Jest/RTL components | 21 | 21 | 0 |
| Playwright Chromium | 13 | 13 | 0 |
| **Total** | **180** | **177** | **3** |

The existing 116 backend regressions passed. Additional priority tests expose three open failures:

- A direct payment-provider `TimeoutError` escapes standardized error handling.
- Identical repeated Pending payment initiation creates two attempts; duplicate successful callbacks remain idempotent.
- Identical repeated deviation submissions create two active records and double the total.

In that historical snapshot, the latter two fail the requested replay-prevention invariant. Defining retry/event identity requires owner policy review so legitimate separate attempts/events are not incorrectly blocked. These are historical failures from the 16 November snapshot. Newer main commits fix timeout handling and replay protection; consult the current regenerated test reports for the integrated result. Failures are not skipped or marked expected-failure.

Measured coverage: backend **80.96% lines / 51.76% branches**; frontend **48.13% lines / 38.31% branches**. Coverage is not a pass rate. The recorded browser snapshot covers Chromium; Firefox/Edge were not rerun for that test package.

See the [unit/component report](test_results/unit_test_report.md), [system report](test_results/system_test_report.md), [coverage analysis](test_results/code_branch_coverage_analysis.md), [raw failures](test_results/raw/observed-failures.json) and [actual commands](test_results/raw/commands.md).

## CI and release status

GitHub Actions configures frontend lint/Jest/build, backend checks and PostgreSQL tests, security/dependency checks, Compose health checks and Chromium/Edge/Firefox workflows. `CI required` aggregates prerequisite results. Branch protection and independent review must be configured separately; workflow YAML does not enforce them by itself.

The manual release workflow builds downloadable images. Automated deployment/promotion is not implemented. Independent human sign-off, complete manual usability, agreed load acceptance, external provider acceptance and recovery rehearsal remain pending; no production readiness is inferred from passing browser journeys.

## Repository and documentation

```text
frontend/src/app/       Next.js pages, layouts and routes
frontend/src/features/ Domain UI components and API clients
frontend/src/lib/      Shared API, role and formatting helpers
backend/config/        Django settings, URLs, errors and health checks
backend/apps/          Accounts, information, leave/attendance, facilities,
                       student services and Director modules
frontend/e2e/          Canonical Playwright journeys and privacy/health checks
tests/                 Browser-suite forwarding and validation material
test_results/          Recorded reports, raw outputs and coverage
evidence/              Dated implementation/integration evidence
scripts/               Validation and recovery helpers
.github/workflows/     CI and image-build workflows
compose.yaml           Local frontend/API/PostgreSQL stack
docs/                  Source PDFs, contracts, validation and maintenance
deliverables/          Submitted project PDFs
demo_video/            Recorded project demonstration
```

Start with the [setup and integration guide](docs/07-maintenance/ci-setup.md), [API contract](docs/04-design/api-contract.md), [role permissions](docs/04-design/role-permissions.md), [traceability matrix](docs/05-validation/rtm.md) and [integration evidence](evidence/team-integration-2026-11-16.md). The [integration manifest](docs/07-maintenance/team-integration-manifest.json) preserves source/merge provenance.

The SRS/SAD/STP and Development Plan PDFs in [docs/sources](docs/sources) preserve the original requirements and proposed sprint mappings. Integration follows the PDF permission policy where older source-folder variants disagree. All existing FR IDs are preserved; the duplicate legacy UC-02 correction remains a proposal. Some supporting documents still contain starter instructions or older notes; use their dated integration updates and actual registered code for current behavior.

Earlier implementation details and retired starter/archive documents remain available in Git history and dated evidence. Inspect the relevant contracts/history and preserve operational audit records before contributing. Shared UI changes must reuse the existing CSS tokens/components.

The team shares integration, authorization review, validation, documentation and demonstration responsibilities. Submitted PDFs are in [deliverables](deliverables), and the recorded demonstration is in [demo_video](demo_video). Hosted Firefox previously had a shared login-redirect failure; local Chromium success does not establish that the hosted browser matrix is fully passing.
