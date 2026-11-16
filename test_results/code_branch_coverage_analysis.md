# Code and branch coverage analysis

Execution snapshot, source commit: `9a364dd1873b7ff50683c6a7bd9101ffce0bf1a4` plus local test-only additions at execution time.
Environment: Python 3.13.7, Django 5.2.18, Node v22.20.0, PostgreSQL 15.19.
Scope: local synthetic fixtures only; new isolated database `hostelspace_initialtests_20261116`
and pytest's disposable test database. At execution time: no existing database reset, live payment,
production behavior edit, production migration, commit, push or deployment.
Independent human review remains pending; shared handoff history is not fabricated.

Status vocabulary: Passed, Failed, Not Implemented, Blocked, Not Run.
Sources inspected: README, AGENTS (root/frontend), HISTORY, CHANGELOG, decisions,
current SRS/SAD/STP PDF (functional p30/security p31), API/role contracts, actual
models/services/views/tests and workflow YAML. Some documentation still contains
instruction placeholders or old harness notes; actual registered routes and code
were inventoried in [project-inventory.json](raw/project-inventory.json).

## Measured totals

| Metric | Observed numerator / denominator | Coverage |
|---|---|---|
| Backend executable lines/statements | 1518 / 1875 | 80.96% |
| Backend decision branches | 176 / 340 | 51.76% |
| Backend combined lines + branches (coverage.py summary) | covered line and branch opportunities | 76.48% |
| Backend function bodies with at least one executed body statement | 119 / 153 | 77.78% |
| Frontend executable lines | 477 / 991 | 48.13% |
| Frontend statements | 506 / 1114 | 45.42% |
| Frontend branches | 331 / 864 | 38.31% |
| Frontend functions | 112 / 305 | 36.72% |

**Python branch coverage was measured successfully.** pytest-cov used
`--cov-branch`, configuration has `branch=true`, and coverage JSON reports
`meta.branch_coverage=true`. 164 branches remain missing,
including 64 partially covered decisions. Missing
branches include completely unexecuted decisions as well as one unvisited arm;
these counts are not interchangeable. Negative branch targets denote exits.

Backend functions are a derived body-hit rate from coverage.py 7.17 function
regions, excluding the empty module region and zero-statement bodies. This is not
a native coverage.py function percentage and does not prove all function paths.
Exact regions and hits are in [function evidence](coverage/backend-function-coverage.json).

## Scope and interpretation

Backend instruments all `apps` and `config`; tests and generated migrations are
excluded by existing configuration. Import-only model declaration coverage is not
proof of every database behavior. PostgreSQL constraint and concurrency assertions
provide separate runtime evidence. Failed tests contribute executed lines to
coverage; coverage is not a test pass percentage or product acceptance.

Frontend instruments 61 implemented source modules, including
unimported route/components at zero. Tests and instruction-only starter files are
excluded; actual implementation is not excluded to inflate percentages. This is
broader than the earlier imported-module-only report. Browser execution is not
instrumented and is not merged into Jest coverage. Async page behavior is tested
by Playwright rather than claimed from component coverage.

## Files and lines not covered

