/*
HOSTELSPACE — DETAILED FILE IMPLEMENTATION TASK
STATUS: Instruction-filled starter; application behavior NOT IMPLEMENTED.
TARGET FILE: frontend/src/features/study-room/api.js
ACCOUNTABLE OWNER: Aryan Singh
INDEPENDENT REVIEWER: Atiksh Gour
USER STORIES: US-09
DEVELOPMENT PLAN SPRINT(S): 2 (proposed working mapping; team approval required)
ORIGINAL SRS SPRINT(S): 2 (preserved baseline mapping)
REQUIREMENTS: FR-03; BR-02
FILE PURPOSE: Feature API wrapper

WHAT TO IMPLEMENT IN THIS FILE
Only canonical study-room endpoints through shared lib/api.js; no own auth, DB access, hardcoded demo success or bypassed CSRF; normalize domain errors.

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

OWNER: Aryan Singh | REVIEWER: Atiksh Gour
TARGET FILE: frontend/src/features/study-room/api.js
DEVELOPMENT-PLAN SPRINT: 2
ORIGINAL SRS SPRINT: 2
STORY: US-09
REQUIREMENTS: FR-03; BR-02
RESPONSIBILITY: Feature API wrapper
FILE TASK: Only canonical study-room endpoints through shared lib/api.js; no own auth, DB access, hardcoded demo success or bypassed CSRF; normalize domain errors.

US-09 — Display and update study-room Open/Closed status
Dependencies: US-01; approved updater permissions
Acceptance context (deliver only the part owned by this file, report remaining dependencies):
- Accept only Open or Closed.
- Show latest status, optional timings/message and update time.
- Only Director or explicitly permitted staff update; record updating user.
- No booking, seats, reservation API or student edit action. Preserve legacy UC-02; UC-11 is a proposed controlled correction, not an approved change.

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
*/

/* IMPLEMENTATION AREA: replace this marker with reviewed code. */
