Integration permissions follow the supplied PDF; see `docs/04-design/role-permissions.md` and `evidence/team-integration-2026-11-16.md`.

# facilities

Open/Closed study-room status with staff editing (not booking); staff-assigned laundry weekdays; immutable receipt details and assignment snapshot; scoped student history and idempotent collection.

Uses the existing Django ORM, DRF session authentication and shared permissions. See the root README for setup/test commands, `docs/04-design/` for contracts and `docs/06-testing/results.md` for actual verification. Tests live in this module’s `tests/` directory.
