from fastapi import FastAPI
from app.routes.user import router as user_router
from app.routes.authentication import router as auth_router

app = FastAPI(title="Event Desk API")

app.include_router(auth_router)
app.include_router(user_router)

@app.get("/")
async def root():
    return {"message": "Hello World from Event Desk!"}

