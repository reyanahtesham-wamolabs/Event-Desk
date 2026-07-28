import uuid
import enum
from datetime import datetime

from sqlalchemy import ForeignKey, Table, Column, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base
from .event_tag import event_tags


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(unique=True, index=True)

    events: Mapped[list["Event"]] = relationship(secondary=event_tags, back_populates="tags")