| Backend source | Line/statement coverage | Branch coverage | Missing executable lines |
|---|---|---|---|
| `apps/accounts/apps.py` | 100.00% | N/A (no decisions) | None |
| `apps/accounts/management/commands/seed_demo.py` | 0.00% | 0.00% | 3, 4, 5, 6, 8, 9, 10, 11, 13, 14, 15, 16, 19, 20, 22, 23, 24, 25, 26, 29, 30, 32, 33, 36, 37, 38, 39, 41, 42, 43, 46, 47, 48, 49, 50, 51, 52, 53, 62, 70, 78, 86, 93, 102, 105, 109, 121, 132, 133, 142, 150 |
| `apps/accounts/models.py` | 100.00% | N/A (no decisions) | None |
| `apps/accounts/permissions.py` | 100.00% | 100.00% | None |
| `apps/accounts/serializers.py` | 91.89% | 62.50% | 14, 26, 29 |
| `apps/accounts/services.py` | 90.91% | 75.00% | 41 |
| `apps/accounts/urls.py` | 100.00% | N/A (no decisions) | None |
| `apps/accounts/views.py` | 81.82% | 25.00% | 73, 86, 88, 89, 90, 91, 94, 95, 96, 97, 98, 99 |
| `apps/director_dashboard/apps.py` | 100.00% | N/A (no decisions) | None |
| `apps/director_dashboard/overview.py` | 93.33% | 90.91% | 20, 54, 55 |
| `apps/director_dashboard/serializers.py` | 100.00% | N/A (no decisions) | None |
| `apps/director_dashboard/services.py` | 84.21% | 60.00% | 19, 24, 25, 28, 29, 35, 36, 48, 54 |
| `apps/director_dashboard/urls.py` | 100.00% | N/A (no decisions) | None |
| `apps/director_dashboard/views.py` | 85.00% | 40.00% | 20, 21, 22, 26, 54, 60, 122, 124, 135 |
| `apps/facilities/apps.py` | 100.00% | N/A (no decisions) | None |
| `apps/facilities/models.py` | 100.00% | N/A (no decisions) | None |
| `apps/facilities/serializers.py` | 100.00% | N/A (no decisions) | None |
| `apps/facilities/services.py` | 98.18% | 83.33% | 73 |
| `apps/facilities/urls.py` | 100.00% | N/A (no decisions) | None |
| `apps/facilities/views.py` | 89.23% | 50.00% | 15, 16, 50, 69, 93, 95, 96 |
| `apps/information/apps.py` | 100.00% | N/A (no decisions) | None |
| `apps/information/models.py` | 100.00% | N/A (no decisions) | None |
| `apps/information/serializers.py` | 100.00% | 100.00% | None |
| `apps/information/urls.py` | 100.00% | N/A (no decisions) | None |
| `apps/information/views.py` | 91.11% | 50.00% | 50, 55, 60, 61 |
| `apps/leave_attendance/access.py` | 0.00% | 0.00% | 5, 6, 7, 9, 10, 11, 13, 14, 16, 17, 18, 20, 21, 22, 23, 24, 25, 26, 28, 29, 30, 31, 32, 33, 35, 36, 37, 38, 39, 40, 41, 42, 43, 45, 46, 47, 48, 49, 50, 52, 53, 54, 55, 56, 57, 58, 59, 60, 63, 65, 66, 67, 68, 69 |
| `apps/leave_attendance/apps.py` | 100.00% | N/A (no decisions) | None |
| `apps/leave_attendance/errors.py` | 0.00% | 0.00% | 1, 4, 5, 6, 7, 8, 9, 10, 12, 13 |
| `apps/leave_attendance/location.py` | 94.12% | 87.50% | 13 |
| `apps/leave_attendance/models.py` | 100.00% | N/A (no decisions) | None |
| `apps/leave_attendance/permissions.py` | 78.69% | 50.00% | 19, 30, 31, 32, 38, 50, 54, 57, 63, 64, 65, 66, 67 |
| `apps/leave_attendance/queries.py` | 0.00% | N/A (no decisions) | 2, 5, 6, 8, 9 |
| `apps/leave_attendance/serializers.py` | 92.47% | 75.00% | 22, 32, 75, 76, 77, 108, 109 |
| `apps/leave_attendance/services.py` | 87.01% | 68.18% | 29, 43, 48, 55, 56, 69, 70, 71, 72, 82 |
| `apps/leave_attendance/urls.py` | 100.00% | N/A (no decisions) | None |
| `apps/leave_attendance/views.py` | 85.34% | 33.33% | 104, 105, 113, 134, 135, 144, 145, 146, 147, 148, 149, 164, 168, 170, 214, 215, 218 |
| `apps/student_services/apps.py` | 100.00% | N/A (no decisions) | None |
| `apps/student_services/management/commands/seed_service_demo.py` | 0.00% | 0.00% | 2, 3, 5, 6, 7, 8, 10, 11, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33 |
| `apps/student_services/models.py` | 98.02% | 100.00% | 17, 20 |
| `apps/student_services/payments.py` | 89.53% | 76.47% | 25, 36, 77, 80, 101, 104, 113, 129, 131 |
| `apps/student_services/serializers.py` | 96.91% | 50.00% | 112, 119, 210 |
| `apps/student_services/services.py` | 94.23% | 81.25% | 17, 36, 61 |
| `apps/student_services/urls.py` | 100.00% | N/A (no decisions) | None |
| `apps/student_services/views.py` | 71.18% | 36.84% | 85, 115, 120, 137, 143, 144, 145, 150, 151, 152, 153, 154, 155, 156, 157, 162, 163, 164, 165, 166, 167, 168, 171, 172, 173, 174, 175, 185, 223, 225, 232, 237, 239, 240, 245, 246, 247, 272, 276, 279, 280, 286, 300, 301, 302, 303, 304, 305, 306 |
| `config/asgi.py` | 0.00% | N/A (no decisions) | 1, 3, 5, 6 |
| `config/exceptions.py` | 75.00% | 50.00% | 11, 19, 20, 23 |
| `config/health.py` | 100.00% | N/A (no decisions) | None |
| `config/logging.py` | 0.00% | N/A (no decisions) | 4 |
| `config/settings/base.py` | 93.18% | 50.00% | 44, 57, 68 |
| `config/settings/ci.py` | 100.00% | N/A (no decisions) | None |
| `config/settings/local.py` | 0.00% | 0.00% | 4, 5, 6, 8, 10, 11, 12, 13, 14, 15, 16, 19, 21 |
| `config/settings/production.py` | 0.00% | 0.00% | 1, 3, 4, 6, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22, 23, 26, 31 |
| `config/urls.py` | 100.00% | N/A (no decisions) | None |
| `config/wsgi.py` | 0.00% | N/A (no decisions) | 2, 4, 6, 7 |

