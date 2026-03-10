from fastapi import APIRouter, HTTPException, Request
from typing import List
import httpx
import os
from .models_api import Task, Category
from logger import api_logger as logger

router = APIRouter()

# The internal DB service URL (accessible inside Docker/K8s)
DB_URL = os.getenv("DB_API_URL", "http://db-service:8001")

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
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{DB_URL}/tasks")
            res.raise_for_status()
            return res.json()
    except httpx.HTTPStatusError as e:
        error_response(e.response.status_code, e.response.text, request)
    except Exception as e:
        logger.error(f"Error reading tasks: {e}")
        error_response(500, "Internal Server Error", request)

@router.get("/categories", response_model=List[str])
async def read_categories(request: Request) -> List[str]:
    logger.info("Reading categories")
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{DB_URL}/categories")
            res.raise_for_status()
            return res.json()
    except httpx.HTTPStatusError as e:
        error_response(e.response.status_code, e.response.text, request)
    except Exception as e:
        logger.error(f"Error reading categories: {e}")
        error_response(500, "Internal Server Error", request)

@router.post("/tasks", response_model=Task)
async def create_task(task: Task, request: Request) -> Task:
    logger.info("Creating task")
    try:
        async with httpx.AsyncClient() as client:
            # Send the task object as JSON
            res = await client.post(f"{DB_URL}/tasks", json=task.model_dump(mode="json"))
            res.raise_for_status()
            return res.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Error creating task from DB service: {e.response.text}")
        error_response(e.response.status_code, e.response.json().get("detail", "Constraint violation"), request)
    except Exception as e:
        logger.error(f"Unexpected error creating task: {e}")
        error_response(500, f"Error creating task: {e}", request)

@router.post("/categories", response_model=Category)
async def create_category(category: Category, request: Request) -> Category:
    logger.info("Creating category")
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{DB_URL}/categories", json=category.model_dump())
            res.raise_for_status()
            return res.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Error creating category from DB service: {e.response.text}")
        error_response(e.response.status_code, e.response.json().get("detail", "Category already exists"), request)
    except Exception as e:
        logger.error(f"Unexpected error creating category: {e}")
        error_response(500, f"Error creating category: {e}", request)

@router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: Task, request: Request) -> Task:
    logger.info("Updating task")
    try:
        async with httpx.AsyncClient() as client:
            res = await client.put(f"{DB_URL}/tasks/{task_id}", json=task.model_dump(mode="json"))
            res.raise_for_status()
            return res.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Error updating task from DB service: {e.response.text}")
        error_response(e.response.status_code, e.response.json().get("detail", "Constraint violation"), request)
    except Exception as e:
        logger.error(f"Unexpected error updating task: {e}")
        error_response(500, f"Error updating task: {e}", request)

@router.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(task_id: int, request: Request) -> dict:
    logger.info("Deleting task")
    try:
        async with httpx.AsyncClient() as client:
            res = await client.delete(f"{DB_URL}/tasks/{task_id}")
            res.raise_for_status()
            return res.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Error deleting task from DB service: {e.response.text}")
        error_response(e.response.status_code, e.response.json().get("detail", "Task not found"), request)
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        error_response(500, f"Error deleting task: {e}", request)

@router.delete("/categories/{category_name}", response_model=dict)
async def delete_category(category_name: str, request: Request) -> dict:
    logger.info("Deleting category")
    try:
        async with httpx.AsyncClient() as client:
            res = await client.delete(f"{DB_URL}/categories/{category_name}")
            res.raise_for_status()
            return res.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Error deleting category from DB service: {e.response.text}")
        error_response(e.response.status_code, e.response.json().get("detail", "Cannot delete category"), request)
    except Exception as e:
        logger.error(f"Error deleting category: {e}")
        error_response(500, f"Error deleting category: {e}", request)
