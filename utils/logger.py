import logging
import os
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from config.settings import settings

# Create data dir if not exists
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
LOG_FILE = os.path.join(DATA_DIR, 'orchestrator.log')

class SensitiveDataFilter(logging.Filter):
    """Filter to redact sensitive API keys from logs"""
    def __init__(self):
        super().__init__()
        self.sensitive_strings = [
            os.getenv("OPENROUTER_API_KEY", ""),
            settings.wp_app_password
        ]
        # Remove empty strings to avoid replacing everything
        self.sensitive_strings = [s for s in self.sensitive_strings if s]

    def filter(self, record):
        if isinstance(record.msg, str):
            for s in self.sensitive_strings:
                if s in record.msg:
                    record.msg = record.msg.replace(s, "***REDACTED***")
        return True

def get_logger(agent_name: str) -> logging.Logger:
    """
    Returns a configured logger for the given agent/module.
    Logs are structured as JSON and rotated.
    """
    logger = logging.getLogger(agent_name)
    
    # Only configure if it doesn't already have handlers to avoid duplicates
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        
        # Stream Handler (Console)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        
        # Rotating File Handler (Max 5MB, keep 2 backups)
        try:
            file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=2)
            file_handler.setFormatter(formatter)
            
            # Add filters
            sensitive_filter = SensitiveDataFilter()
            stream_handler.addFilter(sensitive_filter)
            file_handler.addFilter(sensitive_filter)
            
            logger.addHandler(stream_handler)
            logger.addHandler(file_handler)
        except (IOError, OSError):
            # File system not writable (common in containerized environments)
            # Just use stream handler only
            sensitive_filter = SensitiveDataFilter()
            stream_handler.addFilter(sensitive_filter)
            logger.addHandler(stream_handler)
        
    return logger
