from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Interval
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base  


class Category(Base):
    __tablename__ = "categories"
    
    category_name = Column(String(100), primary_key=True, autoincrement=True)
    
    tasks = relationship("Task", back_populates="category")

class Task(Base):
    __tablename__ = "tasks"
    
    task_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(100), ForeignKey("categories.category_name"), nullable=False)
    deadline = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    status = Column(String(20), nullable=False)
    description = Column(String(255), nullable=True)
    
    category = relationship("Category", back_populates="tasks")
    status_details = relationship("TaskStatusDetails", back_populates="task", uselist=False)

class TaskStatusDetails(Base):
    __tablename__ = "task_status_details"
    
    task_id = Column(Integer, ForeignKey("tasks.task_id"), primary_key=True)
    time_worked = Column(Interval)
    completed_at = Column(TIMESTAMP)
    
    task = relationship("Task", back_populates="status_details")
