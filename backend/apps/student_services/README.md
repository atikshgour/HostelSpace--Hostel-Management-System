<!-- Owner: Atiksh Gour | US-13 | Sprint 4 (prior proposed development mapping: 2) -->
<!-- Reviewer: Anvi Srinivas; account dependency review: Anvi Srinivas / Arin Singh; pending -->
# Student complaint submission and tracking

Implemented scope: US-13, FR-07 student portion, SEC-03; TC-FR07-01.
The user selected Sprint 4, consistent with the original SRS mapping. The starter's
proposed development-plan Sprint 2 mapping remains a proposal, not an approval.
Staff assignment/status updates (US-14), mess and payments remain unimplemented.

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
