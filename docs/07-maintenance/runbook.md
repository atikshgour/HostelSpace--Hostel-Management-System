# Recovery and maintenance runbook

Owner: Atiksh Gour (payments and recovery). Independent reviewer: Anvi Srinivas. Sprint 6, US-24. Arin Singh owns leave and attendance triage; Aryan Singh owns facilities triage. A production operator and backup schedule remain to be appointed before release.

## Weekly routine

Atiksh reviews backend/frontend dependency and security advisories weekly, records versions and an upgrade issue, and runs CI and payment tests after accepted upgrades. The assigned operator checks the most recent backup job, retention and restore drill evidence. Triage new bugs by impact, affected roles, reproduction, owner and severity; escalate data loss, authentication failure and payment mismatch immediately to Atiksh and Anvi. Preserve logs without secrets, cookies, payment credentials or student coordinates.

## Synthetic PostgreSQL drill

Use an isolated local PostgreSQL server and **synthetic records only**. Never run these scripts against production. Set PostgreSQL connection variables `PGHOST`, `PGPORT`, `PGUSER`, and credentials via a secured passfile or environment. Use `PGDATABASE=hostelspace_synthetic_<label>` and `HS_SYNTHETIC_ONLY=YES`. Set `HS_BACKUP_DIR` to a secured existing directory outside this repository and run `bash scripts/backup.sh`. It creates a custom-format dump and exact per-table count manifest with restrictive file permissions. Keep both outside Git and restrict access and retention under the operator's policy.

Create an empty, separate `hostelspace_restore_<label>` database on the isolated server. Set `HS_RESTORE_DATABASE`, `HS_BACKUP_FILE`, `HS_COUNTS_FILE`, and `HS_RESTORE_CONFIRM='RESTORE SYNTHETIC TEST DATABASE'`; run `bash scripts/restore-test.sh`. The script refuses a missing or populated target and checks every public-table count after restore. Compare schema/migration state, health endpoint and sample synthetic API reads manually. Dispose of drill databases and files under the approved local retention policy. Do not interpret matching counts as proof of row-level integrity.

## Compatible application rollback

Record the deployed frontend/API commit and migration state before release. Keep the last known-good images. In an isolated clone, restore the synthetic database, run `python backend/manage.py showmigrations`, and verify the known-good API models and frontend against the **current** schema. Run health, authentication and payment regression tests. If compatible, redeploy the paired known-good frontend/API images, then check health and the same smoke tests. Do not reverse migrations or rewrite payment attempts as part of an application rollback. If incompatible, stop and prepare a reviewed forward fix or data recovery plan. Production rollback and deployment require explicit approval.

## Payment incident

For an ambiguous or pending sandbox attempt, inspect the server attempt ID and provider order state through authorized tools. Recheck provider status through the existing verification API; do not create a duplicate due or mark Paid manually. A captured payment must match order, amount and currency. Record only sanitized attempt IDs, timestamps and outcome in the incident ticket. Escalate mismatches and provider errors to Atiksh; preserve immutable attempt history. Retest success, failure, pending and duplicate calls with synthetic test-mode records before release. Never use live funds.

## Status

The scripts and procedure are implemented for review. A separate restore drill, compatible rollback drill and external Razorpay sandbox flows require environment access and are tracked in `evidence/us24-validation.md`. Independent review and US-23 release checks remain open.
