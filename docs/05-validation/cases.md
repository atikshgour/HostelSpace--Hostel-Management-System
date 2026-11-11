# Validation case register

Prepared from the original SRS requirements and existing starter test-register IDs. Legacy SRS RTM uses TC-01…TC-11; retain those aliases for FR-01…FR-11 rather than claiming a different source naming scheme. This pack preserves the starter’s expanded `TC-FR…`, `TC-NFR…`, `TC-SEC…`, CI and release IDs. These are case specifications, not fabricated test executions.

All cases started **Not Run**. Status below distinguishes actual local evidence from untested full-team acceptance. “Local pass” is not production sign-off. Prerequisites and inputs are fictional/local unless specifically approved otherwise. Story links for teammate modules are planning references and must be reconciled with the actual board before updates.

| Case | Requirements | Story | Owner | Preconditions | Steps/inputs | Expected | Current evidence/status |
|---|---|---|---|---|---|---|---|
| TC-FR01-01 | FR-01 | US-01 | Anvi | Active fictional user/session | Sign in/out; invalid credentials; inactive user | Correct dashboard/session; signed-out access denied | Local login/session/CSRF flow passed; real dashboard/profile NOT RUN |
| TC-FR01-02 | FR-01 | US-02 | Anvi | Student profile and two students | Read/update permitted profile fields; submit protected fields | Only own permitted fields change | NOT RUN — teammate module |
| TC-FR02-01 | FR-02 | US-03 | Anvi | Authorized content staff and student | Create/update/deactivate notice/contact/rule; read as student | Staff maintenance only; active content visible | NOT RUN — teammate content CRUD; Arin rule-choice boundary tested |
| TC-FR03-01 | FR-03; BR-02 | US-04 | Aryan | Current study-room status | Staff sets Open/Closed and optional timings/message; student reads | Latest status; no booking workflow | NOT RUN — teammate module |
| TC-FR04-01 | FR-04; BR-03; BR-04 | US-09; US-10 | Aryan | Allocated laundry day, staff/student | Attempt student reassignment; collect before received; valid handover/collection | No self-selection; receipt precedes collection; history retained | NOT RUN — teammate module |
| TC-FR05-01 | FR-05; BR-01 | US-05; US-06 | Arin | Two assignments, warden, Chief | Valid/invalid leave; scoped reads; escalation/finalization/repeated decision | Pending with server owner; correct staff only; final immutable; timeline retained | LOCAL PASS; PostgreSQL concurrent finalization gate pending |
| TC-FR06-01 | FR-06; BR-05 | US-07 | Arin | Assigned session and approved synthetic policy | Open/close/distance/accuracy/age boundaries; denied location; retry/parallel accept | Only valid in-policy samples accepted; one accepted record; raw sample discarded | LOCAL PASS; PostgreSQL race and real-policy approval pending |
| TC-FR07-01 | FR-07 | US-11; US-12 | Atiksh | Two students and assigned staff | Submit/track complaint; update status; wrong owner read | Valid ID/history; authorized updates; own student only | NOT RUN — teammate module |
| TC-FR08-01 | FR-08 | US-13 | Atiksh | Mess staff and allocated students | Maintain allocation/coupons; read as unrelated student | Only authorized staff write; student sees own active allocation/coupons | NOT RUN — teammate module |
| TC-FR09-01 | FR-09; BR-06 | US-14; US-15 | Atiksh | Fictional provider sandbox only | Payment success/failure; retry/parallel callback | One success reference; failure leaves unpaid; no stored credentials | NOT RUN — teammate module |
| TC-FR10-01 | FR-10; BR-07 | US-08 | Arin | Active rule with 2.50 weight and assigned student | Record; change rule; deactivate; recompute; wrong-role/owner reads | Immutable copied weight; sum active only; retained audit and correct scope | LOCAL PASS; real shared Rule integration pending |
| TC-FR11-01 | FR-11 | US-16 | Anvi | Director and non-Director users | Authorized user/settings/report operations; unauthorized attempt | Only Director management; scoped summaries not personal-record leakage | NOT RUN — teammate module |
| TC-NFR01-01 | NFR-01 | US-22 | All | Agreed target environment/load/dataset | Measure normal-page navigation under agreed test load | Each agreed normal page <3 seconds | NOT RUN — no approved load/performance run |
| TC-NFR02-01 | NFR-02 | US-22 | All | Desktop/mobile keyboard/browser | Read form labels; invalid submit; focus correction | Clear labels/errors and usable controls | PARTIAL — Arin Chromium UI labels/errors/responsive checks passed; full manual accessibility pending |
| TC-NFR03-01 | NFR-03; BR-05 | US-07; US-15 | Arin/Atiksh | PostgreSQL, concurrent clients | Parallel/retry attendance and payment success | No duplicate accepted attendance/successful payment | PARTIAL — local attendance uniqueness/retry passed; PostgreSQL/payment pending |
| TC-NFR04-01 | NFR-04 | US-22 | All | Current Chrome, Edge, Firefox and mobile viewport | Repeat agreed workflows in each browser | Consistent behavior and maintainable independent modules | PARTIAL — Chromium desktop/390px only; Edge/Firefox NOT RUN |
| TC-NFR05-01 | NFR-05 | US-22 | All | Installed automated test environment | Run validation/calculation tests and inspect evidence | Important rules have genuine automated checks | PARTIAL — Arin suite passed; full-team coverage not claimed |
| TC-SEC01-01 | SEC-01; SEC-03 | US-22 | All | Two students/assignments, roles, active/expired sessions | Anonymous/wrong-role/wrong-owner/other-warden requests; UI URL direct navigation | Every protected server request checks active role/session/object scope | PARTIAL — Arin local server cases passed; all teammate modules and production-session policy pending |
| TC-SEC02-01 | SEC-02 | US-01; US-22 | Anvi | Shared real authentication model | Inspect saved password representation and authentication behavior | Secure authentication hashing; no plaintext credential storage/logging | NOT RUN for shared auth — demo uses Django hashing only |
| TC-SEC04-01 | SEC-04 | US-22 | All | Known schema and server allowlists | Bad dates/nonfinite/out-of-range coordinates/nonobject/actor/snapshot fields | Reject invalid/unauthorized input before storage; safe errors | PARTIAL — Arin backend cases passed; teammate modules pending |
| TC-SEC05-01 | SEC-05 | US-07; US-22 | Arin | Fictional location, instrumented browser, DB and logs | Enter page; click submit; deny permission; inspect persistence/background calls | No pre-click/background location; one sample; no raw sample retention | PARTIAL — browser/model/error checks passed; production proxy/APM audit pending |
| TC-SEC06-01 | SEC-06 | US-15; US-22 | Atiksh | Payment sandbox, schemas and logs | Run provider success/failure; inspect data and logs | No card/payment credentials persisted or logged | NOT RUN — teammate payment module |
| TC-CICD-01 | NFR-05; SEC-01; SEC-04 | US-22 | All | Team CI pipeline and reviewed PR | Run clean install/build/test/migration checks in CI | Required checks and review pass with real links | NOT RUN — local commands are not a CI run |
| TC-REL-01 | All FR/NFR/SEC/BR | US-22 | All | Merged app, all owner approvals, deployment staging | Complete regression, backup/migration/rollback and demo checklist | No open release blockers; truthful reviewed traceability | NOT RUN — no release/deployment performed |

