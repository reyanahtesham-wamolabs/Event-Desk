import uuid
import enum

from sqlalchemy import Column, String, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class ChangeType(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    acting_user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    change_type = Column(Enum(ChangeType), nullable=False)
    affected_user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    affected_event_id = Column(String, ForeignKey("events.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    acting_user = relationship("User", back_populates="audit_logs_acted", foreign_keys=[acting_user_id])
    affected_user = relationship("User", foreign_keys=[affected_user_id])
    affected_event = relationship("Event", foreign_keys=[affected_event_id])