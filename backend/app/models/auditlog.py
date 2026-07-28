import uuid
import enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class ChangeType(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    acting_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    change_type: Mapped[ChangeType] = mapped_column()
    affected_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    affected_event_id: Mapped[str | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))

    # Relationships
    acting_user: Mapped["User | None"] = relationship(
        back_populates="audit_logs_acted", foreign_keys=[acting_user_id]
    )
    affected_user: Mapped["User | None"] = relationship(foreign_keys=[affected_user_id])
    affected_event: Mapped["Event | None"] = relationship(foreign_keys=[affected_event_id])
