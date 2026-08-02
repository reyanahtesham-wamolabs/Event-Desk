import uuid
import enum
from datetime import datetime

from sqlalchemy import ForeignKey, Table, Column, String

from .database import Base


event_tags = Table(
    "event_tags",
    Base.metadata,
    Column("event_id", String, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

