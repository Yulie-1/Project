from sqlalchemy import Text, Integer, String, ForeignKey, TIMESTAMP, Interval, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timedelta
from .database import Base  
from typing import List, Optional


class Category(Base):
    __tablename__ = "categories"
    
    category_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    
    tasks: Mapped[List["Task"]] = relationship(back_populates="category", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"
    
    task_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) # Creates a unique identifier for each task
    category_name: Mapped[str] = mapped_column(String(100), ForeignKey("categories.category_name"), nullable=False)
    deadline: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open", server_default="open")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    category: Mapped["Category"] = relationship(back_populates="tasks")
    status_details: Mapped["TaskStatusDetails"] = relationship("TaskStatusDetails", back_populates="task", uselist=False, cascade="all, delete-orphan")

class TaskStatusDetails(Base):
    __tablename__ = "task_status_details"

    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.task_id"), primary_key=True)
    time_worked: Mapped[timedelta] = mapped_column(Interval, default=timedelta(0), server_default="0")  # accumulated work time, defaults to 0
    completed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)  # set when status enters in_progress

    task: Mapped["Task"] = relationship("Task", back_populates="status_details")
