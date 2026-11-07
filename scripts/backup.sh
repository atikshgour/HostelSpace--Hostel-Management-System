#!/usr/bin/env bash
# Owner: Atiksh Gour | US-24 | Sprint 6 | Reviewer: Anvi Srinivas
set -euo pipefail
die() { printf 'Backup refused: %s\n' "$1" >&2; exit 1; }
[[ ${HS_SYNTHETIC_ONLY:-} == YES ]] || die 'confirm synthetic source with HS_SYNTHETIC_ONLY=YES'
[[ ${PGDATABASE:-} =~ ^hostelspace_synthetic_[a-z0-9_]+$ ]] || die 'source database name is not allowlisted'
[[ -n ${PGHOST:-} && -n ${PGUSER:-} && -d ${HS_BACKUP_DIR:-} ]] || die 'PGHOST, PGUSER and existing HS_BACKUP_DIR required'
command -v pg_dump >/dev/null || die 'pg_dump required'
command -v psql >/dev/null || die 'psql required'
repo=$(cd "$(dirname "$0")/.." && pwd -P)
destination=$(cd "$HS_BACKUP_DIR" && pwd -P)
case "$destination/" in "$repo/"*) die 'destination inside repository';; esac
[[ $destination != "$repo" && ! -L $HS_BACKUP_DIR ]] || die 'unsafe destination'
umask 077
stamp=$(date -u +%Y%m%dT%H%M%SZ)
dump="$destination/${PGDATABASE}_${stamp}.dump"
counts="$destination/${PGDATABASE}_${stamp}.counts"
[[ ! -e $dump && ! -e $counts ]] || die 'output exists'
trap 'rm -f -- "$dump" "$counts"' ERR
pg_dump --format=custom --no-owner --no-acl --file="$dump"
psql -X -A -t -v ON_ERROR_STOP=1 -c "SELECT format('SELECT %L, count(*) FROM %I.%I;', schemaname || '.' || tablename, schemaname, tablename) FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename" | psql -X -A -t -v ON_ERROR_STOP=1 > "$counts"
printf 'Synthetic dump: %s\nCount manifest: %s\n' "$dump" "$counts"
