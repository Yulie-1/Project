from enum import Enum
from pydantic import BaseModel
import datetime

class Status(str, Enum):
    null = "null"
    pending = "pending"
    in_progress = "in_progress"
    done = "done"

class Task(BaseModel):
    creation_time: float | None = None
    category_name: str
    status: Status
    deadline: datetime.datetime | None = None  # Assuming deadline is a datetime, can be None if not set
    description: str | None = None