from fastapi import FastAPI
from routes.routes_api import router
#from logging_middleware import log_requests

app = FastAPI()

app.include_router(router)
#app.middleware("http")(log_requests)



