"""
Integration tests for the ADHD task API.

These tests run against the REAL database, so they use a unique
test category name (prefixed with _test_) and clean up after themselves.

Run with:  python -m pytest tests/test_api.py -v
"""
import asyncio
import sys
import pytest
import pytest_asyncio
import httpx
from httpx import AsyncClient, ASGITransport

# psycopg needs SelectorEventLoop on Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# -- pytest-asyncio config --------------------------------------------------
pytest_plugins = ["pytest_asyncio"]

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TEST_CATEGORY = "_test_integration"


@pytest_asyncio.fixture(scope="module")
async def client():
    """Async HTTP client wired directly to the FastAPI ASGI app."""
    from main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_and_teardown(client):
    """Create the test category before tests, delete it (and any tasks) after."""
    # ---- setup ----
    r = await client.post("/categories", json={"category_name": TEST_CATEGORY})
    # 200 = created, 409 = already exists from a previous failed run – both OK
    assert r.status_code in (200, 409), f"Category setup failed: {r.text}"

    yield  # run the tests

    # ---- teardown: delete any lingering test tasks then the category ----
    tasks_r = await client.get("/tasks")
    if tasks_r.status_code == 200:
        for task in tasks_r.json():
            if task.get("category_name") == TEST_CATEGORY:
                await client.delete(f"/tasks/{task['task_id']}")

    await client.delete(f"/categories/{TEST_CATEGORY}")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

async def create_test_task(client, description="test task", status="open"):
    payload = {
        "category_name": TEST_CATEGORY,
        "status": status,
        "description": description,
    }
    r = await client.post("/tasks", json=payload)
    assert r.status_code == 200, f"Task creation failed: {r.text}"
    return r.json()


# ---------------------------------------------------------------------------
# Tests: Categories
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_read_categories_returns_list(client):
    r = await client.get("/categories")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_create_duplicate_category_returns_409(client):
    r = await client.post("/categories", json={"category_name": TEST_CATEGORY})
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_delete_nonexistent_category_returns_404(client):
    r = await client.delete("/categories/_does_not_exist_xyz")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Tests: Tasks — CRUD
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_read_tasks_returns_list(client):
    r = await client.get("/tasks")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_create_task_returns_task_with_id(client):
    task = await create_test_task(client, description="create test")
    assert task["task_id"] is not None
    assert task["category_name"] == TEST_CATEGORY
    assert task["status"] == "open"


@pytest.mark.asyncio
async def test_create_task_with_invalid_category_returns_409(client):
    r = await client.post("/tasks", json={
        "category_name": "_nonexistent_cat_xyz",
        "status": "open",
    })
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_update_task_basic_fields(client):
    task = await create_test_task(client, description="update test")
    task_id = task["task_id"]

    r = await client.put(f"/tasks/{task_id}", json={
        "category_name": TEST_CATEGORY,
        "status": "pending",
        "description": "updated description",
    })
    assert r.status_code == 200
    updated = r.json()
    assert updated["status"] == "pending"
    assert updated["description"] == "updated description"


@pytest.mark.asyncio
async def test_update_nonexistent_task_returns_404(client):
    r = await client.put("/tasks/999999", json={
        "category_name": TEST_CATEGORY,
        "status": "open",
        "description": "ghost task",
    })
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_delete_task(client):
    task = await create_test_task(client, description="delete test")
    task_id = task["task_id"]

    r = await client.delete(f"/tasks/{task_id}")
    assert r.status_code == 200
    assert "deleted" in r.json()["message"].lower()


@pytest.mark.asyncio
async def test_delete_nonexistent_task_returns_404(client):
    r = await client.delete("/tasks/999999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Tests: Status transitions (time_worked / started_at / completed_at)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_open_to_in_progress_sets_started_at(client):
    """Moving open -> in_progress should create a TaskStatusDetails with started_at set."""
    import DB.db_func as db
    from sqlalchemy import select
    from DB.models_db import TaskStatusDetails

    task = await create_test_task(client, description="transition test open->in_progress")
    task_id = task["task_id"]

    r = await client.put(f"/tasks/{task_id}", json={
        "category_name": TEST_CATEGORY,
        "status": "in_progress",
        "description": task["description"],
    })
    assert r.status_code == 200

    # Check DB directly
    async with db.establish_connection() as session:
        stmt = select(TaskStatusDetails).where(TaskStatusDetails.task_id == task_id)
        result = await session.execute(stmt)
        details = result.scalar_one_or_none()

    assert details is not None, "TaskStatusDetails row should exist"
    assert details.started_at is not None, "started_at should be set when entering in_progress"


@pytest.mark.asyncio
async def test_in_progress_to_done_accumulates_time_and_sets_completed_at(client):
    """Moving in_progress -> done should accumulate time_worked and set completed_at."""
    import DB.db_func as db
    from sqlalchemy import select
    from DB.models_db import TaskStatusDetails
    from datetime import timedelta

    task = await create_test_task(client, description="transition test in_progress->done")
    task_id = task["task_id"]

    # step 1: open -> in_progress
    await client.put(f"/tasks/{task_id}", json={
        "category_name": TEST_CATEGORY,
        "status": "in_progress",
        "description": task["description"],
    })

    # step 2: in_progress -> done
    r = await client.put(f"/tasks/{task_id}", json={
        "category_name": TEST_CATEGORY,
        "status": "done",
        "description": task["description"],
    })
    assert r.status_code == 200

    async with db.establish_connection() as session:
        stmt = select(TaskStatusDetails).where(TaskStatusDetails.task_id == task_id)
        result = await session.execute(stmt)
        details = result.scalar_one_or_none()

    assert details is not None
    assert details.completed_at is not None, "completed_at should be set when done"
    assert details.started_at is None, "started_at should be cleared after leaving in_progress"
    assert details.time_worked >= timedelta(0), "time_worked should be a non-negative timedelta"


@pytest.mark.asyncio
async def test_time_worked_accumulates_across_multiple_in_progress_sessions(client):
    """time_worked should add up across multiple open->in_progress->open cycles."""
    import DB.db_func as db
    from sqlalchemy import select
    from DB.models_db import TaskStatusDetails
    from datetime import timedelta

    task = await create_test_task(client, description="multi-session time test")
    task_id = task["task_id"]

    base = {
        "category_name": TEST_CATEGORY,
        "description": task["description"],
    }

    # First in_progress session
    await client.put(f"/tasks/{task_id}", json={**base, "status": "in_progress"})
    await client.put(f"/tasks/{task_id}", json={**base, "status": "open"})

    async with db.establish_connection() as session:
        stmt = select(TaskStatusDetails).where(TaskStatusDetails.task_id == task_id)
        r1 = await session.execute(stmt)
        details1 = r1.scalar_one_or_none()
    time_after_first = details1.time_worked

    # Second in_progress session
    await client.put(f"/tasks/{task_id}", json={**base, "status": "in_progress"})
    await client.put(f"/tasks/{task_id}", json={**base, "status": "open"})

    async with db.establish_connection() as session:
        stmt = select(TaskStatusDetails).where(TaskStatusDetails.task_id == task_id)
        r2 = await session.execute(stmt)
        details2 = r2.scalar_one_or_none()
    time_after_second = details2.time_worked

    assert time_after_second >= time_after_first, (
        "time_worked should be >= after a second in_progress session"
    )
