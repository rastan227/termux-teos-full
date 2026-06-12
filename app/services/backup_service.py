import logging
import os
import subprocess
import shutil
from datetime import datetime, timedelta
from app.core.config import settings

logger = logging.getLogger(__name__)

class BackupService:
    
    BACKUP_DIR = os.getenv("BACKUP_DIR", "/backups")
    
    @classmethod
    async def run_backup(cls):
        """Run full backup of database and files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(cls.BACKUP_DIR, f"teos_backup_{timestamp}.tar.gz")
        
        try:
            os.makedirs(cls.BACKUP_DIR, exist_ok=True)
            
            # Backup PostgreSQL
            db_dump = os.path.join(cls.BACKUP_DIR, f"db_{timestamp}.sql")
            subprocess.run(
                f"PGPASSWORD={os.getenv('DB_PASS')} pg_dump -h postgres -U teos teos_db > {db_dump}",
                shell=True, check=True
            )
            
            # Backup Redis if needed
            redis_dump = os.path.join(cls.BACKUP_DIR, f"redis_{timestamp}.rdb")
            if os.path.exists("/data/redis/dump.rdb"):
                shutil.copy("/data/redis/dump.rdb", redis_dump)
            
            # Backup storage files
            storage_backup = os.path.join(cls.BACKUP_DIR, f"storage_{timestamp}")
            shutil.copytree(settings.STORAGE_LOCAL_PATH, storage_backup)
            
            # Create tarball
            subprocess.run(f"tar -czf {backup_file} -C {cls.BACKUP_DIR} db_{timestamp}.sql redis_{timestamp}.rdb storage_{timestamp}", shell=True)
            
            # Cleanup temp files
            os.remove(db_dump)
            if os.path.exists(redis_dump):
                os.remove(redis_dump)
            shutil.rmtree(storage_backup)
            
            # Delete old backups (retention)
            cls._cleanup_old_backups()
            
            logger.info(f"Backup completed: {backup_file}")
            return backup_file
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None
    
    @classmethod
    async def restore_backup(cls, backup_file: str):
        """Restore from backup file"""
        try:
            # Extract
            extract_dir = os.path.join(cls.BACKUP_DIR, "restore_temp")
            os.makedirs(extract_dir, exist_ok=True)
            subprocess.run(f"tar -xzf {backup_file} -C {extract_dir}", shell=True, check=True)
            
            # Restore database
            db_file = [f for f in os.listdir(extract_dir) if f.startswith("db_")][0]
            subprocess.run(
                f"PGPASSWORD={os.getenv('DB_PASS')} psql -h postgres -U teos teos_db < {os.path.join(extract_dir, db_file)}",
                shell=True, check=True
            )
            
            # Restore storage
            storage_dir = [f for f in os.listdir(extract_dir) if f.startswith("storage_")][0]
            shutil.copytree(os.path.join(extract_dir, storage_dir), settings.STORAGE_LOCAL_PATH, dirs_exist_ok=True)
            
            # Cleanup
            shutil.rmtree(extract_dir)
            logger.info(f"Restored from {backup_file}")
            return True
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    @classmethod
    def _cleanup_old_backups(cls):
        """Delete backups older than retention days"""
        retention_days = settings.BACKUP_RETENTION_DAYS
        cutoff = datetime.now() - timedelta(days=retention_days)
        for f in os.listdir(cls.BACKUP_DIR):
            if f.startswith("teos_backup_") and f.endswith(".tar.gz"):
                file_path = os.path.join(cls.BACKUP_DIR, f)
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if mtime < cutoff:
                    os.remove(file_path)
                    logger.info(f"Deleted old backup: {f}")
