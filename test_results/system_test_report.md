# System, integration and browser test report

Generated 2026-11-17T07:11:08.486339+00:00 from recorded artifacts.
Backend execution: 2026-11-17T07:06:55.032939+00:00; frontend: 2026-11-17T07:05:49.767215+00:00.
Source HEAD: `f921d4cdd399803451d4d3c0e30e72d587eb074a` plus uncommitted test/config/script changes.
Local synthetic PostgreSQL only. No production data changes or live payments.
Publication is user-authorized; command metadata identifies the tested source HEAD.
Each command's own timestamp/exit is preserved in [commands](supporting_artifacts/raw/commands.md).
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
| P12 | Payment success/failure/timeout/retry | Passed | Passed | Assertions passed; see JUnit and source test. |
| P13 | Duplicate payment callbacks/submissions | Passed | Passed | Assertions passed; see JUnit and source test. |
| P14 | Deviation totals and duplicate prevention | Passed | Passed | Assertions passed; see JUnit and source test. |

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

Actual: Assertions passed; see JUnit and source test.

### P13 — BR-06 / NFR-03 + requested replay invariant

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Steps: Initiate twice while Pending; repeat success callback; initiate after Paid.

Expected: One pending attempt for identical replay; one successful result.

Actual: Assertions passed; see JUnit and source test.

### P14 — FR-10 / TC-FR10-01 + requested replay invariant

Preconditions: Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider.

Steps: Record rule deviation; read total; repeat identical submission.

Expected: Correct weight total; no duplicate for the same replay.

Actual: Assertions passed; see JUnit and source test.

## Browser execution

Chromium command started **2026-11-17T07:09:06.490022+00:00**, exit 0.
Recorded Playwright results: **13 passed, 0 failed,
0 skipped, 0 flaky**.
Journeys cover login/profile/navigation, information/study status, Director accounts,
laundry receipt/collection, leave/escalation, attendance/deviations, complaints,
mess/coupons, simulated fees and content publishing, plus privacy and health checks.
Privacy response mocks prove UI behavior only. Health smoke is not load acceptance.
Payment simulation and mocked provider tests do not establish provider acceptance.
Firefox/Edge were not run for this update. Browser runtime is not merged into Jest coverage.

## Open defects and acceptance limits

None.

Coverage and test outcomes are separate; backend has 178 passed and 0 failed.
Independent review, complete manual usability, agreed load acceptance,
external provider acceptance, staging/release and recovery rehearsal remain pending.
Publication is separately user-authorized and is not acceptance evidence.

[Commands](supporting_artifacts/raw/commands.md), [browser JSON](supporting_artifacts/raw/browser-results.json),
[browser log](supporting_artifacts/raw/e2e.log), [browser HTML](supporting_artifacts/raw/browser-html/index.html),
[JUnit](supporting_artifacts/raw/backend-junit.xml), [failures](supporting_artifacts/raw/observed-failures.json).
