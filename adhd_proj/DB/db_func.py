from .database import Database
from .models_db import Task, Category, TaskStatusDetails
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
from logger import db_logger as logger
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.engine import Result
from datetime import datetime, timezone, timedelta

# make sure that task cant be done and something else - trigger?

load_dotenv()

USERNAME = os.getenv("DB_USERNAME")  
PASSWORD = os.getenv("DB_PASSWORD")  
HOST = os.getenv("DB_HOST")  
PORT = os.getenv("DB_PORT") 
DATABASE_NAME = os.getenv("DB_DATABASE_NAME") 

db_url = f"postgresql+psycopg://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}"
database = Database(db_url)

@asynccontextmanager
async def establish_connection():
    logger.info("Establishing database connection...")
    session = database.get_session()
    try:
        yield session    # hand over the session for queries
    except Exception as e:
        logger.error(f"Database operation failed: {e}")
        raise
    finally:
        logger.info("Closing database connection...")
        await session.aclose()  # must be awaited for async sessions


async def read_tasks() -> list[Task]:
    logger.info("Reading tasks from database")
    async with establish_connection() as session:
        stmt = select(Task)
        result: Result = await session.execute(stmt)
        tasks = result.scalars().all()
        return tasks
    # for now a simple function to simulate reading tasks
    #return [
    #    Task(task_id=1, category_name="Work", status="in_progress", deadline=None, description="Complete project report"),
    #    Task(task_id=2, category_name="Personal", status="done", deadline=None, description="Grocery shopping"),
    #]
    
async def read_categories() -> list[Category]:
    logger.info("Reading categories from database")
    async with establish_connection() as session:
        stmt = select(Category)
        result: Result = await session.execute(stmt)
        categories = result.scalars().all()
        return list(categories)

async def create_task(task: Task) -> Task:
    logger.info(f"Creating task: {task.description}")
    async with establish_connection() as session:
        session.add(task)
        await session.commit()
        await session.refresh(task) #"Go back to the database and get the latest version of this specific object." 
        return task

async def create_category(category_name: str) -> Category:
    logger.info(f"Creating category: {category_name}")
    async with establish_connection() as session:
        category = Category(category_name=category_name)
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category

async def update_task(task_id: int, task_data: Task) -> Task | None:
    logger.info(f"Updating task ID {task_id}")
    async with establish_connection() as session:
        stmt = select(Task).options(selectinload(Task.status_details)).where(Task.task_id == task_id)
        result = await session.execute(stmt)
        existing_task = result.scalar_one_or_none()
        
        if not existing_task:
            return None

        old_status = existing_task.status
        new_status = task_data.status
        # Use naive UTC datetime to match PostgreSQL TIMESTAMP WITHOUT TIME ZONE columns
        now = datetime.utcnow()

        # Ensure TaskStatusDetails row exists
        details = existing_task.status_details
        if not details:
            details = TaskStatusDetails(task_id=task_id, time_worked=timedelta(0))
            session.add(details)

        # Status transition logic
        if new_status == "in_progress" and old_status != "in_progress":
            # Task just entered in_progress - record start time
            details.started_at = now
        elif old_status == "in_progress" and new_status != "in_progress":
            # Task just left in_progress - accumulate elapsed time
            if details.started_at:
                details.time_worked += now - details.started_at
                details.started_at = None
            if new_status == "done":
                details.completed_at = now

        # Update task fields
        existing_task.category_name = task_data.category_name
        existing_task.status = task_data.status
        existing_task.deadline = task_data.deadline
        existing_task.description = task_data.description
        
        await session.commit()
        # Re-fetch with relationship loaded to avoid lazy-load on refresh
        stmt2 = select(Task).options(selectinload(Task.status_details)).where(Task.task_id == task_id)
        result2 = await session.execute(stmt2)
        return result2.scalar_one()

async def delete_task(task_id: int) -> bool:
    logger.info(f"Deleting task ID {task_id}")
    async with establish_connection() as session:
        stmt = select(Task).options(selectinload(Task.status_details)).where(Task.task_id == task_id)
        result = await session.execute(stmt)
        existing_task = result.scalar_one_or_none()
        
        if not existing_task:
            return False
            
        await session.delete(existing_task)
        await session.commit()
        return True

async def delete_category(category_name: str) -> bool:
    # check if there are tasks in this category
    # if there are tasks in this category, return False
    
    logger.info(f"Deleting category: {category_name}")
    async with establish_connection() as session:
        stmt = (
            select(Category)
            .options(selectinload(Category.tasks).selectinload(Task.status_details))
            .where(Category.category_name == category_name)
        )
        result = await session.execute(stmt)
        existing_category = result.scalar_one_or_none()
        
        if not existing_category:
            return False
            
        await session.delete(existing_category)
        await session.commit()
        return True
