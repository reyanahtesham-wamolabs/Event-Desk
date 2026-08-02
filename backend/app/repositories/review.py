import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.review import Review
from app.models.event import Event
from app.utils.exceptions import NotFoundError


class ReviewRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        event_id: str,
        user_id: str,
        review: str,
        rating: int,
    ) -> Review:
        event = await self.db.get(Event, event_id)
        if event is None:
            raise NotFoundError(f"Event '{event_id}' not found")

        new_review = Review(
            id=str(uuid.uuid4()),
            review=review,
            rating=rating,
            user_id=user_id,
            event_id=event_id,
            reply_id=None,
        )
        self.db.add(new_review)
        await self.db.commit()
        await self.db.refresh(new_review)
        return new_review

    async def get(self, review_id: str) -> Review:
        stmt = (
            select(Review)
            .where(Review.id == review_id)
            .options(selectinload(Review.replies))
        )
        result = await self.db.execute(stmt)
        review = result.scalar_one_or_none()
        if not review:
            raise NotFoundError(f"Review '{review_id}' not found")
        return review

    async def get_by_event(self, event_id: str) -> Sequence[Review]:
        """Return top-level reviews (not replies) for a given event."""
        stmt = (
            select(Review)
            .where(Review.event_id == event_id, Review.reply_id.is_(None))
            .options(selectinload(Review.replies))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_user(self, user_id: str) -> Sequence[Review]:
        stmt = (
            select(Review)
            .where(Review.user_id == user_id)
            .options(selectinload(Review.replies))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_reply(
        self,
        *,
        review_id: str,
        user_id: str,
        review_text: str,
    ) -> Review:
        parent = await self.get(review_id)

        reply = Review(
            id=str(uuid.uuid4()),
            review=review_text,
            rating=0,
            user_id=user_id,
            event_id=parent.event_id,
            reply_id=review_id,
        )
        self.db.add(reply)
        await self.db.commit()
        await self.db.refresh(reply)
        return reply

    async def update(self, review_id: str, **fields) -> Review:
        review = await self.get(review_id)
        for key, value in fields.items():
            if not hasattr(review, key):
                raise ValueError(f"Invalid field: {key}")
            setattr(review, key, value)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def delete(self, review_id: str) -> None:
        review = await self.get(review_id)
        await self.db.delete(review)
        await self.db.commit()
