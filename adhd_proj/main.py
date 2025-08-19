from fastapi import FastAPI
from routes import router
from middleware import log_requests

app = FastAPI()

app.include_router(router)
app.middleware("http")(log_requests)



