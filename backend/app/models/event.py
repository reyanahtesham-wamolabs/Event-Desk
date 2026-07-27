import uuid
import enum
from datetime import datetime

from sqlalchemy import ForeignKey, Table, Column, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


event_tags = Table(
    "event_tags",
    Base.metadata,
    Column("event_id", String, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(unique=True, index=True)

    events: Mapped[list["Event"]] = relationship(secondary=event_tags, back_populates="tags")


class EventCategory(str, enum.Enum):
    MUSIC = "music"
    SPORTS = "sports"
    CONFERENCE = "conference"
    THEATER = "theater"
    OTHER = "other"


class EventStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column()
    event_time: Mapped[datetime] = mapped_column()
    total_tickets: Mapped[int] = mapped_column()
    tags: Mapped[list["Tag"]] = relationship(secondary=event_tags, back_populates="events")
    category: Mapped[EventCategory] = mapped_column()
    status: Mapped[EventStatus] = mapped_column(default=EventStatus.DRAFT)
    organizer_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    
    organizer: Mapped["User | None"] = relationship(back_populates="organized_events", foreign_keys=[organizer_id])
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="event")
    reviews: Mapped[list["Review"]] = relationship(back_populates="event")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="event")