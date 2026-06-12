import logging
import logging.handlers
import json
import sys
from datetime import datetime
from pathlib import Path
from app.core.config import settings

class CustomJSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.thread
        }
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)

def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    console = logging.StreamHandler(sys.stdout)
    if settings.ENVIRONMENT == "production":
        console.setFormatter(CustomJSONFormatter())
    else:
        console.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    root_logger.addHandler(console)
    
    Path("logs").mkdir(exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        "logs/teos.log", maxBytes=10*1024*1024, backupCount=10
    )
    file_handler.setFormatter(CustomJSONFormatter())
    root_logger.addHandler(file_handler)
    
    error_handler = logging.handlers.RotatingFileHandler(
        "logs/error.log", maxBytes=10*1024*1024, backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(CustomJSONFormatter())
    root_logger.addHandler(error_handler)
    
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return root_logger
