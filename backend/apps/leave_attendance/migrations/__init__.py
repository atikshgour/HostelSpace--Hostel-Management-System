# HOSTELSPACE — DETAILED FILE IMPLEMENTATION TASK
# STATUS: Instruction-filled starter; application behavior NOT IMPLEMENTED.
# TARGET FILE: backend/apps/leave_attendance/migrations/__init__.py
# ACCOUNTABLE OWNER: Arin Singh
# INDEPENDENT REVIEWER: Aryan Singh
# USER STORIES: US-05, US-06, US-07, US-08
# DEVELOPMENT PLAN SPRINT(S): 2; 3 (proposed working mapping; team approval required)
# ORIGINAL SRS SPRINT(S): 3; 4 (preserved baseline mapping)
# REQUIREMENTS: FR-05; SEC-03–04; FR-05; BR-01; FR-06; NFR-03; SEC-05; BR-05; FR-10; BR-07
# FILE PURPOSE: Python package marker
#
# WHAT TO IMPLEMENT IN THIS FILE
# Keep conventional package marker minimal; no import-time side effects or fake business logic; use tests/ package, never conflicting tests.py.
#
# BEFORE STARTING
# 1. Read README.md, AGENTS.md, current source documents, relevant story and contracts.
# 2. Check actual repository state and Git diff; no existing implementation is implied by this starter.
# 3. Resolve blocked dependencies before inventing interfaces or missing policies.
# 4. Inspect frontend/src/app/globals.css and docs/ui/design-system.md for UI work.
# 5. Preserve HISTORY.md, domain transition history and other owners' reviewed work.
#
# COPY-READY AI IMPLEMENTATION PROMPT
# You are assisting Team 11 with HostelSpace. Read README.md, AGENTS.md, HISTORY.md, CHANGELOG.md, current SRS/SAD/STP, docs/decisions/, docs/04-design/api-contract.md, docs/04-design/role-permissions.md and the latest relevant Git history/diff before editing. Explicitly inspect frontend/src/app/globals.css and docs/ui/design-system.md before any UI change; reuse existing tokens/components, never invent a second palette or reset shared styles. If files/history do not yet exist, report that and establish only the approved foundation; never fabricate history.
# Use Next.js App Router + JavaScript + Tailwind, Django/DRF sessions and CSRF, Django ORM and PostgreSQL. No direct Next.js SQL, NextAuth, JWT-in-localStorage or second backend. Use SQLite only in explicit local quick mode. Use the reviewed API contract (plural /api/leaves/; reconcile the older /api/leave/ example rather than creating duplicates). Server authorization is authoritative; scope queries to active roles, ownership and assignment. Match standardized JSON errors {code,message,fields}; protect login CSRF explicitly. Never cache authenticated API responses. Use synthetic records only.
# Implement only this file's responsibility for the selected story, integrating with existing code. List affected paths, dependencies and unanswered decisions first. Do not overwrite another owner's module. Keep names required by Next.js/Django unchanged. Add owner/story/sprint header comments where the format permits; for JSON, generated lockfiles and migrations use the manifest/sidecar instead of invalid comments. Do not modify generated files by hand.
# Preserve operational history: append transitions with actor, server time, old/new state and remarks; do not rewrite past laundry details, deviation weights or payment attempts. Never store raw student geolocation, passwords in plaintext, payment credentials, session cookies or secrets in logs/prompts/history. Current state must come from the backend, not fabricated UI data.
# Add or update focused pytest/API tests and Jest/RTL component tests as relevant; use Playwright for complete and async-server flows. Verify PostgreSQL constraints/concurrency where relevant. Never weaken tests or fabricate test results. Do not deploy, use live payments, delete/reset data, run production migrations, commit or push without explicit approval.
# Return changed-file diff, actual commands/results, acceptance criteria covered, remaining gaps and explanation for the named owner to demonstrate. After human review, append a truthful handoff entry to HISTORY.md and docs/prompts/<owner>/ including story, files, decisions, tests actually run and reviewer. Update the RTM with real evidence only.
#
# OWNER: Arin Singh | REVIEWER: Aryan Singh
# TARGET FILE: backend/apps/leave_attendance/migrations/__init__.py
# DEVELOPMENT-PLAN SPRINT: 2; 3
# ORIGINAL SRS SPRINT: 3; 4
# STORY: US-05, US-06, US-07, US-08
# REQUIREMENTS: FR-05; SEC-03–04; FR-05; BR-01; FR-06; NFR-03; SEC-05; BR-05; FR-10; BR-07
# RESPONSIBILITY: Python package marker
# FILE TASK: Keep conventional package marker minimal; no import-time side effects or fake business logic; use tests/ package, never conflicting tests.py.
#
# US-05 — Submit and track a leave request
# Dependencies: US-01, US-18
# Acceptance context (deliver only the part owned by this file, report remaining dependencies):
# - Valid dates and non-empty reason create a Pending request with ID and submission time.
# - Reject end before start and missing input.
# - Derive student identity and assigned warden on the server; show assigned requests to that warden.
# - Students see only their own request history.
#
# US-06 — Review leave and escalate to the Chief Warden
# Dependencies: US-05
# Acceptance context (deliver only the part owned by this file, report remaining dependencies):
# - Only the assigned Warden decides Pending: Approve, Reject or Escalate.
# - Only Chief Warden finalizes Escalated requests.
# - Approved/Rejected are final and immutable; concurrent/repeated decisions cannot overwrite them.
# - Append actor, server timestamp, previous/new status and remarks for each transition; student sees status and decision history.
#
# US-07 — Configure attendance sessions and submit one-time location attendance
# Dependencies: US-01, US-18; approved attendance policy
# Acceptance context (deliver only the part owned by this file, report remaining dependencies):
# - Authorized wardens configure start/end, centre and positive radius; end follows start.
# - Server validates inclusive time window, distance and approved accuracy threshold; valid in-range submissions yield one accepted record.
# - Closed/outside-range/denied/unavailable/low-accuracy cases do not create accepted attendance.
# - PostgreSQL uniqueness and atomic handling prevent concurrent or retry duplicate accepted records per student/session.
# - Request one geolocation sample only after Submit; no watchPosition, background polling or retained raw student coordinates in DB/logs/history. Retain time and check result only; browser location is not tamper-proof.
#
# US-08 — Record deviations and calculate active weightage
# Dependencies: US-01, US-03
# Acceptance context (deliver only the part owned by this file, report remaining dependencies):
# - Authorized wardens record student, existing rule, copied rule weightage, remarks, actor and server time; students cannot write.
# - Sum active entries only, excluding deactivated entries.
# - Changing the source rule must not rewrite historical copied weightage.
# - Student read-only history is owner-scoped; staff reads are authorization-scoped.
#
# OWNER'S REVIEW / HANDOFF CHECKLIST
# [ ] This file contains a real, understood implementation rather than this instruction placeholder.
# [ ] Imports/exports, callers and reviewed API contracts agree with the integrated repository.
# [ ] Only this file's responsibility is implemented; related changes are listed for review.
# [ ] Server-side role, ownership, assignment and input validation are checked where applicable.
# [ ] Loading, empty, error and success UI states use shared CSS/components where applicable.
# [ ] Operational transitions retain actor, server time, remarks and immutable historical data.
# [ ] Focused tests exercise applicable positive, negative, boundary and retry cases.
# [ ] Commands actually run and actual outcomes are recorded; unexecuted checks remain Not Run.
# [ ] Migrations/lockfiles are generated by the actual selected tools, never fabricated.
# [ ] No secrets, raw attendance coordinates or payment credentials enter source/logs/evidence.
# [ ] Independent reviewer checks the diff; RTM and truthful handoff records are updated.
# [ ] No live payments, production data changes, deployments, commits or pushes without approval.
#
# IMPLEMENTATION HANDOFF — FILL ONLY AFTER REAL WORK
# Actual Jira key: Not created
# Implementation status: Not implemented
# Changed paths: Not recorded
# Commands and observed results: Not Run
# Unresolved decisions / limitations: Record before implementation
# PR / reviewer / evidence: Not available

# IMPLEMENTATION AREA: replace this marker with reviewed content.
