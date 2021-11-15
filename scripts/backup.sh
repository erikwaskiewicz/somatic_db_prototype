# for details on backup and restore - see https://www.postgresql.org/docs/12/backup-dump.html#BACKUP-DUMP-RESTORE

BACKUP_DIR="/home/ew/db_backups/"

# Backup Postgres DB
/usr/pgsql-12/bin/pg_dump somatic_variant_db -U somatic_variant_db_user -h localhost | gzip > "$BACKUP_DIR"/"$(date '+%Y%m%d%H%M%S')_somatic_db.txt.gz"

