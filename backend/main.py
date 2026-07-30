from fastapi import FastAPI
from app.routes.user import router as user_router
from app.routes.authentication import router as auth_router
from app.routes.event import router as event_router
from app.routes.tag import router as tag_router
from app.routes.ticket import router as ticket_router
from app.routes.review import router as review_router
from app.routes.notification import router as notification_router
from starlette.responses import JSONResponse
from app.utils.exceptions import AppException
from contextlib import asynccontextmanager
from app.core.scheduler import scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the scheduler
    scheduler.start()
    yield
    # Shutdown: Stop the scheduler
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(event_router)
app.include_router(tag_router)
app.include_router(ticket_router)
app.include_router(review_router)
app.include_router(notification_router)

@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
        )
    