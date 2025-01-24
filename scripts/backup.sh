# for details on backup and restore - see https://www.postgresql.org/docs/12/backup-dump.html#BACKUP-DUMP-RESTORE
# to setup password on cron, see https://stackoverflow.com/questions/2893954/how-to-pass-in-password-to-pg-dump

BACKUP_DIR="/u02/backups/svd/"

# Backup Postgres DB
/usr/bin/pg_dump somatic_variant_db -U somatic_variant_db_user -h localhost | gzip > "$BACKUP_DIR"/"$(date '+%Y%m%d%H%M%S')_somatic_db.txt.gz"

