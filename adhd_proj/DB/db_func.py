from .database import Database
from .models_db import Task
from contextlib import contextmanager
from dotenv import load_dotenv
import os
from logger import db_logger as logger

# make sure that task cant be done and something else - trigger?

load_dotenv()

USERNAME = os.getenv("DB_USERNAME")  
PASSWORD = os.getenv("DB_PASSWORD")  
HOST = os.getenv("DB_HOST")  
PORT = os.getenv("DB_PORT") 
DATABASE_NAME = os.getenv("DB_DATABASE_NAME") 

db_url = f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}"
database = Database(db_url)

        
@contextmanager
async def establish_connection():
    logger.info("Establishing database connection...")
    session = Database.get_session()
    try:
        yield session    # hand over the session for queries
    except Exception as e:
        logger.error(f"Database operation failed: {e}")
        raise
    finally:
        logger.info("Closing database connection...")
        session.close()  # guaranteed cleanup


async def read_tasks() -> list[Task]:
    #async with establish_connection() as session:
    #    users = session.query(User).all()

    # for now a simple function to simulate reading tasks
    logger.info("Reading tasks from database")
    return [
        Task(task_id=1, category_name="Work", status="in_progress", deadline=None, description="Complete project report"),
        Task(task_id=2, category_name="Personal", status="done", deadline=None, description="Grocery shopping"),
    ]
    
async def read_categories() -> list[str]:
    # Simulate a database call to read categories
    logger.info("Reading categories from database")
    return ["Work", "Personal", "Health"]

async def create_task(task: Task) -> int:
    logger.info(f"Creating task: {task.description}")
    # Simulate a database call to create a task
    task_id = 1 # for now
    return task_id

async def create_category(category_name: str) -> str:
    logger.info(f"Creating category: {category_name}")
    # Simulate a database call to create a category
    return category_name

async def update_task(task_id: int, task: Task) -> Task:
    logger.info(f"Updating task ID {task_id}")
    # Simulate a database call to update a task
    return task

async def delete_task(task_id: int) -> dict:
    logger.info(f"Deleting task ID {task_id}")
    # Simulate a database call to delete a task
    return {"message": f"Task {task_id} deleted successfully"}

async def delete_category(category_name: str) -> dict:
    logger.info(f"Deleting category: {category_name}")
    # Simulate a database call to delete a category
    return {"message": f"Category '{category_name}' deleted successfully"}