Complete missing backend line numbers/branch pairs: [backend gaps](coverage/backend-gaps.json).
Frontend unexecuted statement/function locations and branch arms:
[frontend gaps](coverage/frontend-gaps.json). All per-file frontend line/statement/
function/branch totals are in [Jest summary](coverage/frontend/coverage-summary.json);
LCOV contains exact unhit executable line locations.

## Untested decisions and module mapping

- `leave_attendance/access.py` is an unexecuted legacy helper; active views import
  `permissions.py`. Legacy queries/errors and deployment settings are also largely
  unexecuted. Retained code is measured, not deleted or excluded for coverage.
- Director reassignment/deactivation/role conversion edge branches, some inactive
  account paths, fallback study status and information update/delete paths remain.
- Payment malformed provider-order variants, missing credentials, mismatched
  amount/currency/reference and final-state alternatives are only partially hit.
  The direct-timeout test exposes an unhandled path, not a passing recovery path.
- Frontend Director/UserManagement, study editor, some route shells, AppShell
  navigation/logout branches and service form errors have sparse Jest coverage.
- New pure units map to auth permissions, LeaveInput, attendance location logic
  and provider request errors. Priority API cases map to accounts, leave/attendance,
  complaints, payment attempts and deviation aggregation. Existing domain tests
  cover facilities/information/Director/mess, histories and PostgreSQL races.
- Per-file test-context mapping generated from actual coverage data:
  [backend test-module map](coverage/backend-test-module-map.json). Empty context
  entries are import/setup execution, not attributed to a test. Coverage contexts
  show code execution, not every database assertion or proof of a requirement.

## Commands and artifact references

[Exact executed commands](raw/commands.md), [backend command](raw/backend-command.json),
[frontend command](raw/frontend-command.json).

- [Backend HTML](coverage/backend-html/index.html)
- [Cobertura XML](coverage.xml)
- [coverage.py JSON with test contexts](coverage.json)
- [Frontend HTML](coverage/frontend/index.html)
- [Istanbul JSON](coverage/frontend/coverage-final.json)
- [Jest totals](coverage/frontend/coverage-summary.json)
- [LCOV](coverage/frontend/lcov.info)
- [Browser HTML](raw/browser-html/index.html) (functional evidence; not instrumented coverage)

The full branch-coverage and manual/provider/release acceptance gaps remain open.
No proposed coverage target is silently approved or reported as achieved.
