# Truthful member AI prompt and review log

```text
HOSTELSPACE — DETAILED FILE IMPLEMENTATION TASK
STATUS: Instruction-filled starter; application behavior NOT IMPLEMENTED.
TARGET FILE: docs/prompts/anvi/prompt-log.md
ACCOUNTABLE OWNER: Anvi Srinivas
INDEPENDENT REVIEWER: Arin Singh
USER STORIES: US-01, US-02, US-03, US-04, US-17, US-21
DEVELOPMENT PLAN SPRINT(S): 1; 2; 3; summaries after source modules; 4–6 (proposed working mapping; team approval required)
ORIGINAL SRS SPRINT(S): 1; 2; 5; setup from 1; 6 (preserved baseline mapping)
REQUIREMENTS: FR-01; SEC-01–03; FR-01; SEC-03–04; FR-02; FR-11; BR-01; All FRs; architecture; NFR-02, NFR-04; handoff
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

OWNER: Anvi Srinivas | REVIEWER: Arin Singh
TARGET FILE: docs/prompts/anvi/prompt-log.md
DEVELOPMENT-PLAN SPRINT: 1; 2; 3; summaries after source modules; 4–6
ORIGINAL SRS SPRINT: 1; 2; 5; setup from 1; 6
STORY: US-01, US-02, US-03, US-04, US-17, US-21
REQUIREMENTS: FR-01; SEC-01–03; FR-01; SEC-03–04; FR-02; FR-11; BR-01; All FRs; architecture; NFR-02, NFR-04; handoff
RESPONSIBILITY: Truthful member AI prompt and review log
FILE TASK: Store used prompt, date/model, selected US, relevant files, accepted/rejected decisions, human reviewer, actual test output reference and gaps. Template only; do not claim these prompts were used by the member.

US-01 — Sign in, sign out and open the correct dashboard
Dependencies: US-17, US-18
Acceptance context (deliver only the part owned by this file, report remaining dependencies):
- Active users reach the correct role dashboard; invalid/inactive users are denied with a generic message.
- Protected APIs check active sessions and roles even on direct requests.
- Logout invalidates the session and subsequent protected requests fail.
- Use Django sessions; deployment session cookies are HttpOnly, Secure and host-only; login and writes require CSRF.

US-02 — View and update my student profile
Dependencies: US-01
Acceptance context (deliver only the part owned by this file, report remaining dependencies):
- Only the signed-in student can read/update their own profile.
- Valid phone changes persist after refresh; reject empty/malformed input with field messages.
- Phone-only student edits are the proposed baseline pending confirmation; reject protected-field updates to name, SRN, hostel, room and role.

US-03 — Publish and read notices, contacts, information and rules
Dependencies: US-01, US-18
Acceptance context (deliver only the part owned by this file, report remaining dependencies):
- Students see active notices in the current active window, hostel information, contacts and rules.
- Only the Director and explicitly authorized content staff create/edit/deactivate content.
- Reject missing titles and invalid active ranges.
- Keep stable rule IDs; deactivate referenced rules instead of deleting them.

US-04 — Manage authorized users, settings and Director summaries
Dependencies: US-01; US-06, US-07, US-14, US-16 for summaries
Acceptance context (deliver only the part owned by this file, report remaining dependencies):
- Director-only management endpoints activate/deactivate accounts, assign permitted roles and maintain approved settings.
- Deactivated accounts lose access, including existing sessions on subsequent requests.
- Permit only one active Chief Warden; support that Chief supervising multiple wardens and student-to-warden assignment.
- Counts for pending leave, attendance by session, open complaints and unpaid fees match owning-module records; empty sets return zero; do not edit source records through reports.

US-17 — Baseline architecture and scaffold monorepo
Dependencies: None
Acceptance context (deliver only the part owned by this file, report remaining dependencies):
- Working Next.js and Django/DRF skeletons with health response.
- Architecture/deployment diagrams show browser → Next.js → Django → PostgreSQL, external payment/location and separate CI path.
- Record stack revision and duplicate UC correction proposal without changing FR IDs.
- All four members review and can run the skeleton.

US-21 — Validate usability and assemble final handoff
Dependencies: US-01–16; US-22–24 for sign-off
Acceptance context (deliver only the part owned by this file, report remaining dependencies):
- Chrome/Edge/Firefox checks cover labels, actionable errors, keyboard and phone/tablet/desktop usability.
- Final report traces every FR to actual stories, PRs, tests and evidence.
- 15-minute presentation/rehearsal includes each member explaining and demonstrating owned functionality.
- List unfinished work/defects honestly; never label unbuilt stories implemented.

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
