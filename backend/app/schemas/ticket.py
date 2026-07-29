from pydantic import BaseModel
from app.models.enum import TicketTier


class TicketOut(BaseModel):
    id: str
    seat_num: int
    ticket_tier: TicketTier
    price: int
    user_id: str | None
    event_id: str

    class Config:
        from_attributes = True


class TicketCreate(BaseModel):
    event_id: str
    seat_num: int
    ticket_tier: TicketTier
    price: int


class TicketBulkCreate(BaseModel):
    tickets: list[TicketCreate]


class TicketUpdate(BaseModel):
    seat_num: int | None = None
    ticket_tier: TicketTier | None = None
    price: int | None = None


class PurchaseAnyRequest(BaseModel):
    tier: TicketTier


class AvailableCountOut(BaseModel):
    event_id: str
    tier: TicketTier | None
    available: int
