Integration permissions follow the supplied PDF; see `docs/04-design/role-permissions.md` and `evidence/team-integration-2026-11-16.md`.

# director_dashboard

Director-only source-record summaries, user/role/student assignments, activation restrictions and allowlisted portal settings. Other operational modules retain ownership of their source records.

Uses the existing Django ORM, DRF session authentication and shared permissions. See the root README for setup/test commands, `docs/04-design/` for contracts and `docs/06-testing/results.md` for actual verification. Tests live in this module’s `tests/` directory.
