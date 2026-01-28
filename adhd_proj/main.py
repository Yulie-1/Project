from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes.routes_api import router
import DB.db_func as db
#from logging_middleware import log_requests

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    await db.database.create_tables()
    yield
    # Shutdown: (Optional) Dispose engine if needed, but usually redundant

app = FastAPI(lifespan=lifespan)

app.include_router(router)
#app.middleware("http")(log_requests)



