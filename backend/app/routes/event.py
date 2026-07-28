from fastapi import APIRouter, Depends

from app.dependencies.authorization import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/event", tags=["Event"])


@router.get("/create_event", response_model=UserResponse)
async def create_event(current_user: User = Depends(get_current_user)):
    return "yes"

@router.get("/get_all_events", response_model=UserResponse)
async def get_all_events(current_user: User = Depends(get_current_user)):
    return "yes"

@router.get("/update_event", response_model=UserResponse)
async def update_event(current_user: User = Depends(get_current_user)):
    return "yes"

@router.get("/delete_event", response_model=UserResponse)
async def delete_event(current_user: User = Depends(get_current_user)):
    return "yes"


@router.get("/create_tag", response_model=UserResponse)
async def create_tag(current_user: User = Depends(get_current_user)):
    return "yes"

@router.get("/get_tags", response_model=UserResponse)
async def get_tags(current_user: User = Depends(get_current_user)):
    return "yes"

@router.get("/delete_tag", response_model=UserResponse)
async def delete_tag(current_user: User = Depends(get_current_user)):
    return "yes"


@router.get("/add_tag_to_event", response_model=UserResponse)
async def add_tag_to_event(current_user: User = Depends(get_current_user)):
    return "yes"
