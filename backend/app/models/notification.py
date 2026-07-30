import uuid
import enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class NotificationType(str, enum.Enum):
    EVENT_REMINDER = "event_reminder"
    EVENT_UPDATE = "event_update"
    EVENT_CANCELLED = "event_cancelled"
    TICKET_CONFIRMATION = "ticket_confirmation"
    REVIEW_REPLY = "review_reply"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    event_id: Mapped[str | None] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    type: Mapped[NotificationType] = mapped_column()
    message: Mapped[str] = mapped_column(default="")
    is_read: Mapped[bool] = mapped_column(default=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="notifications")
    event: Mapped["Event | None"] = relationship(back_populates="notifications")