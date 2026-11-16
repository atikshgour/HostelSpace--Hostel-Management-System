# System, integration and browser test report

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

## Fourteen requested priority cases

Planned and implemented: all 14 cases using existing routes, model fields and
services. Overall priority requirements: 11 Passed, 3 Failed (P12-P14).
No priority case is Blocked or Not Implemented. This includes the additional
socket-timeout check in P12, beyond its passing wrapped-timeout API workflow.

| ID | Priority requirement | Status | Observed result |
|---|---|---|---|
| P01 | Valid credential login | Passed | Assertions passed; details in backend JUnit and source test. |
| P02 | Invalid credential login | Passed | Assertions passed; details in backend JUnit and source test. |
| P03 | Student denied Warden/admin endpoints | Passed | Assertions passed; details in backend JUnit and source test. |
| P04 | Valid leave submission | Passed | Assertions passed; details in backend JUnit and source test. |
| P05 | Invalid/incomplete leave rejected | Passed | Assertions passed; details in backend JUnit and source test. |
| P06 | Warden approves and rejects leave | Passed | Assertions passed; details in backend JUnit and source test. |
| P07 | Valid time/location attendance | Passed | Assertions passed; details in backend JUnit and source test. |
| P08 | Outside-boundary attendance rejected | Passed | Assertions passed; details in backend JUnit and source test. |
| P09 | Repeated attendance prevented | Passed | Assertions passed; details in backend JUnit and source test. |
| P10 | Complaint creation and owned visibility | Passed | Assertions passed; details in backend JUnit and source test. |
| P11 | Unauthorized complaint update denied | Passed | Assertions passed; details in backend JUnit and source test. |
| P12 | Payment success/failure/timeout/retry | Failed | Workflow passes wrapped URLError timeout, failure and successful retry. Direct socket TimeoutError escapes normalization (supporting unit test Failed). |
| P13 | Duplicate payment callbacks/submissions | Failed | Identical Pending initiation creates 2 attempts. Repeated success callbacks still produce exactly 1 Success; initiation after Paid returns 400. Replay invariant Failed. |
| P14 | Deviation totals and duplicate prevention | Failed | Initial total equals rule weight. Identical repeated submission creates 2 active rows and doubles the total. Replay invariant Failed. |

## Preconditions, steps and expected/actual results

### P01 - FR-01 / TC-FR01-01

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Input/workflow: CSRF bootstrap; valid synthetic login; GET identity.

Expected: 200 and owned session.

Actual: Assertions passed; details in backend JUnit and source test.

API node `test_P01_valid_login`: Passed; combined priority status: **Passed**.

### P02 - FR-01 / TC-FR01-02

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Input/workflow: CSRF bootstrap; wrong password; GET identity.

Expected: 400 invalid_credentials; no session.

Actual: Assertions passed; details in backend JUnit and source test.

API node `test_P02_invalid_login`: Passed; combined priority status: **Passed**.

### P03 - SEC-01/03

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Input/workflow: Student requests Director APIs and staff-only writes.

Expected: 403 and no privileged operation.

Actual: Assertions passed; details in backend JUnit and source test.

API node `test_P03_student_denied_staff_and_admin_actions`: Passed; combined priority status: **Passed**.

### P04 - FR-05 / TC-FR05-01

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Input/workflow: Assigned student submits valid dates/reason.

Expected: 201 Pending; assigned Warden and actor history.

Actual: Assertions passed; details in backend JUnit and source test.

API node `test_P04_valid_leave`: Passed; combined priority status: **Passed**.

### P05 - FR-05 / SEC-04

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Input/workflow: Submit empty, blank-reason and reversed-date payloads.

Expected: 400; zero leave rows.

Actual: Assertions passed; details in backend JUnit and source test.

API node `test_P05_invalid_leave`: Passed; combined priority status: **Passed**.

### P06 - FR-05 / TC-FR05-01

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Input/workflow: Create two leaves; assigned Warden finalizes each.

Expected: Approved/Rejected; two transitions each.

Actual: Assertions passed; details in backend JUnit and source test.

API node `test_P06_warden_approves_and_rejects`: Passed; combined priority status: **Passed**.

### P07 - FR-06 / TC-FR06-01

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Input/workflow: Assigned student submits within current session and radius.

Expected: 201 Accepted; no raw coordinates in output.

Actual: Assertions passed; details in backend JUnit and source test.

API node `test_P07_valid_attendance`: Passed; combined priority status: **Passed**.

### P08 - FR-06 / TC-FR06-01

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Input/workflow: Submit synthetic point beyond configured radius.

Expected: 201 derived Rejected / OUTSIDE_RADIUS.

Actual: Assertions passed; details in backend JUnit and source test.

API node `test_P08_outside_boundary_rejected`: Passed; combined priority status: **Passed**.

### P09 - BR-05 / NFR-03

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Input/workflow: Submit the same accepted student/session twice.

Expected: Second request 409; exactly one row.

