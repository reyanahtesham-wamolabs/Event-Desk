from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.authorization import get_current_user, require_permission
from app.models.event import EventCategory, EventStatus
from app.models.user import User
from app.core.permissions import Permission
from app.services.event import EventService
from app.dependencies.services import get_event_service

router = APIRouter(prefix="/events", tags=["events"])


# ---- Schemas ----


class EventCreate(BaseModel):
    title: str
    description: str | None = None
    event_time: datetime
    total_tickets: int
    category: EventCategory
    tag_ids: list[str] | None = None


class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    event_time: datetime | None = None
    total_tickets: int | None = None
    category: EventCategory | None = None
    tag_ids: list[str] | None = None


class TagOut(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True


class EventOut(BaseModel):
    id: str
    title: str
    description: str | None
    event_time: datetime
    total_tickets: int
    category: EventCategory
    status: EventStatus
    organizer_id: str | None
    tags: list[TagOut]

    class Config:
        from_attributes = True


# ---- Routes ----


@router.post("", response_model=EventOut, status_code=201)
async def create_event(
    payload: EventCreate,
    user: User = Depends(require_permission(Permission.CREATE_EVENT)),
    events_service: EventService = Depends(get_event_service),
):
    return await events_service.create_event(user, **payload.model_dump())


@router.get("", response_model=list[EventOut])
async def list_published_events(
    category: EventCategory | None = None,
    tag_name: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(require_permission(Permission.VIEW_PUBLISHED_EVENTS)),
    events_service: EventService = Depends(get_event_service),
):
    return await events_service.list_published_events(
        category=category, tag_name=tag_name, skip=skip, limit=limit
    )


@router.get("/mine", response_model=list[EventOut])
async def list_my_events(
    status: EventStatus | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    events_service:EventService=Depends(get_event_service)
):
    """Organizer's own events, any status — no separate permission needed beyond auth."""
    return await events_service.list_my_events(
         user, status=status, skip=skip, limit=limit
    )


@router.get("/{event_id}", response_model=EventOut)
async def get_event(
    event_id: str,
    user: User = Depends(get_current_user),
    events_service:EventService=Depends(get_event_service)
):
    return await events_service.get_event(event_id)


@router.patch("/{event_id}", response_model=EventOut)
async def edit_event(
    event_id: str,
    payload: EventUpdate,
    user: User = Depends(require_permission(Permission.EDIT_EVENT)),
    events_service:EventService=Depends(get_event_service)
):
    fields = payload.model_dump(exclude_unset=True)
    return await events_service.edit_event(user, event_id, **fields)


@router.post("/{event_id}/publish", response_model=EventOut)
async def publish_event(
    event_id: str,
    user: User = Depends(require_permission(Permission.EDIT_EVENT)),
    events_service:EventService=Depends(get_event_service)
):
    return await events_service.publish_event(user, event_id)


@router.post("/{event_id}/cancel", response_model=EventOut)
async def cancel_event(
    event_id: str,
    user: User = Depends(require_permission(Permission.CANCEL_EVENT)),
    events_service:EventService=Depends(get_event_service)
):
    return await events_service.cancel_event( user, event_id)


@router.delete("/{event_id}", status_code=204)
async def delete_event(
    event_id: str,
    user: User = Depends(get_current_user),
    events_service:EventService=Depends(get_event_service)
):
    """Admin-only hard delete — enforced inside the service, not via require_permission,
    since there's no dedicated DELETE_EVENT permission in the current enum."""
    await events_service.delete_event(user, event_id)
