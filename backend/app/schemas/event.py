from pydantic import BaseModel, Field
from app.utils.validators import datetime_with_timezone
from app.models.event import EventCategory, EventStatus
from datetime import datetime
from app.models.enum import TicketTier
from .tag import TagResponse
from .ticket import TicketResponse
class EventCreate(BaseModel):
    title: str
    description: str | None = None
    event_time: datetime_with_timezone
    category: EventCategory
    tag_ids: list[str] | None = None
    gold_ticket_count:int=Field(ge=0)
    gold_ticket_price:int=Field(ge=0)
    silver_ticket_count:int=Field(ge=0)
    silver_ticket_price:int=Field(ge=0)
    bronze_ticket_count:int=Field(ge=0)
    bronze_ticket_price:int=Field(ge=0)
    

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
    tickets: list[TicketResponse]

    class Config:
        from_attributes = True

