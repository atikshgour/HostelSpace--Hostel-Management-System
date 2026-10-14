# Truthful member AI prompt and review log

```text
HOSTELSPACE — DETAILED FILE IMPLEMENTATION TASK
STATUS: Instruction-filled starter; application behavior NOT IMPLEMENTED.
TARGET FILE: docs/prompts/atiksh/prompt-log.md
ACCOUNTABLE OWNER: Atiksh Gour
INDEPENDENT REVIEWER: Anvi Srinivas
USER STORIES: US-13, US-14, US-15, US-16, US-20, US-24
DEVELOPMENT PLAN SPRINT(S): 2; 3; 1 setup; 3 promotion completion; 5–6 (proposed working mapping; team approval required)
ORIGINAL SRS SPRINT(S): 4; 5; 1 setup; 6 final evidence; 6 (preserved baseline mapping)
REQUIREMENTS: FR-07; SEC-03–04; FR-07; SEC-01; FR-08; SEC-03–04; FR-09; NFR-03; SEC-06; BR-06; CI/CD; NFR-05; FR-09; NFR-03; SEC-06; recovery
FILE PURPOSE: Truthful member AI prompt and review log

WHAT TO IMPLEMENT IN THIS FILE
Store used prompt, date/model, selected US, relevant files, accepted/rejected decisions, human reviewer, actual test output reference and gaps. Template only; do not claim these prompts were used by the member.

BEFORE STARTING
1. Read README.md, AGENTS.md, current source documents, relevant story and contracts.
2. Check actual repository state and Git diff; no existing implementation is implied by this starter.
3. Resolve blocked dependencies before inventing interfaces or missing policies.
4. Inspect frontend/src/app/globals.css and docs/ui/design-system.md for UI work.
5. Preserve HISTORY.md, domain transition history and other owners' reviewed work.

COPY-READY AI IMPLEMENTATION PROMPT
You are assisting Team 11 with HostelSpace. Read README.md, AGENTS.md, HISTORY.md, CHANGELOG.md, current SRS/SAD/STP, docs/decisions/, docs/04-design/api-contract.md, docs/04-design/role-permissions.md and the latest relevant Git history/diff before editing. Explicitly inspect frontend/src/app/globals.css and docs/ui/design-system.md before any UI change; reuse existing tokens/components, never invent a second palette or reset shared styles. If files/history do not yet exist, report that and establish only the approved foundation; never fabricate history.
Use Next.js App Router + JavaScript + Tailwind, Django/DRF sessions and CSRF, Django ORM and PostgreSQL. No direct Next.js SQL, NextAuth, JWT-in-localStorage or second backend. Use SQLite only in explicit local quick mode. Use the reviewed API contract (plural /api/leaves/; reconcile the older /api/leave/ example rather than creating duplicates). Server authorization is authoritative; scope queries to active roles, ownership and assignment. Match standardized JSON errors {code,message,fields}; protect login CSRF explicitly. Never cache authenticated API responses. Use synthetic records only.
Implement only this file's responsibility for the selected story, integrating with existing code. List affected paths, dependencies and unanswered decisions first. Do not overwrite another owner's module. Keep names required by Next.js/Django unchanged. Add owner/story/sprint header comments where the format permits; for JSON, generated lockfiles and migrations use the manifest/sidecar instead of invalid comments. Do not modify generated files by hand.
Preserve operational history: append transitions with actor, server time, old/new state and remarks; do not rewrite past laundry details, deviation weights or payment attempts. Never store raw student geolocation, passwords in plaintext, payment credentials, session cookies or secrets in logs/prompts/history. Current state must come from the backend, not fabricated UI data.
Add or update focused pytest/API tests and Jest/RTL component tests as relevant; use Playwright for complete and async-server flows. Verify PostgreSQL constraints/concurrency where relevant. Never weaken tests or fabricate test results. Do not deploy, use live payments, delete/reset data, run production migrations, commit or push without explicit approval.
Return changed-file diff, actual commands/results, acceptance criteria covered, remaining gaps and explanation for the named owner to demonstrate. After human review, append a truthful handoff entry to HISTORY.md and docs/prompts/<owner>/ including story, files, decisions, tests actually run and reviewer. Update the RTM with real evidence only.

OWNER: Atiksh Gour | REVIEWER: Anvi Srinivas
TARGET FILE: docs/prompts/atiksh/prompt-log.md
DEVELOPMENT-PLAN SPRINT: 2; 3; 1 setup; 3 promotion completion; 5–6
ORIGINAL SRS SPRINT: 4; 5; 1 setup; 6 final evidence; 6
STORY: US-13, US-14, US-15, US-16, US-20, US-24
REQUIREMENTS: FR-07; SEC-03–04; FR-07; SEC-01; FR-08; SEC-03–04; FR-09; NFR-03; SEC-06; BR-06; CI/CD; NFR-05; FR-09; NFR-03; SEC-06; recovery
RESPONSIBILITY: Truthful member AI prompt and review log
FILE TASK: Store used prompt, date/model, selected US, relevant files, accepted/rejected decisions, human reviewer, actual test output reference and gaps. Template only; do not claim these prompts were used by the member.

US-13 — Submit and track maintenance complaint
Dependencies: US-01, US-18
Acceptance context (deliver only the part owned by this file, report remaining dependencies):
- Use server student profile room plus valid category and non-empty description.
- Create Open complaint with ID; invalid input yields field errors and no record.
- Own list/detail persists after refresh.
- No cross-student reads or modifications.

US-14 — Assign complaints and update progress
Dependencies: US-13
Acceptance context (deliver only the part owned by this file, report remaining dependencies):
- Director assigns to active Maintenance Staff.
- Only assigned staff or Director perform permitted transitions Open → In Progress → Resolved.
- Append actor, server time and remarks per transition; no silent revert of resolved complaint.
- Student sees current status and history but cannot edit assignment or staff remarks.

US-15 — Manage mess allocation and active coupons
Dependencies: US-01, US-18
Acceptance context (deliver only the part owned by this file, report remaining dependencies):
- Only Mess Staff creates/updates allocations and coupons.
- Student sees current personal assigned mess and active currently valid coupons.
- Reject invalid date range and missing coupon code.
- No cross-student access or student writes; no ordering, QR redemption or billing.

US-16 — View fees and verify test payment results
Dependencies: US-01, US-18; sandbox provider access
Acceptance context (deliver only the part owned by this file, report remaining dependencies):
- Separate FeeDue and PaymentAttempt; fixed-precision amount/currency; initiate for server-calculated amount.
- Only verified server-side matching fee/order/amount/currency success marks fee Paid.
- Failed/cancelled attempts leave Unpaid; unverified result stays Pending.
- Unique provider reference plus atomic update prevents duplicate success even on concurrent callbacks/retries.
- Keep failure/cancellation/pending attempt history; no credentials, card/UPI PINs or real funds; provider-hosted test checkout only. Simulation requires faculty approval and explicit labeling.

US-20 — Gate PRs and deploy reviewed releases
Dependencies: US-17, US-18, US-19
Acceptance context (deliver only the part owned by this file, report remaining dependencies):
- PRs run lint/scanners/PostgreSQL backend tests/frontend tests/builds without deployment secrets.
- Branch protection and independent review block failed required checks; empty tests are not success.
- Trusted successful main push deploys staging for the same source SHA; wait for readiness/version and smoke success.
- Only approved production promotion of the same reviewed SHA; document manual approval alternative if plan lacks reviewers.
- Preserve real CI/coverage/scanner artifacts including failures; no queued-deploy-as-success or host auto-deploy bypass.

US-24 — Verify recovery and complete maintenance guidance
Dependencies: US-16, US-20; US-23 before release
Acceptance context (deliver only the part owned by this file, report remaining dependencies):
- Restore synthetic PostgreSQL backup into separate database and verify expected counts.
- Record/test known-good frontend/API rollback after checking schema compatibility; app rollback does not reverse migrations.
- Retest sandbox success/failure/pending/duplicate payment acceptance with no real funds/data.
- Name maintainers, weekly dependency review, backups, incident/bug triage and recovery steps; no dumps/secrets in repository.

OWNER'S REVIEW / HANDOFF CHECKLIST
[ ] This file contains a real, understood implementation rather than this instruction placeholder.
[ ] Imports/exports, callers and reviewed API contracts agree with the integrated repository.
[ ] Only this file's responsibility is implemented; related changes are listed for review.
[ ] Server-side role, ownership, assignment and input validation are checked where applicable.
[ ] Loading, empty, error and success UI states use shared CSS/components where applicable.
[ ] Operational transitions retain actor, server time, remarks and immutable historical data.
[ ] Focused tests exercise applicable positive, negative, boundary and retry cases.
[ ] Commands actually run and actual outcomes are recorded; unexecuted checks remain Not Run.
[ ] Migrations/lockfiles are generated by the actual selected tools, never fabricated.
[ ] No secrets, raw attendance coordinates or payment credentials enter source/logs/evidence.
[ ] Independent reviewer checks the diff; RTM and truthful handoff records are updated.
[ ] No live payments, production data changes, deployments, commits or pushes without approval.

IMPLEMENTATION HANDOFF — FILL ONLY AFTER REAL WORK
Actual Jira key: Not created
Implementation status: Not implemented
Changed paths: Not recorded
Commands and observed results: Not Run
Unresolved decisions / limitations: Record before implementation
PR / reviewer / evidence: Not available
```
