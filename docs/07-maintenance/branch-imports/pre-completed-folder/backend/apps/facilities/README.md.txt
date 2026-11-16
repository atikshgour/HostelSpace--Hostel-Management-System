## Updated integration

See the root README “Updated usability and workflows” and `docs/04-design/api-contract.md` for current permissions and endpoints. Warden operational account creation, automatic laundry schedules/selectable return days, catalogue-based mess choice and Warden announcements supersede older Director-only/manual-allocation notes below. Historical model/API paths are retained for compatibility.

# facilities

Open/Closed study-room status with staff editing (not booking); staff-assigned laundry weekdays; immutable receipt details and assignment snapshot; scoped student history and idempotent collection.

Uses the existing Django ORM, DRF session authentication and shared permissions. See the root README for setup/test commands, `docs/04-design/` for contracts and `docs/06-testing/results.md` for actual verification. Tests live in this module’s `tests/` directory.
