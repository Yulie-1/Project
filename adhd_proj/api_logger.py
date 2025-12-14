import logging
from logging.handlers import RotatingFileHandler
import json
from dotenv import load_dotenv
import os

load_dotenv()

FILE_PATH = os.getenv("FILE_PATH")

# For later: Use QueueHandler + background thread or extremely high-frequency logging
os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)

class JsonLogFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "message": record.getMessage(),
            "url": getattr(record, "url", None),
            "method": getattr(record, "method", None),
            "timestamp": self.formatTime(record, self.datefmt)
        }
        return json.dumps(log_data)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(FILE_PATH, maxBytes=5_000_000, backupCount=3) 
file_handler.setLevel(logging.INFO)
formatter = JsonLogFormatter()

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


