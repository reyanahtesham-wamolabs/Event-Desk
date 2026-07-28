import uuid
import enum

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ORGANIZER = "organizer"
    ATTENDEE = "attendee"


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True, index=True)
    role: Mapped[UserRole] = mapped_column(default=UserRole.ATTENDEE)
    organized_events: Mapped[list["Event"]] = relationship(back_populates="organizer", foreign_keys="Event.organizer_id")
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="user")
    reviews: Mapped[list["Review"]] = relationship(back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")
    refresh_token: Mapped["RefreshToken | None"] = relationship(back_populates="user", uselist=False)
    audit_logs_acted: Mapped[list["AuditLog"]] = relationship(back_populates="acting_user", foreign_keys="AuditLog.acting_user_id")