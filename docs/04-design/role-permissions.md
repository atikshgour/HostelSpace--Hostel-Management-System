# Role and record permission matrix

Server decisions are authoritative. Coarse gate: IsAuthenticated + WorkflowRole. Endpoint verbs and `permissions.py` scopes provide the finer checks. All callers must be active. Role strings are uppercase integration contracts, not user-editable request fields.

| Action | Student | Warden | Chief Warden | Director/other roles |
|---|---|---|---|---|
| Submit leave | Own identity | No | No | No |
| Read leave | Own | Captured assigned warden | Supervised escalations + requests this Chief already finalized | No personal workflow API |
| Decide Pending | No | Captured assigned warden | No | No |
| Finalize Escalated | No | No | Supervises the request’s assigned warden | No |
| Create session | No | Own warden identity | No | No |
| List sessions | Assigned warden’s | Own | Supervised wardens’ | No |
| Submit attendance | Own, assigned session | No | No | No |
| Read attendance | Own | Assigned active students | Supervised active students | No |
| Read deviations/total | Own; filter cannot expand | Assigned active students | Supervised active students | No |
| Record/deactivate deviation | No | Assigned active students | Supervised active students (ratify with team) | No |
| Edit historic transition/weight/sample | No | No | No | No API provided |

Final leave states cannot be re-decided. Deviations are deactivated once with actor/time/reason, never removed. Rule updates do not rewrite snapshots. Default scope follows current active student assignment for attendance and deviations; leave keeps its submitting warden. Reassignment policy needs explicit sign-off. Model admin deliberately exposes no unrestricted writable audit models. This is application-level API integrity, not a claim that a privileged DBA cannot change rows.

The local harness enforces one active Chief with a partial unique constraint. The real accounts owner must implement the corresponding policy; this domain pack cannot enforce it on an external custom user model.
