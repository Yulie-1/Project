from enum import Enum
from pydantic import BaseModel
import datetime

class Status(str, Enum):
    open = "open"
    pending = "pending"
    in_progress = "in_progress"
    done = "done"

class Task(BaseModel):
    task_id: int | None = None
    created_at: datetime.datetime | None = None
    category_name: str
    status: Status = Status.open
    deadline: datetime.datetime | None = None
    description: str | None = None

    class Config:
        from_attributes = True

class Category(BaseModel):
    category_name: str

    class Config:
        from_attributes = True