Actual: Assertions passed; details in backend JUnit and source test.

API node `test_P09_repeated_attendance_prevented`: Passed; combined priority status: **Passed**.

### P10 - FR-07 / TC-FR07-01

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Input/workflow: Two students create complaints; first lists/reads second.

Expected: Only own list; cross-read 404.

Actual: Assertions passed; details in backend JUnit and source test.

API node `test_P10_complaint_creation_and_ownership`: Passed; combined priority status: **Passed**.

### P11 - FR-07 / SEC-01

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Input/workflow: Other student tries to resolve complaint.

Expected: 403; original Open state unchanged.

Actual: Assertions passed; details in backend JUnit and source test.

API node `test_P11_unauthorized_complaint_update`: Passed; combined priority status: **Passed**.

### P12 - FR-09 / TC-FR09-01

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Input/workflow: Fail simulation; mock provider timeout; retry and succeed.

Expected: Unpaid until success; retained failure; normalized timeout error.

Actual: Workflow passes wrapped URLError timeout, failure and successful retry. Direct socket TimeoutError escapes normalization (supporting unit test Failed).

API node `test_P12_payment_success_failure_timeout_retry`: Passed; combined priority status: **Failed**.

### P13 - BR-06 / NFR-03 + requested replay invariant

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Input/workflow: Initiate twice while Pending; repeat success callback; initiate after Paid.

Expected: One pending attempt for identical replay; one successful result.

Actual: Identical Pending initiation creates 2 attempts. Repeated success callbacks still produce exactly 1 Success; initiation after Paid returns 400. Replay invariant Failed.

API node `test_P13_duplicate_payment_callbacks_and_submissions`: Failed; combined priority status: **Failed**.

### P14 - FR-10 / TC-FR10-01 + requested replay invariant

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Input/workflow: Record rule deviation; read total; repeat identical submission.

Expected: Correct weight total; no duplicate for the same replay.

Actual: Initial total equals rule weight. Identical repeated submission creates 2 active rows and doubles the total. Replay invariant Failed.

API node `test_P14_deviation_total_and_duplicate_prevention`: Failed; combined priority status: **Failed**.

## Complete browser workflows

Playwright Chromium: 13 Passed,
0 Failed, 0 Not Run,
0 flaky. Real built Next.js and Django services with
PostgreSQL and nine synthetic demo roles were used. Payment mode was explicitly
local simulation; no real payment provider was used. Login tests held synthetic
session cookies in worker memory, not report artifacts; traces were disabled.
The privacy-specific cases use empty-response mocks and are labeled as such in
their source, not claimed as backend verification.

Journeys: login/profile/mobile navigation; current notices/rules/study status;
Director-created assigned accounts and Warden denial; laundry policy/receipt/
ready/collection; student-to-Warden-to-Chief leave; geolocation attendance and
deviation snapshots; Director-assigned/Maintenance-resolved complaint;
Mess-Staff allocations/coupons and cross-student denial; simulated fee payment;
Content-Staff publishing; two privacy assertions; low-volume health smoke.

These passing browser workflows do not test the failing raw socket timeout or
pending duplicate submissions and do not override those failures. Current task
Firefox and Edge runs: Not Run (scope was the installed Chromium system run);
previous hosted results are not substituted for execution of this test change.

## Security and reliability

Passed: valid session/CSRF auth, invalid login rejection, student/admin boundaries,
complaint ownership and unauthorized updates, staff-assignment scoping, no raw
location samples in attendance output/model, duplicate accepted attendance,
single successful payment callbacks and retained failed attempts. Existing
PostgreSQL concurrency tests ran, including attendance/leave/payment races.
Failed: direct timeout normalization, pending-payment replay deduplication and
deviation replay deduplication. See [failure evidence](raw/observed-failures.json).
No live/sandbox provider acceptance is claimed from mocks or local simulation.

## Defects, blockers and assumptions

Three observed failures remain open; production code was intentionally unchanged.
P13/P14 require confirming replay identity versus legitimate separate attempts/
events before selecting a production fix. Automated test additions would make a
future CI run fail until those assertions or approved product policy are resolved;
they were not pushed during test execution. No environment blocker prevented this run.
Full manual usability, approved 20-user/100-warm-visit load, staging, live provider,
production inspection and recovery rehearsal are Not Run (outside this local
automated suite). The health smoke is not a load/performance acceptance test.

## Commands and observed outputs

[Exact commands](raw/commands.md); [environment](raw/environment.json);
[inventory](raw/project-inventory.json); [JUnit](raw/backend-junit.xml);
[Playwright JSON](raw/browser-results.json); [browser log](raw/e2e.log);
[interactive browser report](raw/browser-html/index.html);
[build output](raw/build.log); [backend service log](raw/backend-service.log);
[frontend service log](raw/frontend-service.log).

All runs were executed; reports use observed artifacts. During execution no deployment, migration
of production data, commit or push was performed.
