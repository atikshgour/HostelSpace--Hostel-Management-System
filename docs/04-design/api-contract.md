# Arin API contract — implementation reference, team approval pending

All domain endpoints are prefixed `/api/`, use Django sessions, require an active authenticated user, and return `Cache-Control: no-store, private`. No bearer/JWT scheme. Every write must include an `X-CSRFToken` from the shared bootstrap. Anonymous session-auth DRF requests return 403; the local `/auth/me/` endpoint returns 401. Standard errors: `{code, message, fields}`. Normal validation 400; role/protected-field denial 403; out-of-scope or nonexistent object 404; final-state/duplicate-accepted conflict 409. List page size is 25, with `{count,next,previous,results}`. Timestamps are timezone-aware ISO strings; clients convert for display. Decimal values serialize as strings.

| Method/path | Input | Output | Authorization |
|---|---|---|---|
| GET `/leaves/` | page | paginated LeaveOutput | Own student; assigned warden; Chief escalations or previously finalized-by-that-Chief requests in supervised scope |
| POST `/leaves/` | start_date, end_date, reason | 201 LeaveOutput | Student; identity/assigned warden derived server-side |
| GET `/leaves/{uuid}/` | — | LeaveOutput | Same record scope |
| POST `/leaves/{uuid}/decision/` | decision: Approved/Rejected/Escalated; nonempty remarks | LeaveOutput | Assigned warden decides Pending; supervising Chief only finalizes Escalated |
| GET `/attendance/sessions/` | page | paginated SessionOutput | Student’s assigned warden; own warden; Chief’s supervised wardens |
| POST `/attendance/sessions/` | title, opens_at, closes_at, centre_latitude, centre_longitude, radius_m, max_accuracy_m, max_sample_age_seconds | 201 SessionOutput | Warden only |
| POST `/attendance/submit/` | session UUID; latitude, longitude, accuracy_m, sampled_at | 201 AttendanceOutput (Accepted OR Rejected) | Student and assigned session; duplicate accepted result is 409 |
| GET `/attendance/history/` | page | paginated AttendanceOutput | Own student; staff’s assigned/supervised students |
| GET `/deviations/` | optional student; page | paginated DeviationOutput | Own student or assigned/supervised scope; student filter cannot expand scope |
| POST `/deviations/` | student, active rule, nonempty remarks | 201 DeviationOutput | Assigned warden or supervising Chief; server copies rule title/weightage |
| GET `/deviations/total/` | student required for staff, ignored for students | `{student,active_total}` | Own student or assigned/supervised selected student |
| POST `/deviations/{uuid}/deactivate/` | nonempty reason | DeviationOutput | Authorized staff; repeated deactivation 409; no deletion |
| GET `/arin/students/` | page | `{id,name}` choices | Warden/Chief assigned/supervised active students only |
| GET `/arin/rules/` | page | `{id,title,weightage}` active rule choices | Warden/Chief only |

## Output fields (exact definitions: serializers.py)

- LeaveOutput: id, student, assigned_warden, start_date, end_date, reason, status, created_at, transitions. Transition: id, actor, from_status, to_status, remarks, occurred_at.
- SessionOutput: id, title, warden, opens_at, closes_at, radius_m, max_accuracy_m, max_sample_age_seconds. Centre coordinates are not returned, even to staff, in this minimal reference; there is no edit-session UI.
- AttendanceOutput: id, session, student, result, reason_code, submitted_at. No sample coordinates/accuracy/distance/sample timestamp.
- DeviationOutput: id, student, rule, rule_title_snapshot, weightage_snapshot, remarks, recorded_by, recorded_at, active, deactivated_by, deactivated_at, deactivation_reason.

## Input and policy notes

Strict allowlists reject caller-supplied actor/status/snapshot/active/owner fields with 403. Non-object payloads and malformed IDs are 400. Date end must be on/after start. Session end must follow start. Coordinates must be finite, latitude ±90/longitude ±180. Radius and max accuracy are >0 to 100000; session sample-age bound is 1–300 seconds. These are technical limits, not faculty-approved attendance settings. Server checks inclusive opening/closing window, supplied accuracy <= configured threshold, age <= configured maximum (future tolerance 5 seconds), then Haversine distance <= radius. Rejection codes: OUTSIDE_WINDOW, LOW_ACCURACY, STALE_SAMPLE, OUTSIDE_RADIUS. Accepted code: WITHIN_POLICY. Invalid JSON/schema validation does not create a stored attendance attempt; valid but policy-rejected samples create only the derived rejected outcome.

## Shared auth contract (Anvi owns production)

Local harness implements GET `/api/auth/csrf/` → `{csrfToken}`, POST `/login/` → `{id,role}`, POST `/logout/` → `{signed_out:true}`, GET `/me/` → `{id,role}`. The frontend uses these exact paths. Both login/logout are explicitly CSRF-protected. Shared routes must provide equivalent semantics or adapt the client/identity hook in one place. Production login throttling, session policy and profile management are outside this pack. No role is accepted from the sign-in body.

Internal `queries.py` aggregate functions are not public routes. Caller must authorize Director access before invoking them; do not expose personal querysets to Director by copying these helpers blindly.
