#!/usr/bin/env bash
# Owner: Atiksh Gour | US-24 | Sprint 6 | Reviewer: Anvi Srinivas
set -euo pipefail
die() { printf 'Restore refused: %s\n' "$1" >&2; exit 1; }
[[ ${HS_RESTORE_CONFIRM:-} == 'RESTORE SYNTHETIC TEST DATABASE' && ${HS_SYNTHETIC_ONLY:-} == YES ]] || die 'explicit synthetic restore confirmation required'
[[ ${PGDATABASE:-} =~ ^hostelspace_synthetic_[a-z0-9_]+$ ]] || die 'source database name is not allowlisted'
[[ ${HS_RESTORE_DATABASE:-} =~ ^hostelspace_restore_[a-z0-9_]+$ ]] || die 'target database name is not allowlisted'
[[ -n ${PGHOST:-} && -n ${PGUSER:-} && -f ${HS_BACKUP_FILE:-} && -f ${HS_COUNTS_FILE:-} ]] || die 'connection, dump and count manifest required'
command -v pg_restore >/dev/null || die 'pg_restore required'
command -v psql >/dev/null || die 'psql required'
[[ $(psql -X -A -t -v ON_ERROR_STOP=1 -d postgres -c "SELECT count(*) FROM pg_database WHERE datname = '$HS_RESTORE_DATABASE'") == 1 ]] || die 'target database must already exist'
[[ $(psql -X -A -t -v ON_ERROR_STOP=1 -d "$HS_RESTORE_DATABASE" -c "SELECT count(*) FROM pg_tables WHERE schemaname = 'public'") == 0 ]] || die 'target database must be empty'
pg_restore --exit-on-error --no-owner --no-acl --dbname="$HS_RESTORE_DATABASE" "$HS_BACKUP_FILE"
actual=$(mktemp)
trap 'rm -f -- "$actual"' EXIT
psql -X -A -t -v ON_ERROR_STOP=1 -d "$HS_RESTORE_DATABASE" -c "SELECT format('SELECT %L, count(*) FROM %I.%I;', schemaname || '.' || tablename, schemaname, tablename) FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename" | psql -X -A -t -v ON_ERROR_STOP=1 -d "$HS_RESTORE_DATABASE" > "$actual"
cmp -s "$HS_COUNTS_FILE" "$actual" || die 'restored table counts differ'
printf 'Verified matching table counts in %s\n' "$HS_RESTORE_DATABASE"
