#!/bin/bash
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="teos_db"
DB_USER="teos"
DB_PASS="teos_pass"

mkdir -p $BACKUP_DIR

PGPASSWORD=$DB_PASS pg_dump -h postgres -U $DB_USER $DB_NAME > $BACKUP_DIR/teos_db_$TIMESTAMP.sql
cp /data/redis/dump.rdb $BACKUP_DIR/redis_$TIMESTAMP.rdb 2>/dev/null || true

tar -czf $BACKUP_DIR/teos_backup_$TIMESTAMP.tar.gz $BACKUP_DIR/*.sql $BACKUP_DIR/*.rdb 2>/dev/null
rm -f $BACKUP_DIR/*.sql $BACKUP_DIR/*.rdb

find $BACKUP_DIR -name "teos_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: teos_backup_$TIMESTAMP.tar.gz"
