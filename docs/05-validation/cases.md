# Full expected test case register

```text
HOSTELSPACE — DETAILED FILE IMPLEMENTATION TASK
STATUS: Instruction-filled starter; application behavior NOT IMPLEMENTED.
TARGET FILE: docs/05-validation/cases.md
ACCOUNTABLE OWNER: Arin Singh
INDEPENDENT REVIEWER: Aryan Singh
USER STORIES: US-22
DEVELOPMENT PLAN SPRINT(S): 1 design; 4–6 execution (proposed working mapping; team approval required)
ORIGINAL SRS SPRINT(S): 1 design; 6 final validation (preserved baseline mapping)
REQUIREMENTS: All FR/NFR/SEC/BR
FILE PURPOSE: Full expected test case register

WHAT TO IMPLEMENT IN THIS FILE
Retain STP IDs TC-FR01-01/02 and TC-FR02-01 through TC-FR11-01, TC-NFR01–05-01, TC-SEC01/02/04/05/06-01, TC-CICD-01 and TC-REL-01. Add trace for every BR and SEC-03 under SEC01. Initial status Not Run.

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

OWNER: Arin Singh | REVIEWER: Aryan Singh
TARGET FILE: docs/05-validation/cases.md
DEVELOPMENT-PLAN SPRINT: 1 design; 4–6 execution
ORIGINAL SRS SPRINT: 1 design; 6 final validation
STORY: US-22
REQUIREMENTS: All FR/NFR/SEC/BR
RESPONSIBILITY: Full expected test case register
FILE TASK: Retain STP IDs TC-FR01-01/02 and TC-FR02-01 through TC-FR11-01, TC-NFR01–05-01, TC-SEC01/02/04/05/06-01, TC-CICD-01 and TC-REL-01. Add trace for every BR and SEC-03 under SEC01. Initial status Not Run.

US-22 — Maintain validation and verify access rules
Dependencies: US-18; feature slices for execution
Acceptance context (deliver only the part owned by this file, report remaining dependencies):
- Every FR, NFR, SEC and BR has cases with preconditions/input/expected result.
- Seeded role, session, CSRF and ownership checks cover all personal modules, only against own local/staging app.
- Attendance boundary/retry cases on PostgreSQL; no retained raw location.
- Fill actual results only after execution; link failed cases to observed bugs and rerun. Tests remain Not Run initially.

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
