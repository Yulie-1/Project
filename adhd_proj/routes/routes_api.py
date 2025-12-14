from fastapi import APIRouter, HTTPException, Request
from typing import List
import time
import DB.db_func as db
from .models_api import Task
from api_logger import logger

router = APIRouter()

@router.get("/tasks", response_model=List[Task])
async def read_tasks(request: Request) -> List[Task]:
    logger.info("Reading tasks")
    tasks = await db.read_tasks()
    tasks = None
    if not tasks:
        logger.error(
            "HTTPerror 404: No tasks found",
            extra={"extra_data": {
                "method": request.method,
                "url": str(request.url),
            }}
        )
        raise HTTPException(status_code=404, detail="No tasks found")
    return tasks

@router.get("/categories", response_model=List[str])
async def read_categories() -> List[str]:
    categories = await db.read_categories()
    if not categories:
        raise HTTPException(status_code=404, detail="No categories found")
    return categories

@router.post("/tasks", response_model=Task)
async def create_task(task: Task) -> dict:
    task.creation_time = time.perf_counter()
    task_id = await db.create_task(task)
    if not task_id:
        raise HTTPException(status_code=500, detail="Could not create task")
    return {"task_id": task_id}

@router.post("/categories", response_model=dict)
async def create_category(category_name: str) -> dict:
    category_id = await db.create_category(category_name)
    if not category_id:
        raise HTTPException(status_code=500, detail="Could not create category")
    return {"category_name": category_id}

@router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: Task) -> Task:
    updated_task = await db.update_task(task_id, task)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

@router.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(task_id: int) -> dict:
    response = await db.delete_task(task_id)
    if not response:
        raise HTTPException(status_code=404, detail="Task not found")
    return response

@router.delete("/categories/{category_name}", response_model=dict)
async def delete_category(category_name: str) -> dict:
    response = await db.delete_category(category_name)
    if not response:
        raise HTTPException(status_code=404, detail="Category not found")
    return response
