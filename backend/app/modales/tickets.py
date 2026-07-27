import uuid

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    seat_num = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_id = Column(String, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="tickets")
    event = relationship("Event", back_populates="tickets")