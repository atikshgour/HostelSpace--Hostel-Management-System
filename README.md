# HostelSpace — Hostel Management System

HostelSpace is a browser-based hostel management system developed by Team 11 for PES University, Bangalore, Department of Computer Science and Engineering, course UE24CS341A Software Engineering. The project follows an Agile workflow and is version 1.0 in the supplied project documents.

The normal stack is a Next.js/JavaScript frontend, Django REST Framework backend, Django sessions with CSRF protection, and PostgreSQL.

## Team and responsibilities

| Member | Main responsibility |
|---|---|
| Anvi Srinivas | Authentication, profile, information/content, and Director workflows |
| Arin Singh | Leave, Warden decisions, location-verified attendance, and deviation records |
| Aryan Singh | Study-room and laundry workflows |
| Atiksh Gour | Complaints, mess, fees/payments, CI and integration foundation |

The whole team shares integration, authorization review, validation, documentation, and demonstration responsibilities.

## Implemented modules

- Session login/logout, CSRF bootstrap, active-role authorization, and student profile updates.
- Notices, contacts, hostel rules, and study-room status.
- Laundry assignment, handover, ready/collection states, staff queues, and retained history.
- Leave submission, Warden decisions, Chief Warden escalation, and transition history.
- One-time location-verified attendance with time, radius, accuracy, stale-sample, and duplicate checks. Raw coordinates are not retained.
- Deviation records, server-side rule snapshots, active totals, deactivation, and duplicate replay protection.
- Student complaints, Director assignment, Maintenance progress, ownership checks, and status history.
- Mess options, capacity checks, student choices, coupons, and staff management.
- Fee dues and payment attempts with local simulation and Razorpay test-mode integration points.
- Director user/settings/report workflows and server-side role/ownership/assignment scoping.
- Health endpoints, Docker Compose, GitHub Actions CI, Jest/RTL, pytest/API, and Playwright tests.

## Architecture

```text
Browser -> Next.js frontend -> Django REST Framework -> PostgreSQL
                                  |-- session + CSRF
                                  |-- payment adapter (simulation/test mode)
                                  `-- one-time browser location validation
```

The frontend never connects directly to the database. Django authorization is authoritative.

## Repository layout

- `frontend/` — Next.js UI, feature modules, Jest/RTL tests, and Playwright specs.
- `backend/` — Django project, REST endpoints, domain apps, migrations, and pytest tests.
- `backend/apps/accounts/` — authentication and roles.
- `backend/apps/director_dashboard/` — Director overview, reports, users, and settings.
- `backend/apps/facilities/` — laundry and study-room operations.
- `backend/apps/information/` — notices, contacts, rules, and publication.
- `backend/apps/leave_attendance/` — leave, attendance, location validation, and deviations.
- `backend/apps/student_services/` — complaints, mess, fees, and payments.
- `tests/` — system-test wrapper; actual Playwright specs are in `frontend/e2e/`.
- `docs/` — architecture, design, validation, testing, and maintenance notes.
- `deliverables/` — project PDFs; `demo_video/` — demonstration video.
- `evidence/` — sanitized validation notes, not a runtime dependency.
- `test_results/` — recorded coverage/report snapshots.
- `STARTER_QA.json`, `STORIES.json` — retained QA and story registers.

## Requirements

Docker Desktop with Compose v2 is recommended. Node.js 22, npm, and Python 3.12 are required for local development. PostgreSQL is required for the normal stack and concurrency checks. SQLite is supported only as an explicit quick mode.

## Docker setup

```powershell
Copy-Item .env.example .env
notepad .env
docker compose up -d --build
```

Set private `POSTGRES_PASSWORD` and `DJANGO_SECRET_KEY` in `.env`. Open `http://localhost:3000/login`; API health is at `http://localhost:8000/api/health/`.

Stop the stack with:

```powershell
docker compose down
```

The API container applies migrations on startup. Local synthetic demo accounts and presentation commands are in the ignored `accounts.md` file.

## Windows quick mode without Docker

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
$env:DJANGO_SETTINGS_MODULE='config.settings.local'
$env:HOSTELSPACE_SQLITE='1'
$env:DJANGO_SECRET_KEY='local-only-development-key'
..\.venv\Scripts\python.exe backend\manage.py migrate
..\.venv\Scripts\python.exe backend\manage.py seed_demo
```

Run these in separate terminals:

```powershell
..\.venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000
```

```powershell
cd frontend
npm ci
npm run dev
```

Then open `http://localhost:3000/login`.

## Tests

```powershell
Push-Location backend
..\.venv\Scripts\python.exe manage.py check
..\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
..\.venv\Scripts\python.exe -m pytest -q
Pop-Location
```

```powershell
Push-Location frontend
npm ci
npm run lint
npm run test:ci
npm run build
Pop-Location
```

Playwright requires running services and a private seeded-account password:

```powershell
cd frontend
$env:HOSTELSPACE_DEMO_PASSWORD='your-local-demo-password'
npm run test:e2e -- --project=chromium
```

The workflow `.github/workflows/ci.yml` runs frontend checks, PostgreSQL backend tests, security scans, Compose smoke checks, Playwright in Chromium/Firefox/Edge, and the aggregate `CI required` gate. The current Firefox job has a known shared login-redirect failure; therefore CI must not be described as fully passing until that is resolved.

## Evidence and safety

`evidence/` is useful for faculty/demo traceability but is not needed to start the application. `test_results/` is also non-runtime report data. Recorded evidence must not be confused with a fresh run on every commit.

Use synthetic records only. Never commit `.env` files, passwords, session cookies, raw location samples, payment credentials, local databases, or generated dependencies. Do not run production migrations, deploy, or use live payments from this repository.
