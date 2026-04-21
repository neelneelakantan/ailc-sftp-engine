import logging
import json
import uuid
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "correlation_id": getattr(record, 'correlation_id', str(uuid.uuid4())),
            "module": record.module,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logger():
    logger = logging.getLogger("SFTP_Engine")
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    return logger

# Global logger instance
logger = setup_logger()