from pydantic import BaseModel
from app.utils.validators import datetime_with_timezone
from app.models.event import EventCategory, EventStatus
from datetime import datetime
from app.models.enum import TicketTier
from .tag import TagResponse
class EventCreate(BaseModel):
    title: str
    description: str | None = None
    event_time: datetime_with_timezone
    category: EventCategory
    tag_ids: list[str] | None = None
    gold_ticket_count:int
    gold_ticket_price:int
    silver_ticket_count:int
    silver_ticket_price:int
    bronze_ticket_count:int
    bronze_ticket_price:int
    

class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    event_time: datetime_with_timezone | None = None
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

