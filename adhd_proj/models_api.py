from enum import Enum
from typing import Union
from pydantic import BaseModel, Field

class Status(str, Enum):
    pending = "ending"
    in_progress = "in_progress"
    done = "done"

class Task(BaseModel):
    model_config = {"extra": "forbid"}  # No extra fields!!

    category_name: str
    status: Status
    deadline: Union[int, None] = None # Assuming deadline is a timestamp, can be None if not set
    description: Union[str, None] = None