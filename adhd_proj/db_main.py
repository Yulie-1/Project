from fastapi import FastAPI, HTTPException
from typing import List
import DB.db_func as db
from routes.models_api import Task, Category
from sqlalchemy.exc import IntegrityError
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    await db.database.create_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/tasks", response_model=List[Task])
async def read_tasks():
    return await db.read_tasks()

@app.get("/categories", response_model=List[str])
async def read_categories():
    categories = await db.read_categories()
    return [c.category_name for c in categories]

@app.post("/tasks", response_model=Task)
async def create_task(task: Task):
    db_task = db.Task(
        category_name=task.category_name,
        status=task.status.value,
        deadline=task.deadline,
        description=task.description
    )
    try:
        return await db.create_task(db_task)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Constraint violation")

@app.post("/categories", response_model=Category)
async def create_category(category: Category):
    try:
        return await db.create_category(category.category_name)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Category already exists")

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: Task):
    # Pass the pydantic model directly as it was done in the monolith
    try:
        updated = await db.update_task(task_id, task)
        if not updated:
            raise HTTPException(status_code=404, detail="Task not found")
        return updated
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Constraint violation")

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    success = await db.delete_task(task_id)
    if not success:
         raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "deleted"}

@app.delete("/categories/{category_name}")
async def delete_category(category_name: str):
    try:
        success = await db.delete_category(category_name)
        if not success:
             raise HTTPException(status_code=404, detail="Category not found")
        return {"message": "deleted"}
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Cannot delete category")
