import uuid
import enum
from datetime import datetime

from sqlalchemy import ForeignKey, Table, Column, String,DateTime
from .enum import EventCategory,EventStatus
from sqlalchemy import ForeignKey, Table, Column, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base
from .event_tag import event_tags



class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column()
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    total_tickets: Mapped[int] = mapped_column()
    tags: Mapped[list["Tag"]] = relationship(secondary=event_tags, back_populates="events")
    category: Mapped[EventCategory] = mapped_column()
    status: Mapped[EventStatus] = mapped_column(default=EventStatus.DRAFT)
    organizer_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    
    organizer: Mapped["User | None"] = relationship(back_populates="organized_events", foreign_keys=[organizer_id])
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="event")
    reviews: Mapped[list["Review"]] = relationship(back_populates="event")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="event")