## Arin focused subcases (automated)

- US-05: create Pending and server assignment; end-before-start; empty/missing/unknown fields; own history; unknown UUID; pagination.
- US-06: assigned warden only; Chief cannot view Pending; escalation→Chief approval; final repeated decision is 409; immutable transition history; PostgreSQL double-finalization test (skips on SQLite).
- US-07: valid sample; one accepted result; rejected low-accuracy attempt can retry; inclusive opening/closing/radius/accuracy/age boundaries; stale/future/outside-window/outside-radius; nonfinite/out-of-range; unassigned session; denied/unavailable browser sample; no location before click; no stored sample fields; PostgreSQL concurrent acceptance test (skips on SQLite).
- US-08: staff-only writes; assignment scope; active rule only; caller weight rejected; copied rule weight unchanged after source update; deactivation retained and repeated deactivation conflict; active-only sum; student cannot expand own total with a query ID.
- US-18/22: coarse roles + scoped server objects, inactive role helper, session CSRF and login CSRF, no-store cache, safe validation fields, malformed student IDs and nonobject payloads.

## Full business-rule trace (none omitted)

| Rule | Case | Local/full status |
|---|---|---|
| BR-01 one Chief supervises multiple wardens | TC-FR05-01; TC-SEC01-01 | Local harness models one active Chief and supervised flows; real shared account constraint pending |
| BR-02 no study-room booking | TC-FR03-01 | Not Run — Aryan |
| BR-03 no student laundry-day selection | TC-FR04-01 | Not Run — Aryan |
| BR-04 received before collected | TC-FR04-01 | Not Run — Aryan |
| BR-05 one accepted attendance per session/student | TC-FR06-01; TC-NFR03-01 | Local uniqueness/retry pass; PostgreSQL race pending |
| BR-06 failed payment leaves unpaid | TC-FR09-01 | Not Run — Atiksh |
| BR-07 active deviations sum | TC-FR10-01 | Local backend and live lifecycle pass |

SEC-03 is explicitly traced under TC-SEC01-01 and each personal-record functional case. No full-project security requirement is marked complete from Arin-only evidence.
