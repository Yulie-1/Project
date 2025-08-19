from fastapi import APIRouter, HTTPException
from typing import List
import time
import db_func as db
from models_api import Task

router = APIRouter()

@router.get("/tasks", response_model=List[Task])
async def read_tasks():
    tasks = await db.read_tasks()
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found")
    return tasks

@router.post("/tasks", response_model=Task)
async def create_task(task: Task):
    creation_time = time.perf_counter()
    response = await db.create_task(task, creation_time)
    if not response:
        raise HTTPException(status_code=500, detail="Could not update task")
    return task

@router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: Task):
    updated_task = await db.update_task(task_id, task)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

@router.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(task_id: int):
    response = await db.delete_task(task_id)
    if not response:
        raise HTTPException(status_code=404, detail="Task not found")
    return response
