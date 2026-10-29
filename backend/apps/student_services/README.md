<!-- Owner: Atiksh Gour | US-13 | Sprint 4 (prior proposed development mapping: 2) -->
<!-- Reviewer: Anvi Srinivas; account dependency review: Anvi Srinivas / Arin Singh; pending -->
# Student complaint submission and tracking

Implemented scope: US-13, FR-07 student portion, SEC-03; TC-FR07-01.
The user selected Sprint 4, consistent with the original SRS mapping. The starter's
proposed development-plan Sprint 2 mapping remains a proposal, not an approval.
US-14 staff assignment/status updates are now implemented below. Mess and payments
remain unimplemented. Independent review is pending for both complaint slices.

## US-14 management workflow (2026-10-29)

Owner: Atiksh Gour; reviewer: Anvi Srinivas (pending). GitHub issue #19,
Sprint 4; proposed development-plan mapping remains Sprint 2. FR-07, SEC-01;
TC-FR07-01 staff portion.

The management page is `/complaints/manage`. It consumes existing Django sessions;
US-01 still owns login/logout. There is no public account creation or invented
session login. Active Director and Maintenance Staff sessions can read the paginated
`GET /api/complaints/manage/` list. Directors see all complaints; Maintenance Staff
see only their own assignments. The response adds `can_assign` for UI controls;
server permissions independently authorize every write. GET sets the CSRF cookie.

| Method | Path | Authorized behavior |
| --- | --- | --- |
| GET | `/api/maintenance-staff/` | Director only; paginated active Maintenance Staff IDs/names/usernames |
| POST | `/api/complaints/{id}/assign/` | Director only; assign/reassign active Maintenance Staff |
| POST | `/api/complaints/{id}/progress/` | Director or currently assigned Maintenance Staff; advance one step |

Assignment body: `{"assigned_to": 3, "remarks": "Synthetic assignment"}`.
Progress body: `{"expected_status": "Open", "status": "In Progress", "remarks": "Synthetic work started"}`.
IDs are illustrative; obtain them from the APIs. Remarks must be a string containing
1–500 characters after trimming. Unknown/protected fields are rejected. Writes
require CSRF and return 200 with the persisted complaint. All responses/errors are
uncached and use the existing `{code,message,fields}` error contract.

Only `Open → In Progress → Resolved` is accepted. Starting work requires an
assignment. No skips, reversals, repeated transitions, duplicate assignments,
unassignment, or reassignment after resolution are exposed. A stale expected status
returns 400 with `expected_status`; reload before retrying. Foreign/unassigned
maintenance IDs and missing IDs both return 404. No superuser bypass exists.
An inactive/changed-role actor cannot write even through a stale service caller.

Complaint responses now include nullable `assigned_to`. Every history entry also
includes nullable `old_assigned_to` and `new_assigned_to`. Assignment events keep
the status unchanged and snapshot both assignees. Progress events snapshot the
current assignee and old/new status. Actor, server time and remarks are retained;
old US-13 history remains untouched, with null assignment snapshots. Student
read endpoints expose the same persisted status/history, with no write permission.

Writes atomically lock authoritative users and the complaint, validate permissions,
update current state, and append history. PostgreSQL user locks use NO KEY UPDATE:
this blocks role/deactivation changes while allowing history foreign-key key-share
locks. Failed history insertion rolls back the write. Routine ORM history guards
remain in force; privileged direct SQL is outside their boundary.

The generated additive migration is `0002_complaint_assigned_to_and_more.py`; see
[its sidecar](../../../docs/07-maintenance/us14-migration-manifest.json). It preserves
existing records. No production migration was run. Review a migration plan before
applying it to an approved local database.

Next.js proxies `/api/*` to Django. Direct local development defaults to
`http://127.0.0.1:8000`; set `DJANGO_API_URL` **before building** to change it.
Docker's build argument defaults to `http://api:8000`. The local Django settings
trust only the two localhost port-3000 frontend origins. Production requires its
reviewed HTTPS origin and session/CSRF cookie configuration; no production setup
or deployment is claimed. The feature adapter supplies session/CSRF fetches because
the shared `src/lib/api.js` remains another owner's unimplemented placeholder;
consolidation with the US-01 client remains an integration task.

Verification: [actual commands, results and limits](../../../evidence/us14-validation.md).
The opt-in browser test runs from `backend` with the isolated PostgreSQL environment:
`python -m pytest apps/student_services/tests/browser_us14.py -q`. It requires the
frontend dependencies, local Chrome, Node and free localhost port 3314. It starts
and stops its own Next.js process and Django test server; session values travel
only through subprocess stdin and are not saved in browser traces/state files.

