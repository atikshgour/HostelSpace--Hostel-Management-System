# US-24 recovery validation — 2026-11-07

Owner: Atiksh Gour. Independent reviewer: Anvi Srinivas (pending). Issue: #28.

Changed: `scripts/backup.sh`, `scripts/restore-test.sh`, and `docs/07-maintenance/runbook.md`. The scripts restrict source and target names to synthetic database prefixes, require explicit restore confirmation, create dumps outside the repository, reject populated restore targets and compare exact public-table counts. The runbook covers maintainer duties, rollback compatibility, incident triage and payment reconciliation.

Actual checks:

- `git diff --check`: passed, with line-ending warnings only.
- `bash -n scripts/backup.sh scripts/restore-test.sh`: blocked; Windows `bash.exe` alias could not be accessed.
- `.venv/Scripts/python.exe -m pytest backend/apps/student_services/tests/test_payments.py -q`: blocked before collection because `DJANGO_SECRET_KEY` was unset.
- Separate PostgreSQL restore/count comparison: Not Run; no isolated synthetic source/target or usable Bash was available.
- Known-good frontend/API rollback and schema compatibility drill: Not Run; no deployment images or approved release baseline was supplied.
- Razorpay sandbox success/failure/pending/duplicate checkout: Not Run; test credentials and external sandbox were unavailable. Existing mocked payment tests are described in `evidence/us16-validation.md` and are not a substitute.

Acceptance remains partial. No production data, live payment, deployment, production migration or push was performed. Independent review and US-23 release checks remain pending.
