from pydantic import BaseModel
from app.models.event import EventCategory, EventStatus
from app.services.event import EventService
from datetime import datetime
from .tag import TagResponse
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


class EventResponse(BaseModel):
    id: str
    title: str
    description: str | None
    event_time: datetime
    total_tickets: int
    category: EventCategory
    status: EventStatus
    organizer_id: str | None
    tags: list[TagResponse]

    class Config:
        from_attributes = True
