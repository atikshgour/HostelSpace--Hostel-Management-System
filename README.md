# HostelSpace

HostelSpace is a browser-based hostel management system for Team 11, PES University. It uses a Next.js/JavaScript frontend, Django REST Framework backend, Django sessions and CSRF, and PostgreSQL in the normal containerized environment.

## Current state

The application is implemented on `main`. The latest verified local commit includes the integrated feature modules, priority acceptance tests, idempotent payment/deviation replay handling, and frontend/backend coverage evidence.

Normal architecture:

```text
Browser -> Next.js -> Django/DRF -> PostgreSQL
                         |-> payment provider in Razorpay TEST mode
                         |-> browser location sample for one-time attendance
```

Local payment simulation is available only in Django debug/local mode. No live payments or production data are supported.

## Implemented features

- Session login/logout, CSRF protection, active-role authorization, and student profile phone updates.
- Notices, information, contacts, hostel rules, and study-room status.
- Automatic laundry-day assignment, handover, ready state, collection, and retained history.
- Leave submission, assigned Warden decisions, Chief Warden escalation, and transition history.
- One-time location-verified attendance with time, radius, accuracy, stale-sample, and duplicate checks; raw coordinates are not retained.
- Deviation records, server-side rule snapshots, active totals, deactivation, and duplicate replay prevention.
- Student-owned complaints, Director assignment, Maintenance progress, and retained status history.
- Mess options, capacity checks, student choices, coupons, and staff management.
- Fee dues, retained payment attempts, local simulation, Razorpay TEST verification, and duplicate pending-payment prevention.
- Director user/settings/report workflows and server-side role/ownership scoping.
- Health endpoints, Docker Compose configuration, GitHub Actions CI, Jest/RTL tests, pytest/API tests, and Playwright browser tests.

## Quick start with Docker

Create a local `.env` from `.env.example` and set private values for `POSTGRES_PASSWORD` and `DJANGO_SECRET_KEY`.

```powershell
docker compose up -d --build
```

Open [http://localhost:3000/login](http://localhost:3000/login). API health is available at [http://localhost:8000/api/health/](http://localhost:8000/api/health/).

## Windows quick mode without Docker

SQLite is supported only as an explicit local quick mode and does not replace PostgreSQL concurrency checks.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
$env:DJANGO_SETTINGS_MODULE='config.settings.local'
$env:HOSTELSPACE_SQLITE='1'
$env:DJANGO_SECRET_KEY='local-only-development-key'
..\.venv\Scripts\python.exe backend\manage.py migrate
..\.venv\Scripts\python.exe backend\manage.py seed_demo
```

Start the services in separate terminals:

```powershell
..\.venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000
cd frontend
npm ci
npm run dev
```

Local synthetic demo usernames and the private demo password are recorded in the ignored `accounts.md` file. Never use those credentials outside the local demo.

## Tests

Backend quick-mode checks:

```powershell
Push-Location backend
..\.venv\Scripts\python.exe manage.py check
..\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
..\.venv\Scripts\python.exe -m pytest -q
Pop-Location
```

Frontend checks:

```powershell
Push-Location frontend
npm ci
npm run lint
npm run test:ci
npm run build
Pop-Location
```

The latest local quick-mode run passed 138 backend tests with 8 PostgreSQL-only skips. Frontend lint, 21 Jest tests, and the production build passed. Full PostgreSQL, Docker Compose, and Chromium/Firefox/Edge browser checks should be run when Docker Desktop is available.

## CI workflow

`.github/workflows/ci.yml` runs frontend lint/tests/build, backend Ruff/Django/migration/pytest checks against PostgreSQL, Bandit/pip-audit/npm audit, Compose health smoke, Playwright workflows for Chromium/Firefox/Edge, and a required aggregate job that rejects failed, skipped, or cancelled checks.

## Repository layout

- `backend/` - Django project, domain apps, migrations, and backend tests.
- `frontend/` - Next.js application, shared UI, feature modules, and component tests.
- `tests/` - Playwright/system test package.
- `docs/03-architecture/`, `docs/04-design/`, `docs/05-validation/`, `docs/06-testing/`, `docs/07-maintenance/` - current technical and validation documentation.
- `evidence/` and `test_results/` - sanitized test evidence and coverage reports.
- `deliverables/` - project PDFs.
- `demo_video/` - demonstration video.
- `STARTER_QA.json` and `STORIES.json` - retained project QA/story registers.

## Safety boundaries

Use synthetic records only. Do not commit `.env` files, passwords, session cookies, raw location samples, payment credentials, local databases, or generated dependencies. Do not run production migrations, deploy, or use live payments from this repository.
