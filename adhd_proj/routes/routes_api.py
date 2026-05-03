from fastapi import APIRouter, HTTPException, Request
from typing import List
import time
import DB.db_func as db
from .models_api import Task
from logger import api_logger as logger

router = APIRouter()

def error_response(status_code: int, detail: str, request: Request):
    logger.error(
        f"HTTPerror {status_code}: {detail}",
        extra={"extra_data": {
            "method": request.method,
            "url": str(request.url),
        }}
    )
    raise HTTPException(status_code=status_code, detail=detail)

@router.get("/tasks", response_model=List[Task])
async def read_tasks(request: Request) -> List[Task]:
    logger.info("Reading tasks")
    tasks = await db.read_tasks()
    if not tasks:
        error_response(404, "No tasks found", request)
    return tasks

@router.get("/categories", response_model=List[str])
async def read_categories(request: Request) -> List[str]:
    logger.info("Reading categories")
    categories = await db.read_categories()
    if not categories:
        error_response(404, "No categories found", request)
    return categories

@router.post("/tasks", response_model=Task)
async def create_task(task: Task, request: Request) -> dict:
    logger.info("Creating task")
    task.creation_time = time.perf_counter()
    task_id = await db.create_task(task)
    if not task_id:
        error_response(500, "Could not create task", request)
    return {"task_id": task_id}

@router.post("/categories", response_model=dict)
async def create_category(category_name: str, request: Request) -> dict:
    logger.info("Creating category")
    category_id = await db.create_category(category_name)
    if not category_id:
        error_response(500, "Could not create category", request)
    return {"category_name": category_id}

@router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: Task, request: Request) -> Task:
    logger.info("Updating task")
    updated_task = await db.update_task(task_id, task)
    if not updated_task:
        error_response(404, "Task not found", request)
    return updated_task

@router.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(task_id: int, request: Request) -> dict:
    logger.info("Deleting task")
    response = await db.delete_task(task_id)
    if not response:
        error_response(404, "Task not found", request)
    return response

@router.delete("/categories/{category_name}", response_model=dict)
async def delete_category(category_name: str, request: Request) -> dict:
    logger.info("Deleting category")
    response = await db.delete_category(category_name)
    if not response:
        error_response(404, "Category not found", request)
    return response
