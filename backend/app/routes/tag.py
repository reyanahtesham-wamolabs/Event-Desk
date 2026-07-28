from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.authorization import get_current_user
from app.models.user import User
from app.services.tag import TagService
from app.dependencies.services import get_tag_service

router = APIRouter(prefix="/tags", tags=["tags"])



class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class TagUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class TagOut(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True



@router.post("", response_model=TagOut, status_code=201)
async def create_tag(
    payload: TagCreate,
    user: User = Depends(get_current_user),
    tags_service:TagService=Depends(get_tag_service)
):
    """Admin check happens inside the service — tags have no dedicated permission enum entry."""
    return await tags_service.create_tag( user, payload.name)


@router.get("", response_model=list[TagOut])
async def list_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    user: User = Depends(get_current_user),
    tags_service:TagService=Depends(get_tag_service)
):
    return await tags_service.list_tags( skip=skip, limit=limit)


@router.put("/{tag_id}", response_model=TagOut)
async def update_tag(
    tag_id: str,
    payload: TagUpdate,
    user: User = Depends(get_current_user),
    tags_service:TagService=Depends(get_tag_service)
):
    return await tags_service.update_tag(user, tag_id, payload.name)


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: str,
    user: User = Depends(get_current_user),
    tags_service:TagService=Depends(get_tag_service)
):
    await tags_service.delete_tag(user, tag_id)