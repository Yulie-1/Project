from fastapi import Request
import time

async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["Process-Time"] = str(process_time)
    print(f"{request.method} {request.url.path} took {process_time:.3f}s")

    with open("request_logs.txt", "a") as log_file:
        log_file.write(f"{request.method} {request.url.path} took {process_time:.3f}s\n")

    return response
