from .dependencies import Base, engine
from .routers import auth,categories,expenses,analytics,users
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time

app=FastAPI()


Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(expenses.router)
app.include_router(analytics.router)
app.include_router(users.router)


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("fastapi-app")

# Middleware для логування запитів
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"New request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        logger.info(f"Completed: {request.method} {request.url} - Status: {response.status_code} - Time: {duration:.2f}s")
        return response
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise e

# Обробка помилок
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

# Ендпоінт для тестування
@app.get("/")
async def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Hello, Loki and Grafana!"}

@app.get("/error")
async def trigger_error():
    logger.warning("Simulated error endpoint accessed")
    raise ValueError("This is a simulated error")

