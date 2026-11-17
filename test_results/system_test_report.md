# System, integration and browser test report

Generated 2026-11-17T06:56:42.800603+00:00 from recorded artifacts.
Backend execution: 2026-11-17T06:49:25.602301+00:00; frontend: 2026-11-17T06:50:01.985933+00:00.
Source HEAD: `7b7d4c436c88b03f12ac5d07039f031000ca99ae` plus uncommitted test/config/script changes.
Local synthetic PostgreSQL only. No production data changes, live payments, commit or push.
Each command's own timestamp/exit is preserved in [commands](raw/commands.md).
Independent human review remains pending. Coverage success does not override failing tests.

## Priority requirements

| ID | Requirement | API test | Combined requirement | Actual result |
|---|---|---|---|---|
| P01 | Valid credential login | Passed | Passed | Assertions passed; see JUnit and source test. |
| P02 | Invalid credential login | Passed | Passed | Assertions passed; see JUnit and source test. |
| P03 | Student denied Warden/admin endpoints | Passed | Passed | Assertions passed; see JUnit and source test. |
| P04 | Valid leave submission | Passed | Passed | Assertions passed; see JUnit and source test. |
| P05 | Invalid/incomplete leave rejected | Passed | Passed | Assertions passed; see JUnit and source test. |
| P06 | Warden approves and rejects leave | Passed | Passed | Assertions passed; see JUnit and source test. |
| P07 | Valid time/location attendance | Passed | Passed | Assertions passed; see JUnit and source test. |
| P08 | Outside-boundary attendance rejected | Passed | Passed | Assertions passed; see JUnit and source test. |
| P09 | Repeated attendance prevented | Passed | Passed | Assertions passed; see JUnit and source test. |
| P10 | Complaint creation and owned visibility | Passed | Passed | Assertions passed; see JUnit and source test. |
| P11 | Unauthorized complaint update denied | Passed | Passed | Assertions passed; see JUnit and source test. |
| P12 | Payment success/failure/timeout/retry | Passed | Failed | Wrapped-timeout API workflow passes; direct socket TimeoutError escapes normalization. |
| P13 | Duplicate payment callbacks/submissions | Failed | Failed | AssertionError: 2 != 1 : Repeated pending initiation created separate PaymentAttempt rows |
| P14 | Deviation totals and duplicate prevention | Failed | Failed | AssertionError: 2 != 1 : Identical repeated deviation submission created a second record |

P12 includes the supporting direct-timeout unit. Its API test alone is not sufficient.
### P01 — FR-01 / TC-FR01-01

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Steps: CSRF bootstrap; valid synthetic login; GET identity.

Expected: 200 and owned session.

Actual: Assertions passed; see JUnit and source test.

### P02 — FR-01 / TC-FR01-02

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Steps: CSRF bootstrap; wrong password; GET identity.

Expected: 400 invalid_credentials; no session.

Actual: Assertions passed; see JUnit and source test.

### P03 — SEC-01/03

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Steps: Student requests Director APIs and staff-only writes.

Expected: 403 and no privileged operation.

Actual: Assertions passed; see JUnit and source test.

### P04 — FR-05 / TC-FR05-01

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Steps: Assigned student submits valid dates/reason.

Expected: 201 Pending; assigned Warden and actor history.

Actual: Assertions passed; see JUnit and source test.

### P05 — FR-05 / SEC-04

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Steps: Submit empty, blank-reason and reversed-date payloads.

Expected: 400; zero leave rows.

Actual: Assertions passed; see JUnit and source test.

### P06 — FR-05 / TC-FR05-01

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Steps: Create two leaves; assigned Warden finalizes each.

Expected: Approved/Rejected; two transitions each.

Actual: Assertions passed; see JUnit and source test.

### P07 — FR-06 / TC-FR06-01

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Steps: Assigned student submits within current session and radius.

Expected: 201 Accepted; no raw coordinates in output.

Actual: Assertions passed; see JUnit and source test.

### P08 — FR-06 / TC-FR06-01

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Steps: Submit synthetic point beyond configured radius.

Expected: 201 derived Rejected / OUTSIDE_RADIUS.

Actual: Assertions passed; see JUnit and source test.

### P09 — BR-05 / NFR-03

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Steps: Submit the same accepted student/session twice.

Expected: Second request 409; exactly one row.

Actual: Assertions passed; see JUnit and source test.

### P10 — FR-07 / TC-FR07-01

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Steps: Two students create complaints; first lists/reads second.

Expected: Only own list; cross-read 404.

Actual: Assertions passed; see JUnit and source test.

### P11 — FR-07 / SEC-01

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Steps: Other student tries to resolve complaint.

Expected: 403; original Open state unchanged.

Actual: Assertions passed; see JUnit and source test.

### P12 — FR-09 / TC-FR09-01

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Steps: Fail simulation; mock provider timeout; retry and succeed.

Expected: Unpaid until success; retained failure; normalized timeout error.

Actual: Wrapped-timeout API workflow passes; direct socket TimeoutError escapes normalization.

### P13 — BR-06 / NFR-03 + requested replay invariant

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Steps: Initiate twice while Pending; repeat success callback; initiate after Paid.

Expected: One pending attempt for identical replay; one successful result.

Actual: AssertionError: 2 != 1 : Repeated pending initiation created separate PaymentAttempt rows

### P14 — FR-10 / TC-FR10-01 + requested replay invariant

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Steps: Record rule deviation; read total; repeat identical submission.

Expected: Correct weight total; no duplicate for the same replay.

Actual: AssertionError: 2 != 1 : Identical repeated deviation submission created a second record

## Browser execution

Chromium command started **2026-11-17T06:52:53.802596+00:00**, exit 0.
Recorded Playwright results: **13 passed, 0 failed,
0 skipped, 0 flaky**.
Journeys cover login/profile/navigation, information/study status, Director accounts,
laundry receipt/collection, leave/escalation, attendance/deviations, complaints,
mess/coupons, simulated fees and content publishing, plus privacy and health checks.
Privacy response mocks prove UI behavior only. Health smoke is not load acceptance.
Payment simulation and mocked provider tests do not establish provider acceptance.
Firefox/Edge were not run for this update. Browser runtime is not merged into Jest coverage.

## Open defects and acceptance limits

- `test_P13_duplicate_payment_callbacks_and_submissions`: AssertionError: 2 != 1 : Repeated pending initiation created separate PaymentAttempt rows
- `test_P14_deviation_total_and_duplicate_prevention`: AssertionError: 2 != 1 : Identical repeated deviation submission created a second record
- `test_direct_socket_timeout_is_validation_error`: TimeoutError: Synthetic direct socket timeout

Passing branch coverage does not make these failures passing. Backend suite remains
nonzero. Independent review, complete manual usability, agreed load acceptance,
external provider acceptance, staging/release and recovery rehearsal remain pending.
No commit or push was performed for this update.

[Commands](raw/commands.md), [browser JSON](raw/browser-results.json),
[browser log](raw/e2e.log), [browser HTML](raw/browser-html/index.html),
[JUnit](raw/backend-junit.xml), [failures](raw/observed-failures.json).
