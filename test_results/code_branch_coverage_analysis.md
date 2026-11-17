# Code and branch coverage analysis

Generated 2026-11-17T06:56:42.800603+00:00 from recorded artifacts.
Backend execution: 2026-11-17T06:49:25.602301+00:00; frontend: 2026-11-17T06:50:01.985933+00:00.
Source HEAD: `7b7d4c436c88b03f12ac5d07039f031000ca99ae` plus uncommitted test/config/script changes.
Local synthetic PostgreSQL only. No production data changes, live payments, commit or push.
Each command's own timestamp/exit is preserved in [commands](raw/commands.md).
Independent human review remains pending. Coverage success does not override failing tests.

## Branch target: strictly above 90%

| Layer | Covered / total branch opportunities | Coverage | Target |
|---|---|---|---|
| Backend | 309 / 340 | 90.88% | Passed |
| Frontend | 842 / 864 | 97.45% | Passed |
| Overall | 1151 / 1204 | 95.60% | Passed |

Overall is the opportunity-weighted ratio `(Python covered + Istanbul covered) /
(Python total + Istanbul total)`, not an average of percentages. The tools use
different branch models, so the separate layer gates are authoritative. Both
must exceed 90%; one cannot compensate for the other.

Backend line coverage: **95.95%**;
frontend line coverage: **96.47%**.
Backend combined line/branch coverage.py summary: 95.17%.
Backend remaining branches: 31. Frontend remaining branch arms:
22.

## Scope and reproducibility

Python instruments all apps/config with branch measurement; tests and generated
migrations retain their existing exclusions. Frontend instruments all 61
implemented modules, including unimported modules at zero; only tests and instruction
placeholders retain their existing exclusions. No production code or coverage exclusions
were changed to reach this target. The denominator is 340 Python and 864 frontend
branch opportunities in this snapshot. Failed tests also contribute coverage.

`python scripts/run-initial-tests.py coverage` runs both layers even if one fails,
records timestamps/commands/exits, rejects missing/stale coverage, and checks each
layer strictly above 90%. A failing test still makes the command fail. Default Jest
also measures the full implemented scope and enforces >90% global branch coverage.

Retained legacy scope code is tested directly; the orphan frontend LeaveWorkspace
uses mocked legacy adapters and is not claimed as a registered route. Unreachable
old role branches remain visible as gaps rather than bypassing permission checks.
Mocked provider and configuration boundaries do not exercise a live service/deployment.

## Measured Python modules

| File | Lines | Branches |
|---|---|---|
| `apps/accounts/apps.py` | 100.00% | N/A |
| `apps/accounts/management/commands/seed_demo.py` | 100.00% | 100.00% |
| `apps/accounts/models.py` | 100.00% | N/A |
| `apps/accounts/permissions.py` | 100.00% | 100.00% |
| `apps/accounts/serializers.py` | 100.00% | 100.00% |
| `apps/accounts/services.py` | 90.91% | 75.00% |
| `apps/accounts/urls.py` | 100.00% | N/A |
| `apps/accounts/views.py` | 98.48% | 100.00% |
| `apps/director_dashboard/apps.py` | 100.00% | N/A |
| `apps/director_dashboard/overview.py` | 100.00% | 100.00% |
| `apps/director_dashboard/serializers.py` | 100.00% | N/A |
| `apps/director_dashboard/services.py` | 98.25% | 96.67% |
| `apps/director_dashboard/urls.py` | 100.00% | N/A |
| `apps/director_dashboard/views.py` | 91.67% | 80.00% |
| `apps/facilities/apps.py` | 100.00% | N/A |
| `apps/facilities/models.py` | 100.00% | N/A |
| `apps/facilities/serializers.py` | 100.00% | N/A |
| `apps/facilities/services.py` | 98.18% | 83.33% |
| `apps/facilities/urls.py` | 100.00% | N/A |
| `apps/facilities/views.py` | 92.31% | 75.00% |
| `apps/information/apps.py` | 100.00% | N/A |
| `apps/information/models.py` | 100.00% | N/A |
| `apps/information/serializers.py` | 100.00% | 100.00% |
| `apps/information/urls.py` | 100.00% | N/A |
| `apps/information/views.py` | 95.56% | 100.00% |
| `apps/leave_attendance/access.py` | 100.00% | 100.00% |
| `apps/leave_attendance/apps.py` | 100.00% | N/A |
| `apps/leave_attendance/errors.py` | 100.00% | 100.00% |
| `apps/leave_attendance/location.py` | 100.00% | 100.00% |
| `apps/leave_attendance/models.py` | 100.00% | N/A |
| `apps/leave_attendance/permissions.py` | 100.00% | 100.00% |
| `apps/leave_attendance/queries.py` | 0.00% | N/A |
| `apps/leave_attendance/serializers.py` | 97.85% | 87.50% |
| `apps/leave_attendance/services.py` | 94.81% | 86.36% |
| `apps/leave_attendance/urls.py` | 100.00% | N/A |
| `apps/leave_attendance/views.py` | 89.66% | 50.00% |
| `apps/student_services/apps.py` | 100.00% | N/A |
| `apps/student_services/management/commands/seed_service_demo.py` | 92.86% | 90.00% |
| `apps/student_services/models.py` | 98.02% | 100.00% |
| `apps/student_services/payments.py` | 96.51% | 91.18% |
| `apps/student_services/serializers.py` | 97.94% | 100.00% |
| `apps/student_services/services.py` | 100.00% | 100.00% |
| `apps/student_services/urls.py` | 100.00% | N/A |
| `apps/student_services/views.py` | 88.82% | 71.05% |
| `config/asgi.py` | 0.00% | N/A |
| `config/exceptions.py` | 100.00% | 100.00% |
| `config/health.py` | 100.00% | N/A |
| `config/logging.py` | 0.00% | N/A |
| `config/settings/base.py` | 100.00% | 100.00% |
| `config/settings/ci.py` | 100.00% | N/A |
| `config/settings/local.py` | 100.00% | 75.00% |
| `config/settings/production.py` | 100.00% | 100.00% |
| `config/urls.py` | 100.00% | N/A |
| `config/wsgi.py` | 0.00% | N/A |

## Remaining gaps and raw evidence

[Backend exact missing lines/branches](coverage/backend-gaps.json),
[frontend exact unexecuted arms/functions](coverage/frontend-gaps.json),
[Python test contexts](coverage/backend-test-module-map.json),
[Python function-body hits](coverage/backend-function-coverage.json).
Empty contexts are import/setup execution or unavailable context data, not test evidence.
Function-body hit rate is not complete path coverage.

[Python JSON](coverage.json), [XML](coverage.xml), [Python HTML](coverage/backend-html/index.html),
[Istanbul JSON](coverage/frontend/coverage-final.json),
[Jest summary](coverage/frontend/coverage-summary.json), [frontend HTML](coverage/frontend/index.html),
[LCOV](coverage/frontend/lcov.info), [branch totals](branch-coverage-summary.json),
[commands](raw/commands.md). HTML/XML/JSON are regenerated by the actual test tools.
