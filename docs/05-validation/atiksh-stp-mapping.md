# Atiksh test mapping to the supplied SRS/SAD/STP

Source: `deliverables/SRS_SAD_STP_ SE_Deliverable_2_3_4.pdf`, SRS FR table (PDF p4),
SAD architecture (p12/p15), STP functional cases (p30), security/nonfunctional
cases (p31), traceability and reporting (p32). Original IDs are retained.
This is an implementation mapping, not team/faculty acceptance or a release sign-off.

| PDF case | Required behavior | Automated evidence / remaining scope |
| --- | --- | --- |
| TC-FR07-01 / FR-07 | Own complaints, assignment, Open ? In Progress ? Resolved, retained history, no revert | `backend/apps/student_services/tests/test_api.py::ComplaintTests`, `test_stp.py::STPAuditTests`, complaint browser journey |
| TC-FR08-01 / FR-08 | Mess Staff creates allocation/coupons; active own records only, range checks, student read-only | `test_api.py::MessTests`, `test_stp.py::STPMessPermissionTests`, FR08 browser journey; PDF permissions enforced instead of folder self-selection/Warden extensions |
| TC-FR09-01 / FR-09 / BR-06 | Verified matching success, failure remains unpaid, pending until verified, duplicate callback idempotent | `test_payments.py::PaymentTests`, `test_stp.py::STPPaymentRaceTests`; browser simulation is explicitly local; real sandbox execution remains Not Run |
| TC-NFR03-01 | Concurrent payment retries cannot create duplicate success | PostgreSQL callback race and unique-success database constraint in `test_stp.py` |
| TC-SEC01-01 / SEC-01,03 | Active sessions, roles and cross-student access denied | `accounts/tests/test_api.py`, complaints/mess/payment ownership tests |
| TC-SEC02-01 | Passwords hashed, secrets absent in responses | Django production hashers retained; identity-secret exclusion test; deployment/database inspection remains Not Run |
| TC-SEC04-01 | Reject malformed/protected inputs without partial writes | Complaint invalid category/description/identity, coupon ranges, fee amount/currency and CSRF API tests |
| TC-SEC06-01 | No payment credentials; server-side verification and no duplicate result | `test_stp.py::STPAuditTests`, `test_payments.py`; mocked provider response/signature checks, no real provider claim |
| TC-NFR02-01 | Labelled forms, corrections, responsive keyboard use | Shared UI/login/complaint/mess/fee RTL tests; complete keyboard/phone manual acceptance remains Not Run |
| TC-NFR04-01 | Chrome, Edge, Firefox smoke flows | Browser CI matrix; local and hosted actual execution recorded separately in evidence |
| TC-NFR05-01 | Automated important validation rules; all required jobs pass | CI lint/tests/build/security/Compose/browser jobs, aggregate required gate |
| TC-CICD-01 | No PR deploy secrets; failures block merge; trusted main tested SHA stages | Test-only CI implemented; branch protection and same-SHA staging not verified/implemented; do not mark complete |
| TC-REL-01 | Restore and rollback known-good build/data with SHA evidence | Not Run; no deployment/recovery authorization or environment supplied |

TC-FR01-01/02 have shared authentication coverage but profile/navigation acceptance
belongs to Anvi. TC-FR02?06, TC-FR10?11, attendance SEC-05 and BR cases belong to
other owners and are not claimed by this branch. TC-NFR01-01 requires approved
20-user/100-warm-visit load; it is Not Run. The STP's 80% coverage target is proposed,
not approved, and no fabricated project-wide percentage is claimed.

Actual executions, environment, gaps and commands: `evidence/atiksh-integration-2026-11-16.md`.
