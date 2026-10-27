# Arin schema and integration assumptions

## Required shared models

- `settings.AUTH_USER_MODEL` defaults to `accounts.User` in shared config. Required fields/behavior: pk, is_authenticated, is_active, role, get_full_name(), get_username().
- Student has reverse one-to-one `student_profile`, whose `assigned_warden` references the user model. Warden has `chief_warden` referencing a Chief user. Production must validate assignment roles and the single-active-Chief policy.
- `settings.HOSTELSPACE_RULE_MODEL` defaults to `information.Rule`. Required: pk, title (<=200), weightage decimal(10,2) nonnegative, active Boolean.

## Arin models

| Model | Key relationships / data | Invariants |
|---|---|---|
| LeaveRequest | UUID; student; captured assigned_warden; dates/reason/status; server created_at | DB end>=start; API Pending on create; final states immutable through service |
| LeaveTransition | leave; actor; from/to; remarks; server occurred_at | Append through transactional submit/decision; no update/delete API |
| AttendanceSession | UUID; warden; title; window; centre configuration; radius/accuracy/age policy | DB valid window, positive limits, coordinate ranges; serializer finite numeric validation |
| Attendance | UUID; session; student; result/reason_code/server submitted_at | Partial unique `(session,student)` WHERE result='Accepted'; rejected retries allowed; NO student sample fields |
| Deviation | UUID; student; rule; title/weight snapshots; remarks; recording actor/time; active; deactivation actor/time/reason | Nonnegative DB weight; server reads/locks source rule; totals include active only; retained history |

Foreign keys use PROTECT to avoid silently deleting historical records. UUIDs reduce accidental ID collisions but are NOT authorization. Lists are bounded to 25 rows per page. `Deviation` is the concrete implementation name for the original plan’s descriptive DeviationRecord entity.

## Transactions and migration portability

`decide_leave()` locks the scoped request with `select_for_update` inside an atomic transaction. `submit_attendance()` combines a preliminary check with a database partial unique constraint and a nested savepoint to handle a racing acceptance as 409. Deviation recording locks the rule before snapshot; deactivation locks the existing entry.

The initial migration resolves user and rule models via settings and first-migration dependencies. It is shared by both harness and proposed integration. Confirm the real Rule is created in its first migration and review dependency cycles before applying anywhere. If the team already has applied migrations, create a reviewed forward migration instead of overwriting existing history. Disposable integration migration and `makemigrations --check` results are in `docs/05-validation/execution-log.md`; real shared-model and PostgreSQL gates are not automatically satisfied.

## Scope boundaries

Only Arin’s domain schema is implemented here. Shared user/profile/content, study-room/laundry, complaint/mess/payment and Director-management models must come from their owners. US-18 full-project approval stays pending until all entity/permission contracts and migration graphs are reviewed.
