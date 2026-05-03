import logging
from logging.handlers import RotatingFileHandler
import json
from dotenv import load_dotenv
import os

load_dotenv()

FILE_PATH_API = os.getenv("FILE_PATH_API")
FILE_PATH_DB = os.getenv("FILE_PATH_DB")

# For later: Use QueueHandler + background thread or extremely high-frequency logging
os.makedirs(os.path.dirname(FILE_PATH_API), exist_ok=True)
os.makedirs(os.path.dirname(FILE_PATH_DB), exist_ok=True)

class JsonLogFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "message": record.getMessage(),
            "url": getattr(record, "url", None),
            "method": getattr(record, "method", None),
            "timestamp": self.formatTime(record, self.datefmt)
        }
        log_data["logger_name"] = record.name
        return json.dumps(log_data)
    
    
formatter = JsonLogFormatter()
api_logger = logging.getLogger("api_logger")
api_logger.setLevel(logging.INFO)
    
# Create the handler for the API logger
api_file_handler = RotatingFileHandler(FILE_PATH_API, maxBytes=5_000_000, backupCount=3) 
api_file_handler.setLevel(logging.INFO)

# Set the formatter
api_file_handler.setFormatter(formatter)
api_logger.addHandler(api_file_handler)


# --- 6. DB Logger Setup (NEW) ---
# Create a new logger with a unique name
db_logger = logging.getLogger("db_logger")
db_logger.setLevel(logging.INFO) # You could set this to DEBUG for more verbosity
db_logger.propagate = False # Prevents duplicate logs

# Create the handler for the DB logger
db_file_handler = RotatingFileHandler(FILE_PATH_DB, maxBytes=2_000_000, backupCount=3) # e.g., 2MB limit
db_file_handler.setLevel(logging.INFO)

# REUSE the same formatter
db_file_handler.setFormatter(formatter)
db_logger.addHandler(db_file_handler)


