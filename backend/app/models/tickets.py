import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .enum import TicketTier
from .database import Base


class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    seat_num: Mapped[int] = mapped_column()
    ticket_tier:Mapped[TicketTier]=mapped_column()
    price: Mapped[int] = mapped_column()
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    event_id: Mapped[str] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    
    user: Mapped["User | None"] = relationship(back_populates="tickets")
    event: Mapped["Event"] = relationship(back_populates="tickets")


