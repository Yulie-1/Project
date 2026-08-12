from fastapi import APIRouter, HTTPException, Request
from typing import List
import time
import DB.db_func as db
from .models_api import Task, Category
from logger import api_logger as logger
from sqlalchemy.exc import IntegrityError

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
    try:
        tasks = await db.read_tasks()
        return tasks
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading tasks: {e}")
        error_response(500, "Internal Server Error", request)

@router.get("/categories", response_model=List[str])
async def read_categories(request: Request) -> List[str]:
    logger.info("Reading categories")
    try:
        categories = await db.read_categories()
        # Convert list of Category objects to list of strings
        return [c.category_name for c in categories]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading categories: {e}")
        error_response(500, "Internal Server Error", request)

@router.post("/tasks", response_model=Task)
async def create_task(task: Task, request: Request) -> Task:
    logger.info("Creating task")
    try:
        db_task = db.Task(
            category_name=task.category_name,
            status=task.status.value,
            deadline=task.deadline,
            description=task.description
        )
        created_task = await db.create_task(db_task)
        return created_task
    except HTTPException:
        raise
    except IntegrityError as e:
        logger.error(f"IntegrityError creating task: {e}")
        error_response(409, "Constraint violation (e.g. invalid category)", request)
    except Exception as e:
        logger.error(f"Unexpected error creating task: {e}")
        error_response(500, f"Error creating task: {e}", request)

@router.post("/categories", response_model=Category)
async def create_category(category: Category, request: Request) -> Category:
    logger.info("Creating category")
    try:
        created_category = await db.create_category(category.category_name)
        return created_category
    except HTTPException:
        raise
    except IntegrityError as e:
        logger.error(f"IntegrityError creating category: {e}")
        error_response(409, f"Category '{category.category_name}' already exists", request)
    except Exception as e:
        logger.error(f"Unexpected error creating category: {e}")
        error_response(500, f"Error creating category: {e}", request)

@router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: Task, request: Request) -> Task:
    logger.info("Updating task")
    try:
        updated_task = await db.update_task(task_id, task)
        if not updated_task:
            logger.error(f"Task {task_id} not found for update")
            error_response(404, "Task not found", request)
        return updated_task
    except HTTPException:
        raise
    except IntegrityError as e:
        logger.error(f"IntegrityError updating task: {e}")
        error_response(409, "Constraint violation", request)
    except Exception as e:
        logger.error(f"Unexpected error updating task: {e}")
        error_response(500, f"Error updating task: {e}", request)

@router.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(task_id: int, request: Request) -> dict:
    logger.info("Deleting task")
    try:
        success = await db.delete_task(task_id)
        if not success:
            logger.error(f"Task {task_id} not found for deletion")
            error_response(404, "Task not found", request)
        return {"message": f"Task {task_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        error_response(500, f"Error deleting task: {e}", request)

@router.delete("/categories/{category_name}", response_model=dict)
async def delete_category(category_name: str, request: Request) -> dict:
    logger.info("Deleting category")
    try:
        success = await db.delete_category(category_name)
        if not success:
            logger.error(f"Category '{category_name}' not found for deletion")
            error_response(404, "Category not found", request)
        return {"message": f"Category '{category_name}' deleted successfully"}
    except HTTPException:
        raise
    except IntegrityError as e:
        logger.error(f"IntegrityError deleting category: {e}")
        error_response(409, "Cannot delete category (still in use?)", request)
    except Exception as e:
        logger.error(f"Error deleting category: {e}")
        error_response(500, f"Error deleting category: {e}", request)