## API

All endpoints require a Django session for an active user with role `student`.
No Basic/JWT authentication, signup, login or staff API is added by this slice.
US-01 must supply the session login/logout flow, including explicit login CSRF.
The minimal custom User/Profile dependency was explicitly authorized by the user.

| Method | Path | Result |
| --- | --- | --- |
| GET | `/api/complaint-categories/` | Paginated active categories; sets CSRF cookie |
| GET | `/api/complaints/` | Paginated own records, newest first |
| POST | `/api/complaints/` | 201 persisted Open complaint and its creation history |
| GET | `/api/complaints/{id}/` | Own current record and chronological history |

Pagination: 20 results per page, `?page=2`; envelope
`{count,next,previous,results}`. All responses, including errors, use `no-store`.
Client category choice comes from the categories endpoint; no category vocabulary
was defined by the sources, so categories are server-managed database rows.
No production categories or policy seed is supplied. Provision reviewed categories
through controlled maintenance tooling; there is no student category-write endpoint.

POST body:
```json
{"category": 1, "description": "Synthetic example: room light needs repair"}
```
Here `1` is illustrative; clients must use an ID returned by the categories API.
Description must be a string containing 1–2000 characters after trimming.
Category must identify an existing active category. Unknown/protected fields
(including room, student, status, assignment and history) are rejected with 400.

Response fields: `id`, `room`, `category` (ID), `category_code`, `category_name`,
`description`, `status`, `created_at`, `history`.
Each history item contains `id,actor,created_at,old_status,new_status,remarks`.
Creation derives the student from the session and snapshots the assigned room
from StudentProfile; it never accepts a client room. Missing profile/room is 400.
Initial status is exactly `Open`. Initial history has empty old status, new
status Open, the student actor, server timestamp and fixed submission remarks.

The transactional service reloads/locks the user, profile and category. Failure
to insert history rolls back the complaint. Query scoping precedes detail lookup,
so a foreign complaint is indistinguishable from a nonexistent one. All student
update/delete methods are rejected; superusers and every staff role are also denied.
The detail GET returns persisted current state, including later staff updates.

## Sessions, CSRF and errors

After US-01 has established a session, GET categories to obtain the CSRF cookie,
then send it as `X-CSRFToken` on POST along with the session cookie. The API uses
DRF SessionAuthentication with an explicit `Session` challenge so unauthenticated
requests return 401. Session creation/login is deliberately not exposed here.
Never copy cookie/token values into logs, evidence or prompt files.

Errors use `{code,message,fields}`: 400 `validation_error` or `parse_error`,
401 `not_authenticated`, 403 `permission_denied` (including failed CSRF),
404 `not_found`, 405 `method_not_allowed`. Unexpected failures return sanitized
500 `server_error` with no exception details. Validation creates no complaint/history.

## Storage and integration

Models: accounts.User/StudentProfile, ComplaintCategory, Complaint, ComplaintTransition.
Generated initial migrations and their ownership are listed in
[the migration sidecar](../../../docs/07-maintenance/us13-migration-manifest.json).
Only untouched placeholder migrations were replaced. No production DB was changed.
Switching an existing database from default auth.User needs a reviewed conversion
plan; never reset data or fake migrations to install this change.

Backend settings now enable auth, sessions and these two apps. Django middleware
and DRF enforce active sessions/CSRF. URLs mount the module under `/api/`.
Docker includes the app source. For a **fresh local synthetic database only**,
review `python manage.py migrate --plan`, then run `python manage.py migrate`
under the local PostgreSQL configuration before using accounts/complaints.
Compose equivalent: `docker compose exec api python manage.py migrate --plan`
and then `docker compose exec api python manage.py migrate`.
Startup does not apply migrations automatically.

## Verification and handoff

From backend with a disposable PostgreSQL database configured:
```text
python manage.py check
python manage.py makemigrations --check --dry-run
python -m ruff check .
python -m pytest
```
Tests create/drop Django's isolated test database; use a dedicated synthetic test
server/user with database-creation privileges, never a production connection.
CI discovers US-13 tests alongside health tests and runs on PostgreSQL 16.
See [actual commands/results and remaining gaps](../../../evidence/us13-backend-validation.md).
No frontend files, commits, pushes or human review records are claimed here.
After human review, append the truthful HISTORY and owner prompt-log handoff.

Source basis: supplied SRS PDF pp. 3–5 (profile/complaint fields, FR-07) and the
repository's US-13 file instructions. API choices above implement the placeholder
contract for independent review; they do not imply prior team approval.
