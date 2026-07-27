import uuid

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    review = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    reply_id = Column(String, ForeignKey("reviews.id", ondelete="SET NULL"), nullable=True)  # self-referencing
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_id = Column(String, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="reviews")
    event = relationship("Event", back_populates="reviews")
    reply = relationship("Review", remote_side=[id], backref="replies")