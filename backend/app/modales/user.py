import uuid
import enum

from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship

from .database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ORGANIZER = "organizer"
    ATTENDEE = "attendee"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.ATTENDEE)

    # Relationships
    organized_events = relationship("Event", back_populates="organizer", foreign_keys="Event.organizer_id")
    tickets = relationship("Ticket", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    refresh_token = relationship("RefreshToken", back_populates="user", uselist=False)
    audit_logs_acted = relationship("AuditLog", back_populates="acting_user", foreign_keys="AuditLog.acting_user_id")