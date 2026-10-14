# HostelSpace

## Hostel Management System

HostelSpace is a browser-based hostel management system developed for the **UE24CS341A - Software Engineering** course at **PES University, Bangalore**.

HostelSpace is a simple web-based hostel management system for students and hostel staff. At present, many hostel activities are handled through notice boards, paper forms, registers, messages, and repeated visits to the hostel office.
Information is spread across different places, so students may need to ask several people before they receive an update. Staff also have to check different records to answer common questions.

HostelSpace brings these activities into one portal. A student can sign in, view hostel notices and rules, check whether the study room is open, see the assigned laundry day, track clothes given and collected, apply for leave, submit attendance, raise a maintenance complaint, view mess details, pay hostel fees, and check deviation-weightage records. Students will see only their own records and the services available to them.

Hostel staff will use the same system according to their roles. Wardens will process leave, attendance, and discipline records. The Chief Warden will supervise the wardens and handle important cases. The Hostel Director will have overall control of hostel information and authorized users. Laundry, mess, and maintenance staff will update only the records related to their work. The project keeps every feature direct and limited so that the team can build, test, and explain the complete system within the course schedule.

## Project Information

| Item | Details |
|---|---|
| Project Name | HostelSpace |
| Project | Hostel Management System |
| Course | UE24CS341A - Software Engineering |
| University | PES University, Bangalore |
| Department | Computer Science and Engineering |
| Team | Team 11 |
| Methodology | Agile |
| Version | 1.0 |
| Development | Git and GitHub |
| Project Planning | Jira |

## Team Members

| Name | USN | Primary Responsibilities |
|---|---|---|
| Anvi Srinivas | PES1UG24CS076 | Student profile, notices, information, contacts, and hostel rules |
| Arin Singh | PES1UG24CS079 | Leave, location-verified attendance, and deviation records |
| Aryan Singh | PES1UG24CS086 | Study-room status, laundry allocation, handover, and collection |
| Atiksh Gour | PES1UG24CS096 | Maintenance complaints, mess and coupons, and hostel fee payment |

## Project Scope

HostelSpace covers the following first-version functionality:

- Role-based sign-in and student profile access
- Hostel notices, contacts, information, and rules
- Study-room open or closed status
- Assigned laundry-day tracking
- Laundry handover and collection tracking
- Leave management
- Location-verified attendance submission
- Maintenance complaints
- Mess allocation and coupons
- Hostel fee payment records
- Deviation-weightage records
- Authorized staff updates and Hostel Director reports

Students can view hostel notices and rules, check the study-room status, see their assigned laundry day, track clothes, apply for leave, submit attendance, raise maintenance complaints, view mess details, pay hostel fees, and review their deviation-weightage records. Students see only their own records and the services available to them.

### Out of Scope

The first version does not include:

- Study-room booking
- Student selection of laundry days
- Continuous location tracking
- Full hostel accounting
- Biometric devices
- Inventory management
- Native mobile application

## User Roles

The system supports the following user classes:

- **Student** - Uses student services and views personal records
- **Warden** - Reviews leave, views attendance, and records deviations
- **Chief Warden** - Supervises wardens and handles escalated matters
- **Hostel Director** - Controls authorized users, information, settings, and reports
- **Maintenance Staff** - Updates assigned maintenance complaints
- **Mess Staff** - Maintains mess allocation and coupons
- **Laundry Staff** - Maintains assigned laundry days and handover or collection records

Staff members use the system according to their roles. Each staff role updates only the records related to its work, while wardens, the Chief Warden, and the Hostel Director handle progressively broader oversight and authorization responsibilities.

## Technology Stack

- **Frontend:** Next.js
- **Languages:** JavaScript, HTML, CSS
- **Database:** SQL
- **Authentication:** Role-based authentication
- **Version Control:** Git and GitHub
- **Project Management:** Jira

## System Architecture

At a high level, HostelSpace follows this structure:

