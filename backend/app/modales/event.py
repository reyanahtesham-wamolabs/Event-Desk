import uuid
import enum

from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


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

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    event_time = Column(DateTime, nullable=False)
    total_tickets = Column(Integer, nullable=False)
    tags = Column(String, nullable=True)  # NOTE: ERD listed as FK but no Tags table was defined; stored as plain string
    category = Column(Enum(EventCategory), nullable=False)
    status = Column(Enum(EventStatus), nullable=False, default=EventStatus.DRAFT)
    organizer_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    organizer = relationship("User", back_populates="organized_events", foreign_keys=[organizer_id])
    tickets = relationship("Ticket", back_populates="event")
    reviews = relationship("Review", back_populates="event")
    notifications = relationship("Notification", back_populates="event")