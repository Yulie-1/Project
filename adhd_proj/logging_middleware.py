from fastapi import Request, HTTPException
import time

# Note to self: Always wrap middleware functions with try and except blocks! 
# Logs should NEVER affect functionality.



async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    try: 
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        print(f"{request.method} {request.url.path} took {process_time:.3f}s")

        with open("request_logs.txt", "a") as log_file:
            log_file.write(f"{request.method} {request.url.path} took {process_time:.3f}s\n")

        return response
    
    except HTTPException as e:
        process_time = time.perf_counter() - start_time
        log_line = (
            f"ERROR {request.method} {request.url.path} "
            f"returned {e.status_code} in {process_time:.3f}s - Detail: {e.detail}"
        )
        print(log_line)
        with open("request_logs.txt", "a") as log_file:
            log_file.write(f"{log_line}\n")
        raise