```text
		    +------------------+
		    |      Users       |
		    | Student / Staff  |
		    +--------+---------+
			     |
			     v
		    +------------------+
		    |     Browser      |
		    +--------+---------+
			     |
			     v
		    +------------------+
		    |     Next.js      |
		    |  Web Application |
		    +--------+---------+
			     |
	      +--------------+--------------+
	      |                             |
	      v                             v
      +------------------+        +------------------+
      | Authentication & |        |    Application   |
      | Role Management  |        |     Services     |
      +------------------+        +--------+---------+
					   |
					   v
				  +------------------+
				  |    SQL Database  |
				  +------------------+
```
## Maintenance Complaints

Students can submit maintenance complaints, and authorized staff can update their status.



**This ZIP contains the actual proposed project tree, not only a file-task catalog.**
Every one of the 275 planned paths exists and contains its own detailed implementation instructions.
This is an instruction-filled starter, **not a runnable Next.js/Django application**. No feature implementation,
passing application tests, deployment, Jira creation or faculty approval is claimed.

## Open this first
1. Extract the ZIP. Open the `hostelspace` folder in your editor.
2. Read `START_HERE.md`, `PROJECT_TREE.txt`, `AGENTS.md` and `docs/decisions/baseline.md`.
3. Find your module or filter `FILE_MANIFEST.json` by owner/story; open the actual source file.
4. Read its owner, reviewer, sprint mappings, responsibility and acceptance context.
5. Copy the complete AI prompt from inside that file. Ask AI to implement one reviewed slice, not the entire project.
6. Replace that file's placeholder with real code; retain a concise owner/story/sprint header where allowed.
7. Run actual checks, request independent review and record honest results in the RTM and history.

## What is inside each file?
- Full accountable owner and independent reviewer names.
- Development Plan sprint mapping and original SRS sprint mapping.
- US IDs and relevant requirement references.
- File-specific responsibility and detailed implementation task.
- Complete copy-ready prompt including relevant story dependencies and acceptance context.
- Global CSS/shared UI, security, validation, domain-history and handoff requirements.
- Review checklist and deliberately unfilled implementation/evidence fields.

Instructions are comments in JS/JSX/CSS/Python/shell/configuration files, normal content in Markdown,
and `_file_task` arrays in JSON. JSON contains no illegal comments. Configurations still require real implementation.
**`package-lock.json` files are explicitly marked placeholders, not genuine npm lockfiles.** Replace the package
manifest with reviewed dependencies, remove the placeholder lockfile, and generate a real lockfile with npm.
Do not try `npm ci` until a real matching lockfile exists. No dependency versions are invented here.

**`migrations/0001_initial.py` files are instruction placeholders, not generated Django migrations.**
Choose the user model and implement reviewed models first. Remove only these untouched starter migration placeholders
before running `makemigrations` against the local development configuration. Never remove a real applied migration.
The Director app has no planned model migration unless the approved design adds actual owned models.

`manage.py` and shell scripts stop with a clear message. GitHub workflows are manual-only readiness blockers;
they do not deploy, receive secrets, or pretend to run real tests. Feature/test files contain instructions, not passing stubs.
`globals.css` additionally includes a proposed reusable token/base-style foundation; the app UI is not implemented.

## Ownership
| Owner | Feature stories | Shared stories | Primary reviewer |
| --- | --- | --- | --- |
| Anvi Srinivas | US-01–04: auth/profile/information/Director | US-17 architecture; US-21 usability/handoff | Arin Singh |
| Arin Singh | US-05–08: leave/attendance/deviations | US-18 schema/contracts; US-22 validation | Aryan Singh |
| Aryan Singh | US-09–12: study room/laundry | US-19 Docker; US-23 integration | Atiksh Gour |
| Atiksh Gour | US-13–16: complaints/mess/fees | US-20 CI/CD; US-24 recovery | Anvi Srinivas |

## Build order
1. Agree open policies and actual schedule. No historical sprint work is implied.
2. US-17 + US-18: scaffold, one shared user model, API/role contracts and style/history foundations.
3. US-19 + US-01 + initial US-20: PostgreSQL/Docker/demo data, auth/CSRF/proxy vertical slice and real checks.
4. Parallel feature slices after authentication: Anvi US-02/03; Arin US-05 then 06; Aryan US-09 and 10 then 11 then 12;
   Atiksh US-13 then 14. US-03 rules precedes US-08 deviations.
