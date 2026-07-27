import uuid
import enum

from sqlalchemy import Column, String, Enum, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class NotificationType(str, enum.Enum):
    EVENT_REMINDER = "event_reminder"
    EVENT_UPDATE = "event_update"
    EVENT_CANCELLED = "event_cancelled"
    TICKET_CONFIRMATION = "ticket_confirmation"
    REVIEW_REPLY = "review_reply"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(String, ForeignKey("events.id", ondelete="CASCADE"), nullable=True)
    type = Column(Enum(NotificationType), nullable=False)

    # Relationships
    user = relationship("User", back_populates="notifications")
    event = relationship("Event", back_populates="notifications")