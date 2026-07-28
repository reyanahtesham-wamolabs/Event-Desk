import uuid
from datetime import datetime
from sqlalchemy import ForeignKey,DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    token: Mapped[str] = mapped_column(unique=True)
    expire_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    
    user: Mapped["User"] = relationship(back_populates="refresh_token")