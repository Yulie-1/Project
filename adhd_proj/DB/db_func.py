from .database import Database
from .models_db import Task, Category
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
from logger import db_logger as logger
from sqlalchemy import select
from sqlalchemy.engine import Result

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
        session.close()  # guaranteed cleanup


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
        stmt = select(Task).where(Task.task_id == task_id)
        result = await session.execute(stmt)
        existing_task = result.scalar_one_or_none()
        
        if not existing_task:
            return None
            
        # Update fields
        existing_task.category_name = task_data.category_name
        existing_task.status = task_data.status
        existing_task.deadline = task_data.deadline
        existing_task.description = task_data.description
        
        await session.commit()
        await session.refresh(existing_task)
        return existing_task

async def delete_task(task_id: int) -> bool:
    logger.info(f"Deleting task ID {task_id}")
    async with establish_connection() as session:
        stmt = select(Task).where(Task.task_id == task_id)
        result = await session.execute(stmt)
        existing_task = result.scalar_one_or_none()
        
        if not existing_task:
            return False
            
        await session.delete(existing_task)
        await session.commit()
        return True

async def delete_category(category_name: str) -> bool:
    logger.info(f"Deleting category: {category_name}")
    async with establish_connection() as session:
        stmt = select(Category).where(Category.category_name == category_name)
        result = await session.execute(stmt)
        existing_category = result.scalar_one_or_none()
        
        if not existing_category:
            return False
            
        await session.delete(existing_category)
        await session.commit()
        return True