5. US-07 after attendance policy; US-15 mess; US-16 fees after approved provider sandbox access.
6. Complete US-04 summaries only after source services exist; continue US-21/22/23 throughout.
7. US-24 recovery, final regression and real independent release approval.

## Sources and constraints
The supplied SAD and Development Plan select Browser → Next.js/JavaScript/Tailwind → Django/DRF → PostgreSQL.
Earlier direct-SQL wording in Synopsis/SRS requires recorded revision, not silent alteration.
All FR-01–11, NFR-01–05, SEC-01–06 and BR-01–07 remain in scope. Both sprint mappings are kept in file headers.
The supplied PDFs are source documents, not proof of approval or implementation.

Agree phone-only profile updates, authorized content/study updaters, attendance centre/radius/accuracy/time policy,
payment sandbox/provider, test load/coverage targets, actual GitHub handles, hosting resources and official deadline.
No public signup, booking/reservation, student laundry-day selection, continuous tracking, meal ordering/QR redemption,
full accounting, biometrics, inventory, native app, Redis, Celery, microservices or Kubernetes.

## History has two meanings
- **Project history:** `HISTORY.md`, `CHANGELOG.md`, prompt logs, Git/PR decisions and real commands/results.
- **Operational history:** append-only leave/complaint transitions; original laundry handover/collection details;
  copied historical deviation weightage; separate fee/payment attempts and verified payment references.
Never invent old activity or keep raw attendance coordinates, credentials, session cookies or payment secrets in either history.

## Where to find things
`frontend/`: actual route/component/client/style/config paths.
`backend/`: actual Django configuration, app/model/service/permission/test/migration paths.
`tests/`: actual E2E, security and system-validation paths.
`.github/`, `scripts/`, `compose.yaml`: delivery and recovery starter paths.
`docs/`: design, architecture, validation, test summary, maintenance, report, demo and individual prompt logs.
`evidence/`: guidance for genuine sanitized evidence, not fabricated test outputs.
`reference/HostelSpace_Build_Guide.html`: optional searchable companion guide; not a replacement for this tree.

## Validation boundary
`STARTER_QA.json` verifies archive/file completeness and instruction presence only.
It is not an application test, security review, CI result, database migration check or deployed release certificate.

---
## Detailed task for this README

# Project entry point and reproducible setup

```text
HOSTELSPACE — DETAILED FILE IMPLEMENTATION TASK
STATUS: Instruction-filled starter; application behavior NOT IMPLEMENTED.
TARGET FILE: README.md
ACCOUNTABLE OWNER: Anvi Srinivas
INDEPENDENT REVIEWER: Arin Singh
USER STORIES: US-17
DEVELOPMENT PLAN SPRINT(S): 1 (proposed working mapping; team approval required)
ORIGINAL SRS SPRINT(S): 1 (preserved baseline mapping)
REQUIREMENTS: All FRs; architecture
FILE PURPOSE: Project entry point and reproducible setup

WHAT TO IMPLEMENT IN THIS FILE
Describe architecture, install/run/test commands, env names without secrets, demo roles, source precedence, build order and current status. Do not imply the blueprint is a working app.

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
TARGET FILE: README.md
DEVELOPMENT-PLAN SPRINT: 1
ORIGINAL SRS SPRINT: 1
STORY: US-17
REQUIREMENTS: All FRs; architecture
RESPONSIBILITY: Project entry point and reproducible setup
FILE TASK: Describe architecture, install/run/test commands, env names without secrets, demo roles, source precedence, build order and current status. Do not imply the blueprint is a working app.

US-17 — Baseline architecture and scaffold monorepo
Dependencies: None
Acceptance context (deliver only the part owned by this file, report remaining dependencies):
- Working Next.js and Django/DRF skeletons with health response.
- Architecture/deployment diagrams show browser → Next.js → Django → PostgreSQL, external payment/location and separate CI path.
- Record stack revision and duplicate UC correction proposal without changing FR IDs.
- All four members review and can run the skeleton.

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
