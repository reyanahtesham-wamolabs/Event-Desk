import uuid
import enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class TicketTier(str, enum.Enum):
    GOLD="gold",
    SILVER="silver",
    BRONZE="bronze"