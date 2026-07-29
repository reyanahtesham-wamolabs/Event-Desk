from fastapi import FastAPI
from app.routes.user import router as user_router
from app.routes.authentication import router as auth_router
from app.routes.event import router as event_router
from app.routes.tag import router as tag_router
from app.routes.ticket import router as ticket_router
from starlette.responses import JSONResponse
from app.utils.exceptions import AppException

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(event_router)
app.include_router(tag_router)
app.include_router(ticket_router)

@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
        )
    