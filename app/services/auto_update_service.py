import logging
import subprocess
import os
import json
import requests
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)

class AutoUpdateService:
    
    CURRENT_VERSION = "1.0.0"
    GIT_REPO = settings.GIT_REPO_URL
    
    @classmethod
    async def check_updates(cls):
        """Check for new version on Git"""
        if not cls.GIT_REPO:
            logger.warning("No GIT_REPO_URL configured")
            return None
        
        try:
            # Fetch latest tags
            result = subprocess.run(
                f"git ls-remote --tags {cls.GIT_REPO}",
                shell=True, capture_output=True, text=True
            )
            tags = []
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) == 2:
                    tag = parts[1].replace("refs/tags/", "")
                    if tag:
                        tags.append(tag)
            
            if not tags:
                return None
            
            # Get latest version (simple semver compare)
            latest = max(tags, key=lambda v: [int(x) for x in v.lstrip('v').split('.')])
            if latest.lstrip('v') > cls.CURRENT_VERSION:
                logger.info(f"New version available: {latest}")
                return latest
            return None
        except Exception as e:
            logger.error(f"Update check failed: {e}")
            return None
    
    @classmethod
    async def perform_update(cls, version: str):
        """Perform the update to given version"""
        if not cls.GIT_REPO:
            return False
        
        try:
            # Backup current state
            from app.services.backup_service import BackupService
            backup_file = await BackupService.run_backup()
            if not backup_file:
                logger.error("Backup before update failed")
                return False
            
            # Pull new version
            subprocess.run(f"git fetch --tags", shell=True, check=True)
            subprocess.run(f"git checkout tags/{version}", shell=True, check=True)
            
            # Install dependencies
            subprocess.run(f"pip install -r requirements.txt", shell=True, check=True)
            
            # Run migrations
            subprocess.run(f"alembic upgrade head", shell=True, check=True)
            
            # Restart services (handled by supervisor/docker)
            logger.info(f"Successfully updated to {version}")
            return True
        except Exception as e:
            logger.error(f"Update failed: {e}")
            # Attempt rollback
            await cls.rollback(backup_file)
            return False
    
    @classmethod
    async def rollback(cls, backup_file: str):
        """Rollback to previous state"""
        from app.services.backup_service import BackupService
        success = await BackupService.restore_backup(backup_file)
        if success:
            logger.info("Rollback successful")
        else:
            logger.critical("Rollback failed!")
