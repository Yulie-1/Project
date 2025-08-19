from database import Database
from models_db import Task

# make sure that task cant be done and something else - trigger?

USERNAME = "username"  
PASSWORD = "password"  
HOST = "localhost"  
PORT = "5432" 
DATABASE_NAME = "your_db_name"  

# TODO: find your username and password
"""
db_url = f"postgresql+psycopg://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}"
database = Database(db_url)
database.create_tables()

def get_db():
    db = database.get_session()
    try:
        yield db
    finally:
        db.close()
        """


async def read_tasks():
    # for now a simple function to simulate reading tasks
    return [
        Task(task_id=1, category_name="Work", status="in_progress", deadline=None, description="Complete project report"),
        Task(task_id=2, category_name="Personal", status="done", deadline=None, description="Grocery shopping"),
    ]

async def create_task(task: Task, creation_time: float):
    # Simulate a database call to create a task
    return task

async def update_task(task_id: int, task: Task):
    # Simulate a database call to update a task
    return task

async def delete_task(task_id: int):
    # Simulate a database call to delete a task
    return {"message": f"Task {task_id} deleted successfully"}

