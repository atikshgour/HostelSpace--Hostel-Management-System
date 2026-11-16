# Unit and component test report

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

## Plan and implementation

Planned: isolated permission/active-account decisions, attendance accuracy/radius/
age decisions and Haversine scale, leave validator boundaries, and provider timeout
normalization. Implemented and executed: 16 new Python unit cases, plus 14
API acceptance cases and the existing 116 backend regressions. Deviation aggregation,
payment state transitions and duplicate/database constraints are integration tests,
not misleadingly described as pure unit arithmetic.

Unit tests Not Implemented: 0 within these selected existing interfaces.
Unit tests Blocked: 0. Raw timeout handling is implemented incompletely and Failed;
it is not marked Blocked. Test-only socket/provider mocks prevent network activity.

| Python unit node | Actual status |
|---|---|
| `test_attendance_boundary_decisions[change0-expected0]` | Passed |
| `test_attendance_boundary_decisions[change1-expected1]` | Passed |
| `test_attendance_boundary_decisions[change2-expected2]` | Passed |
| `test_attendance_boundary_decisions[change3-expected3]` | Passed |
| `test_attendance_boundary_decisions[change4-expected4]` | Passed |
| `test_haversine_distance_identity_and_scale` | Passed |
| `test_leave_input_validation[body0-True]` | Passed |
| `test_leave_input_validation[body1-False]` | Passed |
| `test_leave_input_validation[body2-False]` | Passed |
| `test_leave_input_validation[body3-False]` | Passed |
| `test_active_role_permission[DIRECTOR-True-True-True]` | Passed |
| `test_active_role_permission[STUDENT-True-True-False]` | Passed |
| `test_active_role_permission[DIRECTOR-False-True-False]` | Passed |
| `test_active_role_permission[DIRECTOR-True-False-False]` | Passed |
| `test_wrapped_provider_timeout_is_validation_error` | Passed |
| `test_direct_socket_timeout_is_validation_error` | Failed |

New Python units: 15 Passed,
1 Failed. Full backend run: 143
Passed, 3 Failed, 0 Not Run; total 146.
Existing 116 regression cases passed. API priority cases themselves: 12 Passed,
2 Failed; priority requirement P12 is additionally Failed because its direct
socket-timeout unit fails. No test was weakened, skipped or xfailed.

## Frontend components

Jest/RTL executed 21 cases in 15 suites:
21 Passed, 0 Failed.
The three new tests exercise native required-field validation, a disabled pending
sign-in that becomes successful navigation, and transport failure/retry visibility.
Existing tests cover reversed leave dates, successful leave submission, empty
complaint/fee lists, owned read-only laundry/mess UI and backend error messages.

Executed component nodes:

- student submits validated leave without caller-owned identity fields
- client rejects reversed dates before an API write
- frontend: incomplete login stays invalid and does not send a request
- frontend: pending sign-in disables repeat submission, then navigates on success
- frontend: transport failure is visible and permits a later retry
- geolocation is requested only after the explicit submit click
- login sends session credentials through CSRF transport
- invalid login displays backend error
- sign-in fallback never submits credentials in a URL
- TC-FR08-01: student reads assigned mess and coupons without write controls
- test checkout displays explicit simulation label and takes no payment credentials
- student submits category and description, never room or identity
- information tabs display real API notices and rules
- profile protects identity and saves only the phone field
- student receives read-only history and server-calculated active total
- shared components expose accessible labels, status and table headers
- disabled button prevents duplicate actions
- director report displays zero counts without inventing records
- student sees automatic weekday and cannot change policy or collect batches
- study room is read-only and shows the current server status
- health returns uncached JSON

## Actual failures and feature references

- P12 / FR-09: `test_direct_socket_timeout_is_validation_error` receives a direct
  `TimeoutError` instead of the standardized unavailable-provider validation error.
  `provider_request` handles wrapped `URLError`, not direct socket timeouts.
- P13 / requested pending-payment replay prevention: two identical initiate posts
  create two Pending attempts. Duplicate successful callbacks remain idempotent.
- P14 / requested deviation replay prevention: identical posts create two active
  deviations. Initial aggregation and snapshot behavior pass existing tests.

The last two assertions assume identical repeated payloads represent the same
event/retry. Current APIs lack a retry/event correlation key; whether identical
real-world events may be recorded separately needs owner policy review. We tested
the requested replay invariant without inventing a request field or adding a new
uniqueness policy to production. These are Failed against that invariant, not
claims that every distinct retry or repeated real violation must be rejected.

## Commands and evidence

Exact command arrays, working directories, timestamps and exit codes:
[commands](raw/commands.md), [backend command](raw/backend-command.json),
[frontend command](raw/frontend-command.json).
Observed outputs: [backend log](raw/backend.log), [JUnit](raw/backend-junit.xml),
[failures](raw/observed-failures.json), [Jest results](raw/frontend-results.json),
[frontend log](raw/frontend.log). Coverage is analyzed separately in
[coverage analysis](code_branch_coverage_analysis.md).
