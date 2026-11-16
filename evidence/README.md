# Sanitized evidence index

Owner: Aryan Singh · Reviewer: Atiksh Gour · Story: US-23

## UI screenshots

`tests/e2e/critical-flows.spec.js` writes screenshots to `evidence/ui/` each time the browser suite runs against disposable synthetic accounts. **The images are not committed on branch `aryan`.** They contain only synthetic demo data, but they are regenerated on every run, so commit them only if the team decides to keep a fixed evidence set.

The 2026-11-14 run (12/12 passed) produced these 22 files:

- `ui/announcement-editor-dialog.png`
- `ui/announcements.png`
- `ui/attendance-accepted.png`
- `ui/complaint-resolved.png`
- `ui/deviation-management.png`
- `ui/director-overview.png`
- `ui/hostel-rules.png`
- `ui/laundry-group-schedule.png`
- `ui/laundry-receive-dialog.png`
- `ui/laundry-work-queue.png`
- `ui/leave-approved.png`
- `ui/mobile-navigation.png`
- `ui/mobile-profile.png`
- `ui/payment-simulation.png`
- `ui/student-dashboard.png`
- `ui/student-laundry.png`
- `ui/student-mess.png`
- `ui/study-room.png`
- `ui/warden-account-dialog.png`
- `ui/warden-announcements.png`
- `ui/warden-mess-management.png`
- `ui/warden-people.png`

These screenshots show views that were exercised. They are not independent human acceptance.

## Other evidence

- Test commands and observed results: `docs/06-testing/test-summary.md`.
- Branch `aryan` commits: `325bad1` (Sprint 1), `f240aed` (Sprint 2), `7f44eee` (Sprint 3), `72b15c8` (Sprint 4), `b7a9aa3` (Sprint 5).
- Hosted CI, container runs and migration runs on a shared database: none yet for this branch.

No passwords, session cookies, databases, raw attendance coordinates, payment credentials or Playwright failure traces are stored here.
