import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    review: Mapped[str] = mapped_column()
    rating: Mapped[int] = mapped_column()
    reply_id: Mapped[str | None] = mapped_column(ForeignKey("reviews.id", ondelete="SET NULL"))
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    event_id: Mapped[str] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    
    user: Mapped["User | None"] = relationship(back_populates="reviews")
    event: Mapped["Event"] = relationship(back_populates="reviews")
    reply: Mapped["Review | None"] = relationship(
        "Review",
        remote_side=[id],
        back_populates="replies",
    )

    replies: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="reply",
    )