# Leave, attendance and deviation domain

Owner: **Arin Singh** · reviewer: **Aryan Singh** (pending).

- **Sprint 3 / US-05 and US-06:** student leave submission/history, assigned-Warden decisions, Chief-Warden escalation, immutable final states and append-only transition history.
- **Sprint 4 / US-07:** Warden attendance sessions, one explicit browser location sample, server-side window/age/accuracy/radius checks, and one accepted attendance per student/session.
- **Sprint 4 / US-08:** server-owned rule snapshots, active-weightage totals, scoped reads, and retained deactivation history.
- **US-18 / US-22:** contracts, permission scopes, migration constraints and focused validation cases.

## Integration contract

The team-owned `accounts` app must provide an active custom user with `role`, `student_profile.assigned_warden`, and `warden.chief_warden`. The team-owned `information.Rule` must provide `title`, nonnegative decimal `weightage`, and `active`. `permissions.py` is the only shared-model adapter. Do not add a second user or Rule model.

`services.py` owns transactional writes. `views.py` always applies record scopes. Serializers reject caller-supplied actor, status, owner and weight fields. `Attendance` stores only the result, reason and server submission time—not raw student coordinates, accuracy, distance or device sample time.

Run after the shared accounts and information modules are implemented:

```bash
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test apps.leave_attendance.tests
```

The concurrency cases in `test_services.py` run only with PostgreSQL. SQLite results cannot close the duplicate-acceptance or concurrent-finalization release gates.
