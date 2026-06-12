#!/bin/bash
set -e
BACKUP_FILE=$1
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Backup file not found: $BACKUP_FILE"
    exit 1
fi
echo "Restoring from $BACKUP_FILE..."
RESTORE_DIR="/tmp/teos_restore"
mkdir -p $RESTORE_DIR
tar -xzf $BACKUP_FILE -C $RESTORE_DIR
docker-compose down
docker-compose up -d postgres
sleep 5
if [ -f "$RESTORE_DIR/teos_db_*.sql" ]; then
    DB_DUMP=$(ls $RESTORE_DIR/teos_db_*.sql | head -1)
    docker exec -i teos_postgres psql -U teos teos_db < $DB_DUMP
fi
if [ -d "$RESTORE_DIR/storage" ]; then
    rm -rf storage
    cp -r $RESTORE_DIR/storage .
fi
docker-compose up -d
rm -rf $RESTORE_DIR
echo "Restore completed successfully."
