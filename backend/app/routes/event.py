from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.dependencies.authorization import get_current_user, require_permission
from app.models.event import EventCategory, EventStatus
from app.models.user import User
from app.core.permissions import Permission
from app.services.event import EventService
from app.dependencies.services import get_event_service
from app.schemas.event import EventCreate,EventResponse,EventUpdate
router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventResponse, status_code=201)
async def create_event(
    payload: EventCreate,
    user: User = Depends(require_permission(Permission.CREATE_EVENT)),
    events_service: EventService = Depends(get_event_service),
):
    return await events_service.create_event(user, **payload.model_dump())


@router.get("", response_model=list[EventResponse])
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


@router.get("/mine", response_model=list[EventResponse])
async def list_my_events(
    status: EventStatus | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    events_service: EventService = Depends(get_event_service),
):
    return await events_service.list_my_events(
        user, status=status, skip=skip, limit=limit
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    user: User = Depends(get_current_user),
    events_service: EventService = Depends(get_event_service),
):
    return await events_service.get_event(event_id)


@router.patch("/{event_id}", response_model=EventResponse)
async def edit_event(
    event_id: str,
    payload: EventUpdate,
    user: User = Depends(require_permission(Permission.EDIT_EVENT)),
    events_service: EventService = Depends(get_event_service),
):
    fields = payload.model_dump(exclude_unset=True)
    return await events_service.edit_event(user, event_id, **fields)


@router.post("/{event_id}/publish", response_model=EventResponse)
async def publish_event(
    event_id: str,
    user: User = Depends(require_permission(Permission.EDIT_EVENT)),
    events_service: EventService = Depends(get_event_service),
):
    return await events_service.publish_event(user, event_id)


@router.post("/{event_id}/cancel", response_model=EventResponse)
async def cancel_event(
    event_id: str,
    user: User = Depends(require_permission(Permission.CANCEL_EVENT)),
    events_service: EventService = Depends(get_event_service),
):
    return await events_service.cancel_event(user, event_id)


@router.delete("/{event_id}", status_code=204)
async def delete_event(
    event_id: str,
    user: User = Depends(require_permission(Permission.DELETE_EVENT)),
    events_service: EventService = Depends(get_event_service),
):
    await events_service.delete_event(user, event_id)
